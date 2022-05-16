import unittest
from unittest import mock

# Setting the default AWS region environment variable required by the Python SDK boto3
with mock.patch.dict('os.environ', {'AWS_REGION': 'us-east-1'}):
    from logWorker import logWorker_handler

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
                "value": "2022-05-01 12:00:40.919"
            },
            {
                "field": "@message",
                "value": "[DEBUG]\t2022-05-01T12:00:40.919Z\tc7c37296-80a4-4e90-bd89-e89139b9b1d1\tMaking request for OperationModel(name=UpdateItem) with params: {'url_path': '/', 'query_string': '', 'method': 'POST', 'headers': {'X-Amz-Target': 'DynamoDB_20120810.UpdateItem', 'Content-Type': 'application/x-amz-json-1.0', 'User-Agent': 'Boto3/1.10.34 Python/3.8.13 Linux/4.14.255-273-220.498.amzn2.x86_64 exec-env/AWS_Lambda_python3.8 Botocore/1.13.50 Resource'}, 'body': b'{\"TableName\": \"aws-serverless-shopping-cart-shoppingcart-service-DynamoDBShoppingCartTable-1M6QOEAR5W7QN\", \"Key\": {\"pk\": {\"S\": \"cart#e8d249f0-4a09-4c85-a59f-3d1d613a301f\"}, \"sk\": {\"S\": \"product#d2580eff-d105-45a5-9b21-ba61995bc6da\"}}, \"ExpressionAttributeNames\": {\"#quantity\": \"quantity\", \"#expirationTime\": \"expirationTime\", \"#productDetail\": \"productDetail\"}, \"ExpressionAttributeValues\": {\":val\": {\"N\": \"1\"}, \":ttl\": {\"N\": \"1651492840\"}, \":productDetail\": {\"M\": {\"category\": {\"S\": \"sweets\"}, \"createdDate\": {\"S\": \"2017-04-06T06:21:36 -02:00\"}, \"description\": {\"S\": \"Dolore ipsum eiusmod dolore aliquip laborum laborum aute ipsum commodo id irure duis ipsum.\"}, \"modifiedDate\": {\"S\": \"2019-09-21T12:08:48 -02:00\"}, \"name\": {\"S\": \"candied prunes\"}, \"package\": {\"M\": {\"height\": {\"N\": \"329\"}, \"length\": {\"N\": \"179\"}, \"weight\": {\"N\": \"293\"}, \"width\": {\"N\": \"741\"}}}, \"pictures\": {\"L\": [{\"S\": \"http://placehold.it/32x32\"}]}, \"price\": {\"N\": \"35\"}, \"productId\": {\"S\": \"d2580eff-d105-45a5-9b21-ba61995bc6da\"}, \"tags\": {\"L\": [{\"S\": \"laboris\"}, {\"S\": \"dolor\"}, {\"S\": \"in\"}, {\"S\": \"labore\"}, {\"S\": \"duis\"}]}}}}, \"UpdateExpression\": \"ADD #quantity :val SET #expirationTime = :ttl, #productDetail = :productDetail\"}', 'url': 'https://dynamodb.us-east-1.amazonaws.com/', 'context': {'client_region': 'us-east-1', 'client_config': <botocore.config.Config object at 0x7f3a90c8e550>, 'has_streaming_input': False, 'auth_type': None}}\n"
            },
            {
                "field": "exist",
                "value": "1"
            },
            {
                "field": "@requestId",
                "value": "c7c37296-80a4-4e90-bd89-e89139b9b1d1"
            },
            {
                "field": "@log",
                "value": "622370397643:/aws/lambda/aws-serverless-shopping-cart-sho-AddToCartFunction-tkpoQy5Bx9So"
            },
            {
                "field": "@ptr",
                "value": "CpcBClwKWDYyMjM3MDM5NzY0MzovYXdzL2xhbWJkYS9hd3Mtc2VydmVybGVzcy1zaG9wcGluZy1jYXJ0LXNoby1BZGRUb0NhcnRGdW5jdGlvbi10a3BvUXk1Qng5U28QAxI3GhgCBiQIl2IAAAAAMLKEswAGJudlYAAAASIgASihkvr7hzAwlJT6+4cwOKcBQPnQAkjveVDeXxBgGAE="
            }
        ],
        [
            {
                "field": "@timestamp",
                "value": "2022-05-01 12:00:40.913"
            },
            {
                "field": "@message",
                "value": "[DEBUG]\t2022-05-01T12:00:40.913Z\t933b2804-f8b2-4bb2-8487-23067fd56f3a\tMaking request for OperationModel(name=UpdateItem) with params: {'url_path': '/', 'query_string': '', 'method': 'POST', 'headers': {'X-Amz-Target': 'DynamoDB_20120810.UpdateItem', 'Content-Type': 'application/x-amz-json-1.0', 'User-Agent': 'Boto3/1.10.34 Python/3.8.13 Linux/4.14.255-273-220.498.amzn2.x86_64 exec-env/AWS_Lambda_python3.8 Botocore/1.13.50 Resource'}, 'body': b'{\"TableName\": \"aws-serverless-shopping-cart-shoppingcart-service-DynamoDBShoppingCartTable-1M6QOEAR5W7QN\", \"Key\": {\"pk\": {\"S\": \"cart#e8d249f0-4a09-4c85-a59f-3d1d613a301f\"}, \"sk\": {\"S\": \"product#4c1fadaa-213a-4ea8-aa32-58c217604e3c\"}}, \"ExpressionAttributeNames\": {\"#quantity\": \"quantity\", \"#expirationTime\": \"expirationTime\", \"#productDetail\": \"productDetail\"}, \"ExpressionAttributeValues\": {\":val\": {\"N\": \"1\"}, \":ttl\": {\"N\": \"1651492840\"}, \":productDetail\": {\"M\": {\"category\": {\"S\": \"fruit\"}, \"createdDate\": {\"S\": \"2017-04-17T01:14:03 -02:00\"}, \"description\": {\"S\": \"Culpa non veniam deserunt dolor irure elit cupidatat culpa consequat nulla irure aliqua.\"}, \"modifiedDate\": {\"S\": \"2019-03-13T12:18:27 -01:00\"}, \"name\": {\"S\": \"packaged strawberries\"}, \"package\": {\"M\": {\"height\": {\"N\": \"948\"}, \"length\": {\"N\": \"455\"}, \"weight\": {\"N\": \"54\"}, \"width\": {\"N\": \"905\"}}}, \"pictures\": {\"L\": [{\"S\": \"http://placehold.it/32x32\"}]}, \"price\": {\"N\": \"716\"}, \"productId\": {\"S\": \"4c1fadaa-213a-4ea8-aa32-58c217604e3c\"}, \"tags\": {\"L\": [{\"S\": \"mollit\"}, {\"S\": \"ad\"}, {\"S\": \"eiusmod\"}, {\"S\": \"irure\"}, {\"S\": \"tempor\"}]}}}}, \"UpdateExpression\": \"ADD #quantity :val SET #expirationTime = :ttl, #productDetail = :productDetail\"}', 'url': 'https://dynamodb.us-east-1.amazonaws.com/', 'context': {'client_region': 'us-east-1', 'client_config': <botocore.config.Config object at 0x7fddcf2ab520>, 'has_streaming_input': False, 'auth_type': None}}\n"
            },
            {
                "field": "exist",
                "value": "1"
            },
            {
                "field": "@requestId",
                "value": "933b2804-f8b2-4bb2-8487-23067fd56f3a"
            },
            {
                "field": "@log",
                "value": "622370397643:/aws/lambda/aws-serverless-shopping-cart-sho-AddToCartFunction-tkpoQy5Bx9So"
            },
            {
                "field": "@ptr",
                "value": "CpcBClwKWDYyMjM3MDM5NzY0MzovYXdzL2xhbWJkYS9hd3Mtc2VydmVybGVzcy1zaG9wcGluZy1jYXJ0LXNoby1BZGRUb0NhcnRGdW5jdGlvbi10a3BvUXk1Qng5U28QARI3GhgCBhu3FfYAAAABBCbs5QAGJudkwAAAAmIgASj/ifr7hzAwg5T6+4cwOKcBQIrRAkiDelDyXxBgGAE="
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

def mocked_putToS3(date_from_str, file_name, inventory):
    print('')
    #nothing?




class logWorkerTest(unittest.TestCase):

    @mock.patch('logWorker.queryCloudwatch', side_effect=mocked_queryCloudwatch)
    @mock.patch('logWorker.getQueryResults', side_effect=mocked_getQueryResults)
    @mock.patch('logWorker.putToS3', side_effect=mocked_putToS3)
    def test_inventory_success(self, queryCloudwatch_mock, getQueryResults_mock, putToS3_mock):
        response = logWorker_handler(self.logWorkerEvent(), "")
        expected_response = None

        self.assertEqual(queryCloudwatch_mock.call_count, 1)
        self.assertEqual(getQueryResults_mock.call_count, 1)
        self.assertEqual(putToS3_mock.call_count, 1)
        self.assertEqual(response, expected_response)


    @mock.patch('logWorker.queryCloudwatch', side_effect=mocked_queryCloudwatch)
    @mock.patch('logWorker.getQueryResults', side_effect=mocked_getQueryResults)
    @mock.patch('logWorker.putToS3', side_effect=mocked_putToS3)
    def test_Daily(self, queryCloudwatch_mock, getQueryResults_mock, putToS3_mock):
        response = logWorker_handler(self.logWorkerEventDaily(), "")
        expected_response = None

        self.assertEqual(queryCloudwatch_mock.call_count, 1)
        self.assertEqual(getQueryResults_mock.call_count, 1)
        self.assertEqual(putToS3_mock.call_count, 1)
        self.assertEqual(response, expected_response)

    def logWorkerEvent(self):
        return {
            "date_from": 1651363200,
            "date_to": 1651449600,
            "isDaily": 0
        }

    def logWorkerEventDaily(self):
        return {
            "isDaily": 1
        }
