import threading
import time
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController

mouse = MouseController()
keyboard = KeyboardController()

rmb_held = False
stop_event = threading.Event()

def spam_actions():
    keys = ['1', '2', '3', '4', '5']
    index = 0
    while not stop_event.is_set():
        # Press key
        keyboard.press(keys[index])
        keyboard.release(keys[index])
        index = (index + 1) % len(keys)

        # Click LMB and RMB
        mouse.press(Button.left)
        mouse.release(Button.left)
        mouse.press(Button.right)
        mouse.release(Button.right)

        time.sleep(0.1)  # Adjust speed as needed

def on_click(x, y, button, pressed):
    global rmb_held

    if button == Button.right:
        if pressed and not rmb_held:
            rmb_held = True
            stop_event.clear()
            threading.Thread(target=spam_actions, daemon=True).start()
        elif not pressed:
            rmb_held = False
            stop_event.set()

# Start mouse listener
with MouseListener(on_click=on_click) as listener:
    listener.join()
