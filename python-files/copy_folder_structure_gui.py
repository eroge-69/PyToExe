
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_source():
    path = filedialog.askdirectory(title="Select Source Folder")
    if path:
        source_var.set(path)

def select_target():
    path = filedialog.askdirectory(title="Select Destination Folder")
    if path:
        target_var.set(path)

def run_robocopy():
    src = source_var.get()
    dst = target_var.get()
    if not os.path.isdir(src):
        messagebox.showerror("Error", "Source folder is invalid or not selected.")
        return
    if not os.path.isdir(dst):
        messagebox.showerror("Error", "Destination folder is invalid or not selected.")
        return

    cmd = ['robocopy', src, dst, '/e', '/xf', '*.*']
    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", "Folder structure copied successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Robocopy Error", f"Robocopy exited with code {e.returncode}")

root = tk.Tk()
root.title("Copy Folder Structure Only")
root.geometry("500x180")
root.resizable(False, False)

source_var = tk.StringVar()
target_var = tk.StringVar()

tk.Label(root, text="Source Folder:").pack(pady=(10,0))
tk.Entry(root, textvariable=source_var, width=60).pack()
tk.Button(root, text="Browse...", command=select_source).pack(pady=(0,10))

tk.Label(root, text="Destination Folder:").pack()
tk.Entry(root, textvariable=target_var, width=60).pack()
tk.Button(root, text="Browse...", command=select_target).pack(pady=(0,10))

tk.Button(root, text="Copy Structure", command=run_robocopy).pack(pady=5)

root.mainloop()
