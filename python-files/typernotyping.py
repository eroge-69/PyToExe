import keyboard
import time
from pynput.keyboard import Key, Controller
key = Controller()
while True:
    key.type("hi there")
    time.sleep("0.1")
    key.press(key.enter)
    time.sleep("0.1")
    key.release(key.enter)
    time.sleep("0.1")