"""
Main controller of this program
central of function to call from another module (likely proxy ?)
"""

import pyping

def check_router_status(router_id) -> bool:
    # get router ip :P
    r = pyping.ping('localhost')
    if r.ret_code == 0:
        return True
    return False

def check_syslog_status():
    pass

def get_routers():
    pass
