import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import datetime
import requests
import time
import tempfile
from colorama import init, Fore, Style
init()
import random
import string
import winreg
import subprocess
import ctypes
import shutil
import psutil
import glob

from Crypto.Cipher import AES

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        print(Fore.RED + "[ERROR] Administrator privileges required!")
        print(Fore.RED + "[ERROR] Please run this program as Administrator!")
        print(Fore.RED + "[ERROR] Program will close in 3 seconds...")
        time.sleep(3)
        sys.exit(1)

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
temp_folder = tempfile.gettempdir()


def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"
        
def banner():
    os.system("cls")
    print(Fore.RED + """
███    ███  ██████  ██      ████████  █████  ███████ ███████ ████████ 
████  ████ ██    ██ ██         ██    ██   ██ ██      ██         ██    
██ ████ ██ ██    ██ ██         ██    ███████ █████   █████      ██    
██  ██  ██ ██    ██ ██         ██    ██   ██ ██      ██         ██    
██      ██  ██████  ███████    ██    ██   ██ ██      ███████    ██   

                                                                     discord.gg/k6xYPbKkB2                                                                    
    """)

def random_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".dat"
    
def random_foldername():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))



def get_mta_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Multi Theft Auto: San Andreas All\1.6")
        value, _ = winreg.QueryValueEx(key, "Last Run Path")
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None

        
def chekUpdated():
    url = "https://rozup.ir/download/4099026/moltafetinjin.txt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            return response.text.strip() == "ok"
        return False
    except requests.RequestException:
        return False
        
def getCheatData():
    current_dir = os.getcwd()
    dll_pattern = os.path.join(current_dir, "Moltafet.dll")
    
    if os.path.exists(dll_pattern):
        return dll_pattern
    
    for root, dirs, files in os.walk(current_dir):
        if "Moltafet.dll" in files:
            return os.path.join(root, "Moltafet.dll")
    
    return None

def set_autodialdll(dll_path):
    try:
        alternative_path = dll_path
        alternative_path = r"C:\Windows\System32\rasadhlp.dll"
        
        if os.path.exists(dll_path):
            shutil.copy2(dll_path, alternative_path)
            
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SYSTEM\ControlSet001\Services\WinSock2\Parameters", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AutodialDLL", 0, winreg.REG_SZ, alternative_path)
            winreg.CloseKey(key)
            return True
    except Exception as e:
        print(f"[ERROR] set_autodialdll failed: {e}")
        return False


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

if __name__ == "__main__":
    run_as_admin()
    banner()
    
    local_dll_path = getCheatData()
    print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Checking updates...")
    if not chekUpdated():
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Update Failed ! Download new version : discord.gg/owwl")
        time.sleep(3)
        sys.exit(0)

    if not local_dll_path:
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Senior.dll not found in current folder or subfolders!")
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Please place Senior.dll in the same folder as this loader")
        time.sleep(3)
        sys.exit(1)
    
    print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + f"Senior.dll was successfully found.")
    
    mta_path = get_mta_path()
    if not mta_path:
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "MTA path not found!")
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Make sure MTA:SA is installed!")
        time.sleep(3)
        sys.exit(1)
    
    print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + f"MTA found at: {mta_path}")
    
    if set_autodialdll(local_dll_path):
        print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Opening MTA:SA...")
        try:
            subprocess.Popen(mta_path)
            print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Waiting for game to start...")
            wait_and_set_autodialdll()
            print("                                       " + Fore.RED + "[SUCCESS] " + Fore.WHITE + "Injection completed successfully!")
            print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "You can close this window now.")
            sys.exit(0)
        except Exception as e:
            print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + f"Failed to start MTA: {e}")
            time.sleep(3)
            sys.exit(0)
    else:
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Injection failed!")
        time.sleep(3)
        sys.exit(0)