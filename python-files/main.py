import keyboard
import threading
import time

sending = False

def space_repeat():
    while sending:
        keyboard.press_and_release('space')
        time.sleep(0.02)

def space_down(e):
    global sending
    if not sending:
        sending = True
        threading.Thread(target=space_repeat, daemon=True).start()

def space_up(e):
    global sending
    sending = False

keyboard.on_press_key('space', space_down)
keyboard.on_release_key('space', space_up)

keyboard.wait('p')