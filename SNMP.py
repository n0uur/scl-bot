"""
SNMP Manager Module
"""

import sys
from pysnmp.hlapi import *
import datetime

COMUNITY_CODE = 'sclbot'
IP_ADDR_RT1 = '10.0.15.7'
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
        sys.exit()


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
        sys.exit()


def getRouterHostName(ip, communityCode):
    return getSNMP(ip, communityCode, '.1.3.6.1.2.1.1.5.0')


def setRouterHostName(ip, communityCode):
    newHostName = input("NewHostName: ")
    return setSNMP(ip, communityCode, '.1.3.6.1.2.1.1.5.0', newHostName)


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


def setInterfaceAdminStatus(ip, communityCode):
    selectedInterface = input("Interface: ")
    interfaceStatus = input("Status: ")
    return setSNMP(ip, communityCode, ".1.3.6.1.2.1.2.2.1.7." + selectedInterface, Integer(DICT_SET_STATUS[interfaceStatus]))


def getInterfaceLineStatus(ip, communityCode, index):
    return DICT_GET_STATUS[getSNMP(ip, communityCode, ".1.3.6.1.2.1.2.2.1.8.%d" % index)]


def getRouterSMMP(ipAddress, communityCode):
    details = []
    details.append("ชื่อ Router : " +
                   getRouterHostName(ipAddress, communityCode))
    details.append(("เวลาที่เปิดใช้งาน : " +
                    str(getRouterUptime(ipAddress, communityCode))))
    for i in range(1, getInterfaceCount(ipAddress, communityCode)):
        details.append("Interface ที่ {0}:{1}\n\tAdmin Status: {2}\n\tOper Status: {3}".format(
            i, getInterfaceDescr(ipAddress, communityCode, i), getInterfaceAdminStatus(ipAddress, communityCode, i), getInterfaceLineStatus(ipAddress, communityCode, i)))
    print(*details)


if __name__ == '__main__':
    getRouterSMMP('10.0.15.7', 'sclbot')
