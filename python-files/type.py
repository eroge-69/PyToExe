import customtkinter as ctk
import pyautogui
import pyperclip
import threading
import time
import pygetwindow as gw
import os
import psutil
import win32process
import win32gui
import win32con
import keyboard
import tkinter.filedialog as fd
import json

# Config
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
app = ctk.CTk()
app.title("DT Sync v3.4 - Auto Typer")
app.geometry("720x900")
app.grid_columnconfigure((0, 1), weight=1)

# Globals
typing_event = threading.Event()
loop_mode = False
clipboard_mode = False
force_focus_mode = True
selected_window_title = None
selected_process_name = None
selected_hwnd = None
settings_file = "dt_sync_settings.json"

# --- Save/Load Settings ---
def save_settings():
    settings = {
        "text": text_entry.get("0.0", "end").strip(),
        "repeat": repeat_slider.get(),
        "speed": speed_slider.get(),
        "loop": loop_var.get(),
        "clipboard": clipboard_var.get(),
        "focus": focus_var.get(),
        "interval": loop_interval_slider.get(),
        "selected_window": selected_window_title or "",
    }
    with open(settings_file, "w") as f:
        json.dump(settings, f)

def load_settings():
    global selected_window_title, selected_process_name, selected_hwnd
    if not os.path.exists(settings_file):
        return
    try:
        with open(settings_file, "r") as f:
            settings = json.load(f)
        text_entry.delete("0.0", "end")
        text_entry.insert("0.0", settings["text"])
        repeat_slider.set(settings["repeat"])
        speed_slider.set(settings["speed"])
        loop_var.set(settings["loop"])
        clipboard_var.set(settings["clipboard"])
        focus_var.set(settings["focus"])
        loop_interval_slider.set(settings["interval"])
        if settings["selected_window"]:
            on_window_selected(settings["selected_window"])
            window_dropdown.set(settings["selected_window"])
    except:
        pass

# --- Window Selection ---
def update_window_list():
    windows = gw.getAllTitles()
    cleaned = [w for w in windows if w.strip() != ""]
    window_dropdown.configure(values=cleaned)
    status_label.configure(text=f"Refreshed {len(cleaned)} window(s)")

def on_window_selected(choice):
    global selected_window_title, selected_process_name, selected_hwnd
    selected_window_title = choice
    try:
        win = gw.getWindowsWithTitle(choice)[0]
        selected_hwnd = win._hWnd
        _, pid = win32process.GetWindowThreadProcessId(win._hWnd)
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.pid == pid:
                selected_process_name = proc.info['name']
                exe_label.configure(text=f"Target: {selected_process_name}")
                break
    except:
        selected_process_name = None
        selected_hwnd = None
        exe_label.configure(text="Target: Unknown")

# --- Typing Engine ---
def force_focus():
    if selected_hwnd and win32gui.IsWindow(selected_hwnd):
        try:
            win32gui.ShowWindow(selected_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(selected_hwnd)
            time.sleep(0.2)
        except:
            status_label.configure(text="⚠️ Can't focus window.")

def typing_worker():
    count = 0
    repeat_count = int(repeat_slider.get())
    custom_text = text_entry.get("0.0", "end").strip()
    text_to_type = pyperclip.paste() if clipboard_mode else custom_text

    time.sleep(1)
    while typing_event.is_set() and (loop_mode or count < repeat_count):
        if force_focus_mode:
            force_focus()

        win = gw.getActiveWindow()
        if selected_window_title and (not win or selected_window_title not in win.title):
            time.sleep(0.5)
            continue

        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

        for char in text_to_type:
            if not typing_event.is_set():
                break
            pyautogui.write(char)
            time.sleep(speed_slider.get())

        count += 1
        time.sleep(loop_interval_slider.get())

    typing_event.clear()
    status_label.configure(text="✅ Typing stopped.")

def start_typing():
    if typing_event.is_set():
        return
    save_settings()
    typing_event.set()
    threading.Thread(target=typing_worker, daemon=True).start()
    status_label.configure(text="⏳ Typing started...")

def stop_typing():
    typing_event.clear()
    status_label.configure(text="⏹ Stopping...")

# --- UI Updates ---
def toggle_clipboard_mode():
    global clipboard_mode
    clipboard_mode = clipboard_var.get()

def toggle_loop_mode():
    global loop_mode
    loop_mode = loop_var.get()

def toggle_force_focus_mode():
    global force_focus_mode
    force_focus_mode = focus_var.get()

def update_char_count(*args):
    char_label.configure(text=f"Characters: {len(text_entry.get('0.0', 'end').strip())}")

def load_file():
    file = fd.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file:
        with open(file, "r", encoding="utf-8") as f:
            text_entry.delete("0.0", "end")
            text_entry.insert("0.0", f.read())

def clear_text():
    text_entry.delete("0.0", "end")

def hotkey_listener():
    keyboard.add_hotkey("ctrl+shift+t", lambda: start_typing() if not typing_event.is_set() else None)
    keyboard.add_hotkey("ctrl+shift+y", lambda: stop_typing() if typing_event.is_set() else None)
    keyboard.wait()

# --- UI Components ---
ctk.CTkLabel(app, text="🌀 DT Sync v3.4", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(15, 5))
text_entry = ctk.CTkTextbox(app, height=120, width=660)
text_entry.grid(row=1, column=0, columnspan=2, pady=5, padx=10)
text_entry.bind("<KeyRelease>", update_char_count)

char_label = ctk.CTkLabel(app, text="Characters: 0")
char_label.grid(row=2, column=0, sticky="w", padx=20)

ctk.CTkFrame(app)
ctk.CTkButton(app, text="📂 Load .txt", command=load_file, corner_radius=8).grid(row=2, column=1, sticky="e", padx=20)
ctk.CTkButton(app, text="🧹 Clear Text", command=clear_text, corner_radius=8).grid(row=3, column=1, sticky="e", padx=20)

clipboard_var = ctk.BooleanVar(); ctk.CTkCheckBox(app, text="📋 Use Clipboard", variable=clipboard_var, command=toggle_clipboard_mode).grid(row=3, column=0, sticky="w", padx=20)
loop_var = ctk.BooleanVar(); ctk.CTkCheckBox(app, text="🔁 Loop", variable=loop_var, command=toggle_loop_mode).grid(row=4, column=0, sticky="w", padx=20)
focus_var = ctk.BooleanVar(value=True); ctk.CTkCheckBox(app, text="🪟 Focus Lock", variable=focus_var, command=toggle_force_focus_mode).grid(row=4, column=1, sticky="e", padx=20)

ctk.CTkLabel(app, text="🎯 Select Target Window:").grid(row=5, column=0, columnspan=2, pady=(10, 2))
window_dropdown = ctk.CTkOptionMenu(app, values=[], command=on_window_selected)
window_dropdown.grid(row=6, column=0, columnspan=2, padx=20)
ctk.CTkButton(app, text="🔄 Refresh", command=update_window_list, corner_radius=10).grid(row=7, column=0, columnspan=2)
exe_label = ctk.CTkLabel(app, text="Target: None")
exe_label.grid(row=8, column=0, columnspan=2)

ctk.CTkLabel(app, text="⚡ Speed (sec/char)").grid(row=9, column=0, columnspan=2)
speed_slider = ctk.CTkSlider(app, from_=0.01, to=0.3); speed_slider.set(0.05)
speed_slider.grid(row=10, column=0, columnspan=2, padx=30)

ctk.CTkLabel(app, text="🔁 Repeat Count").grid(row=11, column=0, columnspan=2)
repeat_slider = ctk.CTkSlider(app, from_=1, to=10); repeat_slider.set(1)
repeat_slider.grid(row=12, column=0, columnspan=2, padx=30)

ctk.CTkLabel(app, text="⌛ Loop Delay (sec)").grid(row=13, column=0, columnspan=2)
loop_interval_slider = ctk.CTkSlider(app, from_=1, to=30); loop_interval_slider.set(3)
loop_interval_slider.grid(row=14, column=0, columnspan=2, padx=30)

status_label = ctk.CTkLabel(app, text="Ready", wraplength=600)
status_label.grid(row=15, column=0, columnspan=2, pady=10)
ctk.CTkButton(app, text="▶ Start Typing", command=start_typing, corner_radius=12).grid(row=16, column=0, pady=5)
ctk.CTkButton(app, text="⏹ Stop Typing", command=stop_typing, corner_radius=12).grid(row=16, column=1, pady=5)

# Launch
update_window_list()
load_settings()
threading.Thread(target=hotkey_listener, daemon=True).start()
app.mainloop()
