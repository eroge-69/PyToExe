import pyautogui
import cv2
import numpy as np
import time
from mss import mss
import keyboard
import ctypes

ctypes.windll.user32.MessageBoxW(0, "������ �������!\n����� 8 ��� ���������/���������� �����������", "Aim Assist", 0)

monitor = {"top": 300, "left": 800, "width": 320, "height": 240}

lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])

sct = mss()
auto_aim_enabled = False

while True:
    if keyboard.is_pressed('8'):
        auto_aim_enabled = not auto_aim_enabled
        print("����������������:", "���" if auto_aim_enabled else "����")
        time.sleep(0.5)

    if auto_aim_enabled:
        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            if w > 40:  # ������������ ������ (� ��� ������� ���)
                target_x = x + w // 2
                target_y = y + h // 2
                screen_x = monitor["left"] + target_x
                screen_y = monitor["top"] + target_y
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                pyautogui.press('1')
                pyautogui.press('4')
                pyautogui.press('3')

    time.sleep(0.01)
