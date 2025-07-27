from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import time
import pyautogui
import psutil

import subprocess


#file = open("c:/!ortip/test.txt", "r")
#content = file.read()
#print(content)
#file.close()


subprocess.Popen(["c:/1/bar_generator.exe"])  
time.sleep(0.1)
keyboard = KeyboardController()


# Press the Tab key
pyautogui.press('tab')
pyautogui.press('down')
pyautogui.press('down')
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('tab')
#keyboard.type(content)
#print (content)
 
#time.sleep(1)
#for process in (process for process in psutil.process_iter() if process.name()=="bar_generator.exe"):
#    process.kill()


