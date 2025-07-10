from pynput import keyboard
import threading
import traceback
import os

log_file = 'last_key.log'

def on_press(key):
    try:
        print(f"Key pressed: {key}")
        with open(log_file, 'w') as f:
            f.write(str(key.char))
    except AttributeError:
        print(f"Special key pressed: {key}")
        with open(log_file, 'w') as f:
            f.write(str(key))
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

def on_release(key):
    pass

def start_listener():
    try:
        print("Starting listener...")
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

# Start the listener in a separate thread
thread = threading.Thread(target=start_listener)
thread.daemon = True
thread.start()

print("Script is running. Press Enter to exit...")
input()  # Keep the main thread alive
