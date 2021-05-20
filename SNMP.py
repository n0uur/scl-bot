"""
SNMP Manager Module
"""

from pysnmp.hlapi import *
import datetime

COMUNITY_CODE = 'sclbot'
IP_ADDR_RT1 = '10.0.15.7'


def getRouterHostName():
    iterator = getCmd(SnmpEngine(),
                      CommunityData(COMUNITY_CODE),
                      UdpTransportTarget((IP_ADDR_RT1, 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.5.0'))
                      )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for varBind in varBinds:  # SNMP response contents
        routerName = [x.prettyPrint() for x in varBind][-1]

    return routerName


def getRouterUptime():
    iterator = getCmd(SnmpEngine(),
                      CommunityData(COMUNITY_CODE),
                      UdpTransportTarget((IP_ADDR_RT1, 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.3.0'))
                      )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for varBind in varBinds:  # SNMP response contents
        routerUptime = [x.prettyPrint() for x in varBind][-1]

    routerUptime = datetime.timedelta(seconds=int(routerUptime) / 100)

    return routerUptime


def getInterfaceCount():
    iterator = getCmd(SnmpEngine(),
                      CommunityData(COMUNITY_CODE),
                      UdpTransportTarget((IP_ADDR_RT1, 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity('.1.3.6.1.2.1.2.1.0'))
                      )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for varBind in varBinds:  # SNMP response contents
        interfaceCount = [x.prettyPrint() for x in varBind][-1]

    return int(interfaceCount)


def getInterfaceDescr(index):
    iterator = getCmd(SnmpEngine(),
                       CommunityData(COMUNITY_CODE),
                       UdpTransportTarget((IP_ADDR_RT1, 161)),
                       ContextData(),
                       ObjectType(ObjectIdentity(
                           ".1.3.6.1.2.1.2.2.1.2.%d" % index))
                       )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for varBind in varBinds:  # SNMP response contents
        interfaceDescr = [x.prettyPrint() for x in varBind][-1]

    return interfaceDescr

def getInterfaceAdminStatus(index):
    iterator = getCmd(SnmpEngine(),
                       CommunityData(COMUNITY_CODE),
                       UdpTransportTarget((IP_ADDR_RT1, 161)),
                       ContextData(),
                       ObjectType(ObjectIdentity(
                           ".1.3.6.1.2.1.2.2.1.7.%d" % index))
                       )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for varBind in varBinds:  # SNMP response contents
        interfaceAdminStatus = [x.prettyPrint() for x in varBind][-1]
    dict = {"1":"up", "2":"down"}
    return dict[interfaceAdminStatus]

def getInterfaceLineStatus(index):
    iterator = getCmd(SnmpEngine(),
                       CommunityData(COMUNITY_CODE),
                       UdpTransportTarget((IP_ADDR_RT1, 161)),
                       ContextData(),
                       ObjectType(ObjectIdentity(
                           ".1.3.6.1.2.1.2.2.1.8.%d" % index))
                       )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    for varBind in varBinds:  # SNMP response contents
        interfaceAdminStatus = [x.prettyPrint() for x in varBind][-1]
    dict = {"1":"up", "2":"down"}
    return dict[interfaceAdminStatus]

def main():
    print("RouterHostName:", getRouterHostName())
    print("RouterUptime:", getRouterUptime())
    for i in range(1, getInterfaceCount()):
        print("RouterInterface {0}:{1}\n\tAdmin Status: {2}\n\tOper Status: {3}".format(i, getInterfaceDescr(i), getInterfaceAdminStatus(i), getInterfaceLineStatus(i)))


main()
