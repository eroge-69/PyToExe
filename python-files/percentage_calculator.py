import tkinter as tk
from tkinter import ttk

def calculate():
    try:
        number = float(entry_number.get())
        percent = float(entry_percent.get())
        result = (number * percent) / 100
        result_label.config(text=f"Result: {result}")
    except ValueError:
        result_label.config(text="Invalid input!")

root = tk.Tk()
root.title("Tiny % Calculator")
root.geometry("300x300")
root.resizable(False, False)

ttk.Label(root, text="Number:").pack(pady=(10, 0))
entry_number = ttk.Entry(root, justify='center')
entry_number.pack()

ttk.Label(root, text="Percentage (%):").pack(pady=(5, 0))
entry_percent = ttk.Entry(root, justify='center')
entry_percent.pack()

ttk.Button(root, text="Calculate", command=calculate).pack(pady=10)

result_label = ttk.Label(root, text="Result: ")
result_label.pack()

root.mainloop()
