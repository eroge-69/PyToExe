import tkinter as tk
import random

balance_btc = 0.0
balance_ltc = 0.0
BTC_USD = 64000
LTC_USD = 75

def start_sniping(currency):
    global balance_btc, balance_ltc
    if currency == "BTC":
        amount = random.uniform(0.35, 0.55)
        balance_btc += amount
        btc_label.config(text=f"BTC BALANCE: {balance_btc:.7f} BTC\n${balance_btc * BTC_USD:,.2f}")
        output_text.insert(tk.END, f"Sniped {amount:.7f} BTC!\n")
    elif currency == "LTC":
        amount = random.uniform(0.35, 0.55)
        balance_ltc += amount
        ltc_label.config(text=f"LTC BALANCE: {balance_ltc:.7f} LTC\n${balance_ltc * LTC_USD:,.2f}")
        output_text.insert(tk.END, f"Sniped {amount:.7f} LTC!\n")

def clear_output():
    output_text.delete("1.0", tk.END)

root = tk.Tk()
root.title("Simple Crypto Sniper")
root.geometry("500x400")

btc_label = tk.Label(root, text="BTC BALANCE: 0.0000000 BTC\n$0.00", font=("Arial", 14))
btc_label.pack(pady=10)

ltc_label = tk.Label(root, text="LTC BALANCE: 0.0000000 LTC\n$0.00", font=("Arial", 14))
ltc_label.pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

btc_btn = tk.Button(btn_frame, text="Start BTC Sniping", command=lambda: start_sniping("BTC"), width=20)
btc_btn.grid(row=0, column=0, padx=10)

ltc_btn = tk.Button(btn_frame, text="Start LTC Sniping", command=lambda: start_sniping("LTC"), width=20)
ltc_btn.grid(row=0, column=1, padx=10)

clear_btn = tk.Button(root, text="Clear Output", command=clear_output, width=20)
clear_btn.pack(pady=10)

output_text = tk.Text(root, height=10, width=60)
output_text.pack(pady=10)

root.mainloop()
