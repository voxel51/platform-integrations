const { IncomingWebhook } = require('@slack/webhook');
const url = process.env.SLACK_WEBHOOK_URL;
const webhook = new IncomingWebhook(url);
/*
  Example client application (integration middleware)
  that converts a Voxel51 Platform payload and forwards
  it to Slack via a pre-configured webhook.
*/
module.exports.sendToSlack = (req, res) => {
  (async () => {
    const formattedData = formatData(req.body);
    return await webhook.send(formattedData);
  })();
};

/*
  Formats data coming from the Platform into a format
  that Slack expects. 
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