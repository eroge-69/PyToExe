import os
import subprocess
import re
import winreg
import time

def set_title(title):
    os.system(f"title {title}")

set_title("Temp Spoofer Real Only")

log_file = "spoof_log.txt"

def log_event(event):
    with open(log_file, "a") as f:
        f.write(f"{time.ctime()}: {event}\n")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_network_adapters():
    key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    adapters = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        name = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                        net_cfg = winreg.QueryValueEx(subkey, "NetCfgInstanceId")[0]
                        adapters[net_cfg] = (subkey_name, name)
                    except FileNotFoundError:
                        continue
    except PermissionError:
        return None
    return adapters

def set_mac_address(adapter_subkey, mac):
    key_path = fr"SYSTEM\CurrentControlSet\Control\Class\{{4d36e972-e325-11ce-bfc1-08002be10318}}\{adapter_subkey}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, mac)
        log_event(f"MAC address set to {mac} in registry.")
        return True
    except PermissionError:
        return False

def restart_adapter(adapter_name):
    subprocess.run(f'netsh interface set interface name="{adapter_name}" admin=disable', shell=True)
    subprocess.run(f'netsh interface set interface name="{adapter_name}" admin=enable', shell=True)
    log_event(f"Adapter {adapter_name} restarted.")

def change_hostname(new_hostname):
    try:
        subprocess.check_call(f'wmic computersystem where name="%COMPUTERNAME%" call rename name="{new_hostname}"', shell=True)
        log_event(f"Hostname changed to {new_hostname}")
    except subprocess.CalledProcessError:
        print("Failed to change hostname. Run as Administrator.")

def change_ip(adapter_name, new_ip, subnet_mask="255.255.255.0", gateway=""):
    try:
        subprocess.check_call(f'netsh interface ip set address name="{adapter_name}" static {new_ip} {subnet_mask} {gateway}', shell=True)
        log_event(f"IP address for {adapter_name} set to {new_ip}")
    except subprocess.CalledProcessError:
        print("Failed to change IP address. Run as Administrator.")

def temp_spoof_mac_real():
    adapters = get_network_adapters()
    if adapters is None:
        print("Need to run as Administrator to spoof MAC.")
        return

    print("Available network adapters:")
    for i, (guid, (subkey, name)) in enumerate(adapters.items(), 1):
        print(f"{i}: {name} ({guid})")

    choice = input("Select adapter by number: ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(adapters):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return

    selected_guid = list(adapters.keys())[choice - 1]
    subkey, name = adapters[selected_guid]

    mac = input("Enter new MAC address (12 hex digits, no separators): ")
    if not len(mac) == 12 or any(c not in "0123456789ABCDEFabcdef" for c in mac):
        print("Invalid MAC format.")
        return
    mac = mac.upper()

    success = set_mac_address(subkey, mac)
    if not success:
        print("Failed to set MAC address. Run script as Administrator.")
        return

    restart_adapter(name)
    print("MAC address spoofed successfully.")

def temp_spoof_hostname():
    new_hostname = input("Enter new hostname: ")
    if not new_hostname:
        print("Hostname cannot be empty.")
        return
    change_hostname(new_hostname)
    print("Hostname changed.")

def temp_spoof_ip():
    adapters = get_network_adapters()
    if adapters is None:
        print("Need to run as Administrator to change IP.")
        return

    print("Available network adapters:")
    for i, (guid, (subkey, name)) in enumerate(adapters.items(), 1):
        print(f"{i}: {name} ({guid})")

    choice = input("Select adapter by number: ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(adapters):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return

    new_ip = input("Enter new IP address (e.g. 192.168.1.100): ")
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', new_ip):
        print("Invalid IP format.")
        return

    subkey, name = list(adapters.values())[choice - 1]
    change_ip(name, new_ip)
    print("IP address changed.")

def show_menu():
    print("1: Spoof MAC address (real)")
    print("2: Spoof hostname (real)")
    print("3: Spoof IP address (real)")
    print("4: Exit")

def main():
    while True:
        clear_screen()
        show_menu()
        choice = input("Choose an option: ")
        if choice == "1":
            temp_spoof_mac_real()
        elif choice == "2":
            temp_spoof_hostname()
        elif choice == "3":
            temp_spoof_ip()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option.")
        input("Press Enter to continue...")

if __name__ == "__main__":
    if os.name != 'nt':
        print("Warning: Real spoofing only works on Windows.")
    main()
