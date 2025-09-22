import pyautogui
import time
import keyboard  # pip install keyboard

time.sleep(5)  # Başlamadan önce imleci hazırla

while True:
    if keyboard.is_pressed("*"):  # * tuşuna basınca dur
        break

    x, y = pyautogui.position()
    pyautogui.click(x, y)        # 1. Sol tık
    time.sleep(0.180)            # 180 ms bekle
    pyautogui.typewrite("999")   # "999" yaz
    time.sleep(0.180)            # 180 ms bekle
    pyautogui.click(x, y)        # 2. Sol tık

    time.sleep(600)              # 10 dakika bekle
