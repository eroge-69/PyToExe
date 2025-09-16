import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab, Image, ImageDraw, ImageFont
import time
from pynput import keyboard
import threading

running = False
status_text = "Paused"

# Toggle start/stop with `
def on_press(key):
    global running, status_text
    try:
        if key.char == '`':
            running = not running
            status_text = "Running" if running else "Paused"
            print(status_text)
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

# Color ranges
red_lower = np.array([150, 0, 0])
red_upper = np.array([255, 80, 80])
blue_lower = np.array([0, 0, 150])
blue_upper = np.array([80, 80, 255])

# Function to show a small overlay
def overlay():
    while True:
        img = Image.new('RGB', (200, 50), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        d.text((10,10), f"Status: {status_text}", fill=(0,255,0) if running else (255,0,0), font=font)
        img.show()
        time.sleep(1)

# Run overlay in separate thread (optional, can slow if not handled carefully)
#threading.Thread(target=overlay, daemon=True).start()

while True:
    if running:
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

        red_mask = cv2.inRange(screen, red_lower, red_upper)
        blue_mask = cv2.inRange(screen, blue_lower, blue_upper)

        overlap = cv2.bitwise_and(red_mask, blue_mask)
        if np.any(overlap):
            pyautogui.press('e')
            time.sleep(0.1)

    time.sleep(0.01)
