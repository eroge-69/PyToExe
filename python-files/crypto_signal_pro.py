import requests
import tkinter as tk

# List of cryptocurrencies to track
cryptos = ["bitcoin", "ethereum", "solana", "dogecoin", "binancecoin"]
prices_history = {coin: [] for coin in cryptos}

def get_prices():
    ids = ",".join(cryptos)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    response = requests.get(url)
    return response.json()

def analyze_prices():
    data = get_prices()
    results = ""
    
    for coin in cryptos:
        current_price = data[coin]['usd']
        prices_history[coin].append(current_price)
        if len(prices_history[coin]) > 5:
            prices_history[coin].pop(0)
        
        avg_price = sum(prices_history[coin]) / len(prices_history[coin])
        
        results += f"{coin.upper()} | Price: ${current_price:.2f} | Avg: ${avg_price:.2f} → "
        
        if current_price > avg_price:
            results += "🔼 BUY\n"
        elif current_price < avg_price:
            results += "🔽 SELL\n"
        else:
            results += "⚖️ NEUTRAL\n"

    label_output.config(text=results)
    window.after(10000, analyze_prices)  # Update every 10 seconds

# GUI setup
window = tk.Tk()
window.title("Crypto Signal Pro")
window.geometry("500x300")

label_title = tk.Label(window, text="📊 Crypto Market Analyzer", font=("Arial", 16))
label_title.pack(pady=10)

label_output = tk.Label(window, text="Loading...", font=("Courier", 10), justify="left")
label_output.pack(pady=10)

analyze_prices()
window.mainloop()
