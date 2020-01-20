# Voxel51 Platform Integrations
This repository contains example implementations of integrations with various services to interact
with the Voxel51 Platform.  

## Repository Structure
Each top level folder contains a separate example independent of others, which will show
how to use the API client libraries to build a component to link other systems or pipelines to the platform.

## Index

### Ingress App
The Ingress application is AWS Lambda based component that listens to S3 bucket for new Data to run Platform jobs on.  
The Lambda function is configured to listen on Object Create S3 events from the configured bucket.
For each new data, a signed url is generated, this url is posted to the Platform as data (to avoid uploading and copying data),
and a Job is requested on that data for the configured Analytics.
This app uses the [api-py](https://github.com/voxel51/api-py) client library and AWS S3 and Lambda.

### Egress App
The Egress application is an AWS Lambda based component that listens to Platform job completion events via a Webhook.
The Lambda function is created with an API-Gateway which exposes a static url.  This url is then used as a Platform Webhook
which is configured via the Console.  With this url assigned to "Job Completion" events, each time a job completes this url
recieves data posted to that url that the Lamda app is configured to process.  The example Lambda code uses the api-py Client 
library to download the output data for the completed job, optionally manipulate or transform it, and then upload it to
an output S3 bucket external to the Platform. 
This app uses the [api-py](https://github.com/voxel51/api-py) client library and AWS S3, Lambda, and API-Gateway.

### Slack Integration
The Slack app demonstrates how the api-js client library can be used with Google Cloud Functions to create a Slack 
integration.  Just like the Egress App, this uses a GC Function url as a webhook to which any Platform event can
be subscribed.  As a result the event data can be posted to a Slack channel of your choice.
This app uses the [api-py](https://github.com/voxel51/api-js) client library, Google Cloud Functions, and Slack.