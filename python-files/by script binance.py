import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import MACD

def get_all_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    info = requests.get(url).json()
    symbols = [s['symbol'] for s in info['symbols'] if s['isSpotTradingAllowed'] and s['quoteAsset'] == 'USDT']
    return symbols

def fetch_data(symbol, interval='1h', limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])
    
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    return df[['timestamp', 'close', 'volume']]

def apply_indicators(df):
    rsi = RSIIndicator(close=df['close'], window=14)
    macd = MACD(close=df['close'])
    df['RSI'] = rsi.rsi()
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()
    return df

def process_all():
    final_rows = []
    symbols = get_all_symbols()
    print(f"🔍 Total Spot Coins Found: {len(symbols)}")

    for symbol in symbols:
        try:
            df = fetch_data(symbol)
            if df is None or df.empty: continue
            df = apply_indicators(df)
            latest = df.iloc[-1]  # Use latest data point

            if (
                latest['RSI'] > 30 and
                latest['volume'] > 50_000_000 and
                latest['MACD'] > latest['Signal']
            ):
                final_rows.append({
                    'Symbol': symbol,
                    'RSI': round(latest['RSI'], 2),
                    'Volume': round(latest['volume'], 2),
                    'MACD': round(latest['MACD'], 4),
                    'Signal': round(latest['Signal'], 4)
                })
        except Exception as e:
            print(f"⚠️ Skipping {symbol} due to error: {e}")

    if final_rows:
        df_final = pd.DataFrame(final_rows)
        df_final.to_excel("spot_coins_filtered.xlsx", index=False)
        print("✅ Excel file saved: spot_coins_filtered.xlsx")
    else:
        print("❌ No coins matched the filter criteria.")

# 🧪 Run the scanner
if __name__ == "__main__":
    process_all()
