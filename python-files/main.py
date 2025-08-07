import os
from pystyle import *
import tls_client, requests
import ctypes
import random
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style
import time
from pymongo import MongoClient
import hashlib
import uuid
import json
import sys

MONGO_URI = "mongodb+srv://iblamerex:Rexisop_1@rex.zqbyv.mongodb.net/?retryWrites=true&w=majority&appName=rex"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['KeyManager']
keys_collection = db['keys']

def getCurrentTime():
    return datetime.now().strftime("%H:%M:%S")

def get_hwid():
    hwid = str(uuid.getnode())
    return hashlib.sha256(hwid.encode()).hexdigest()

def validate_key(key, show_details=True):
    """Enhanced key validation with HWID management and PENDING status handling"""
    key_data = keys_collection.find_one({"key": key, "category": "TOKEN-PASS-CHANGER"})
    
    if not key_data:
        return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Invalid key!') + Fore.RESET

    if key_data["revoked"]:
        return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Key has been revoked') + Fore.RESET
    
    current_hwid = get_hwid()
    current_hwids = key_data.get("hwids", [])
    max_users = key_data.get("max_users", 1)
    
    if key_data["status"] == "PENDING":
        if len(current_hwids) < max_users:
            now = datetime.now(timezone.utc)
            expiry = now + timedelta(days=key_data["days_duration"])
            
            if current_hwid not in current_hwids:
                current_hwids.append(current_hwid)

            keys_collection.update_one(
                {"key": key},
                {
                    "$set": {
                        "status": "ACTIVE",
                        "activated_at": now,
                        "expiry": expiry,
                        "hwids": current_hwids 
                    }
                }
            )
            return True, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, '✓ Key activated successfully') + Fore.RESET
        else:
            return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, f'✗ Maximum users reached ({max_users}/{max_users}) for this PENDING key. Cannot activate.') + Fore.RESET
    
    
    elif key_data["status"] == "ACTIVE":
        expiry = key_data["expiry"]
        if expiry is not None:
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            
            if datetime.now(timezone.utc) > expiry:
                keys_collection.update_one({"key": key}, {"$set": {"status": "INACTIVE"}})
                return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Key has expired') + Fore.RESET
        
        if key_data.get("ip_lock"):
            try:
                current_ip = requests.get("https://api.ipify.org").text
                if current_ip != key_data["ip_lock"]:
                    return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ IP address mismatch') + Fore.RESET
            except:
                pass 
        
        if current_hwid in current_hwids:
            return True, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, '✓ Key validated successfully') + Fore.RESET
        
        if len(current_hwids) < max_users:
            keys_collection.update_one(
                {"key": key},
                {"$push": {"hwids": current_hwid}}
            )
            return True, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, f'✓ Key activated successfully ({len(current_hwids) + 1}/{max_users} slots used)') + Fore.RESET
        
        return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, f'✗ Maximum users reached ({max_users}/{max_users})') + Fore.RESET
    
    elif key_data["status"] == "INACTIVE":
        return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Key has expired') + Fore.RESET
    
    return False, f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Unknown key status!') + Fore.RESET


def get_key_info(key):
    """Get detailed key information, handling PENDING, ACTIVE, INACTIVE statuses"""
    key_data = keys_collection.find_one({"key": key, "category": "TOKEN-PASS-CHANGER"})
    if not key_data:
        return None
    
    if key_data["status"] == "ACTIVE" and key_data["expiry"]:
        now = datetime.now(timezone.utc)
        expiry = key_data["expiry"]
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if now >= expiry:
            keys_collection.update_one({"key": key}, {"$set": {"status": "INACTIVE"}})
            key_data["status"] = "INACTIVE"
            
    days_remaining = None
    if key_data["status"] == "ACTIVE" and key_data["expiry"]:
        expiry = key_data["expiry"]
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        days_remaining = (expiry - datetime.now(timezone.utc)).days
    elif key_data["status"] == "PENDING":
        days_remaining = key_data["days_duration"] 
    
    current_hwids = key_data.get("hwids", [])
    max_users = key_data.get("max_users", 1)
    
    return {
        "key": key_data["key"],
        "category": key_data["category"],
        "status": key_data["status"],
        "days_duration": key_data.get("days_duration"),
        "expiry": key_data["expiry"],
        "days_remaining": days_remaining,
        "revoked": key_data["revoked"],
        "current_hwids": len(current_hwids),
        "max_users": max_users,
        "ip_lock": key_data.get("ip_lock", None)
    }

def display_key_info(key_info):
    """Display key information in a formatted way"""
    if not key_info:
        return
    
    print(f'\n{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.blue_to_white, '📊 Key Information:') + Fore.RESET)
    print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.cyan_to_blue, f'🎟️ Key: {key_info["key"]}') + Fore.RESET)
    
    if key_info["status"] == "PENDING":
        print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.yellow_to_white, f'⏳ Duration: {key_info["days_duration"]} days (activates on first use)') + Fore.RESET)
    elif key_info["status"] == "ACTIVE":
        if key_info["days_remaining"] is not None:
            print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.cyan_to_blue, f'📅 Days Left: {key_info["days_remaining"]} days') + Fore.RESET)
        if key_info["expiry"]:
            expiry_local = key_info["expiry"].astimezone(datetime.now(timezone.utc).astimezone().tzinfo)
            print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.cyan_to_blue, f'⏰ Expires: {expiry_local.strftime("%Y-%m-%d %H:%M:%S")}') + Fore.RESET)
    elif key_info["status"] == "INACTIVE":
        print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '💀 Status: EXPIRED') + Fore.RESET)

    if key_info["ip_lock"]:
        print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.cyan_to_blue, f'🌐 IP Lock: {key_info["ip_lock"]}') + Fore.RESET)
    
    status_text = key_info["status"]
    if key_info["revoked"]:
        status_text = "REVOKED"
    elif key_info["status"] == "ACTIVE" and key_info["days_remaining"] < 0:
        status_text = "EXPIRED" 
    
    status_color = Colors.red_to_white if status_text in ["REVOKED", "EXPIRED", "INACTIVE"] else (Colors.yellow_to_white if status_text == "PENDING" else Colors.green_to_white)
    print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(status_color, f'🔒 Status: {status_text}') + Fore.RESET)
    time.sleep(2)

try:
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        with open("input/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ config.json not found') + Fore.RESET)
        input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.purple_to_blue, f'! Press Enter to exit.') + Fore.RESET)
        sys.exit()
    except json.JSONDecodeError:
        print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Invalid JSON in config.json') + Fore.RESET)
        input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.purple_to_blue, f'! Press Enter to exit.') + Fore.RESET)
        sys.exit()

    if "license" not in config.get("key", {}):
        print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ No license key found in config') + Fore.RESET)
        input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.purple_to_blue, f'! Press Enter to exit.') + Fore.RESET)
        sys.exit()
    
    key = config["key"]["license"]
    
    print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.blue_to_white, '! Validating license key...') + Fore.RESET)
    
    valid, message = validate_key(key)
    print(message)
    
    if not valid:
        input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.purple_to_blue, f'! Press Enter to exit.') + Fore.RESET)
        sys.exit()
    
    key_info_data = get_key_info(key)
    if key_info_data:
        display_key_info(key_info_data)
    
    print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, '✓ License validation completed!') + Fore.RESET)
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')
    
except Exception as e:
    print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, f'✗ License check failed: {e}') + Fore.RESET)
    input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.purple_to_blue, f'! Press Enter to exit.') + Fore.RESET)
    sys.exit()

if os.name == "nt":
    ctypes.windll.kernel32.SetConsoleTitleW("Virtual Token Password Changer")

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

os.system('cls' if os.name == 'nt' else 'clear')

class rex:

    def __init__(self):
        try:
            self.tokens = self.load_tokens()
            self.nowtimer = datetime.today().strftime('%H:%M:%S')
            os.system("mode 80, 20")
            self.clear()
            self.setTitle("Token Pass Changer | Made by 1huz")
            self.banner()


            with open("input/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            useproxy = config.get("proxy", False)

            if useproxy:
                print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, '✓ Proxy is ENABLED') + Fore.RESET)
                try:
                    with open("input/proxies.txt", "r", encoding="utf-8") as pf:
                        proxies = pf.read().splitlines()
                    proxy = "http://" + random.choice(proxies)
                except Exception as e:
                    print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, f'✗ An error occurred while reading proxies.txt: {e}') + Fore.RESET)
                    proxy = None
                self.session = tls_client.Session(client_identifier = "chrome_122", random_tls_extension_order=True)
                self.session.proxies = {
                    "http": proxy,
                    "https": proxy
                }
            else:
                print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, '✗ Proxy is DISABLED') + Fore.RESET)
                self.session = tls_client.Session(client_identifier = "chrome_122", random_tls_extension_order=True)

            self.today_folder = os.path.join("output", datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(self.today_folder, exist_ok=True)
            self.success_file = os.path.join(self.today_folder, "success.txt")
            self.error_file = os.path.join(self.today_folder, "error.txt")

            self.xyz_main()
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred during initialization: {e}") + Fore.RESET)
    
    def load_tokens(self):
        try:
            with open("input/tokens.txt", "r", encoding="utf-8") as file:
                return file.read().splitlines()
        except FileNotFoundError:

            print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.red_to_white, f'✗ tokens.txt file not found.') + Fore.RESET)
            return []
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while loading tokens: {e}") + Fore.RESET)
            return []

    def banner(self):
        try:
            banner = f'''

┌┬┐┌─┐┬┌─┌─┐┌┐┌  ┌─┐┬ ┬┌─┐┌┐┌┌─┐┌─┐┬─┐
 │ │ │├┴┐├┤ │││  │  ├─┤├─┤││││ ┬├┤ ├┬┘
 ┴ └─┘┴ ┴└─┘┘└┘  └─┘┴ ┴┴ ┴┘└┘└─┘└─┘┴└─
                (Made by 1huz | .gg/virtualstore)

'''
            print(Colorate.Vertical(Colors.purple_to_blue, Center.XCenter(banner)))
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while displaying the banner: {e}") + Fore.RESET)
    
    def clear(self):
        try:
            os.system("cls")
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while clearing the console: {e}") + Fore.RESET)
    
    def setTitle(self, _str):
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(f"{_str}")
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while setting the console title: {e}") + Fore.RESET)

    @staticmethod
    def get_cookie(): 
        try:
            response = requests.Session().get('https://discord.com/app')
            cookie = str(response.cookies)
            return cookie.split('dcfduid=')[1].split(' ')[0], cookie.split('sdcfduid=')[1].split(' ')[0], cookie.split('cfruid=')[1].split(' ')[0]
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while getting cookies: {e}") + Fore.RESET)
            return None, None, None
    
    @staticmethod
    def get_headers(token):
        try:
            dcfduid, sdcfduid, cfruid = rex.get_cookie() 
            if not all([dcfduid, sdcfduid, cfruid]):
                print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ Failed to get Discord cookies. Headers might be incomplete.") + Fore.RESET)

            headers = {
                "authority": "discord.com",
                "method": "GET",
                "path": "/api/v9/users/@me",
                "scheme": "https",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": token,
                "Cache-Control": "no-cache",
                "cookie": f"__dcfduid={dcfduid}; __sdcfduid={sdcfduid}; locale=en-US; __cfruid={cfruid}", 
                "Dnt": "1",
                "Pragma": "no-cache",
                "Priority": "u=1, i",
                "Referer": "https://discord.com/channels/@me",
                "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "en-US",
                "X-Discord-Timezone": "Asia/Calcutta",
                "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVEeXdhZXAua2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMjYuMC4wLjAgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEyNi4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMCIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjozMDMzNTEsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0=",
            }
            return headers
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while getting headers: {e}") + Fore.RESET)
            return None
    
    @staticmethod
    def check_status(status_code: int):
        status_messages = {
            200: "Success",
            201: "Success",
            204: "Success",
            400: "Detected Captcha",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method not allowed",
            429: "Too many Requests"
        }
        return status_messages.get(status_code, "Unknown Status")

    
    def xyz_main(self):

        try:
            start = time.time()
            checked = 0
            valid = 0
            invalid = 0
            changed = 0
            pass_type = input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.blue_to_white, '? Password type? (random/custom): ') + Fore.RESET).strip().lower()
            if pass_type == "random":
                def generate_random_password(length=10):
                    import string
                    chars = string.ascii_letters + string.digits + "@#$%&*"
                    return ''.join(random.choice(chars) for _ in range(length))
                get_new_pass = lambda: generate_random_password(10)
            elif pass_type == "custom":
                custom_pass = input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.blue_to_white, '? Enter your custom password: ') + Fore.RESET)
                get_new_pass = lambda: custom_pass
            else:
                print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ Invalid option. Please choose 'random' or 'custom'.") + Fore.RESET)
                return

            thread_input = input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.blue_to_white, '? Threads (default: 3, max: 20): ') + Fore.RESET).strip()
            max_threads = 20
            default_threads = 3
            if thread_input == '':
                threads = default_threads
            else:
                try:
                    threads = int(thread_input)
                    if threads > max_threads:
                        print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ Max threads is {max_threads}, using {max_threads}.") + Fore.RESET)
                        threads = max_threads
                    elif threads < 1:
                        print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ Minimum threads is 1, using 1.") + Fore.RESET)
                        threads = 1
                except ValueError:
                    print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ Invalid input, using default {default_threads}.") + Fore.RESET)
                    threads = default_threads

            def pwchanger(token, password, email):
                nonlocal checked, valid, invalid, changed 
                new_pass = get_new_pass()
                url = 'https://discord.com/api/v9/users/@me'
                payload = {'password': password, 'new_password': new_pass}
                headerz = rex.get_headers(token)
                if not headerz: 
                    print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ Failed to get headers for {email}. Skipping.") + Fore.RESET)
                    invalid += 1
                    return
                    
                old_tk = token[:32] + "..."
                try:
                    r = self.session.patch(url, json=payload, headers=headerz)
                    checked += 1 
                    if r.status_code == 200:
                        new_token = r.json()['token']
                        new_tk = new_token[:32] + "..."
                        print(f"{Fore.LIGHTBLACK_EX}[{self.nowtimer}] {Fore.RESET}| "
                              f"{Colorate.Horizontal(Colors.red_to_white, '✗ Old Token: ')}{Fore.RESET}{old_tk:<40} | "
                              f"{Colorate.Horizontal(Colors.green_to_white, '✓ New Token: ')}{Fore.RESET}{new_tk:<40} | "
                              f"{Colorate.Horizontal(Colors.blue_to_white, '! Password: ')}{Fore.RESET}{new_pass:<20}")
                        
                        with open(self.success_file, "a", encoding="utf-8") as f:
                            f.write(f"{email}:{new_pass}:{new_token}\n")
                        changed += 1
                        valid += 1
                    else:
                        print(f"{Fore.LIGHTBLACK_EX}[{self.nowtimer}] {Fore.RESET}| "
                              f"{Colorate.Horizontal(Colors.red_to_white, '✗ Old Token: ')}{Fore.RESET}{old_tk:<40} | "
                              f"{Colorate.Horizontal(Colors.red_to_white, '✗ Failed: ')}({rex.check_status(r.status_code)}){Fore.RESET}")

                        with open(self.error_file, "a", encoding="utf-8") as ef:
                            ef.write(f"{email}:{password}:{token} | Status: {r.status_code} | Error: {rex.check_status(r.status_code)}\n")
                        invalid += 1
                except Exception as e:
                    print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | " + Colorate.Horizontal(Colors.red_to_white, f"✗ An error occurred while changing password for {email}: {e}") + Fore.RESET)
        
                    with open(self.error_file, "a", encoding="utf-8") as ef:
                        ef.write(f"{email}:{password}:{token} | Exception: {str(e)}\n")
                    invalid += 1

            seen = set()
            tokens = []
            for account in self.tokens:
                if account not in seen:
                    tokens.append(account)
                    seen.add(account)

            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            for batch in chunks(tokens, threads):
                with ThreadPoolExecutor(max_workers=int(threads)) as executor:
                    futures = []
                    for account in batch:
                        email, password, token = account.split(':')[:3]
                        futures.append(executor.submit(pwchanger, token, password, email))
                    for future in futures:
                        future.result() 

            elapsed = time.time() - start
            print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, f'✓ Checked {checked} tokens in {int(elapsed // 60)} minutes and {int(elapsed % 60)} seconds') + Fore.RESET)
            print(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.green_to_white, f'✓ Finished checking tokens: Checked={checked}, Valid={valid}, Invalid={invalid}, Changed={changed}') + Fore.RESET)
            input(f'{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{getCurrentTime()}{Fore.WHITE}] | ' + Colorate.Horizontal(Colors.purple_to_blue, f'! Press Enter to exit.') + Fore.RESET)
            sys.exit()
        except Exception as e:
            print(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    rex()