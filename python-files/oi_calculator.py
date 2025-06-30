
import tkinter as tk
from tkinter import messagebox

def calculate_percentage():
    try:
        first_value = float(entry_first.get())
        second_value = float(entry_second.get())
        change = ((first_value - second_value) / first_value) * 100
        result_label.config(text=f"Change: {change:.2f}%")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# GUI Setup
root = tk.Tk()
root.title("Open Interest % Drop Calculator")
root.geometry("300x200")
root.resizable(False, False)

# Widgets
tk.Label(root, text="First Value (Previous)").pack(pady=5)
entry_first = tk.Entry(root)
entry_first.pack()

tk.Label(root, text="Second Value (Current)").pack(pady=5)
entry_second = tk.Entry(root)
entry_second.pack()

tk.Button(root, text="Calculate % Drop", command=calculate_percentage).pack(pady=10)
result_label = tk.Label(root, text="Change: ")
result_label.pack(pady=5)

# Run the app
root.mainloop()
