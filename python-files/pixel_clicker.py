import pyautogui
import keyboard
import time
from PIL import ImageGrab

def get_center_pixel():
    screen_width, screen_height = pyautogui.size()
    x, y = screen_width // 2, screen_height // 2
    return ImageGrab.grab(bbox=(x, y, x+1, y+1)).getpixel((0, 0))

print("Hold ALT to monitor center pixel... Press ESC to quit.")

prev_color = None

while True:
    if keyboard.is_pressed("esc"):
        print("Exiting...")
        break

    if keyboard.is_pressed("alt"):
        current_color = get_center_pixel()
        if prev_color is None:
            prev_color = current_color

        if current_color != prev_color:
            pyautogui.click()
            print("Color changed → Mouse clicked!")
            prev_color = current_color
    else:
        prev_color = None

    time.sleep(0.05)