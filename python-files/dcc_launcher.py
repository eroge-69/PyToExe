
# Online Python - IDE, Editor, Compiler, Interpreter

def sum(a, b):
    return (a + b)

a = int(input('Enter 1st number: '))
b = int(input('Enter 2nd number: '))

print(f'Sum of {a} and {b} is {sum(a, b)}')
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# --------- PATHS TO YOUR SOFTWARE (Update these to match your PC) ----------
APP_PATHS = {
    "Maya": r"C:\Program Files\Autodesk\Maya2018\bin\maya.exe",
    "Substance Painter": r"C:\Program Files\Allegorithmic\Substance Painter\Substance Painter.exe",
    "ZBrush": r"C:\Program Files\Pixologic\ZBrush 2021\ZBrush.exe",
    "Houdini": r"C:\Program Files\Side Effects Software\Houdini 19.5.569\bin\houdinifx.exe",
    "Nuke": r"C:\Program Files\Nuke13.2v4\Nuke13.2.exe"
}

# --------- FUNCTION TO OPEN APP ----------
def open_app(app_name):
    path = APP_PATHS.get(app_name)
    if path and os.path.exists(path):
        try:
            subprocess.Popen(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open {app_name}\n{e}")
    else:
        messagebox.showerror("Error", f"Path not found for {app_name}.\nPlease update the path.")

# --------- UI SETUP ----------
root = tk.Tk()
root.title("DCC Launcher")
root.geometry("400x300")
root.resizable(False, False)

title_label = tk.Label(root, text="DCC Pipeline Launcher", font=("Segoe UI", 14, "bold"))
title_label.pack(pady=15)

for app in APP_PATHS.keys():
    btn = tk.Button(root, text=f"Open {app}", font=("Segoe UI", 11), width=25, 
                    command=lambda a=app: open_app(a))
    btn.pack(pady=5)

exit_btn = tk.Button(root, text="Exit", font=("Segoe UI", 11), width=25, command=root.quit)
exit_btn.pack(pady=20)

root.mainloop()
