import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def get_stock_data(symbol):
    # Get 5 years of daily data for the selected stock
    stock = yf.download(symbol, period="5y", interval="1d")
    stock.dropna(inplace=True)
    return stock


def train_and_predict(stock_df):
    df = stock_df[['Open', 'High', 'Low', 'Close']].copy()
    df['Target_Open'] = df['Open'].shift(-1)
    df['Target_High'] = df['High'].shift(-1)
    df['Target_Low'] = df['Low'].shift(-1)
    df['Target_Close'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

    X = df[['Open', 'High', 'Low', 'Close']]
    y_open = df['Target_Open']
    y_high = df['Target_High']
    y_low = df['Target_Low']
    y_close = df['Target_Close']

    model_open = LinearRegression().fit(X, y_open)
    model_high = LinearRegression().fit(X, y_high)
    model_low = LinearRegression().fit(X, y_low)
    model_close = LinearRegression().fit(X, y_close)

    pred_open_test = model_open.predict(X)
    pred_high_test = model_high.predict(X)
    pred_low_test = model_low.predict(X)
    pred_close_test = model_close.predict(X)

    r2_open = r2_score(y_open, pred_open_test)
    r2_high = r2_score(y_high, pred_high_test)
    r2_low = r2_score(y_low, pred_low_test)
    r2_close = r2_score(y_close, pred_close_test)

    avg_accuracy = (r2_open + r2_high + r2_low + r2_close) / 4

    latest_data = X.iloc[[-1]]
    pred_open = model_open.predict(latest_data)[0]
    pred_high = model_high.predict(latest_data)[0]
    pred_low = model_low.predict(latest_data)[0]
    pred_close = model_close.predict(latest_data)[0]

    return round(pred_open, 2), round(pred_high, 2), round(pred_low, 2), round(pred_close, 2), round(avg_accuracy * 100, 2)


def show_predictions():
    symbol = stock_entry.get().strip().upper()
    if not symbol:
        result_text.set("⚠️ Please enter a valid stock symbol (e.g., RELIANCE.NS)")
        return

    try:
        status_label.config(text="Fetching data and predicting...")
        root.update_idletasks()
        stock_data = get_stock_data(symbol)
        pred_open, pred_high, pred_low, pred_close, accuracy = train_and_predict(stock_data)

        result_text.set(
            f"📈 Prediction for Next Trading Day ({symbol}):\n\n"
            f"🟢 Open: ₹{pred_open}\n"
            f"🔼 High: ₹{pred_high}\n"
            f"🔽 Low:  ₹{pred_low}\n"
            f"🔴 Close: ₹{pred_close}\n\n"
            f"🎯 Model Accuracy: ~{accuracy}%"
        )
        status_label.config(text="Prediction complete ✅")
    except Exception as e:
        result_text.set("❌ Error: " + str(e))
        status_label.config(text="Failed ❌")


# GUI Setup
root = tk.Tk()
root.title("Stock Next Day Predictor")
root.geometry("440x480")
root.configure(bg="#f2f2f2")

tk.Label(root, text="📊 Stock Next-Day Predictor", font=("Helvetica", 16, "bold"), bg="#f2f2f2").pack(pady=10)

# Input field

entry_frame = tk.Frame(root, bg="#f2f2f2")
entry_frame.pack(pady=5)

tk.Label(entry_frame, text="Enter Stock Symbol (e.g., ^NSEI):", bg="#f2f2f2").pack(side=tk.LEFT, padx=5)
stock_entry = ttk.Entry(entry_frame, width=20)
stock_entry.pack(side=tk.LEFT)

# Predict button
predict_btn = ttk.Button(root, text="Predict Next Day", command=show_predictions)
predict_btn.pack(pady=15)

# Results
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, font=("Courier", 11), bg="#f2f2f2", justify="left")
result_label.pack(pady=10)

# Status
status_label = tk.Label(root, text="", font=("Helvetica", 10), bg="#f2f2f2", fg="green")
status_label.pack(pady=5)

root.mainloop()
