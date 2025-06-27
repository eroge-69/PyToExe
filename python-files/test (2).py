import time
import threading
from pynput.keyboard import Controller
import keyboard

keyboard_controller = Controller()
spamming = False

def spam_e():
    global spamming
    while spamming:
        keyboard_controller.press('e')
        keyboard_controller.release('e')
        time.sleep(0.05)  # adjust speed if needed

def start_spam():
    global spamming
    if not spamming:
        spamming = True
        threading.Thread(target=spam_e).start()
        print("Started spamming 'E'")

def stop_spam():
    global spamming
    spamming = False
    print("Stopped spamming 'E'")

keyboard.add_hotkey('F6', start_spam)
keyboard.add_hotkey('F7', stop_spam)

print("Press F6 to START spamming 'E'")
print("Press F7 to STOP")
print("Press ESC to quit")

keyboard.wait('esc')
