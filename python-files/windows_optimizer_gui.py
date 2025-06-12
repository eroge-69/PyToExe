import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_script(script_path, script_type):
    try:
        if script_type == "bat":
            subprocess.run(["start", "cmd", "/c", script_path], shell=True)
        elif script_type == "ps1":
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], shell=True)
        elif script_type == "reg":
            subprocess.run(["regedit", "/s", script_path], shell=True)
        messagebox.showinfo("Success", f"Executed: {os.path.basename(script_path)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Windows Optimizer By SRS")
root.geometry("400x400")
root.config(bg="#1e1e1e")

tk.Label(root, text="Windows Optimizer Tools", font=("Helvetica", 16), bg="#1e1e1e", fg="white").pack(pady=10)

buttons = [
    ("Clean Temp Files", "scripts/clean_temp.bat", "bat"),
    ("Apply FPS 240 Tweak", "scripts/FPS_240_TWEAK by srs .reg", "reg"),
    ("Run Game Boost Script", "scripts/game_boost.ps1", "ps1"),
    ("MSI App Player Boost", "scripts/GAMING_BOOST_FOR_MSI_APP_PLAYER.reg", "reg"),
    ("Mouse Accuracy Boost", "scripts/Mouse Accuracy Boost .reg", "reg"),
    ("Fix Keyboard Input Lag", "scripts/Windows_Keyboard_InputLag_Fix.reg", "reg"),
]

for text, path, type_ in buttons:
    tk.Button(root, text=text, width=40, bg="#007acc", fg="white", font=("Helvetica", 10),
              command=lambda p=path, t=type_: run_script(p, t)).pack(pady=5)

root.mainloop()
