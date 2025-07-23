# scan_subnet.py
import ipaddress
import socket
from scapy.all import ARP, Ether, srp

def scan(ip_net):
    try:
        net = ipaddress.ip_network(ip_net, strict=False)
    except ValueError:
        print("Subnet non valida.")
        return

    print(f"Scansione di {ip_net} in corso... ({net.num_addresses} indirizzi)\n")
    print(f"{'IP':<16} {'MAC':<18} {'Hostname'}")
    print("-" * 50)

    if net.num_addresses > 1024:
        print("⚠️ Attenzione: rete molto grande. La scansione può richiedere molto tempo.")

    arp = ARP(pdst=str(net))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]

    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "N/A"
        print(f"{ip:<16} {mac:<18} {hostname}")

if __name__ == "__main__":
    subnet = input("Inserisci subnet (es. 192.168.0.0/16): ")
    scan(subnet)
