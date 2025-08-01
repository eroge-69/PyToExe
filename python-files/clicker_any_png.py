
import pyautogui
import time
import os
import sys
from pathlib import Path

CLICK_DELAY = 2  # Задержка между кликами в секундах
CONFIDENCE = 0.85  # Уверенность в совпадении изображения

def resource_path(relative_path):
    """Поддержка относительных путей для .exe (PyInstaller)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def find_target_image():
    """Находит первый PNG-файл в папке и возвращает его путь"""
    for file in Path(".").iterdir():
        if file.suffix.lower() == ".png":
            return resource_path(file.name)
    return None

def main():
    print("Запуск кликера. Для выхода нажмите Ctrl+C.")
    image_path = find_target_image()
    if not image_path or not os.path.exists(image_path):
        print("PNG-файл не найден в папке. Положи картинку рядом с .exe и перезапусти.")
        return

    print(f"Будет использоваться файл: {image_path}")

    while True:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=CONFIDENCE)
        if location:
            print(f"Найдено: {location}, кликаем...")
            pyautogui.click(location)
        else:
            print("Изображение не найдено.")
        time.sleep(CLICK_DELAY)

if __name__ == "__main__":
    main()
