import os
import shutil
import subprocess
from tkinter import Tk, filedialog

def generate_dummy_exe(output_path):
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def generate_dummy_exe(output_path):
    with open(output_path, 'wb') as f:
        f.write(b'MZ')  # Basic EXE header
        f.write(os.urandom(512))  # Random filler

def select_exe():
    filepath = filedialog.askopenfilename(
        title="Select an EXE file",
        filetypes=[("Executable Files", "*.exe")]
    )
    if filepath:
        exe_path.set(filepath)

def generate_or_use_exe():
    name = exe_name.get().strip()
    if not name:
        messagebox.showwarning("Input Required", "Please enter a new EXE name.")
        return

    if not name.endswith(".exe"):
        name += ".exe"

    new_exe_path = os.path.join(os.getcwd(), name)

    if use_dummy.get():
        generate_dummy_exe(new_exe_path)
        messagebox.showinfo("Success", f"Dummy EXE created as: {name}")
    else:
        original = exe_path.get()
        if not original or not os.path.exists(original):
            messagebox.showerror("Error", "No EXE file selected or path is invalid.")
            return
        shutil.copy(original, new_exe_path)
        messagebox.showinfo("Success", f"EXE copied and renamed to: {name}")

    try:
        subprocess.Popen(
            new_exe_path,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        messagebox.showinfo("Running", f"{name} is now running silently.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run EXE: {e}")

# GUI Setup
root = tk.Tk()
root.title("EXE Generator & Renamer")
root.geometry("420x300")
root.resizable(False, False)

tk.Label(root, text="EXE Renamer + Launcher", font=("Segoe UI", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=5)

use_dummy = tk.BooleanVar()
use_dummy.set(True)

tk.Radiobutton(frame, text="Generate Dummy EXE", variable=use_dummy, value=True).grid(row=0, column=0, sticky="w", padx=10)
tk.Radiobutton(frame, text="Upload Your EXE", variable=use_dummy, value=False).grid(row=1, column=0, sticky="w", padx=10)

exe_path = tk.StringVar()
tk.Button(root, text="Select EXE", command=select_exe).pack(pady=5)
tk.Entry(root, textvariable=exe_path, width=50).pack(padx=10)

tk.Label(root, text="New EXE Name (e.g., Windows Runtime.exe):").pack(pady=5)
exe_name = tk.StringVar()
tk.Entry(root, textvariable=exe_name, width=40).pack()

tk.Button(root, text="Generate & Launch", command=generate_or_use_exe, bg="#4caf50", fg="white", padx=10, pady=5).pack(pady=15)

tk.Label(root, text="Made for educational use only", font=("Segoe UI", 8)).pack(side="bottom", pady=5)

root.mainloop()
