import pyautogui
import time

# Set the coordinates for the center of the screen
center_x = 1920 // 2
center_y = 1080 // 2

# Set the delay between each aim (in seconds)
delay = 1.5

while True:
    # Take a screenshot and find the enemy's position
    img = pyautogui.screenshot()
    data = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if data[x, y] == (255, 0, 0):  # Replace with the color of your enemy
                target_x = x
                target_y = y

    # Move the mouse to the center of the screen
    pyautogui.moveTo(center_x, center_y)

    # Wait for a bit before aiming at the target
    time.sleep(delay)

    # Move the mouse to the target's position
    pyautogui.moveTo(target_x + center_x - img.size[0] // 2, target_y + center_y - img.size[1] // 2)