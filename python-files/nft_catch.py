import pyautogui
import time
import pytesseract
from PIL import Image
import keyboard
import threading
from PIL import ImageGrab, ImageFilter
import os
import sys
import datetime
import requests
import re
import ast

# Функция для чтения координат из файла
def load_coordinates_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Ищем словарь COORDINATES в файле
        pattern = r'COORDINATES\s*=\s*\{([^}]*)\}'
        match = re.search(pattern, content)
        if not match:
            raise ValueError("Не удалось найти COORDINATES в файле")
        
        dict_content = "{" + match.group(1) + "}"
        
        # Заменяем кортежи на списки для безопасного eval
        dict_content = re.sub(r'\(\((.*?)\),\s*\((.*?)\)\)', r'[[\1], [\2]]', dict_content)
        dict_content = re.sub(r'\((\d+),\s*(\d+)\)', r'[\1, \2]', dict_content)
        
        # Преобразуем строку в словарь Python
        coords_dict = ast.literal_eval(dict_content)
        
        # Конвертируем списки обратно в кортежи
        for key, value in coords_dict.items():
            if isinstance(value, list):
                if all(isinstance(item, list) for item in value):
                    # Это вложенные координаты (прямоугольник)
                    coords_dict[key] = tuple(tuple(coord) for coord in value)
                else:
                    # Это простые координаты (точка)
                    coords_dict[key] = tuple(value)
        
        return coords_dict
    
    except Exception as e:
        print(f"Ошибка при загрузке координат: {e}")
        return None

# Загружаем координаты из файла
COORDINATES = load_coordinates_from_file('coords.txt')
if COORDINATES is None:
    # Координаты по умолчанию на случай ошибки
    COORDINATES = {
        'refresh_btn': (2237, 113),
        'refresh_btn2': (2294, 136),
        'refresh_btn3': (2304, 176),
        'gift_1_btn': (2257, 224),
        'buy_confirm_btn': (2283, 454),
        'final_confirm_btn': (2458, 323),
        'price_area_1': ((2402, 441), (2436, 456)),
    }

# Проверка статуса программы
status = requests.get("https://pastebin.com/raw/WzxVeXvj").text 
if status == 'False':
    print("Программа закрыта! Ожидайте")
    sys.exit()
elif status == 'True':
    pass
else:
    print("Неизвестная ошибка! Проверьте соединение сети!")
    sys.exit()
import os
coo = os.environ.get("USERNAME")
# Остальные настройки
pytesseract.pytesseract.tesseract_cmd = rf'C:\Users\{coo}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
send_text = True
pricenum = 1
pyautogui.FAILSAFE = False
stop_flag = False


def refresh_market():
    """Обновляет список подарков"""
    pyautogui.click(COORDINATES['refresh_btn'])
    time.sleep(0.2)
    pyautogui.click(COORDINATES['refresh_btn3'])

def refresh_markets():
    pyautogui.click(COORDINATES['refresh_btn'])
    time.sleep(0.2)
    pyautogui.click(COORDINATES['refresh_btn2'])
    time.sleep(0.2)

def check_stop_key():
    """Проверяет, была ли нажата клавиша 7 для остановки"""
    global stop_flag
    keyboard.wait('7')  # Ждет нажатия 7
    stop_flag = True
    print("\nstop 7")

def get_price(area):
    """Извлекает цену из указанной области и преобразует по заданным правилам"""
    # Делаем скриншот области с ценой
    left, top = area[0]
    right, bottom = area[1]
    width = right - left
    height = bottom - top
    top -= 10
    bottom += 15
    
    if pricenum == 1:
        left -=25
        bottom -= 15
        bottom +=20
        top -= 15
        top+= 10
        right +=6
    elif pricenum == '2':
        left -= 5
        bottom -= 15
        bottom -= 5
        top += 10
        top -= 5

    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    screenshot.save("price_debug.png")  # Для проверки
    
    # Используем OCR для распознавания текста
    price_text = pytesseract.image_to_string(screenshot, config='--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,')
    
    try:
        # Очищаем текст и преобразуем в число
        price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
        
        # Преобразование по заданным правилам
        if '.' in price_text:
            parts = price_text.split('.')
            if len(parts) == 2:
                decimal_part = parts[1]
                # Если формат 0.00 (два знака после точки)
                if len(decimal_part) >= 2:
                    # Убираем точку и добавляем один ноль в конце
                    transformed_price = float(price_text.replace('.', '') + '0')
                # Если формат 0.0 (один знак после точки)
                elif len(decimal_part) == 1:
                    # Убираем точку и добавляем два нуля в конце
                    transformed_price = float(price_text.replace('.', '') + '00')
                else:
                    transformed_price = price
            else:
                transformed_price = price
        else:
            transformed_price = price
            
        return transformed_price
        
    except ValueError:
        print(f"err: {price_text}")
        sys.exit(0)
        return None

def buy_gift():
    """Покупает подарок по указанному номеру"""
    # Подтверждаем покупку
    pyautogui.click(COORDINATES['buy_confirm_btn'])
    time.sleep(0.3)
    # Финальное подтверждение
    pyautogui.click(COORDINATES['final_confirm_btn'])
    time.sleep(0.1)
    pyautogui.click(COORDINATES['final_confirm_btn'])
    time.sleep(0.1)
    pyautogui.click(COORDINATES['final_confirm_btn'])
    time.sleep(0.1)
    pyautogui.click(COORDINATES['final_confirm_btn'])
    time.sleep(0.1)
    pyautogui.click(COORDINATES['final_confirm_btn'])
    time.sleep(0.1)

def monitor_prices(threshold):
    global stop_flag, send_text
    stop_thread = threading.Thread(target=check_stop_key)
    stop_thread.daemon = True  # Завершится при завершении основного потока
    stop_thread.start()
    
    while not stop_flag:
        refresh_market()
        time.sleep(0.2)
        pyautogui.click(COORDINATES['gift_1_btn'])
        # Проверяем цену первого подарка
        price = get_price(COORDINATES['price_area_1'])
        
        if price is not None:
            if send_text: print(f"[NFTCATCH] цена 1 лота <> {price} звезд") 
            
            if price <= threshold:
                now = datetime.datetime.now()
                print(now.strftime("%H:%M"))
                print(f"DETECT PRICE ({threshold})! BUYING")
                buy_gift()
                print("SUF")
                break
        else:
            print("xz")
        
        pyautogui.press('esc')
        time.sleep(0.3)
        refresh_markets()
        pyautogui.click(COORDINATES['gift_1_btn'])
        # Проверяем цену первого подарка
        price = get_price(COORDINATES['price_area_1'])
        
        if price is not None:
            if send_text: print(f"[NFTCATCH] цена 1 лота <> {price} звезд") 
            
            if price <= threshold:
                now = datetime.datetime.now()
                print(now.strftime("%H:%M"))
                print(f"DETECT PRICE ({threshold})! BUYING")
                buy_gift()
                print("SUF")
                break
        else:
            print("xz")
        
        pyautogui.press('esc')
        time.sleep(0.3)

# Баннер и меню
banner = '''
d8b   db d88888b d888888b       .o88b.  .d8b.  d888888b  .o88b. db   db 
888o  88 88'     `~~88~~'      d8P  Y8 d8' `8b `~~88~~' d8P  Y8 88   88 
88V8o 88 88ooo      88         8P      88ooo88    88    8P      88ooo88 
88 V8o88 88~~~      88         8b      88~~~88    88    8b      88~~~88 
88  V888 88         88         Y8b  d8 88   88    88    Y8b  d8 88   88 
VP   V8P YP         YP          `Y88P' YP   YP    YP     `Y88P' YP   YP 
                                                                        
                                                                        
'''
print("--------------------------------------------------------------------")
print("NFT CATCH t.me/moondetect")
print("--------------------------------------------------------------------")
print("\n")

if __name__ == "__main__":
    try:
        while True:
            print("[1] Начать NFT DETECT")
            print("[2] Руководство")
            print("[3] Открыть telegram")
            choice = input("Выберите раздел: ")
            
            if choice == '1':
                print("< Программа запустилась! Удачи >")
                break
            elif choice == '2':
                print('''
Настройки окна: возьмите окно и переместите вверх, после перемещения в шторку найдите вариацию в виде окна и переместите окно в ПРАВЫЙ ВЕРХНИЙ УГОЛ этой вариации окна, после сожмите окно до минимума (Либо если шторки нет передвиньте в удобное место и не передвигайте окно)
Заходите и запускаете пипетку > и копируете кооридинаты которые вставляете в файл coords.txt (в поддержке раскажут подробней)
Что потом? Заходите в профиль > подарить подарок > себе (или на 2 аккаунт) >> выберите подарок. Готово! Запускайте программу!\n\n''')
            elif choice == '3':
                os.startfile(r'C:\Users\Happy\AppData\Roaming\Telegram Desktop\Telegram.exe')
                print("< Телеграм запущен >")
            else:
                print("Неверный выбор. Пожалуйста, выберите 1, 2 или 3.")
        
        threshold = float(input("порог (от 0 до числа которого будет скупать подарки): "))
        print(f"ценка::: <= {threshold}")
        print("exit ctrl+c")
        
        # Даем 5 секунд на переключение в окно браузера
        print("detecting window")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(5)
        
        monitor_prices(threshold)
    except KeyboardInterrupt:
        print("\nstopped by u")
    except Exception as e:
        print(f"error: {e}")