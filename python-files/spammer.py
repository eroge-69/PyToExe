import threading
import time
import keyboard  # pip install keyboard
from pynput.keyboard import Controller as KeyController
from pynput.mouse import Controller as MouseController, Button

# Controllers
key_controller = KeyController()
mouse_controller = MouseController()

# Settings
key1 = '1'   # first key to press
key2 = '2'   # second key to press
delay = 0.1  # seconds between actions

running = False
stop_thread = False

def spam_loop():
    global running, stop_thread
    while not stop_thread:
        if running:
            key_controller.press(key1)
            key_controller.release(key1)

            key_controller.press(key2)
            key_controller.release(key2)

            mouse_controller.click(Button.left, 1)

            time.sleep(delay)
        else:
            time.sleep(0.1)  # idle

def toggle_spam():
    global running
    running = not running
    print("Spammer", "ON" if running else "OFF")

def main():
    global stop_thread
    # Start spamming thread
    t = threading.Thread(target=spam_loop)
    t.daemon = True
    t.start()

    print("Press F8 to toggle spammer ON/OFF. Press ESC to quit.")
    keyboard.add_hotkey("F8", toggle_spam)

    # Wait until ESC pressed
    keyboard.wait("esc")
    stop_thread = True
    print("Exiting...")

if __name__ == "__main__":
    main()
