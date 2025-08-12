# replace_spaces_gui.py
import tkinter as tk
from tkinter import messagebox

def replace_spaces():
    text = entry.get()
    replaced = text.replace(" ", "-")
    output_var.set(replaced)

# Create main window
root = tk.Tk()
root.title("Replace Spaces with -")
root.geometry("400x200")

# Input label and field
tk.Label(root, text="Enter your text:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# Button to process
tk.Button(root, text="Replace Spaces", command=replace_spaces).pack(pady=5)

# Output label
output_var = tk.StringVar()
tk.Label(root, textvariable=output_var, fg="blue").pack(pady=10)

root.mainloop()
