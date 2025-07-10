
import os
import psutil
import ctypes
import tkinter as tk
from tkinter import messagebox

# تنظیمات اولیه
game_mode = False

# لیست برنامه‌هایی که باید بسته شوند
apps_to_kill = ["chrome.exe", "discord.exe", "spotify.exe", "onedrive.exe"]

# فعال‌سازی High Performance Power Plan
def set_high_performance():
    os.system("powercfg /setactive SCHEME_MIN")

# بازگرداندن به Power Plan پیش‌فرض (Balanced)
def set_balanced():
    os.system("powercfg /setactive SCHEME_BALANCED")

# بستن برنامه‌های مزاحم
def kill_background_apps():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() in apps_to_kill:
            try:
                proc.kill()
            except Exception:
                pass

# پاکسازی رم با استفاده از EmptyWorkingSet (فقط برای سیستم‌های ویندوز)
def clear_ram():
    try:
        ctypes.windll.psapi.EmptyWorkingSet(-1)
    except Exception:
        pass

# بهینه‌سازی سیستم
def optimize_system():
    set_high_performance()
    kill_background_apps()
    clear_ram()

# غیرفعالسازی بهینه‌سازی
def reset_system():
    set_balanced()

# عملیات کلیک روی دکمه
def toggle_mode():
    global game_mode
    game_mode = not game_mode
    if game_mode:
        optimize_system()
        btn.config(text="خاموش کردن Game Mode", bg="green")
        status_label.config(text="Game Mode: ON", fg="green")
    else:
        reset_system()
        btn.config(text="روشن کردن Game Mode", bg="gray")
        status_label.config(text="Game Mode: OFF", fg="red")

# رابط گرافیکی
root = tk.Tk()
root.title("Gamer Man")
root.geometry("300x150")
root.resizable(False, False)

status_label = tk.Label(root, text="Game Mode: OFF", font=("Arial", 12), fg="red")
status_label.pack(pady=10)

btn = tk.Button(root, text="روشن کردن Game Mode", font=("Arial", 12), command=toggle_mode, bg="gray")
btn.pack(pady=10)

root.mainloop()
