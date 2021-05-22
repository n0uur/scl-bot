"""
SNMP Manager Module
"""

import datetime

from pysnmp.hlapi import *

DICT_GET_STATUS = {"1": "up", "2": "down"}
DICT_SET_STATUS = {"up": "1", "down": "2"}


def getSNMP(ipAddress, communityCode, oid, port=161):
    try:
        iterator = getCmd(SnmpEngine(),
                          CommunityData(communityCode),
                          UdpTransportTarget((ipAddress, port)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid))
                          )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        for varBind in varBinds:  # SNMP response contents
            result = [x.prettyPrint() for x in varBind][-1]

        return result
    except:
        print('Connection to router time out!')
        return None


def setSNMP(ipAddress, communityCode, oid, value, port=161):
    try:
        iterator = setCmd(SnmpEngine(),
                          CommunityData(communityCode),
                          UdpTransportTarget((ipAddress, port)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid), value)
                          )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        for varBind in varBinds:  # SNMP response contents
            result = [x.prettyPrint() for x in varBind][-1]

        return result
    except:
        print('Connection to router time out!')
        return None


def getRouterHostName(ip, communityCode):
    return getSNMP(ip, communityCode, '.1.3.6.1.4.1.9.2.1.3.0')


def setRouterHostName(ip, communityCode, hostname):
    return setSNMP(ip, communityCode, '.1.3.6.1.2.1.1.5.0', hostname)


def getRouterUptime(ip, communityCode):
    routerUptime = getSNMP(ip, communityCode, '.1.3.6.1.2.1.1.3.0')
    routerUptime = datetime.timedelta(seconds=int(routerUptime) / 100)
    return routerUptime


def getInterfaceCount(ip, communityCode):
    return int(getSNMP(ip, communityCode, '.1.3.6.1.2.1.2.1.0'))


def getInterfaceDescr(ip, communityCode, index):
    return getSNMP(ip, communityCode, ".1.3.6.1.2.1.2.2.1.2.%d" % index)


def getInterfaceAdminStatus(ip, communityCode, index):
    return DICT_GET_STATUS[getSNMP(ip, communityCode, ".1.3.6.1.2.1.2.2.1.7.%d" % index)]


def setInterfaceAdminStatus(ip, communityCode, interface, status):
    return setSNMP(ip, communityCode, ".1.3.6.1.2.1.2.2.1.7." + interface,
                   Integer(DICT_SET_STATUS[status]))


def getInterfaceLineStatus(ip, communityCode, index):
    return DICT_GET_STATUS[getSNMP(ip, communityCode, ".1.3.6.1.2.1.2.2.1.8.%d" % index)]


def getRouterSMMP(ipAddress, communityCode):
    details = {
        "hostname": getRouterHostName(ipAddress, communityCode),
        "uptime": str(getRouterUptime(ipAddress, communityCode)),
        "interfaces": [
            {
                "index": i,
                "name": getInterfaceDescr(ipAddress, communityCode, i),
                "admin_status": getInterfaceAdminStatus(ipAddress, communityCode, i),
                "line_status": getInterfaceLineStatus(ipAddress, communityCode, i)
            }
            for i in range(1, getInterfaceCount(ipAddress, communityCode))
        ]
    }
    return details
    # details.append("ชื่อ Router : " +
    #                getRouterHostName(ipAddress, communityCode))
    # details.append(("เวลาที่เปิดใช้งาน : " +
    #                 str(getRouterUptime(ipAddress, communityCode))))
    # for i in range(1, getInterfaceCount(ipAddress, communityCode)):
    #     details.append("Interface ที่ {0}:{1}\n\tAdmin Status: {2}\n\tOper Status: {3}".format(
    #         i, getInterfaceDescr(ipAddress, communityCode, i), getInterfaceAdminStatus(ipAddress, communityCode, i),
    #         getInterfaceLineStatus(ipAddress, communityCode, i)))
    # print(*details)


if __name__ == '__main__':
    getRouterSMMP('10.0.15.7', 'sclbot')
