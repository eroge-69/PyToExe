import tkinter as tk
from tkinter import StringVar

def update_results(*args):
    try:
        balance = float(balance_var.get())
        stop_loss = float(stop_loss_var.get())

        rpt = balance * 0.03
        quantity = rpt / stop_loss

        result_label.config(text=f"RPT (3%): ₹{rpt:.2f}\nQuantity: {quantity:.4f}")
    except (ValueError, ZeroDivisionError):
        result_label.config(text="RPT (3%): ₹0.00\nQuantity: 0.0000")

# Setup GUI
root = tk.Tk()
root.title("Trading Quantity Calculator")
root.geometry("320x200")

balance_var = StringVar()
stop_loss_var = StringVar()

balance_var.trace_add("write", update_results)
stop_loss_var.trace_add("write", update_results)

# UI Elements
tk.Label(root, text="Account Balance (₹):").pack(pady=5)
tk.Entry(root, textvariable=balance_var).pack(pady=5)

tk.Label(root, text="Stop Loss (₹ per unit):").pack(pady=5)
tk.Entry(root, textvariable=stop_loss_var).pack(pady=5)

result_label = tk.Label(root, text="RPT (3%): ₹0.00\nQuantity: 0.0000", font=("Arial", 12), fg="blue")
result_label.pack(pady=20)

root.mainloop()
