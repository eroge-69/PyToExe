import pyautogui
import time

with pyautogui.hold('win'):
    pyautogui.press('r')

pyautogui.write("cmd")
pyautogui.press('enter')

time.sleep(1)

pyautogui.press('f11')
pyautogui.write("color a")
pyautogui.press('enter')

time.sleep(0.5)

pyautogui.write("dir /s")
pyautogui.press('enter')

time.sleep(10)

with pyautogui.hold('alt'):
    pyautogui.press('f4')