import time
import threading
from pynput.mouse import Controller, Button
from pynput import keyboard

TOGGLE_KEY = keyboard.KeyCode(char='r')  # R tuşu
clicking = False
mouse = Controller()

pressed_keys = set()

def clicker():
    global clicking
    current_cps = 5
    target_cps = 15

    while True:
        if clicking:
            if current_cps < target_cps:
                current_cps += 1
                if current_cps > target_cps:
                    current_cps = target_cps
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(1 / current_cps)
        else:
            current_cps = 5
            time.sleep(0.05)

def on_press(key):
    global clicking

    pressed_keys.add(key)

    # R tuşuna basılırsa çalıştır
    if key == TOGGLE_KEY:
        clicking = not clicking
        print("Tıklama açık!" if clicking else "Tıklama kapalı!")

def on_release(key):
    try:
        pressed_keys.remove(key)
    except KeyError:
        pass

click_thread = threading.Thread(target=clicker)
click_thread.daemon = True
click_thread.start()

print("AutoClicker başlatıldı! [R] ile aç/kapa.")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
