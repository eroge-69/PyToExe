import tkinter as tk
from tkinter import messagebox
import pytesseract
import pyautogui
import requests
import time
import json
import threading
import mss
import cv2
import numpy as np
from PIL import Image

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# LLM API
LLM_API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "mistral"  # change if needed

# Globals
region = None
running = False
last_message = ""
conversation_history = [
    {"role": "system", "content": "You reply casually like the user — short, human, friendly."}
]

def grab_text_from_screen():
    global region
    with mss.mss() as sct:
        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2] - region[0],
            "height": region[3] - region[1],
        }
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        gray = img.convert("L")
        text = pytesseract.image_to_string(gray, lang="eng")
        return text.strip()

def generate_reply(new_user_message):
    global conversation_history
    conversation_history.append({"role": "user", "content": new_user_message})
    headers = {"Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": conversation_history,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        r = requests.post(LLM_API_URL, headers=headers, data=json.dumps(data))
        reply = r.json()["choices"][0]["message"]["content"].strip()
        conversation_history.append({"role": "assistant", "content": reply})
        if len(conversation_history) > 11:
            conversation_history = [conversation_history[0]] + conversation_history[-10:]
        return reply
    except Exception as e:
        return f"⚠️ Error: {e}"

def type_reply(text):
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.typewrite(text, interval=0.04)
    pyautogui.press("enter")

def bot_loop(status_label):
    global running, last_message
    while running:
        try:
            msg = grab_text_from_screen()
            if msg and msg != last_message:
                status_label.config(text=f"📩 New: {msg[:50]}", fg="blue")
                reply = generate_reply(msg)
                if reply:
                    type_reply(reply)
                    last_message = msg
            else:
                status_label.config(text="⏸ Waiting...", fg="gray")
        except Exception as e:
            status_label.config(text=f"❌ Error: {e}", fg="red")
        time.sleep(5)

def start_bot(status_label):
    global running
    if not region:
        messagebox.showwarning("Region Missing", "Please select a screen region first.")
        return
    if not running:
        running = True
        threading.Thread(target=bot_loop, args=(status_label,), daemon=True).start()
        status_label.config(text="✅ Bot running...", fg="green")

def stop_bot(status_label):
    global running
    running = False
    status_label.config(text="⛔ Bot stopped.", fg="red")

def select_region(region_label):
    def run_selector():
        global region
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        r = cv2.selectROI("Select Chat Area", screen_np, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select Chat Area")
        if r[2] > 0 and r[3] > 0:
            region = (int(r[0]), int(r[1]), int(r[0] + r[2]), int(r[1] + r[3]))
            region_label.config(text=f"📐 Region set: {region}", fg="green")
        else:
            region_label.config(text="⚠️ Region not selected", fg="red")

    threading.Thread(target=run_selector, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("Auto AI Chat Replier")
root.geometry("480x300")
root.resizable(False, False)

region_label = tk.Label(root, text="📍 No region selected", fg="red")
region_label.pack(pady=10)

tk.Button(root, text="🖼️ Select Screen Region", command=lambda: select_region(region_label)).pack(pady=5)

status_label = tk.Label(root, text="Bot not running", fg="red")
status_label.pack(pady=10)

tk.Button(root, text="▶️ Start Bot", command=lambda: start_bot(status_label)).pack(pady=5)
tk.Button(root, text="⏹️ Stop Bot", command=lambda: stop_bot(status_label)).pack(pady=5)

tk.Button(root, text="❌ Exit", command=root.destroy).pack(pady=20)

root.mainloop()
