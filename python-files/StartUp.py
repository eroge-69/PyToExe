#import json;
import paramiko;

password = 'password'

#with open('Stadium.json', 'r') as file:
#    data = json.load(file)

ip_address = '10.211.2.11'#.replace('XXX', data['Arena_Code'])
commands = ['config', 'poe priority crit', 'poe power limit user-defined 32000', 'poe']

#for key, value in data.items():
#    if type(value) is list:
switch_ip = ip_address.replace('YY', key)
print("Turning " + switch_ip + " 0/1 on" + '\n')
interfaceCmd = "interface " + ',' + "0/1"
commands.insert(1, interfaceCmd)

try:
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(switch_ip, username='admin', password=password)

    command = '\n'.join(commands)
    _stdin, _stdout, _stderr = client.exec_command(command)
    print(_stdout.read().decode())
            
    client.close()
except Exception as e:
    print(e)

commands.remove(interfaceCmd)