import tkinter as tk
import subprocess
import random
import os
base_number = 14405034

def check_key():
    key = entry.get()
    parts = key.split("S")
    valid = True
    for part in parts:
        if not part.isdigit() or int(part) < base_number or int(part) > base_number + 99439979:
            valid = False
            break
    if valid:
        result_label.config(text="VALID KEY", fg="lime")
        os.system("start cmd /k echo e")
    else:
        result_label.config(text="INVALID KEY", fg="red")

root = tk.Tk()
root.title("S.A.N.Y.I")
root.geometry("400x200")
root.configure(bg="black")

label = tk.Label(root, text="Enter key:", font=("Courier", 12), fg="cyan", bg="black")
label.pack(pady=10)

entry = tk.Entry(root, font=("Courier", 12), width=35, justify="center")
entry.pack(pady=5)

check_button = tk.Button(root, text="Check Key", font=("Courier", 12, "bold"), fg="yellow", bg="black",
                         activebackground="cyan", command=check_key)
check_button.pack(pady=10)

result_label = tk.Label(root, text="", font=("Courier", 12), fg="lime", bg="black")
result_label.pack(pady=10)

root.mainloop()
