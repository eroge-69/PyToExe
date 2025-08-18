import sys
import threading
import keyboard
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# --- Variables ---
count = 0
increment_key = "space"  # Change to any key

# --- Functions ---
def create_icon_image():
    """Create a simple blue square icon for tray"""
    img = Image.new("RGB", (64, 64), "blue")
    d = ImageDraw.Draw(img)
    return img

def update_icon():
    icon.title = f"Zikr: {count}"

def add_count():
    global count
    count += 1
    update_icon()

def reset_count():
    global count
    count = 0
    update_icon()

def exit_app(icon, item):
    icon.stop()
    sys.exit()

def on_key_event(e):
    add_count()

# --- Tray thread ---
def tray_thread():
    global icon
    menu = (
        item('Reset', lambda: reset_count()),
        item('Exit', exit_app)
    )
    icon = pystray.Icon("zikr_counter", create_icon_image(), f"Zikr: {count}", menu)
    icon.run()

# --- Start tray ---
threading.Thread(target=tray_thread, daemon=True).start()

# --- Keyboard listener ---
keyboard.on_press_key(increment_key, on_key_event)

# Keep the program running
keyboard.wait()