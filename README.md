# Voxel51 Platform Integrations

This repository contains example implementations of integrations with various
services to interact with the Voxel51 Platform.

Available at
[https://github.com/voxel51/platform-integrations](https://github.com/voxel51/platform-integrations).

<img src="https://drive.google.com/uc?id=1j0S8pLsopAqF1Ik3rf-CdyAIU4kA0sOP" alt="voxel51-logo.png" width="40%"/>


## Repository Structure

Each top-level folder contains a separate example application that demonstrates
how to build integrations that link to the Voxel51 Platform in various ways,
typically leveraging the API client libraries.

```
.
├── README.md                   <-- This README
├── egress                      <-- Platform egress app
├── ingress                     <-- Platform ingress app
└── slack                       <-- Platform Slack integration
```

## Ingress App

The Ingress application is an [AWS Lambda](https://aws.amazon.com/lambda) tool
that automatically runs Platform jobs on data uploaded to an S3 bucket.
Specifically, the Lambda function is configured to listen for
`s3:ObjectCreated` events on a configurable bucket.

For each new data, a signed URL is generated and posted to the Platform (as
oppposed to uploading the raw data to the Platform, which would duplicate
storage), and job(s) are run on that data for the configured analytic(s).

#### Dependencies

- The [Python Client Library](https://github.com/voxel51/api-py) for the
Voxel51 Platform
- [AWS S3 Storage](https://aws.amazon.com/s3)
- [AWS Lambda](https://aws.amazon.com/lambda)


## Egress App

The Egress application is an [AWS Lambda](https://aws.amazon.com/lambda) tool
that automatically responds to Platform job completion events configured via a
Platform webhook. The Lambda function is created with an
[Amazon API Gateway](https://aws.amazon.com/api-gateway) which exposes a static
URL. This URL is then used as the endpoint for a Platform webhook, which is
configured via your Platform Console account.

When the webhook is configured for `job_complete` events, every job completed
on your Platform account will send metadata about the completed job to the
static URL that the Lambda app is configured to process.

The example Lambda code in this app uses the
[Python Client Library](https://github.com/voxel51/api-py) to download the
output of the completed job, optionally manipulate or transform it, and then
upload it to a configurable external S3 bucket.

#### Dependencies

- The [Python Client Library](https://github.com/voxel51/api-py) for the
Voxel51 Platform
- [AWS S3 Storage](https://aws.amazon.com/s3)
- [AWS Lambda](https://aws.amazon.com/lambda)
- [Amazon API Gateway](https://aws.amazon.com/api-gateway)


## Slack Integration

The Slack app demonstrates how to build a [Slack](https://slack.com)
integration that will generate Slack messages in a channel of your choice in
response to events in your Platform account.

The tool uses [Google Cloud Functions](https://cloud.google.com/functions) to
provide a static URL that is configured as an endpoint for a Platform webhook.
Internally, the GCF uses the
[JavaScript Client Library](https://github.com/voxel51/api-js) to parse the
event data and then publishes the event to Slack.

#### Dependencies

- The [JavaScript Client Library](https://github.com/voxel51/api-js) for the
Voxel51 Platform
- [Google Cloud Functions](https://cloud.google.com/functions)


## Copyright

Copyright 2017-2020, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
