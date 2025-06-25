# py2exe_converter.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

# Function to run PyInstaller
def convert_to_exe():
    py_path = filedialog.askopenfilename(title="Select your .py script", filetypes=[("Python Files", "*.py")])
    if not py_path:
        return

    icon_path = filedialog.askopenfilename(title="(Optional) Select an .ico icon file", filetypes=[("Icon Files", "*.ico")])

    cmd = ["pyinstaller", "--onefile", "--noconsole"]
    if icon_path:
        cmd += [f"--icon={icon_path}"]
    cmd.append(py_path)

    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"EXE created! Check the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"PyInstaller failed: {e}")

# Setup GUI
root = tk.Tk()
root.title("Python to EXE Converter")
root.geometry("400x200")
root.resizable(False, False)

label = tk.Label(root, text="Select a Python script to convert to EXE", font=("Arial", 12))
label.pack(pady=20)

convert_btn = tk.Button(root, text="Choose .py file & Convert", command=convert_to_exe, font=("Arial", 12), bg="lime", fg="black")
convert_btn.pack(pady=10)

exit_btn = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12))
exit_btn.pack(pady=10)

root.mainloop()
