import pyautogui
import time
import random
import threading
from pystray import Icon as icon, MenuItem as item, Menu as menu
from PIL import Image, ImageDraw

def move_mouse_every(min_seconds=2, max_seconds=4):
    while True:
        x, y = pyautogui.position()
        dx = random.randint(-10, 10)
        dy = random.randint(-10, 10)
        pyautogui.moveTo(x + dx, y + dy, duration=random.uniform(0.1, 0.3))
        time.sleep(random.uniform(min_seconds, max_seconds))

def create_image():
    # Create a simple black square icon
    image = Image.new("RGB", (64, 64), "black")
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, 64, 64), fill="black")
    return image

def on_quit(icon, item):
    icon.stop()

def run_tray():
    tray_icon = icon("MouseMover", create_image(), menu=menu(item('Quit', on_quit)))
    tray_icon.run()

if __name__ == "__main__":
    t = threading.Thread(target=move_mouse_every, daemon=True)
    t.start()
    run_tray()
