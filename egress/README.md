# Voxel51 AWS Egress Client
This project demonstrates how a AWS Lambda (and other AWS services) can be 
deployed and configured to listen to Voxel51 Platform API events via Voxel51 API-Webhooks.

The example contained here is designed to listen to `job_complete` events for purposes of "egressing" 
the job outputs to storage you control.

### Motivation
All Data and Jobs (and their outputs) are temporary and may expire based on their TTL (time-to-live).  
A user may update the TTL of a Job or Data anytime before expiration.  
The purpose of the Platform is to allow users to process their data, and download the outputs to 
a more permanent storage location of their choice.  This example client will demonstrate a scalable solution 
to achieve that using AWS Lambda, S3, and APIGateway - all built and commissioned by using the SAM build tool!

### What does it deploy?
This system is deployed with an `APIGateway`, `Lambda Function`, and `S3` bucket which are created if they do not
already exist.  You may customize this of course to integrate with other infrastructure, which can be done via the AWS
console or the SAM build templates.

### How it works
This system provides the user a fixed URL with an API route that accepts POST requests (the APIGateway).  
This URL can then be provided to the Voxel51 Platform as a Webhook.  When an event occurs on the Platform, it checks
if any Webhooks are subscribed to that event, and sends a message via a HTTP POST request to the user-provided URL.
The Lambda Function is the serverless application that will recieve these requests routed via the APIGateway.  
The Lambda Function "Handler" code is then invoked, which can parse data off the request (`event`) and do anything the user desires.  
In this example, we grab the `id` and check that the event is a `job_complete` event.  With these two conditions satisfied, we can then
request to download the job-output from the Platform via the job id provided from the event.  
Then we upload this data to storage external to that of the Platform (in this case a configured S3 bucket).  This will then
automatically save all job-outputs for your use.  
Remember: All things on the Platform expire eventually, this egress client allows a user to get all job-output from the Platform eventfully.  
This way the user does not need to worry about updating expiration on data or jobs later.

## Setup

### Dependencies
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

### Installation
1.  Install the dependencies listed above.
2.  (optional) `virtualenv egressve`
3.  (optional) `source egressve/bin/activate`
4.  `pip install -r requirements.txt`

At this point, you have everything you need to run local builds and deploy the application using SAM!


## Build

```bash
sam build -m requirements.txt --use-container
```

### Local development
SAM provides a lot of capability to test and run your system locally before deploying AWS resources.
```bash
sam local invoke -e event.json -env-vars env.json
```
 - `sam local invoke` invokes the Lambda function using docker locally
 - `event.json` is a mock request object to send to the Lambda function
 - `env.json` allows a user to specify a local set of environment variables, see the `env.json-example`.

You can also run the Lambda on a local api server and send full web-requests with:
```bash
sam local start-api --port 5000 --env-vars env.json --host 0.0.0.0
```
The host and ports are optional, but very useful if you are developing this locally with other systems.
To test the Lambda function via a local api like this, you can send a curl'd request like so:
```bash
curl localhost:5000/job-complete -X POST -H "Content-Type: application/json" -d '{"id":<jobid>, "event":"job_complete", "msg":"Test!"}'
```

## Deploy

```bash
sam deploy --guided
```
Using the guided option, the CLI will prompt you for your desired configurations for deployment.  
It will also allow you to save these settings to the `samconfig.toml` file to automate future deployments with the same settings.

To deploy with your saved or default settings:
```bash
sam deploy
```

