"""
BTC Backtester GUI
===================

Features:
- GUI interface (Tkinter)
- Start / Stop buttons
- Progress bar + log box
- System Monitor (CPU, RAM usage %)
- Internet Speed (Download/Upload)
- Backtesting logic integrated (simplified)

Requirements:
    pip install ccxt pandas numpy psutil speedtest-cli tqdm ta
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import psutil
import speedtest
from datetime import datetime, timedelta
import ccxt
import pandas as pd
import numpy as np

# ---------------------------
# Global state
# ---------------------------
running = False

# ---------------------------
# Internet Speed Check
# ---------------------------
def get_internet_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Mbps
        upload_speed = st.upload() / 1_000_000
        return f"Down: {download_speed:.2f} Mbps | Up: {upload_speed:.2f} Mbps"
    except Exception:
        return "No Connection"

# ---------------------------
# System Monitor
# ---------------------------
def update_system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"CPU: {cpu:.1f}% | RAM: {ram:.1f}%"

# ---------------------------
# Data Fetcher (1m only for demo)
# ---------------------------
def fetch_ohlcv(symbol="BTC/USDT", timeframe="1m", since_days=5):
    ex = ccxt.binance()
    since = int((datetime.utcnow() - timedelta(days=since_days)).timestamp() * 1000)
    bars = ex.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=1000)
    df = pd.DataFrame(bars, columns=["ts","open","high","low","close","volume"])
    df["datetime"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.set_index("datetime")
    return df

# ---------------------------
# Backtesting logic (very simplified)
# ---------------------------
def run_backtest(progress_var, log_box):
    global running
    log_box.insert(tk.END, "Fetching BTC/USDT data...\n")
    log_box.see(tk.END)

    try:
        df = fetch_ohlcv(since_days=1)  # 1 day demo
    except Exception as e:
        log_box.insert(tk.END, f"Data fetch error: {e}\n")
        return

    log_box.insert(tk.END, f"Loaded {len(df)} candles.\n")
    log_box.see(tk.END)

    total_steps = len(df)
    step_count = 0

    for ts, row in df.iterrows():
        if not running:
            log_box.insert(tk.END, "Stopped by user.\n")
            return

        # fake strategy: detect big candles
        if (row["high"] - row["low"]) / row["open"] > 0.01:
            log_box.insert(tk.END, f"{ts} - Big Move detected!\n")

        step_count += 1
        progress = int((step_count / total_steps) * 100)
        progress_var.set(progress)
        log_box.see(tk.END)
        time.sleep(0.05)  # simulate processing time

    log_box.insert(tk.END, "✅ Backtest Completed!\n")
    log_box.see(tk.END)

# ---------------------------
# GUI Functions
# ---------------------------
def start_backtest(progress_var, log_box, start_btn, stop_btn):
    global running
    if running:
        messagebox.showinfo("Info", "Backtest already running!")
        return
    running = True
    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)

    # clear log
    log_box.delete(1.0, tk.END)

    # threading
    t = threading.Thread(target=run_backtest, args=(progress_var, log_box))
    t.start()

def stop_backtest(start_btn, stop_btn):
    global running
    running = False
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)

def update_status_bar(status_label):
    while True:
        sys_stats = update_system_stats()
        net_stats = get_internet_speed()
        status_label.config(text=f"{sys_stats} | {net_stats}")
        time.sleep(3)

# ---------------------------
# Main GUI
# ---------------------------
def main_gui():
    root = tk.Tk()
    root.title("BTC Backtester GUI")
    root.geometry("700x500")

    # Progress bar
    progress_var = tk.IntVar()
    progress = ttk.Progressbar(root, maximum=100, variable=progress_var)
    progress.pack(fill="x", padx=10, pady=10)

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    start_btn = tk.Button(btn_frame, text="Start Backtest", width=15,
                          command=lambda: start_backtest(progress_var, log_box, start_btn, stop_btn))
    start_btn.pack(side=tk.LEFT, padx=5)

    stop_btn = tk.Button(btn_frame, text="Stop", width=15,
                         command=lambda: stop_backtest(start_btn, stop_btn), state=tk.DISABLED)
    stop_btn.pack(side=tk.LEFT, padx=5)

    # Log box
    log_box = tk.Text(root, height=20)
    log_box.pack(fill="both", padx=10, pady=10, expand=True)

    # Status bar
    status_label = tk.Label(root, text="System Info Loading...", anchor="w")
    status_label.pack(fill="x", side=tk.BOTTOM)

    # Thread for status updates
    threading.Thread(target=update_status_bar, args=(status_label,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main_gui()
