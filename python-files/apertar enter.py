import pyautogui
import time
import keyboard

while True:
    for _ in range(2):
        pyautogui.click(x=135, y=381)
        
    time.sleep(0.8)     

    keyboard.press_and_release('enter')

    time.sleep(0.2)
