import pyautogui
import keyboard
import time

clicking = False  # Keeps track of clicking state

print("Press 'j' to toggle autoclicker on/off.")

while True:
    if keyboard.is_pressed('j'):
        clicking = not clicking  # Toggle state
        print("Clicking ON" if clicking else "Clicking OFF")
        time.sleep(0.3)  # Prevents rapid toggling if key is held down

    if clicking:
        pyautogui.click()
        time.sleep(0.1)  # Click speed
