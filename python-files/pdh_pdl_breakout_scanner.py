
import requests
import time
import datetime
import winsound

BASE_URL = "https://api.delta.exchange"
HEADERS = {"Accept": "application/json"}

# Settings
PERCENT_THRESHOLD = 20  # 20% move
VOLUME_SPIKE_MULTIPLIER = 2  # Today's volume > 2x yesterday
REFRESH_SECONDS = 300  # 5 minutes

def get_markets():
    url = f"{BASE_URL}/v2/products"
    res = requests.get(url, headers=HEADERS)
    return [m for m in res.json()['result'] if m['spot_index']]

def get_ohlc(symbol, interval="1d", limit=3):
    url = f"{BASE_URL}/v2/history/candles"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    res = requests.get(url, headers=HEADERS, params=params)
    data = res.json()
    return data['result'] if 'result' in data else []

def get_current_price(symbol):
    url = f"{BASE_URL}/v2/tickers/{symbol}"
    res = requests.get(url, headers=HEADERS)
    return float(res.json()['result']['last_price'])

def beep():
    try:
        winsound.Beep(1000, 500)
    except:
        pass

def scan_breakouts():
    markets = get_markets()
    print(f"=== Delta Exchange PDH/PDL Breakout Scanner ===")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Scanning...
")

    for market in markets:
        symbol = market['symbol']
        try:
            candles = get_ohlc(symbol)
            if len(candles) < 3:
                continue

            prev_day = candles[-2]
            today = candles[-1]

            pdh = float(prev_day['high'])
            pdl = float(prev_day['low'])
            prev_close = float(prev_day['close'])
            today_close = float(today['close'])
            change_percent = ((today_close - prev_close) / prev_close) * 100

            today_volume = float(today['volume'])
            prev_volume = float(prev_day['volume'])

            volume_spike = today_volume > VOLUME_SPIKE_MULTIPLIER * prev_volume

            current_price = get_current_price(symbol)

            breakout = False

            if current_price > pdh:
                print(f"🚀 {symbol} BREAKING PDH! Current: {current_price:.4f} > PDH: {pdh:.4f}")
                breakout = True
            elif current_price < pdl:
                print(f"🔻 {symbol} BREAKING PDL! Current: {current_price:.4f} < PDL: {pdl:.4f}")
                breakout = True

            if abs(change_percent) >= PERCENT_THRESHOLD:
                print(f"⚠️ {symbol} has moved {change_percent:.2f}% in 24h")

            if volume_spike:
                print(f"📊 {symbol} volume spike! Today: {today_volume:.2f}, Yesterday: {prev_volume:.2f}")

            if breakout or abs(change_percent) >= PERCENT_THRESHOLD or volume_spike:
                beep()
                print("-" * 50)

        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")

# Main loop
if __name__ == "__main__":
    while True:
        scan_breakouts()
        print(f"\nSleeping {REFRESH_SECONDS // 60} minutes...\n")
        time.sleep(REFRESH_SECONDS)
