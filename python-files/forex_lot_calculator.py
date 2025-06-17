
import tkinter as tk
from tkinter import messagebox

def calculate_lot():
    try:
        risk = float(entry_risk.get())
        stop_loss = float(entry_sl.get())
        pip_value = float(entry_pip_value.get())

        lot_size = risk / (stop_loss * pip_value)
        result_label.config(text=f"Lot Size: {round(lot_size, 3)} lots")

    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numbers.")

# GUI setup
root = tk.Tk()
root.title("Forex Lot Size Calculator")
root.geometry("300x200")

tk.Label(root, text="Risk Amount ($):").pack()
entry_risk = tk.Entry(root)
entry_risk.pack()

tk.Label(root, text="Stop-Loss (pips):").pack()
entry_sl = tk.Entry(root)
entry_sl.pack()

tk.Label(root, text="Pip Value per Lot ($):").pack()
entry_pip_value = tk.Entry(root)
entry_pip_value.insert(0, "10")
entry_pip_value.pack()

tk.Button(root, text="Calculate", command=calculate_lot).pack(pady=10)
result_label = tk.Label(root, text="Lot Size: ")
result_label.pack()

root.mainloop()
