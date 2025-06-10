
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Define default settings file
settings_file = "settings.json"

# Define pip cost mapping
pip_values = {
    "NQ": 20,
    "SP": 50,
    "EURUSD": 10,
    "GBPUSD": 10,
    "XAUUSD": 100,
    "US30": 10
}

# Load saved settings
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    return {}

# Save current settings
def save_settings():
    data = {
        "account_size": account_size_var.get(),
        "risk_percent": risk_percent_var.get(),
        "pair": pair_var.get(),
        "target": target_var.get(),
        "stop_size": stop_size_var.get()
    }
    with open(settings_file, "w") as f:
        json.dump(data, f)

# Calculate the Risk $ and Lot Size
def calculate():
    try:
        account_size = float(account_size_var.get())
        risk_percent = float(risk_percent_var.get().strip('%')) / 100
        stop_size = float(stop_size_var.get())
        target = float(target_var.get())
        pair = pair_var.get()
        pip_value = pip_values.get(pair, 10)

        risk_amount = account_size * risk_percent
        lot_size = risk_amount / (stop_size * pip_value)
        pips_needed = target / (lot_size * pip_value)

        risk_dollar_var.set(f"${risk_amount:.2f}")
        lot_size_var.set(f"{lot_size:.2f}")
        pips_needed_var.set(f"{pips_needed:.2f}")

        save_settings()

    except Exception as e:
        messagebox.showerror("Error", f"Calculation failed: {e}")

# Clear all fields
def clear_all():
    account_size_var.set("")
    risk_percent_var.set("")
    risk_dollar_var.set("")
    pair_var.set("")
    target_var.set("")
    stop_size_var.set("")
    lot_size_var.set("")
    pips_needed_var.set("")

# Clear only stop size
def clear_stop_size():
    stop_size_var.set("")

# Main app window
root = tk.Tk()
root.title("💼 Tariq Forex Calculator")
root.geometry("500x500")

# Load previous settings
settings = load_settings()

# Variables
account_size_var = tk.StringVar(value=settings.get("account_size", ""))
risk_percent_var = tk.StringVar(value=settings.get("risk_percent", ""))
risk_dollar_var = tk.StringVar()
pair_var = tk.StringVar(value=settings.get("pair", ""))
target_var = tk.StringVar(value=settings.get("target", ""))
stop_size_var = tk.StringVar(value=settings.get("stop_size", ""))
lot_size_var = tk.StringVar()
pips_needed_var = tk.StringVar()

# UI Layout
ttk.Label(root, text="💰 Account Size:").pack()
ttk.Entry(root, textvariable=account_size_var).pack()

ttk.Label(root, text="📊 Risk %:").pack()
risk_percent_dropdown = ttk.Combobox(root, textvariable=risk_percent_var, values=["0.50%", "1%", "2%"])
risk_percent_dropdown.pack()

ttk.Label(root, text="💵 Risk $:").pack()
ttk.Entry(root, textvariable=risk_dollar_var, state="readonly").pack()

ttk.Label(root, text="💱 Pair:").pack()
ttk.Combobox(root, textvariable=pair_var, values=list(pip_values.keys())).pack()

ttk.Label(root, text="🎯 Target:").pack()
ttk.Entry(root, textvariable=target_var).pack()

ttk.Label(root, text="🚫 Stop Size (pips):").pack()
ttk.Entry(root, textvariable=stop_size_var).pack()

ttk.Label(root, text="📏 Lot Size:").pack()
ttk.Entry(root, textvariable=lot_size_var, state="readonly").pack()

ttk.Label(root, text="🧮 Pips Needed to Win:").pack()
ttk.Entry(root, textvariable=pips_needed_var, state="readonly").pack()

# Buttons
ttk.Button(root, text="✅ Calculate", command=calculate).pack(pady=5)
ttk.Button(root, text="🧼 Clear All", command=clear_all).pack(pady=5)
ttk.Button(root, text="🔄 Clear Stop Size", command=clear_stop_size).pack(pady=5)

root.mainloop()
