import subprocess


def get_interface_ip(remote_ip=None):
    interface_ip = '127.0.0.1'
    remote_ip = remote_ip or '8.8.8.8'
    result = subprocess.check_output('ip route get {}'.format(remote_ip), shell=True)
    result_split = result.split()

    # result_split will look like:
    # ['8.8.8.8', 'via', '172.16.185.2', 'dev', 'eth0', 'src', '172.16.185.173', 'cache']
    #
    # So just find the index containing 'src', and the next token will be the interface IP
    index_containing_src = 0
    for i in range(len(result_split)):
        if result_split[i].decode() == 'src':
            index_containing_src = i
            break

    interface_ip_index = index_containing_src + 1
    if interface_ip_index < len(result_split):
        interface_ip = result_split[interface_ip_index]

    return interface_ip
