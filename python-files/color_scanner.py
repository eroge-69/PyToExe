import pyautogui
import time
from PIL import ImageGrab

def get_crosshair_pixel_color():
    screen_width, screen_height = pyautogui.size()
    x = screen_width // 2
    y = screen_height // 2
    img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    return img.getpixel((0, 0))

print("🔍 Farbscanner gestartet – STRG+C zum Beenden.")
time.sleep(1)

try:
    while True:
        color = get_crosshair_pixel_color()
        print(f"Farbe unter Fadenkreuz: RGB{color}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n🛑 Farbscanner beendet.")