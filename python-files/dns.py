import requests
import subprocess
import platform
import os
import shlex

DOH_SERVERS = {
    '1': ('Cloudflare', 'https://cloudflare-dns.com/dns-query'),
    '2': ('AdGuard', 'https://dns.adguard.com/dns-query'),
    '3': ('OpenDNS', 'https://dns.opendns.com/dns-query'),
}

DNS_IPS = {
    'Cloudflare': ['1.1.1.1', '1.0.0.1'],
    'AdGuard': ['94.140.14.14', '94.140.15.15'],
    'OpenDNS': ['208.67.222.222', '208.67.220.220']
}

def clear_console():
    os.system("cls" if platform.system() == "Windows" else "clear")

def get_system_dns():
    try:
        result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
        dns_servers = []
        collect = False
        for line in result.stdout.splitlines():
            if "DNS Servers" in line:
                collect = True
                dns_servers.append(line.split(":")[1].strip())
            elif collect and line.strip():
                dns_servers.append(line.strip())
            elif collect and not line.strip():
                collect = False
        return dns_servers
    except Exception as e:
        return [f"Error retrieving DNS: {e}"]

def query_doh(domain, server_name, server_url):
    print(f"\nQuerying '{domain}' using {server_name} DoH ({server_url})")
    payload = {"name": domain, "type": "A"}
    try:
        response = requests.get(server_url, params=payload, headers={'Accept': 'application/dns-json'})
        if response.status_code == 200:
            data = response.json()
            if "Answer" in data:
                for ans in data["Answer"]:
                    if ans["type"] == 1:
                        print(f"Resolved IP: {ans['data']}")
            else:
                print("No records found.")
        else:
            print(f"Query failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error querying DNS: {e}")

def get_connected_adapters():
    try:
        result = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()[3:]
        adapters = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 4 and parts[1] == "Connected":
                adapter_name = " ".join(parts[3:])
                adapters.append(adapter_name)
        return adapters
    except Exception as e:
        print(f"Error getting adapters: {e}")
        return []

def set_windows_dns(dns_ips):
    print(f"\nApplying DNS: {dns_ips}")
    try:
        adapters = get_connected_adapters()
        for adapter in adapters:
            quoted_adapter = f'"{adapter}"' if ' ' in adapter else adapter
            subprocess.run(['netsh', 'interface', 'ip', 'set', 'dns', quoted_adapter, 'static', dns_ips[0]], check=True)
            if len(dns_ips) > 1:
                subprocess.run(['netsh', 'interface', 'ip', 'add', 'dns', quoted_adapter, dns_ips[1], 'index=2'], check=True)
        print("DNS successfully set.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to apply DNS:\n{e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def reset_dns_to_auto():
    print("\nResetting all adapters to automatic DNS...")
    try:
        adapters = get_connected_adapters()
        for adapter in adapters:
            quoted_adapter = f'"{adapter}"' if ' ' in adapter else adapter
            subprocess.run(['netsh', 'interface', 'ip', 'set', 'dns', quoted_adapter, 'dhcp'], check=True)
        print("DNS reset to automatic.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reset DNS:\n{e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    while True:
        clear_console()
        print("=== DNS Manager for Windows ===")
        print("1. Set Cloudflare DNS")
        print("2. Set AdGuard DNS")
        print("3. Set OpenDNS DNS")
        print("4. Show current system DNS")
        print("5. Reset DNS to automatic")
        print("6. Query domain (using Cloudflare)")
        print("0. Exit")
        choice = input("\nSelect an option: ").strip()

        clear_console()

        if choice in DOH_SERVERS:
            name, url = DOH_SERVERS[choice]
            set_windows_dns(DNS_IPS[name])
        elif choice == '4':
            print("Current System DNS:")
            for dns in get_system_dns():
                print(f" - {dns}")
        elif choice == '5':
            reset_dns_to_auto()
        elif choice == '6':
            domain = input("Enter domain to resolve (e.g., example.com): ").strip()
            clear_console()
            query_doh(domain, "Cloudflare", DOH_SERVERS['1'][1])
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

        input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    main()
