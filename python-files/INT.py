import os
import shutil
import ctypes
import psutil
import tkinter as tk
from tkinter import messagebox
import threading
import time

def get_ram_stats():
    mem = psutil.virtual_memory()
    used = round(mem.used / (1024 ** 3), 2)
    total = round(mem.total / (1024 ** 3), 2)
    percent = mem.percent
    return used, total, percent

def update_ram_display():
    used, total, percent = get_ram_stats()
    ram_label.config(text=f"💾 RAM: {used}GB / {total}GB ({percent}%)")
    root.after(2000, update_ram_display)

def clear_temp(path):
    try:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            try:
                if os.path.isfile(full_path) or os.path.islink(full_path):
                    os.unlink(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
            except:
                continue
    except:
        pass

def kill_background_apps():
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            if proc.info['memory_percent'] < 5 and not proc.info['name'].lower().startswith("system"):
                proc.kill()
        except:
            continue

def fake_progress():
    progress_label.config(text="🚀 Boosting... [▒▒▒▒▒▒▒▒▒▒] 0%")
    for i in range(1, 11):
        progress_label.config(text=f"🚀 Boosting... [{'█'*i}{'▒'*(10-i)}] {i*10}%")
        time.sleep(0.2)

def boost_system():
    boost_btn.config(state="disabled")
    status_label.config(text="")
    threading.Thread(target=fake_progress).start()

    before = get_ram_stats()[2]

    if var_ram.get():
        ctypes.windll.psapi.EmptyWorkingSet(-1)

    if var_temp.get():
        clear_temp("C:\\Windows\\Temp")
    
    if var_percent_temp.get():
        clear_temp(os.environ['TEMP'])

    if var_prefetch.get():
        clear_temp("C:\\Windows\\Prefetch")

    if var_apps.get():
        kill_background_apps()

    after = get_ram_stats()[2]
    diff = before - after

    time.sleep(2.5)
    progress_label.config(text="")
    status_label.config(
        text=f"✅ Boost Complete!\nBefore: {before}% RAM\nAfter: {after}% RAM\n🧠 Saved: {diff:.2f}%"
    )
    boost_btn.config(state="normal")

# ==== واجهة البرنامج ====
root = tk.Tk()
root.title("⚡ DUCK BOOSTER PRO")
root.geometry("420x520")
root.config(bg="#0a0a0a")
root.resizable(False, False)

tk.Label(root, text="🦆 DUCK BOOSTER", font=("Arial", 16, "bold"),
         bg="#0a0a0a", fg="#00ff88").pack(pady=10)

ram_label = tk.Label(root, text="", bg="#0a0a0a", fg="#aaaaaa", font=("Arial", 11))
ram_label.pack(pady=5)
update_ram_display()

var_ram = tk.BooleanVar(value=True)
var_temp = tk.BooleanVar(value=True)
var_percent_temp = tk.BooleanVar(value=True)
var_prefetch = tk.BooleanVar(value=False)
var_apps = tk.BooleanVar(value=False)

frame = tk.Frame(root, bg="#0a0a0a")
frame.pack(pady=5)

options = [
    ("🧠 Clean RAM", var_ram),
    ("🧹 Clear C:\\Windows\\Temp", var_temp),
    ("🧹 Clear %TEMP%", var_percent_temp),
    ("🧹 Clear PREFETCH", var_prefetch),
    ("❌ Close background apps", var_apps)
]

for text, var in options:
    tk.Checkbutton(frame, text=text, variable=var, font=("Arial", 11),
                   bg="#0a0a0a", fg="white", selectcolor="#0f0").pack(anchor="w", padx=25, pady=6)

boost_btn = tk.Button(root, text="🚀 BOOST NOW", font=("Arial", 15, "bold"),
                      bg="#00cc66", fg="white", width=20, command=lambda: threading.Thread(target=boost_system).start())
boost_btn.pack(pady=25)

progress_label = tk.Label(root, text="", bg="#0a0a0a", fg="#999999", font=("Consolas", 11))
progress_label.pack()

status_label = tk.Label(root, text="", bg="#0a0a0a", fg="#cccccc", font=("Arial", 11), justify="center")
status_label.pack(pady=10)

root.mainloop()
