"""
Web Application Module
Mainly use for receive Line bot webhooks.
"""
from flask import Flask, request
from linebot import *
from linebot.models import *

app = Flask(__name__)
access_token = "<chanel access token>"
secret = "<chanel secret>"
line_bot_api = LineBotApi(channel_access_token=access_token)
handler = WebhookHandler(channel_secret=secret)


@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json(silent=True, force=True)
    retrieveString = body["events"][0]['message']['text']
    replyToken = body["events"][0]['replyToken']
    print("Msg : {0}\nReplyToken : {1}".format(retrieveString, replyToken))
    sendReplyMsg(tokens=replyToken)
    return 'OK'


def sendReplyMsg(tokens):
    template_msg = {
        "type": "buttons",
        "thumbnailImageUrl": "https://miro.medium.com/max/3016/0*5RLp-IJkJC6dLHvV.jpg",
        "title": "Test",
        "text": "Test",
        "actions": [
            {
                "type": "message",
                "label": "Action 1",
                "text": "Action 1"
            },
            {
                "type": "message",
                "label": "Action 2",
                "text": "Action 2"
            },
            {
                "type": "message",
                "label": "Action 3",
                "text": "Action 3"
            },
            {
                "type": "message",
                "label": "Action 4",
                "text": "Action 4"
            }
        ]
    }
    line_bot_api.reply_message(tokens, TemplateSendMessage(
        template=template_msg, alt_text="Use Mobile Devices"))


if __name__ == "__main__":
    app.run()
