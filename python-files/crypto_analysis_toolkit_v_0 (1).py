"""
Crypto Analysis Toolkit — v5.0 Professional Plan — Runnable Executable Version
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ccxt
import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import sys
import os

# --- Minimal Strategy Implementation ---
class BaseStrategy:
    def prepare(self, df):
        return df

    def generate_signals(self, df):
        signals = pd.DataFrame(index=df.index)
        signals['signal'] = 0
        signals['stoploss'] = df['close'] * 0.98
        signals['takeprofit'] = df['close'] * 1.02
        signals.loc[df.index[::10], 'signal'] = 1
        signals.loc[df.index[5::10], 'signal'] = -1
        return signals

class EnsembleStrategy(BaseStrategy):
    def __init__(self):
        self.auto_learn = False
        self.performance_history = []

# --- Data Fetching ---
def fetch_coin_data(symbol: str, timeframe: str = '1h', limit: int = 100, exchange_name: str = 'binance', cache: dict = None) -> pd.DataFrame:
    if cache is None:
        cache = {}
    key = f'{exchange_name}_{symbol}_{timeframe}_{limit}'
    if key in cache:
        return cache[key]
    exchange_class = getattr(ccxt, exchange_name)()
    bars = exchange_class.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    cache[key] = df
    return df

# --- GUI ---
class CryptoGUI:
    def __init__(self, strategy: EnsembleStrategy, coin_list):
        self.strategy = strategy
        self.coin_list = coin_list
        self.root = tk.Tk()
        self.root.title('Crypto Analysis Toolkit v5.0 Executable')
        self.create_widgets()
        self.updating = False
        self.cache = {}

    def create_widgets(self):
        ttk.Label(self.root, text='Select Coin:').grid(row=0, column=0, padx=5, pady=5)
        self.coin_var = tk.StringVar(value=self.coin_list[0])
        ttk.OptionMenu(self.root, self.coin_var, self.coin_list[0], *self.coin_list).grid(row=0, column=1, padx=5, pady=5)

        self.auto_learn_var = tk.BooleanVar(value=self.strategy.auto_learn)
        ttk.Checkbutton(self.root, text='Enable Auto-Learn', variable=self.auto_learn_var).grid(row=1, column=0, columnspan=2)

        ttk.Button(self.root, text='Run Analysis', command=self.run_analysis).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(self.root, text='Start Live Update', command=self.start_live_update).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(self.root, text='Export Data', command=self.export_data).grid(row=4, column=0, columnspan=2, pady=5)

        self.accuracy_label = ttk.Label(self.root, text='Last Accuracy: N/A')
        self.accuracy_label.grid(row=5, column=0, columnspan=2, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(10,5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)

    def run_analysis(self):
        coin = self.coin_var.get()
        self.strategy.auto_learn = self.auto_learn_var.get()
        df = fetch_coin_data(coin, cache=self.cache)
        df = self.strategy.prepare(df)
        signals = self.strategy.generate_signals(df)
        self.plot_signals(df, signals)
        self.last_signals = signals
        self.accuracy_label.config(text='Last Accuracy: Simulated')
        self.notify_signals(signals)

    def start_live_update(self, interval=60):
        if not self.updating:
            self.updating = True
            threading.Thread(target=self._live_update_loop, args=(interval,), daemon=True).start()

    def _live_update_loop(self, interval):
        while self.updating:
            self.run_analysis()
            time.sleep(interval)

    def plot_signals(self, df, signals):
        self.ax.clear()
        self.ax.plot(df.index, df['close'], label='Close', color='blue')
        self.ax.scatter(df.index[signals['signal']==1], df['close'][signals['signal']==1], marker='^', color='green', label='Buy')
        self.ax.scatter(df.index[signals['signal']==-1], df['close'][signals['signal']==-1], marker='v', color='red', label='Sell')
        self.ax.plot(df.index, signals['stoploss'], '--', color='orange', label='Stop Loss')
        self.ax.plot(df.index, signals['takeprofit'], '--', color='purple', label='Take Profit')
        self.ax.legend()
        self.canvas.draw()

    def notify_signals(self, signals):
        latest = signals.iloc[-1]
        if latest['signal'] == 1:
            print(f'Alert: Buy signal detected for {self.coin_var.get()}')
        elif latest['signal'] == -1:
            print(f'Alert: Sell signal detected for {self.coin_var.get()}')

    def export_data(self):
        if hasattr(self, 'last_signals'):
            file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files','*.csv')])
            if file_path:
                self.last_signals.to_csv(file_path)
                print(f'Data exported to {file_path}')

    def run(self):
        self.root.mainloop()

# --- Build Executable Instructions ---
# To create a downloadable executable, you can use PyInstaller:
# 1. Install PyInstaller: pip install pyinstaller
# 2. Run: pyinstaller --onefile --noconsole crypto_toolkit.py
# This will generate a .exe file in the 'dist' folder that can be run on Windows without Python.

# --- Run Toolkit ---
if __name__ == '__main__':
    coins = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    strategy = EnsembleStrategy()
    app = CryptoGUI(strategy, coins)
    app.run()
