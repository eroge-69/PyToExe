import time
import keyboard
import pyautogui
import mss
import numpy as np
import cv2
import random # <-- ДОБАВИЛИ МОДУЛЬ ДЛЯ СЛУЧАЙНОСТЕЙ

# --- НАСТРОЙКИ ---
TRIGGER_KEY = 'f6' 
DETECTION_BOX_SIZE = 20

# --- УЛУЧШЕННЫЕ НАСТРОЙКИ ЦВЕТА (ФИОЛЕТОВЫЙ) ---
# Этот диапазон более широкий и надежный
PURPLE_LOWER = np.array([125, 40, 40])
PURPLE_UPPER = np.array([155, 255, 255])

# --- НАСТРОЙКИ "ЧЕЛОВЕЧНОСТИ" ---
# Имитация времени реакции человека (в секундах)
# Хороший игрок реагирует за 0.15 - 0.25 секунды. Мы сделаем чуть быстрее.
REACTION_TIME_MIN = 0.02  # 20 миллисекунд
REACTION_TIME_MAX = 0.08  # 80 миллисекунд

# Пауза после выстрела для имитации корректировки прицела
COOLDOWN_MIN = 0.1
COOLDOWN_MAX = 0.15


# --- ОСНОВНОЙ КОД ---

def main():
    """Главная функция, запускающая цикл триггера."""
    
    print("Триггер с 'человечностью' запущен.")
    print(f"Нажмите '{TRIGGER_KEY}' для включения/выключения.")
    
    # ... (остальной код инициализации без изменений) ...
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    box_half = DETECTION_BOX_SIZE // 2
    detection_box = {
        'top': center_y - box_half,
        'left': center_x - box_half,
        'width': DETECTION_BOX_SIZE,
        'height': DETECTION_BOX_SIZE,
    }
    bot_enabled = False
    sct = mss.mss()

    while True:
        try:
            if keyboard.is_pressed(TRIGGER_KEY):
                bot_enabled = not bot_enabled
                status = "ВКЛЮЧЕН" if bot_enabled else "ВЫКЛЮЧЕН"
                print(f"Триггер {status}")
                time.sleep(0.5)

            if bot_enabled:
                screenshot = sct.grab(detection_box)
                img = np.array(screenshot)
                hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv_img, PURPLE_LOWER, PURPLE_UPPER)
                
                if np.any(mask):
                    
                    # --- БЛОК ИМИТАЦИИ ЧЕЛОВЕКА ---

                    # 1. Имитируем случайное время реакции
                    reaction_delay = random.uniform(REACTION_TIME_MIN, REACTION_TIME_MAX)
                    print(f"Обнаружен фиолетовый! Реагирую через {reaction_delay:.3f} сек...")
                    time.sleep(reaction_delay)
                    
                    # 2. Делаем выстрел
                    pyautogui.click()
                    print("...Стреляю!")

                    # 3. Имитируем случайную паузу после выстрела
                    cooldown_delay = random.uniform(COOLDOWN_MIN, COOLDOWN_MAX)
                    time.sleep(cooldown_delay)

                    # --- КОНЕЦ БЛОКА ИМИТАЦИИ ---

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            break

if __name__ == "__main__":
    main()