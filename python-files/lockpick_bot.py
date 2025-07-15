import pyautogui
import time
import mss
import numpy as np
import cv2

# Settings
region = {"top": 530, "left": 910, "width": 100, "height": 100}
target_color = (255, 255, 255)
tolerance = 30

def is_white(pixel):
    return all(abs(int(c) - 255) < tolerance for c in pixel)

def main():
    print("Lockpick bot started. Press Ctrl+C to stop.")
    time.sleep(2)
    with mss.mss() as sct:
        while True:
            img = np.array(sct.grab(region))
            center_pixel = img[50, 50][:3]
            if is_white(center_pixel):
                pyautogui.press("space")
                time.sleep(0.15)

if __name__ == "__main__":
    main()
