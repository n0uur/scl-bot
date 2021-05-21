"""
SNMP Manager Module
"""

import datetime
import sys

from pysnmp.hlapi import *

COMMUNITY_CODE = "sclbot"
RT_IP_ADDR = {"1": "10.0.15.7"}
DICT_GET_STATUS = {"1": "up", "2": "down"}
DICT_SET_STATUS = {"up": "1", "down": "2"}


def getSNMP(oid):
    try:
        iterator = getCmd(SnmpEngine(),
                          CommunityData(COMMUNITY_CODE),
                          UdpTransportTarget((RT_IP_ADDR["1"], 161)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid))
                          )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        for varBind in varBinds:  # SNMP response contents
            result = [x.prettyPrint() for x in varBind][-1]

        return result
    except:
        print("Connection to router timeout!")
        sys.exit()


def setSNMP(oid, value):
    try:
        iterator = setCmd(SnmpEngine(),
                          CommunityData(COMMUNITY_CODE),
                          UdpTransportTarget((RT_IP_ADDR["1"], 161)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid), value)
                          )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        for varBind in varBinds:  # SNMP response contents
            result = [x.prettyPrint() for x in varBind][-1]

        return result
    except:
        print("Connection to router timeout!")
        sys.exit()


def getRouterHostName():
    return getSNMP(".1.3.6.1.2.1.1.5.0")


def setRouterHostName():
    newHostName = input("NewHostName: ")
    return setSNMP(".1.3.6.1.2.1.1.5.0", newHostName)


def getRouterUptime():
    routerUptime = getSNMP(".1.3.6.1.2.1.1.3.0")
    routerUptime = datetime.timedelta(seconds=int(routerUptime) / 100)
    return routerUptime


def getInterfaceCount():
    return int(getSNMP(".1.3.6.1.2.1.2.1.0"))


def getInterfaceDescr(index):
    return getSNMP(".1.3.6.1.2.1.2.2.1.2.%d" % index)


def getInterfaceAdminStatus(index):
    return DICT_GET_STATUS[getSNMP(".1.3.6.1.2.1.2.2.1.7.%d" % index)]


def setInterfaceAdminStatus():
    selectedInterface = input("Interface: ")
    interfaceStatus = input("Status: ")
    return setSNMP(".1.3.6.1.2.1.2.2.1.7." + selectedInterface, Integer(DICT_SET_STATUS[interfaceStatus]))


def getInterfaceLineStatus(index):
    return DICT_GET_STATUS[getSNMP(".1.3.6.1.2.1.2.2.1.8.%d" % index)]


def main():
    # setRouterHostName()
    # setInterfaceAdminStatus()
    print("RouterHostName:", getRouterHostName())
    print("RouterUptime:", getRouterUptime())
    for i in range(1, getInterfaceCount()):
        print("RouterInterface {0}:{1}\n\tAdmin Status: {2}\n\tOper Status: {3}".format(
            i, getInterfaceDescr(i), getInterfaceAdminStatus(i), getInterfaceLineStatus(i)))


main()
