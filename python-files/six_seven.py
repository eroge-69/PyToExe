import tkinter as tk
from tkinter import messagebox

def check_answer():
    answer = entry.get()
    if answer.strip() == "21":
        messagebox.showinfo("Result", "your goddam right")
    else:
        messagebox.showinfo("Result", "sybau")

# Create window
root = tk.Tk()
root.title("Quick Math")
root.geometry("300x150")

# Question label
label = tk.Label(root, text="What's 9 + 10?", font=("Arial", 14))
label.pack(pady=10)

# Input field
entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=5)

# Submit button
button = tk.Button(root, text="Submit", command=check_answer, font=("Arial", 12))
button.pack(pady=10)

root.mainloop()
