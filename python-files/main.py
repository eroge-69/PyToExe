import cv2
import pyautogui
import time

mouse = cv2.imread("mouse.png")
confirm = cv2.imread("confirm.png")
pyautogui.move(0, 1500)
time.sleep(0.5)
pyautogui.click(x=1912, y=1062)
time.sleep(0.5)
pyautogui.click(x=1200, y=300, button=pyautogui.RIGHT)
pyautogui.click(x=842, y=743)
time.sleep(0.5)
pyautogui.click('mouse.png')
time.sleep(0.5)
pyautogui.move(0, 100)
pyautogui.click()
pyautogui.click('rundll32_k0RFbrkvP4.png')

