"""
Syslog receiver
"""

from Line import Line
import socketserver

SYSLOG_PORT = 514


class SyslogHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip())
        logData = data.split("*")[-1].split(": ")
        # print(logData)
        logTime = logData[2]
        hostName = data.split("*")[0].split(":")[1].strip()
        logMessage = ""
        for i in logData[3:]:
            logMessage += i
        logDataDict = {
            "time": logTime,
            "hostname": hostName,
            "message": logMessage
        }
        Line.broadcastSyslog(logDataDict)
        # print(logDataDict)
        # return logDataDict


# for debugging

def startSyslog():
    server = socketserver.UDPServer(("0.0.0.0", SYSLOG_PORT), SyslogHandler)
    server.serve_forever()


if __name__ == "__main__":
    startSyslog()
