
import cv2
import numpy as np
import pyautogui
import threading
import keyboard
import time
import tkinter as tk
from PIL import ImageTk, Image
import ctypes

# Ładowanie wzorca arbuza
template = cv2.imread("arbuz.png", cv2.IMREAD_UNCHANGED)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
w, h = template_gray.shape[::-1]

running = False
hit_count = 0

def click_in_match(x, y, w, h):
    rx = np.random.randint(x + 5, x + w - 5)
    ry = np.random.randint(y + 5, y + h - 5)
    pyautogui.moveTo(rx, ry)
    pyautogui.click()

def detect_and_click():
    global running, hit_count
    while True:
        if running:
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            res = cv2.matchTemplate(frame, template_gray, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.80)
            matches = list(zip(*loc[::-1]))
            if matches:
                x, y = matches[0]
                click_in_match(x, y, w, h)
                # Poczekaj aż arbuz zniknie (czyli przestanie się pojawiać w tym miejscu)
                for _ in range(20):
                    screenshot = pyautogui.screenshot()
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                    res = cv2.matchTemplate(frame, template_gray, cv2.TM_CCOEFF_NORMED)
                    if np.max(res) < 0.80:
                        break
                    time.sleep(0.05)
                hit_count += 1
                update_label()
        time.sleep(0.05)

def toggle():
    global running
    running = not running
    status_label.config(text="Bot aktywny" if running else "Bot wyłączony",
                        fg="green" if running else "red")

def update_label():
    counter_label.config(text=f"Zbite arbuzy: {hit_count}")

def setup_gui():
    global status_label, counter_label
    window = tk.Tk()
    window.title("Arbuz Bot")
    window.attributes("-topmost", True)
    window.geometry("200x80+20+20")
    window.resizable(False, False)

    status_label = tk.Label(window, text="Bot wyłączony", fg="red", font=("Arial", 12))
    status_label.pack()

    counter_label = tk.Label(window, text="Zbite arbuzy: 0", font=("Arial", 12))
    counter_label.pack()

    window.after(100, lambda: window.lift())  # aby nie zniknęło pod grą
    threading.Thread(target=detect_and_click, daemon=True).start()
    window.mainloop()

keyboard.add_hotkey("F8", toggle)

setup_gui()
