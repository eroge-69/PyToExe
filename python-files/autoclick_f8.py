
import pyautogui
import time
import threading
from pynput import keyboard

running = False

def click_sequence():
    global running
    x = 500  # Toạ độ X (bạn có thể chỉnh lại theo nhu cầu)
    y_start = 955
    step = -65
    rows = 12

    while running:
        # Bấm phím B
        pyautogui.press('b')
        time.sleep(3)
        # Click 12 hàng
        for i in range(rows):
            if not running:
                break
            pyautogui.click(x, y_start + step * i)
            time.sleep(0.2)
        running = False  # chạy 1 lần rồi dừng

def on_press(key):
    global running
    try:
        if key == keyboard.Key.f8:
            if not running:
                running = True
                t = threading.Thread(target=click_sequence)
                t.start()
            else:
                running = False
    except:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
