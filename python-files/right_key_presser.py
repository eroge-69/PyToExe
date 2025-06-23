
import pyautogui
import time

interval = 50  # seconds

print("Right arrow key presser started. Press Ctrl+C to stop.")

try:
    while True:
        pyautogui.press('right')  # Press the right arrow key
        print("Pressed → Right key.")
        time.sleep(interval)
except KeyboardInterrupt:
    print("Stopped by user.")
