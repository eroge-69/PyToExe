import time
from pynput import keyboard
from pynput.keyboard import Key, Controller, Listener

# Create keyboard controller
kb = Controller()

# Control flag to stop the loop
running = True

# Key press duration
duration = 0.5

# Sequence of keys to press
sequence = [Key.up, Key.left, Key.down, Key.right, Key.up]

def on_press(key):
    global running
    if key == Key.esc:
        running = False
        print("Escape pressed. Stopping...")

# Start listening for Esc key in background
listener = Listener(on_press=on_press)
listener.start()

# Loop through arrow key sequence
try:
    while running:
        for key in sequence:
            if not running:
                break
            kb.press(key)
            time.sleep(duration)
            kb.release(key)
            time.sleep(0.05)  # Small delay between keys
finally:
    listener.stop()
