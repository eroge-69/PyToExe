import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from binance.client import Client
import sys

# ✅ Binance Testnet API
API_KEY = "v1OY9LX8vu9CC6gkR3nlP4A2fqfekko6SMViEdE9x0RI8QK1MQJSXDi9ub6QLuKa"
API_SECRET = "EpkD6fXwBbUQxFRO1AjKJkuJgA6HdWmy3GeILKk9qmqg9kzOPbClUnFJKCwYe0T7"
SYMBOL = "BTCUSDT"

try:
    client = Client(API_KEY, API_SECRET)
    client.API_URL = 'https://testnet.binance.vision/api'
except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(str(e))
    sys.exit("❌ Binance API connection failed")

bot_running = [False]

# ✅ Fetch candle data
def get_candles():
    try:
        candles = client.get_klines(symbol=SYMBOL, interval="1m", limit=50)
        df = pd.DataFrame(candles, columns=[
            "Time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote", "Trades", "Taker buy base", "Taker buy quote", "Ignore"
        ])
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df.set_index('Time', inplace=True)
        df = df.astype(float)
        return df
    except Exception as e:
        append_log(f"❌ Candle Error: {e}")
        return pd.DataFrame()

# ✅ Generate buy/sell signal
def get_signal(df):
    try:
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        if df['MA5'].iloc[-1] > df['MA20'].iloc[-1]:
            return "BUY"
        elif df['MA5'].iloc[-1] < df['MA20'].iloc[-1]:
            return "SELL"
        return "HOLD"
    except:
        return "NO SIGNAL"

# ✅ Simulated trade
def execute_trade(signal):
    return f"💡 Signal: {signal} (Simulated)"

# ✅ Update GUI chart
def update_chart():
    df = get_candles()
    if df.empty:
        return
    fig, _ = mpf.plot(df, type='candle', mav=(5, 20), style='charles', returnfig=True)
    for widget in chart_frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig[0], master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# ✅ Bot logic
def bot_loop():
    while bot_running[0]:
        df = get_candles()
        if not df.empty:
            signal = get_signal(df)
            result = execute_trade(signal)
            append_log(result)
            update_chart()
        time.sleep(60)

# ✅ Button functions
def start_bot():
    if not bot_running[0]:
        bot_running[0] = True
        threading.Thread(target=bot_loop, daemon=True).start()
        append_log("✅ Bot started")

def stop_bot():
    bot_running[0] = False
    append_log("🛑 Bot stopped")

# ✅ Logger
def append_log(msg):
    log_box.config(state="normal")
    log_box.insert(tk.END, f"{msg}\n")
    log_box.config(state="disabled")
    log_box.see(tk.END)

# ✅ GUI Setup
root = tk.Tk()
root.title("📊 One-Click Binance Bot")
root.geometry("900x700")
root.configure(bg="#f0f0f0")

tk.Label(root, text="🟢 Auto Trading Bot - Binance Testnet", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

btns = tk.Frame(root, bg="#f0f0f0")
tk.Button(btns, text="▶ Start", command=start_bot, bg="green", fg="white", width=15).pack(side=tk.LEFT, padx=10)
tk.Button(btns, text="■ Stop", command=stop_bot, bg="red", fg="white", width=15).pack(side=tk.LEFT, padx=10)
btns.pack()

chart_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
chart_frame.pack(pady=10)

log_box = scrolledtext.ScrolledText(root, width=105, height=10, state="disabled", font=("Courier", 10))
log_box.pack(padx=10, pady=10)

append_log("🤖 Ready. Click ▶ Start to begin.")
update_chart()
root.mainloop()
