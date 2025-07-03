import pyautogui  # for mouse control and pixel color detection
import time       # for sleeping/waiting between actions


color = (231, 212, 180)  # RGB color to detect

while True:
    color1 = pyautogui.pixel(951,438)
    time.sleep(0.3)  # wait for a short duration before checking again
    if color1 == color:
        pyautogui.rightClick()
        time.sleep(2)
        pyautogui.rightClick()


