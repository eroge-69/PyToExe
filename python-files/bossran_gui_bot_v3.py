# BossRan Bot - Full Features: Pet Feed, Captcha, Stats, Camera Rotate

import tkinter as tk
import pydirectinput as pdi
import time
import numpy as np
import threading
import keyboard
from PIL import ImageGrab
import cv2
import pytesseract
import random
import re
import pygetwindow as gw
import logging
from queue import Queue

# --- CONFIG ---
class Config:
    PET_ICON_POS = (640, 710)
    EXPECTED_COLOR = np.array([0, 0, 0])
    TOLERANCE = 30
    PET_CARD_POS = (807, 428)
    FOOD_SLOTS = [(844, 428), (877, 428), (915, 428), (951, 428), (987, 428)]
    INVENTORY_CHECK_POS = (816, 318)
    INVENTORY_CHECK_COLOR = (42, 42, 42)
    INVENTORY_TOLERANCE = 30
    CAPTCHA_BOX = (343, 348, 680, 443)
    OK_BUTTON_POS = (644, 431)
    GOLD_AREA = (780, 733, 925, 754)
    click_x_range = (50, 770)
    click_y_range = (380, 400)
    skill_keys = ['1','2','3','4','5','6','7','8','9','0']
    TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# --- STATE ---
class BotState:
    def __init__(self):
        self.running = False
        self.paused = False
        self.stop_requested = False
        self.last_pet_feed_time = 0
        self.captcha_last_solved = 0
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_time = 0
        self.last_stats_update = 0
        self.last_gold_check = 0
        self.gold_start = None
        self.gold_last = None
        self.stats = {
            "last_pet_feed_time": "N/A",
            "last_captcha_time": "N/A",
            "gold_current": "N/A",
            "gold_total": "N/A",
            "gold_start": "N/A",
            "runtime": "00:00:00",
        }

state = BotState()
input_queue = Queue()

# --- UTIL ---
def sleep(s): time.sleep(s)

def grab_image(bbox, gray=False):
    img = ImageGrab.grab(bbox=bbox).convert("RGB")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY) if gray else np.array(img)

def log(msg):
    logging.info(msg)
    if log_box:
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)
    print(msg.encode('ascii', errors='ignore').decode())

# --- GAME ---
def align_window():
    try:
        win = next(w for w in gw.getAllWindows() if "ran" in w.title.lower() and "bot" not in w.title.lower())
        win.restore(); win.moveTo(0, 0); win.resizeTo(1024, 768)
        log(f"[WINDOW] Aligned: {win.title}")
    except Exception as e:
        log(f"[ERROR] Window align: {e}")

def open_inventory():
    keyboard.press_and_release('i'); sleep(1)

def close_inventory():
    keyboard.press_and_release('i'); sleep(1)

def read_gold():
    # Open inventory if not open
    if not is_inventory_open():
        open_inventory()
        sleep(1.5)  # ✅ Delay to let inventory fully load

    # ✅ Move mouse out of the way (center of screen)
    center_x = 1024 // 2
    center_y = 768 // 2
    pdi.moveTo(center_x, center_y)
    sleep(0.5)  # ✅ Let the mouse settle and UI finish any animations

    # ✅ Grab gold image after delay
    img = ImageGrab.grab(bbox=Config.GOLD_AREA).convert("L")
    sleep(0.2)  # Optional extra delay before OCR
    _, thresh = cv2.threshold(np.array(img), 140, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(thresh, config='--psm 7')
    digits = re.sub(r'[^0-9]', '', text)
    return int(digits) if digits.isdigit() else 0

def is_inventory_open():
    x, y = Config.INVENTORY_CHECK_POS
    img = grab_image((x-5, y-5, x+5, y+5))
    return np.sum(np.linalg.norm(img - Config.INVENTORY_CHECK_COLOR, axis=2) < Config.INVENTORY_TOLERANCE) > 25

def is_pet_alive():
    x, y = Config.PET_ICON_POS
    img = grab_image((x-1, y-1, x+2, y+2))
    matches = np.sum(np.linalg.norm(img - Config.EXPECTED_COLOR, axis=2) < Config.TOLERANCE)
    return matches >= 3

def try_feed_from_slot(slot):
    pdi.moveTo(*slot); sleep(1)
    pdi.mouseDown(button='left'); sleep(0.05); pdi.mouseUp(button='left'); sleep(1)
    pdi.moveTo(*Config.PET_CARD_POS); sleep(0.5)
    pdi.mouseDown(button='right'); sleep(0.05); pdi.mouseUp(button='right'); sleep(2)
    pdi.moveTo(*slot); sleep(1)
    pdi.mouseDown(button='left'); sleep(0.05); pdi.mouseUp(button='left'); sleep(1)

def feed_pet():
    if time.time() - state.last_pet_feed_time < 90:
        return

    # Double check that pet is not already summoned
    for _ in range(2):
        pdi.press('a'); sleep(1)
        if is_pet_alive():
            return  # Pet is alive, no need to feed

    if not is_inventory_open():
        open_inventory()

    for slot in Config.FOOD_SLOTS:
        try_feed_from_slot(slot)

        # ✅ Check if pet already alive right after feeding
        if is_pet_alive():
            state.last_pet_feed_time = time.time()
            state.stats['last_pet_feed_time'] = time.strftime('%I:%M %p')
            close_inventory()
            log(f"[PET] Fed from slot {slot}")
            return

        # 🧪 Try pressing A to summon, then check again
        pdi.press('a'); sleep(1)
        if is_pet_alive():
            state.last_pet_feed_time = time.time()
            state.stats['last_pet_feed_time'] = time.strftime('%I:%M %p')
            close_inventory()
            log(f"[PET] Fed from slot {slot} (after pressing A)")
            return

    if is_inventory_open():
        close_inventory()
    log("[PET] Feeding failed - no food or pet not responding")

# --- CAPTCHA ---
def is_captcha_visible():
    img = grab_image(Config.CAPTCHA_BOX, gray=True)
    _, thresh = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, config='--psm 6').lower()
    return "please type the captcha" in text

def solve_captcha():
    if time.time() - state.captcha_last_solved < 10: return
    for _ in range(3):
        if not is_captcha_visible(): break
        log("[CAPTCHA] Detected, solving...")
        for _ in range(40): pdi.press('backspace'); sleep(0.01)
        sleep(2)
        img = grab_image(Config.CAPTCHA_BOX, gray=True)
        _, thresh = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        match = re.search(r'\[\s*(\d{4,6})\s*\]', text)
        code = match.group(1) if match else ""
        if code:
            for char in code: pdi.press(char); sleep(0.1)
            pdi.moveTo(*Config.OK_BUTTON_POS); sleep(0.2)
            pdi.mouseDown(button='left'); sleep(0.05); pdi.mouseUp(button='left'); sleep(3)
            if not is_captcha_visible():
                state.captcha_last_solved = time.time()
                state.stats['last_captcha_time'] = time.strftime('%I:%M %p')
                log(f"[CAPTCHA] Solved: {code}")
                break

# --- STATS ---
def update_gold_stats():
    if not state.gold_start:
        state.gold_start = read_gold()
        state.gold_last = state.gold_start
        state.stats["gold_start"] = f"{state.gold_start:,}"
        state.stats["gold_current"] = f"{state.gold_start:,}"
        state.stats["gold_total"] = "0"
    elif time.time() - state.last_gold_check > 1800:
        current = read_gold()
        state.gold_last = current
        state.stats["gold_current"] = f"{current:,}"
        diff = current - state.gold_start
        state.stats["gold_total"] = f"{diff:,}"
        state.last_gold_check = time.time()

def update_stats():
    if not state.running:
        return
    if state.start_time:
        runtime = time.time() - state.start_time - state.total_paused_time
        state.stats["runtime"] = time.strftime('%H:%M:%S', time.gmtime(runtime))
    update_gold_stats()
    refresh_gui()

def refresh_gui():
    last_feed_label.config(text=f"🐶 Last Pet Feed: {state.stats['last_pet_feed_time']}")
    last_captcha_label.config(text=f"🔐 Last Captcha: {state.stats['last_captcha_time']}")
    gold_start_label.config(text=f"💰 Starting Gold: {state.stats['gold_start']}")
    gold_now_label.config(text=f"⏳ Gold Now: {state.stats['gold_current']}")
    gold_total_label.config(text=f"🪙 Gold Farmed: {state.stats['gold_total']}")
    runtime_label.config(text=f"⏱ Runtime: {state.stats['runtime']}")

# --- ATTACK ---
def attack_loop():
    for _ in range(5):
        if state.stop_requested or not state.running or state.paused:
            return
        x = random.randint(*Config.click_x_range)
        y = random.randint(*Config.click_y_range)
        input_queue.put(('move', x, y))
        input_queue.put(('click',))
        if random.random() < 0.9:
            input_queue.put(('key', random.choice(Config.skill_keys)))
        sleep(0.2)

def rotate_camera():
    pdi.keyDown('right')
    sleep(1.0)
    pdi.keyUp('right')

# --- CONTROL ---
def toggle_pause():
    state.paused = not state.paused
    if state.paused:
        state.pause_start_time = time.time()
        status_label.config(text="Status: Paused")
        log("[BOT] Paused")
    else:
        if state.pause_start_time:
            state.total_paused_time += time.time() - state.pause_start_time
        state.pause_start_time = None
        status_label.config(text="Status: Running")
        log("[BOT] Resumed")

def schedule_stat_updates():
    if state.running and not state.paused:
        update_stats()
    root.after(1000, schedule_stat_updates)

def bot_loop():
    log("[BOT] Starting...")
    try:
        while state.running and not state.stop_requested:
            if state.paused: sleep(0.2); continue
            if is_inventory_open(): close_inventory()
            if is_captcha_visible(): solve_captcha(); continue
            if not is_pet_alive(): feed_pet()
            attack_loop()
            rotate_camera()
    except Exception as e:
        log(f"[BOT ERROR] {e}")


def start_bot():
    if not state.running:
        align_window()
        state.running = True
        state.paused = False
        state.stop_requested = False
        state.start_time = time.time()
        state.total_paused_time = 0
        update_gold_stats()
        threading.Thread(target=bot_loop, daemon=True).start()
        schedule_stat_updates()
        status_label.config(text="Status: Running")
        log("[BOT] Started")

def stop_bot():
    if state.pause_start_time:
        state.total_paused_time += time.time() - state.pause_start_time
    state.pause_start_time = None
    state.stop_requested = True
    state.running = False
    status_label.config(text="Status: Stopped")
    log("[BOT] Stopped")

# --- INPUT THREAD ---
def input_worker():
    while True:
        try:
            action = input_queue.get()
            if not state.running or state.paused or state.stop_requested:
                continue
            if action[0] == 'move': pdi.moveTo(action[1], action[2])
            elif action[0] == 'click': pdi.click(button='right')
            elif action[0] == 'key': pdi.press(action[1])
        except Exception as e:
            log(f"[INPUT ERROR] {e}")

threading.Thread(target=input_worker, daemon=True).start()

# --- GUI ---
root = tk.Tk()
root.title("BossRan Bot")
root.geometry("700x420")
root.configure(bg="#121212")

left = tk.Frame(root, bg="#121212")
left.pack(side="left", fill="y", padx=10)
right = tk.Frame(root, bg="#121212")
right.pack(side="right", fill="both", expand=True, padx=10)

tk.Label(right, text="BossRan Auto Bot", font=("Consolas", 14, "bold"), fg="white", bg="#121212").pack(pady=8)
tk.Button(right, text="▶ Start Bot", command=start_bot, font=("Consolas", 11), bg="#00C853", fg="white", width=20).pack(pady=5)
tk.Button(right, text="⏹ Stop Bot", command=stop_bot, font=("Consolas", 11), bg="#D50000", fg="white", width=20).pack(pady=5)
status_label = tk.Label(right, text="Status: Idle", font=("Consolas", 11), fg="white", bg="#121212")
status_label.pack(pady=5)

log_box = tk.Text(right, height=10, width=55, font=("Consolas", 9), bg="black", fg="white")
log_box.pack(pady=10)

last_feed_label = tk.Label(left, text="🐶 Last Pet Feed: N/A", font=("Consolas", 11), fg="white", bg="#121212")
last_feed_label.pack(anchor="w")
last_captcha_label = tk.Label(left, text="🔐 Last Captcha: N/A", font=("Consolas", 11), fg="white", bg="#121212")
last_captcha_label.pack(anchor="w")
gold_start_label = tk.Label(left, text="💰 Starting Gold: N/A", font=("Consolas", 11), fg="white", bg="#121212")
gold_start_label.pack(anchor="w")
gold_now_label = tk.Label(left, text="⏳ Gold Now: N/A", font=("Consolas", 11), fg="white", bg="#121212")
gold_now_label.pack(anchor="w")
gold_total_label = tk.Label(left, text="🪙 Gold Farmed: N/A", font=("Consolas", 11), fg="white", bg="#121212")
gold_total_label.pack(anchor="w")
runtime_label = tk.Label(left, text="⏱ Runtime: 00:00:00", font=("Consolas", 11), fg="white", bg="#121212")
runtime_label.pack(anchor="w")

keyboard.add_hotkey('f8', toggle_pause)
root.protocol("WM_DELETE_WINDOW", stop_bot)
root.mainloop()
