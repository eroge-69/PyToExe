import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
from pynput import mouse
import threading
import time
import pygetwindow as gw

# Store mappings as a list of tuples: (original, desired)
mappings = []

# Currently selected window title
selected_window = None

# Keep track of pressed keys
active_keys = set()

# GUI Input state
waiting_for = None
waiting_entry = None

def get_active_windows():
    """Return a list of active window titles."""
    titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
    return list(dict.fromkeys(titles))  # remove duplicates, keep order

def is_target_window_active():
    """Check if selected window is currently focused."""
    if not selected_window:
        return False
    try:
        win = gw.getActiveWindow()
        return win and selected_window.lower() in win.title.lower()
    except:
        return False

def listen_mouse():
    """Mouse listener thread."""
    def on_click(x, y, button, pressed):
        btn = str(button).lower()
        # Check if mapped
        for og, ds in mappings:
            if ds == btn:
                if is_target_window_active():
                    if pressed and og not in active_keys:
                        keyboard.press(og)
                        active_keys.add(og)
                    elif not pressed and og in active_keys:
                        keyboard.release(og)
                        active_keys.remove(og)
    listener = mouse.Listener(on_click=on_click)
    listener.start()

def listen_keyboard():
    """Keyboard listener thread for remapped inputs."""
    while True:
        if selected_window and is_target_window_active():
            for og, ds in mappings:
                if keyboard.is_pressed(ds) and og not in active_keys:
                    keyboard.press(og)
                    active_keys.add(og)
                elif not keyboard.is_pressed(ds) and og in active_keys:
                    keyboard.release(og)
                    active_keys.remove(og)
        time.sleep(0.05)

def start_mapping():
    global selected_window
    selected_window = window_var.get()
    if not selected_window:
        messagebox.showerror("Error", "Please select a window first.")
        return
    if not mappings:
        messagebox.showerror("Error", "Please add at least one mapping.")
        return
    messagebox.showinfo("Started", f"Mappings active only in: {selected_window}")
    threading.Thread(target=listen_mouse, daemon=True).start()
    threading.Thread(target=listen_keyboard, daemon=True).start()

def capture_input(entry, label):
    """Wait for next input (mouse or keyboard)."""
    global waiting_for, waiting_entry
    waiting_for = label
    waiting_entry = entry
    entry.delete(0, tk.END)
    entry.insert(0, f"Press any key/mouse...")

    def on_key(e):
        global waiting_for, waiting_entry
        if waiting_for:
            key_name = e.name.lower()
            waiting_entry.delete(0, tk.END)
            waiting_entry.insert(0, key_name)
            waiting_for = None
            waiting_entry = None
            keyboard.unhook_all()

    def on_mouse(x, y, button, pressed):
        global waiting_for, waiting_entry
        if pressed and waiting_for:
            btn_name = str(button).lower()
            waiting_entry.delete(0, tk.END)
            waiting_entry.insert(0, btn_name)
            waiting_for = None
            waiting_entry = None
            return False  # stop listener

    keyboard.hook(on_key)
    threading.Thread(target=lambda: mouse.Listener(on_click=on_mouse).run(), daemon=True).start()

def save_mapping():
    """Save the current 2x2 grid into mappings."""
    global mappings
    og = og_entry.get().strip().lower()
    ds = ds_entry.get().strip().lower()
    if not og or not ds:
        messagebox.showerror("Error", "Both inputs must be set.")
        return
    mappings.append((og, ds))
    mapping_list.insert(tk.END, f"{ds} → {og}")
    og_entry.delete(0, tk.END)
    ds_entry.delete(0, tk.END)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Custom Input Mapper for RAGE")

# Window selector
frame_top = tk.Frame(root)
frame_top.pack(pady=5)

window_var = tk.StringVar()
window_dropdown = ttk.Combobox(frame_top, textvariable=window_var, width=50)
window_dropdown.pack(side=tk.LEFT, padx=5)

def refresh_windows():
    window_dropdown['values'] = get_active_windows()
    if not window_dropdown.get() and window_dropdown['values']:
        window_dropdown.current(0)

refresh_btn = tk.Button(frame_top, text="Refresh Windows", command=refresh_windows)
refresh_btn.pack(side=tk.LEFT)

# Mapping section
frame_map = tk.Frame(root)
frame_map.pack(pady=10)

tk.Label(frame_map, text="Original Input").grid(row=0, column=0, padx=10)
tk.Label(frame_map, text="Desired Input").grid(row=0, column=1, padx=10)

og_entry = tk.Entry(frame_map, width=20)
og_entry.grid(row=1, column=0, padx=5)
og_btn = tk.Button(frame_map, text="Set", command=lambda: capture_input(og_entry, "og"))
og_btn.grid(row=1, column=0, sticky="e")

ds_entry = tk.Entry(frame_map, width=20)
ds_entry.grid(row=1, column=1, padx=5)
ds_btn = tk.Button(frame_map, text="Set", command=lambda: capture_input(ds_entry, "ds"))
ds_btn.grid(row=1, column=1, sticky="e")

save_btn = tk.Button(root, text="Add Mapping", command=save_mapping)
save_btn.pack(pady=5)

mapping_list = tk.Listbox(root, width=50)
mapping_list.pack(pady=5)

start_btn = tk.Button(root, text="Start Mapping", command=start_mapping, bg="lightgreen")
start_btn.pack(pady=10)

root.mainloop()
