import threading
from pynput import keyboard, mouse
import time

mouse_controller = mouse.Controller()
clicking = False

def on_press(key):
    global clicking
    try:
        if key.char == 'e':
            clicking = True
        elif key.char == 'd':
            clicking = False
    except:
        pass

def auto_clicker():
    while True:
        if clicking:
            mouse_controller.click(mouse.Button.left, 1)
            time.sleep(0.1)
        else:
            time.sleep(0.1)

def listen_for_keys():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

key_listener_thread = threading.Thread(target=listen_for_keys)
key_listener_thread.daemon = True
key_listener_thread.start()
auto_clicker()