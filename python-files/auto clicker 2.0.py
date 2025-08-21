import pyautogui
import time
import keyboard  # Used to detect key presses

clicking = False  # Start with clicking disabled

if __name__ == "__main__":
    while True:
        # Check if '*' is pressed to toggle the clicking state
        if keyboard.is_pressed('*'):
            clicking = not clicking  # Toggle the clicking state
            print("Left-clicking started!" if clicking else "Left-clicking stopped!")
            time.sleep(0.0001)  # Small delay to prevent multiple presses from being detected at once

        if clicking:
            pyautogui.click(button='left')  # Simulate a left-click
            time.sleep(0.1)  # Small delay to prevent overwhelming the system
