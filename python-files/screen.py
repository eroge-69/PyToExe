import time
import os
from PIL import ImageGrab
import subprocess

SAVE_PATH = os.path.expanduser("~") + "\\AutoScreenshots\\latest.png"
UPLOAD_CMD = ["rclone", "copy", SAVE_PATH, "gdrive:screenshots", "--update"]

def take_screenshot():
    image = ImageGrab.grab()
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    image.save(SAVE_PATH)

def upload_to_drive():
    try:
        subprocess.run(UPLOAD_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass  # silently ignore errors

def main():
    while True:
        take_screenshot()
        upload_to_drive()
        time.sleep(2)  # 2 second interval

if __name__ == "__main__":
    main()