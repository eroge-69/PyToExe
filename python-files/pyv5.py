import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import json
import os

# === CONFIG ===
SETTINGS_FILE = "timer_settings.json"
SESSION_FILE = "timer_session.json"
DEFAULT_FONT = "Consolas"
DEFAULT_SIZE = 40
DEFAULT_POS = (100, 100)
COLOR_RUNNING = "white"
COLOR_PAUSED = "red"
REFRESH_MS = 250

# === UTILITIES ===
def load_json(path, fallback):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            pass
    return fallback

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

# === FORMAT TIME ===
def format_time(secs, mode="down"):
    if secs < 0 and mode == "down":
        return "⏰ TIME IS UP!!!! ⏰"
    secs = max(0, int(secs))
    hrs, remainder = divmod(secs, 3600)
    mins, sec = divmod(remainder, 60)
    return f"{hrs:02}:{mins:02}:{sec:02}"

# === SETTINGS LOAD ===
settings = load_json(SETTINGS_FILE, {"font_size": DEFAULT_SIZE, "position": DEFAULT_POS})
current_size = settings.get("font_size", DEFAULT_SIZE)
start_x, start_y = settings.get("position", DEFAULT_POS)

# === GUI SETUP ===
root = tk.Tk()
root.withdraw()  # hide main window until setup is done

# === GUI STARTUP PROMPT ===
def show_start_dialog():
    dialog = tk.Toplevel()
    dialog.title("Start Timer")
    dialog.geometry("300x230")
    dialog.configure(bg="#1e1e1e")
    dialog.resizable(False, False)
    dialog.grab_set()

    from tkinter import ttk

    def style_button(button):
        button.configure(bg="#3a3a3a", fg="white", activebackground="#555", activeforeground="white", relief="flat")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TCombobox", fieldbackground="#2a2a2a", background="#2a2a2a", foreground="white")
    style.map("TCombobox", fieldbackground=[("readonly", "#2a2a2a")])

    tk.Label(dialog, text="Set Time:", bg="#1e1e1e", fg="white").pack(pady=(10, 0))

    selector_frame = tk.Frame(dialog, bg="#1e1e1e")
    selector_frame.pack()

    hours = tk.StringVar(value="0")
    minutes = tk.StringVar(value="0")
    seconds = tk.StringVar(value="0")

    hour_box = ttk.Combobox(selector_frame, textvariable=hours, values=[str(i) for i in range(24)], width=4, state="readonly")
    min_box = ttk.Combobox(selector_frame, textvariable=minutes, values=[str(i) for i in range(60)], width=4, state="readonly")
    sec_box = ttk.Combobox(selector_frame, textvariable=seconds, values=[str(i) for i in range(60)], width=4, state="readonly")

    hour_box.pack(side="left", padx=5, pady=10)
    tk.Label(selector_frame, text=":", fg="white", bg="#1e1e1e").pack(side="left")
    min_box.pack(side="left", padx=5)
    tk.Label(selector_frame, text=":", fg="white", bg="#1e1e1e").pack(side="left")
    sec_box.pack(side="left", padx=5)

    # Mode selection
    tk.Label(dialog, text="Count direction:", bg="#1e1e1e", fg="white").pack(pady=(10, 2))
    mode_var = tk.StringVar(value="down")
    mode_dropdown = ttk.Combobox(dialog, textvariable=mode_var, values=["down", "up"], state="readonly")
    mode_dropdown.pack()

    def on_start():
        try:
            h = int(hours.get())
            m = int(minutes.get())
            s = int(seconds.get())
            total_sec = h * 3600 + m * 60 + s
            if total_sec == 0:
                raise ValueError
            dialog.destroy()
            start_timer(total_sec, mode_var.get())
        except:
            messagebox.showerror("Invalid time", "Please select a time greater than 0.")

    def on_load():
        session = load_json(SESSION_FILE, None)
        if session:
            dialog.destroy()
            start_timer(session["current_time"], session["mode"], session["start_time"], session["paused"])
        else:
            messagebox.showerror("No session", "No saved session found!")

    # Buttons
    start_btn = tk.Button(dialog, text="▶ Start New", command=on_start)
    load_btn = tk.Button(dialog, text="🔁 Load Last", command=on_load)

    start_btn.pack(pady=(10, 5))
    load_btn.pack(pady=(0, 10))

    style_button(start_btn)
    style_button(load_btn)

# === START FUNCTION ===
def start_timer(init_time, mode, start_time=None, was_paused=False):
    global current_time, count_mode, paused, last_tick, START_TIME_SEC
    current_time = init_time
    START_TIME_SEC = start_time if start_time is not None else init_time
    count_mode = mode
    paused = was_paused
    last_tick = time.time()
    build_main_ui()

# === MAIN TIMER WINDOW ===
def build_main_ui():
    root.deiconify()
    root.title("Floating Timer")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "black")
    root.configure(bg="black")

    global label
    label = tk.Label(root, text="", font=(DEFAULT_FONT, current_size, "bold"), fg=COLOR_RUNNING, bg="black")
    label.pack()

    root.geometry(f"+{start_x}+{start_y}")
    update_text()

# === MOVEMENT ===
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")
    save_json(SETTINGS_FILE, {"font_size": current_size, "position": (x, y)})

# === UPDATE LOOP ===
def update_text():
    global current_time, last_tick
    now = time.time()
    if not paused:
        delta = now - last_tick
        current_time += delta if count_mode == "up" else -delta
    last_tick = now

    label.config(text=format_time(current_time, count_mode))
    label.config(fg=COLOR_PAUSED if paused else COLOR_RUNNING)

    save_json(SESSION_FILE, {
        "current_time": current_time,
        "start_time": START_TIME_SEC,
        "mode": count_mode,
        "paused": paused
    })

    root.after(REFRESH_MS, update_text)

# === FONT SIZE CONTROL ===
def increase_font(event=None):
    global current_size
    current_size += 2
    label.config(font=(DEFAULT_FONT, current_size, "bold"))
    save_json(SETTINGS_FILE, {"font_size": current_size, "position": (root.winfo_x(), root.winfo_y())})

def decrease_font(event=None):
    global current_size
    current_size = max(6, current_size - 2)
    label.config(font=(DEFAULT_FONT, current_size, "bold"))
    save_json(SETTINGS_FILE, {"font_size": current_size, "position": (root.winfo_x(), root.winfo_y())})

# === PAUSE & RESET ===
def pause_timer(event=None):
    global paused
    paused = not paused

def reset_timer(event=None):
    global current_time, paused, last_tick
    paused = False
    last_tick = time.time()
    current_time = START_TIME_SEC if count_mode == "down" else 0

# === KEYBINDS & DRAG ===
root.bind("+", increase_font)
root.bind("_", decrease_font)
root.bind("(", pause_timer)
root.bind(")", reset_timer)

# Movement
label = tk.Label()  # placeholder so bind doesn't crash
label.bind("<Button-1>", start_move)
label.bind("<B1-Motion>", do_move)

# === INIT ===
show_start_dialog()
root.mainloop()
