import tkinter as tk
from tkinter import ttk
import random
import datetime
import winsound

# === GLOBAL BALANCE ===
balance_btc = 0.0
balance_ltc = 0.0
BTC_USD = 64000  # aktuální kurz BTC
LTC_USD = 75      # aktuální kurz LTC
session_stats = {
    "BTC": {"generated": 0, "found": 0, "total": 0.0},
    "LTC": {"generated": 0, "found": 0, "total": 0.0}
}

def random_address(prefix='1'):
    base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return prefix + ''.join(random.choice(base58_chars) for _ in range(33))

def random_amount():
    return round(random.uniform(0.35, 0.55), 7)

def update_balance_labels():
    btc_usd = balance_btc * BTC_USD
    ltc_usd = balance_ltc * LTC_USD
    btc_balance_label.config(text=f"BTC BALANCE: {balance_btc:.7f} BTC\n${btc_usd:,.2f}")
    ltc_balance_label.config(text=f"LTC BALANCE: {balance_ltc:.7f} LTC\n${ltc_usd:,.2f}")

def export_balances():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"balances_{now}.txt"
    with open(filename, 'w') as f:
        f.write(f"BTC BALANCE: {balance_btc:.7f} BTC (${balance_btc * BTC_USD:.2f})\n")
        f.write(f"LTC BALANCE: {balance_ltc:.7f} LTC (${balance_ltc * LTC_USD:.2f})\n")
    output_text.insert(tk.END, f"\nBalances exported to {filename}\n")
    output_text.see(tk.END)

def start_sniping(currency):
    global lines, index, balance_btc, balance_ltc
    output_text.delete("1.0", tk.END)
    lines = []
    index = 0
    special_indexes = set(random.sample(range(10000), 20))

    session_stats[currency]["generated"] = 0
    session_stats[currency]["found"] = 0
    session_stats[currency]["total"] = 0.0

    if currency == 'BTC':
        balance_btc = 0.0
    else:
        balance_ltc = 0.0

    for i in range(10000):
        addr = random_address('1' if currency == 'BTC' else 'L')
        if i in special_indexes:
            amt = 1.0 if random.random() < 0.1 else random_amount()
            amt_str = f"{amt:.7f}".replace('.', ',')
        else:
            amt = 0.0
            amt_str = "0,0000000"
        lines.append((f"{addr}  {amt_str} {currency}", amt))

    update_balance_labels()
    output_text.insert(tk.END, f"Starting {currency} Sniping...\n\n")
    vypis_cast(currency)

def vypis_cast(currency, delay=250):
    global index, lines, balance_btc, balance_ltc

    if index < len(lines):
        text, amount = lines[index]
        if "1,0000000" in text:
            output_text.insert(tk.END, text + ", ", "rare")
        else:
            output_text.insert(tk.END, text + ", ")
        output_text.see(tk.END)

        if amount > 0:
            winsound.Beep(1000, 150)
            session_stats[currency]["found"] += 1
            session_stats[currency]["total"] += amount

        session_stats[currency]["generated"] += 1

        if currency == 'BTC':
            balance_btc += amount
        else:
            balance_ltc += amount

        update_balance_labels()
        index += 1
        root.after(delay, lambda: vypis_cast(currency, delay))

def open_withdraw_window():
    def send_withdraw():
        global balance_btc, balance_ltc
        currency = currency_var.get()
        try:
            amount = float(amount_entry.get().replace(',', '.'))
        except ValueError:
            status_label.config(text="Invalid amount", fg="red")
            return

        address = address_entry.get().strip()
        if not address:
            status_label.config(text="Address required", fg="red")
            return

        usd_amount = amount * (BTC_USD if currency == 'BTC' else LTC_USD)
        if usd_amount < 1000:
            status_label.config(text="Minimum withdrawal is $1000", fg="red")
            return

        if currency == 'BTC':
            if amount > balance_btc:
                status_label.config(text="Insufficient BTC balance", fg="red")
                return
            balance_btc -= amount
        else:
            if amount > balance_ltc:
                status_label.config(text="Insufficient LTC balance", fg="red")
                return
            balance_ltc -= amount

        update_balance_labels()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("withdraw_log.txt", "a") as log:
            log.write(f"{now} | {currency} | {amount:.7f} | {address}\n")

        status_label.config(
            text=f"Withdrawal of {amount:.7f} {currency} sent to {address}", fg="green"
        )

    win = tk.Toplevel(root)
    win.title("Withdraw Funds")
    win.geometry("400x250")
    win.resizable(False, False)

    tk.Label(win, text="Select Currency:").pack(pady=(10, 0))
    currency_var = tk.StringVar(value="BTC")
    ttk.Combobox(win, textvariable=currency_var, values=["BTC", "LTC"], state="readonly").pack()

    tk.Label(win, text="Amount:").pack(pady=(10, 0))
    amount_entry = tk.Entry(win)
    amount_entry.pack()

    tk.Label(win, text="Address:").pack(pady=(10, 0))
    address_entry = tk.Entry(win, width=50)
    address_entry.pack()

    tk.Button(win, text="Send", command=send_withdraw).pack(pady=10)
    status_label = tk.Label(win, text="", fg="green")
    status_label.pack()

def show_stats():
    stats = "Session Statistics:\n\n"
    for currency in ["BTC", "LTC"]:
        stats += f"{currency}:\n"
        stats += f"Generated: {session_stats[currency]['generated']}\n"
        stats += f"Found: {session_stats[currency]['found']}\n"
        stats += f"Total Value: {session_stats[currency]['total']:.7f} {currency} (${session_stats[currency]['total'] * (BTC_USD if currency == 'BTC' else LTC_USD):,.2f})\n\n"
    output_text.insert(tk.END, stats)
    output_text.see(tk.END)

def exit_app():
    root.destroy()

# === GUI ===
root = tk.Tk()
root.title("Crypto Sniper Tool")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

title_label = tk.Label(root, text="Crypto Sniper Tool", font=("Helvetica", 20, "bold"), fg="#00ffcc", bg="#1e1e1e")
title_label.pack(pady=(10, 0))

top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(pady=10)

btc_balance_label = tk.Label(top_frame, text="BTC BALANCE: 0.0000000 BTC", font=("Arial", 14), fg="#00ff00", bg="#1e1e1e")
btc_balance_label.pack(side=tk.LEFT, padx=40)

ltc_balance_label = tk.Label(top_frame, text="LTC BALANCE: 0.0000000 LTC", font=("Arial", 14), fg="#00ffff", bg="#1e1e1e")
ltc_balance_label.pack(side=tk.LEFT, padx=40)

output_text = tk.Text(root, height=25, wrap='word', bg="#111111", fg="#ffffff", font=("Courier", 10))
output_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
output_text.tag_config("rare", foreground="#ffcc00", font=("Courier", 10, "bold"))

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="BTC Sniping", command=lambda: start_sniping("BTC"), width=15, bg="#444444", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="LTC Sniping", command=lambda: start_sniping("LTC"), width=15, bg="#444444", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Withdraw", command=open_withdraw_window, width=15, bg="#444444", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Export Balances", command=export_balances, width=15, bg="#444444", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Show Stats", command=show_stats, width=15, bg="#444444", fg="white").pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_app, width=15, bg="#444444", fg="white").pack(side=tk.LEFT, padx=10)

root.mainloop()
