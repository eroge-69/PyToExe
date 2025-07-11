import tkinter as tk
import subprocess
import os
import psutil
from datetime import datetime

root = tk.Tk()
root.title("E44OR OS - Activated")
root.configure(bg="#0d0d0d")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.iconbitmap("e44or_glitch.ico")

clock_time = tk.Label(root, text="", font=("Consolas", 36, "bold"), fg="#ffffff", bg="#0d0d0d")
clock_time.place(x=15, y=10)

clock_date = tk.Label(root, text="", font=("Consolas", 14), fg="#888888", bg="#0d0d0d")
clock_date.place(x=18, y=60)

def update_clock():
    now = datetime.now()
    clock_time.config(text=now.strftime("%I:%M %p"))
    clock_date.config(text=now.strftime("%A, %b %d"))
    root.after(1000, update_clock)

update_clock()

battery_label = tk.Label(root, text="🔋", font=("Consolas", 12), fg="#ffffff", bg="#0d0d0d")
battery_label.place(relx=1.0, y=5, anchor='ne')

def update_battery():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        status = f"🔋 {percent}% {'(Charging)' if plugged else ''}"
        battery_label.config(text=status)
    root.after(10000, update_battery)

update_battery()

main_frame = tk.Frame(root, bg="#0d0d0d")
main_frame.pack(pady=70)

tk.Label(main_frame, text="🟢 E44OR OS", font=("Consolas", 28, "bold"),
         fg="#ffffff", bg="#0d0d0d").pack(pady=10)

tk.Label(main_frame, text="Forged from Apple’s ashes. Activated by sin. Designed for war.",
         font=("Consolas", 12), fg="#888", bg="#0d0d0d").pack()

def launch(command):
    try:
        subprocess.Popen(command, shell=True)
    except: pass

def add_button(name, command):
    tk.Button(main_frame, text=name, font=("Consolas", 14), fg="#ffffff", bg="#1a1a1a",
              activebackground="#333", width=40, height=2, borderwidth=0,
              command=lambda: launch(command)).pack(pady=6)

prism_shortcut = os.path.expandvars(
    r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Prism Launcher.lnk"
)

add_button("🟪 Launch Prism Launcher", f'start "" "{prism_shortcut}"')
add_button("📝 Microsoft Word", "start winword")
add_button("📊 Microsoft Excel", "start excel")
add_button("📽️ Microsoft PowerPoint", "start powerpnt")
add_button("🗒️ Microsoft OneNote", "start onenote")
add_button("🌐 Google Chrome", "start chrome")
add_button("📁 File Explorer", "explorer")
add_button("🧠 Task Manager", "taskmgr")
add_button("📄 Notepad (Injector Placeholder)", "notepad")
add_button("🔒 Lock E44OR OS", "rundll32.exe user32.dll,LockWorkStation")

tk.Button(main_frame, text="❌ Exit Shell", font=("Consolas", 12), fg="#ff5555", bg="#0d0d0d",
          activebackground="#330000", width=20, command=root.destroy).pack(pady=30)

root.mainloop()
