
import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        entry_price = float(entry_price_entry.get())
        sl_pips = float(sl_entry.get())
        tp_pips = float(tp_entry.get())

        sl_price = entry_price - (sl_pips * 0.0001)
        tp_price = entry_price + (tp_pips * 0.0001)

        result_label.config(text=f"SL Price: {sl_price:.5f}\nTP Price: {tp_price:.5f}")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers.")

def reset_fields():
    entry_price_entry.delete(0, tk.END)
    sl_entry.delete(0, tk.END)
    tp_entry.delete(0, tk.END)
    result_label.config(text="")

root = tk.Tk()
root.title("Infinity SL/TP Master")
root.geometry("300x250")
root.configure(bg="#1e1e2f")

tk.Label(root, text="Entry Price", fg="white", bg="#1e1e2f").pack()
entry_price_entry = tk.Entry(root)
entry_price_entry.pack()

tk.Label(root, text="SL (Pips)", fg="white", bg="#1e1e2f").pack()
sl_entry = tk.Entry(root)
sl_entry.pack()

tk.Label(root, text="TP (Pips)", fg="white", bg="#1e1e2f").pack()
tp_entry = tk.Entry(root)
tp_entry.pack()

tk.Button(root, text="Calculate", command=calculate).pack(pady=5)
tk.Button(root, text="Reset", command=reset_fields).pack()

result_label = tk.Label(root, text="", fg="cyan", bg="#1e1e2f")
result_label.pack(pady=10)

root.mainloop()
