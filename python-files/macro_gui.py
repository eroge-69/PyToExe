import tkinter as tk
from tkinter import messagebox
from pynput import mouse, keyboard
import pyautogui
import time
import json
import threading

recorded = []
recording = False
start_time = None
mouse_listener = None
keyboard_listener = None

def on_move(x, y):
    if recording:
        recorded.append(('move', time.time() - start_time, x, y))

def on_click(x, y, button, pressed):
    if pressed and recording:
        recorded.append(('click', time.time() - start_time, x, y, str(button)))

def on_press(key):
    if recording:
        try:
            recorded.append(('key', time.time() - start_time, key.char))
        except AttributeError:
            recorded.append(('key', time.time() - start_time, str(key)))

def start_recording():
    global recorded, recording, start_time, mouse_listener, keyboard_listener
    if recording:
        messagebox.showinfo("Already Recording", "Recording is already in progress.")
        return
    recorded = []
    start_time = time.time()
    recording = True
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener.start()
    keyboard_listener.start()
    status_label.config(text="Recording... Press ESC to stop.")

def on_release(key):
    if key == keyboard.Key.esc:
        stop_recording()
        return False  # Stop keyboard listener

def stop_recording():
    global recording, mouse_listener, keyboard_listener
    if not recording:
        status_label.config(text="Not currently recording.")
        return
    recording = False
    if mouse_listener:
        mouse_listener.stop()
    if keyboard_listener:
        keyboard_listener.stop()
    status_label.config(text=f"Recording stopped ({len(recorded)} actions)")

def save_macro():
    if not recorded:
        messagebox.showwarning("No Macro", "No macro recorded to save.")
        return
    try:
        with open("macro.json", "w") as f:
            json.dump(recorded, f)
        status_label.config(text="Macro saved as macro.json")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save macro:\n{e}")

def smooth_move(prev_pos, next_pos, duration):
    if duration <= 0:
        pyautogui.moveTo(*next_pos)
        return
    steps = max(int(duration / 0.01), 1)
    x0, y0 = prev_pos
    x1, y1 = next_pos
    for i in range(1, steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = y0 + (y1 - y0) * i / steps
        pyautogui.moveTo(x, y)
        time.sleep(duration / steps)

def play_macro():
    try:
        with open("macro.json", "r") as f:
            macro = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Not Found", "macro.json not found.")
        return
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load macro:\n{e}")
        return

    status_label.config(text="Playing back macro...")

    def playback():
        prev_time = 0
        prev_pos = None
        for action in macro:
            action_type = action[0]
            timestamp = action[1]
            delay = timestamp - prev_time
            if delay > 0:
                time.sleep(delay)
            prev_time = timestamp

            if action_type == 'move':
                _, _, x, y = action
                if prev_pos is not None:
                    smooth_move(prev_pos, (x, y), delay)
                else:
                    pyautogui.moveTo(x, y)
                prev_pos = (x, y)
            elif action_type == 'click':
                _, _, x, y, button = action
                # pyautogui.click supports button='left', 'right', 'middle'
                btn = button.lower().replace('button.', '')
                pyautogui.click(x, y, button=btn)
            elif action_type == 'key':
                _, _, key = action
                # Clean key string for pyautogui.press
                key_str = str(key).replace("'", "").replace("Key.", "")
                try:
                    pyautogui.press(key_str)
                except Exception:
                    # Some keys may not be supported, skip silently
                    pass
        status_label.config(text="Macro playback complete.")

    threading.Thread(target=playback).start()

# GUI Setup
root = tk.Tk()
root.title("Macro Recorder")
root.geometry("320x280")

tk.Label(root, text="Macro Recorder", font=("Helvetica", 16)).pack(pady=10)

tk.Button(root, text="Start Recording", width=25, command=start_recording).pack(pady=5)
tk.Button(root, text="Save Macro", width=25, command=save_macro).pack(pady=5)
tk.Button(root, text="Play Macro", width=25, command=play_macro).pack(pady=5)

status_label = tk.Label(root, text="Idle", fg="blue")
status_label.pack(pady=20)

root.mainloop()
