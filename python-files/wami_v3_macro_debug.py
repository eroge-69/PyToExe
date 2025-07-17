
import tkinter as tk
from tkinter import ttk
import webbrowser
import json
import os
import threading
import keyboard  # مكتبة الضغط

macro_running = False

options = [
    *[chr(c) for c in range(ord('A'), ord('Z') + 1)],
    *[str(n) for n in range(0, 10)],
    "Shift", "Ctrl", "Alt", "Tab", "Space", "CapsLock", "Enter", "Esc", "Backspace",
    "Insert", "Delete", "Home", "End", "PageUp", "PageDown",
    "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
    "Mouse Left", "Mouse Right", "Mouse Middle",
    "Mouse Button 4", "Mouse Button 5",
    "Scroll Up", "Scroll Down"
]

def save_settings():
    settings = {
        "edit_key": edit_key.get(),
        "reset_key": reset_key.get(),
        "select_key": select_key.get(),
        "shotgun_key": shotgun_key.get()
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
            edit_key.set(settings.get("edit_key", ""))
            reset_key.set(settings.get("reset_key", ""))
            select_key.set(settings.get("select_key", ""))
            shotgun_key.set(settings.get("shotgun_key", ""))

def open_discord():
    webbrowser.open("https://discord.gg/ZMQKVEggg7")

def monitor_edit_key():
    global macro_running
    macro_running = True

    e_key = edit_key.get().lower()
    r_key = reset_key.get().lower()
    s_key = select_key.get().lower()
    sh_key = shotgun_key.get().lower()

    print(f"[🎮] Listening for Edit Key: {e_key}")
    print(f"[🔧] Reset: {r_key}, Select: {s_key}, Shotgun: {sh_key}")

    def on_press(event):
        if event.name == e_key and macro_running:
            print("▶️ Pressed Edit Key")
            keyboard.press(r_key)
            keyboard.press(s_key)

    def on_release(event):
        if event.name == e_key and macro_running:
            print("⏹️ Released Edit Key")
            keyboard.release(r_key)
            keyboard.release(s_key)
            print("💥 Pressing Shotgun Key...")
            keyboard.press_and_release(sh_key)

    keyboard.on_press(on_press)
    keyboard.on_release(on_release)
    keyboard.wait()

def start_script():
    save_settings()
    threading.Thread(target=monitor_edit_key, daemon=True).start()
    print("✅ Macro is running. Press the Edit Key to activate.")

def stop_script():
    global macro_running
    macro_running = False
    keyboard.unhook_all()
    print("🛑 Macro stopped.")

root = tk.Tk()
root.title("wami v3 - Debug Mode")
root.geometry("340x350")
root.configure(bg="#0c0c2b")

tk.Label(root, text="wami v3 - Debug", font=("Arial", 14, "bold"), bg="#0c0c2b", fg="white").pack(pady=10)

def create_dropdown(label_text):
    frame = tk.Frame(root, bg="#0c0c2b")
    frame.pack(pady=5)
    label = tk.Label(frame, text=label_text, fg="white", bg="#0c0c2b")
    label.pack(side="left")
    combo = ttk.Combobox(frame, values=options)
    combo.pack(side="right")
    return combo

edit_key = create_dropdown("Edit Key:")
reset_key = create_dropdown("Reset Key:")
select_key = create_dropdown("Select Key:")
shotgun_key = create_dropdown("Shotgun Key:")

button_frame = tk.Frame(root, bg="#0c0c2b")
button_frame.pack(pady=15)

tk.Button(button_frame, text="Start", width=8, command=start_script).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Stop", width=8, command=stop_script).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Exit", width=8, command=root.quit).grid(row=0, column=2, padx=5)

tk.Button(root, text="Discord", width=20, command=open_discord).pack(pady=10)

load_settings()
root.mainloop()
