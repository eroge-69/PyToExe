
import tkinter as tk
from tkinter import messagebox

def convert_price_to_degree():
    try:
        price = float(entry.get())
        degree = round(price % 360, 2)
        result_label.config(text=f"Degree: {degree}°")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number")

# GUI setup
root = tk.Tk()
root.title("Price to Degree Converter")
root.geometry("300x150")

tk.Label(root, text="Enter Price:").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="Convert", command=convert_price_to_degree).pack(pady=5)
result_label = tk.Label(root, text="Degree: ")
result_label.pack(pady=5)

root.mainloop()
