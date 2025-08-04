import tkinter as tk
from tkinter import messagebox
import json
import os

SAVE_FILE = "last_session.json"

def save_inputs(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def load_inputs():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return {}

def calculate(event=None):
    try:
        capital = float(entry_capital.get())
        risk_percent = float(entry_risk.get()) / 100
        stop_loss_value = float(entry_stop_loss.get())
        entry_price = float(entry_entry_price.get())
        target_price = float(entry_target_price.get())
        account_type = account_type_var.get()
        leverage = float(entry_leverage.get()) if entry_leverage.get() else 1

        stop_loss_percent = stop_loss_value / entry_price

        capital_at_risk = capital * risk_percent
        if account_type == "spot":
            position_size = capital_at_risk / stop_loss_percent
        else:
            position_size = capital_at_risk / (stop_loss_percent * leverage)

        nominal_position = position_size * leverage
        stop_loss_dollar = stop_loss_percent * nominal_position

        rr_ratio = (target_price - entry_price) / (entry_price - (entry_price - stop_loss_value)) if stop_loss_value != 0 else 0
        potential_profit = (target_price - entry_price) * position_size

        result = f"""Position Size: ${position_size:,.2f}
Nominal Position: ${nominal_position:,.2f}
Capital at Risk: ${capital_at_risk:,.2f}
Stop Loss (Value): ${stop_loss_dollar:,.2f}
Stop Loss (%): {stop_loss_percent*100:.2f}%
Drawdown: {(capital_at_risk / capital) * 100:.2f}%
---
R:R Ratio: {rr_ratio:.2f}
Potential Profit: ${potential_profit:,.2f}
"""

        messagebox.showinfo("Result", result)

        save_inputs({
            "capital": entry_capital.get(),
            "risk": entry_risk.get(),
            "stop_loss": entry_stop_loss.get(),
            "leverage": entry_leverage.get(),
            "entry_price": entry_entry_price.get(),
            "target_price": entry_target_price.get(),
            "account_type": account_type
        })

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

def reset_fields():
    entry_capital.delete(0, 'end')
    entry_risk.delete(0, 'end')
    entry_stop_loss.delete(0, 'end')
    entry_leverage.delete(0, 'end')
    entry_entry_price.delete(0, 'end')
    entry_target_price.delete(0, 'end')

root = tk.Tk()
root.title("Position Size Calculator")

tk.Label(root, text="Capital ($):").grid(row=0, column=0, sticky="w")
entry_capital = tk.Entry(root)
entry_capital.grid(row=0, column=1)

tk.Label(root, text="Risk %:").grid(row=1, column=0, sticky="w")
entry_risk = tk.Entry(root)
entry_risk.grid(row=1, column=1)

tk.Label(root, text="Stop Loss ($ diff):").grid(row=2, column=0, sticky="w")
entry_stop_loss = tk.Entry(root)
entry_stop_loss.grid(row=2, column=1)

tk.Label(root, text="Leverage (1 if spot):").grid(row=3, column=0, sticky="w")
entry_leverage = tk.Entry(root)
entry_leverage.grid(row=3, column=1)

tk.Label(root, text="Entry Price:").grid(row=4, column=0, sticky="w")
entry_entry_price = tk.Entry(root)
entry_entry_price.grid(row=4, column=1)

tk.Label(root, text="Target Price:").grid(row=5, column=0, sticky="w")
entry_target_price = tk.Entry(root)
entry_target_price.grid(row=5, column=1)

account_type_var = tk.StringVar(value="spot")
tk.Radiobutton(root, text="Spot", variable=account_type_var, value="spot").grid(row=6, column=0, sticky="w")
tk.Radiobutton(root, text="Leverage", variable=account_type_var, value="leverage").grid(row=6, column=1, sticky="w")

tk.Button(root, text="Calculate", command=calculate).grid(row=7, column=0, columnspan=2)
tk.Button(root, text="Reset", command=reset_fields).grid(row=8, column=0, columnspan=2)

last_inputs = load_inputs()
entry_capital.insert(0, last_inputs.get("capital", ""))
entry_risk.insert(0, last_inputs.get("risk", ""))
entry_stop_loss.insert(0, last_inputs.get("stop_loss", ""))
entry_leverage.insert(0, last_inputs.get("leverage", ""))
entry_entry_price.insert(0, last_inputs.get("entry_price", ""))
entry_target_price.insert(0, last_inputs.get("target_price", ""))
account_type_var.set(last_inputs.get("account_type", "spot"))

root.bind("<Return>", calculate)

root.mainloop()
