import json
import boto3 #remove for testing
import os

s3_client = boto3.client("s3") #replace with '' for testing
S3_BUCKET = os.environ["SUMMARY_BUCKET"] #ditto

def lambda_handler(event, context):
    '''
    If flagged as 'list', get the names of all deployment docs
    If flagged as 'fetch' get it from S3 and return it.
    '''
    config = json.loads(event.get("body"))
    operation_flag = config.get("type")
    S3_prefix = 'deployment_summaries'
    
    deployment_docs = []
    
    if operation_flag == "fetch":
        S3_prefix = config.get("key")
        fetched_file = getRequestedFile(S3_prefix)
        return makeReturn(200, json.dumps(fetched_file))
    
    response = getDeploymentDocList(S3_prefix)
    
    if "Contents" in response:
        s3_files = response["Contents"]
        for file in s3_files: 
 
            #case: we're fetching names of all files
            if ".json" in file["Key"]:
                deployment_docs.append(file["Key"])
        
        return makeReturn(200, json.dumps(deployment_docs))

    else:
        return makeReturn(404, "No deployment documentation exists.")



def makeReturn(statusCode, body):
    return {
                "statusCode": statusCode,
                "headers": {
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Headers" : "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods" : "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                    "Access-Control-Allow-Origin" : "*",
                },
                "body": json.dumps(body)
    }


def getRequestedFile(file_name):
    return json.loads(s3_client.get_object(Bucket=S3_BUCKET, Key=file_name)["Body"].read().decode("utf-8"))


def getDeploymentDocList(S3_prefix):
    return s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_prefix, StartAfter=S3_prefix)