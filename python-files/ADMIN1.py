import tkinter as tk
from tkinter import messagebox
import time
import threading
import tempfile
import ctypes
import os

# Hardcoded credentials
USERNAME = "BCA"
PASSWORD = "0393"

# Example product key (you can replace this with your own)
PRODUCT_KEY = "W269N-WFGWX-YVC9B-4J6C9-T83GX"  # Replace with your actual key

# CMD commands to activate Windows
CMD_COMMANDS = [
    f"slmgr /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX",
    "slmgr /skms kms8.msguides.com",
    "slmgr /ato"
]

def run_commands_as_admin():
    """Run CMD commands as Administrator using a temporary .bat file"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bat", mode='w') as bat_file:
            for cmd in CMD_COMMANDS:
                bat_file.write(cmd + "\n")
            bat_file.write("pause\n")  # Pause to keep window open
            bat_path = bat_file.name

        # Use ShellExecute to run as admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", bat_path, None, None, 1
        )

        output_text.insert(tk.END, "🛠️ Running activation commands as Administrator...\n")
    except Exception as e:
        output_text.insert(tk.END, f"❌ Failed to run as admin: {e}\n")

    output_text.see(tk.END)

def simulate_activation():
    progress_label.config(text="Activating Windows...")
    for i in range(1, 101):
        time.sleep(0.03)
        progress_var.set(f"Progress: {i}%")
        progress_label.update()
    messagebox.showinfo("AK WINDOWS ACTIVATOR", f"✅ Windows Activated Successfully!\n\nProduct Key: {PRODUCT_KEY}")
    run_commands_as_admin()

def login():
    user = username_entry.get()
    pwd = password_entry.get()

    if user == USERNAME and pwd == PASSWORD:
        login_frame.pack_forget()
        activator_frame.pack(pady=20)
    else:
        messagebox.showerror("Error", "Invalid Username or Password!")

def start_activation():
    threading.Thread(target=simulate_activation, daemon=True).start()

# Main window
root = tk.Tk()
root.title("AK WINDOWS ACTIVATOR")
root.geometry("500x400")
root.configure(bg="blue")

# Login Frame
login_frame = tk.Frame(root, bg="blue")
login_frame.pack(pady=50)

tk.Label(login_frame, text="Username:", fg="white", bg="blue", font=("Arial", 12)).grid(row=0, column=0, pady=5)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=0, column=1, pady=5)

tk.Label(login_frame, text="Password:", fg="white", bg="blue", font=("Arial", 12)).grid(row=1, column=0, pady=5)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1, pady=5)

tk.Button(login_frame, text="Login", command=login, bg="white", fg="blue").grid(row=2, columnspan=2, pady=10)

# Activator Frame
activator_frame = tk.Frame(root, bg="blue")

tk.Label(activator_frame, text="AK WINDOWS ACTIVATOR", font=("Arial", 16, "bold"), bg="blue", fg="white").pack(pady=10)
tk.Button(activator_frame, text="Activate Windows", command=start_activation, bg="white", fg="blue").pack(pady=10)

progress_var = tk.StringVar(value="Progress: 0%")
progress_label = tk.Label(activator_frame, textvariable=progress_var, font=("Arial", 12), bg="blue", fg="white")
progress_label.pack(pady=5)

# CMD Output Box
output_text = tk.Text(activator_frame, height=8, width=50, bg="black", fg="lime", insertbackground="white")
output_text.pack(pady=10)

# Disclaimer
tk.Label(root, text="NOT COPYWRITING AND WINDOWS", font=("Arial", 8), bg="blue", fg="white").pack(side="bottom", pady=5)

root.mainloop()
