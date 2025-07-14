import os
import socket
import requests
import fade
import ifaddr
import ipaddress
from colorama import init, Fore
from scapy.all import ARP, Ether, srp, conf
from mac_vendor_lookup import MacLookup, VendorNotFoundError

init(autoreset=True)

def show_banner():
    banner = """
   ▄████████ ▄██   ▄   ███▄▄▄▄      ▄████████    ▄███████▄    ▄████████  ▄█  ▀████    ▐████▀ 
  ███    ███ ███   ██▄ ███▀▀▀██▄   ███    ███   ███    ███   ███    ███ ███    ███▌   ████▀  
  ███    █▀  ███▄▄▄███ ███   ███   ███    ███   ███    ███   ███    █▀  ███▌    ███  ▐███    
  ███        ▀▀▀▀▀▀███ ███   ███   ███    ███   ███    ███   ███        ███▌    ▀███▄███▀    
▀███████████ ▄██   ███ ███   ███ ▀███████████ ▀█████████▀  ▀███████████ ███▌    ████▀██▄     
         ███ ███   ███ ███   ███   ███    ███   ███                 ███ ███    ▐███  ▀███    
   ▄█    ███ ███   ███ ███   ███   ███    ███   ███           ▄█    ███ ███   ▄███     ███▄  
 ▄████████▀   ▀█████▀   ▀█   █▀    ███    █▀   ▄████▀       ▄████████▀  █▀   ████       ███▄                                                                                                                                                               
"""
    print(fade.brazil(banner))

def show_layout():
    menu = """
┌──────────────────────────────────────────────────────────────────────────────┐
│ Available Tools:                                                             │
│  [1] Get IP              [2] Network Scanner         [3] Port Checker        │
│  [4] Reputation Check    [5] Geolocation             [6] Discord Token Check │
│  [7] Ping Device         [8] Webhook Inspector       [9] Server Info Fetcher │
├──────────────────────────────────────────────────────────────────────────────┤
│ Made with love by ayhug0 on discord                                          │
└──────────────────────────────────────────────────────────────────────────────┘
"""
    print(fade.brazil(menu))

def get_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        print(Fore.CYAN + f"\nLocal IP: {ip}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def get_subnet():
    for adapter in ifaddr.get_adapters():
        for ip_info in adapter.ips:
            ip = ip_info.ip
            if isinstance(ip, str) and ip.startswith(("192.", "10.", "172.")):
                network = ipaddress.IPv4Network(f"{ip}/{ip_info.network_prefix}", strict=False)
                return adapter.nice_name, str(network)
    return None, None

def scan_network():
    try:
        iface, subnet = get_subnet()
        if not subnet or not iface:
            print(Fore.RED + "No valid network interface detected.")
            return
        if not conf.use_pcap:
            print(Fore.RED + "Npcap not configured. Install Scapy in WinPcap mode.")
            return

        MacLookup().update_vendors()
        print(Fore.CYAN + f"\n🔍 Scanning {subnet} via {iface}...\n")
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP()
        live = []

        for ip in ipaddress.IPv4Network(subnet).hosts():
            pkt[ARP].pdst = str(ip)
            ans = srp(pkt, iface=iface, timeout=0.3, verbose=False)[0]
            for _, resp in ans:
                mac = resp.hwsrc
                try:
                    vendor = MacLookup().lookup(mac)
                except VendorNotFoundError:
                    vendor = "Unknown"
                live.append((resp.psrc, mac, vendor))

        if live:
            print(Fore.BLUE + "IP Address       MAC Address          Vendor")
            print(Fore.BLUE + "-" * 55)
            for ip, mac, vendor in live:
                print(Fore.CYAN + f"{ip:<16} {mac:<20} {vendor}")
        else:
            print(Fore.YELLOW + "No active devices found.")
    except Exception as e:
        print(Fore.RED + f"Scan error: {e}")

def port_check():
    try:
        ip = input("Target IP: ")
        port = int(input("Port #: "))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        status = "OPEN" if result == 0 else "CLOSED"
        print(Fore.CYAN + f"\nPort {port} on {ip} is {status}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def reputation_check():
    try:
        ip = input("IP to check: ")
        data = requests.get(f"https://ipapi.co/{ip}/json/").json()
        print(Fore.CYAN + f"\nISP: {data.get('org')}")
        print(f"Location: {data.get('city')}, {data.get('region')}, {data.get('country_name')}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def geolocate_ip():
    try:
        ip = input("IP to locate: ")
        geo = requests.get(f"https://ipapi.co/{ip}/json/").json()
        print(Fore.CYAN + f"\nCity: {geo.get('city')}")
        print(f"Region: {geo.get('region')}")
        print(f"Country: {geo.get('country_name')}")
        print(f"Coordinates: {geo.get('latitude')}, {geo.get('longitude')}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def discord_token_check():
    token = input("🔑 Enter Discord token: ")
    headers = {"Authorization": token}
    try:
        res = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if res.status_code == 200:
            user = res.json()
            print(Fore.GREEN + f"\nValid Token: {user['username']}#{user['discriminator']}")
        else:
            print(Fore.RED + "\nInvalid or expired token.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def ping_device():
    try:
        ip = input("Ping IP: ")
        cmd = f"ping -n 1 {ip}" if os.name == 'nt' else f"ping -c 1 {ip}"
        result = os.system(cmd)
        print(Fore.CYAN + f"\n{ip} is {'Reachable' if result == 0 else 'Unreachable'}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def webhook_inspect():
    url = input("🔗 Enter Discord webhook URL: ")
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            print(Fore.GREEN + f"\nWebhook: {data.get('name')} (ID: {data.get('id')})")
            print(f"Channel: {data.get('channel_id')} | Server: {data.get('guild_id')}")
        else:
            print(Fore.RED + "\nWebhook not found or inactive.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def server_info_fetch():
    token = input("🔑 Enter Discord token: ")
    headers = {"Authorization": token}
    try:
        res = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
        if res.status_code == 200:
            guilds = res.json()
            print(Fore.CYAN + f"\nYou're in {len(guilds)} servers:\n")
            for g in guilds:
                print(Fore.GREEN + f"• {g.get('name')} (ID: {g.get('id')})")
        else:
            print(Fore.RED + "\nInvalid token or fetch failed.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    show_banner()
    show_layout()

    while True:
        try:
            choice = input(Fore.GREEN + "\nChoose tool (1–9) or [x] to exit: ").strip().lower()
            if choice == '1': get_ip()
            elif choice == '2': scan_network()
            elif choice == '3': port_check()
            elif choice == '4': reputation_check()
            elif choice == '5': geolocate_ip()
            elif choice == '6': discord_token_check()
            elif choice == '7': ping_device()
            elif choice == '8': webhook_inspect()
            elif choice == '9': server_info_fetch()
            elif choice == 'x':
                print(Fore.YELLOW + "\nExiting VENAXUM Toolkit. Stay stealthy 🕶️")
                break
            else:
                print(Fore.RED + "Invalid selection.")
        except Exception as e:
            print(Fore.RED + f"\n Error caught: {e}")

        input(Fore.WHITE + "\n↩ Press Enter to return to menu...")
        os.system('cls' if os.name == 'nt' else 'clear')
        show_banner()
        show_layout()
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Fore.RED + f"\nFatal Error: {e}")
    input(Fore.WHITE + "\nPress Enter to fully exit...")
