# aws-sam-python-ingress
This is an AWS SAM app that uses automatically uploads newly-created S3 Objects
to the Voxel51 Platform using presigned URLs.

## Project structure
```bash
.
├── README.md                   <-- This instructions file
├── src                         <-- Source code for the Lambda function
│   ├── __init__.py
│   ├── app.py                  <-- Lambda function code
│   └── requirements.txt            <-- Lambda function dependencies
└── template.yaml               <-- SAM template
```


## Requirements
* A Voxel51 API Token
* [AWS CLI](https://aws.amazon.com/cli/)
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Docker installed](https://www.docker.com/community-edition)
* [jq](https://stedolan.github.io/jq/)


## CLI Commands to package and deploy your application
CLI commands to package, deploy and describe outputs defined within the cloudformation stack.

First, we need an `S3 bucket` where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
BUCKET=BUCKET_NAME
aws s3 mb s3://${BUCKET}
```

Next, run the following command to compile dependencies for your Lambda function. The `sam build` command automatically creates deployment artifacts that you can deploy to Lambda using the `sam package` and `sam deploy` commands.

```bash
# Run the build process inside an AWS Lambda-like Docker container
sam build --use-container
```

Next, run the following command to package your Lambda function. The `sam package` command creates a deployment package (ZIP file) containing your code and dependencies, and uploads them to the S3 bucket you specify. 

```bash
sam package \
    --template-file .aws-sam/build/template.yaml \
    --output-template-file packaged.yaml \
    --s3-bucket ${BUCKET}
```

The `sam deploy` command will create a Cloudformation Stack and deploy your SAM resources.
```bash
VOXEL51_API_TOKEN=/path/to/your/api-token.json
sam deploy \
    --template-file packaged.yaml \
    --stack-name voxel51-platform-ingress \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
      Voxel51ApiToken=$(cat ${VOXEL51_API_TOKEN} | jq '.access_token|tostring')
```

To see the name of the S3 bucket created after deployment, you can use the `aws cloudformation describe-stacks` command.
```bash
aws cloudformation describe-stacks \
    --stack-name voxel51-platform-ingress --query 'Stacks[].Outputs'
```
