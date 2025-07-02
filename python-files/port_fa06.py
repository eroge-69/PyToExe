#!/usr/bin/env python3

import netmiko
from netmiko import ConnectHandler

iosv_l2 = {
    'device_type': 'cisco_ios',
    'ip': '192.168.5.10',
    'username': 'admin',
    'password': 'C1sc0123!',
    'secret': 'C1sc0123!',
}

net_connect = ConnectHandler(**iosv_l2)
net_connect.enable()
output = net_connect.send_command('sh int status', use_textfsm=True)

# Find fa0/6 in the output
name, status = None, None
for intf in output:
    if intf['port'] == 'Fa0/6':
        name = intf['port']
        status = intf['status']
        break

if name is None:
    print('Interface Fa0/6 not found')
    exit()

print(f'Interface {name} {status}')

# Always perform shut/no shut as per your requirement
config_commands = ['int Fa0/6', 'shut', 'no shut']
output = net_connect.send_config_set(config_commands)
print(output)

output = net_connect.send_command('show int status')
print(output)