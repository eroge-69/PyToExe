# auto_s_on_w_release.py
"""
Presses the 's' key automatically once whenever you release the 'w' key.

Installation:
    pip install pynput

Usage:
    python auto_s_on_w_release.py

To convert to a standalone Windows executable (run this in the same folder):
    pip install pyinstaller
    pyinstaller --onefile --noconsole auto_s_on_w_release.py

The resulting EXE will be located in the 'dist' folder.
"""

from pynput import keyboard


# Keeps track of whether 'w' is currently held down
w_held = False

# We’ll use this to send key presses
controller = keyboard.Controller()


def on_press(key):
    global w_held
    # Check if 'w' is pressed
    if key == keyboard.KeyCode.from_char('w'):
        w_held = True


def on_release(key):
    global w_held
    # If the released key is 'w' and it had been held down, send one 's'
    if key == keyboard.KeyCode.from_char('w') and w_held:
        controller.press('s')
        controller.release('s')
        w_held = False  # Reset the flag


# Create and start the listener.
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
