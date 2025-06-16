
import cv2
import numpy as np
import pyautogui
import mss
import keyboard
import time
import random

# Színtartományok (RGB)
resource_colors = {
    "palladium": ([200, 200, 200], [255, 255, 255]),
    "cargo":     ([130, 80, 0],    [200, 150, 50]),
    "prometium": ([180, 0, 0],     [255, 80, 80]),
    "endurium":  ([0, 180, 0],     [80, 255, 80]),
    "terbium":   ([0, 0, 180],     [80, 80, 255]),
}

def random_delay(min_d=0.5, max_d=1.5):
    time.sleep(random.uniform(min_d, max_d))

def find_and_collect():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))
        image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        for name, (lower, upper) in resource_colors.items():
            mask = cv2.inRange(image, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if 5 < w < 40 and 5 < h < 40:
                    cx = x + w // 2 + random.randint(-3, 3)
                    cy = y + h // 2 + random.randint(-3, 3)
                    pyautogui.moveTo(cx, cy, duration=0.1)
                    pyautogui.click()
                    print(f"[{name}] Kattintás: {cx}, {cy}")
                    random_delay(2, 3)
                    return

print("Bot elindult – F11 leállítja.")
time.sleep(2)

try:
    while not keyboard.is_pressed("F11"):
        find_and_collect()
        random_delay(0.5, 1.0)
except KeyboardInterrupt:
    pass

print("Bot leállt.")
