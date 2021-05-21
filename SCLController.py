"""
Main controller of this program
central of function to call from another module (likely proxy ?)
"""

# import pyping
import yaml


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

    @classmethod
    def getRouter(cls, router_id):
        if cls.routers is None:
            # todo : read routers.yml file
            routers = None
            with open("routers.yml") as file:
                routers = yaml.load(file, Loader=yaml.FullLoader)['routers']
                # print(routers)
            if routers is None:
                return None

            cls.routers = [
                Router(router) for router in routers
            ]
        for router in cls.routers:
            if router.name == router_id:
                return router
        return None


class SCL:

    @staticmethod
    def check_router_status(router) -> bool:
        # get router ip :P
        # r = pyping.ping('localhost')
        # if r.ret_code == 0:
        #     return True
        # return False
        pass

    @staticmethod
    def check_syslog_status():
        pass

    @staticmethod
    def get_routers():
        pass

if __name__ == "__main__":
    pass