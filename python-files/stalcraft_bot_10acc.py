import time
import os
import logging
import pyautogui
import cv2
import numpy as np
from telegram import Bot

TELEGRAM_TOKEN = "7566194395:AAGwLjPayqpUjLvviU83SnnBHeI0zwz-tAA"
TELEGRAM_USER_ID = "612778193"

bot = Bot(token=TELEGRAM_TOKEN)

THRESHOLD = 0.8
PAUSE = 1.5
ACCOUNT_COUNT = 10

logging.basicConfig(filename='cycle_bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

def log_and_wait(msg, delay=PAUSE):
    print(msg)
    logging.info(msg)
    time.sleep(delay)

def send_telegram(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_USER_ID, text=msg)
    except Exception as e:
        logging.error(f"Ошибка Telegram: {e}")

def find_on_screen(template_path, threshold=THRESHOLD):
    if not os.path.exists(template_path):
        logging.error(f"Файл не найден: {template_path}")
        return None
    screenshot = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    template = cv2.imread(template_path, 0)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    points = list(zip(*loc[::-1]))
    if points:
        return points[0]
    return None

def click_template(template_file, label):
    coords = find_on_screen(template_file)
    if coords:
        x, y = coords
        pyautogui.moveTo(x + 5, y + 5)
        pyautogui.click()
        log_and_wait(f"Нажал: {label}")
        return True
    else:
        logging.warning(f"Не найдено: {label}")
    return False

def check_and_handle_death():
    # Ждем 3 секунды после входа
    log_and_wait("Ожидание 3 секунды после входа...", 3)
    
    # Проверяем наличие смерти
    if find_on_screen("Death.png"):
        log_and_wait("Обнаружена смерть!")
        # Ждем 15 секунд перед нажатием ресурекшена
        log_and_wait("Ожидание 15 секунд перед ресурекшеном...", 15)
        # Ищем кнопку ресурекшена и кликаем
        if click_template("Resurrection.png", "Кнопка ресурекшена"):
            log_and_wait("Нажат ресурекшен")
        else:
            logging.warning("Не удалось найти кнопку ресурекшена")
    else:
        log_and_wait("Смерть не обнаружена, продолжаем...")

def main_loop():
    while True:
        for i in range(1, ACCOUNT_COUNT + 1):
            log_and_wait(f"====== Аккаунт {i} ======", 1)

            if not click_template(f"entry_{i}.png", f"Выбор аккаунта {i}"):
                continue
            time.sleep(1)

            if not click_template("login.png", "Кнопка входа"):
                continue
            
            # Добавляем обработку смерти
            check_and_handle_death()

            pyautogui.press("f")
            log_and_wait("Нажал F (открытие тайника)", 5)

            click_template("collect.png", "Кнопка сбора (X)")
            
            # Проверяем наличие кнопки отмены
            if find_on_screen("Cancel.png"):
                click_template("Cancel.png", "Кнопка отмены")
            
            time.sleep(2)
            pyautogui.press("esc")
            log_and_wait("Нажал ESC")
            time.sleep(3)

            click_template("exit.png", "

            log_and_wait("Ожидание перед следующим аккаунтом...", 40)

if __name__ == "__main__":
    log_and_wait("СТАРТ БОТА. Запуск цикла по аккаунтам...", 2)
    main_loop()
