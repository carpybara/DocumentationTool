import datetime
import unittest
import json
from unittest import mock

# Setting the default AWS region environment variable required by the Python SDK boto3
with mock.patch.dict('os.environ', {'AWS_REGION': 'us-east-1'}):
    from DeploymentFetcher import lambda_handler


def mocked_getRequestedFile(file_name):
    return json.loads("deployment_summaries/ArchitectureState_until_20220321T155500.json")


def mocked_getDeploymentDocList(S3_prefix):
    x = datetime.date(2015, 1, 1)
    return  {
    'IsTruncated': True|False,
    'Contents': [
        {
            'Key': 'deployment_summaries/ArchitectureState_until_20220321T155500.json',
            'LastModified': x,
            'ETag': 'string',
            'ChecksumAlgorithm': [
                '',
            ],
            'Size': 123,
            'StorageClass': '',
            'Owner': {
                'DisplayName': 'string',
                'ID': 'string'
            }
        },
    ],
    'Name': 'string',
    'Prefix': 'string',
    'Delimiter': 'string',
    'MaxKeys': 123,
    'CommonPrefixes': [
        {
            'Prefix': 'string'
        },
    ],
    'EncodingType': 'url',
    'KeyCount': 123,
    'ContinuationToken': 'string',
    'NextContinuationToken': 'string',
    'StartAfter': 'string'
}



class logWorkerTest(unittest.TestCase):

    @mock.patch('DeploymentFetcher.getRequestedFile', side_effect=mocked_getRequestedFile)
    @mock.patch('DeploymentFetcher.getDeploymentDocList', side_effect=mocked_getDeploymentDocList)
    def test_inventory_success(self, getRequestedFile_mock, getDeploymentDocList_mock):
        response = lambda_handler(self.deploymentFetcherEvent(), "")
        body = json.dumps(["deployment_summaries/ArchitectureState_until_20220321T155500.json"])
        statusCode = 200
        expected_response = {
                "statusCode": statusCode,
                "headers": {
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Headers" : "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods" : "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                    "Access-Control-Allow-Origin" : "*",
                },
                "body": json.dumps(body)
    }
        

        self.assertEqual(getRequestedFile_mock.call_count, 1)
        self.assertEqual(getDeploymentDocList_mock.call_count, 0)
        self.assertEqual(response, expected_response)



    def deploymentFetcherEvent(self):
        return {
  "resource": "/fetcher",
  "path": "/fetcher",
  "httpMethod": "POST",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,de;q=0.8",
    "content-type": "application/json",
    "Host": "k9k78hhull.execute-api.us-east-1.amazonaws.com",
    "origin": "http://localhost:3000",
    "referer": "http://localhost:3000/",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "X-Amzn-Trace-Id": "Root=1-6234d3a0-5a72d11b2ad114ec1c7448e2",
    "X-Forwarded-For": "95.91.243.202",
    "X-Forwarded-Port": "443",
    "X-Forwarded-Proto": "https"
  },
  "multiValueHeaders": {
    "accept": [
      "*/*"
    ],
    "accept-encoding": [
      "gzip, deflate, br"
    ],
    "accept-language": [
      "en-US,en;q=0.9,de;q=0.8"
    ],
    "content-type": [
      "application/json"
    ],
    "Host": [
      "k9k78hhull.execute-api.us-east-1.amazonaws.com"
    ],
    "origin": [
      "http://localhost:3000"
    ],
    "referer": [
      "http://localhost:3000/"
    ],
    "sec-ch-ua": [
      "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\""
    ],
    "sec-ch-ua-mobile": [
      "?0"
    ],
    "sec-ch-ua-platform": [
      "\"Linux\""
    ],
    "sec-fetch-dest": [
      "empty"
    ],
    "sec-fetch-mode": [
      "cors"
    ],
    "sec-fetch-site": [
      "cross-site"
    ],
    "User-Agent": [
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    ],
    "X-Amzn-Trace-Id": [
      "Root=1-6234d3a0-5a72d11b2ad114ec1c7448e2"
    ],
    "X-Forwarded-For": [
      "95.91.243.202"
    ],
    "X-Forwarded-Port": [
      "443"
    ],
    "X-Forwarded-Proto": [
      "https"
    ]
  },
  "queryStringParameters": "None",
  "multiValueQueryStringParameters": "None",
  "pathParameters": "None",
  "stageVariables": "None",
  "requestContext": {
    "resourceId": "r5j8my",
    "resourcePath": "/fetcher",
    "httpMethod": "POST",
    "extendedRequestId": "PMYBLGLDoAMF3Nw=",
    "requestTime": "18/Mar/2022:18:46:56 +0000",
    "path": "/Test/fetcher",
    "accountId": "622370397643",
    "protocol": "HTTP/1.1",
    "stage": "Test",
    "domainPrefix": "k9k78hhull",
    "requestTimeEpoch": 1647629216974,
    "requestId": "c4676aa1-f496-4ea3-bbb0-ade35c6441f7",
    "identity": {
      "cognitoIdentityPoolId": "None",
      "accountId": "None",
      "cognitoIdentityId": "None",
      "caller": "None",
      "sourceIp": "95.91.243.202",
      "principalOrgId": "None",
      "accessKey": "None",
      "cognitoAuthenticationType": "None",
      "cognitoAuthenticationProvider": "None",
      "userArn": "None",
      "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
      "user": "None"
    },
    "domainName": "k9k78hhull.execute-api.us-east-1.amazonaws.com",
    "apiId": "k9k78hhull"
  },
  "body": "{\"type\":\"list\",\"key\":\"deployment_summaries/ArchitectureState_until_20220321T155500.json\"}",
  "isBase64Encoded": False
}