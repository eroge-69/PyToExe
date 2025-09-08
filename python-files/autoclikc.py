from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import time

mouse = Controller()
clicking = False
delay = 0.001  # 1ms = ~1000 clickssec

def click_mouse()
    while True
        if clicking
            mouse.click(Button.left)
            time.sleep(delay)

def on_press(key)
    global clicking
    try
        if key.char == 's'
            clicking = True
        elif key.char == 'e'
            clicking = False
    except AttributeError
        pass

def on_release(key)
    if key == keyboard.Key.esc
        return False

click_thread = threading.Thread(target=click_mouse)
click_thread.daemon = True
click_thread.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener
    listener.join()
