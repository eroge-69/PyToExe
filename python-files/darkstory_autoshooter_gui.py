
import pyautogui
import keyboard
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab

# ค่าพื้นฐาน
running = False
delay = 100  # default 100 ms
screen_size = (1600, 1024)

def is_white(pixel):
    r, g, b = pixel
    return r > 240 and g > 240 and b > 240

def find_white_name():
    screenshot = ImageGrab.grab(bbox=(0, 0, *screen_size))
    pixels = screenshot.load()

    for y in range(200, 1024):  # เริ่มค้นหาจากบนลงล่าง
        for x in range(0, 1600):
            if is_white(pixels[x, y]):
                pyautogui.moveTo(x, y)
                pyautogui.click()
                return

def auto_shoot_loop():
    global running
    while True:
        if running:
            find_white_name()
            time.sleep(delay / 1000.0)
        else:
            time.sleep(0.1)

def toggle():
    global running
    running = not running
    status_label.config(text="กำลังทำงาน" if running else "หยุดทำงาน")

def update_delay(val):
    global delay
    delay = int(val)

# สร้าง GUI
root = tk.Tk()
root.title("DarkStory Auto Shooter")

frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Label(frame, text="Delay (ms):").grid(column=0, row=0)
delay_slider = ttk.Scale(frame, from_=10, to=1000, orient="horizontal", command=update_delay)
delay_slider.set(delay)
delay_slider.grid(column=1, row=0)

toggle_button = ttk.Button(frame, text="เริ่ม / หยุด (Tab)", command=toggle)
toggle_button.grid(column=0, row=1, columnspan=2, pady=10)

status_label = ttk.Label(frame, text="หยุดทำงาน", foreground="red")
status_label.grid(column=0, row=2, columnspan=2)

# กด Tab เพื่อ toggle การทำงาน
def listen_tab():
    while True:
        keyboard.wait("tab")
        toggle()
        time.sleep(0.3)  # กันการกดรัว

threading.Thread(target=auto_shoot_loop, daemon=True).start()
threading.Thread(target=listen_tab, daemon=True).start()

root.mainloop()
