import time
import threading
import requests
import pandas as pd
import pandas_ta as ta
import winsound
import tkinter as tk

def fetch_eth_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "ETHUSDT", "interval": "1m", "limit": 100}
    response = requests.get(url, params=params)
    closes = [float(candle[4]) for candle in response.json()]
    return closes

def calculate_rsi(closes):
    df = pd.DataFrame(closes, columns=["close"])
    df["rsi"] = ta.rsi(df["close"], length=14)
    return df["rsi"].iloc[-1]

def check_rsi_loop():
    while True:
        try:
            closes = fetch_eth_data()
            rsi = calculate_rsi(closes)
            status = f"RSI فعلی: {rsi:.2f}"
            label_var.set(status)

            if rsi > 75:
                label_var.set(f"{status} ⚠️ اشباع خرید")
                winsound.Beep(1000, 600)
            elif rsi < 25:
                label_var.set(f"{status} ⚠️ اشباع فروش")
                winsound.Beep(600, 600)

        except Exception as e:
            label_var.set(f"❌ خطا: {e}")

        time.sleep(60)

# رابط گرافیکی
window = tk.Tk()
window.title("ربات هشدار RSI اتریوم")
window.geometry("300x100")

label_var = tk.StringVar()
label = tk.Label(window, textvariable=label_var, font=("Helvetica", 12))
label.pack(pady=20)
label_var.set("در حال دریافت داده...")

# اجرای حلقه بررسی در نخ جداگانه
threading.Thread(target=check_rsi_loop, daemon=True).start()

window.mainloop()