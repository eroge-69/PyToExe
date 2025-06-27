import pyautogui
import time

while True:
    pyautogui.moveRel(50, 0, duration=0.5)
    pyautogui.moveRel(-50, 0, duration=0.5)
    print("moved")
    time.sleep(5) 
