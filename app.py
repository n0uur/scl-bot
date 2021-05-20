"""
Web Application Module
Mainly use for receive Line bot webhooks.
"""

import os
from dotenv import load_dotenv

from flask import Flask, request
from linebot import *
from linebot.models import *

from Model.User import User

################## INIT ##################

load_dotenv()

app = Flask(__name__)
access_token = os.environ.get("LINE_ACCESS_TOKEN")
secret = os.environ.get("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(channel_access_token=access_token)
handler = WebhookHandler(channel_secret=secret)

################## #### ##################

################## ROUTE #################

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json(silent=True, force=True)
    print(body)
    retrieveString = body["events"][0]['message']['text']
    replyToken = body["events"][0]['replyToken']
    print("Msg : {0}\nReplyToken : {1}".format(retrieveString, replyToken))
    sendReplyMsg(tokens=replyToken)
    return 'OK'

@app.route("/test")
def testClass():
    user = User()
    return "%d" % User.count()

################## ##### #################

######################################################

def sendReplyMsg(tokens):
    template_msg = {
        "type": "buttons",
        "thumbnailImageUrl": "https://inwfile.com/s-aa/qct4vq.jpg",
        "title": "จัดการ Router : Router 1",
        "text": "คุณสามารถจัดการ Router นี้ได้ โดยสามารถเลือกการทำงานได้ที่เมนูด้านล่าง",
        "actions": [
            {
                "type": "message",
                "label": "ตั้งค่า",
                "text": "Router Config,"
            },
            {
                "type":"postback",
                "label":"ตั้งค่า",
                "data":"routerid=1",
                "text":"Config Router"
            },
            {
                "type": "message",
                "label": "Remote",
                "text": "Remote"
            }
        ]
    }
    line_bot_api.reply_message(tokens, TemplateSendMessage(
        template=template_msg, alt_text="Use Mobile Devices"))

######################################################

if __name__ == "__main__":
    app.run()
