import pyautogui
import keyboard
import time
import random
import win32api
import win32con
import pytesseract
import numpy as np
import cv2
from PIL import ImageGrab

# ===== CONFIG =====
ITEMS_TO_TRACK = {
    "Элитры": {"max_buy": 200000, "sell_price": 700000},
    "Броня": {"max_buy": 150000, "sell_price": 500000},
    "Слитки": {"max_buy": 50000, "sell_price": 150000}
}
REFRESH_COOLDOWN = 3  # Секунды между проверками
MIN_DELAY = 0.05  # Минимальная задержка
MAX_DELAY = 0.3  # Максимальная задержка
DEBUG_MODE = True

# Настройки OCR
PRICE_REGION = (800, 400, 1000, 450)  # Область цены (x1, y1, x2, y2)
ITEM_REGION = (500, 400, 700, 450)  # Область названия предмета
TESSERACT_CONFIG = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'

# Координаты (настройте под себя!)
CHAT_POS = (100, 950)
SEARCH_BUTTON = (300, 300)
BUY_BUTTON = (900, 450)
CONFIRM_BUTTON = (950, 600)
REFRESH_BUTTON = (1100, 200)

# ===== OCR УЛУЧШЕНИЯ =====
def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.dilate(thresh, kernel, iterations=1)
    return processed

def extract_text_from_region(region):
    screenshot = ImageGrab.grab(bbox=region)
    processed_img = preprocess_image(screenshot)
    text = pytesseract.image_to_string(processed_img, config=TESSERACT_CONFIG)
    return ''.join(filter(str.isdigit, text))

# ===== ОСНОВНЫЕ ФУНКЦИИ =====
def log(message):
    if DEBUG_MODE:
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

def human_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

def human_click(x, y):
    win32api.SetCursorPos((x + random.randint(-3, 3), y + random.randint(-3, 3)))
    human_delay()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(random.uniform(0.02, 0.1))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    human_delay()

def human_type(text):
    for char in text:
        keyboard.write(char)
        time.sleep(random.uniform(0.03, 0.15))

def search_item(item_name):
    log(f"Поиск: {item_name}")
    human_click(*CHAT_POS)
    human_type(f"/ah search {item_name}")
    keyboard.press_and_release('enter')
    human_delay()

def check_item_and_price():
    try:
        item_text = extract_text_from_region(ITEM_REGION)
        price_text = extract_text_from_region(PRICE_REGION)
        if not price_text:
            return None, None
        
        price = int(price_text)
        for item_name in ITEMS_TO_TRACK:
            if item_name.lower() in item_text.lower():
                return item_name, price
        return None, price
    except:
        return None, None

def buy_and_resell(item_name, sell_price):
    log(f"Покупка {item_name}...")
    human_click(*BUY_BUTTON)
    human_delay()
    human_click(*CONFIRM_BUTTON)
    human_delay()
    
    log(f"Перепродажа за {sell_price}...")
    human_click(*CHAT_POS)
    human_type(f"/ah sell {item_name} {sell_price}")
    keyboard.press_and_release('enter')
    human_delay()

def main_loop():
    log("Скрипт запущен (F12 - остановить)")
    while not keyboard.is_pressed('F12'):
        try:
            for item in ITEMS_TO_TRACK:
                search_item(item)
                time.sleep(0.5)
                
                item_name, price = check_item_and_price()
                if item_name and price <= ITEMS_TO_TRACK[item_name]["max_buy"]:
                    buy_and_resell(item_name, ITEMS_TO_TRACK[item_name]["sell_price"])
                
                human_click(*REFRESH_BUTTON)
                time.sleep(REFRESH_COOLDOWN * random.uniform(0.9, 1.1))
                
        except Exception as e:
            log(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Укажите свой путь
    time.sleep(random.uniform(1, 5))
    main_loop()