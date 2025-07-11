
import tkinter as tk
from tkinter import ttk, messagebox

def round_lot(lot):
    return round(lot * 100) / 100

def calculate():
    try:
        capital = float(capital_entry.get())
        leverage = float(leverage_entry.get())
        stop_loss = float(stop_loss_entry.get())
        risk_percent = float(risk_entry.get())

        risk_amount = (risk_percent / 100) * capital
        raw_lot_size = risk_amount / (stop_loss * 10)
        lot_size = round_lot(raw_lot_size)

        rr3 = round(risk_amount * 3, 2)
        rr10 = round(risk_amount * 10, 2)
        half_rr = round((risk_amount / 2 * 3) + (risk_amount / 2 * 10), 2)

        lot_result.config(text=f"Lot Size: {lot_size} lots")
        rr3_result.config(text=f"Return at 1:3: ${rr3}")
        rr10_result.config(text=f"Return at 1:10: ${rr10}")
        half_result.config(text=f"Half @1:3 + Half @1:10: ${half_rr}")

        table_text.delete("1.0", tk.END)
        table_text.insert(tk.END, f"{'RR':<10}{'Full Return':<20}{'Partial Return':<20}\n")
        for rr in range(1, 11):
            full = round(risk_amount * rr, 2)
            partial = round((risk_amount / 2 * rr) + (risk_amount / 2 * 10), 2)
            table_text.insert(tk.END, f"1:{rr:<9}{full:<20}{partial:<20}\n")
    except Exception as e:
        messagebox.showerror("Input Error", str(e))

def switch_theme():
    if theme_var.get() == "Light":
        style.theme_use('default')
        root.configure(bg="white")
    else:
        style.theme_use('clam')
        root.configure(bg="#2e2e2e")

root = tk.Tk()
root.title("Lot Size & RR Calculator")
root.geometry("420x580")
style = ttk.Style()

theme_var = tk.StringVar(value="Light")
theme_menu = ttk.OptionMenu(root, theme_var, "Light", "Light", "Dark", command=lambda _: switch_theme())
theme_menu.pack(pady=5)

frame = ttk.Frame(root)
frame.pack(pady=5)

labels = ["Capital ($):", "Leverage:", "Stop Loss (pips):", "Risk %:"]
entries = []
for label in labels:
    ttk.Label(frame, text=label).pack()
    entry = ttk.Entry(frame)
    entry.pack()
    entries.append(entry)

capital_entry, leverage_entry, stop_loss_entry, risk_entry = entries

ttk.Button(root, text="Calculate", command=calculate).pack(pady=10)

lot_result = ttk.Label(root, text="")
lot_result.pack()
rr3_result = ttk.Label(root, text="")
rr3_result.pack()
rr10_result = ttk.Label(root, text="")
rr10_result.pack()
half_result = ttk.Label(root, text="")
half_result.pack()

table_text = tk.Text(root, height=15, width=48)
table_text.pack(pady=10)

switch_theme()
root.mainloop()
