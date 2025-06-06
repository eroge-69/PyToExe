
import time
import threading
import queue
import base64
import json
import logging
from io import BytesIO

import pyautogui
import mss
import cv2
import numpy as np
import openai
import win32gui
from PIL import Image

# --- Настройки ---
def load_api_key(filename="apikey.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Не удалось загрузить API ключ из {filename}: {e}")
        return None

OPENAI_API_KEY = load_api_key()
if OPENAI_API_KEY is None:
    raise ValueError("API ключ не загружен. Проверьте файл apikey.txt.")

MODEL_NAME = "gpt-4o"
SCREENSHOT_WIDTH = 640
SCREENSHOT_HEIGHT = 360
CAPTURE_INTERVAL = 1.0  # время между скриншотами (сек)
COMMAND_INTERVAL = 0.4  # задержка между командами
PAUSE_BRIGHTNESS_THRESHOLD = 35
MAX_COMMAND_QUEUE_SIZE = 3
MAX_MESSAGE_HISTORY = 6  # сколько сообщений хранить для контекста

# --- Логи ---
logging.basicConfig(
    filename='minecraft_ai_bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def log_debug(msg):
    print(msg)
    logging.info(msg)

# --- OpenAI ---
openai.api_key = OPENAI_API_KEY

# --- Очереди ---
screenshot_queue = queue.Queue(maxsize=1)
command_queue = queue.Queue(maxsize=MAX_COMMAND_QUEUE_SIZE)

# --- История сообщений для контекста ---
message_history = [
    {"role": "system", "content": "Ты ИИ, управляющий игроком в Minecraft. Обрабатывай скриншоты и возвращай команды JSON."}
]

# --- Поиск окна ---
def find_minecraft_window():
    hwnds = []
    def enum_handler(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "Minecraft" in title:
            results.append(hwnd)
    win32gui.EnumWindows(enum_handler, hwnds)
    return hwnds[0] if hwnds else None

# --- Захват экрана ---
def capture_screen_loop(hwnd):
    with mss.mss() as sct:
        while True:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                monitor = {"left": left, "top": top, "width": right - left, "height": bottom - top}
                sct_img = sct.grab(monitor)
                img = np.array(sct_img)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                img = cv2.resize(img, (SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT))
                if screenshot_queue.full():
                    _ = screenshot_queue.get()
                screenshot_queue.put(img)
                time.sleep(CAPTURE_INTERVAL)
            except Exception as e:
                logging.error(f"Capture error: {e}")
                time.sleep(2)

# --- Конвертация в base64 ---
def image_to_base64(img):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    buffered = BytesIO()
    pil_img.save(buffered, format="JPEG", quality=50)
    return base64.b64encode(buffered.getvalue()).decode()

# --- Проверка паузы ---
def is_game_paused(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    return brightness < PAUSE_BRIGHTNESS_THRESHOLD

# --- Преобразование изображения в описание (простейший вариант) ---
def describe_scene(img):
    # Просто считаем средний цвет и яркость (можно расширить)
    avg_color = img.mean(axis=(0,1))
    brightness = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    description = f"Средний цвет RGB: {avg_color.astype(int).tolist()}, яркость: {brightness:.1f}"
    return description

# --- Парсинг команды ---
def parse_command(cmd_text):
    try:
        return json.loads(cmd_text)
    except Exception:
        return {"walk": False, "jump": False, "attack": False, "dig": False,
                "direction": "none", "look_x": 0, "look_y": 0}

# --- Цикл GPT с историей ---
def gpt_command_loop():
    last_cmd = None
    global message_history

    while True:
        try:
            img = screenshot_queue.get()
            if img is None:
                time.sleep(1)
                continue

            if is_game_paused(img):
                empty_cmd = {"walk": False, "jump": False, "attack": False, "dig": False,
                             "direction": "none", "look_x": 0, "look_y": 0}
                if command_queue.full():
                    _ = command_queue.get()
                command_queue.put(empty_cmd)
                time.sleep(2)
                continue

            img_b64 = image_to_base64(img)
            scene_desc = describe_scene(img)

            # Добавляем новое сообщение в историю
            message_history.append({"role": "user", "content": f"Сцена: {scene_desc}"})
            message_history.append({"role": "user", "content": [
                {"type": "text", "text": "Определи действия и куда смотреть."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]})

            # Ограничиваем длину истории
            if len(message_history) > MAX_MESSAGE_HISTORY:
                message_history = message_history[-MAX_MESSAGE_HISTORY:]

            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=message_history,
                max_tokens=150,
                temperature=0.3,
            )
            cmd_text = response.choices[0].message['content']

            cmd = parse_command(cmd_text)

            # Добавляем ответ ИИ в историю
            message_history.append({"role": "assistant", "content": cmd_text})

            if last_cmd != cmd:
                if command_queue.full():
                    _ = command_queue.get()
                command_queue.put(cmd)
                last_cmd = cmd

            time.sleep(COMMAND_INTERVAL)

        except Exception as e:
            logging.error(f"GPT loop error: {e}")
            time.sleep(3)

# --- Выполнение команды ---
def perform_action(cmd):
    try:
        for key in ['w', 'a', 's', 'd']:
            pyautogui.keyUp(key)

        if cmd.get("walk", False):
            d = cmd.get("direction", "none")
            if d == "forward": pyautogui.keyDown('w')
            elif d == "backward": pyautogui.keyDown('s')
            elif d == "left": pyautogui.keyDown('a')
            elif d == "right": pyautogui.keyDown('d')

        if cmd.get("jump", False):
            pyautogui.press('space')

        if cmd.get("attack", False) or cmd.get("dig", False):
            pyautogui.mouseDown(button='left')
        else:
            pyautogui.mouseUp(button='left')

        look_x = cmd.get("look_x", 0)
        look_y = cmd.get("look_y", 0)

        sens = 1.0
        move_x = int(look_x * sens)
        move_y = int(look_y * sens)

        if move_x != 0 or move_y != 0:
            pyautogui.moveRel(move_x, move_y, duration=0.1)

        log_debug(f"Выполнено действие: {cmd}")

    except Exception as e:
        logging.error(f"Ошибка выполнения действия: {e}")

# --- Цикл исполнения ---
def action_loop():
    while True:
        try:
            cmd = command_queue.get()
            if cmd:
                perform_action(cmd)
            time.sleep(COMMAND_INTERVAL)
        except Exception as e:
            logging.error(f"Action loop error: {e}")
            time.sleep(1)

# --- Главная функция ---
def main():
    hwnd = None
    while hwnd is None:
        hwnd = find_minecraft_window()
        if hwnd is None:
            time.sleep(2)

    threading.Thread(target=capture_screen_loop, args=(hwnd,), daemon=True).start()
    threading.Thread(target=gpt_command_loop, daemon=True).start()
    threading.Thread(target=action_loop, daemon=True).start()

    log_debug("Minecraft AI бот запущен!")

    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
