
import cv2
import numpy as np
import pyautogui
import mss
import keyboard
import time
import random

def random_delay(min_delay=0.5, max_delay=1.5):
    time.sleep(random.uniform(min_delay, max_delay))

# Palladium színtartomány (szürkésfehér csillogás)
lower_color = np.array([200, 200, 200])
upper_color = np.array([255, 255, 255])

def find_and_click():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))
        image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        mask = cv2.inRange(image, lower_color, upper_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if 5 < w < 40 and 5 < h < 40:
                center_x = x + w // 2 + random.randint(-3, 3)
                center_y = y + h // 2 + random.randint(-3, 3)
                pyautogui.moveTo(center_x, center_y, duration=0.1)
                pyautogui.click()
                print(f"Kattintás: {center_x}, {center_y}")
                random_delay(1.5, 3)
                break

print("Bot elindult. Nyomd meg az F11-et a leállításhoz.")
time.sleep(2)

try:
    while not keyboard.is_pressed("F11"):
        find_and_click()
        random_delay(0.5, 1.0)
except KeyboardInterrupt:
    print("Bot manuálisan leállítva.")

print("Bot leállt.")
