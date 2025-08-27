import pyautogui
import random

pyautogui.FAILSAFE = False

while True:
    rand = random.randint(1, 5)
    count = 0
    pyautogui.keyDown('alt')
    while count < rand:
        pyautogui.press('tab')
        count += 1
    pyautogui.keyUp('alt')
    pyautogui.moveTo(100, 500, duration=0.1)