from binance.client import Client
import pandas as pd
import time

# -------- SETTINGS --------
symbol = "BTCUSDT"  # Pair to trade
interval = "1m"     # Candle interval

# -------- INPUTS --------
api_key = input("Enter your Binance API Key: ")
api_secret = input("Enter your Binance API Secret: ")
budget = float(input("Enter your budget in USDT: "))
paper_mode = input("Paper mode? (y/n): ").lower() == "y"

# -------- INITIALIZE --------
client = Client(api_key, api_secret)

def get_latest_price():
    avg_price = client.get_avg_price(symbol=symbol)
    return float(avg_price['price'])

def get_historical_data():
    klines = client.get_klines(symbol=symbol, interval=interval, limit=20)
    df = pd.DataFrame(klines, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = pd.to_numeric(df["close"])
    return df

def strategy():
    df = get_historical_data()
    df["MA5"] = df["close"].rolling(window=5).mean()
    df["MA10"] = df["close"].rolling(window=10).mean()
    latest = df.iloc[-1]
    if latest["MA5"] > latest["MA10"]:
        return "BUY"
    elif latest["MA5"] < latest["MA10"]:
        return "SELL"
    else:
        return "HOLD"

# -------- MAIN LOOP --------
usdt_balance = budget
crypto_balance = 0

print("\nStarting bot in {} mode...".format("PAPER" if paper_mode else "LIVE"))

while True:
    try:
        signal = strategy()
        price = get_latest_price()
        print(f"Price: {price} | Signal: {signal}")

        if paper_mode:
            if signal == "BUY" and usdt_balance > 0:
                crypto_balance = usdt_balance / price
                usdt_balance = 0
                print(f"[PAPER] Bought {crypto_balance:.6f} BTC at {price} USDT")
            elif signal == "SELL" and crypto_balance > 0:
                usdt_balance = crypto_balance * price
                crypto_balance = 0
                print(f"[PAPER] Sold for {usdt_balance:.2f} USDT")
        else:
            if signal == "BUY":
                order = client.order_market_buy(symbol=symbol, quantity=0.001)
                print(f"Live BUY order: {order}")
            elif signal == "SELL":
                order = client.order_market_sell(symbol=symbol, quantity=0.001)
                print(f"Live SELL order: {order}")

        time.sleep(60)  # Wait for next candle
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
