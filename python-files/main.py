import pyautogui
import time
import threading
import keyboard

clicking = False

def clicker():
    while True:
        if clicking:
            pyautogui.click()
        time.sleep(0.01)  # adjust speed here

def toggle_clicking():
    global clicking
    clicking = not clicking
    print("Clicking:", clicking)

print("Auto Clicker (.EXE Style)")
print("Press F6 to toggle clicking")
print("Press ESC to exit")

threading.Thread(target=clicker, daemon=True).start()

keyboard.add_hotkey('f6', toggle_clicking)
keyboard.wait('esc')
