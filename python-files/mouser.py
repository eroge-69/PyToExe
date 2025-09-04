import pyautogui
import random
import time

pyautogui.FAILSAFE = False

# Infinite loop to move the mouse cursor one pixel randomly to the right or left
while True:
    # Get the current mouse position
    current_x, current_y = pyautogui.position()
    
    # Randomly choose to move left (-1) or right (+1)
    move_direction = random.choice([-2, 2])
    
    # Calculate the new x-coordinate
    new_x = current_x + move_direction
    
    # Move the mouse cursor to the new position
    pyautogui.moveTo(new_x, current_y, duration=0.1)  # Adjust duration as needed
    
    # Pause for 60 seconds before the next movement
    time.sleep(60)
