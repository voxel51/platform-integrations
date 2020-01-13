# Slack integration

| You will need a Voxel51 Platform account to integrate with Slack.

## Setting up the Slack application
To integrate the platform with Slack, you can easily set up a webhook
for a specific slack channel.

[Follow the steps outlined by Slack](https://api.slack.com/messaging/webhooks) 
to get started.

## Integrating with the Platform

Once you have a webhook URL, proceed with the following steps to hook it all up:
1. set the `SLACK_WEBHOOK_URL` environment variable to URL given to you by Slack
in the environment where the webhook will be running.
2. In your Voxel51 Platform, go to Account > Web Hooks.
3. Create a new webhook by pasting in the Slack webhook URL and subscribing to the desired events.
4. Set the client 



In this folder there is a very simple example of a client application entrypoint that can be run as a Google Cloud Function or AWS Lambda.

