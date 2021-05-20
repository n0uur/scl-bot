"""
Line Response handler
"""

import json
from linebot import *
from linebot.models import *


class Line():

    line_bot_api = None
    handler = None

    @classmethod
    def setBotApi(cls, channel_access_token, channel_secret):
        cls.line_bot_api = LineBotApi(
            channel_access_token=channel_access_token)
        cls.handler = WebhookHandler(channel_secret=channel_secret)

    @classmethod
    def event(cls, event) -> bool:

        # print(event)

        if cls.line_bot_api == None or cls.handler == None:
            return False

        print(json.dumps(event))

        if event['type'] == "message":
            if event['message']['type'] == "sticker":  # sticker ? just dunno wat to doooo
                replySticker = StickerSendMessage(
                    package_id="11537", sticker_id="52002751")

                replyText = "ไม่พบการใช้คำสั่งด้วยสติกเกอร์ หากต้องการทราบคำสั่งสามารถพิมพ์ \"help\" เพื่อดูรายการคำสั่งได้"

                cls.line_bot_api.reply_message(event['replyToken'], [
                    replySticker,
                    TextSendMessage(
                        text=replyText,
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(
                                        label="ดูรายการคำสั่งทั้งหมด", text="help")
                                )
                            ])
                    )])

                return True

            elif event['message']['type'] == "text":  # text message as action command

                message = event['message']['text'].lower()

                if message == "help":
                    # show all commands
                    replyText = "👋 รายการคำสั่งที่ใช้งานได้\n🚀 help ; ดูรายการคำสั่งทั้งหมด\n🚀 Router List ; ดู Router ทั้งหมด\n🚀 Status ; แสดงสถานะของระบบ Bot\n\n🔧 Router Status, <router id> ; ดูสถานะ Router\n🔧 Router Remote, <router id> ; Remote เข้าสู่ Console ของ Router\n🔧 Router Config, <router id> ; เข้าสู่โหมดตั้งค่า Router\n🔧 Router Log, <router id> ; ดู Log 10 รายการล่าสุดของ Router ผ่าน Syslog"
                    cls.line_bot_api.reply_message(event['replyToken'],
                                                   TextSendMessage(
                        text=replyText,
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(
                                        label="ดู Router ทั้งหมด", text="Router List")
                                ),
                                QuickReplyButton(
                                    action=MessageAction(
                                        label="แสดงสถานะของระบบ", text="Status")
                                )
                            ])
                    ))

                    return True

                elif message == "router list":
                    # show all routers
                    pass

                # cls.sendReplyButton(event['replyToken'])

                # return True

        elif event['type'] == "postback":
            pass
        else:
            pass

        cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text="ไม่พบคำสั่ง หรือยังไม่สามารถใช้งานได้ในขณะนี้"))

        return False

    @classmethod
    def sendReplyButton(cls, reply_token, alt_text="ข้อความนีัแสดงได้เฉพาะบนโทรศัพท์มือถือ"):
        template_msg = {
            "type": "buttons",
            "thumbnailImageUrl": "https://inwfile.com/s-aa/qct4vq.jpg",
            "title": "Router: Router 1",
            "text": "คุณสามารถจัดการ Router นี้ได้ โดยสามารถเลือกการทำงานได้ที่เมนูด้านล่าง",
            "actions": [
                {
                    "type": "message",
                    "label": "สถานะ",
                    "text": "Router Status, 1"
                },
                {
                    "type": "message",
                    "label": "ตั้งค่า",
                    "text": "Router Config, 1"
                },
                {
                    "type": "message",
                    "label": "SSH Remote",
                    "text": "Router Remote, 1"
                }
            ]
        }
        cls.line_bot_api.reply_message(reply_token, TemplateSendMessage(
            template=template_msg, alt_text=alt_text))

    @staticmethod
    def getEventInfo(event):

        try:
            info = {
                "user_id": event['source']['userId'],
                "reply_token": event['replyToken'],
            }
        except:
            print("Cannot get event infomation")
            return None

        try:
            msg_id = event["message"]["id"]
            msg_type = event["message"]["type"]

            info['message'] = {
                "id": msg_id,
                "type": msg_type
            }
        except:
            print("Invalid message type..")
            info['message'] = None
            return info
