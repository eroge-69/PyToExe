import webbrowser
import time
import keyboard

buffer = ""

def process_scanned(data):
    if data.startswith("http://") or data.startswith("https://"):
        webbrowser.open(data)

while True:
    event = keyboard.read_event(suppress=False)
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == "enter":   # Scanner usually sends Enter at end
            process_scanned(buffer.strip())
            buffer = ""
        else:
            buffer += event.name if len(event.name) == 1 else ""
