import random
import string
import tkinter as tk
from tkinter import messagebox

def generate_password():
    part1 = chr(random.randint(65, 72))          # A-H
    part2 = chr(random.randint(97, 107))         # a-k
    part3 = chr(random.randint(109, 122))        # m-z
    part4 = chr(random.randint(74, 90))          # J-Z
    part5 = str(random.randint(100, 999))        # 100-999
    symbols = [33, 35, 36, 37, 42, 43, 47, 61, 63, 64]  # ! # $ % * + / = ? @
    part6 = chr(random.choice(symbols))
    part7 = str(random.randint(1000, 9999))      # 1000-9999

    password = part1 + part2 + part3 + part4 + part5 + part6 + part7
    entry.delete(0, tk.END)
    entry.insert(0, password)

def copy_to_clipboard():
    pwd = entry.get()
    if pwd:
        root.clipboard_clear()
        root.clipboard_append(pwd)
        root.update()
        messagebox.showinfo("Copied", "Geslo je kopirano v odložišče!")

# GUI
root = tk.Tk()
root.title("Password Generator")

entry = tk.Entry(root, width=30, font=("Arial", 14))
entry.pack(pady=10)

btn_generate = tk.Button(root, text="Generate", command=generate_password, font=("Arial", 12))
btn_generate.pack(pady=5)

btn_copy = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard, font=("Arial", 12))
btn_copy.pack(pady=5)

root.mainloop()
