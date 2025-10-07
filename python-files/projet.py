from pynput import keyboard 

recorded_keys = []

def on_press(key):
    print(f"Key pressed: {key}")
    try:
        recorded_keys.append(key.char)
    except AttributeError:
        recorded_keys.append(str(key))

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press==on_press, on_release=on_release) as listener:
    listener.join()
    
print("rec:", recorded_keys)