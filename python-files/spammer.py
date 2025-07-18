import threading
import time
import keyboard  # pip install keyboard
import pyautogui  # pip install pyautogui
import pyperclip  # pip install pyperclip
import random

running = False
stop_event = threading.Event()

second_messages = ["69", "50", "63"]
second_index = 0

def paste_and_enter(text):
    pyperclip.copy(text)
    time.sleep(random.uniform(0.6, 1.6))
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")

def spam_loop():
    global second_index

    while not stop_event.is_set():
        paste_and_enter("!9k slots")
        if stop_event.wait(0.3): break

        paste_and_enter(second_messages[second_index])
        second_index = (second_index + 1) % len(second_messages)

        if stop_event.wait(6.4): break

def toggle_spam():
    global running
    running = not running

    if running:
        stop_event.clear()
        print("[+] Started Spamming")
        threading.Thread(target=spam_loop, daemon=True).start()
    else:
        stop_event.set()
        print("[-] Stopped Spamming")

keyboard.add_hotkey("ctrl+f6", toggle_spam)

print("▶ Press Ctrl + F6 to start/stop the spam loop...")
keyboard.wait()