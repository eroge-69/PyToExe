
from time      import sleep
from random    import randint
from pyautogui import leftClick

while True:
    leftClick(randint(100, 1800), randint(100, 900))
    sleep(3)
