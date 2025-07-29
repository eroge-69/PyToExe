import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading
import time

usb_drive = "D:\\"
key_file = "keyfile.txt"
expected_key = "9f6c2d2a-8b3a-4f28-a9b0-83a897b0d6ee"
network_path = r"\\Sales\Whitco"
network_drive = "H:"

def connect_network_drive(password):
    subprocess.call(f'net use {network_drive} /delete /yes', shell=True)
    cmd = f'net use {network_drive} {network_path} /user:mini {password}'
    result = subprocess.call(cmd, shell=True)
    return result == 0

def disconnect_network_drive():
    subprocess.call(f'net use {network_drive} /delete /yes', shell=True)

def monitor_usb():
    key_path = os.path.join(usb_drive, key_file)
    while True:
        time.sleep(2)
        if not os.path.exists(key_path):
            disconnect_network_drive()
            messagebox.showwarning("USB Removed", "USB key removed. Network drive disconnected.")
            root.quit()
            break

def launch_access():
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Password cannot be empty.")
        return

    key_path = os.path.join(usb_drive, key_file)
    if not os.path.exists(key_path):
        messagebox.showerror("Error", f"Key file not found:\n{key_path}")
        return

    with open(key_path, "r") as f:
        actual_key = f.read().strip()

    if actual_key != expected_key:
        messagebox.showerror("Error", "Invalid key! Access denied.")
        return

    if connect_network_drive(password):
        subprocess.Popen(f'explorer {network_drive}', shell=True)
        threading.Thread(target=monitor_usb, daemon=True).start()
        root.destroy()
    else:
        messagebox.showerror("Error", "Failed to connect network drive. Check password.")

def on_exit():
    disconnect_network_drive()
    root.destroy()

root = tk.Tk()
root.title("USB Key Folder Access")
root.geometry("400x220")
root.resizable(False, False)

label = tk.Label(root, text="Insert USB with keyfile and enter password", font=("Arial", 12))
label.pack(pady=10)

pass_label = tk.Label(root, text="Password:", font=("Arial", 10))
pass_label.pack()

password_entry = tk.Entry(root, show="*", width=30, font=("Arial", 10))
password_entry.pack(pady=5)

btn = tk.Button(root, text="Open Folder", font=("Arial", 12), command=launch_access)
btn.pack(pady=10)

exit_btn = tk.Button(root, text="Exit", font=("Arial", 10), command=on_exit)
exit_btn.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
