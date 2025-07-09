import ipaddress

def ip_to_binary(ip):
    return '.'.join(f'{int(octet):08b}' for octet in ip.split('.'))

def main():
    ip_input = input("Input IPv4 address: ").strip()
    mask_input = input("Subnet Mask (CIDR /xx or dotted decimal): ").strip()

    # Convert CIDR to dotted decimal if needed
    if mask_input.startswith('/'):
        cidr = int(mask_input[1:])
        net = ipaddress.IPv4Network(f"{ip_input}/{cidr}", strict=False)
    else:
        # Assume dotted decimal mask
        net = ipaddress.IPv4Network(f"{ip_input}/{mask_input}", strict=False)

    network = net.network_address.exploded
    broadcast = net.broadcast_address.exploded
    wildcard = '.'.join(str(255 - int(octet)) for octet in net.netmask.exploded.split('.'))

    hosts = net.num_addresses
    first_ip = str(net.network_address + 1) if hosts > 2 else str(net.network_address)
    last_ip = str(net.broadcast_address - 1) if hosts > 2 else str(net.broadcast_address)

    print("\nResults:\n")
    print(f"Network\t{network}\t{ip_to_binary(network)}")
    print(f"Broadcast\t{broadcast}\t{ip_to_binary(broadcast)}")
    print(f"Wildcard\t{wildcard}\t{ip_to_binary(wildcard)}")
    print(f"First IP\t{first_ip}\t{ip_to_binary(first_ip)}")
    print(f"Last IP\t{last_ip}\t{ip_to_binary(last_ip)}")
    print(f"Hosts\t{hosts}\t")

if __name__ == "__main__":
    main()
