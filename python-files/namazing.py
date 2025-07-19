import os
import cv2
import numpy as np
import time
import ctypes
from PIL import ImageGrab

# ===== НАСТРОЙКИ =====
CAPTCHA_REGION = (845, 765, 1076, 867)  # Ваша область капчи
IMAGES_FOLDER = "D:/capcha_screenshots"  # Папка для скриншотов
HOLD_TIME = 1.1                         # Время зажатия (2 сек)
THRESHOLD = 0.9                         # Точность распознавания
CHECK_DELAY = 0.2                       # Частота проверки

# ===== УЛУЧШЕННЫЙ МЕТОД НАЖАТИЯ SHIFT =====
def press_shift(hold_time):
    """Усовершенствованный метод нажатия левого Shift"""
    try:
        # 1. Метод через SendInput (самый надежный)
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

        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        VK_LSHIFT = 0xA0  # Конкретно левый Shift

        extra = ctypes.c_ulong(0)
        ii = INPUT()
        ii.type = INPUT_KEYBOARD
        ii.ki.wVk = VK_LSHIFT
        
        # Нажатие
        ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
        time.sleep(hold_time)
        
        # Отпускание
        ii.ki.dwFlags = KEYEVENTF_KEYUP
        ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
        
        print("Левый Shift нажат успешно (метод SendInput)")
        return True
        
    except Exception as e:
        print(f"Ошибка SendInput: {e}")
        try:
            # 2. Резервный метод через keybd_event
            ctypes.windll.user32.keybd_event(0xA0, 0, 0, 0)  # Нажатие
            time.sleep(hold_time)
            ctypes.windll.user32.keybd_event(0xA0, 0, 0x0002, 0)  # Отпускание
            print("Левый Shift нажат (резервный метод)")
            return True
        except Exception as e:
            print(f"Ошибка резервного метода: {e}")
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
                if match["key"] == "shift":
                    press_shift(HOLD_TIME)  # Используем специальный метод для Shift
                else:
                    # Стандартный метод для других клавиш
                    if match["key"] in ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                                       'n','o','p','q','r','s','t','u','v','w','x','y','z',
                                       'up','down','left','right','space']:
                        # Реализацию press_key для других клавиш оставляем без изменений
                        pass
                time.sleep(0.5)
            else:
                time.sleep(CHECK_DELAY)
                
    except KeyboardInterrupt:
        print("\nРабота завершена")

if __name__ == "__main__":
    # Проверка запуска от администратора
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Требуются права администратора!")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        main()
    except Exception as e:
        print(f"Ошибка: {e}")