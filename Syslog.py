"""
Syslog receiver
"""
import socketserver
import logging
from SNMP import getRouterHostName

SYSLOG_PORT = 514
SYSLOG_SERVER = "ip at your interface"
ROUTER_IP = "router ip"
COMMUNITY_CODE = "commu code"


class SyslogHandler(socketserver.BaseRequestHandler):
    def handle(self) -> dict:
        data = bytes.decode(self.request[0].strip())
        logData = data.split("*")[-1].split(": ")
        # print(logData)
        logTime = logData[0]
        hostName = getRouterHostName(ROUTER_IP, COMMUNITY_CODE).split(".")[0]
        logMessage = ""
        for i in logData[1:]:
            logMessage += i
        logDataDict = {
            "time": logTime,
            "hostname": hostName,
            "message": logMessage
        }
        print(logDataDict)
        return logDataDict


# for debugging

def startSyslog():
    try:
        logging.warning(" * Starting Syslog Server on http://{}:{}/".format(SYSLOG_SERVER, SYSLOG_PORT))
        server = socketserver.UDPServer((SYSLOG_SERVER, SYSLOG_PORT), SyslogHandler)
        server.serve_forever()
    except Exception:
        print("Something went wrong.. :(")


if __name__ == "__main__":
    startSyslog()
