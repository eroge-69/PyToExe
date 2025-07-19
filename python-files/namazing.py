import os
import cv2
import numpy as np
import time
import ctypes
from PIL import ImageGrab

# ===== НАСТРОЙКИ =====
CAPTCHA_REGION = (845, 765, 1076, 867)  # Ваша область капчи
IMAGES_FOLDER = "D:/capcha_screenshots"  # Папка для скриншотов
HOLD_TIME = 2.0                         # Время зажатия (2 сек)
THRESHOLD = 0.9                         # Точность распознавания
CHECK_DELAY = 0.3                       # Частота проверки

# ===== НИЗКОУРОВНЕВЫЙ ВВОД =====
SendInput = ctypes.windll.user32.SendInput

# Структуры для эмуляции ввода
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ki", KEYBDINPUT),
        ("padding", ctypes.c_ubyte * 8)
    ]

def press_key(key):
    """Самый надежный метод ввода через SendInput"""
    # Коды клавиш
    vk_codes = {
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
        'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
        'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
        'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
        'z': 0x5A,
        'up': 0x26,       # VK_UP
        'down': 0x28,     # VK_DOWN
        'left': 0x25,     # VK_LEFT
        'right': 0x27,    # VK_RIGHT
        'space': 0x20,    # VK_SPACE
        'shift': 0xA0     # VK_LSHIFT (ЛЕВЫЙ Shift)
    }
    
    if key not in vk_codes:
        print(f"Клавиша {key} не поддерживается")
        return False

    # Настройка ввода
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    extra = ctypes.c_ulong(0)
    ii = INPUT()
    ii.type = INPUT_KEYBOARD
    ii.ki.wVk = vk_codes[key]
    
    try:
        # Нажатие клавиши
        SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
        time.sleep(HOLD_TIME)
        
        # Отпускание клавиши
        ii.ki.dwFlags = KEYEVENTF_KEYUP
        SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
        
        print(f"Успешно нажата клавиша: {key}")
        return True
    except Exception as e:
        print(f"Ошибка ввода: {e}")
        return False

# ===== ОСНОВНАЯ ФУНКЦИЯ =====
def main():
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    ctypes.windll.user32.SetProcessDPIAware()
    
    print("=== АВТОКЛАВИАТУРА ===")
    print("Запуск... (Ctrl+C для остановки)")
    
    try:
        while True:
            # 1. Делаем скриншот
            try:
                img = ImageGrab.grab(bbox=CAPTCHA_REGION)
            except Exception as e:
                print(f"Ошибка скриншота: {e}")
                time.sleep(1)
                continue
            
            # 2. Ищем совпадения
            match = None
            try:
                best_match = {"key": None, "confidence": 0}
                for filename in os.listdir(IMAGES_FOLDER):
                    if filename.endswith(('.png', '.jpg')):
                        template = cv2.imread(os.path.join(IMAGES_FOLDER, filename), cv2.IMREAD_GRAYSCALE)
                        if template is None:
                            continue
                            
                        current_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
                        res = cv2.matchTemplate(current_gray, template, cv2.TM_CCOEFF_NORMED)
                        _, confidence, _, _ = cv2.minMaxLoc(res)
                        
                        if confidence > best_match["confidence"]:
                            best_match = {
                                "key": os.path.splitext(filename)[0].lower(),
                                "confidence": confidence
                            }
                
                if best_match["confidence"] > THRESHOLD:
                    match = best_match
            except Exception as e:
                print(f"Ошибка сравнения: {e}")
            
            # 3. Обработка
            if match:
                print(f"Найдено: {match['key']} (точность: {match['confidence']:.2f})")
                press_key(match["key"])
                time.sleep(0.5)  # Защитная пауза
            else:
                time.sleep(CHECK_DELAY)
                
    except KeyboardInterrupt:
        print("\nРабота завершена")

if __name__ == "__main__":
    # Проверка запуска от администратора
    try:
        main()
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Попробуйте запустить скрипт от имени администратора")