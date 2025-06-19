BRANDING = "Hyfty" # change this for ez paste / resell
PRINTCLR = "\033[34m" # change this to your brands color
AUTHENTICATED = False # change this to true to skip auth
# NOTE: Keyauth information is down at the bottom near the if __name__

import os
import random
import string
import subprocess
import ctypes
import sys
import time
import urllib.request
import uuid
import hashlib
from ctypes import windll, byref, c_ulong
import binascii
import requests
import json

# constants 
STD_OUTPUT_HANDLE = -11
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

#change colors as needed
CYAN = "\033[96m"
WHITE = "\033[97m"
DIM = "\033[2m"
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"

# DO NOT CHANGE UNLESS YOU KNOW WHAT UR DOING
TEMP_DIR_PATH = r"C:\Windows\InputMethod"
AMI_EXE_URL = "https://raw.githubusercontent.com/creed3900/viywiwyeviweyv/main/AMIDEWINx64.EXE"
AMIFLDRV_URL = "https://raw.githubusercontent.com/creed3900/viywiwyeviweyv/main/amifldrv64.sys"
AMIGENDRV_URL = "https://raw.githubusercontent.com/creed3900/viywiwyeviweyv/main/amigendrv64.sys"
BATCH_FILE_PATH = os.path.join(TEMP_DIR_PATH, f"{BRANDING}_bat.bat")
TASK_NAME = F"{BRANDING}"

# replace with ur brand https://patorjk.com/software/taag/#p=display&h=0&v=0&f=Big&t=Winterz
ASCII = r"""   _                   
 | |  | |      / _| |        
 | |__| |_   _| |_| |_ _   _ 
 |  __  | | | |  _| __| | | |
 | |  | | |_| | | | |_| |_| |
 |_|  |_|\__, |_|  \__|\__, |
          __/ |         __/ |
         |___/         |___/                               
                                                                                             
"""
class KeyAuthAPI:
    def __init__(self, name, ownerid, version, hash_to_check):
        if len(ownerid) != 10:
            print("Invalid ownerid length. Get your correct KeyAuth credentials.")
            time.sleep(3)
            os._exit(1)

        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check

        self.sessionid = ""
        self.initialized = False
        self.init()

    def init(self):
        if self.sessionid != "":
            print("Already initialized.")
            time.sleep(3)
            os._exit(1)

        post_data = {
            "type": "init",
            "ver": self.version,
            "hash": self.hash_to_check,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)
        if response == "KeyAuth_Invalid":
            print("Application doesn't exist.")
            time.sleep(3)
            os._exit(1)

        json_resp = json.loads(response)
        if json_resp["message"] == "invalidver":
            if json_resp.get("download"):
                print("New version available, opening download link...")
                os.system(f"start {json_resp['download']}")
                time.sleep(3)
                os._exit(1)
            else:
                print("Invalid version, contact owner.")
                time.sleep(3)
                os._exit(1)

        if not json_resp["success"]:
            print(json_resp["message"])
            time.sleep(3)
            os._exit(1)

        self.sessionid = json_resp["sessionid"]
        self.initialized = True

    def license(self, key, hwid=None):
        self.__check_init()
        if hwid is None:
            hwid = self.get_hwid()

        post_data = {
            "type": "license",
            "key": key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)
        json_resp = json.loads(response)

        if json_resp["success"]:
           
            # optionally return strings instead of True/ False for better error handling
            return True
        else:
            return False 

    def __do_request(self, post_data):
        try:
            response = requests.post("https://keyauth.win/api/1.3/", data=post_data, timeout=10)
            return response.text
        except Exception as e:
            print(f"Request failed: {e}")
            time.sleep(3)
            os._exit(1)

    def __check_init(self):
        if not self.initialized:
            print("Call init() before using this function.")
            time.sleep(3)
            os._exit(1)

    @staticmethod
    def get_hwid():
        # Basic HWID retrieval, replace or expand for your needs
        import platform
        return platform.node()
    
# TODO: add string encryption
# TODO: add antidebug probably gonna be pyprotect or WinterzProtLib

def getchecksum():
    file_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return None
    

# --- Utility functions ---

def enable_vt_mode():
    hOut = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    mode = c_ulong()
    windll.kernel32.GetConsoleMode(hOut, byref(mode))
    mode = c_ulong(mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    windll.kernel32.SetConsoleMode(hOut, mode)

def set_window_title(title): # better and more permanant version of os.system("title {wtv}") because its thru windows directly
    ctypes.windll.kernel32.SetConsoleTitleW(title) #can also add custom chars like | or !
    
def generate_random_string(length=15, lowercase = False):
    chars = string.ascii_uppercase + string.digits 
    if lowercase: chars += string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(length)) # good but can be better

def greenblue(text):
    faded = ""
    blue = 100
    for line in text.splitlines():
        faded += (f"\033[38;2;0;255;{PRINTCLR}{line}\033[0m\n")
        if not blue == 255:
            blue += 15
            if blue > 255:
                blue = 255
    return faded

def print_ascii():
    print(greenblue(ASCII))

def fade_print(text, delay=0.05):
    print(f"{PRINTCLR}[{BRANDING}]{RESET} ", end="")
    for char in text:
        print(f"{char}", end="", flush=True)
        time.sleep(delay)
    print()

def generate_random_uuid():
    return str(uuid.uuid4()).replace('-', '').upper()

def wmic_read_serial(name):
    """Attempt* to read serial using WMIC for given component name."""
    try:
        if name == "BIOS Serial":
            cmd = ["wmic", "bios", "get", "serialnumber"]
        elif name == "BaseBoard Serial":
            cmd = ["wmic", "baseboard", "get", "serialnumber"]
        elif name == "Chassis Serial":
            cmd = ["wmic", "chassis", "get", "serialnumber"]
        elif name == "Processor Serial":
            cmd = ["wmic", "cpu", "get", "ProcessorId"]
        elif name == "System Serial":
            cmd = ["wmic", "computersystem", "get", "serialnumber"]
        else:
            return "UNKNOWN"

        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        lines = output.strip().splitlines()
        if len(lines) >= 2:
            real_val = lines[1].strip()
        else:
            real_val = "UNKNOWN"
    except Exception:
        real_val = "UNKNOWN"
    return real_val
def generate_intel():
    # Intel format: BX + 5-digit code + model suffix (e.g., 12700K, 13600KF)
    
    base_prefix = "BX"
    cpu_ids = [
        "80715", "80716", "80717", "80718", "80719",
        "80684", "80693", "80695", "80697", "80808"
    ]

    models = [
        "12400F", "12600K", "12700K", "12900KF",
        "13400F", "13600K", "13700K", "13900KS",
        "14400F", "14600K", "14700KF", "14900K"
    ]

    cpu_id = random.choice(cpu_ids)
    model = random.choice(models)

    return f"{base_prefix}{cpu_id}{model}"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def task_exists(task_name):
    cmd = ['schtasks', '/Query', '/TN', task_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def create_scheduled_task(task_name, batch_path):
    cmd = [
        "schtasks", "/Create", "/SC", "ONSTART", "/RL", "HIGHEST",
        "/TN", task_name, "/TR", f'"{batch_path}"', "/F"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Scheduled task created successfully.")
    else:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Failed to create scheduled task:\n{result.stderr}")
        sys.exit(1)

def delete_scheduled_task(task_name):
    cmd = ["schtasks", "/Delete", "/TN", task_name, "/F"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Scheduled task deleted successfully.")
    else:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Failed to delete scheduled task:\n{result.stderr}")
        sys.exit(1)

def download_file(url, dest):
    try:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Downloading File...")
        urllib.request.urlretrieve(url, dest)
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Download complete.")
    except Exception as e:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Download error: {e}")
        sys.exit(1)

def create_batch_file(uuid_val, SS, CS, BS, PSN, PAT, PPN):
    lines = [
        "@echo off",
        "setlocal EnableDelayedExpansion",
        "pushd %~dp0",
        "title Winterz bouta touch ur dih",
        f'AMIDEWINx64.EXE /SU {uuid_val} >nul 2>&1',
        f'AMIDEWINx64.EXE /SS {SS} >nul 2>&1',
        f'AMIDEWINx64.EXE /CS {CS} >nul 2>&1',
        f'AMIDEWINx64.EXE /BS {BS} >nul 2>&1',
        f'AMIDEWINx64.EXE /PSN {PSN} >nul 2>&1',
        f'AMIDEWINx64.EXE /PAT {PAT} >nul 2>&1',
        f'AMIDEWINx64.EXE /PPN {PPN} >nul 2>&1',
        'AMIDEWINx64.EXE /CSK "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /CM "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /SK "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /SF "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /BT "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /BLC "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /CSK "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /CA "Default string" >nul 2>&1',
        "exit"
    ]
    os.makedirs(TEMP_DIR_PATH, exist_ok=True)
    with open(BATCH_FILE_PATH, "w") as f:
        f.write("\r\n".join(lines))
    print(f"{PRINTCLR}[{BRANDING}]{RESET} Successfully initilized task!")




def spoof_random_serials(asus_mode = False):
    if not is_admin():
        print(f"{PRINTCLR}[{BRANDING}]{RESET} ERROR: Administrator privileges required for ASUS spoof.")
        return

    serial_names = [
        "BIOS Serial",
        "BaseBoard Serial",
        "Chassis Serial",
        "Processor Serial",
        "System Serial",
    ]

    old_serials = {}
    new_serials = {}

    #  uses wmic -> not the best way to do it but i cant really change for all support
    for name in serial_names:
        old_val = wmic_read_serial(name)
        old_serials[name] = old_val
        new_serials[name] = generate_random_string(15)

    # spoofing preview
    print()
    for name in serial_names:
        print(f"{PRINTCLR}[{BRANDING}]{RESET} {name} OLD: {DIM}{old_serials[name]}{RESET} -> NEW: {PRINTCLR}{new_serials[name]}{RESET}")
    print()

    uuid_val = new_serials["BIOS Serial"]
    BS = new_serials["BaseBoard Serial"]
    SS = new_serials["System Serial"]
    CS = new_serials["Chassis Serial"]
    PSN = new_serials["Processor Serial"]
    PAT = "CPU-INTEL-WINTERZ" 
    PPN = generate_intel() # this is the model not the serial 

    # will eventually add amd but rn serials will say intel no matter what? (i have an amd processer but intel serials work js fine EDIT: at least for fn)
    
    """
    BIOS Serial (uuid_val) — a UUID 

    BaseBoard Serial (BS) — usually an alphanumeric string; 15 chars random is fine.

    System Serial (SS) — same as above.

    Chassis Serial (CS) — usually alphanumeric, 15 random chars is good.

    Processor Serial (PSN) — depends on CPU, but again, random 15 chars should be accepted.

    PAT (Platform/Manufacturer string) —  hardcoded this, which is fine.

    PPN (Processor model) — good to be realistic; this generates semi realistic serials, would also prefer the PAT to be the right brand
    
    """

    # download shit
    download_file(AMI_EXE_URL, os.path.join(TEMP_DIR_PATH, "AMIDEWINx64.EXE"))
    download_file(AMIFLDRV_URL, os.path.join(TEMP_DIR_PATH, "amifldrv64.sys"))
    download_file(AMIGENDRV_URL, os.path.join(TEMP_DIR_PATH, "amigendrv64.sys"))

    # we dont need to create a task here because it autosaves serials :3
    
    if not asus_mode:
        commands = [  
        f'AMIDEWINx64.EXE /SU {uuid_val} >nul 2>&1',
        f'AMIDEWINx64.EXE /SS {SS} >nul 2>&1',
        f'AMIDEWINx64.EXE /CS {CS} >nul 2>&1',
        f'AMIDEWINx64.EXE /BS {BS} >nul 2>&1',
        f'AMIDEWINx64.EXE /PSN {PSN} >nul 2>&1',
        f'AMIDEWINx64.EXE /PAT {PAT} >nul 2>&1',
        f'AMIDEWINx64.EXE /PPN {PPN} >nul 2>&1',
        'AMIDEWINx64.EXE /CSK "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /CM "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /SK "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /SF "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /BT "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /BLC "Default string" >nul 2>&1',
        'AMIDEWINx64.EXE /CA "Default string" >nul 2>&1',
        ] # same as the bat file but we dont need to make a bat file for ts
        for cmd in commands:
            os.system(cmd)
        print(f"{PRINTCLR}[{BRANDING}]{RESET} Random spoofing complete.\n")

    else: 
        create_batch_file(uuid_val, SS, CS, BS, PSN, PAT, PPN)

        # the reason we create a task is to spoof on boot eventually ill make it seeded with the seed stored in a file so you get same serials every time

        if task_exists(TASK_NAME): 
            print(f"{PRINTCLR}[{BRANDING}]{RESET} ASUS spoof task already exists. Please contact support if your serials arent changing!")
            print(f"{PRINTCLR}[{BRANDING}]{RESET} Would you like to manually overwrite the task anyways? {RED}y{RESET}/{GREEN}n")
        else:
            create_scheduled_task(TASK_NAME, BATCH_FILE_PATH)

        print(f"{PRINTCLR}[{BRANDING}]{RESET} ASUS Spoof setup complete. Please restart your PC and verify serials.")

    
WinterzAuth = KeyAuthAPI(
    name = "ImHyfty's Application", 
    ownerid = "NUuHY0X3Li",
    version = "1.0", 
    hash_to_check = getchecksum()
)

def main_menu():
    global AUTHENTICATED
    while not AUTHENTICATED:
        os.system("cls")
        print_ascii()
        fade_print(f"Welcome to Hyfty Spoofer\n")
        fade_print(f"Please enter your key!\n")
        key = input(">")
        status = WinterzAuth.license(key)
        if status: AUTHENTICATED = True
        else: print(f"{RED}[{BRANDING}]{RESET} Invalid license key{RESET}")
        os.system("pause")
    print("{PRINTCLR}[{BRANDING}]{RESET} Successfully authenticated. Welcome to {BRANDING} Perm!{RESET}")
    while True:
        os.system("cls")
        
        print_ascii()
        time.sleep(0.1)
        print(f"{PRINTCLR}Choose an option:{RESET}")
        print(f"  {PRINTCLR}1{RESET}. Spoof all serials")
        print(f"  {PRINTCLR}2{RESET}. ASUS Spoof Mode")
        print(f"  {PRINTCLR}4{RESET}. Exit\n")

        choice = input(f"{PRINTCLR}[{BRANDING}]{RESET} Enter choice: ").strip()

        if choice == "1":
            spoof_random_serials()
    
        elif choice == "2":
            spoof_random_serials(asus_mode=True)
        elif choice == "4":
            fade_print("Exiting! Goodbye!")
            break
        else:
            fade_print("Invalid choice, try again.")



if __name__ == "__main__":
    os.system("cls")
    enable_vt_mode()
    
    set_window_title(f"{BRANDING} Perm | Coded by 1337tuno -_- | {generate_random_string(15, True)}")

    main_menu()
