/**
 * Example middleware that converts Voxel51 Platform webhook payloads to
 * Slack webhook notifications.
 *
 * Copyright 2017-2020, Voxel51, Inc.<br>
 * {@link https://voxel51.com voxel51.com}
 */
const { IncomingWebhook } = require('@slack/webhook');

const url = process.env.SLACK_WEBHOOK_URL;
const webhook = new IncomingWebhook(url);

/*
 * Converts data from a Voxel51 Platform payload into the format that Slack
 * expects. `id` and `msg` are fields on the data object coming from the
 * Platform.
 */
const formatData = (data) => {
  return {
    blocks: [
      {
        'type': 'section',
        'fields': [
          {
            'type': 'mrkdwn',
            'text': '*ID*',
          },
          {
            'type': 'mrkdwn',
            'text': '*Message*',
          },
          {
            'type': 'plain_text',
            'text': data.id,
          },
          {
            'type': 'plain_text',
            'text': data.msg,
          },
        ],
      },
    ],
  };
};

/*
 * Example client application (integration middleware) that receives a Voxel51
 * Platform payload and forwards it to Slack via a pre-configured webhook.
 */
module.exports.sendToSlack = async (req, res) => {
  try {
    const formattedData = formatData(req.body);
    await webhook.send(formattedData);
    res.status(204).send();
  } catch (error) {
    console.error(error);
    res.status(500).send()
  }
};
