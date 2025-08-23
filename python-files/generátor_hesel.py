import tkinter as tk
import random
import string
from tkinter import messagebox

def generate_password():
    length = int(length_entry.get())
    chars = ''
    if lower_var.get():
        chars += string.ascii_lowercase
    if upper_var.get():
        chars += string.ascii_uppercase
    if digits_var.get():
        chars += string.digits
    if symbols_var.get():
        chars += string.punctuation
    if not chars:
        messagebox.showerror("Chyba", "Vyberte alespoň jednu možnost!")
        return
    password = ''.join(random.choice(chars) for _ in range(length))
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

root = tk.Tk()
root.title("Generátor hesel")

tk.Label(root, text="Délka hesla:").grid(row=0, column=0)
length_entry = tk.Entry(root)
length_entry.grid(row=0, column=1)
length_entry.insert(0, "12")

lower_var = tk.BooleanVar(value=True)
upper_var = tk.BooleanVar(value=True)
digits_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Malá písmena", variable=lower_var).grid(row=1, column=0)
tk.Checkbutton(root, text="Velká písmena", variable=upper_var).grid(row=1, column=1)
tk.Checkbutton(root, text="Číslice", variable=digits_var).grid(row=2, column=0)
tk.Checkbutton(root, text="Speciální znaky", variable=symbols_var).grid(row=2, column=1)

tk.Button(root, text="Generovat", command=generate_password).grid(row=3, column=0, columnspan=2)

password_entry = tk.Entry(root, width=30)
password_entry.grid(row=4, column=0, columnspan=2)

root.mainloop()
