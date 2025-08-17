import tkinter as tk
from tkinter import ttk
import requests
import pandas as pd
import numpy as np
import time
import threading

# Timeframes (granularity in seconds for Coinbase candles)
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "3h": 10800,
    "4h": 14400,
}

def fetch_candles(granularity):
    url = f"https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity={granularity}"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.sort_values('time')
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_indicators(df):
    df["RSI"] = compute_rsi(df["close"], 14)
    df["VWAP"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["Pred%"] = ((df["close"] - df["VWAP"]) / df["VWAP"]) * 100
    return df

def score_dot(value, green_cond, yellow_cond=None):
    if green_cond(value):
        return "🟢"
    elif yellow_cond and yellow_cond(value):
        return "🟡"
    return "🔴"

class BitProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bit Pro - Full Snapshot")
        self.root.geometry("1400x800")

        # Notebook tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Core table
        self.tree_core = self._create_table(
            ["TF", "Price %", "RSI", "VWAP", "Pred%", "Decision"]
        )
        self.notebook.add(self.tree_core, text="🟩 Core")

        # Final Summary
        self.summary_text = tk.Text(root, height=12, wrap="word")
        self.summary_text.pack(fill="x", padx=10, pady=10)

        # Update loop
        self.update_data()
        self.auto_refresh()

    def _create_table(self, columns):
        frame = tk.Frame(self.notebook)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(expand=True, fill="both")
        self.tree = tree
        return frame

    def update_data(self):
        try:
            self.tree.delete(*self.tree.get_children())
            dots = []
            buyer_pressures = []

            for tf, gran in TIMEFRAMES.items():
                df = fetch_candles(gran)
                df = calculate_indicators(df)
                last = df.iloc[-1]
                prev = df.iloc[-2]
                price_change = ((last['close'] - prev['close']) / prev['close']) * 100

                rsi_dot = score_dot(last['RSI'], lambda v: v >= 55, lambda v: 45 <= v < 55)
                pred_dot = score_dot(last['Pred%'], lambda v: v >= 0.6, lambda v: 0.53 <= v < 0.6)
                price_dot = score_dot(price_change, lambda v: v >= 0)
                decision = "🟢 Long Bias" if rsi_dot=="🟢" and price_dot=="🟢" else "🟡 Neutral"

                self.tree.insert("", "end", values=[tf, f"{price_change:.2f}%", f"{last['RSI']:.1f}", f"{last['VWAP']:.2f}", f"{last['Pred%']:.2f}%", decision])

                dots.extend([price_dot, rsi_dot, pred_dot])
                buyer_pressures.append(max(0, min(100, 50 + price_change * 2)))

            greens = dots.count("🟢")
            yellows = dots.count("🟡")
            reds = dots.count("🔴")
            total = greens + yellows + reds
            avg_score = round(100 * (2*greens + 1*yellows) / (2*total), 1) if total > 0 else 0
            avg_buyer = round(sum(buyer_pressures)/len(buyer_pressures), 1) if buyer_pressures else 50
            avg_seller = 100 - avg_buyer
            net_pressure = "Bullish" if avg_buyer > avg_seller else ("Bearish" if avg_seller > avg_buyer else "Neutral")

            summary = f"""
🔎 Final Summary
• Dot Totals: 🟢 {greens} | 🟡 {yellows} | 🔴 {reds} = {total} dots
• Avg Score: {avg_score}%
• Buyer vs Seller Pressure: 🟢 {avg_buyer}% • 🔴 {avg_seller}% → {net_pressure}
"""
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary)

        except Exception as e:
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, f"Error fetching data: {e}")

    def auto_refresh(self):
        def loop():
            while True:
                self.update_data()
                time.sleep(30)
        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BitProApp(root)
    root.mainloop()
