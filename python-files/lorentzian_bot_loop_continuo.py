
import time
import numpy as np
import pandas as pd
import requests
import ta
from datetime import datetime

symbols = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "cardano": "ADA",
    "polkadot": "DOT",
    "litecoin": "LTC",
    "binancecoin": "BNB",
    "avalanche": "AVAX",
    "chainlink": "LINK",
    "tron": "TRX",
    "uniswap": "UNI",
    "stellar": "XLM",
    "near-protocol": "NEAR",
    "aptos": "APT",
    "arbitrum": "ARB",
    "the-graph": "GRT"
}


capital = 10000
positions = {sym: 0 for sym in symbols}
entry_prices = {sym: 0 for sym in symbols}
directions = {sym: None for sym in symbols}
capital_history = [capital]

# Parametri leva
leverage = 5
adx_threshold = 25
taker_fee_pct = 0.00055

k_neighbors = 8
TELEGRAM_TOKEN = "7912021484:AAHvvUnZQAfUqPYdL5HsjsNENdVypHlWjmk"
TELEGRAM_CHAT_IDS = ["8102379503", "5181093826"]

last_update_time = datetime.now()

def send_telegram(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        try:
            requests.post(url, data=data)
        except:
            pass

def send_periodic_update(latest_prices):
    global last_update_time
    now = datetime.now()
    if (now - last_update_time).total_seconds() >= 420:
        invested = sum(positions[sym] * latest_prices.get(sym, 0) for sym in symbols)
        total = capital + invested
        msg = f"⏱️ {now.strftime('%H:%M')} | Capitale Totale: ${total:.2f} (Liquidità: ${capital:.2f}, Investito: ${invested:.2f})"
        send_telegram(msg)
        last_update_time = now

def get_price_history(symbol):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '1',
        'interval': 'minutely'
    }
    try:
        response = requests.get(url, params=params)
        prices = response.json()['prices']
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df['price'] = df['price'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except:
        return pd.DataFrame()

def calculate_features(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['price'], window=14).rsi()
    df['adx'] = ta.trend.ADXIndicator(high=df['price'], low=df['price'], close=df['price'], window=14).adx()
    df['cci'] = ta.trend.CCIIndicator(high=df['price'], low=df['price'], close=df['price'], window=20).cci()
    df['wt'] = df['price'].rolling(window=10).mean()
    return df.dropna()

def lorentzian_distance(p1, p2):
    return np.sum(np.log(1 + np.abs(np.array(p1) - np.array(p2))))

def knn_predict(features_df, k=8):
    last_row = features_df.iloc[-1]
    distances = []
    for i in range(0, len(features_df) - 4, 4):
        row = features_df.iloc[i]
        p1 = [row['rsi'], row['adx'], row['cci'], row['wt']]
        p2 = [last_row['rsi'], last_row['adx'], last_row['cci'], last_row['wt']]
        d = lorentzian_distance(p1, p2)
        future_return = features_df.iloc[i + 4]['price'] - features_df.iloc[i]['price']
        label = np.sign(future_return)
        distances.append((d, label))
    distances.sort(key=lambda x: x[0])
    nearest = distances[:k]
    prediction = np.sign(np.sum([x[1] for x in nearest]))
    return prediction

def execute_trade(symbol, prediction, current_price, adx_now):
    global capital
    allocated = capital / len(symbols)
    use_leverage = adx_now > adx_threshold
    lev = leverage if use_leverage else 1
    margin = allocated / lev

    if directions[symbol] is None and prediction != 0:
        amount = (margin * lev) / current_price
        positions[symbol] = amount
        entry_prices[symbol] = current_price
        directions[symbol] = 'long' if prediction > 0 else 'short'
        fee = amount * current_price * taker_fee_pct
        capital -= fee
        msg = f"[{datetime.now()}] ✅ OPEN {directions[symbol].upper()} {symbols[symbol]} @ {current_price:.2f} | ADX: {adx_now:.2f} | LEVA x{lev} | Fee: ${fee:.2f}"
        print(msg)
        send_telegram(msg)

    elif directions[symbol] is not None:
        price_diff = current_price - entry_prices[symbol]
        profit_pct = (price_diff / entry_prices[symbol]) * (leverage if adx_now > adx_threshold else 1)
        if directions[symbol] == 'short':
            profit_pct = -profit_pct

        if abs(profit_pct) >= 0.05:
            pnl = margin * profit_pct
            fee = positions[symbol] * current_price * taker_fee_pct
            capital += pnl - fee
            msg = f"[{datetime.now()}] 🔴 CLOSE {directions[symbol].upper()} {symbols[symbol]} @ {current_price:.2f} | PnL: ${pnl:.2f}, Fee: ${fee:.2f} | Capital: ${capital:.2f}"
            print(msg)
            send_telegram(msg)
            positions[symbol] = 0
            directions[symbol] = None

    capital_history.append(capital)

def run_loop():
    while True:
        latest_prices = {}
        for symbol in symbols:
            df = get_price_history(symbol)
            if df.empty:
                continue
            df = calculate_features(df)
            if len(df) < 50:
                continue
            sub_df = df.iloc[-50:]
            prediction = knn_predict(sub_df, k=k_neighbors)
            current_price = sub_df['price'].iloc[-1]
            adx_now = sub_df['adx'].iloc[-1]
            latest_prices[symbol] = current_price
            execute_trade(symbol, prediction, current_price, adx_now)
        send_periodic_update(latest_prices)
        time.sleep(60)

if __name__ == "__main__":
    run_loop()
