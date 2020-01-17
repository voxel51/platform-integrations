# Slack integration

| You will need a Voxel51 Platform account to integrate with Slack.

This guide will give you an example for how to set up a Slack webhook that integrates with the Voxel51 Platform. This example uses [Google Cloud Functions](https://cloud.google.com/functions/) as the client application that sits in-between the Platform and Slack to do the message translating that the Slack webhook requires. You can build out this application using any serverless function provider, like [AWS Lambda](https://aws.amazon.com/lambda/), or even your own server. There are a lot of resources out there detailing how to set up Slack webhooks  with AWS Lambda.

## Setting up the Slack application
To integrate the platform with Slack, you can easily set up a webhook
for a specific slack channel.

| Note that some of the provided notifications happen quite often on the Platform. Be mindful of the channel to which you are sending notifications!

[Follow the steps outlined by Slack](https://api.slack.com/messaging/webhooks) 
to get started. You should have a webhook URL after you have finished this process.

## Setting up the Google Cloud Function to integrate with Slack

In this folder there is a very simple example of a client application entrypoint that can be run as a Google Cloud Function. Below are the steps you can take to set up a Cloud Function to serve the webhook.

1. Log into your [Google Cloud Console](https://console.cloud.google.com/login) and navigate to the [Cloud Functions](https://console.cloud.google.com/functions) page.

2. In the top navigation bar click "Create Function".

3. Give the function a reasonable name, and leave the rest as defaults.

4. In the Inline Editor under "Source code" select Node.js 10 (Beta) (or your preferred language).

5. Paste in the relevant source file code (index.js and package.json).

6. Under "Environment variables, networking, timeouts and more" add a new Environment variable called `SLACK_WEBHOOK_URL` and set it to the Slack webhook URL that you created earlier.

7. Click "Create". It will take a few seconds to create the function.

8. Click on the "Trigger" tab and copy the URL provided.

## Integrating with the Platform

Once you have the trigger URL from the Cloud Function you set up above, proceed with the following steps to hook it all up:

1. In your Voxel51 Platform, go to *Account > Webhooks*.
2. Create a new webhook by pasting in the URL and subscribing to the desired events.
3. Submit the webhook.
4. Use the Platform and look for notifications in Slack!


