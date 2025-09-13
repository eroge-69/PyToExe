from SmartApi import SmartConnect
import pandas as pd
import time
from datetime import datetime, timedelta
import pyotp
import requests
import warnings
warnings.filterwarnings("ignore")

# ==== ANGEL ONE CONFIG ====
CLIENT_ID = "K179607"
PIN = "2171"
TOTP = "GLG5X2RG6CEVHLXXFLPGGRFCII"
API_KEY = "83I1o2Yv"

# ==== STRATEGY CONFIG ====
SYMBOL_TOKEN = "99926000"  # NIFTY Spot
TARGET = 20
QUANTITY = 75
PREMIUM = 100
ENTRY_TIME = "09:20"
EXIT_TIME = "15:00"
TIMEFRAME = "ONE_MINUTE"

# ==== INSTRUMENT MASTER ====
JSON_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
instruments = pd.json_normalize(requests.get(JSON_URL).json())

# ==== CONNECT TO ANGEL ONE ====
def connect_angel():
    smart_api = SmartConnect(API_KEY)
    totp = pyotp.TOTP(TOTP).now()
    smart_api.generateSession(CLIENT_ID, PIN, totp)
    return smart_api

# ==== HEIKIN ASHI CALCULATION ====
def calculate_heiken_ashi(df):
    df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    df.reset_index(inplace=True)

    for i in range(len(df)):
        if i == 0:
            df.at[i, 'HA_Open'] = (df.at[i, 'open'] + df.at[i, 'close']) / 2
        else:
            df.at[i, 'HA_Open'] = (df.at[i-1, 'HA_Open'] + df.at[i-1, 'HA_Close']) / 2

    df['HA_High'] = df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    df['HA_Low'] = df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
    df.set_index('timestamp', inplace=True)
    return df

# ==== FETCH LAST 100 MARKET CANDLES ====
def fetch_last_100_candles(obj, symbol_token, interval):
    df_all = pd.DataFrame()
    now = datetime.now()
    market_start_today = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end_today = now.replace(hour=15, minute=30, second=0, microsecond=0)

    if now < market_start_today:
        from_date = (now - timedelta(days=1)).strftime("%Y-%m-%d") + " 09:15"
        to_date = (now - timedelta(days=1)).strftime("%Y-%m-%d") + " 15:30"
    else:
        from_date = market_start_today.strftime("%Y-%m-%d %H:%M")
        to_date = now.strftime("%Y-%m-%d %H:%M")

    params = {
        "exchange": "NSE",
        "symboltoken": symbol_token,
        "interval": interval,
        "fromdate": from_date,
        "todate": to_date
    }

    try:
        data = obj.getCandleData(params)
        if data and "data" in data and data["data"]:
            df_all = pd.DataFrame(data["data"], columns=['timestamp','open','high','low','close','volume'])
            df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
            df_all.set_index('timestamp', inplace=True)
    except Exception as e:
        print(f"⚠️ Error fetching candles: {e}")

    if len(df_all) < 100:
        remaining = 100 - len(df_all)
        prev_day = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        params_prev = {
            "exchange": "NSE",
            "symboltoken": symbol_token,
            "interval": interval,
            "fromdate": prev_day + " 09:15",
            "todate": prev_day + " 15:30"
        }
        try:
            data_prev = obj.getCandleData(params_prev)
            if data_prev and "data" in data_prev and data_prev["data"]:
                df_prev = pd.DataFrame(data_prev["data"], columns=['timestamp','open','high','low','close','volume'])
                df_prev['timestamp'] = pd.to_datetime(df_prev['timestamp'])
                df_prev.set_index('timestamp', inplace=True)
                df_all = pd.concat([df_prev.tail(remaining), df_all])
        except Exception as e:
            print(f"⚠️ Error fetching previous day: {e}")

    return df_all.tail(100)

# ==== GET ATM OPTION ====
def get_atm_option(obj, underlying_price, option_type, price):
    atm_strike = int(round(underlying_price / 50) * 50)
    temp = instruments[(instruments['name'] == 'NIFTY') & (instruments['symbol'].str.contains(option_type))]
    temp['expiry'] = pd.to_datetime(temp['expiry'], format='%d%b%Y')
    temp = temp[temp['expiry'] == temp['expiry'].min()]

    nearest = None
    min_diff = float('inf')
    for _, opt in temp.iterrows():
        try:
            ltp_data = obj.ltpData(opt['exch_seg'], opt['symbol'], opt['token'])
            ltp = ltp_data.get("data", {}).get("ltp", 0)
            diff = abs(ltp - price)
            if diff < min_diff:
                min_diff = diff
                nearest = {"symbol": opt['symbol'], "token": opt['token']}
        except:
            continue
    return nearest["symbol"], nearest["token"]

# ==== PLACE ORDER ====
def place_order(obj, symbol, token, transaction_type, quantity):
    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": str(token),
        "transactiontype": transaction_type,
        "exchange": "NFO",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": 0,
        "quantity": quantity
    }
    order_id = obj.placeOrder(order_params)
    print(f"✅ Order placed: {transaction_type} {symbol} | ID: {order_id}")

# ==== MAIN PE LOGIC ====
if __name__ == "__main__":
    obj = connect_angel()

    order_put = 0
    put_target, put_stoploss = 0, 0
    put, put_token = "", 0

    while True:
        try:
            now = datetime.now()

            # Exit check
            if now.strftime("%H:%M") >= EXIT_TIME:
                if order_put == 1:
                    place_order(obj, put, put_token, "BUY", QUANTITY)  # exit PE by buying
                    order_put = 0
                print("⏹️ Exiting at market close")
                break

            # Entry check
            if now.strftime("%H:%M") >= ENTRY_TIME:
                data = fetch_last_100_candles(obj, SYMBOL_TOKEN, TIMEFRAME)
                if data.empty:
                    time.sleep(5)
                    continue

                ha = calculate_heiken_ashi(data)
                prev = ha.iloc[-2]  # last green candle
                curr = ha.iloc[-1]  # current red candle
                underlying_price = ha.iloc[-1]['close']

                # PE Buy condition (short put)
                if order_put == 0 and prev['HA_Close'] > prev['HA_Open'] and \
                   curr['HA_Close'] < curr['HA_Open'] and curr['low'] < prev['low']:

                    put, put_token = get_atm_option(obj, underlying_price, "PE", PREMIUM)
                    put_stoploss = min(prev['HA_High'], PREMIUM + 10)  # stoploss in option price
                    put_target = prev['low'] - TARGET

                    print(f"🚀 PE Entry at {curr['close']} | SL: {put_stoploss} | TGT: {put_target}")
                    place_order(obj, put, put_token, "BUY", QUANTITY)
                    order_put = 1

                # Exit check
                if order_put == 1:
                    last_close = ha.iloc[-1]['close']
                    if last_close <= put_target or last_close >= put_stoploss:
                        print(f"⚡ PE Exit at {last_close}")
                        place_order(obj, put, put_token, "SELL", QUANTITY)
                        order_put = 0

            time.sleep(5)

        except Exception as e:
            print("⚠️ Exception:", e)
            time.sleep(5)
