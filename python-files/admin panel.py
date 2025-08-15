import tkinter as tk
from tkinter import ttk
import psutil
import socket
import time
import os
import random
import winsound
import threading
import ctypes
import platform
import datetime
import requests

# === Setup ===
root = tk.Tk()
root.title("SCP Admin Interface")
root.attributes("-fullscreen", True)
root.configure(bg="black")

# === Global Log ===
log = tk.Text(root, height=10, bg="black", fg="lime", font=("Courier", 12))
log.pack(fill="both", expand=True, padx=10, pady=10)

# === Boot Sequence ===
boot_frame = tk.Frame(root, bg="black")
boot_text = tk.Text(boot_frame, bg="black", fg="lime", font=("Courier", 12))
boot_text.pack(fill="both", expand=True)
boot_frame.pack(fill="both", expand=True)

boot_lines = [
    "[SCP-CORE] Initializing containment protocols...",
    "[SYSTEM] Loading neural sync modules...",
    "[SECURITY] Locking external access ports...",
    "[DIAGNOSTIC] Memory sectors unstable...",
    "[SCP-CORE] Launching Admin Interface..."
]

def typewriter(lines, delay=50):
    def write_line(i=0, j=0):
        if i < len(lines):
            if j < len(lines[i]):
                boot_text.insert(tk.END, lines[i][j])
                boot_text.update()
                root.after(delay, write_line, i, j+1)
            else:
                boot_text.insert(tk.END, "\n")
                root.after(delay, write_line, i+1, 0)
        else:
            boot_frame.pack_forget()
            show_main_ui()
    write_line()

# === Real Stats ===
def get_uptime():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    return str(now - boot_time).split('.')[0]

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "N/A"

def update_stats():
    cpu_label.config(text=f"CPU Usage: {psutil.cpu_percent()}%")
    mem = psutil.virtual_memory()
    mem_label.config(text=f"Memory Usage: {mem.percent}% ({mem.used // (1024**2)}MB)")
    disk = psutil.disk_usage('/')
    disk_label.config(text=f"Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB)")
    ip_label.config(text=f"Local IP: {socket.gethostbyname(socket.gethostname())}")
    pub_ip_label.config(text=f"Public IP: {get_public_ip()}")
    uptime_label.config(text=f"System Uptime: {get_uptime()}")
    processes_label.config(text=f"Processes: {len(psutil.pids())}")
    log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] System check OK\n")
    log.see(tk.END)
    root.after(3000, update_stats)

# === Admin Actions ===
def fake_overclock(component):
    log.insert(tk.END, f"[ACTION] Overclocking {component}...\n")
    log.insert(tk.END, f"[WARN] {component} temperature rising...\n")
    voltage_bar['value'] = random.randint(80, 100)
    winsound.Beep(1000, 200)
    log.insert(tk.END, f"[INFO] {component} frequency set to MAX\n")
    log.see(tk.END)

def trigger_alert():
    for _ in range(3):
        popup = tk.Toplevel()
        popup.title("SECURITY BREACH")
        tk.Label(popup, text="Unauthorized Access Detected!", fg="red", font=("Courier", 14)).pack()
        popup.geometry(f"300x100+{random.randint(100, 800)}+{random.randint(100, 500)}")
        winsound.Beep(random.randint(500, 2000), 300)

def show_bsod():
    bsod = tk.Toplevel()
    bsod.title("CRITICAL ERROR")
    bsod.configure(bg="blue")
    tk.Label(bsod, text="A fatal exception has occurred.\nSystem will now shut down.",
             font=("Consolas", 14), fg="white", bg="blue").pack(pady=50)
    bsod.geometry("600x200+400+300")
    winsound.Beep(200, 1000)

def force_update():
    update_win = tk.Toplevel()
    update_win.attributes("-fullscreen", True)
    update_win.configure(bg="blue")
    tk.Label(update_win, text="Installing Windows Update 0%", font=("Consolas", 20), fg="white", bg="blue").pack(expand=True)
    for i in range(101):
        update_win.update()
        time.sleep(0.05)
        tk.Label(update_win, text=f"Installing Windows Update {i}%", font=("Consolas", 20), fg="white", bg="blue").pack()
        winsound.Beep(500, 10)

def flash_screen():
    flash = tk.Toplevel()
    flash.attributes("-fullscreen", True)
    flash.configure(bg="white")
    flash.update()
    winsound.Beep(1000, 200)
    root.after(200, flash.destroy)

def invert_screen():
    ctypes.windll.user32.SetSysColors(1, (0,), (0xFFFFFF,))

def matrix_mode():
    matrix = tk.Toplevel()
    matrix.attributes("-fullscreen", True)
    matrix.configure(bg="black")
    canvas = tk.Canvas(matrix, bg="black")
    canvas.pack(fill="both", expand=True)
    drops = [0 for _ in range(200)]
    def draw():
        canvas.delete("all")
        for i in range(len(drops)):
            text = chr(random.randint(33, 126))
            canvas.create_text(i*10, drops[i], text=text, fill="green", font=("Consolas", 12))
            drops[i] = drops[i]+10 if drops[i]<matrix.winfo_height() else 0
        matrix.after(50, draw)
    draw()

# === Wrong Password Shutdown ===
def check_password(entry, button):
    if entry.get() != "admin123":
        log.insert(tk.END, "[ERROR] Unauthorized access attempt detected.\n")
        log.insert(tk.END, "[ACTION] Initiating system shutdown...\n")
        winsound.Beep(400, 500)
        root.update()
        os.system("shutdown /s /t 5")
    else:
        log.insert(tk.END, "[ACCESS] Admin privileges granted.\n")
        entry.pack_forget()
        button.pack_forget()
        hardware_frame.pack(pady=10)

# === Main UI ===
def show_main_ui():
    # Header
    tk.Label(root, text="SCP Admin Interface", font=("Segoe UI", 20), fg="white", bg="black").pack(pady=10)

    global cpu_label, mem_label, disk_label, ip_label, pub_ip_label, uptime_label, processes_label
    stats_frame = tk.Frame(root, bg="black")
    cpu_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    mem_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    disk_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    ip_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    pub_ip_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    uptime_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    processes_label = tk.Label(stats_frame, font=("Consolas", 14), fg="lime", bg="black")
    cpu_label.pack(anchor="w")
    mem_label.pack(anchor="w")
    disk_label.pack(anchor="w")
    ip_label.pack(anchor="w")
    pub_ip_label.pack(anchor="w")
    uptime_label.pack(anchor="w")
    processes_label.pack(anchor="w")
    stats_frame.pack(pady=10)

    update_stats()

    # Password entry
    entry = tk.Entry(root, show="*", font=("Consolas", 14))
    entry.pack(pady=5)
    login_button = tk.Button(root, text="Enter Admin Mode", command=lambda: check_password(entry, login_button))
    login_button.pack()

    # Hidden hardware control panel
    global hardware_frame
    hardware_frame = tk.Frame(root, bg="black")
    tk.Label(hardware_frame, text="Hardware & Security Suite", font=("Segoe UI", 16), fg="white", bg="black").pack()
    global voltage_bar
    voltage_bar = ttk.Progressbar(hardware_frame, length=300, mode='determinate')
    voltage_bar.pack(pady=2)

    # Buttons
    btns = [
        ("Overclock CPU", lambda: fake_overclock("CPU")),
        ("Boost GPU", lambda: fake_overclock("GPU")),
        ("Max RAM Frequency", lambda: fake_overclock("RAM")),
        ("Run Full Containment Protocol", trigger_alert),
        ("Run Security Sweep", lambda: log.insert(tk.END, "[SCAN] Threats found: 3 critical\n")),
        ("Firewall Emergency Lockdown", lambda: log.insert(tk.END, "[FIREWALL] All external ports locked\n")),
        ("Force Windows Update", force_update),
        ("Critical Error (BSOD)", show_bsod),
        ("Flash Screen", flash_screen),
        ("Invert Screen Colors", invert_screen),
        ("Matrix Mode", matrix_mode)
    ]

    for t, c in btns:
        tk.Button(hardware_frame, text=t, command=c).pack(pady=2)

# === Launch Boot Sequence ===
typewriter(boot_lines)
root.mainloop()

