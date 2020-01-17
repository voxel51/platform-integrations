const { IncomingWebhook } = require('@slack/webhook');
const url = process.env.SLACK_WEBHOOK_URL;
const webhook = new IncomingWebhook(url);
/*
  Example client application (integration middleware)
  that converts a Voxel51 Platform payload and forwards
  it to Slack via a pre-configured webhook.
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

/*
  Formats data coming from the Platform into a format
  that Slack expects.
  "id" and "msg" are fields on the data object coming from the Platform
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
