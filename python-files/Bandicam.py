import pyautogui
import time
import random
from PIL import ImageGrab
import keyboard
import threading

# --- Настройки ---
SIGN_REGION = (460, 690, 470, 700)  # Координаты области появления знака (настрой под себя)

running = False  # Флаг включения/выключения бота

# --- Проверка знака ---
def check_for_red_exclamation():
    img = ImageGrab.grab(bbox=SIGN_REGION)
    for x in range(img.width):
        for y in range(img.height):
            r, g, b = img.getpixel((x, y))

            # Гибкая проверка "почти красного"
            if r > 200 and g < 100 and b < 100:
                return True
    return False

# --- Закидывание удочки ---
def cast_fishing_rod():
    pyautogui.click(button='right')
    time.sleep(random.uniform(0.5, 1.5))

# --- Основной цикл рыбалки ---
def fishing_loop():
    global running
    while running:
        cast_fishing_rod()
        timeout = random.uniform(10, 12)  
        start_time = time.time()
        while running:
            if check_for_red_exclamation():
                pyautogui.click(button='right')
                break
            elif time.time() - start_time > timeout:  
                print("⏳ Нет поклёвки — перекидываю удочку")
                pyautogui.click(button='right')  # второй ПКМ
                time.sleep(random.uniform(0.2, 1.0))
                break
            time.sleep(0.1)
        time.sleep(random.uniform(0.2, 1.0))

# --- Управление включением/выключением ---
def listen_hotkeys():
    global running
    while True:
        if keyboard.is_pressed('ctrl+up') and not running:
            print("▶️ Бот запущен")
            running = True
            threading.Thread(target=fishing_loop, daemon=True).start()
            time.sleep(1)
        elif keyboard.is_pressed('ctrl+right') and running:
            print("⛔ Бот остановлен")
            running = False
            time.sleep(1)

# --- Запуск ---
if __name__ == '__main__':
    print("⌨️  Нажми Ctrl + ↑ чтобы запустить, Ctrl + → чтобы остановить.")
    listen_hotkeys()