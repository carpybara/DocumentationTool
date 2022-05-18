import json
import boto3
from datetime import datetime, timedelta
import time
import ast
import os

s3_client = boto3.client("s3")
S3_BUCKET = os.environ["SUMMARY_BUCKET"]
lambda_client = boto3.client('lambda')
LogWorkerARN = os.environ['LOGWORKER_ARN']
VersionWorkerARN = os.environ['VERSIONWORKER_ARN']


def fetcher_handler(event, context):

    if LogWorkerARN=="TODO" or VersionWorkerARN=="TODO":
        print("YAML Configurations incorrect!")
        return -1

    merged_inventory = {}
    merged_versions = {}
    
    #case: invoke from CheckForDeployment
    if "flag" in event:
        flag = event.get("flag")
        date_to_epoch = event.get("to")
    
    #case: request via API
    else:
        configuration = json.loads(event.get("body"))
        date_from_epoch = configuration.get("from")
        date_to_epoch = configuration.get("to")
        flag = configuration.get("flag")
    
    isOnlyFullDays = False

    #case: empty 'from' means deployment documentation 
    if flag == "deployment":
        #Find out 'from' via S3
        date_from_epoch = int(getLastDeploymentDate())
        date_to_epoch = int(date_to_epoch)
    
    else:
        date_from_epoch = int(date_from_epoch)
        date_to_epoch = int(date_to_epoch)
        
    date_from_date = datetime.fromtimestamp(date_from_epoch)
    date_to_date = datetime.fromtimestamp(date_to_epoch)
    
    #case: request of only full days 
    if date_from_date.hour==0 and date_to_date.hour==0 and date_to_date.minute == 0 and date_from_date.minute == 0:
        isOnlyFullDays = True
        #Fetch full day files
        isMissing, files = checkAndFetchFiles(date_from_epoch, date_to_epoch)
    
    #case: request of not only full days    
    else:
        #Invoke workers for incomplete days async
        requestDocsForPartDays(date_from_epoch, date_to_epoch)
            
        #Get full days
        complete_from, complete_to = stripIncompleteDaysFromTimestamp(date_from_epoch, date_to_epoch)
         
        #If the query is for one incomplete day, then complete_from==complete_to.
        #case: there are complete days to get.
        if not complete_from==complete_to:
            #Fetch full day files
            isMissing, files = checkAndFetchFiles(complete_from, complete_to)
        
        #case: if there are no complete days to fetch, then there aren't any files or missing objects.
        else:
            files = {}
            isMissing = []
            

    #Abort if one of the full days was missing as well
    if sum(isMissing)>0:
        return_msg = "Data missing for these dates. Call again soon."
        return makeReturn(404, return_msg)
        
    #case: if both objects are empty, then we don't want to merge.
    if files or len(isMissing)!=0:
        
        #Summarizes days. If isDeploymentDocumentationRequest, files is different, so it summarizes just full days.
        merged_inventory, merged_versions = mergeAllFiles(files, merged_inventory, merged_versions)
    
    #case: we need to pick up the requested data extraction results for the incomplete days.
    if not isOnlyFullDays:
        from_contents = []
        to_contents = []
        
        #case: from date is not an incomplete day, so 'to' must have the incomplete day.
        if date_from_date.hour == 0 and date_from_date.minute == 0:
            to_contents = checkS3ForIncompleteDocs(date_to_epoch)
            
        #case: 'to' day is not incomplete, so 'from' must be.
        elif date_to_date.hour == 0 and date_to_date.minute == 0:
            from_contents = checkS3ForIncompleteDocs(date_from_epoch)
        

        #case: both days are incomplete
        elif (date_to_date.hour!=0 or date_to_date.minute!=0) and (date_from_date.hour!=0 or date_from_date.minute!=0) and (date_from_date.day!=date_to_date.day) and (date_from_date.month!=date_to_date.month):
            #Check S3 until incomplete docs exist
            from_contents = checkS3ForIncompleteDocs(date_from_epoch)
            to_contents = checkS3ForIncompleteDocs(date_to_epoch)
        elif (date_to_date.hour!=0 or date_to_date.minute!=0) and (date_from_date.hour!=0 or date_from_date.minute!=0) and (date_from_date.day==date_to_date.day) and (date_from_date.month==date_to_date.month):
            to_contents = checkS3ForIncompleteDocs(date_to_epoch)
    
    
        #merge the two, then call populateFileDict on it with a new/empty files dict.
        files_incompleteDocs = {}
        files_incompleteDocs = populateFileDict(from_contents+to_contents, files_incompleteDocs)

        #mergeAllFiles with files_incompleteDocs and the merged_inventory, merged_versions items that are already used/partially filled
        merged_inventory, merged_versions = mergeAllFiles(files_incompleteDocs, merged_inventory, merged_versions)
      
      
    #Round before sending off
    #merged_versions = roundVersionAttributes(merged_versions)
    merged_total = {"inventory": merged_inventory, "versions": merged_versions}
    
    
    if flag == "deployment":
        #Save documentation in S3 instead of returning.
        path = 'deployment_summaries/ArchitectureState_until_' + str(date_to_date.year) + checkDateNulls(date_to_date.month) + checkDateNulls(date_to_date.day) + 'T' + checkDateNulls(date_to_date.hour) + checkDateNulls(date_to_date.minute) + checkDateNulls(date_to_date.second) + '.json'
        s3_client.put_object(Key=path, Bucket=S3_BUCKET ,Body=str(json.dumps(merged_total)))

        return makeReturn(200, 'Deployment documentation created.')
        
    else:
        return makeReturn(200, merged_total)


def roundAttributes(keyValuePair):
    for key in keyValuePair.keys():
        if not isinstance(keyValuePair[key], list):
            keyValuePair[key] = round(keyValuePair[key], 3)
    return keyValuePair
    
    
def getMaxVersionOfFunction(inputDict):
    functionTOMaxVersion = {}
    copyDict = inputDict.copy()
    for f_name, entry in copyDict.items():
        if f_name != 'stats':
            temp_stats = entry.pop('stats')
            functionTOMaxVersion[f_name] = max(entry.keys())
            entry['stats'] = temp_stats 
          
    return functionTOMaxVersion
 
    
def weightedAverage(value1, weight1, value2, weight2):
    return ((value1*weight1 + value2*weight2) / (weight1+weight2))
 
    
def getLastDeploymentDate():
    '''
    Get last deployment date from the S3 bucket where documentation is saved.
    If no deployment documentation is available, return date of 1 week ago.
    '''
    S3_prefix = "deployment_summaries"
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_prefix, StartAfter=S3_prefix)
    if "Contents" in response:
        s3_files = response["Contents"]
        max_date = -1
        for file in s3_files:
            file_date = file['LastModified'].timestamp()
            
            if file_date > max_date:
                max_date = file_date
                
        print("summaries available")
        return max_date
        
    else:
        print("no summaries available")
        date_object = datetime.now()
        return (datetime(date_object.year, date_object.month, date_object.day) - timedelta(days=7)).timestamp()
  
        
def requestDocsForPartDays(time_from, time_to):
    #case: either incomplete days at from AND to, or just one of both.
    
    date_from = datetime.fromtimestamp(time_from)
    date_to = datetime.fromtimestamp(time_to)
    
    #Need the next midnight to know the end of the 'from' day and the prev midnight
    # for the beginning of the 'to' day.
    #case: 'from' day is a complete
    if date_from.hour==0 and date_from.minute==0:
        next_midnight = datetime(date_from.year, date_from.month, date_from.day).timestamp()
    else:
        next_midnight = datetime(date_from.year, date_from.month, date_from.day+1).timestamp()
        
    prev_midnight = datetime(date_to.year, date_to.month, date_to.day).timestamp()
    
    incomplete_day_from = {
        "date_from": time_from,
        "date_to": int(next_midnight),
        "isDaily": 0
    }
    incomplete_day_to = {
        "date_from": int(prev_midnight),
        "date_to": time_to,
        "isDaily": 0
    }
    
    #case: only incomplete day on the "from"
    if (date_from.hour!=0 or date_from.minute!=0) and (date_to.hour==0 and date_to.minute == 0):
        #only request incomplete_day_from
        invokeVersionWorker(incomplete_day_from)
        invokeLogWorker(incomplete_day_from)
        
        
    #case: only incomplete day on the "to"
    elif (date_to.hour!=0 or date_to.minute != 0) and (date_from.hour==0 and date_from.minute==0):
        invokeVersionWorker(incomplete_day_to)
        invokeLogWorker(incomplete_day_to)
        
    #case: query is only requesting within a single day.
    elif (date_to.hour!=0 or date_to.minute != 0) and (date_from.hour!=0 or date_from.minute!=0) and date_from.day==date_to.day and date_from.month==date_to.month:
        request = {
            "date_from": time_from,
            "date_to": time_to,
            "isDaily": 0
        }
        invokeVersionWorker(request)
        invokeLogWorker(request)
        
    #case: from and to days are incomplete.
    else:
        invokeVersionWorker(incomplete_day_from)
        invokeLogWorker(incomplete_day_from)
        invokeVersionWorker(incomplete_day_to)
        invokeLogWorker(incomplete_day_to)
   
    
def invokeVersionWorker(date):
    lambda_client.invoke(
        FunctionName = VersionWorkerARN,
        InvocationType = 'Event',
        Payload = json.dumps(date)
    )
    
    
def invokeLogWorker(date):
    lambda_client.invoke(
        FunctionName = LogWorkerARN,
        InvocationType = 'Event',
        Payload = json.dumps(date)
    )
    
    
def mergeInventories(inventory_file, merger_object):
    addition_dict = {}
    addition_dict_keys = []
    #iterating through current inventory file
    for (index, inventory_entry) in inventory_file.items():
        counting_differences = 0
        via_currentInventory = ''
        if len(inventory_entry)==5:
            via_currentInventory = inventory_entry['via']
                    
        #iterating through the summary we are creating
        for (n, merged_item) in merger_object.items():
            via_mergedInventory = ''
            if len(merged_item)==5:
                via_mergedInventory = merged_item['via']
                        
            #case: The entry already exists in the summary we are creating, so we can just add the counted operations and move on.
            if inventory_entry['source']==merged_item['source'] and inventory_entry['terminus']==merged_item['terminus'] and inventory_entry['terminus_location']==merged_item['terminus_location'] and via_currentInventory==via_mergedInventory:
                merged_item['count'] += inventory_entry['count']
                break
            #case: spotted a difference
            else: counting_differences += 1
                            
            #case: the entry is different from each entry in our summary, add it to the summary
            if counting_differences == len(merger_object): 
                addition_dict[str(len(merger_object))] = inventory_entry
                addition_dict_keys.append(str(len(merger_object)))

    #Final addition of the unique inventory items to our summary    
    if len(addition_dict_keys)>0:
        for addition_key in addition_dict_keys:
            merger_object[addition_key] = addition_dict[addition_key]
            

def mergeVersions(inventory_file, merger_object):
    add_to_functions_dict = {}
       
    #get highest version of each function so we know which stats are more up to date. Relevant for layerList, initDuration, timeout
    latestVersionPerFunction_VersionFile = getMaxVersionOfFunction(inventory_file)
    latestVersionPerFunction_Merger = getMaxVersionOfFunction(merger_object)
    #Iterating through version file 
                
    for (function_name, versions) in inventory_file.items():
        counting_differences = 0
        add_to_versions_dict = {}
                    
        #iterating through version info we have already gathered "so far"
        for (merged_names, merged_version_info) in merger_object.items():
                        
            if merged_names=='stats':
                pass
             #case: we already have function_name in our list
            elif merged_names==function_name:
                            
                #Merge at function level
                new_func_sampled = versions['stats']['func_sampled'] + merged_version_info['stats']['func_sampled']
                new_func_duration = weightedAverage(merged_version_info['stats']['func_avg_billedDuration'], merged_version_info['stats']['func_sampled'], versions['stats']['func_avg_billedDuration'], versions['stats']['func_sampled'])
                new_func_computation = merged_version_info['stats']['func_total_computation'] + versions['stats']['func_total_computation']
                            
                #take stats from most recent version
                highestVersion_Merger = latestVersionPerFunction_Merger[merged_names]
                highestVersion_VersionFile = latestVersionPerFunction_VersionFile[function_name]
                            
                if latestVersionPerFunction_Merger[merged_names] < highestVersion_VersionFile:
                    new_layerList = versions['stats']['layerList']
                    new_timeout = versions['stats']['timeout']
                    new_current_avg_initDuration = versions['stats']['current_avg_initDuration']
                    new_memorySize = versions['stats']['memorySize']
                elif latestVersionPerFunction_Merger[merged_names] > highestVersion_VersionFile:
                    new_layerList = merged_version_info['stats']['layerList']
                    new_timeout = merged_version_info['stats']['timeout']
                    new_current_avg_initDuration = merged_version_info['stats']['current_avg_initDuration']
                    new_memorySize = merged_version_info['stats']['memorySize']
                #case: they equal    
                else:
                    new_layerList = versions['stats']['layerList']
                    new_timeout = versions['stats']['timeout']
                    new_memorySize = versions['stats']['memorySize']
                    new_current_avg_initDuration = weightedAverage(versions['stats']['current_avg_initDuration'], versions[highestVersion_VersionFile][-1]['version_sampled'], merged_version_info['stats']['current_avg_initDuration'], merged_version_info[highestVersion_Merger][-1]['version_sampled'])


                merged_version_info['stats'] = {
                    "func_avg_billedDuration": new_func_duration,
            		"func_total_computation": new_func_computation,
            		"func_sampled": new_func_sampled,
            		"timeout": new_timeout,
            		"current_avg_initDuration": new_current_avg_initDuration,
            		"memorySize": new_memorySize,
            		"layerList": new_layerList
                }
                            
                #Iterate through versions within the function from the new file: versions
                for version_nr, version_data in versions.items():
                    #case: we know about this version
                    if version_nr == 'stats':
                        continue
                    elif version_nr in merged_version_info: #Note: Otherwise merged_version_info.values()?
                        #Merge at version level
                        #Merge time lists
                        #Take out the last element in list (the version stats) so I can simply add the lists together.
                        version_stats_temp1 = version_data.pop()
                        version_stats_temp2 = merged_version_info[version_nr].pop()

                        #Append the timestamps from version_data to merged_version_info
                        merged_version_info[version_nr] = merged_version_info[version_nr] + version_data
                                    
                        #Merge version stats
                        new_sampled = version_stats_temp2['version_sampled'] + version_stats_temp1['version_sampled']
                        new_maxMemory = ((version_stats_temp2['version_avg_maxMemoryUsed'] * version_stats_temp2['version_sampled']) + (version_stats_temp1['version_avg_maxMemoryUsed'] * version_stats_temp1['version_sampled'])) / new_sampled

                                    
                        #Put back at end of the list
                        merged_version_info[version_nr].append({
                            "version_avg_maxMemoryUsed": new_maxMemory,
            				"version_sampled": new_sampled
                        })
                                
                    #case: we have no information about this version yet.
                    else:
                        # Save to be appended to merged_version_info after done iterating over merger_object
                        add_to_versions_dict[merged_names] = {version_nr: version_data}

            #case: these are not the same function
            else: counting_differences += 1
                        
            #case: the entry is different from each entry in our summary, add entire function component to summary, but like later
            if counting_differences == len(merger_object)-1: #-1 because stats shouldn't be counted as a difference?
                add_to_functions_dict[function_name] = versions
                continue #?
    
    #case: There's at least 1 entire function to add        
    if len(add_to_functions_dict)>0:
        for function_name in add_to_functions_dict.keys():
            merger_object[function_name] = add_to_functions_dict[function_name]
    #case: There's at least 1 version to add       
    if len(add_to_versions_dict)>0:
        for function_name in add_to_versions_dict.keys():
            merger_object[function_name] = add_to_versions_dict[function_name] #I think this works....
            
    #Merge on total level
    new_total_computation = merger_object['stats']['app_computation'] + inventory_file['stats']['app_computation']
    new_total_sampled = merger_object['stats']['total_sampled'] + inventory_file['stats']['total_sampled']
                
    merger_object['stats'] = {
        'app_computation': new_total_computation,
        'total_sampled': new_total_sampled
    }           
            
            
def populateFileDict(returned_files, our_files):
    for s3_file in returned_files:
        if ".json" in s3_file["Key"]:
            response_2 = json.dumps(s3_client.get_object(Bucket=S3_BUCKET, Key=s3_file["Key"])["Body"].read().decode("utf-8"))
            our_files[s3_file["Key"]] = json.loads(response_2)
    return our_files
    
            
def checkAndFetchFiles(date_from_epoch, date_to_epoch):
    our_files = {}
    isMissing = []
    
    
    #Convert UNIX to string
    date_from = datetime.fromtimestamp(int(date_from_epoch))
    date_to = datetime.fromtimestamp(int(date_to_epoch))
    time_delta = date_to - date_from
    #Insert function that actually calculates amount of days of span.
    
    incremented_date = date_from
    # day_summaries/202203/23/versions.json is example
    #first run day=0 
    for day in range(int(time_delta.days)): 
        
        S3_prefix = "day_summaries/" + str(incremented_date.year) + checkDateNulls(incremented_date.month) + "/" + checkDateNulls(incremented_date.day)
        

        # Gets all files for a specific date
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_prefix, StartAfter=S3_prefix)
        #work with epoch time
        current_date = {
            "date_from": datetime.timestamp(incremented_date),
            "date_to": datetime.timestamp(incremented_date + timedelta(days=1)),
            "isDaily": 0
        }
        inventory_missing = True
        versions_missing = True

        if "Contents" in response:
            s3_files = response["Contents"]

            for s3_file in s3_files:
                if "inventory.json" in s3_file["Key"]:
                    inventory_missing = False
                if "versions.json" in s3_file["Key"]:
                    versions_missing = False
        else:
            s3_files = []
        
        if inventory_missing:
            invokeLogWorker(current_date)

        if versions_missing:
            invokeVersionWorker(current_date)

        #Need to keep track of if there was ever a file missing.    
        isMissing.append(inventory_missing)
        isMissing.append(versions_missing)
        
        #Moving files from S3 into files dict to work with
        populateFileDict(s3_files, our_files)
        
        incremented_date += timedelta(days=1) #increment date after, so first day isn't skipped.

    return isMissing, our_files
    
def stripIncompleteDaysFromTimestamp(date_from_epoch, date_to_epoch):
    #Timestamp to dates
    date_from = datetime.fromtimestamp(date_from_epoch)
    date_to = datetime.fromtimestamp(date_to_epoch)
        
    #Strip incomplete days
    #case: 'from' day is not incomplete, so don't cut it away.
    if (date_from.hour==0 and date_from.minute==0):
        first_midnight = datetime(date_from.year, date_from.month, date_from.day).timestamp()
        
    #case: the query is only for time within one day.
    elif datetime(date_to.year, date_to.month, date_to.day) == datetime(date_from.year, date_from.month, date_from.day):
        first_midnight =datetime(date_from.year, date_from.month, date_from.day).timestamp()
        
    #case: 'from' day is incomplete, cut it away so we are only left with full days.  
    else:
        first_midnight = datetime(date_from.year, date_from.month, date_from.day+1).timestamp()
    
    #if 'to' day is full, nothing is really cut away. If it's incomplete, something is cut away.
    last_midnight = datetime(date_to.year, date_to.month, date_to.day).timestamp() 
    
    return first_midnight, last_midnight
    
    
    
def makeReturn(statusCode, body):
    return {
                "statusCode": statusCode,
                "headers": {
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Headers" : "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods" : "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                    "Access-Control-Allow-Origin" : '*',
                },
                "body": json.dumps(body)
    }
    
    
def mergeAllFiles(files, merged_inventory, merged_versions):

    #iterating through files
    for (key, summary_object) in files.items():
        summary_object = ast.literal_eval(summary_object)

        #case: inventory file
        if "inventory" in key:
            #case: merged_inventory empty
            if not bool(merged_inventory):
                merged_inventory = summary_object
                
            #case: not empty, so we need to see which entries can be summarized and which have to be appended.
            else:
                mergeInventories(summary_object, merged_inventory)
        

        #case: version file
        if "versions" in key:
            #case: merged memory empty
            if not bool(merged_versions):
                merged_versions = summary_object
            #case: summar object empty    
            elif not bool(summary_object):
                continue
            #case: not empty, so summarize/append
            else:
                mergeVersions(summary_object, merged_versions)
                
    return merged_inventory, merged_versions
    
    
    
def roundVersionAttributes(merged_versions):
    
    merged_versions['stats'] = roundAttributes(merged_versions['stats'])
    for func_name, entry in merged_versions.items():
        if func_name != "stats":
            entry['stats'] = roundAttributes(entry['stats'])
            for version_nr, version_info in entry.items():
                if version_nr != 'stats':
                    version_info.append(roundAttributes(version_info.pop()))
    
    return merged_versions
    
    
def checkS3ForIncompleteDocs(timestampOfIncomplete):
    #Timestamp to date object
    dateOfIncomplete = datetime.fromtimestamp(timestampOfIncomplete)
    
    response = None
    S3_prefix = 'day_summaries/' + str(dateOfIncomplete.year) + checkDateNulls(dateOfIncomplete.month) + '/' + checkDateNulls(dateOfIncomplete.day) +'/' + str(timestampOfIncomplete)#rest of name not necessary
    while response==None:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_prefix, StartAfter=S3_prefix)
        #case: no answer from the query yet
        if response== None:
            time.sleep(1)
            
        #case: queried file wasn't found
        elif response != None and not 'Contents' in response:
            response = None
            time.sleep(1)
        
        elif 'Contents' in response:
            #case: only one object is there so far.
            if len(response['Contents'])<2:
                response = None
                time.sleep(1)
            
            
    return response['Contents']
            

def checkDateNulls(date):
    date = str(date)
    if len(date)==1:
        date = '0'+date
    return date