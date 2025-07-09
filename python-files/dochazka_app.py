
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

def parse_time(time_str):
    for fmt in ("%H:%M", "%H.%M", "%H%M"):
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
    return None

def parse_balance(balance_str):
    balance_str = balance_str.strip()
    if balance_str in ("0", "0:00"):
        return 0
    if ":" in balance_str:
        try:
            negative = "-" in balance_str
            parts = balance_str.replace("-", "").split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            total = hours * 60 + minutes
            return -total if negative else total
        except:
            return None
    else:
        try:
            return int(balance_str)
        except:
            return None

def parse_required_time(required_str):
    if ":" in required_str:
        h, m = required_str.split(":")
    elif "." in required_str:
        h, m = required_str.split(".")
    else:
        h, m = required_str, "0"
    try:
        return timedelta(hours=int(h), minutes=int(m))
    except:
        return None

def calculate():
    arrival = parse_time(entry_arrival.get())
    leave = parse_time(entry_leave.get())
    balance = parse_balance(entry_balance.get())
    required = parse_required_time(entry_required.get())

    if arrival is None or leave is None or balance is None or required is None:
        messagebox.showerror("Chyba", "Zkontrolujte formáty vstupů.")
        return

    expected_leave = arrival + required
    adjusted_leave = expected_leave - timedelta(minutes=balance)
    worked = leave - arrival
    total_diff = worked - required + timedelta(minutes=balance)

    result = f"Očekávaný odchod: {expected_leave.strftime('%H:%M')}\n"
    result += f"Odchod po zůstatku: {adjusted_leave.strftime('%H:%M')}\n"

    minutes = int(total_diff.total_seconds() // 60)
    hours = abs(minutes) // 60
    mins = abs(minutes) % 60

    if minutes < 0:
        result += f"Chybí: {hours}h {mins}m"
    elif minutes > 0:
        result += f"Přesčas: {hours}h {mins}m"
    else:
        result += "Odpracováno přesně"

    messagebox.showinfo("Výsledek", result)

root = tk.Tk()
root.title("Docházka")

tk.Label(root, text="Příchod (např. 7:45):").grid(row=0, column=0, sticky="e")
entry_arrival = tk.Entry(root)
entry_arrival.grid(row=0, column=1)

tk.Label(root, text="Zůstatek (např. -1:30):").grid(row=1, column=0, sticky="e")
entry_balance = tk.Entry(root)
entry_balance.grid(row=1, column=1)

tk.Label(root, text="Odchod (např. 16:20):").grid(row=2, column=0, sticky="e")
entry_leave = tk.Entry(root)
entry_leave.grid(row=2, column=1)

tk.Label(root, text="Pracovní doba (např. 8:40):").grid(row=3, column=0, sticky="e")
entry_required = tk.Entry(root)
entry_required.insert(0, "8:40")
entry_required.grid(row=3, column=1)

tk.Button(root, text="Spočítat", command=calculate).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
