"""
Router Model
"""

import yaml
from icmplib import ping


class Router:
    routers = None

    def __init__(self, router_details):
        self.name = router_details['name']  # use as Id
        self.ip = router_details['ip']
        self.snmp_read = router_details['snmp_read']
        self.snmp_write = router_details['snmp_write']
        self.ssh_username = router_details['ssh_username']
        self.ssh_password = router_details['ssh_password']
        self.enable_password = router_details['enable_password']

    def getStatus(self):
        host = ping(self.ip, count=2)
        return host.is_alive

    @classmethod
    def getRouter(cls, router_id):
        if cls.routers is None:
            # todo : read routers.yml file
            routers = None
            with open("routers.yml") as file:
                routers = yaml.load(file, Loader=yaml.FullLoader)['routers']
                # print(routers)
            if routers is None:
                print("routers.yml not found! copy routers.yml.example to routers.yml and try again.")
                return None

            cls.routers = [
                Router(router) for router in routers
            ]
        for router in cls.routers:
            if router.name == router_id:
                return router
        return None
