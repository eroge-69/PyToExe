import pyautogui
import time

pyautogui.keyDown('alt')
pyautogui.keyDown('win')
pyautogui.keyDown('shift')
pyautogui.keyDown('ctrl')
for i in range(500000000000000):
    pyautogui.press('p')

pyautogui.keyUp('alt')
pyautogui.keyUp('win')
pyautogui.keyUp('shift')
pyautogui.keyUp('ctrl')