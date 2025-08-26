import os
import tkinter as tk
from tkinter import messagebox
import random

# --- Functions ---
def clear_temp():
    try:
        os.system("del /s /q %temp%\\*")
        messagebox.showinfo("Kezyfn Tweaks", "Temp files cleared!")
    except:
        messagebox.showerror("Kezyfn Tweaks", "Failed to clear temp files.")

def high_perf():
    try:
        os.system("powercfg -setactive SCHEME_MIN")
        messagebox.showinfo("Kezyfn Tweaks", "High Performance mode enabled!")
    except:
        messagebox.showerror("Kezyfn Tweaks", "Failed to enable High Performance mode.")

def disable_gamebar():
    try:
        os.system('reg add "HKCU\\Software\\Microsoft\\GameBar" /v ShowGameBarTips /t REG_DWORD /d 0 /f')
        os.system('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f')
        messagebox.showinfo("Kezyfn Tweaks", "Game Bar & DVR disabled!")
    except:
        messagebox.showerror("Kezyfn Tweaks", "Failed to disable Game Bar/DVR.")

def optimize_network():
    try:
        os.system("netsh int tcp set global autotuninglevel=disabled")
        os.system("netsh int tcp set global rss=enabled")
        messagebox.showinfo("Kezyfn Tweaks", "Network optimized!")
    except:
        messagebox.showerror("Kezyfn Tweaks", "Failed to optimize network.")

def stop_background_apps():
    try:
        os.system("taskkill /F /FI \"STATUS eq RUNNING\" /FI \"USERNAME eq %USERNAME%\"")
        messagebox.showinfo("Kezyfn Tweaks", "Background apps stopped!")
    except:
        messagebox.showerror("Kezyfn Tweaks", "Failed to stop background apps.")

def disable_animations():
    try:
        os.system("reg add \"HKCU\\Control Panel\\Desktop\" /v UserPreferencesMask /t REG_BINARY /d 901200 /f")
        messagebox.showinfo("Kezyfn Tweaks", "Windows animations disabled!")
    except:
        messagebox.showerror("Kezyfn Tweaks", "Failed to disable animations.")

# --- GUI ---
app = tk.Tk()
app.title("Kezyfn Tweaks")
app.geometry("550x450")
app.resizable(False, False)

# Background canvas
canvas = tk.Canvas(app, width=550, height=450, bg="#030b2f", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Draw random stars
for _ in range(100):
    x = random.randint(0, 550)
    y = random.randint(0, 450)
    size = random.randint(1, 3)
    canvas.create_oval(x, y, x+size, y+size, fill="white", outline="white")

# Frame for buttons
frame = tk.Frame(app, bg="#030b2f")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Label
tk.Label(frame, text="Kezyfn Tweaks", font=("Arial", 26, "bold"), fg="white", bg="#030b2f").pack(pady=20)

# Button colors
button_color = "#4da6ff"  # light blue
button_fg = "#000000"

# Buttons
tk.Button(frame, text="🧹 Clear Temp Files", width=30, bg=button_color, fg=button_fg, command=clear_temp).pack(pady=5)
tk.Button(frame, text="⚡ Enable High Performance", width=30, bg=button_color, fg=button_fg, command=high_perf).pack(pady=5)
tk.Button(frame, text="🎮 Disable Game Bar/DVR", width=30, bg=button_color, fg=button_fg, command=disable_gamebar).pack(pady=5)
tk.Button(frame, text="🌐 Optimize Network", width=30, bg=button_color, fg=button_fg, command=optimize_network).pack(pady=5)
tk.Button(frame, text="🚫 Stop Background Apps", width=30, bg=button_color, fg=button_fg, command=stop_background_apps).pack(pady=5)
tk.Button(frame, text="🔧 Disable Windows Animations", width=30, bg=button_color, fg=button_fg, command=disable_animations).pack(pady=5)

app.mainloop()
