def ip_to_binary(ip):
    return '.'.join(f'{int(octet):08b}' for octet in str(ip).split('.'))

IP_Addr = ipaddress.ip_interface(input('Enter IP address in IP/Mask Form : '))

Net_Addr = IP_Addr.network
pref_len = IP_Addr.with_prefixlen
Mask = IP_Addr.with_netmask
wildcard = IP_Addr.hostmask
broadcast_address = Net_Addr.broadcast_address
hosts = list(Net_Addr.hosts())

print('Network Address : ', str(Net_Addr).split('/')[0], '\t', ip_to_binary(str(Net_Addr.network_address)))
print('Broadcast Address : ' , broadcast_address, '\t', ip_to_binary(broadcast_address))
print('CIDR Notation : ', pref_len.split('/')[1])
print('Subnet Mask : ', Mask.split('/')[1], '\t', ip_to_binary(Mask.split('/')[1]))
print('Wildcard Mask : ' , wildcard, '\t', ip_to_binary(wildcard))
print('First IP : ' , hosts[0], '\t', ip_to_binary(hosts[0]))
print('Last IP : ' , hosts[-1], '\t', ip_to_binary(hosts[-1]))
print('Hosts Count :', len(hosts))
