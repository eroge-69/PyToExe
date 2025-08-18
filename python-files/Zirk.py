import sys
import threading
import tkinter as tk
from tkinter import simpledialog
import keyboard
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageFont

# --- Variables ---
count = 0
increment_key = "space"  # default key

# --- Functions ---
def create_icon_image(number):
    img = Image.new("RGB", (64, 64), "blue")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    w, h = draw.textsize(str(number), font=font)
    draw.text(((64 - w) / 2, (64 - h) / 2), str(number), fill="white", font=font)
    return img

def update_icon():
    icon.icon = create_icon_image(count)
    icon.title = f"Zikr: {count}"

def add_count():
    global count
    try:
        num = int(simpledialog.askstring("Add Count", "Enter number to add:"))
        count += num
        update_icon()
    except:
        pass

def reset_count():
    global count
    count = 0
    update_icon()

def change_key():
    global increment_key
    key = simpledialog.askstring("Change Key", "Enter new increment key:")
    if key:
        increment_key = key

def exit_app(icon, item):
    icon.stop()
    sys.exit()

def on_key_event(e):
    global count
    count += 1
    update_icon()

# --- Tray thread ---
def tray_thread():
    global icon
    menu = (
        item('Add', lambda: add_count()),
        item('Reset', lambda: reset_count()),
        item('Change Key', lambda: change_key()),
        item('Exit', exit_app)
    )
    icon = pystray.Icon("zikr_counter", create_icon_image(count), f"Zikr: {count}", menu)
    icon.run()

# --- Start tray ---
threading.Thread(target=tray_thread, daemon=True).start()

# --- Keyboard listener ---
keyboard.on_press_key(increment_key, on_key_event)

# --- Tkinter root for dialogs ---
root = tk.Tk()
root.withdraw()
root.mainloop()