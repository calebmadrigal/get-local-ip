import platform
import socket

platform_name = platform.system()
if platform_name == 'Windows':
    from ._win32 import get_interface_ip
elif platform_name == 'Darwin':
    from ._osx import get_interface_ip
elif platform_name == 'Linux':
    from ._linux import get_interface_ip
else:
    raise RuntimeError("Unsupported Operating System")


def get_local_ip(remote_host='8.8.8.8'):
    """ Gets the local IP of the computer this is running on by first trying to get it from
    the standard socket interface, and if that returns '127.0.0.1' (due to a local proxy),
    then try to get the IP address of the network interface used to reach the remote_host. """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((remote_host, 80))
    local_ip = s.getsockname()[0]
    s.close()

    if local_ip == '127.0.0.1':
        return get_interface_ip(remote_host)

    return local_ip

__all__ = ['get_local_ip', 'get_interface_ip']
