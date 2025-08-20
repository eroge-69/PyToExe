import time
import webbrowser
import pynput
from pynput import keyboard
from pynput.keyboard import Key, Controller, KeyCode
import random

def on_press(key):
    if key == KeyCode.from_char('w'):
        for i in range(random.randint(1,10)):
            time.sleep(random.randint(1,10))
            webbrowser.open_new('https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley')
    if key == KeyCode.from_char('a'):
        for i in range(random.randint(1,10)):
            time.sleep(random.randint(1,10))
            webbrowser.open_new('https://www.reddit.com/r/Minecraft/')
    if key == KeyCode.from_char('s'):
        for i in range(random.randint(1,10)):
            time.sleep(random.randint(1,10))
            webbrowser.open_new('https://minecraft.wiki/')
    if key == KeyCode.from_char('d'):
        for i in range(random.randint(1,5)):
            time.sleep(random.randint(1,10))
            webbrowser.open_new('https://www.youtube.com/watch?v=g9L9yxwyOY8')


while True:
    if __name__ == "__main__":
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
