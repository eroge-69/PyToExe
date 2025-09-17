"""
MAC Changer for Windows 11
Author: Eakub Ali Polash
Email: eakubalipolash@gmail.com
Version: 25.09.11
Description: Run this Script with Administration Privileged, to change MAC Address of any Network Adapter.
"""
__author__ = "Eakub Ali Polash"
__email__ = "eakubalipolash@gmail.com"
__version__ = "25.09.11"

import subprocess
import winreg
import ctypes
import random
import time


def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_adapters():
    """List network adapters with registry paths."""
    adapters = []
    reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            for i in range(1000):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            name, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                            net_cfg_instance_id, _ = winreg.QueryValueEx(
                                subkey, "NetCfgInstanceId")
                            adapters.append({
                                "name": name,
                                "reg_path": f"{reg_path}\\{subkey_name}",
                                "id": net_cfg_instance_id
                            })
                        except FileNotFoundError:
                            continue
                except OSError:
                    break
    except Exception as e:
        print("Error accessing registry:", e)
    return adapters


def generate_mac():
    """Generate a random MAC address with a unicast, locally administered address."""
    mac = [0x02, 0x00, 0x00,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ''.join(f"{b:02X}" for b in mac)


def set_mac(reg_path, new_mac):
    """Write new MAC to registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
        return True
    except Exception as e:
        print(f"Failed to set MAC: {e}")
        return False


def disable_adapter(adapter_id):
    subprocess.run(
        f"wmic path win32_networkadapter where guid='{adapter_id}' call disable", shell=True)


def enable_adapter(adapter_id):
    subprocess.run(
        f"wmic path win32_networkadapter where guid='{adapter_id}' call enable", shell=True)


def change_mac(adapter):
    print(f"\nChanging MAC for: {adapter['name']}")
    new_mac = generate_mac()
    print(f"Generated new MAC: {new_mac}")

    print("Disabling adapter...")
    disable_adapter(adapter["id"])
    time.sleep(2)

    if set_mac(adapter["reg_path"], new_mac):
        print("MAC address set in registry.")
    else:
        print("Failed to update registry.")
        return

    print("Enabling adapter...")
    enable_adapter(adapter["id"])
    time.sleep(3)
    print(f"MAC address for {adapter['name']} changed to {new_mac}")


def main():
    if not is_admin():
        print("Please run this script as Administrator.")
        return

    adapters = get_adapters()
    if not adapters:
        print("No network adapters found.")
        return

    print("Available network adapters:")
    for idx, adapter in enumerate(adapters):
        print(f"{idx}: {adapter['name']}")

    try:
        choice = int(input("Select adapter index to change MAC: "))
        if 0 <= choice < len(adapters):
            change_mac(adapters[choice])
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


if __name__ == "__main__":
    main()
