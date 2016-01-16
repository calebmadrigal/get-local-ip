import ctypes
import socket
import struct
from ctypes.wintypes import DWORD, ULONG

ip_help_api = ctypes.windll.Iphlpapi
MAX_INTERFACES = 10

#
# win api helper classes and functions
#


class IPAddr(ctypes.Structure):
    _fields_ = [("S_addr", ctypes.c_ulong)]

    def __str__(self):
        return socket.inet_ntoa(struct.pack("L", self.S_addr))


class MIB_IPADDRROW(ctypes.Structure):
    _fields_ = [("dwAddr", IPAddr),
                ("dwIndex", DWORD),
                ("dwMask", DWORD),
                ("dwBCastAddr", IPAddr),
                ("dwReasmSize", DWORD),
                ("unused1", ctypes.c_ushort),
                ("wType", ctypes.c_ushort),
                ]


class MIB_IPADDRTABLE(ctypes.Structure):
    _fields_ = [("dwNumEntries", DWORD),
                ("table", MIB_IPADDRROW * MAX_INTERFACES)]


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def inet_addr(ip):
    return IPAddr(struct.unpack("L", socket.inet_aton(ip))[0])


#
# get ip
#


def get_interface_by_index(index):
    table = MIB_IPADDRTABLE()
    size = ULONG(ctypes.sizeof(table))
    table.dwNumEntries = 0
    ip_help_api.GetIpAddrTable(ctypes.byref(table), ctypes.byref(size), 0)

    for n in range(table.dwNumEntries):
        row = table.table[n]
        if row.dwIndex == index:
            return str(row.dwAddr)
    raise IndexError("interface index out of range")


def get_best_index(remote_ip):
        remote_ip = inet_addr(remote_ip)
        interface_index = ctypes.c_ulong(0)
        err = ip_help_api.GetBestInterface(remote_ip, ctypes.byref(interface_index))
        return int(interface_index.value)


def get_interface_ip(remote_ip=None):
        remote_ip = remote_ip or '8.8.8.8'  # Google DNS
        interface_index = get_best_index(remote_ip)
        return get_interface_by_index(interface_index)


