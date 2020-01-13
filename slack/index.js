const { IncomingWebhook } = require('@slack/webhook');
const url = process.env.SLACK_WEBHOOK_URL;
const webhook = new IncomingWebhook(url);

module.exports.sendToSlack = (req, res) => {
  (async () => {
    const formattedData = formatData(req.body);
    return await webhook.send(formattedData);
  })();
};

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