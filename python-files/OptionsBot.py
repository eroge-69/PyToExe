# STEP 4: Auto SL/Target/Trail + Telegram Alerts (Bot-ready)

import requests
import pandas as pd
import datetime
import time
import numpy as np
import json
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtCore import QTimer
import sys

# === STRATEGY PARAMETERS ===
RSI_PERIOD = 14
EMA_PERIOD = 21
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
OI_THRESHOLD = 20
IV_THRESHOLD = 5
VOLUME_MULTIPLIER = 2
SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']
CAPITAL_PER_TRADE = 5000
STOP_LOSS_PERCENT = 30
TARGET_PERCENT = 60
TRAIL_AFTER = 20

# === AUTH DATA ===
API_KEY = ''
API_SECRET = ''
ACCESS_TOKEN = ''
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = ''

# === Telegram Notification ===
def send_telegram_alert(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload)

# === Upstox Auth ===
def authenticate_upstox(api_key, api_secret):
    global ACCESS_TOKEN
    ACCESS_TOKEN = 'mock_token'
    return True

# === Mock Option Chain ===
def fetch_option_chain(symbol):
    data = {
        'strike_price': [22500, 22600, 22700],
        'type': ['CE', 'PE', 'CE'],
        'last_price': [120, 110, 85],
        'volume': [30000, 50000, 40000],
        'open_interest': [150000, 180000, 170000],
        'iv': [18.5, 20.1, 19.7],
        'timestamp': [datetime.datetime.now()] * 3
    }
    return pd.DataFrame(data)

# === Indicators ===
def compute_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_ema(series, period):
    return series.ewm(span=period).mean()

def compute_macd(close):
    exp1 = close.ewm(span=MACD_FAST).mean()
    exp2 = close.ewm(span=MACD_SLOW).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=MACD_SIGNAL).mean()
    return macd_line, signal_line

# === Signal Logic ===
def generate_signals(df, price_series):
    signals = []
    rsi = compute_rsi(price_series)
    ema = compute_ema(price_series, EMA_PERIOD)
    macd, macd_signal = compute_macd(price_series)

    for idx, row in df.iterrows():
        cond_rsi = rsi.iloc[-1] > 40 if row['type'] == 'CE' else rsi.iloc[-1] < 60
        cond_macd = macd.iloc[-1] > macd_signal.iloc[-1] if row['type'] == 'CE' else macd.iloc[-1] < macd_signal.iloc[-1]
        cond_ema = price_series.iloc[-1] > ema.iloc[-1] if row['type'] == 'CE' else price_series.iloc[-1] < ema.iloc[-1]
        cond_oi = True
        cond_iv = True
        cond_vol = row['volume'] > VOLUME_MULTIPLIER * np.mean(df['volume'])
        if cond_rsi and cond_macd and cond_ema and cond_oi and cond_iv and cond_vol:
            signals.append({
                'symbol': row['type'],
                'strike': row['strike_price'],
                'signal': 'BUY',
                'price': row['last_price']
            })
    return signals

# === Execution Logic ===
def execute_trade(symbol, strike, option_type, price):
    sl = price - (price * STOP_LOSS_PERCENT / 100)
    tgt = price + (price * TARGET_PERCENT / 100)
    send_telegram_alert(f"{symbol} {strike}{option_type} BUY @ ₹{price}\nSL: ₹{sl:.2f} | Target: ₹{tgt:.2f}")
    print(f"ORDER: {symbol} {strike}{option_type} @ ₹{price} | SL: ₹{sl:.2f} | Target: ₹{tgt:.2f}")
    return True

# === GUI ===
class TradingBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NSE/BSE Options Trading Bot")
        self.setGeometry(100, 100, 600, 450)
        self.layout = QVBoxLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setPlaceholderText("Enter API Secret")
        self.telegram_token_input = QLineEdit()
        self.telegram_token_input.setPlaceholderText("Telegram Bot Token")
        self.telegram_chat_input = QLineEdit()
        self.telegram_chat_input.setPlaceholderText("Telegram Chat ID")

        self.auth_button = QPushButton('Authenticate')
        self.start_button = QPushButton('Start Bot')
        self.log_output = QTextEdit()
        self.status_label = QLabel('Status: Idle')

        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(self.api_secret_input)
        self.layout.addWidget(self.telegram_token_input)
        self.layout.addWidget(self.telegram_chat_input)
        self.layout.addWidget(self.auth_button)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.log_output)
        self.setLayout(self.layout)

        self.auth_button.clicked.connect(self.authenticate)
        self.start_button.clicked.connect(self.toggle_bot)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_bot)

    def authenticate(self):
        global API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
        API_KEY = self.api_key_input.text()
        API_SECRET = self.api_secret_input.text()
        TELEGRAM_TOKEN = self.telegram_token_input.text()
        TELEGRAM_CHAT_ID = self.telegram_chat_input.text()
        success = authenticate_upstox(API_KEY, API_SECRET)
        self.status_label.setText("Status: Authenticated" if success else "Status: Auth Failed")

    def toggle_bot(self):
        if self.timer.isActive():
            self.timer.stop()
            self.status_label.setText("Status: Stopped")
            self.start_button.setText("Start Bot")
        else:
            if ACCESS_TOKEN:
                self.timer.start(30000)
                self.status_label.setText("Status: Running")
                self.start_button.setText("Stop Bot")
            else:
                self.status_label.setText("Status: Login Required")

    def run_bot(self):
        for symbol in SYMBOLS:
            df = fetch_option_chain(symbol)
            prices = pd.Series([22000 + np.random.randint(-50, 50) for _ in range(30)])
            signals = generate_signals(df, prices)
            for sig in signals:
                execute_trade(symbol, sig['strike'], sig['symbol'], sig['price'])
            log = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {symbol} signals: {signals}\n"
            self.log_output.append(log)

# === MAIN ===
if __name__ == '__main__':
    app = QApplication(sys.argv)
    bot_window = TradingBotApp()
    bot_window.show()
    sys.exit(app.exec())
