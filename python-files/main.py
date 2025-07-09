import pyautogui as pag
import random
import time

screen_width, screen_height = pag.size()

padding = 50

while True:
    x = random.randint(padding, screen_width - padding)
    y = random.randint(padding, screen_height - padding)
    pag.moveTo(x, y)
    time.sleep(2)
