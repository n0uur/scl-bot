"""
Web Application Module
Mainly use for receive Line bot webhooks.
"""

import os
import threading

from dotenv import load_dotenv
from flask import Flask, request

import Syslog
from Line import Line

################## INIT ##################
load_dotenv()

app = Flask(__name__)
access_token = os.environ.get("LINE_ACCESS_TOKEN")
secret = os.environ.get("LINE_CHANNEL_SECRET")

Line.setBotApi(access_token, secret)


################## ROUTE #################

@app.route("/")
def home():
    return "hello flask :)", 200


@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json(force=False, cache=False)
    for i in range(len(body['events'])):
        event = body['events'][i]
        _ = Line.event(event)
    return '0', 200


##########################################


if __name__ == "__main__":
    flaskThread = threading.Thread(target=app.run)
    syslogThread = threading.Thread(target=Syslog.startSyslog)
    flaskThread.start()
    syslogThread.start()
