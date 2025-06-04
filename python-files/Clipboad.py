import pyperclip
import keyboard
import time
import threading

clipboard_history = []

def on_copy():
    global clipboard_history
    time.sleep(0.05)  # Give time for clipboard to update
    content = pyperclip.paste()
    if content and (len(clipboard_history) == 0 or content != clipboard_history[0]):
        clipboard_history.insert(0, content)  # Add to top

def on_paste():
    global clipboard_history
    if clipboard_history:
        text_to_paste = clipboard_history.pop(0)  # Get latest
        pyperclip.copy(text_to_paste)  # Set clipboard to it
        keyboard.send('ctrl+v')  # Trigger normal paste
        time.sleep(0.05)
        pyperclip.copy('')  # Clear clipboard to prevent reuse

def monitor_keys():
    keyboard.add_hotkey('ctrl+c', on_copy)
    keyboard.add_hotkey('ctrl+v', on_paste)
    print("Clipboard monitor started. Press ESC to stop.")
    keyboard.wait('esc')

if __name__ == '__main__':
    monitor_keys()
