import time
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Key

# Initialize mouse and keyboard controllers
mouse_controller = MouseController()
keyboard_listener = keyboard.Controller()

# Create a set to track currently pressed keys
pressed_keys = set()
pressed_buttons = set()

# Amount of Y-axis recoil movement
RECOIL_AMOUNT = 15
RECOIL_INTERVAL = 0.009  # 9 milliseconds

def on_press(key):
    pressed_keys.add(key)

def on_release(key):
    pressed_keys.discard(key)

def on_click(x, y, button, pressed):
    if pressed:
        pressed_buttons.add(button)
    else:
        pressed_buttons.discard(button)

# Start listeners
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

try:
    while True:
        if (Key.caps_lock in pressed_keys and
            mouse.Button.right in pressed_buttons and
            mouse.Button.left in pressed_buttons):
            
            mouse_controller.move(0, RECOIL_AMOUNT)
            time.sleep(RECOIL_INTERVAL)
        else:
            time.sleep(0.01)
except KeyboardInterrupt:
    pass
