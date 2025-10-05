"""
Alarm20 - 20-session alarm app
Features:
- 20 alarms with time (HH:MM) + AM/PM selector
- Assign a different MP3 to each alarm (copied to app folder)
- Test individual alarm sound
- Save/load config in %APPDATA%\Alarm20\config.json
- Auto-start on user login (creates .bat in Startup folder) - toggleable
- Start/Stop alarm checking, global Stop to immediately stop playback
- Uses pygame for MP3 playback and tkinter for GUI
"""

import os
import sys
import json
import shutil
import threading
import time
from datetime import datetime, date
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame

# ---------- Initialization ----------
pygame.mixer.init()

APP_NAME = "Alarm20"
APPDATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
SOUNDS_DIR = os.path.join(APPDATA, "sounds")
CONFIG_PATH = os.path.join(APPDATA, "config.json")
STARTUP_FOLDER = os.path.join(os.environ.get("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
STARTUP_BAT = os.path.join(STARTUP_FOLDER, f"{APP_NAME}_starter.bat")

if not os.path.exists(SOUNDS_DIR):
    os.makedirs(SOUNDS_DIR, exist_ok=True)

# ---------- State ----------
alarms = []  # list of dicts {time: "HH:MM", ampm: "AM"/"PM", sound: "filename.mp3"}
running = False
triggered_today = set()  # keep track of which alarm indices triggered today
current_playing = None
lock = threading.Lock()

# ---------- Helper functions ----------
def to_24h(time_str, ampm):
    """Convert HH:MM + AM/PM to 24-hour 'HH:MM' string. If input already 24-hr like '14:30' and ampm None, return as is."""
    try:
        hh, mm = map(int, time_str.split(":"))
    except Exception:
        return None
    if ampm is None:
        return f"{hh:02d}:{mm:02d}"
    ampm = ampm.upper()
    if ampm == "AM":
        if hh == 12:
            hh = 0
    else:  # PM
        if hh != 12:
            hh += 12
    return f"{hh:02d}:{mm:02d}"

def copy_sound_and_get_name(src_path, alarm_index):
    """Copy the chosen mp3 to the app sounds folder and return the stored filename (unique)."""
    if not src_path:
        return None
    if not os.path.exists(src_path):
        return None
    _, ext = os.path.splitext(src_path)
    ext = ext.lower()
    if ext not in (".mp3", ".wav", ".ogg"):
        messagebox.showerror("Invalid file", "Please select an mp3/wav/ogg file.")
        return None
    base_name = f"alarm{alarm_index+1}{ext}"
    dest = os.path.join(SOUNDS_DIR, base_name)
    # if a file with same name exists, make unique by timestamp
    if os.path.exists(dest):
        timestamp = int(time.time())
        base_name = f"alarm{alarm_index+1}_{timestamp}{ext}"
        dest = os.path.join(SOUNDS_DIR, base_name)
    shutil.copy2(src_path, dest)
    return base_name

def play_sound_file(filename):
    """Play a sound file from the sounds folder."""
    global current_playing
    if not filename:
        return
    full = os.path.join(SOUNDS_DIR, filename)
    if not os.path.exists(full):
        messagebox.showerror("Missing file", f"Sound file not found: {full}")
        return
    try:
        with lock:
            pygame.mixer.music.load(full)
            pygame.mixer.music.play()
            current_playing = full
    except Exception as e:
        messagebox.showerror("Playback error", str(e))

def stop_playback():
    global current_playing
    with lock:
        pygame.mixer.music.stop()
        current_playing = None

def save_config():
    data = {"alarms": alarms, "autostart": autostart_var.get()}
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", f"Configuration saved to:\n{CONFIG_PATH}")
    except Exception as e:
        messagebox.showerror("Save error", str(e))

def load_config():
    global alarms
    if not os.path.exists(CONFIG_PATH):
        return
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        loaded = data.get("alarms", [])
        # ensure length 20
        alarms = []
        for i in range(20):
            if i < len(loaded):
                alarms.append(loaded[i])
            else:
                alarms.append({"time": "", "ampm": "AM", "sound": ""})
        autostart_var.set(bool(data.get("autostart", False)))
        refresh_ui_from_alarms()
    except Exception as e:
        messagebox.showerror("Load error", str(e))

def ensure_default_alarms():
    global alarms
    if not alarms or len(alarms) != 20:
        alarms = []
        for i in range(20):
            alarms.append({"time": "", "ampm": "AM", "sound": ""})

def add_to_startup(enable):
    """Create or remove a .bat in the Startup folder that starts the exe (or python script) on login."""
    try:
        if enable:
            exe_path = getattr(sys, 'frozen', None)
            if exe_path:
                # running as frozen exe, sys.executable is exe
                exe_path = sys.executable
            else:
                # running as script; make it call python with this script path
                exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            cmd = f'start "" {exe_path}\n'
            with open(STARTUP_BAT, "w", encoding="utf-8") as f:
                f.write(cmd)
        else:
            if os.path.exists(STARTUP_BAT):
                os.remove(STARTUP_BAT)
    except Exception as e:
        messagebox.showerror("Startup error", str(e))

def is_startup_enabled():
    return os.path.exists(STARTUP_BAT)

# ---------- Alarm checking thread ----------
def alarm_thread():
    global running, triggered_today
    triggered_today = set()
    while running:
        now_dt = datetime.now()
        now_str = now_dt.strftime("%H:%M")
        # reset at local midnight
        if now_dt.hour == 0 and now_dt.minute == 0:
            triggered_today = set()
        for idx, a in enumerate(alarms):
            t = a.get("time", "").strip()
            ampm = a.get("ampm", "AM")
            if not t:
                continue
            target = to_24h(t, ampm)
            if not target:
                continue
            if target == now_str and idx not in triggered_today:
                filename = a.get("sound", "")
                if filename:
                    play_sound_file(filename)
                triggered_today.add(idx)
                # prevent retrigger in same minute
                time.sleep(60)
        time.sleep(5)

# ---------- GUI and UI helpers ----------
root = tk.Tk()
root.title("20 Session Alarm - Alarm20")
root.geometry("680x720")
root.resizable(False, False)

# top frame with buttons
top_frame = tk.Frame(root)
top_frame.pack(pady=6)

start_btn = tk.Button(top_frame, text="Start Alarms", width=14, bg="#2ecc71")
stop_btn = tk.Button(top_frame, text="Stop Alarms", width=14, bg="#e74c3c")
save_btn = tk.Button(top_frame, text="Save Settings", width=12)
load_btn = tk.Button(top_frame, text="Load Settings", width=12)
startup_btn = tk.Button(top_frame, text="Apply Autostart", width=12)

start_btn.grid(row=0, column=0, padx=6)
stop_btn.grid(row=0, column=1, padx=6)
save_btn.grid(row=0, column=2, padx=6)
load_btn.grid(row=0, column=3, padx=6)
startup_btn.grid(row=0, column=4, padx=6)

middle_frame = tk.Frame(root)
middle_frame.pack(pady=4, fill="both", expand=True)

# header labels
hdr = ["#", "Time (HH:MM)", "AM/PM", "Sound file", "Select", "Test"]
for c, text in enumerate(hdr):
    tk.Label(middle_frame, text=text, font=("Arial", 9, "bold")).grid(row=0, column=c, padx=4, pady=2)

entries_time = []
entries_ampm = []
labels_sound = []
buttons_select = []
buttons_test = []

def select_sound_for(i):
    path = filedialog.askopenfilename(title=f"Select sound for alarm {i+1}", filetypes=[("Audio files","*.mp3;*.wav;*.ogg")])
    if path:
        newname = copy_sound_and_get_name(path, i)
        if newname:
            alarms[i]["sound"] = newname
            labels_sound[i].config(text=newname)

def test_sound_for(i):
    fname = alarms[i].get("sound", "")
    if not fname:
        messagebox.showwarning("No sound", f"No sound assigned for alarm {i+1}")
        return
    play_sound_file(fname)

# populate 20 rows
for i in range(20):
    tk.Label(middle_frame, text=f"{i+1:02d}").grid(row=i+1, column=0, padx=4, pady=2)
    e_time = tk.Entry(middle_frame, width=12)
    e_time.grid(row=i+1, column=1)
    var_ampm = tk.StringVar(value="AM")
    om = tk.OptionMenu(middle_frame, var_ampm, "AM", "PM")
    om.config(width=5)
    om.grid(row=i+1, column=2)
    lbl_sound = tk.Label(middle_frame, text="", width=28, anchor="w")
    lbl_sound.grid(row=i+1, column=3, padx=4)
    btn_sel = tk.Button(middle_frame, text="Select...", command=lambda idx=i: select_sound_for(idx))
    btn_sel.grid(row=i+1, column=4, padx=4)
    btn_test = tk.Button(middle_frame, text="Test", command=lambda idx=i: test_sound_for(idx))
    btn_test.grid(row=i+1, column=5, padx=4)

    entries_time.append(e_time)
    entries_ampm.append(var_ampm)
    labels_sound.append(lbl_sound)
    buttons_select.append(btn_sel)
    buttons_test.append(btn_test)

# bottom controls
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=8)

autostart_var = tk.BooleanVar(value=is_startup_enabled())
chk_autostart = tk.Checkbutton(bottom_frame, text="Auto-start on Windows login", var=autostart_var)
chk_autostart.grid(row=0, column=0, padx=6)

test_all_btn = tk.Button(bottom_frame, text="Test All Sounds", width=14)
stop_play_btn = tk.Button(bottom_frame, text="Stop Playing Now", width=16, bg="#f44336", fg="white")
status_label = tk.Label(bottom_frame, text="Status: Stopped", fg="gray")
test_all_btn.grid(row=0, column=1, padx=6)
stop_play_btn.grid(row=0, column=2, padx=6)
status_label.grid(row=0, column=3, padx=10)

# ---------- UI actions ----------
def refresh_alarms_from_ui():
    for i in range(20):
        alarms[i]["time"] = entries_time[i].get().strip()
        alarms[i]["ampm"] = entries_ampm[i].get()
        # alarms[i]["sound"] remains as assigned via select (or blank)

def refresh_ui_from_alarms():
    for i in range(20):
        entries_time[i].delete(0, "end")
        entries_time[i].insert(0, alarms[i].get("time", ""))
        entries_ampm[i].set(alarms[i].get("ampm", "AM"))
        labels_sound[i].config(text=alarms[i].get("sound", ""))

def start_alarms_action():
    global running, alarm_thread_obj
    refresh_alarms_from_ui()
    # validate times
    any_valid = False
    for a in alarms:
        if a.get("time", "").strip():
            any_valid = True
            if not to_24h(a["time"], a.get("ampm", "AM")):
                messagebox.showerror("Invalid time", f"Invalid time format: {a['time']}\nUse HH:MM (e.g. 09:30).")
                return
    if not any_valid:
        messagebox.showerror("No alarms", "Please set at least one alarm time.")
        return
    if not any(a.get("sound") for a in alarms):
        if not messagebox.askyesno("No sounds assigned", "No sound assigned to any alarm. Continue without sounds?"):
            return
    if running:
        messagebox.showinfo("Already running", "Alarms are already running.")
        return
    running = True
    status_label.config(text="Status: Running", fg="green")
    alarm_thread_obj = threading.Thread(target=alarm_thread, daemon=True)
    alarm_thread_obj.start()

def stop_alarms_action():
    global running
    running = False
    stop_playback()
    status_label.config(text="Status: Stopped", fg="gray")
    messagebox.showinfo("Stopped", "Alarms stopped.")

def save_action():
    refresh_alarms_from_ui()
    save_config()
    # apply autostart immediately if checked
    add_to_startup(autostart_var.get())

def load_action():
    load_config()
    messagebox.showinfo("Loaded", "Configuration loaded.")

def apply_startup_action():
    add_to_startup(autostart_var.get())
    messagebox.showinfo("Startup", "Autostart updated.")

def test_all_action():
    # play each assigned sound briefly (sequentially)
    for i, a in enumerate(alarms):
        fname = a.get("sound", "")
        if fname:
            status_label.config(text=f"Testing alarm {i+1}")
            play_sound_file(fname)
            # wait a short while while it plays (non-blocking for long files is ok; we'll wait 3 sec)
            time.sleep(3)
            stop_playback()
    status_label.config(text="Status: Stopped")

# bind buttons
start_btn.config(command=start_alarms_action)
stop_btn.config(command=stop_alarms_action)
save_btn.config(command=save_action)
load_btn.config(command=load_action)
startup_btn.config(command=apply_startup_action)
test_all_btn.config(command=test_all_action)
stop_play_btn.config(command=stop_playback)

# ---------- Prepare default and load ----------
ensure_default_alarms()
load_config()

# ensure UI shows loaded values
refresh_ui_from_alarms()

# if autostart var says true but startup file not present, create it
if autostart_var.get() and not is_startup_enabled():
    add_to_startup(True)

# ---------- Start Tk mainloop ----------
root.mainloop()
