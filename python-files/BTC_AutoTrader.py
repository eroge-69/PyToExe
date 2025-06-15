
import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime

# Account credentials
ACCOUNT = 405445369
PASSWORD = "Secret@007"
SERVER = "Exness-MT5Real8"
SYMBOL = "BTCUSD"
LOT = 0.01
TIMEFRAME = mt5.TIMEFRAME_M1
DEVIATION = 5

# Initialize connection to MetaTrader 5
def connect():
    if not mt5.initialize(login=ACCOUNT, server=SERVER, password=PASSWORD):
        print("Initialization failed:", mt5.last_error())
        quit()
    print(f"[{datetime.now()}] Connected to MT5")

# Get latest data and calculate EMAs
def get_ema_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 50)
    df = pd.DataFrame(rates)
    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema15'] = df['close'].ewm(span=15).mean()
    return df

# Detect signal based on EMA crossover
def get_signal(df):
    if df['ema9'].iloc[-2] < df['ema15'].iloc[-2] and df['ema9'].iloc[-1] > df['ema15'].iloc[-1]:
        return "BUY"
    elif df['ema9'].iloc[-2] > df['ema15'].iloc[-2] and df['ema9'].iloc[-1] < df['ema15'].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

# Close open positions for BTCUSD
def close_open_trades():
    positions = mt5.positions_get(symbol=SYMBOL)
    for pos in positions:
        close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(SYMBOL).bid if close_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": pos.volume,
            "type": close_type,
            "position": pos.ticket,
            "price": price,
            "deviation": DEVIATION,
            "magic": 123456,
            "comment": "Auto close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)

# Place trade
def place_order(order_type):
    price = mt5.symbol_info_tick(SYMBOL).ask if order_type == "BUY" else mt5.symbol_info_tick(SYMBOL).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT,
        "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": DEVIATION,
        "magic": 123456,
        "comment": "9/15 EMA Entry",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print(f"[{datetime.now()}] Trade Result: {result}")

# Main loop
def run_bot():
    connect()
    while True:
        df = get_ema_data()
        signal = get_signal(df)
        print(f"[{datetime.now()}] Signal: {signal}")
        if signal in ["BUY", "SELL"]:
            close_open_trades()
            place_order(signal)
        time.sleep(60)

run_bot()
