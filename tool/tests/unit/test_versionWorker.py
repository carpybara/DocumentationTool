import unittest
from unittest import mock

# Setting the default AWS region environment variable required by the Python SDK boto3
with mock.patch.dict('os.environ', {'AWS_REGION': 'us-east-1'}):
    from versionWorker import versionWorker_handler


def mocked_queryCloudwatch(LOG_GROUPS, query, date_from_epoch, date_to_epoch):
    return {
        "queryId": "12ab3456-12ab-123a-789e-1234567890ab"
    }


def mocked_getQueryResults(query_id):
    return {
    "results": [
        [
            {
                "field": "@timestamp",
                "value": "2022-05-02 20:58:14.456"
            },
            {
                "field": "@message",
                "value": "REPORT RequestId: f612fbaf-65ce-4fd2-8d1b-6718fcb0b269\tDuration: 2.03 ms\tBilled Duration: 3 ms\tMemory Size: 512 MB\tMax Memory Used: 70 MB\t\n"
            },
            {
                "field": "@log",
                "value": "622370397643:/aws/lambda/aws-serverless-shopping-cart-s-CartDBStreamHandler-r2hrhRoaOdTT"
            },
            {
                "field": "@type",
                "value": "REPORT"
            },
            {
                "field": "@requestId",
                "value": "f612fbaf-65ce-4fd2-8d1b-6718fcb0b269"
            },
            {
                "field": "@memorySize",
                "value": "512000000"
            },
            {
                "field": "@billedDuration",
                "value": "3"
            },
            {
                "field": "@maxMemoryUsed",
                "value": "70000000"
            }
        ],
        [
            {
                "field": "@timestamp",
                "value": "2022-05-02 20:58:14.452"
            },
            {
                "field": "@message",
                "value": "START RequestId: f612fbaf-65ce-4fd2-8d1b-6718fcb0b269 Version: 3\n"
            },
            {
                "field": "@log",
                "value": "622370397643:/aws/lambda/aws-serverless-shopping-cart-s-CartDBStreamHandler-r2hrhRoaOdTT"
            },
            {
                "field": "@type",
                "value": "START"
            },
            {
                "field": "@requestId",
                "value": "f612fbaf-65ce-4fd2-8d1b-6718fcb0b269"
            }
        ],
    ],
    "statistics": {
        "bytesScanned": 49723,
        "recordsMatched": 2,
        "recordsScanned": 1000
    },
    "status": "Complete"
    }


def mocked_getVersionsByFunction(func_name):
    return {
        "NextMarker": "string",
        "Versions": [ 
        { 
            "Architectures": [ "string" ],
            "CodeSha256": "string",
            "CodeSize": 100,
            "DeadLetterConfig": { 
                "TargetArn": "string"
            },
            "Description": "string",
            "Environment": { 
                "Error": { 
                "ErrorCode": "string",
                "Message": "string"
                },
                "Variables": { 
                "string" : "string" 
                }
            },
            "EphemeralStorage": { 
                "Size": 512
            },
            "FileSystemConfigs": [ 
                { 
                "Arn": "string",
                "LocalMountPath": "string"
                }
            ],
            "FunctionArn": "string",
            "FunctionName": "622370397643:/aws/lambda/aws-serverless-shopping-cart-s-CartDBStreamHandler-r2hrhRoaOdTT",#TODO
            "Handler": "string",
            "ImageConfigResponse": { 
                "Error": { 
                "ErrorCode": "string",
                "Message": "string"
                },
                "ImageConfig": { 
                "Command": [ "string" ],
                "EntryPoint": [ "string" ],
                "WorkingDirectory": "string"
                }
            },
            "KMSKeyArn": "string",
            "LastModified": "1997-07-16T19:20:30.45+01:00", #TODO
            "LastUpdateStatus": "string",
            "LastUpdateStatusReason": "string",
            "LastUpdateStatusReasonCode": "string",
            "Layers": [ 
                { 
                "Arn": "string",
                "CodeSize": 50,
                "SigningJobArn": "string",
                "SigningProfileVersionArn": "string"
                }
            ],
            "MasterArn": "string",
            "MemorySize": 100,
            "PackageType": "string",
            "RevisionId": "string",
            "Role": "string",
            "Runtime": "string",
            "SigningJobArn": "string",
            "SigningProfileVersionArn": "string",
            "State": "string",
            "StateReason": "string",
            "StateReasonCode": "string",
            "Timeout": 10,
            "TracingConfig": { 
                "Mode": "string"
            },
            "Version": "3",
            "VpcConfig": { 
                "SecurityGroupIds": [ "string" ],
                "SubnetIds": [ "string" ],
                "VpcId": "string"
            }
        }
        ]
    }


def mocked_putToS3(date_from_str, file_name, function_version_counter_dict):
    return 0


'''
class versionWorkerTest(unittest.TestCase):

    @mock.patch('versionWorker.queryCloudwatch', side_effect=mocked_queryCloudwatch)
    @mock.patch('versionWorker.getQueryResults', side_effect=mocked_getQueryResults)
    @mock.patch('versionWorker.putToS3', side_effect=mocked_putToS3)
    @mock.patch('versionWorker.getVersionsByFunction', side_effect=mocked_getVersionsByFunction)
    def test_inventory_success(self, queryCloudwatch_mock, getQueryResults_mock, putToS3_mock, getVersionsByFunction_mock):
        response = versionWorker_handler(self.versionWorkerEvent(), "")
        expected_response = 0

        self.assertEqual(queryCloudwatch_mock.call_count, 1)
        self.assertEqual(getQueryResults_mock.call_count, 1)
        self.assertEqual(putToS3_mock.call_count, 1)
        self.assertEqual(getVersionsByFunction_mock.call_count, 1)
        self.assertEqual(response, expected_response)



    def versionWorkerEvent(self):
        return {
            "date_from": 1651363200,
            "date_to": 1651449600,
            "isDaily": 0
        }
'''