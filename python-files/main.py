import keyboard
import pyautogui
import threading
import time

clicking = False
delay = 1 / 30  # 30 CPS


def click_loop():
    while clicking:
        pyautogui.click()
        time.sleep(delay)


def toggle_clicking():
    global clicking
    clicking = not clicking
    if clicking:
        threading.Thread(target=click_loop).start()
    print("CPS BOOSTER:", "ON" if clicking else "OFF")


keyboard.add_hotkey("f6", toggle_clicking)

print("Press F6 to toggle CPS booster")

keyboard.wait("esc")
