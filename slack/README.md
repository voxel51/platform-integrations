# Voxel51 Platform Slack integration

This project demonstrates how to build an app that integrates Slack with the
Voxel51 Platform. In particular, this example uses
[Google Cloud Functions](https://cloud.google.com/functions) as the client
application that sits in-between the Platform and Slack to do the message
translation that the Slack webhook requires.

Note that you can build out this application using any Functions as a service
(FaaS) provider, e.g., [AWS Lambda](https://aws.amazon.com/lambda) or even your
own server. There are many resource available online describing how to setup
Slack webhooks with AWS Lambda.


## Requirements

- The [JavaScript Client Library](https://github.com/voxel51/api-js) for the
Voxel51 Platform
- A valid [Platform API Token](https://voxel51.com/docs/api/#authentication)


## Setting up the Slack application

To integrate the platform with Slack, you can easily set up a webhook for a
specific Slack channel.

> Note that some of the provided notifications, such as `job_complete`, may
> occur very frequently on the Platform. So, be mindful of the Slack channel
> to which you are sending notifications!

First, [follow the steps](https://api.slack.com/messaging/webhooks) outlined by
Slack to get started.

For quick reference, you will need to:

1. [Create a Slack app](https://api.slack.com/apps?new_app=1) (if necessary).
2. Enable incoming webhooks for the app you just created.
3. Use the *Add New Webhook to Workspace* button to create the webhook.

After you complete this process, you should be provided a webhook URL.


## Setting up the Cloud Function

This project contains a very simple example of a client application entrypoint
that can be run using Google Cloud Functions.

The following steps describe how to setup a Cloud Function to serve the
webhook:

1. Log into your [Google Cloud Console](https://console.cloud.google.com/login)
and navigate to the
[Cloud Functions](https://console.cloud.google.com/functions) page

2. In the top navigation bar click "Create Function"

3. Give the function a reasonable name, and leave the rest as defaults

4. In the Inline Editor under "Source code" select `Node.js 10 (Beta)`
(or your preferred language)

5. Paste in the relevant source file code (here, `index.js` and `package.json`)

6. Under "Function to execute" beneath the code editor, you need to input the
main function name (here, `sendToSlack`)

7. Under "Environment variables, networking, timeouts and more" add a new
Environment variable called `SLACK_WEBHOOK_URL` and set it to the Slack webhook
URL that you created earlier

8. Click "Create". It may take a few seconds to create the function

9. Click on the newly created function

10. Click on the "Trigger" tab and copy the URL provided


## Integrating with the Platform

Once you have the trigger URL from the Cloud Function you set up in the
previous section, proceed with the following steps to configure the webhook on
the Platform:

1. Navigate to https://console.voxel51.com/account/webhooks in your Platform
Console Account

2. Create a webhook by pasting the URL and subscribing to the desired events

3. Press submit to register the webhook

The integration should now be live. Use the Platform and look for notifications
in Slack!


## Copyright

Copyright 2017-2020, Voxel51, Inc.<br>
[voxel51.com](https://voxel51.com)
