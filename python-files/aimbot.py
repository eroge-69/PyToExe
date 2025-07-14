
import ctypes
import time
import win32api
import win32con
import cv2
import numpy as np
import pyautogui
from mss import mss

# Screen capture config
monitor = {'top': 200, 'left': 200, 'width': 800, 'height': 600}
sct = mss()

def find_enemy(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_enemy = np.array([0, 70, 50])     # Adjust based on enemy color
    upper_enemy = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_enemy, upper_enemy)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def aim_at(x, y):
    screen_center_x = monitor['width'] // 2
    screen_center_y = monitor['height'] // 2
    dx = x - screen_center_x
    dy = y - screen_center_y
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0)

def fire():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

while True:
    img = np.array(sct.grab(monitor))
    enemies = find_enemy(img)

    if enemies:
        for contour in enemies:
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2
            aim_at(cx, cy)
            fire()
            break  # Shoot at the first found enemy
    time.sleep(0.01)
