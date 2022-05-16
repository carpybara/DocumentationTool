import time
from datetime import datetime
import boto3 #comment out for testing.
import json
import os


import ast
bucket_name = os.environ["SUMMARY_BUCKET"] #Set to empty string for testing
s3 = boto3.resource("s3") #ditto


logs_client = boto3.client('logs', region_name = 'us-east-1') #ditto
lambda_client = boto3.client('lambda') #ditto

LOG_GROUPS = json.loads(os.environ['LOG_GROUPS']) #ditto


def logWorker_handler(event, context):
    
    isDaily = int(event.get("isDaily"))
    if isDaily:
        temp = datetime.utcnow().date()
        date_to_epoch = datetime(temp.year, temp.month, temp.day).timestamp()
        date_from_epoch = date_to_epoch - 86400
    else:
        date_from_epoch = event.get("date_from")
        date_to_epoch  = event.get("date_to")


    filter_standard =  """ | filter (@message like "Making request for" and exist != 0)"""
    filter_streams =  """ or (@message like "Records")""" #works for DynamoDB stream and SQS Queue trigger
    filter_cognito = """ or (@message like "cognito" and @message like "JWT")"""
    filter_API_gateway = """ or (@message like "Sending request to")"""
    
    filters = filter_standard + filter_streams + filter_cognito + filter_API_gateway
    
    query = "fields @timestamp, @message, ispresent(@requestId) as exist, @requestId, @log, @type" + filters + " | sort @timestamp asc" 
    # logs are gone through chronologically because of sort @timestamp asc
    
    start_query_response = queryCloudwatch(LOG_GROUPS, query, date_from_epoch, date_to_epoch)
            
    query_id = start_query_response['queryId']
    response = None
    
    
    while response == None or response['status'] == 'Running':
        time.sleep(1)
        response = getQueryResults(query_id) #logs_client.get_query_results(queryId=query_id)
            
    
    resultJson = {}

    if response and response['results'] and response['results'][0]:
        result_count = 0
        
        JWT_tokens = {}
        
        for log_entry in range(len(response['results'])):
            is_authentication = 0 
            message = str(response['results'][log_entry][1].get('value'))
            requestId = str(response['results'][log_entry][3].get('value'))
            
            #When detecting a JWT, incrementing would give us empty entries in resultJson
            if "JWT" not in message:
                result_count += 1


            if message.startswith('[DEBUG]'):
                
                param_start = int(message.index(' with params'))
                operation_name = message[ int(message.index('OperationModel(name='))+20 : param_start-1] 
                operation_params = message[ param_start+14 : ]
                location = str(response['results'][log_entry][4].get('value')).split(':')[1]
                
                
                resultJson[result_count-1] = {
                    'location': location,
                    'operation_name': operation_name,
                    'operation_params': operation_params,
                    'type': 'function'
                }
                continue
            
            #case: event message
            elif message.startswith('{'):
                trigger = ''
                event_source = ''
                is_authentication = 0
                
                messageDict = json.loads(message) 
                
                if messageDict.get("function_name"):
                    function_name = messageDict.get("function_name")
                    
                #case: Records exist, so its proper event message
                if messageDict.get("message").get("Records"):
                    records = messageDict.get("message").get("Records")
                    event_source = records[0].get("eventSource")
                    
                    #case: its an SQS message
                    if event_source == "aws:sqs": #"https://queue.amazonaws.com/"
                        queue_name = records[0].get("eventSourceARN").split(":")[-1]
                        trigger = event_source + "|" + queue_name

                    #case: It's not (it's dynamodb stream so far)
                    elif event_source == "aws:dynamodb":
                        table_name = records[0].get("eventSourceARN").split("/")[1] #Table from which request originated
                        trigger = event_source + "|" + table_name

                
                resultJson[result_count-1] = {
                    'endpoint': function_name,
                    'trigger': trigger,         #trigger    -> event_source -> function_name #if trigger 0, then its useless cognito message
                    'authentication': is_authentication,
                    'type': 'eventmessage'
                }
                continue
            
            #case: Json Web Token is transmitted. Save this information and add it to the respective caught API-Gateway message.
            if "JWT" in message:
                iss_index = message.index("iss=")
                iss = message[iss_index+4 : ]
                iss = iss[ : iss.index(",")]
                requestId = message.split("(")[1].split(")")[0]
                JWT_tokens[requestId] = iss
                is_authentication = 1
                
                log_name = str(response['results'][log_entry][3].get('value'))
                log_name = log_name.split(":")[1]
                
                resultJson[result_count-1] = {
                    'endpoint': iss,
                    'trigger': log_name, 
                    'authentication': is_authentication,
                    'type': 'api-gateway'
                }
                continue

                
            #case: API-Gateway request to a function.    
            if 'Sending request to' in message:
                requestId = message.split("(")[1].split(")")[0]
                log_name = str(response['results'][log_entry][3].get('value'))
                log_name = log_name.split(":")[1]
                function_name = message.index('https')
                function_name = message[function_name : ]
                function_name = function_name.split('function:')[1].split(':')[0]
                
                #case: Direct API request to a function, without authentication middle-man
                if requestId not in JWT_tokens.keys():
                    resultJson[result_count-1] = {
                        'endpoint': function_name,
                        'trigger': log_name, 
                        'authentication': is_authentication,
                        'type': 'api-gateway'
                    }
                    continue
                
                #case: The request to the function was indirect, so we want to save it as cognito->function
                elif requestId in JWT_tokens.keys():
                    iss = JWT_tokens.get(requestId) 
                    is_authentication = 1

                    resultJson[result_count-1] = {
                        'endpoint': function_name,
                        'trigger': "aws:cognito-idp", #cognito link-string
                        'authentication': is_authentication,
                        'type': 'api-gateway'
                    }
                continue
            
            
            #case: if it was none of the above, then we move on, but redo this number
            else:
                result_count -= 1
                
            
    createInventory(resultJson, date_from_epoch, date_to_epoch)
    
    
    
def createInventory(event, date_from_epoch, date_to_epoch):
    file_name = "inventory.json"
    
    date_from_str = datetime.fromtimestamp(date_from_epoch)
    date_to_str = datetime.fromtimestamp(date_to_epoch)
    
    if len(event) == 0:
        file_name = makeFileName(file_name, date_from_epoch, date_to_epoch, date_from_str, date_to_str)
        s3_path = "day_summaries/" + str(date_from_str.year) + checkDateNulls(date_from_str.month) + "/" + checkDateNulls(date_from_str.day) + "/" + file_name
        s3.Bucket(bucket_name).put_object(Key=s3_path, Body=str(json.dumps({})))
        return 0
    

    #For eventmessage
    triggered_functions = []
    triggers = []
    authentications = []
    
    event_count = {}
    
    #For function
    service_actions = []
    service_endpoints = []
    locations = []
    table = []
    
    operation_count = {}
    param_value = ''
    
    log_report_length = len(event)
    # Going through each received log message
    for n in range(log_report_length):
        

        log_message = event[n]
        log_message_type = log_message['type']
            
        if log_message_type == 'function':
            operation_name = log_message['operation_name']
            operation_params = log_message['operation_params']
            location = log_message['location'].replace("/aws/lambda/", "")
            #case: type of name the sample app likes to provide. Has senseless characters at the end.
            if location[-13:-12] == "-":
                location = location[:-13] #Get rid of senseless chars at end of function names
            operation_params = ast.literal_eval(operation_params.replace("<", '"').replace(">", '"'))
            endpoint_url = operation_params.get("url")
                

            if "lambda" in endpoint_url:
                endpoint_url = endpoint_url.split("/")[-2].replace('%3A', ':') #last part converts ASCII
                endpoint_url = endpoint_url.split(':')[-1]

            if "queue" in endpoint_url:
                param_value = operation_params.get("body").get("QueueUrl").split("/")[-1] #queue name
                endpoint_url = "aws:sqs"

            #case: it's a dynamodb action
            elif "dynamodb" in endpoint_url:
                body_component = str(operation_params.get("body"), "UTF-8")
                table_name = body_component.split(",")[0].split(" ")[1]
                table_name = table_name.strip(":").strip("{").strip('"')
                param_value = table_name
                #change url
                endpoint_url = "aws:dynamodb"
            #case: it's not a dynamodb action
            else:
                param_value = ''

            service_actions, service_endpoints, locations, table, operation_count = summarizeFunctionCalls(service_actions, service_endpoints, locations, table, operation_name, endpoint_url, location, param_value, operation_count)


        if log_message_type == 'eventmessage' or log_message_type == 'api-gateway':
            function_name = str(log_message.get("endpoint"))
            if ('cognito' not in function_name) and ('sqs' not in function_name) and ('dynamo' not in function_name):
                function_name = function_name[:-13]
            trigger = str(log_message.get("trigger"))
            is_authentication = str(log_message.get("authentication"))
            unique_events = len(triggered_functions)
            
            if "cognito" in function_name:
                function_name = "aws:cognito-idp"
            
            triggered_functions, triggers, authentications, event_count = summarizeServiceCalls(unique_events, triggered_functions, triggers, authentications, function_name, trigger, is_authentication, event_count)

    listA_length = len(service_actions)
    listB_length = len(triggered_functions)
    
    #inject data from function calls
    inventory = createInventoryFromFunctionCalls(listA_length, locations, service_actions, service_endpoints, table, operation_count)

    #incorporate data from service calls
    inventory = createInventoryFromServiceCalls(inventory, listA_length, listB_length, triggered_functions, triggers, authentications, event_count)
    

    file_name = makeFileName(file_name, date_from_epoch, date_to_epoch, date_from_str, date_to_str)

    putToS3(date_from_str, file_name, inventory)
    #s3_path = "day_summaries/" + str(date_from_str.year) + checkDateNulls(date_from_str.month) + "/" + checkDateNulls(date_from_str.day) + "/" + file_name
    #s3.Bucket(bucket_name).put_object(Key=s3_path, Body=str(json.dumps(inventory)))


    
def checkDateNulls(date):
    date = str(date)
    if len(date)==1:
        date = '0'+date
    return date
    
    
def summarizeFunctionCalls(operations, endpoints, locations, table_info, operation_name, endpoint_url, location, param_value, operation_count):
    unique_operations = len(operations)
    #case: list isn't empty
    if not unique_operations==0:
        differences_counter = 0
        # Go through recorded messages and compare with current one
        for i in range(unique_operations):
                
            #case: we have recorded this type of operation before
            if operations[i]==operation_name and endpoints[i]==endpoint_url and locations[i]==location and table_info[i]==str(param_value):
                complete_string = location + operation_name + endpoint_url + param_value
                operation_count[complete_string] += 1
                break
                    
            #case: the new log message is different than the one we're looking at
            elif operations[i]!=operation_name or endpoints[i]!=endpoint_url or locations[i]!=location or table_info[i]!=str(param_value):
                differences_counter += 1
                    
                #case: the new log message is different from each of the ones we've looked at
                if differences_counter == unique_operations:
                    operations.append(operation_name)
                    endpoints.append(endpoint_url)
                    locations.append(location)
                    table_info.append(param_value) #this appends ": " if its not a db operation
                    complete_string = location + operation_name + endpoint_url + param_value
                    operation_count[complete_string] = 1
                    break
    
    #case: list is empty, so add current operation
    else:
        operations.append(operation_name)
        endpoints.append(endpoint_url)
        locations.append(location)
        table_info.append(param_value)
        complete_string = location + operation_name + endpoint_url + param_value
        operation_count[complete_string] = 1
    
    return operations, endpoints, locations, table_info, operation_count
    
    

def summarizeServiceCalls(unique_events, triggered_functions, triggers, authentications, function_name, trigger, is_authentication, event_count):
    #case: list not empty
    if not unique_events == 0:
        differences_counter = 0
        for event_number in range(unique_events):
            #case: we have recorded this type of event before
            if triggered_functions[event_number]==function_name and triggers[event_number]==trigger and authentications[event_number]==is_authentication:
                eventkey = str(function_name + trigger + is_authentication) #  + service
                event_count[eventkey] += 1
                break
                    
            #case: the new log message is different than the one we're looking at
            elif triggered_functions[event_number]!=function_name or triggers[event_number]!=trigger or authentications[event_number]!=is_authentication:
                differences_counter += 1
                        
                #case: the new log message is different from each of the ones we've looked at
                if differences_counter == unique_events:
                    triggered_functions.append(function_name)
                    triggers.append(trigger)
                    authentications.append(is_authentication)
                    eventkey = str(function_name + trigger + is_authentication) #  + service
                    event_count[eventkey] = 1

    #case: list empty, so add current event
    else:
        triggered_functions.append(function_name)
        triggers.append(trigger)
        authentications.append(is_authentication)
        eventkey = str(function_name + trigger + is_authentication) # + service
        event_count[eventkey] = 1
        
    return triggered_functions, triggers, authentications, event_count
    
    
def createInventoryFromFunctionCalls(listA_length, locations, service_actions, service_endpoints, table, operation_count):
    inventory = {}
    for i in range(listA_length):
        counter_list_key = str(locations[i] + service_actions[i] + service_endpoints[i] + table[i])
        appropriate_count = operation_count.get(counter_list_key)
        
        inventory[i] = {
            'source': locations[i],
            'terminus': service_endpoints[i],
            'terminus_location': table[i],
            'via': service_actions[i],
            'count': appropriate_count
        }
        
    return inventory
    
    
def createInventoryFromServiceCalls(inventory, listA_length, listB_length, triggered_functions, triggers, authentications, event_count):
    for j in range(listB_length):
        appropriate_count = event_count[str(triggered_functions[j] + triggers[j] + authentications[j])]
        terminus_location = ""
        
        if "aws:dynamodb" in triggers[j]:
            triggers[j] = triggers[j].split("|")[0]
            
        if "aws:sqs" in triggers[j]: #aws:sqs?
            triggers[j] = triggers[j].split("|")[0]
       

        #the dumb cognito messages don't have queue trigger cause they're not from a queue
        #they also don't have an eventSource, so no 'via',
        inventory[listA_length + j] = {
            'source': triggers[j], #This might be too much information, but we need the redundancy because we don't catch service->service in the requests
            'terminus': triggered_functions[j],
            'terminus_location': terminus_location,
            'count': appropriate_count
        }
    
    return inventory
    
def makeFileName(file_name, date_from_epoch, date_to_epoch, date_from_str, date_to_str):
    #case: requested time frame is shorter than a day (-5 minutes to avoid errors)
    if date_to_epoch-date_from_epoch < 86100:
        #Check which timestamp marks the incomplete day and put that as the prefix
        #case: incomplete to-day
        if date_from_str.hour == 0 and date_from_str.minute == 0:
            file_name = str(date_to_epoch) + "_" + file_name
        #case: incomplete from-day
        elif date_to_str.hour == 0 and date_to_str.minute == 0:
            file_name = str(date_from_epoch) + "_" + file_name
        #case: query if for time within 1 day
        else: 
            #if both are incomplete, name it after the 'to'
            file_name = str(date_to_epoch) + "_" + file_name
    
    return file_name

def queryCloudwatch(LOG_GROUPS, query, date_from_epoch, date_to_epoch):

    return logs_client.start_query(
            logGroupNames= LOG_GROUPS,
            queryString=query,
            startTime=int(date_from_epoch),
            endTime=int(date_to_epoch)
    )

def getQueryResults(query_id):
    return logs_client.get_query_results(queryId=query_id)

def putToS3(date_from_str, file_name, inventory):

    s3_path = "day_summaries/" + str(date_from_str.year) + checkDateNulls(date_from_str.month) + "/" + checkDateNulls(date_from_str.day) + "/" + file_name
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=str(json.dumps(inventory)))