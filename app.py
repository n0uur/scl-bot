"""
Web Application Module
Mainly use for receive Line bot webhooks.
"""
from flask import Flask, request
from linebot import *

app = Flask(__name__)

line_bot_api = LineBotApi('<Channel access token>')
handler = WebhookHandler('<Channel secret>')


@app.route("/callback", methods=['POST'])
def callback():
    # body = request.get_data(as_text=True)
    # print(body)
    req = request.get_json(silent=True, force=True)
    intent = req["queryResult"]["intent"]["displayName"]
    text = req['originalDetectIntentRequest']['payload']['data']['message']['text']
    id = req['originalDetectIntentRequest']['payload']['data']['source']['userId']
    disname = line_bot_api.get_profile(id).display_name
    
    print('id = ' + id)
    print('name = ' + disname)
    print('text = ' + text)
    print('intent = ' + intent)

    return 'OK'

if __name__ == "__main__":
    app.run()
