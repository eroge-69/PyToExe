
import pyautogui
import time

def move_mouse():
    while True:
        pyautogui.moveRel(5, 0, duration=0.1)  # Move right slightly
        pyautogui.moveRel(-5, 0, duration=0.1) # Move back left
        time.sleep(10)

if __name__ == "__main__":
    move_mouse()
