# Crypto EMA Pullback Alert System with GUI (4H timeframe)
# Coins: BTC/USDT and ETH/USDT
# Alerts: Telegram + Email ready (setup required)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
import time

try:
    import ccxt
except ImportError:
    ccxt = None
    print("Warning: 'ccxt' module is not installed. Market data fetching will not work.")

# ===============================
# CONFIG SECTION
# ===============================
SYMBOLS = ['BTC/USDT', 'ETH/USDT']
TIMEFRAME = '4h'
LIMIT = 200

# Telegram
TELEGRAM_TOKEN = 'your_telegram_bot_token_here'
TELEGRAM_CHAT_ID = 'your_telegram_user_id_here'

# Email
SMTP_EMAIL = 'your_email@gmail.com'
SMTP_PASSWORD = 'your_app_password_here'
EMAIL_TO = 'recipient@example.com'

EXPORT_CSV = False

# ===============================
# HELPER FUNCTIONS
# ===============================
def fetch_data(symbol):
    if not ccxt:
        raise ImportError("The 'ccxt' module is required to fetch market data. Please run 'pip install ccxt'")
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Datetime', inplace=True)
    return df

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(series):
    ema12 = ema(series, span=12)
    ema26 = ema(series, span=26)
    macd_line = ema12 - ema26
    signal_line = ema(macd_line, span=9)
    macd_hist = macd_line - signal_line
    return macd_line, macd_hist

def bollinger_bands(series, window=20, num_std=2):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, lower_band

def apply_indicators(df):
    df['EMA9'] = ema(df['Close'], span=9)
    df['EMA20'] = ema(df['Close'], span=20)
    df['RSI'] = rsi(df['Close'])
    df['MACD'], df['MACD_Hist'] = macd(df['Close'])
    df['BB_Upper'], df['BB_Lower'] = bollinger_bands(df['Close'])
    return df

def check_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    trend_ok = last['EMA9'] > last['EMA20'] and (last['EMA9'] - last['EMA20']) / last['EMA20'] > 0.01
    rsi_ok = last['RSI'] > 50
    macd_ok = last['MACD'] > 0 and last['MACD_Hist'] > 0
    bullish_candle = prev['Close'] < last['Close']
    pullback = last['Low'] <= last['EMA9']
    return trend_ok and rsi_ok and macd_ok and bullish_candle and pullback

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, EMAIL_TO, msg.as_string())
    server.quit()

def plot_chart(df, symbol):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close', alpha=0.7)
    plt.plot(df['EMA9'], label='EMA 9')
    plt.plot(df['EMA20'], label='EMA 20')
    plt.plot(df['BB_Upper'], label='BB Upper', linestyle='--', alpha=0.6)
    plt.plot(df['BB_Lower'], label='BB Lower', linestyle='--', alpha=0.6)
    plt.title(f"{symbol} - 4H EMA Pullback Setup")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    filename = f"{symbol.replace('/', '_')}_chart.png"
    plt.savefig(filename)
    plt.close()
    return filename

def scan_market():
    results = []
    for symbol in SYMBOLS:
        try:
            df = fetch_data(symbol)
            df = apply_indicators(df)
            if check_signal(df):
                msg = f"🚨 BUY Signal for {symbol} (4H)\nDatetime: {df.index[-1]}\nPrice: {df['Close'].iloc[-1]:.2f}"
                send_telegram(msg)
                send_email(subject=f"Buy Signal for {symbol}", message=msg)
                chart_path = plot_chart(df, symbol)
                results.append({'Symbol': symbol, 'Datetime': df.index[-1], 'Price': df['Close'].iloc[-1]})
                messagebox.showinfo("Signal Alert", f"Buy signal for {symbol}!\nChart saved: {chart_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning {symbol}: {e}")

    if EXPORT_CSV and results:
        pd.DataFrame(results).to_csv("signals_export.csv", index=False)

# ===============================
# GUI SECTION
# ===============================
def start_scan():
    threading.Thread(target=scan_market).start()

def auto_scan():
    def loop():
        while True:
            scan_market()
            time.sleep(60 * 60 * 4)  # Every 4 hours
    threading.Thread(target=loop, daemon=True).start()

def toggle_export():
    global EXPORT_CSV
    EXPORT_CSV = export_var.get()

app = tk.Tk()
app.title("Crypto EMA Pullback Scanner")
app.geometry("400x350")

label = tk.Label(app, text="Crypto EMA Pullback Strategy", font=("Arial", 14))
label.pack(pady=10)

scan_button = tk.Button(app, text="🔍 Scan Market Now", command=start_scan, font=("Arial", 12), bg="green", fg="white")
scan_button.pack(pady=10)

export_var = tk.BooleanVar()
export_checkbox = tk.Checkbutton(app, text="Export signals to CSV", variable=export_var, command=toggle_export)
export_checkbox.pack()

info = tk.Label(app, text="Coins: BTC/USDT, ETH/USDT\nTimeframe: 4H\nAuto-scan every 4 hours", font=("Arial", 10))
info.pack(pady=10)

exit_button = tk.Button(app, text="Exit", command=app.quit, font=("Arial", 10))
exit_button.pack(pady=10)

auto_scan()
app.mainloop()
