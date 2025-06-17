import pyautogui
import time
from random import random
from random import randint

pyautogui.FAILSAFE=False
repeat=1

def moving():
  sleep = round(((random()+0.1)*10)/2,2)
  move_x = randint(0,2560)
  move_y = randint(0,1980)
  duracao = round(random()+0.1,1)
  pyautogui.moveTo(move_x, move_y, duration=duracao)
#  pyautogui.moveRel(move_x, move_y, duration = duracao)
  time.sleep(sleep)
  global repeat
  repeat += 1

while True:
  moving()
