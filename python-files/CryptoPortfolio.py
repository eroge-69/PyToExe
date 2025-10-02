import tkinter as tk
from tkinter import ttk
import requests

# Lista kryptowalut i ich identyfikatory w CoinGecko
cryptos = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "SOLANA": "solana"
}

# Funkcja pobierająca kursy w EUR
def fetch_prices():
    ids = ",".join(cryptos.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur"
    response = requests.get(url).json()
    prices = {k: response[v]["eur"] for k, v in cryptos.items()}
    return prices

# Funkcja aktualizująca tabelę
def update_table():
    prices = fetch_prices()
    for i, crypto in enumerate(cryptos.keys()):
        try:
            amount = float(amount_entries[i].get())
        except:
            amount = 0
        price = prices[crypto]
        value = amount * price
        price_labels[i].config(text=f"{price:.2f} €")
        value_labels[i].config(text=f"{value:.2f} €")
        profit_labels[i].config(text=f"{value - purchase_prices[i]:.2f} €")
    root.after(60000, update_table)  # odśwież co 60 sekund

# --- GUI ---
root = tk.Tk()
root.title("Kryptowaluty - Portfolio")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

# Nagłówki
headers = ["Kryptowaluta", "Ilość posiadana", "Cena zakupu (€)", "Kurs aktualny (€)", "Wartość aktualna (€)", "Zysk/Strata (€)"]
for j, h in enumerate(headers):
    ttk.Label(frame, text=h, font=("Arial", 10, "bold")).grid(row=0, column=j, padx=5, pady=5)

amount_entries = []
price_labels = []
value_labels = []
profit_labels = []
purchase_prices = []

# Wprowadzanie danych i tworzenie wierszy
for i, crypto in enumerate(cryptos.keys()):
    ttk.Label(frame, text=crypto).grid(row=i+1, column=0)
    
    amt_entry = ttk.Entry(frame, width=10)
    amt_entry.grid(row=i+1, column=1)
    amt_entry.insert(0, "0")
    amount_entries.append(amt_entry)
    
    # Wprowadź cenę zakupu w EUR
    price_input = input(f"Podaj cenę zakupu {crypto} w EUR: ")
    try:
        purchase_price = float(price_input)
    except:
        purchase_price = 0
    purchase_prices.append(purchase_price * float(amt_entry.get()))
    
    ttk.Label(frame, text=f"{purchase_price:.2f} €").grid(row=i+1, column=2)
    
    plabel = ttk.Label(frame, text="0.00 €")
    plabel.grid(row=i+1, column=3)
    price_labels.append(plabel)
    
    vlabel = ttk.Label(frame, text="0.00 €")
    vlabel.grid(row=i+1, column=4)
    value_labels.append(vlabel)
    
    prof_label = ttk.Label(frame, text="0.00 €")
    prof_label.grid(row=i+1, column=5)
    profit_labels.append(prof_label)

update_table()
root.mainloop()
