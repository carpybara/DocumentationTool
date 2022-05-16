import json
import boto3
from datetime import datetime
import os

import gzip

lambda_client = boto3.client('lambda')
s3_client = boto3.client("s3")
BUCKET_NAME = os.environ['CLOUDTRAIL_BUCKET']
FETCHER_ARN = os.environ['FETCHER_ARN']

def lambda_handler(event, context):
    '''
    If a UpdateFunctionCode20150331v2 event occured, we need the date/time.
    It marks the 'to' time for the Fetcher query.
    '''

    if BUCKET_NAME=="TODO" or FETCHER_ARN=="TODO":
        print("YAML Configurations incorrect!")
        return -1
    
    for event_item in event['Records']:
        
        if 's3' not in event_item:
            continue
        if 'bucket' not in event_item['s3']:
            continue
        if event_item['s3']['bucket']['name'] == BUCKET_NAME:
            object_key = event_item['s3']['object']['key']
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_key)['Body'] #.read().decode("utf-8")
            items = gzipToEvent(response)
            
            for item in items['Records']:
                if item['eventName'] == 'UpdateFunctionCode20150331v2':
        
                    eventTime = item['eventTime']
                    timeTo = datetime.timestamp(datetime.strptime(eventTime, '%Y-%m-%dT%H:%M:%S%z')) #string->pythontime->unix #old: %Y-%m-%dT%H:%M:%S.%f%z
            
                    lambda_client.invoke(
                        FunctionName = FETCHER_ARN,
                        InvocationType = 'Event',
                        Payload = json.dumps({
                            'from': '',
                            'to': timeTo,
                            'flag': 'deployment'
                        })
                    )

    return 0
    

def gzipToEvent(file):
    with gzip.open(file, 'r') as fin:
        json_bytes = fin.read()

    json_str = json_bytes.decode('utf-8') 
    data = json.loads(json_str)
    return data
    