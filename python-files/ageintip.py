#!/usr/bin/env python3

# ==============================================================================
#  Ageint Security - System IP Configuration Utility v2.2 (Persistent)
#
#  Proprietary and Confidential
#  Author: Levi McCarty
#  © 2024 Ageint Security. All Rights Reserved.
# ==============================================================================

import sys
import subprocess
import os
import platform
import socket

# --- Dependency Bootstrapper ---
REQUIRED_PACKAGES = {
    "psutil": "psutil",
    "requests": "requests",
    "colorama": "colorama"
}

def install_dependencies():
    """Checks for and installs missing Python packages."""
    missing_packages = []
    for package_name in REQUIRED_PACKAGES:
        try:
            __import__(REQUIRED_PACKAGES[package_name])
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"Ageint IP Config: One-time setup required.")
        print(f"Missing components: {', '.join(missing_packages)}")
        if input("Attempt automatic installation? (y/n): ").lower() != 'y':
            print("Installation aborted.")
            sys.exit(1)
        
        print("Attempting to install...\n")
        try:
            command = [sys.executable, "-m", "pip", "install", "--upgrade"] + missing_packages
            subprocess.check_call(command)
            print("\n[SUCCESS] Dependencies installed! Please re-run the script.")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] Failed to install packages: {e}. Please install manually.")
            sys.exit(1)

# Run the dependency check first
install_dependencies()

# --- Now, we can safely import all packages ---
import psutil
import requests
from colorama import init, Fore, Style

# --- Global Configuration & Initialization ---
init(autoreset=True)

TITLE = r"""
    _            _     _     ___ ___  
   /_\  __ _ ___(_)_ _| |_  |_ _| _ \ 
  / _ \/ _` / -_) | ' \  _|  | ||  _/ 
 /_/ \_\__, \___|_|_||_\__| |___|_|   
       |___/                          
"""
BRANDING = "Application made by Levi with Ageint Security."

# --- Helper Functions ---

def get_default_gateway():
    """Gets the default gateway using OS-native commands for reliability."""
    system = platform.system()
    try:
        if system == "Windows":
            command = "powershell -Command \"(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object -Property RouteMetric | Select-Object -First 1).NextHop\""
            gateway = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode().strip()
        elif system in ["Linux", "Darwin"]: # Linux and macOS
            command = "ip route | grep default"
            output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode()
            gateway = output.split()[2]
        else:
            return "N/A (Unsupported OS)"
        return gateway if gateway else "Not Found"
    except Exception:
        return "Not Found"

def get_dns_servers():
    """Gets DNS servers in a cross-platform way."""
    dns_servers = []
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode()
            for line in output.splitlines():
                if "DNS Servers" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        server = parts[1].strip()
                        if server and server not in dns_servers and '.' in server:
                            dns_servers.append(server)
        else: # Linux and macOS
             with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.strip().startswith("nameserver"):
                        server = line.split()[1]
                        if server not in dns_servers:
                            dns_servers.append(server)
    except Exception:
        return ["Not Found"]
    return dns_servers if dns_servers else ["Not Found"]

def get_public_ip_info():
    """Fetches public IP and ISP information."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=3)
        response.raise_for_status()
        data = response.json()
        return {"ip": data.get('ip', 'N/A'), "isp": data.get('org', 'N/A')}
    except requests.RequestException:
        return {"ip": "Not Found", "isp": "Check Internet Connection"}

def generate_and_display_report():
    """Gathers all IP information and prints it in a clean report."""
    os.system('cls' if platform.system() == "Windows" else 'clear')
    print(Fore.CYAN + Style.BRIGHT + TITLE)
    print(Fore.CYAN + BRANDING.center(60))
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)

    # --- Local Network Adapters ---
    print(Fore.YELLOW + Style.BRIGHT + "\n--- Local Network Configuration ---\n")
    
    all_addrs = psutil.net_if_addrs()
    all_stats = psutil.net_if_stats()
    default_gateway = get_default_gateway()

    found_active_adapter = False
    sorted_adapters = sorted(all_addrs.items(), key=lambda item: all_stats[item[0]].isup, reverse=True)

    for name, addrs in sorted_adapters:
        stats = all_stats[name]
        if not stats.isup or "lo" in name.lower():
            continue

        found_active_adapter = True
        print(Fore.WHITE + Style.BRIGHT + f"Adapter: {name}")
        
        ipv4_addr, subnet, mac_addr = "N/A", "N/A", "N/A"

        for addr in addrs:
            if addr.family == socket.AF_INET:
                ipv4_addr = addr.address
                subnet = addr.netmask
            elif hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                mac_addr = addr.address.upper().replace("-",":")
        
        print(f"  {'IPv4 Address':<18}: {Fore.GREEN}{ipv4_addr}")
        print(f"  {'Subnet Mask':<18}: {Fore.WHITE}{subnet}")
        
        if ipv4_addr != "N/A" and default_gateway != "Not Found":
            try:
                ip_obj = socket.inet_aton(ipv4_addr)
                subnet_obj = socket.inet_aton(subnet)
                gateway_obj = socket.inet_aton(default_gateway)
                if (int.from_bytes(ip_obj, 'big') & int.from_bytes(subnet_obj, 'big')) == \
                   (int.from_bytes(gateway_obj, 'big') & int.from_bytes(subnet_obj, 'big')):
                    print(f"  {'Default Gateway':<18}: {Fore.WHITE}{default_gateway}")
            except socket.error:
                pass # Ignore if IPs are not valid for comparison
        
        print(f"  {'MAC Address':<18}: {Fore.WHITE}{mac_addr}")
        print("-" * 35)

    if not found_active_adapter:
        print(f"{Fore.RED}No active network adapters found.")

    # --- DNS & External Information ---
    print(Fore.YELLOW + Style.BRIGHT + "\n--- DNS & External Information ---\n")
    
    dns_servers = get_dns_servers()
    print(f"{'DNS Servers':<18}: {Fore.WHITE}{', '.join(dns_servers)}")
    
    public_info = get_public_ip_info()
    print(f"{'Public IP Address':<18}: {Fore.GREEN}{public_info['ip']}")
    print(f"{'Internet Provider':<18}: {Fore.WHITE}{public_info['isp']}")

    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 60)
    print(Fore.CYAN + "Report Complete.".center(60))
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)


if __name__ == "__main__":
    try:
        generate_and_display_report()
        input("\nPress Enter to exit...")  # <-- This line keeps the application open
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        input("\nPress Enter to exit...")
