import os
import socket
import platform
import subprocess
import time
import re
import urllib.request
from datetime import datetime

# Set terminal color to green on black (Matrix style)
def set_terminal_colors():
    if platform.system().lower() == 'windows':
        os.system('color 0A')

# Clear the terminal screen
def clear_terminal():
    os.system('cls' if platform.system().lower() == 'windows' else 'clear')

# Display Matrix-like animation
def matrix_animation(lines=10):
    matrix_chars = "01"
    for _ in range(lines):
        line = ''.join(matrix_chars[int(time.time() * 1000) % 2] for _ in range(80))
        print(line)
        time.sleep(0.02)

# Write the diagnostic results to a log file
def write_log(log_lines, log_file):
    with open(log_file, 'a', encoding='utf-8') as f:
        for line in log_lines:
            f.write(line + '\n')

# Append explanations and suggestions
def add_explanations(log_lines):
    log_lines.append("\n--- Explanation of Results ---")
    log_lines.append("Hostname: Identifies your computer on the network.")
    log_lines.append("IP Address: Your device's unique address on the local network.")
    log_lines.append("MAC Address: The physical hardware address of network adapters.")
    log_lines.append("ARP Table: Maps IP addresses to physical MAC addresses locally.")
    log_lines.append("Wi-Fi Signal Strength: A low percentage can indicate weak signal or interference. Move closer to the router or check for obstructions.")
    log_lines.append("Internet Check: Shows whether your device can reach the internet. If failed, restart modem/router or check service provider.")
    log_lines.append("Default Gateway: The device that routes traffic from your LAN to the internet.")
    log_lines.append("Public IP: The external IP address seen by the internet.")
    log_lines.append("DNS Servers: If DNS servers are unreachable, try changing to Google's DNS (8.8.8.8).")
    log_lines.append("Ping: Measures connectivity to the target. High latency or packet loss suggests connection problems.")
    log_lines.append("Port Scan: Identifies open services on the target that could indicate vulnerabilities.")
    log_lines.append("Traceroute: Helps diagnose where traffic slows or fails en route to the destination.")

# Sanitize target for valid hostname or IP
def sanitize_target(target):
    target = re.sub(r'^https?://', '', target)
    return target.split('/')[0]

# Sanitize filename for log
def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '', name)

# Display local network info
def get_local_network_info(log_lines):
    print("\n💻 Local Network Info:")
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        log_lines.append(f"Hostname: {hostname}")
        log_lines.append(f"IP Address: {ip}")
        print(f"Hostname: {hostname}")
        print(f"IP Address: {ip}")
    except:
        log_lines.append("Hostname/IP retrieval failed.")

    try:
        if platform.system().lower() == 'windows':
            mac = subprocess.check_output('getmac', shell=True).decode()
        else:
            mac = subprocess.check_output("ifconfig | grep ether", shell=True).decode()
        log_lines.append("MAC Addresses:")
        log_lines.append(mac)
        print("\n🔗 MAC Address:")
        print(mac)
    except:
        log_lines.append("MAC retrieval failed.")

    try:
        if platform.system().lower() == 'windows':
            gateway = subprocess.check_output('ipconfig', shell=True, text=True)
            gateway_line = next((line for line in gateway.split('\n') if 'Default Gateway' in line), None)
            if gateway_line:
                gateway_ip = gateway_line.split(':')[-1].strip()
                log_lines.append(f"Default Gateway: {gateway_ip}")
                print(f"Default Gateway: {gateway_ip}")
    except:
        log_lines.append("Gateway retrieval failed.")

# Get public IP
def get_public_ip(log_lines):
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        print(f"🌍 Public IP Address: {ip}")
        log_lines.append(f"Public IP: {ip}")
    except:
        log_lines.append("Public IP retrieval failed.")

# Get DNS servers
def get_dns_servers(log_lines):
    print("\n🔍 DNS Servers:")
    try:
        if platform.system().lower() == 'windows':
            output = subprocess.check_output('ipconfig /all', shell=True, text=True).split('\n')
            dns_lines = [line.strip() for line in output if 'DNS Servers' in line or line.strip().startswith('192.')]
            for dns_line in dns_lines:
                print(dns_line)
                log_lines.append(f"DNS Server: {dns_line}")
        else:
            resolv_conf = subprocess.check_output('cat /etc/resolv.conf', shell=True, text=True)
            print(resolv_conf)
            log_lines.append("DNS Configuration:")
            log_lines.append(resolv_conf)
    except:
        log_lines.append("DNS retrieval failed.")

# Show ARP table
def show_arp_table(log_lines):
    print("\n📋 ARP Table:")
    try:
        arp = subprocess.check_output('arp -a', shell=True).decode()
        log_lines.append("\nARP Table:")
        log_lines.append(arp)
        print(arp)
    except:
        log_lines.append("ARP table retrieval failed.")

# Wi-Fi signal strength
def get_wifi_signal_strength(log_lines):
    print("\n📶 Wi-Fi Signal Strength:")
    signal_strength = "0%"
    try:
        wifi_output = subprocess.check_output('netsh wlan show interfaces', shell=True, text=True).split('\n')
        signal_line = next((line for line in wifi_output if 'Signal' in line), None)
        if signal_line:
            signal_strength = signal_line.split(':')[1].strip()
    except:
        pass
    print(f"Signal Strength: {signal_strength}")
    log_lines.append(f"Wi-Fi Signal Strength: {signal_strength}")

# Internet connectivity check
def check_internet_connectivity(log_lines):
    print("\n🌐 Internet Connectivity:")
    try:
        subprocess.check_output(['ping', '-n' if platform.system().lower() == 'windows' else '-c', '1', '8.8.8.8'], stderr=subprocess.DEVNULL)
        print("✅ Internet is connected.")
        log_lines.append("Internet Status: Connected")
    except:
        print("❌ Internet is NOT connected.")
        log_lines.append("Internet Status: Disconnected")

# Traceroute
def traceroute(target, log_lines):
    print("\n🚀 Traceroute:")
    command = 'tracert' if platform.system().lower() == 'windows' else 'traceroute'
    try:
        result = subprocess.check_output([command, target], stderr=subprocess.STDOUT, text=True)
        print(result)
        log_lines.append("Traceroute Result:")
        log_lines.append(result)
    except:
        log_lines.append("Traceroute failed.")

# Quick port scan
def quick_port_scan(target, log_lines):
    print("\n🛡️ Quick Port Scan:")
    ports = [22, 80, 443, 3389]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target, port))
        status = "OPEN" if result == 0 else "CLOSED"
        line = f"Port {port}: {status}"
        print(line)
        log_lines.append(line)
        sock.close()

# Ping function
def ping_target(target, count, log_lines):
    print(f"\n📡 Pinging {target}:")
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), target]

    replies = 0
    timeouts = 0

    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    if 'Reply from' in line or 'bytes from' in line:
                        replies += 1
                        print(f"Reply #{replies}: {line}")
                        log_lines.append(f"Reply #{replies}: {line}")
                    else:
                        print(line)
                        log_lines.append(line)

                    if 'Request timed out' in line or 'Destination Host Unreachable' in line:
                        timeouts += 1

        if timeouts >= 3:
            warning = f"⚠️ Multiple timeouts detected. Possible Wi-Fi or internet issue."
            print(warning)
            log_lines.append(warning)

    except Exception as e:
        error = f"❌ Ping failed: {e}"
        print(error)
        log_lines.append(error)

# Main function
def auto_network_diagnostics():
    set_terminal_colors()
    clear_terminal()
    matrix_animation(10)

    print("🛰️  Matrix Network Diagnostics v5.2\n")
    matrix_animation(3)

    target = input("🎯 Enter target to ping (e.g., google.com): ").strip()
    target = sanitize_target(target)
    if not target:
        print("❌ Invalid target. Exiting.")
        return

    try:
        count = int(input("🔢 Enter number of pings: ").strip())
    except:
        count = 4

    log_name = input("📄 Enter log file name (no extension): ").strip()
    log_name = sanitize_filename(log_name) or f"network_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    log_file = log_name + ".txt"

    log = [f"📝 Network Report: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]

    get_local_network_info(log)
    get_public_ip(log)
    get_dns_servers(log)
    get_wifi_signal_strength(log)
    check_internet_connectivity(log)
    time.sleep(1)

    show_arp_table(log)
    time.sleep(1)

    ping_target(target, count, log)
    quick_port_scan(target, log)
    traceroute(target, log)

    add_explanations(log)

    log.append("\n✅ Diagnostics Complete.")
    write_log(log, log_file)

    print(f"\n📝 Log saved as: {log_file}")

if __name__ == "__main__":
    auto_network_diagnostics()

