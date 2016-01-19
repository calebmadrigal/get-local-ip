from getlocalip import get_local_ip, get_interface_ip

print('Local IP: {}'.format(get_local_ip()))
print('Default interface IP: {}'.format(get_interface_ip('8.8.8.8')))
