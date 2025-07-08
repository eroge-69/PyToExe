
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import shutil
import threading
import time
import datetime
import psutil
import urllib.request
import zipfile

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
STEAMCMD_DIR = os.path.join(os.getcwd(), "steamcmd")
SERVER_DIR = os.path.join(STEAMCMD_DIR, "palworld_server")
SERVER_EXECUTABLE = os.path.join(SERVER_DIR, "PalServer.exe")
CONFIG_FILE = os.path.join(os.getcwd(), "server_config.txt")
BACKUP_DIR = os.path.join(os.getcwd(), "backups")
LOG_FILE = os.path.join(os.getcwd(), "server_log.txt")

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# GUI Setup
root = tk.Tk()
root.title("Palworld Server Manager")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Functions
def install_steamcmd_and_server():
    try:
        if not os.path.exists(STEAMCMD_DIR):
            os.makedirs(STEAMCMD_DIR)
        zip_path = os.path.join(STEAMCMD_DIR, "steamcmd.zip")
        urllib.request.urlretrieve(STEAMCMD_URL, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(STEAMCMD_DIR)
        os.remove(zip_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install SteamCMD: {e}")
        return

    try:
        subprocess.run([
            os.path.join(STEAMCMD_DIR, "steamcmd.exe"),
            "+login", "anonymous",
            "+force_install_dir", SERVER_DIR,
            "+app_update", "2394010", "validate",
            "+quit"
        ], check=True)
        messagebox.showinfo("Success", "Palworld server installed/updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install/update server: {e}")

def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"{server_name_var.get()}\n")
            f.write(f"{server_password_var.get()}\n")
            f.write(f"{admin_password_var.get()}\n")
            f.write(f"{max_players_var.get()}\n")
            f.write(f"{restart_interval_var.get()}\n")
        messagebox.showinfo("Saved", "Configuration saved.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save config: {e}")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            lines = f.read().splitlines()
            server_name_var.set(lines[0])
            server_password_var.set(lines[1])
            admin_password_var.set(lines[2])
            max_players_var.set(lines[3])
            restart_interval_var.set(lines[4])
        messagebox.showinfo("Loaded", "Configuration loaded.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load config: {e}")

def backup_server():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    try:
        shutil.copytree(os.path.join(SERVER_DIR, "Pal"), backup_path)
        messagebox.showinfo("Backup", f"Backup created at {backup_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Backup failed: {e}")

def restore_backup():
    folder = filedialog.askdirectory(title="Select Backup Folder")
    if folder:
        try:
            pal_dir = os.path.join(SERVER_DIR, "Pal")
            if os.path.exists(pal_dir):
                shutil.rmtree(pal_dir)
            shutil.copytree(folder, pal_dir)
            messagebox.showinfo("Restore", "Backup restored successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {e}")

def announce_message():
    msg = announcement_entry.get()
    if msg:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.datetime.now()}] Announcement: {msg}\n")
        log_viewer.insert(tk.END, f"Announcement: {msg}\n")
        log_viewer.see(tk.END)

def monitor_system():
    while True:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        status_label.config(text=f"CPU: {cpu}% | Memory: {mem}%")
        time.sleep(5)

def scheduled_restart():
    while True:
        try:
            interval = int(restart_interval_var.get())
            time.sleep((interval - 1) * 60)
            with open(LOG_FILE, "a") as f:
                f.write(f"[{datetime.datetime.now()}] Restart in 60 seconds...\n")
            log_viewer.insert(tk.END, "Restart in 60 seconds...\n")
            log_viewer.see(tk.END)
            time.sleep(60)
            backup_server()
            with open(LOG_FILE, "a") as f:
                f.write(f"[{datetime.datetime.now()}] Server restarted.\n")
            log_viewer.insert(tk.END, "Server restarted.\n")
            log_viewer.see(tk.END)
        except Exception as e:
            log_viewer.insert(tk.END, f"Scheduled restart error: {e}\n")
            log_viewer.see(tk.END)

def launch_server():
    if os.path.exists(SERVER_EXECUTABLE):
        try:
            subprocess.Popen([SERVER_EXECUTABLE], cwd=SERVER_DIR)
            messagebox.showinfo("Server Launch", "Palworld server launched successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch server: {e}")
    else:
        messagebox.showerror("Error", "PalServer.exe not found. Please install the server first.")

def check_firewall():
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=PalServer'],
            capture_output=True, text=True
        )
        if "No rules match the specified criteria" in result.stdout:
            messagebox.showwarning(
                "Firewall Rule Missing",
                "No firewall rule found for PalServer.exe.\n\n"
                "Please allow PalServer.exe through Windows Firewall manually."
            )
        else:
            messagebox.showinfo("Firewall Check", "Firewall rule for PalServer.exe is configured.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check firewall: {e}")

def show_port_instructions():
    instructions = (
        "To host a Palworld server, you need to forward the following UDP ports on your router:\n\n"
        " - Port 8211 (Game Port)\n"
        " - Port 27015 (Steam Query Port)\n\n"
        "Steps:\n"
        "1. Log in to your router's admin panel.\n"
        "2. Locate the Port Forwarding section.\n"
        "3. Add rules to forward UDP ports 8211 and 27015 to your computer's local IP address.\n"
        "4. Save and apply the changes.\n\n"
        "Note: You may also need to allow these ports through Windows Firewall."
    )
    messagebox.showinfo("Port Forwarding Instructions", instructions)

# GUI Layout
title_label = tk.Label(root, text="Palworld Server Manager", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

frame = tk.Frame(root)
frame.pack()

server_name_var = tk.StringVar()
server_password_var = tk.StringVar()
admin_password_var = tk.StringVar()
max_players_var = tk.StringVar()
restart_interval_var = tk.StringVar(value="60")

tk.Label(frame, text="Server Name").grid(row=0, column=0)
tk.Entry(frame, textvariable=server_name_var).grid(row=0, column=1)
tk.Label(frame, text="Server Password").grid(row=1, column=0)
tk.Entry(frame, textvariable=server_password_var).grid(row=1, column=1)
tk.Label(frame, text="Admin Password").grid(row=2, column=0)
tk.Entry(frame, textvariable=admin_password_var).grid(row=2, column=1)
tk.Label(frame, text="Max Players").grid(row=3, column=0)
tk.Entry(frame, textvariable=max_players_var).grid(row=3, column=1)
tk.Label(frame, text="Restart Interval (min)").grid(row=4, column=0)
tk.Entry(frame, textvariable=restart_interval_var).grid(row=4, column=1)

tk.Button(frame, text="Save Config", command=save_config).grid(row=5, column=0)
tk.Button(frame, text="Load Config", command=load_config).grid(row=5, column=1)
tk.Button(frame, text="Backup Server", command=backup_server).grid(row=6, column=0)
tk.Button(frame, text="Restore Backup", command=restore_backup).grid(row=6, column=1)
tk.Button(frame, text="Install/Update Server", command=install_steamcmd_and_server).grid(row=7, column=0)
tk.Button(frame, text="Launch Server", command=launch_server).grid(row=7, column=1)
tk.Button(frame, text="Check Firewall", command=check_firewall).grid(row=8, column=0)
tk.Button(frame, text="Port Instructions", command=show_port_instructions).grid(row=8, column=1)

announcement_entry = tk.Entry(root, width=100)
announcement_entry.pack(pady=5)
tk.Button(root, text="Send Announcement", command=announce_message).pack()

status_label = tk.Label(root, text="CPU: 0% | Memory: 0%")
status_label.pack()

log_viewer = scrolledtext.ScrolledText(root, width=140, height=15)
log_viewer.pack(padx=10, pady=10)

# Start background threads
threading.Thread(target=monitor_system, daemon=True).start()
threading.Thread(target=scheduled_restart, daemon=True).start()

root.mainloop()
