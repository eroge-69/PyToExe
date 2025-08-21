import string
import random
import tkinter as tk
from tkinter import messagebox

def generate_password():
    try:
        length = int(length_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Password length must be a number")
        return

    characterList = ""
    if digits_var.get():
        characterList += string.digits
    if letters_var.get():
        characterList += string.ascii_letters
    if specials_var.get():
        characterList += string.punctuation

    if not characterList:
        messagebox.showerror("Error", "Please select at least one character set")
        return

    password = "".join(random.choice(characterList) for _ in range(length))
    result_var.set(password)

def copy_to_clipboard():
    password = result_var.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()
        messagebox.showinfo("Copied", "Password copied to clipboard!")
    else:
        messagebox.showwarning("Warning", "No password to copy!")
        
# ---------------- GUI ----------------
root = tk.Tk()
root.title("Password Generator")
root.geometry("400x350")

# Password length
tk.Label(root, text="Enter password length:").pack(pady=5)
length_entry = tk.Entry(root)
length_entry.pack(pady=5)

# Initialize BooleanVars
digits_var = tk.BooleanVar()  # Digits variable
letters_var = tk.BooleanVar()  # Letters variable
specials_var = tk.BooleanVar()  # Special characters variable

# Create Checkbuttons
tk.Checkbutton(root, text="Digits", variable=digits_var).pack(anchor="w", padx=20)
tk.Checkbutton(root, text="Letters", variable=letters_var).pack(anchor="w", padx=20)
tk.Checkbutton(root, text="Special Characters", variable=specials_var).pack(anchor="w", padx=20)

# Generate button
tk.Button(root, text="Generate Password", command=generate_password).pack(pady=15)

# Result
result_var = tk.StringVar()  # Password display variable
tk.Entry(root, textvariable=result_var, width=40, state="readonly").pack(pady=10)

# Copy button
tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=5)

root.mainloop()
