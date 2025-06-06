from pynput import keyboard

def on_press(key):
    try:
        print(f"{key.char} дарагдлаа")
    except AttributeError:
        print(f"{key} дарагдлаа: {key}")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()