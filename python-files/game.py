import pyautogui
import time
import random
import threading

def smooth_move(x_start, y_start, x_end, y_end, duration=1.0, steps=100):
    for i in range(steps):
        t = i / steps
        offset_x = random.uniform(-1, 1)
        offset_y = random.uniform(-1, 1)
        x = x_start + (x_end - x_start) * t + offset_x
        y = y_start + (y_end - y_start) * t + offset_y
        pyautogui.moveTo(x, y)
        time.sleep(duration / steps)

def prank_mouse():
    time.sleep(3)  # فرصت آماده شدن

    screenWidth, screenHeight = pyautogui.size()

    while True:
        start_x, start_y = pyautogui.position()
        end_x = random.randint(0, screenWidth - 1)
        end_y = random.randint(0, screenHeight - 1)

        smooth_move(start_x, start_y, end_x, end_y, duration=random.uniform(1, 3))

        if random.random() < 0.3:
            pyautogui.click()

        time.sleep(random.uniform(0.5, 2))

if __name__ == "__main__":
    prank_mouse()
