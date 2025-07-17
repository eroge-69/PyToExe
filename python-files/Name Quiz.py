import tkinter as tk
from tkinter import simpledialog, messagebox

# Create hidden app window
root = tk.Tk()
root.withdraw()

# Ask for the name
name = simpledialog.askstring("Input", "What is your name?")

# Make sure the user didn't cancel
if name:
    if name.lower() == "krisu":
        messagebox.showinfo("Response", "It's okay to be gay")
    else:
        messagebox.showinfo("Response", f"Nice to meet you, {name}")

