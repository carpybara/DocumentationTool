import json
import boto3 #remove for testing
from datetime import datetime
import time
import os

logs_client = boto3.client('logs', region_name = 'us-east-1') #replace with '' for testing
lambda_client = boto3.client('lambda') #ditto
s3 = boto3.resource("s3") #ditto

query = """fields @timestamp, @message, @log, @type, @requestId, @memorySize, @billedDuration, @maxMemoryUsed, @initDuration | filter (@type='START' or @type='REPORT')"""

LOG_GROUPS = json.loads(os.environ['LOG_GROUPS']) #also here
bucket_name = os.environ["SUMMARY_BUCKET"] #also here

def versionWorker_handler(event, context):
    
    isDaily = int(event.get("isDaily"))
    if isDaily:
        temp = datetime.utcnow().date()
        date_to_epoch = datetime(temp.year, temp.month, temp.day).timestamp()
        date_from_epoch = date_to_epoch - 86400
        
        date_from_str = datetime.fromtimestamp(date_from_epoch)
        date_to_str = datetime.fromtimestamp(date_to_epoch)
    else:
        date_from_epoch = event.get("date_from")
        date_to_epoch = event.get("date_to")
        date_from_str = datetime.fromtimestamp(date_from_epoch)
        date_to_str = datetime.fromtimestamp(date_to_epoch)
    
    file_name = "versions.json"
    
    #Need fixed size list for each detected version of each function. Multi-dimensional dictionary.
    function_version_counter_dict = {}
    #hour_counters = [0] * 24 #Fixed size list for counters.
    unclear_versions_dict = {} # Dict for keeping track of for which functions we need to do the list-versions-by-function call
    #Dict for function->timeout and layers
    additionalFunctionStats = {}
    start_query_response = queryCloudwatch(date_from_epoch, date_to_epoch, date_from_str, date_to_str)


    query_id = start_query_response['queryId']
    response = None
    
    while response == None or response['status'] == 'Running':
        time.sleep(1)
        response = getQueryResults(query_id)#logs_client.get_query_results(queryId=query_id)
        
    
    START_msgs = []
    REPORT_msgs = []
    rqId_to_Ver = {} # RequestId->Version mapping
    #This last one is necessray to connect version information with performance information from REPORT messages.
    
    if response and response['results'] and response['results'][0]:
    
        for log_entry in range(len(response['results'])):
            message_type = str(response['results'][log_entry][3].get('value'))
            
            if message_type == "START":
                START_msgs.append(response['results'][log_entry])

            if message_type == "REPORT":
                REPORT_msgs.append(response['results'][log_entry])



    unclear_versions_dict, additionalFunctionStats, function_version_counter_dict, rqId_to_Ver = processStartMessages(START_msgs, unclear_versions_dict, additionalFunctionStats, function_version_counter_dict, rqId_to_Ver)

    additionalFunctionStats, function_version_counter_dict, rqId_to_Ver = resolveVersions(unclear_versions_dict, additionalFunctionStats, function_version_counter_dict, rqId_to_Ver)
    #Now we have call counts per version in function_version_counter_dict and a rqId->version mapping to attribute stats from REPORT messages to the correct version


    functionInitDurations = {}
    
    #Need the max version for each function, don't think i have it anywhere else...
    functionTOMaxVersion = getMaxVersionOfFunction(function_version_counter_dict)
    
    
    rqId_to_Ver, additionalFunctionStats, functionInitDurations, function_version_counter_dict = processReportMessages(REPORT_msgs, functionTOMaxVersion, rqId_to_Ver, additionalFunctionStats, functionInitDurations, function_version_counter_dict)

    function_version_counter_dict = processVersioningData(function_version_counter_dict)

    function_version_counter_dict = createTotalStats(function_version_counter_dict, additionalFunctionStats, functionInitDurations)
    
    #removes no longer needed data per version
    function_version_counter_dict = removeExcessData(function_version_counter_dict)

    #case: requested time frame is shorter than a day (-5 minutes to avoid errors)
    if date_to_epoch-date_from_epoch < 86100:
        #Check which timestamp marks the incomplete day and put that as the prefix
        #case: incomplete to-day
        if date_from_str.hour == 0 and date_from_str.minute == 0:
            file_name = str(date_to_epoch) + "_" + file_name
        #case: incomplete from-day
        elif date_to_str.hour == 0 and date_to_str.minute == 0:
            file_name = str(date_from_epoch) + "_" + file_name
        else: 
            #if both are incomplete, name it after the 'to'
            file_name = str(date_to_epoch) + "_" + file_name

    putToS3(date_from_str, file_name, function_version_counter_dict)
    #s3_path = "day_summaries/" + str(date_from_str.year) + checkDateNulls(date_from_str.month) + "/" + checkDateNulls(date_from_str.day) + "/" + file_name
    #s3.Bucket(bucket_name).put_object(Key=s3_path, Body=str(json.dumps(function_version_counter_dict)))

    return 0

    

def shortenNames(inputDict):
    corrected_dict = {}
    # List comprehension: if "-" is detected near the end, we cut the name off there, because of senseless chars.
    #   else, use normal name.
    corrected_dict = { (k[:-13] if (k[-13:-12]=='-') else k): v for k, v in inputDict.items() }
    return corrected_dict
    
    
def getFunctionStats(function_name):
    Versions = getVersionsByFunction(function_name)['Versions']
    #Versions = lambda_client.list_versions_by_function(FunctionName=function_name)['Versions']
    for entry in Versions:
        if "LATEST" in entry['Version']:
            if "Layers" not in entry.keys():
                return {
                'layerList': '',
                'timeout': entry['Timeout']
                }
            
            return {
                'layerList': entry['Layers'],
                'timeout': entry['Timeout']
            }
    return -1
            
def getMaxVersionOfFunction(inputDict):
    functionTOMaxVersion = {}
    for f_name, entry in inputDict.items(): #stats doesn't exist here yet, no catch necessary
        functionTOMaxVersion[f_name] = max(entry.keys())
    return functionTOMaxVersion
    
def checkDateNulls(date):
    date = str(date)
    if len(date)==1:
        date = '0'+date
    return date
    
    
def queryCloudwatch(date_from_epoch, date_to_epoch, date_from_str, date_to_str):

    start_query_response = logs_client.start_query(
        logGroupNames= LOG_GROUPS,
        queryString=query,
        startTime=int(date_from_epoch),
        endTime=int(date_to_epoch)
    )
    
    return start_query_response
    
    
def processStartMessages(START_msgs, unclear_versions, additionalStats, function_versions, rqIdToVer):

    #START/Versioning procedures...
    for start_msg in START_msgs:
        message = str(start_msg[1].get('value'))
        timestamp = str(start_msg[0].get('value'))
        timestamp_unix = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        requestId = str(start_msg[4].get('value'))
        function_name = str(start_msg[2].get('value')).split(":")[-1].replace("/aws/lambda/", "")

        #case: resolve unclear version
        if '$LATEST' in message:
            # Each timestamp signifies one call with unclear version. All we need to clear up the version in the time of the call.
            #case: first unclear version for this function 
            if function_name not in unclear_versions.keys():
                unclear_versions[function_name] = []
                
            unclear_version_entry = requestId + "|" + str(timestamp_unix)
            unclear_versions[function_name].append(unclear_version_entry)

        #case: version number is known    
        else:
            #get stats if we haven't yet for this function.
            if function_name not in additionalStats.keys():
                additionalStats[function_name] = getFunctionStats(function_name)
            
            #case: Function unregistered
            if function_name not in function_versions.keys():
                function_versions[function_name] = {}
                
            version_nr_location = message.index("Version: ")
            version_nr = int(message[version_nr_location+9:]) # +9 to get just the version number (as a string, since it is a dict key).
            rqIdToVer[requestId] = version_nr

            #case: Version unregistered, must register.
            if version_nr not in function_versions[function_name].keys():
                function_versions[function_name][version_nr] = []

            function_versions[function_name][version_nr].append(timestamp_unix)

    return unclear_versions, additionalStats, function_versions, rqIdToVer
    
    
    
def resolveVersions(unclear_versions, additionalStats, function_versions, rqIdToVer):
    #Make API request for each functio in unclear_versions.keys() and proceed to compare timestamps.
    for unresolved_function in unclear_versions.keys():
        
        versions_response = getVersionsByFunction(unresolved_function)
        
        #case: success
        if versions_response: #Timeout danger?
            #save the data somewhere and continue to next request?

            #I need to map every timestamp from  unclear_versions[unresolved_function] to a version number from the response.
            version_dict = {}
            versions_known = {-1} # A set to keep track of highest numeric version.
            for entry in versions_response['Versions']:
                if 'Layers' not in entry.keys():
                    additionalStats[entry['FunctionName']] = {
                        'layerList': '',
                        'timeout': entry['Timeout']
                    }
                elif 'LATEST' in entry['Version']:
                    additionalStats[entry['FunctionName']] = {
                        'layerList': entry['Layers'],
                        'timeout': entry['Timeout']
                    }
                
                better_date_str = entry["LastModified"].split('+')[0]
                better_date_str = datetime.strptime(better_date_str, "%Y-%m-%dT%H:%M:%S.%f").timestamp()
                if 'LATEST' in entry["Version"]: 
                    version_dict[better_date_str] = entry["Version"]
                else: 
                    version_dict[better_date_str] = int(entry["Version"])

            #Could also sort the version_dict dates in reverse order so that the first date lower than the timestamp is the one with the respective version
            for entry in unclear_versions[unresolved_function]:
                requestId, timestamp = entry.split("|")
                timestamp = float(timestamp)
                max_date = 0
                max_version = -1

                for version_date, version_nr in version_dict.items():
                    version_date = float(version_date)
                    
                    #case: found numeric version
                    if isinstance(version_nr, int):
                        versions_known.add(version_nr)

                    # To find latest date that is lower than timestamp of function call to find the right version.
                    if version_date > max_date and version_date < timestamp:
                        max_date = version_date
                        max_version = version_nr
                #found the last version before the date
                
                #case: the unresolved function has actual latest version as its version, max_version is not an integer
                if not isinstance(max_version, int):
                    max_version = max(versions_known) + 1
 
                #case: This is only for the first timestamp for this function
                if unresolved_function not in function_versions.keys():
                    function_versions[unresolved_function] = {}
                    function_versions[unresolved_function][max_version] = []
                    function_versions[unresolved_function][max_version].append(timestamp)
                    rqIdToVer[requestId] = max_version
                else:
                    #case: version unregistered
                    if max_version not in function_versions[unresolved_function].keys():
                        function_versions[unresolved_function][max_version] = []

                    function_versions[unresolved_function][max_version].append(timestamp)
                    rqIdToVer[requestId] = max_version
    
    return additionalStats, function_versions, rqIdToVer
    
    
def processReportMessages(msgs, maxVersion, rqIdToVer, additionalStats, functionInits, function_versions):
    for report_msg in msgs:
        #message = str(report_msg[1].get('value'))
        requestId = str(report_msg[4].get('value'))
        function_name = str(report_msg[2].get('value')).split(":")[-1].replace("/aws/lambda/", "")
        memorySize = int(report_msg[5].get('value'))
        billedDuration = int(report_msg[6].get('value'))
        maxMemoryUsed = int(report_msg[7].get('value'))


        #case: Start message missing
        if requestId not in rqIdToVer.keys():
            timestamp = str(report_msg[0].get('value'))
            rqIdToVer[requestId] = '0'
            function_versions[function_name]['0'] = [datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").timestamp()]
            #print(requestId)

        #Not all functions log a init duration, because they may not have to reinitialize.
        #case: it is from the latest version.    
        elif maxVersion[function_name]==rqIdToVer[requestId]:
            additionalStats[function_name]['memorySize'] = memorySize
            #case: initDuration exists
            if len(report_msg[8].get('value'))<40:
                #case: function known
                if function_name in functionInits.keys():
                    functionInits[function_name].append(float(report_msg[8].get('value')))
                #case: function unregistered so far
                else:
                    functionInits[function_name] = [float(report_msg[8].get('value'))]
            #case: no initDuration (must've reused container) and function known
            elif function_name in functionInits.keys():
                functionInits[function_name].append(0)
            #case: no initDuration and function unregistered
            else:
                functionInits[function_name] = [0]
    
        respective_versionNr = rqIdToVer[requestId]
        
        #case: no stat entry yet
        if not isinstance(function_versions[function_name][respective_versionNr][-1], dict):
            function_versions[function_name][respective_versionNr].append({
                'memorySize': memorySize,
                'billedDuration': billedDuration,
                'durationValues': str(billedDuration),
                'maxMemoryUsed': maxMemoryUsed,
                'memoryValues': str(maxMemoryUsed),
                'sampled': 1
            })
        else:
            function_versions[function_name][respective_versionNr][-1]['billedDuration'] += billedDuration
            function_versions[function_name][respective_versionNr][-1]['durationValues'] += ", " + str(billedDuration)
            function_versions[function_name][respective_versionNr][-1]['maxMemoryUsed'] += maxMemoryUsed
            function_versions[function_name][respective_versionNr][-1]['memoryValues'] += ", " + str(maxMemoryUsed)
            function_versions[function_name][respective_versionNr][-1]['sampled'] += 1
            #Divide by sampled to at the end to create averages
    
    return rqIdToVer, additionalStats, functionInits, function_versions
    
    
def processVersioningData(function_versions):
    for versions in function_versions.values():
        
        #Calc avg for each version
        for version in versions.values():
            stats = version[-1]
            version[-1] = {
                #'version_memorySize': stats['memorySize'],
                'version_avg_billedDuration': stats['billedDuration'] / stats['sampled'],
                'version_avg_maxMemoryUsed': stats['maxMemoryUsed'] / stats['sampled'],
                'total_computation': stats['sampled'] * ((stats['billedDuration'] / stats['sampled'])/1000) * (stats['memorySize']/1000000000), # count(#)*avg_duration(s)*memorysize(GB)
                'version_sampled': stats['sampled']
            }
            
        func_avg_billedDuration = 0
        func_total_computation = 0
        func_sampled = 0
        #Calc avg for each function (summarize versions)
        for version in versions.values():
            func_avg_billedDuration += version[-1]['version_avg_billedDuration'] * version[-1]['version_sampled']
            func_total_computation += version[-1]['total_computation']
            func_sampled += version[-1]['version_sampled']

            
        versions['stats'] = {
            'func_avg_billedDuration': func_avg_billedDuration/func_sampled,
            'func_total_computation': func_total_computation,
            'func_sampled': func_sampled
        }
    
    return function_versions
    
    
def createTotalStats(function_versions, additionalStats, functionInits):
    #function_version_counter_dict = createTotalStats(function_version_counter_dict, additionalFunctionStats, functionInitDurations)
    app_computation = 0
    total_sampled = 0
    
    for name, function in function_versions.items():
        app_computation += function['stats']['func_total_computation']
        total_sampled += function['stats']['func_sampled']
        
        #move additional stats from additionalStats to function['stats']
        function['stats']['memorySize'] = additionalStats[name]['memorySize']
        function['stats']['timeout'] = additionalStats[name]['timeout']
        function['stats']['layerList'] = additionalStats[name]['layerList']
        function['stats']['current_avg_initDuration'] = sum(functionInits[name]) / len(functionInits[name])
    
    function_versions = shortenNames(function_versions)   
    
    function_versions['stats'] = {
        'app_computation': app_computation,
        'total_sampled': total_sampled
    }
    
    return function_versions
    
def removeExcessData(versioningDict):
    for func_name, versions in versioningDict.items():
        if func_name!="stats":
            for version_name, data in versions.items():
                if version_name!="stats":
                    data[-1] = {
                        "version_sampled": data[-1]['version_sampled'],
                        "version_avg_maxMemoryUsed": data[-1]['version_avg_maxMemoryUsed']
                    }

    return versioningDict


def getQueryResults(query_id):
    return logs_client.get_query_results(queryId=query_id)


def getVersionsByFunction(func_name):
    return lambda_client.list_versions_by_function(FunctionName=func_name)


def putToS3(date_from_str, file_name, function_version_counter_dict):
    s3_path = "day_summaries/" + str(date_from_str.year) + checkDateNulls(date_from_str.month) + "/" + checkDateNulls(date_from_str.day) + "/" + file_name
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=str(json.dumps(function_version_counter_dict)))
    return 0