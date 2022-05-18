How to run this project

Disclaimer: The project has only been tested on windows. Frontend does not work smoothly with Chromium.

Requirements:
- serverless framework: https://www.serverless.com/framework/docs/getting-started
- npm
- For sample app: https://github.com/aws-samples/aws-serverless-shopping-cart#requirements

1. Deploy the sample app to your AWS account according to their instructions: https://github.com/aws-samples/aws-serverless-shopping-cart#option-1---deploy-backend-and-run-frontend-locally

2. Inject the logging statements and make a small change in the sample app, so you don't have to submit a real credit card number.
- Go to backend/shopping-cart-service
- Add this line to each Lambda function after the boto3 import: boto3.set_stream_logger(name='botocore', level='DEBUG')
-- (That should be 8 Lambda functions in total.)
- Go to frontend/src/views/Payment.vue and comment out lines 81, 82, 85, 88, 91 ("required" and "ccvalidate: ccvalidate")
-Save all changes and redeploy.

3. Open a terminal inside the tool directory. Next, you must configure your AWS user. You can then deploy the project to the AWS account with 'serverless deploy' from inside the project directory.
- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html (If you want to make a new user)
- https://www.serverless.com/framework/docs/providers/aws/cli-reference/config-credentials (If you have existing user credentials to use)

4. Create a API-Gateway for Fetcher.
- https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html
- - API-Gateway -> Create Api -> REST API -> Build
- - Enter a name and choose "Create Api"
- - Resources -> root (/) -> Actions (dropdown menu) -> Create Resource -> Enter name and a resource path -> Create Resource
- - Choose the newly created resource -> in Actions, choose Create method -> Choose 'ANY' -> Choose 'Use Lambda Proxy Integration' -> Choose the Lambda region of the tool -> For Lambda Function select the Fetcher function. Save & OK.
- - Actions -> Deploy -> Enter a stage name -> Deploy -> Take a note of the Invoke URL or come back to this page later

- https://codeburst.io/react-js-api-calls-to-aws-lambda-api-gateway-and-dealing-with-cors-89fb897eb04d
- - Choose the created resource -> Actions -> Enable CORS -> Click "Enable CORS and replace existing CORS headers"
- - Resources -> ANY -> Method Response
- - Add HTTP status 200 and 404. Also do this for Resources -> OPTIONS -> Method Response
- - For ANY and OPTIONS go to Method Response and add the following to the Response Headers and Response Body for both HTTP statuses.
- - - Response Headers: Access-Control-Allow-Headers, Access-Control-Allow-Origin, Access-Control-Allow-Methods
- - - Response Body: application/json, Empty
- - Actions -> Deploy API -> Save changes.

5. Repeat step 3 for a new API-Gateway that connects to the DeploymentFetcher instead of Fetcher.

6. Create CloudTrail trail that pushes to a S3 Bucket.
- Create trail with a name that we will use later on.
- Choose "Create new S3 bucket" and give it a name we will use later on.
- Enter a KMS alias and click next
- Make sure only "Management events" and "Write" is selected (no "Read"). Additionally, "Exclude AWS KMS events" and "Exclude Amazon RDS Data API events" can be selected, but it's not necessary.
- Create trail.

7. Create a trigger in the CloudTrail Bucket for CheckForDeployment.
- Go to the Bucket created in step 5.
- Select "Properties"
- Click "Create event notification"
- Give it a name and select "All object create events"
- Choose "Lambda function" as destination and select the CheckForDeployment function.
- Save.

8. Create periodic activation of workers with EventBridge
- Create a rule. (Requires an event bus.)
- Give it a name and select "Schedule"
- Choose the schedule pattern that runs at a specific time.
- Enter (1 0 * * ? *) as the cron expression. Make sure to select GMT (/UTC).
- Select AWS service, Lambda function, logWorker as the target.
- In the Additional Settings, select "Constant (JSON text)" and enter the following: 
{
  "isDaily": 1
}
- Add another target and repeat the previous two steps for versionWorker instead of logWorker.
- Press next until you're done.

8,5. Run and use the sample application a bit to ensure all log groups are created. Also check if a log group for the API-Gateway was created.
- To ensure all functions in the sample app are triggered, do the following:
- Create an account, increase and decrease counters, click the number of an item and enter an amount, add items to your shopping cart before logging in, and finally, do checkout.

9. Now we make configurations in serverless.yaml. 
- Replace the TODO of CLOUDTRAIL_BUCKET with the name of your CloudTrail Bucket
- Replace the TODO of LOGWORKER_ARN with the ARN of the logWorker function.
- Replace the TODO of VERSIONWORKER_ARN with the ARN of the versionWorker function.
- Replace the TODO of FETCHER_ARN with the ARN of the Fetcher function.
- For LOG_GROUPS_VERSIONWORKER, replace the names with the names of the log groups created for the sample application. Make sure to only use double-quotes (") inside the list and don't forget commas.
- Do the same for LOG_GROUPS_LOGWORKER, and additionally add the name of the log group of the sample app API-Gateway.
- Save and deploy again.

10. Setup frontend
- Navigate into the frontend folder.
- Run "npm i" to install the node_modules.
- Navigate to src\Services\Common.ts and enter the stage Invoke URL with the name of the resource you created (including the '/') from the Fetcher and DeploymentFetcher.
- Run "npm start".

Done!