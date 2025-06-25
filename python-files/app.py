
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import datetime

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local Stock Tracker (No Login)")
        self.root.geometry("800x600")

        self.stock_label = tk.Label(root, text="Enter Stock Symbol (e.g., INFY.NS):")
        self.stock_label.pack()

        self.stock_entry = tk.Entry(root)
        self.stock_entry.pack()

        self.fetch_button = tk.Button(root, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack()

        self.price_label = tk.Label(root, text="")
        self.price_label.pack()

        self.calc_frame = tk.Frame(root)
        self.calc_frame.pack(pady=10)

        self.num1 = tk.Entry(self.calc_frame, width=10)
        self.num1.grid(row=0, column=0)
        self.op = ttk.Combobox(self.calc_frame, values=["+", "-"], width=3)
        self.op.current(0)
        self.op.grid(row=0, column=1)
        self.num2 = tk.Entry(self.calc_frame, width=10)
        self.num2.grid(row=0, column=2)

        self.calc_btn = tk.Button(self.calc_frame, text="Calculate", command=self.calculate)
        self.calc_btn.grid(row=0, column=3, padx=5)

        self.calc_result = tk.Label(self.calc_frame, text="")
        self.calc_result.grid(row=0, column=4)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

    def fetch_data(self):
        symbol = self.stock_entry.get()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="7d", interval="1h")
            if df.empty:
                raise ValueError("No data found")
            last_price = df['Close'].iloc[-1]
            self.price_label.config(text=f"Current Price: ₹{last_price:.2f}")

            self.ax.clear()
            self.ax.plot(df.index, df['Close'], label="Close Price")
            self.ax.set_title(f"{symbol} - Last 7 Days (1h)")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Price")
            self.ax.legend()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

    def calculate(self):
        try:
            a = float(self.num1.get())
            b = float(self.num2.get())
            result = a + b if self.op.get() == "+" else a - b
            self.calc_result.config(text=f"= {result:.2f}")
        except ValueError:
            self.calc_result.config(text="Invalid input")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
