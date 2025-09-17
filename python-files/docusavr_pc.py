#!/usr/bin/env python3
"""
DocuSavr PC version
- Logs keystrokes to ~/Save.txt (or %USERPROFILE%\Save.txt on Windows)
- Special combos:
    Delete + a  -> clears Save.txt
    a + b + c   -> create a timestamped backup in DocuSavr_backups and open that folder
"""

import os
import sys
import threading
import time
from datetime import datetime
import shutil
import subprocess
from pynput import keyboard

HOME = os.path.expanduser("~")
SAVE_FILE = os.path.join(HOME, "Save.txt")
BACKUP_DIR = os.path.join(HOME, "DocuSavr_backups")

# Buffer settings
BUFFER_FLUSH_COUNT = 50      # flush when buffer reaches this many chars
BUFFER_FLUSH_INTERVAL = 5.0  # flush at least every N seconds

buffer_lock = threading.Lock()
buffer = []
last_flush = time.time()

# To track currently pressed keys for combo detection
current_keys = set()

# Define combos (lowercase letters for character keys)
STORAGE_COMBO = {"a", "b", "c"}        # create backup + open folder
CLEAR_COMBO = {"delete", "a"}          # clear Save.txt; note: 'delete' or 'backspace' handled below

# helper: ensure directories/files exist
os.makedirs(BACKUP_DIR, exist_ok=True)
open(SAVE_FILE, "a").close()  # touch file

def flush_buffer():
    """Write buffer contents to SAVE_FILE safely."""
    global last_flush
    with buffer_lock:
        if not buffer:
            return
        try:
            with open(SAVE_FILE, "a", encoding="utf-8") as f:
                f.write("".join(buffer))
            buffer.clear()
            last_flush = time.time()
        except Exception as e:
            print("Error writing buffer:", e, file=sys.stderr)

def periodic_flush_loop():
    """Background thread to flush buffer periodically."""
    while True:
        time.sleep(1.0)
        if time.time() - last_flush >= BUFFER_FLUSH_INTERVAL:
            flush_buffer()

def make_backup_and_open():
    """Create a timestamped backup of Save.txt and open the folder for the user."""
    flush_buffer()
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"Save_{timestamp}.txt"
        dest = os.path.join(BACKUP_DIR, backup_name)
        shutil.copy2(SAVE_FILE, dest)
        print(f"[DocuSavr] Backup created: {dest}")
        # Open folder in file manager
        if sys.platform == "win32":
            os.startfile(BACKUP_DIR)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", BACKUP_DIR])
        else:
            # Linux / XDG
            subprocess.Popen(["xdg-open", BACKUP_DIR])
    except Exception as e:
        print("Backup/open failed:", e, file=sys.stderr)

def clear_save_file():
    """Overwrite the save file with empty content."""
    with buffer_lock:
        buffer.clear()
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                f.write("")
            print("[DocuSavr] Save.txt cleared.")
        except Exception as e:
            print("Failed to clear Save.txt:", e, file=sys.stderr)

def key_to_string(key):
    """Convert a pynput key to a reasonable string for logging."""
    try:
        # normal character keys
        if hasattr(key, "char") and key.char is not None:
            return key.char
    except Exception:
        pass

    # special keys mapping
    name = str(key).replace("Key.", "").lower()
    mapping = {
        "space": " ",
        "enter": "\n",
        "tab": "\t",
        "backspace": "[BACKSPACE]",
        "delete": "[DELETE]",
        "esc": "[ESC]",
        "shift": "[SHIFT]",
        "shift_r": "[SHIFT]",
        "ctrl": "[CTRL]",
        "alt": "[ALT]",
        "caps_lock": "[CAPSLOCK]",
        "up": "[UP]",
        "down": "[DOWN]",
        "left": "[LEFT]",
        "right": "[RIGHT]"
    }
    return mapping.get(name, f"[{name.upper()}]")

def on_press(key):
    """Callback for key press events."""
    # update current_keys for combo detection
    key_name = None
    try:
        if hasattr(key, "char") and key.char is not None:
            key_name = key.char.lower()
        else:
            key_name = str(key).replace("Key.", "").lower()
    except Exception:
        key_name = str(key).lower()

    current_keys.add(key_name)

    # Detect clear combo: 'delete' or 'backspace' + 'a'
    # Accept either 'delete' or 'backspace' as delete trigger
    # Note: current_keys contains both string names and chars
    delete_present = ("delete" in current_keys) or ("backspace" in current_keys)
    if delete_present and "a" in current_keys:
        clear_save_file()
        return

    # Detect storage combo: a + b + c simultaneously
    if STORAGE_COMBO.issubset({k for k in current_keys if len(k)==1}):
        make_backup_and_open()
        return

    # Add to buffer
    s = key_to_string(key)
    with buffer_lock:
        buffer.append(s)
        if len(buffer) >= BUFFER_FLUSH_COUNT:
            flush_buffer()

def on_release(key):
    """Callback for key release events - remove from current keys."""
    try:
        if hasattr(key, "char") and key.char is not None:
            k = key.char.lower()
        else:
            k = str(key).replace("Key.", "").lower()
    except Exception:
        k = str(key).lower()

    # remove key from set if present
    if k in current_keys:
        current_keys.discard(k)

def main():
    # start the periodic flush thread
    t = threading.Thread(target=periodic_flush_loop, daemon=True)
    t.start()
    print("[DocuSavr] Running. Logging to:", SAVE_FILE)
    print("[DocuSavr] Special combos: Delete + A clears file. A + B + C creates a backup and opens folder.")
    # start listening
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[DocuSavr] Exiting. Flushing buffer...")
        flush_buffer()
        sys.exit(0)
