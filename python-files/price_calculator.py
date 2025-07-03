import tkinter as tk
from tkinter import messagebox

def calculate_price():
    try:
        volume = float(volume_entry.get())
        price = volume * 0.675
        result_var.set(f"{price:.3f}")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number.")

def copy_result():
    root.clipboard_clear()
    root.clipboard_append(result_var.get())
    root.update()
    messagebox.showinfo("Copied", "Result copied to clipboard.")

root = tk.Tk()
root.title("Product Price Calculator")
root.geometry("300x150")
root.resizable(False, False)

tk.Label(root, text="Enter Volume:").pack(pady=5)
volume_entry = tk.Entry(root, width=20)
volume_entry.pack()

tk.Button(root, text="Calculate", command=calculate_price).pack(pady=5)

result_var = tk.StringVar()
tk.Entry(root, textvariable=result_var, width=20, state="readonly").pack()

tk.Button(root, text="Copy Result", command=copy_result).pack(pady=5)

root.mainloop()
