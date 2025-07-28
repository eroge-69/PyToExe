import pyautogui as mouse
import keyboard
import time
import random

time1 = int(time.time())

while True:
    time2 = int(time.time())
    if keyboard.is_pressed('ctrl+q'):
        break
    if (time2 - time1) % 10 == 0:
        mouse.moveTo(random.randint(10, 1000), random.randint(10, 1000))



