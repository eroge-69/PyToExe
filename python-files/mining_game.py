import tkinter as tk
from tkinter import messagebox
import time
import threading
import requests
import webbrowser
import os
import json

# Պահպանում / բեռննում գումարը ֆայլից
DATA_FILE = "balance.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        balance = data.get("balance", 0.0)
else:
    balance = 0.0

# Մեր մայնինգի կարգավորումներ
USDT_PER_10_DAYS = 1.0
SECONDS_PER_INTERVAL = 7  # 7 վարկյան մեկ աճ
INTERVAL_AMOUNT = USDT_PER_10_DAYS / (10*24*60*60/SECONDS_PER_INTERVAL)  # 10 օր => 10*24*60*60 վարկյան

# Մայնինգի կարգավիճակ
mining = False

def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

def save_balance():
    with open(DATA_FILE, "w") as f:
        json.dump({"balance": balance}, f)

def update_balance_label():
    balance_label.config(text=f"Մեր հաշիվը: {balance:.9f} USDT")

def mining_loop():
    global balance, mining
    while mining:
        if not check_internet():
            messagebox.showwarning("Ինտերնետ չկա", "Ինտերնետ կապ չկա. Մայնինգը կասեցվեց։")
            stop_mining()
            break
        time.sleep(SECONDS_PER_INTERVAL)
        balance += INTERVAL_AMOUNT
        save_balance()
        update_balance_label()
        # Եթե հասնում ենք 200 USDT
        if balance >= 200.0:
            withdraw_button.config(state=tk.NORMAL)

def start_mining():
    global mining
    if not mining:
        mining = True
        threading.Thread(target=mining_loop, daemon=True).start()

def stop_mining():
    global mining
    mining = False

def withdraw():
    global balance
    if balance >= 200.0:
        balance -= 200.0
        save_balance()
        update_balance_label()
        webbrowser.open("https://films.bz/")
        withdraw_button.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Հայտարարություն", "Ցանկացած դեպքում ձեր հաշիվը բավարար չէ։")

# GUI
root = tk.Tk()
root.title("Մայնինգի Սիմուլյացիա (USDT)")

balance_label = tk.Label(root, text=f"Մեր հաշիվը: {balance:.9f} USDT", font=("Arial", 14))
balance_label.pack(pady=10)

start_button = tk.Button(root, text="Սկսել մայնինգը", command=start_mining)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Կասեցնել մայնինգը", command=stop_mining)
stop_button.pack(pady=5)

withdraw_button = tk.Button(root, text="Դուրսբերում 200 USDT", command=withdraw)
withdraw_button.pack(pady=5)
withdraw_button.config(state=tk.DISABLED if balance < 200 else tk.NORMAL)

root.mainloop()
