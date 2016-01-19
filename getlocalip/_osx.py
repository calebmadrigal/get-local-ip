import re
import os
import socket
import ipaddress
import subprocess
import ctypes
import ctypes.util

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


class sockaddr(ctypes.Structure):
    _fields_ = [('sa_len', ctypes.c_uint8),
                ('sa_familiy', ctypes.c_uint8),
                ('sa_data', ctypes.c_byte * 14)]


class sockaddr_in(ctypes.Structure):
    _fields_ = [('sa_len', ctypes.c_uint8),
                ('sa_familiy', ctypes.c_uint8),
                ('sin_port', ctypes.c_ushort),
                ('sin_addr', ctypes.c_byte * 4),
                ('sin_zero', ctypes.c_byte * 8)]


class sockaddr_in6(ctypes.Structure):
    _fields_ = [('sa_len', ctypes.c_uint8),
                ('sa_familiy', ctypes.c_uint8),
                ('sin6_port', ctypes.c_ushort),
                ('sin6_flowinfo', ctypes.c_ulong),
                ('sin6_addr', ctypes.c_byte * 16),
                ('sin6_scope_id', ctypes.c_ulong)]


class ifaddrs(ctypes.Structure):
    pass
ifaddrs._fields_ = [('ifa_next', ctypes.POINTER(ifaddrs)),
                    ('ifa_name', ctypes.c_char_p),
                    ('ifa_flags', ctypes.c_uint),
                    ('ifa_addr', ctypes.POINTER(sockaddr)),
                    ('ifa_netmask', ctypes.POINTER(sockaddr))]


def sockaddr_to_ip(sockaddr_ptr):
    if sockaddr_ptr[0].sa_familiy == socket.AF_INET:
        ipv4 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(sockaddr_in))
        ippacked = bytes(bytearray(ipv4[0].sin_addr))
        ip = str(ipaddress.ip_address(ippacked))
        return ip
    elif sockaddr_ptr[0].sa_familiy == socket.AF_INET6:
        ipv6 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(sockaddr_in6))
        flowinfo = ipv6[0].sin6_flowinfo
        ippacked = bytes(bytearray(ipv6[0].sin6_addr))
        ip = str(ipaddress.ip_address(ippacked))
        scope_id = ipv6[0].sin6_scope_id
        return ip, flowinfo, scope_id
    else:
        return None


def get_ip_for_interface(interface_name):
    """ Given an interface name (e.g. 'en0'), return the IPv4 IP Address associated with that interface. """
    addr = ctypes.POINTER(ifaddrs)()
    retval = libc.getifaddrs(ctypes.byref(addr))
    if retval != 0:
        eno = ctypes.get_errno()
        raise OSError(eno, os.strerror(eno))

    interface_ip = '127.0.0.1'
    while addr:
        iface_name = addr[0].ifa_name.decode()
        iface_ip = sockaddr_to_ip(addr[0].ifa_addr)
        # Make sure to get the IPv4 IP address of this interface. The IPv6 IP Address is a tuple
        if iface_name == interface_name and iface_ip and not isinstance(iface_ip, tuple):
            interface_ip = iface_ip
            break
        addr = addr[0].ifa_next

    return interface_ip


def get_interface_for_remote_ip(remote_ip):
    """ Find the interface name (e.g. 'en0') of the interface used to reach the remote_ip. """
    interface_data = subprocess.check_output('route get {}'.format(remote_ip), shell=True).decode()
    match = re.search('interface: +(\w+)', interface_data)
    if match:
        interface_name = match.group(1)
    else:
        # Default to en0
        interface_name = 'en0'
    return interface_name


def get_interface_ip(remote_ip=None):
    """ Find the IPv4 IP Address of the interface used to reach the remote_ip. """
    remote_ip = remote_ip or '8.8.8.8'
    route_interface = get_interface_for_remote_ip(remote_ip)
    interface_ip = get_ip_for_interface(route_interface)
    return interface_ip
