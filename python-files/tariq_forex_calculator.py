import tkinter as tk
from tkinter import ttk, messagebox

# Pip values per pair
PAIR_PIPS = {
    "NQ": 20,
    "SP": 50,
    "EURUSD": 10,
    "GBPUSD": 10,
    "XAUUSD": 100,
    "US30": 10
}

def calculate():
    try:
        acc_size = float(account_size.get())
        risk_perc = float(risk_percent.get())
        risk_amt = round((acc_size * risk_perc) / 100, 2)
        risk_dollar.set(risk_amt)

        pair = pair_choice.get()
        pip_value = PAIR_PIPS.get(pair, 10)

        stop = float(stop_size.get())
        lot = round(risk_amt / (stop * pip_value), 2)
        lot_size.set(lot)

        tgt = float(target.get())
        pips_needed = round(tgt / (lot * pip_value), 2)
        pips_to_win.set(pips_needed)

    except Exception as e:
        messagebox.showerror("Error", f"Please check your inputs.\n\n{e}")

def clear_all():
    for var in [account_size, risk_percent, risk_dollar, target, stop_size, lot_size, pips_to_win]:
        var.set("")
    pair_choice.set("EURUSD")

def clear_stop():
    stop_size.set("")

def copy_lot():
    try:
        import pyperclip
        pyperclip.copy(str(lot_size.get()))
        messagebox.showinfo("Copied", "Lot size copied to clipboard.")
    except:
        messagebox.showwarning("Warning", "Install pyperclip to copy: pip install pyperclip")

# GUI setup
root = tk.Tk()
root.title("Tariq Forex Calculator")
root.geometry("400x500")
root.resizable(False, False)

# Variables
account_size = tk.StringVar()
risk_percent = tk.StringVar()
risk_dollar = tk.StringVar()
pair_choice = tk.StringVar(value="EURUSD")
target = tk.StringVar()
stop_size = tk.StringVar()
lot_size = tk.StringVar()
pips_to_win = tk.StringVar()

def add_row(row, label_text, var, options=None, readonly=False):
    tk.Label(root, text=label_text).grid(row=row, column=0, sticky='w', padx=10, pady=5)
    if options:
        combo = ttk.Combobox(root, textvariable=var, values=options)
        combo.grid(row=row, column=1, padx=10, pady=5)
    else:
        entry = tk.Entry(root, textvariable=var, state='readonly' if readonly else 'normal')
        entry.grid(row=row, column=1, padx=10, pady=5)

add_row(0, "Account Size 💲", account_size, ["25000", "50000", "100000", "200000"])
add_row(1, "Risk % 📉", risk_percent, ["0.5", "1", "1.5", "2"])
add_row(2, "Risk $ 💵", risk_dollar, None, readonly=True)
add_row(3, "Pair 🔁", pair_choice, list(PAIR_PIPS.keys()))
add_row(4, "Target 🎯", target)
add_row(5, "Stop Size (pips) 🛑", stop_size)
add_row(6, "Lot Size 📊", lot_size)
add_row(7, "Pips Needed to Win 🏁", pips_to_win, None, readonly=True)

# Buttons
tk.Button(root, text="Calculate", width=18, command=calculate).grid(row=8, column=0, pady=10)
tk.Button(root, text="Clear", width=18, command=clear_all).grid(row=8, column=1, pady=10)
tk.Button(root, text="Clear Stop Size", width=18, command=clear_stop).grid(row=9, column=0, pady=5)
tk.Button(root, text="Copy Lot Size", width=18, command=copy_lot).grid(row=9, column=1, pady=5)

root.mainloop()
