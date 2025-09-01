import pyautogui
import keyboard  # to detect key press

# Adjust this value to control speed
SCROLL_SPEED = 200  

print("Hold UP or DOWN arrow to scroll fast. Press ESC to exit.")

while True:
    if keyboard.is_pressed("up"):
        pyautogui.scroll(SCROLL_SPEED)
    elif keyboard.is_pressed("down"):
        pyautogui.scroll(-SCROLL_SPEED)
    elif keyboard.is_pressed("esc"):
        break
