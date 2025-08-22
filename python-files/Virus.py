import pyautogui as p
import random
import time


for i in range(10):

    x= random.randint(900, 1500)

y= random.randint(400, 800)

p.moveTo(x, y)

time.sleep(0.2)