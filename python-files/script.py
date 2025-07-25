import pyautogui as gui
import time

number = 8

while True:
	gui.typewrite(str(number))
	gui.press("enter")
	number += 1
	time.sleep(1.5)