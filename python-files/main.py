import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# تابع برای اجرای دستورات cmd
def run_command(command):
    try:
        subprocess.Popen(command, shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred: {e}")

# تابع برای دستورات مختلف
def on_ping():
    ip = ip_entry.get()
    if ip:
        command = f"ping -t {ip}"
        run_command(command)
    else:
        messagebox.showerror("Error", "Please enter an IP address.")

def on_trace():
    ip = ip_entry.get()
    if ip:
        command = f"tracert {ip}"
        run_command(command)
    else:
        messagebox.showerror("Error", "Please enter an IP address.")

def on_telnet():
    ip = ip_entry.get()
    if ip:
        command = f"telnet {ip}"
        run_command(command)
    else:
        messagebox.showerror("Error", "Please enter an IP address.")

# ساخت رابط گرافیکی
root = tk.Tk()
root.title("Network Tools")

# ورودی IP
tk.Label(root, text="Enter IP Address:").pack(pady=10)
ip_entry = tk.Entry(root, width=20)
ip_entry.pack(pady=5)

# دکمه‌ها
ping_button = tk.Button(root, text="Ping", command=on_ping)
ping_button.pack(pady=5)

trace_button = tk.Button(root, text="Trace", command=on_trace)
trace_button.pack(pady=5)

telnet_button = tk.Button(root, text="Telnet", command=on_telnet)
telnet_button.pack(pady=5)

# اجرای پنجره
root.mainloop()
