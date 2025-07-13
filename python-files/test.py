
import pyautogui
import time
import pygetwindow as gw
from pynput import keyboard

# Configuration variables
DELAY = 0.05  # Sleep time in seconds between clicks
WINDOW_TITLE = "Diablo IV"  # Exact or partial window title to check
KEY_TRIGGER = 'z'  # The key to trigger the action (lowercase for simplicity)

def on_press(key):
    try:
        if key.char.lower() == KEY_TRIGGER:
            active_window = gw.getActiveWindow()
            if active_window and WINDOW_TITLE in active_window.title:
                pyautogui.click(340, 818)
                time.sleep(DELAY)
                pyautogui.click(330, 500)
                time.sleep(DELAY)
                pyautogui.click(338, 956)
    except AttributeError:
        pass  # Ignore non-char keys

# Start the keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
