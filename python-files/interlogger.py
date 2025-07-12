from pynput import keyboard
from datetime import datetime
import os

# File paths
base_path = os.path.dirname(os.path.abspath(__file__))
wordlist_file = os.path.join(base_path, "wordlist.txt")
log_file = os.path.join(base_path, "wordlog.txt")

# Load target words
with open(wordlist_file, "r") as f:
    target_words = set(word.strip().lower() for word in f if word.strip())

typed_chars = ""

def on_press(key):
    global typed_chars
    try:
        if hasattr(key, 'char') and key.char is not None:
            typed_chars += key.char.lower()

            if len(typed_chars) > 100:
                typed_chars = typed_chars[-100:]

            for word in target_words:
                if word in typed_chars:
                    log_word(word)
                    # remove to prevent repeat triggers in long buffer
                    typed_chars = typed_chars.replace(word, "")
        elif key == keyboard.Key.backspace:
            typed_chars = typed_chars[:-1]
    except Exception:
        pass

def log_word(word):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_line = f"[{now}] {word}"

    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write(f"{entry_line} (1)\n")
        return

    with open(log_file, "r") as f:
        lines = f.readlines()

    found = False
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith(entry_line):
            # Line exists, update count
            if "(" in line and line.endswith(")"):
                count_part = line.split("(")[-1].replace(")", "")
                try:
                    count = int(count_part)
                    count += 1
                    lines[i] = f"{entry_line} ({count})\n"
                    found = True
                    break
                except ValueError:
                    pass

    if not found:
        lines.append(f"{entry_line} (1)\n")

    with open(log_file, "w") as f:
        f.writelines(lines)

    print(f"Logged: {word}")

def on_release(key):
    if key == keyboard.Key.esc:
        return False  # Stop the listener

if __name__ == "__main__":
    print("Monitoring input... Press ESC to stop.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
