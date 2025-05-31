"""
SPOOFER Checker | Is your computer spoofed?

This script:

1) Ensures it's running as Admin (UAC prompt if needed).
2) Checks for required modules (wmi, colorama). If missing, offers to install them.
3) Gathers & compares system hardware info (BIOS, Baseboard, Disks, NIC, RAM, PSU).
4) Shows if system has been "SPOOFED" or "NOT SPOOFED" based on changed hardware data.
"""

import sys
import os
import subprocess
import json
import ctypes
from ctypes import wintypes

# List of required 3rd party modules:
REQUIRED_MODULES = ["wmi", "colorama"]

# We'll do a quick is_admin check using ctypes
def is_admin():
    """
    Return True if script is running with admin privileges, otherwise False.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    """
    Relaunches the current script with Administrator privileges via ShellExecute.
    Exits the current (non-admin) process afterward.
    """
    # Re-run the script with admin rights
    params = " ".join(f'"{x}"' for x in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}" {params}', None, 1)
    sys.exit(0)

def check_required_modules():
    """
    Checks if the required modules are installed. Returns a list of missing modules.
    We import them inside a try/except to handle if they're missing.
    """
    missing = []
    for mod in REQUIRED_MODULES:
        try:
            __import__(mod)  # simple attempt to import
        except ImportError:
            missing.append(mod)
    return missing

def install_modules(modules):
    """
    Attempts to install the given list of modules using pip.
    After installation, the script will relaunch itself.
    """
    # Try pip or python -m pip
    for mod in modules:
        print(f"Attempting to install module: {mod}")
        try:
            # You can also do [sys.executable, "-m", "pip", "install", mod]
            # We use shell=True to simplify on Windows; adjust as needed.
            install_command = [sys.executable, "-m", "pip", "install", mod]
            subprocess.check_call(install_command)
        except Exception as e:
            print(f"Failed to install {mod}: {e}")
            print("Please install it manually or fix your Python/pip configuration.")
            sys.exit(1)

    # Re-run the script after installing
    print("Installation complete. Relaunching script...")
    run_as_admin()

# ===============================
#   MAIN HARDWARE SCRIPT LOGIC
# ===============================

# If we've gotten here, modules should be installed. Now we can import them safely
# (or after installing them dynamically).
import uuid
try:
    import wmi
except ImportError:
    print("Unexpected: wmi import failed after we thought it was installed.")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
except ImportError:
    print("Unexpected: colorama import failed after we thought it was installed.")
    sys.exit(1)

# Initialize colorama
init(autoreset=True)

HARDWARE_INFO_FILE = "hardware_info.txt"

def gather_hardware_info():
    """
    Gathers the hardware information from the local machine via WMI
    and returns it as a structured dictionary.
    """
    c = wmi.WMI()

    # =========================
    #  System BIOS/Baseboard
    # =========================
    system_bios_baseboard = {}

    # BIOS info
    try:
        for bios in c.Win32_BIOS():
            system_bios_baseboard["BIOS Serial"] = getattr(bios, 'SerialNumber', 'N/A') or "N/A"
            break
    except:
        system_bios_baseboard["BIOS Serial"] = "N/A"

    # ComputerSystemProduct for UUID
    try:
        for sysprod in c.Win32_ComputerSystemProduct():
            system_bios_baseboard["BIOS UUID"] = getattr(sysprod, 'UUID', 'N/A') or "N/A"
            break
    except:
        system_bios_baseboard["BIOS UUID"] = "N/A"

    # Baseboard info
    try:
        for baseboard in c.Win32_BaseBoard():
            system_bios_baseboard["Baseboard Serial"] = getattr(baseboard, 'SerialNumber', 'N/A') or "N/A"
            break
    except:
        system_bios_baseboard["Baseboard Serial"] = "N/A"

    # =========================
    #  Disks (HDD/SSD/NVMe)
    # =========================
    disks = []
    try:
        for disk in c.Win32_DiskDrive():
            name = getattr(disk, 'Model', 'N/A')
            serial = getattr(disk, 'SerialNumber', 'N/A')
            if serial:
                serial = serial.strip()
            else:
                serial = "N/A"
            disk_info = {
                "Name": name,
                "SerialNumber": serial
            }
            disks.append(disk_info)
    except:
        pass

    # =========================
    #  Network Adapter (NIC)
    # =========================
    network_adapter = {}
    try:
        for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            network_adapter["NIC Name"] = getattr(nic, 'Description', 'N/A') or "N/A"
            current_mac = getattr(nic, 'MACAddress', 'N/A') or "N/A"
            network_adapter["Current MAC Address"] = current_mac
            network_adapter["Permanent MAC Address"] = get_permanent_mac(nic.Index) or current_mac
            break
    except:
        network_adapter["NIC Name"] = "N/A"
        network_adapter["Current MAC Address"] = "N/A"
        network_adapter["Permanent MAC Address"] = "N/A"

    # =========================
    #  Random Access Memory (RAM) Sticks
    # =========================
    ram_sticks = []
    try:
        for mem in c.Win32_PhysicalMemory():
            manufacturer = getattr(mem, 'Manufacturer', 'N/A') or "N/A"
            serial_number = getattr(mem, 'SerialNumber', 'N/A')
            asset_tag = getattr(mem, 'AssetTag', 'N/A')

            if serial_number:
                serial_number = serial_number.strip()
            else:
                serial_number = "N/A"

            if asset_tag:
                asset_tag = asset_tag.strip()
            else:
                asset_tag = "N/A"

            ram_info = {
                "Manufacturer": manufacturer,
                "SerialNumber": serial_number,
                "AssetTag": asset_tag
            }
            ram_sticks.append(ram_info)
    except:
        pass

    # =========================
    #  Power Supply
    # =========================
    power_supply = {}
    power_supply["Power Supply Serial"] = get_power_supply_serial(c)

    hardware_info = {
        "System BIOS/Baseboard": system_bios_baseboard,
        "Disks": disks,
        "Network Adapter (NIC)": network_adapter,
        "Random Access Memory (RAM) Sticks": ram_sticks,
        "Power Supply": power_supply
    }

    return hardware_info

def get_permanent_mac(nic_index):
    """
    Attempt to get the 'permanent' MAC address from Win32_NetworkAdapter.
    Often, 'MACAddress' is the only one available, but some drivers store
    'PermanentAddress' or 'NetworkAddress'.
    """
    c = wmi.WMI()
    try:
        for adapter in c.Win32_NetworkAdapter():
            if adapter.Index == nic_index:
                return getattr(adapter, "PermanentAddress", None)
    except:
        pass
    return None

def get_power_supply_serial(wmi_conn):
    """
    Attempts to fetch the power supply serial from WMI.
    Many systems do not expose PSU details. Returns "N/A" by default.
    """
    return "N/A"

def save_hardware_info(data, filename=HARDWARE_INFO_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_hardware_info(filename=HARDWARE_INFO_FILE):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def compare_hardware_info(old_info, new_info):
    """
    Compare old_info and new_info dictionaries.
    Return True if they match exactly, or False otherwise.
    """
    if set(old_info.keys()) != set(new_info.keys()):
        return False

    for category in old_info:
        old_val = old_info[category]
        new_val = new_info[category]

        if isinstance(old_val, dict) and isinstance(new_val, dict):
            if not compare_dicts(old_val, new_val):
                return False
        elif isinstance(old_val, list) and isinstance(new_val, list):
            if len(old_val) != len(new_val):
                return False
            for i in range(len(old_val)):
                if not compare_dicts(old_val[i], new_val[i]):
                    return False
        else:
            if old_val != new_val:
                return False

    return True

def compare_dicts(d1, d2):
    """
    Compare two dictionaries key-by-key for exact match of values.
    """
    if set(d1.keys()) != set(d2.keys()):
        return False
    for k in d1:
        if d1[k] != d2[k]:
            return False
    return True

def print_colored(text, color):
    print(color + text + Style.RESET_ALL)

def print_hardware_info(hardware_info):
    for category, details in hardware_info.items():
        print(Style.BRIGHT + Fore.CYAN + "===========================================")
        print(category)
        print("===========================================" + Style.RESET_ALL)
        
        if isinstance(details, dict):
            for k, v in details.items():
                print(f"{k:25}: {v}")
        elif isinstance(details, list):
            for idx, item in enumerate(details, start=1):
                print(Fore.MAGENTA + f"[Item {idx}]")
                for k, v in item.items():
                    print(f"  {k:23}: {v}")
                print()
        else:
            print(details)
        print()

def main_script():
    """
    The main logic that gathers, saves or compares hardware info.
    This is separated so we can call it after ensuring admin + modules.
    """
    print("SPOOFER Checker | Is your computer spoofed?\n\n")

    if not os.path.exists(HARDWARE_INFO_FILE):
        # First run: gather info, save, prompt user to run again
        hw_info = gather_hardware_info()
        save_hardware_info(hw_info)
        print("\nHardware information collected and saved.")
        print("Run this script again to check if system values have changed.\n")
        input("Press ENTER to exit.")
    else:
        # Subsequent run: load old info, gather new, compare
        old_info = load_hardware_info()
        new_info = gather_hardware_info()

        # Print the current hardware info
        print_hardware_info(new_info)
        print()

        if compare_hardware_info(old_info, new_info):
            # Not spoofed
            print_colored(">>>> WARNING:  NOT SPOOFED <<<<", Fore.RED)
        else:
            # Spoofed
            print_colored(">>>> SPOOFED | YOU ARE READY <<<<", Fore.GREEN)

        print()
        print_colored("Press ENTER to exit...", Fore.YELLOW)
        input()

def main():
    # 1) Check if we are admin
    if not is_admin():
        run_as_admin()

    # 2) Check required modules
    missing_modules = check_required_modules()
    if missing_modules:
        # Print message in bright red
        print_colored("\nThe following required modules are missing:\n", Fore.RED)
        for m in missing_modules:
            print_colored(f" - {m}", Fore.RED)

        print_colored("\nWould you like to install them now? (Y/N)", Fore.RED)
        choice = input(">>> ").strip().lower()
        if choice == "y":
            install_modules(missing_modules)
            # install_modules() will re-run the script after installing
        else:
            print_colored("Cannot continue without required modules. Exiting.", Fore.RED)
            sys.exit(1)

    # If we reach here, we have admin privileges & all modules installed
    main_script()

if __name__ == "__main__":
    main()
