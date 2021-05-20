"""
Syslog receiver
"""

import socketserver

SYSLOG_PORT = 514

class SyslogHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        return super().handle()

# for debugging

if __name__ == "__main__":
    try:
        server = socketserver.UDPServer(("0.0.0.0", SYSLOG_PORT), SyslogHandler)
        server.serve_forever()
    except Exception:
        print("Something went wrong.. :(")

