"""
Line Response handler
"""

import json
from linebot import *
from linebot.models import *

from Model.User import User
from Model.Router import Router

from SNMP import *

from netmiko import ConnectHandler

class Line:
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

        if cls.line_bot_api is None or cls.handler is None:
            return False

        print(json.dumps(event))

        if event['type'] == "message":
            if event['message']['type'] == "sticker":  # sticker ? just dunno wat to doooo
                replySticker = StickerSendMessage(
                    package_id="11537", sticker_id="52002751")

                replyText = "ไม่พบการใช้คำสั่งด้วยสติกเกอร์ หากต้องการทราบคำสั่งสามารถพิมพ์ \"help\" " \
                            "เพื่อดูรายการคำสั่งได้ "

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

                user = User.getUser(event['source']['userId'])

                if user.state == User.STATE_REMOTE:
                    # todo: parse message to ssh session
                    if message == "exit":
                        statusText = "ปิดการเชื่อมต่อ Remote Console แล้ว"
                        cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                        user.state = User.STATE_NORMAL
                        user.ssh_session.disconnect()
                        user.ssh_session = None

                        return True

                    try:
                        outputText = user.ssh_session.send_command(event['message']['text'])
                    except IOError:
                        outputText = "คำสั่งไม่มีการตอบกลับ"

                    cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=outputText))

                    return True

                elif user.state == User.STATE_SETTING:
                    # todo: get config status and parse message to config router

                    if message == "exit":

                        statusText = "ยกเลิกการตั้งค่าแล้ว"
                        cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                        user.state = User.STATE_NORMAL
                        user.current_config = None
                        user.current_router = None

                        return True

                    if user.current_config == "hostname":

                        router = Router.getRouter(user.current_router)

                        setRouterHostName(router.ip, router.snmp_write, event['message']['text'].strip())

                        statusText = "ตั้งค่า Hostname เป็น " + event['message']['text'].strip() + " แล้ว"
                        cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                        user.state = User.STATE_NORMAL
                        user.current_config = None
                        user.current_router = None

                        return True

                    user.state = User.STATE_NORMAL
                    user.current_config = None
                    user.current_router = None

                    return False

                elif user.state == User.STATE_NORMAL:

                    if message == "help" or message == "?":
                        # show all commands
                        replyText = "👋 รายการคำสั่งที่ใช้งานได้\n🚀 help ; ดูรายการคำสั่งทั้งหมด\n🚀 Router List ;ดู Router ทั้งหมด\n🚀 Status ; แสดงสถานะของระบบ Bot\n\n🔧 Router Select, <router id> ; เลือก Router\n🔧 Router Remote, <router id> ; Remote เข้าสู่ Console ของ Router\n🔧 Router Status, <router id> ; ดูข้อมูลสถานะของ Router\n🔧 Router Config, <router id> ; เข้าสู่โหมดตั้งค่า Router\n"
                        cls.line_bot_api.reply_message(event['replyToken'],
                                                       TextSendMessage(
                                                           text=replyText,
                                                           quick_reply=QuickReply(
                                                               items=[
                                                                   QuickReplyButton(
                                                                       action=MessageAction(
                                                                           label="ดู Router ทั้งหมด",
                                                                           text="Router List")
                                                                   ),
                                                                   QuickReplyButton(
                                                                       action=MessageAction(
                                                                           label="แสดงสถานะของระบบ", text="Status")
                                                                   )
                                                               ])
                                                       ))

                        return True

                    elif message == "router list":
                        routers = Router.getRouters()
                        routers_dict = [
                            {
                                "name": router.name,
                                "hostname": router.hostname,
                                "ip": router.ip,
                                "is_up": router.getStatus()
                            }
                            for router in routers
                        ]
                        carousel_template = CarouselTemplate(columns=[
                            CarouselColumn(text='Hostname: %s\nIP: %s' % (router['hostname'], router['ip']),
                                           title="%s [%s]" % (router['name'], "ออนไลน์" if router['is_up'] else "ออฟไลน์"),
                                           actions=[
                                               MessageAction(label='เลือก', text='Router Select, ' + router['name'])
                                           ],
                                           thumbnail_image_url="https://images.pexels.com/photos/2881224/pexels-photo-2881224.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"
                                           )
                            for router in routers_dict
                        ])
                        cls.line_bot_api.reply_message(event['replyToken'],
                                                       TemplateSendMessage(
                                                           alt_text='ข้อความนี้แสดงได้เฉพาะบนโทรศัพท์มือถือ',
                                                           template=carousel_template)
                                                       )
                        return True

                    elif message == "status":
                        # show system status
                        is_syslog_online = True  # todo : get syslog server status ?... no it's just always online! maybe ?
                        statusText = "👋 สถานะระบบ\nสถานะบอท : 🟢 ปกติ\nสถานะ Syslog : " + (
                            "🟢 ปกติ" if is_syslog_online else "🔴 ปิด")
                        cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                        return True

                    elif len(message.split(',')) >= 2:  # command that having parameters

                        command = message.split(',')[0]
                        params = [i.strip() for i in message.split(',')[1:]]

                        if command == "router select":
                            router = Router.getRouter(params[0])
                            # print(params[0])
                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            router_actions = [
                                {
                                    "type": "message",
                                    "label": "สถานะ",
                                    "text": "Router Status, " + router.name
                                },
                                {
                                    "type": "message",
                                    "label": "ตั้งค่า",
                                    "text": "Router Config, " + router.name
                                },
                                {
                                    "type": "message",
                                    "label": "SSH Remote",
                                    "text": "Router Remote, " + router.name
                                }
                            ]
                            cls.sendReplyButton(event['replyToken'],
                                                router.name,
                                                "คุณสามารถจัดการ Router นี้ได้ โดยสามารถเลือกการทำงานได้ที่เมนูด้านล่าง",
                                                actions=router_actions
                                                )
                        elif command == "router status":

                            router = Router.getRouter(params[0])

                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            router_detail = getRouterSMMP(router.ip, router.snmp_read)

                            replyText = "ℹ ข้อมูลสถานะ Router : " + router_detail['hostname'] + "\n" \
                            + "⏱ เปิดใช้งานมาแล้ว : " + router_detail['uptime'].split('.')[0] + " ชั่วโมง" \
                            + "\n⏱ Latency: %.2f ms\n\n 🌎 Interfaces:\n" % router.getPing()
                            for interface in router_detail['interfaces']:
                                replyText += "- Interface %s : [สถานะ: %s]\n" % \
                                (interface['name'], ("ปิดใช้งาน ⛔" if interface['admin_status'] == "down" else "ปกติ ✅" if interface['line_status'] == "up" else "ไม่มีการเชื่อมต่อ ⚠"))

                            cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=replyText))

                            return True

                        elif command == "router config":
                            router = Router.getRouter(params[0])

                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            router_actions = [
                                {
                                    "type": "message",
                                    "label": "ชื่อ Router",
                                    "text": "Router Rename, " + router.name
                                },
                                {
                                    "type": "message",
                                    "label": "ปิด/เปิด Interfaces",
                                    "text": "Router Config Interfaces, " + router.name
                                },
                            ]
                            cls.sendReplyButton(event['replyToken'],
                                                router.name,
                                                "แก้ไขข้อมูล Router",
                                                actions=router_actions
                                                )

                            return True

                        elif command == "router config interfaces":

                            router = Router.getRouter(params[0])
                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            router_detail = getRouterSMMP(router.ip, router.snmp_read)

                            carousel_template = CarouselTemplate(columns=[
                                CarouselColumn(text="ปิด/เปิดการใช้งาน Interface %s บน Router %s" % (interface['name'], router.name),
                                               title="%s [%s]" % (interface['name'], ("ปิดใช้งาน ⛔" if interface['admin_status'] == "down" else "ปกติ ✅" if interface['line_status'] == "up" else "ไม่มีการเชื่อมต่อ ⚠")),
                                               actions=[
                                                   MessageAction(label='เปิดใช้งาน', text='Interface Up, %s, %s' % (router.name, interface['index'])),
                                                   MessageAction(label='ปิดใช้งาน', text='Interface Down, %s, %s' % (router.name, interface['index']))
                                               ],
                                               thumbnail_image_url="https://images.pexels.com/photos/2881224/pexels-photo-2881224.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"
                                               )
                                for interface in router_detail['interfaces']
                            ])
                            cls.line_bot_api.reply_message(event['replyToken'],
                                                           TemplateSendMessage(
                                                               alt_text='ข้อความนี้แสดงได้เฉพาะบนโทรศัพท์มือถือ',
                                                               template=carousel_template)
                                                           )

                            return True

                        elif command == "router rename":
                            router = Router.getRouter(params[0])

                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            user.state = User.STATE_SETTING
                            user.current_router = router.name
                            user.current_config = "hostname"

                            statusText = "กรุณาพิมพ์ชื่อ Router ที่ต้องการตั้ง หากต้องการยกเลิกให้พิมพ์ \"exit\""
                            cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                            return True

                        elif command == "interface up":

                            router = Router.getRouter(params[0])
                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            interface_index = params[1]

                            setInterfaceAdminStatus(router.ip, router.snmp_write, interface_index, "up")

                            statusText = "เปิดใช้งาน Interface แล้ว"
                            cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                            return True

                        elif command == "interface down":

                            router = Router.getRouter(params[0])
                            if router is None:
                                statusText = "ไม่พบ Router ที่ท่านเลือก"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                return False

                            interface_index = params[1]

                            setInterfaceAdminStatus(router.ip, router.snmp_write, interface_index, "down")

                            statusText = "ปิดใช้งาน Interface แล้ว"
                            cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                            return True

                        elif command == "router remote":

                            try:
                                router = Router.getRouter(params[0])
                                if router is None:
                                    statusText = "ไม่พบ Router ที่ท่านเลือก"
                                    cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))
                                    return False

                                # print(router.getConnectionInfo())

                                net_connect = ConnectHandler(**router.getConnectionInfo())

                                if len(router.enable_password) > 0:
                                    net_connect.enable()

                                user.state = User.STATE_REMOTE
                                user.ssh_session = net_connect

                                statusText = "เชื่อมต่อกับ Console ของ Router แล้ว ท่านสามารถออกจากโหมดนี้ได้โดยใช้คำสั่ง \"exit\""
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                                return True
                            except:
                                statusText = "ไม่สามารถเชื่อมต่อกับ Console ได้"
                                cls.line_bot_api.reply_message(event['replyToken'], TextSendMessage(text=statusText))

                                user.state = User.STATE_NORMAL
                                user.ssh_session = None

                                return False


                    # cls.sendReplyButton(event['replyToken'])
        elif event['type'] == "postback":
            pass
        else:
            pass

        cls.line_bot_api.reply_message(event['replyToken'],
                                       TextSendMessage(
                                           text="ไม่พบคำสั่ง หรือยังไม่สามารถใช้งานได้ในขณะนี้",
                                           quick_reply=QuickReply(
                                               items=[
                                                   QuickReplyButton(
                                                       action=MessageAction(
                                                           label="ดูรายการคำสั่งทั้งหมด", text="help")
                                                   )
                                               ])))

        return False

    @classmethod
    def sendReplyButton(cls, reply_token: str, title: str, text: str, actions: list, image: str = None,
                        alt_text="ข้อความนี้แสดงได้เฉพาะบนโทรศัพท์มือถือ"):
        message = {
            "type": "buttons",
            "thumbnailImageUrl": "https://inwfile.com/s-aa/qct4vq.jpg" if image is None else image,
            "title": title,
            "text": text,
            "actions": actions
        }
        cls.line_bot_api.reply_message(
            reply_token,
            TemplateSendMessage(template=message, alt_text=alt_text)
        )

    @classmethod
    def broadcastSyslog(cls, syslog):
        message = "แจ้งเตือนจาก Router %s เวลา %s : \n%s" % (syslog['hostname'], syslog['time'], syslog['message'])
        cls.line_bot_api.broadcast([
            TextSendMessage(text=message)
        ])

    @staticmethod
    def getEventInfo(event):

        try:
            info = {
                "user_id": event['source']['userId'],
                "reply_token": event['replyToken'],
            }
        except:
            print("Cannot get event information")
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
