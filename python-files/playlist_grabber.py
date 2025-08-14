import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys

# Get path to current script folder
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
SLDL_PATH = os.path.join(BASE_DIR, "sldl.exe")  # Use bundled exe

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if filename:
        csv_file_var.set(filename)

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        dest_folder_var.set(folder)

def run_sldl():
    csv_file = csv_file_var.get()
    username = username_var.get()
    password = password_var.get()
    name_format = name_format_var.get()
    pref_format = pref_format_var.get()
    dest_folder = dest_folder_var.get()

    if extended_mix_var.get():
        name_format = name_format.replace("{title}", "{title} (Extended Mix)")

    if not csv_file or not username or not password:
        messagebox.showerror("Error", "CSV file, username, and password are required.")
        return

    if not os.path.exists(SLDL_PATH):
        messagebox.showerror("Error", f"sldl.exe not found at {SLDL_PATH}")
        return

    cmd = [
        SLDL_PATH,
        csv_file,
        "--user", username,
        "--pass", password,
        "--name-format", name_format,
        "--pref-format", pref_format
    ]
    if dest_folder:
        cmd.extend(["--dest", dest_folder])

    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", "Download complete!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to run sldl.exe:\n{e}")

# GUI setup
root = tk.Tk()
root.title("MD's Soulseek Spotify Playlist Grabber")

csv_file_var = tk.StringVar()
username_var = tk.StringVar()
password_var = tk.StringVar()
name_format_var = tk.StringVar(value="{title} - {artist}")
pref_format_var = tk.StringVar(value="mp3")
dest_folder_var = tk.StringVar()
extended_mix_var = tk.BooleanVar()

# CSV
tk.Label(root, text="CSV File:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=csv_file_var, width=40).grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

# Username
tk.Label(root, text="Username:").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=username_var).grid(row=1, column=1, columnspan=2, sticky="we")

# Password
tk.Label(root, text="Password:").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=password_var, show="*").grid(row=2, column=1, columnspan=2, sticky="we")

# Name Format
tk.Label(root, text="Name Format:").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=name_format_var).grid(row=3, column=1, columnspan=2, sticky="we")

# Extended Mix
tk.Checkbutton(root, text="Add 'Extended Mix' to Title", variable=extended_mix_var).grid(row=4, column=0, columnspan=3, sticky="w")

# Preferred Format
tk.Label(root, text="Preferred Format:").grid(row=5, column=0, sticky="e")
tk.OptionMenu(root, pref_format_var, "mp3", "flac", "wav").grid(row=5, column=1, columnspan=2, sticky="we")

# Destination Folder
tk.Label(root, text="Destination Folder:").grid(row=6, column=0, sticky="e")
tk.Entry(root, textvariable=dest_folder_var, width=40).grid(row=6, column=1)
tk.Button(root, text="Browse", command=browse_folder).grid(row=6, column=2)

# Run Button
tk.Button(root, text="Run SLDL", command=run_sldl).grid(row=7, column=0, columnspan=3, pady=10)

root.mainloop()
