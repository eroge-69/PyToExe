import tkinter as tk
from tkinter import messagebox
import requests
import yfinance as yf

def get_prices():
    cryptos = crypto_entry.get().split(',')
    stocks = stock_entry.get().split(',')

    result = ""

    # Get crypto prices
    for crypto in cryptos:
        crypto = crypto.strip().lower()
        try:
            response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd")
            price = response.json()[crypto]['usd']
            result += f"{crypto.capitalize()}: ${price}\n"
        except Exception:
            result += f"{crypto.capitalize()}: Error getting price\n"

    # Get stock prices
    for stock in stocks:
        stock = stock.strip().upper()
        try:
            ticker = yf.Ticker(stock)
            price = ticker.history(period="1d")['Close'][0]
            result += f"{stock}: ${price:.2f}\n"
        except Exception:
            result += f"{stock}: Error getting price\n"

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, result)

app = tk.Tk()
app.title("Crypto & Stock Price Tracker")

tk.Label(app, text="Cryptos (comma separated):").pack()
crypto_entry = tk.Entry(app, width=50)
crypto_entry.pack()
crypto_entry.insert(0, "bitcoin, ethereum")

tk.Label(app, text="Stocks (comma separated):").pack()
stock_entry = tk.Entry(app, width=50)
stock_entry.pack()
stock_entry.insert(0, "AAPL, TSLA")

tk.Button(app, text="Get Prices", command=get_prices).pack(pady=10)

output_text = tk.Text(app, height=10, width=50)
output_text.pack()

app.mainloop()