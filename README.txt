How to run this project

Disclaimer: The project has only been tested on windows. Frontend does not work smoothly with Chromium.

Requirements:
- serverless framework: https://www.serverless.com/framework/docs/getting-started
- npm
- For sample app: https://github.com/aws-samples/aws-serverless-shopping-cart#requirements

1. Navigate to the sample app and deploy it to your AWS account according to these instructions: https://github.com/aws-samples/aws-serverless-shopping-cart#option-1---deploy-backend-and-run-frontend-locally

2. Open a terminal inside the directory. Next, you must configure your AWS user. You can then deploy the project to the AWS account with 'serverless deploy' from inside the project directory.
- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html (If you want to make a new user)
- https://www.serverless.com/framework/docs/providers/aws/cli-reference/config-credentials (If you have existing user credentials to use)

(2.5. Configure botocore & powertool logging, ...)
(- This will be setup in the sample application.)

3. Create a API-Gateway for Fetcher.
- https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html
- https://codeburst.io/react-js-api-calls-to-aws-lambda-api-gateway-and-dealing-with-cors-89fb897eb04d

4. Repeat step 3 for a new API-Gateway that connects to the DeploymentFetcher.

5. Create CloudTrail trail that pushes to a S3 Bucket.
- Create trail with a name that we will use later on.
- Choose "Create new S3 bucket" and give it a name we will use later on.
- Enter a KMS alias and click next
- Make sure only "Management events" and "Write" is selected (no "Read"). Additionally, "Exclude AWS KMS events" and "Exclude Amazon RDS Data API events" can be selected, but it's not necessary.
- Create trail.

6. Create a trigger in the CloudTrail Bucket for CheckForDeployment.
- Go to the Bucket created in step 5.
- Select "Properties"
- Click "Create event notification"
- Give it a name and select "All object create events"
- Choose "Lambda function" as destination and select the CheckForDeployment function.
- Save.

7. Create periodic activation of workers with EventBridge
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

7,5. Run and use the sample application a bit to ensure all log groups are created. Also check if a log group for the API-Gateway was created.
- To ensure all functions in the sample app are triggered, do the following:
- Create an account, increase and decrease counters, click the number of an item and enter an amount, add items to your shopping cart before logging in, and finally, do checkout.

8. Now we make configurations in serverless.yaml. 
- Replace the TODO of CLOUDTRAIL_BUCKET with the name of your CloudTrail Bucket
- Replace the TODO of LOGWORKER_ARN with the ARN of the logWorker function.
- Replace the TODO of VERSIONWORKER_ARN with the ARN of the versionWorker function.
- Replace the TODO of FETCHER_ARN with the ARN of the Fetcher function.
- For LOG_GROUPS_VERSIONWORKER, replace the names with the names of the log groups created for the sample application. Make sure to only use double-quotes (") inside the list and don't forget commas.
- Do the same for LOG_GROUPS_LOGWORKER, and additionally add the name of the log group of the sample app API-Gateway.
- Save and deploy again.

9. Setup frontend
- Navigate into the frontend folder.
- Run "npm i" to install the node_modules.
- Navigate to src\Services\Common.ts and enter the stage Invoke URL from the Fetcher and DeploymentFetcher, respectively.
- Run "npm start".

Done!