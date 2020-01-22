# Voxel51 Platform AWS Egress Client

This project demonstrates how to build an
[AWS Serverless Application Model](https://aws.amazon.com/serverless/sam)
application that uses [AWS Lambda](https://aws.amazon.com/lambda) to listen to
Voxel51 Platform events via Platform webhooks.

The example contained here is designed to listen to `job_complete` events for
purposes of downloading the outputs of completed jobs on the platform to a
storage location of your choice.


## Organization

```
.
├── README.md                   <-- This README
├── event.json                  <-- Example Platform event data
├── requirements.txt            <-- Lambda function dependencies
├── samconfig.toml              <-- SAM CLI config file
├── src                         <-- Source code for the Lambda function
│   ├── __init__.py
│   └── app.py                  <-- Lambda function code
└── template.yaml               <-- SAM template
```


## Background

### Motivation

All data and jobs (and their outputs) on the Platform are temporary and expire
according to their TTL (time-to-live). A user may update the TTL of a job or
data anytime before expiration, but the purpose of the Platform is to allow
users to process their data and then download the outputs to a more permanent
storage location of their choice.

This example client demonstrates a scalable solution to achieve this using
[AWS Lambda](https://aws.amazon.com/lambda),
[AWS S3 Storage](https://aws.amazon.com/s3), and
[Amazon API Gateway](https://aws.amazon.com/api-gateway), all built and
commissioned using the
[AWS Serverless Application Model](https://aws.amazon.com/serverless/sam).

### What does it deploy?

This system is deployed with an `API Gateway`, `AWS Lambda`, and `S3 bucket`,
which are created if they do not already exist. You may customize these
components to integrate with other infrastructure, which can be done via the
AWS console or the SAM build templates.

### How it works

This system provides the user a static URL with an API route that accepts POST
requests (the API Gateway). This URL is then provided to the Voxel51 Platform
as a webhook. When an event occurs on the Platform, it checks if any webhooks
are subscribed to that event, and sends a message via a HTTP POST request to
the user-provided URL.

The Lambda function is the serverless application that will recieve these
requests routed via the API Gateway. The Lambda function _handler code_ is then
invoked, which can parse data off the request (the `event`) and do anything
the user desires.

In this example, we grab the `id` of the Platform job and check that the event
is a `job_complete` event. With these two conditions satisfied, we then
download the output of the job with the provided `id` from the Platform. Then
we upload this data to an external storage location of our choice (in this
case, an S3 bucket).

With this egress client, all job outputs from the Platform will be
automatically downloaded before they expire on the Platform.


## Dependencies

- The [Python Client Library](https://github.com/voxel51/api-py) for the
Voxel51 Platform
- A valid [Platform API Token](https://voxel51.com/docs/api/#authentication)
- [AWS S3 Storage](https://aws.amazon.com/s3)
- [AWS Lambda](https://aws.amazon.com/lambda)
- [Amazon API Gateway](https://aws.amazon.com/api-gateway)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3](https://www.python.org/downloads)
- [Docker Community Edition](https://hub.docker.com/search/?type=edition&offering=community)


## Installation

1. Install the dependencies listed above.
2. (optional) `virtualenv egressve`
3. (optional) `source egressve/bin/activate`
4. `pip install -r requirements.txt`

At this point, you have everything you need to run local builds and deploy the
application using SAM!


## Build

```
sam build --use-container
```

## Deploy

Before we can deploy anything, we need an S3 bucket where we can upload our
Lambda function packaged as a ZIP file. If you don't have an S3 bucket to store
code artifacts, then this is a good time to create one:

```bash
BUCKET=BUCKET_NAME
aws s3 mb s3://${BUCKET}
```

Next, run the following command to package your Lambda function. The
`sam package` command creates a deployment package (ZIP file) containing your
code and dependencies, and uploads them to the S3 bucket you specify.

```bash
sam package \
    --template-file .aws-sam/build/template.yaml \
    --output-template-file packaged.yaml \
    --s3-bucket ${BUCKET}
```

To deploy, specify values for the parameters of the app, and run:

```
VOXEL51_API_TOKEN=/path/to/your/api-token.json
OUTPUT_BUCKET='v51-output-bucket-<EXAMPLE>'

sam deploy \
    --template-file packaged.yaml \
    --capabilities CAPABILITY_IAM \
    --stack-name voxel51-platform-egress \
    --parameter-overrides \
    Voxel51ApiToken=$(cat ${VOXEL51_API_TOKEN} | jq 'tostring') \
    OutputBucketName=${OUTPUT_BUCKET}
```

Remember the `OUTPUT_BUCKET` is where job outputs will be uploaded to.

After deployment, the CLI will output the gateway URL that was generated based
on your configurations. An example is:

```
https://<hash>.execute-api.<region>.amazonaws.com/Prod/job-complete`
```

This URL is also available via the AWS Console.

To configure a Platform webhook, navigate to the webhooks page of your Platform
Console account at https://console.voxel51.com/account/webhooks. In this
example, check the `Job Complete` event, paste the gateway URL generated above,
and click `Create`. That's it!

With this integration enabled, every time a job completes in your Platform
account, this Lambda function will be invoked and will download the output of
the job to the S3 bucket that you configured!


## Copyright

Copyright 2017-2020, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
