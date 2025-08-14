import tkinter as tk
from tkinter import ttk, messagebox
import ccxt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from datetime import datetime
import math

class CryptoBotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Trading Bot")
        self.geometry("1200x800")
        self.configure(bg="#1e1e1e")  # Dark background

        self.exchange = None
        self.all_assets = []
        self.running = False
        self.initial_balance = 0
        self.pre_trade_balance = 0
        self.prices = []
        self.times = []
        self.buy_marks = []
        self.sell_marks = []
        self.can_buy = True
        self.holding_value = 0
        self.last_price = None
        self.holding_base = 0
        self.buy_price = 0

        # Styles for high contrast dark theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TButton", background="#1e1e1e", foreground="#ffffff")
        self.style.configure("TEntry", fieldbackground="#1e1e1e", foreground="#ffffff")
        self.style.configure("TCombobox", fieldbackground="#1e1e1e", foreground="#ffffff", arrowcolor="#ffffff")
        self.style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff")
        self.style.map("TCombobox", fieldbackground=[("readonly", "#1e1e1e")])
        self.style.map("TCombobox", selectbackground=[("readonly", "#1e1e1e")])
        self.style.map("TCombobox", selectforeground=[("readonly", "#1e1e1e")])

        # API Connection Section
        api_frame = ttk.LabelFrame(self, text="Binance API Connection")
        api_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(api_frame, text="API Key:").grid(row=0, column=0, padx=5, pady=5)
        self.api_key_entry = tk.Entry(api_frame, width=50)
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(api_frame, text="API Secret:").grid(row=1, column=0, padx=5, pady=5)
        self.api_secret_entry = tk.Entry(api_frame, width=50, show="*")
        self.api_secret_entry.grid(row=1, column=1, padx=5, pady=5)

        self.connect_frame = tk.Frame(api_frame, bg="#1e1e1e")
        self.connect_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.connect_btn = tk.Button(self.connect_frame, text="Connect", command=self.connect_to_binance, bg="#1e1e1e", fg="#ffffff")
        self.connect_btn.pack(side="left")
        self.disconnect_btn = tk.Button(self.connect_frame, text="Disconnect", command=self.disconnect_from_binance, bg="#1e1e1e", fg="#ffffff", state="disabled")
        self.disconnect_btn.pack(side="left", padx=5)

        # Pair Selection Section
        pair_frame = ttk.LabelFrame(self, text="Select Crypto Pair")
        pair_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(pair_frame, text="Crypto to Sell (Base):").grid(row=0, column=0, padx=5, pady=5)
        self.base_var = tk.StringVar()
        self.base_dropdown = ttk.Combobox(pair_frame, textvariable=self.base_var, state="readonly", postcommand=self.update_dropdowns)
        self.base_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.base_dropdown.bind("<KeyRelease>", self.search_dropdown)

        tk.Label(pair_frame, text="Crypto to Buy (Quote):").grid(row=1, column=0, padx=5, pady=5)
        self.quote_var = tk.StringVar()
        self.quote_dropdown = ttk.Combobox(pair_frame, textvariable=self.quote_var, state="readonly", postcommand=self.update_dropdowns)
        self.quote_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.quote_dropdown.bind("<KeyRelease>", self.search_dropdown)

        # Threshold Strategy Section
        strategy_frame = ttk.LabelFrame(self, text="Threshold Strategy")
        strategy_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(strategy_frame, text="Buy Threshold (Price <=):").grid(row=0, column=0, padx=5, pady=5)
        self.buy_th_entry = tk.Entry(strategy_frame)
        self.buy_th_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(strategy_frame, text="Sell Threshold (Price >=):").grid(row=1, column=0, padx=5, pady=5)
        self.sell_th_entry = tk.Entry(strategy_frame)
        self.sell_th_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(strategy_frame, text="Trade Quantity (in Base):").grid(row=2, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(strategy_frame)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        self.full_balance_var = tk.BooleanVar()
        self.full_balance_check = ttk.Checkbutton(strategy_frame, text="Use Full Balance", variable=self.full_balance_var, command=self.toggle_quantity_entry)
        self.full_balance_check.grid(row=3, column=0, columnspan=2, pady=5)

        self.start_btn = tk.Button(strategy_frame, text="Start Bot", command=self.toggle_bot, bg="#1e1e1e", fg="#ffffff")
        self.start_btn.grid(row=4, column=0, pady=10)

        self.running_label = tk.Label(strategy_frame, text="", fg="#00ff00", bg="#1e1e1e")
        self.running_label.grid(row=4, column=1, pady=10)

        # Holding Value
        self.holding_label = tk.Label(strategy_frame, text="Holding Value: $0.00", fg="#ffffff", bg="#1e1e1e")
        self.holding_label.grid(row=5, column=0, columnspan=2, pady=5)

        # Stats Section
        stats_frame = ttk.LabelFrame(self, text="Account Stats")
        stats_frame.pack(pady=10, padx=10, fill="x")

        self.balance_label = tk.Label(stats_frame, text="Total Account Balance: $0.00", fg="#ffffff", bg="#1e1e1e")
        self.balance_label.pack(pady=5)

        self.pnl_label = tk.Label(stats_frame, text="PNL: 0.00%", fg="#ffffff", bg="#1e1e1e")
        self.pnl_label.pack(pady=5)

        # Chart Section
        chart_frame = ttk.LabelFrame(self, text="Price Chart")
        chart_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.fig = plt.Figure(figsize=(10, 5), dpi=100, facecolor="#1e1e1e")
        self.ax = self.fig.add_subplot(111, facecolor="#2d2d2d")
        self.ax.set_title("Price Chart", color="#ffffff")
        self.ax.tick_params(colors="#ffffff")
        self.ax.spines['top'].set_color("#ffffff")
        self.ax.spines['bottom'].set_color("#ffffff")
        self.ax.spines['left'].set_color("#ffffff")
        self.ax.spines['right'].set_color("#ffffff")
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def toggle_quantity_entry(self):
        self.quantity_entry.configure(state="disabled" if self.full_balance_var.get() else "normal")

    def update_dropdowns(self):
        if self.exchange:
            self.base_dropdown['values'] = self.all_assets
            self.quote_dropdown['values'] = self.all_assets

    def search_dropdown(self, event):
        value = event.widget.get()
        if value == '':
            event.widget['values'] = self.all_assets
        else:
            data = [asset for asset in self.all_assets if value.lower() in asset.lower()]
            event.widget['values'] = data

    def connect_to_binance(self):
        api_key = self.api_key_entry.get()
        api_secret = self.api_secret_entry.get()
        try:
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'},
            })
            self.connect_btn.configure(text="Connected", state="disabled")
            self.disconnect_btn.configure(state="normal")

            # Fetch all assets
            markets = self.exchange.load_markets()
            bases = set()
            quotes = set()
            for symbol, info in markets.items():
                base, quote = info['base'], info['quote']
                bases.add(base)
                quotes.add(quote)
            self.all_assets = sorted(list(bases.union(quotes)))

            if self.all_assets:
                self.base_var.set(self.all_assets[0])
                self.quote_var.set(self.all_assets[0])
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")

    def disconnect_from_binance(self):
        self.exchange = None
        self.connect_btn.configure(text="Connect", state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.base_dropdown['values'] = []
        self.quote_dropdown['values'] = []
        self.base_var.set("")
        self.quote_var.set("")

    def get_precision_and_min_quantity(self, symbol):
        try:
            market = self.exchange.markets[symbol]
            precision = market['precision']['amount']
            min_quantity = market['limits']['amount']['min']
            return precision, min_quantity
        except Exception as e:
            print(f"Error fetching market info for {symbol}: {e}")
            return None, None

    def format_quantity(self, quantity, precision, min_quantity):
        if quantity is None or precision is None or min_quantity is None:
            return None
        try:
            # Round down to avoid exceeding balance
            rounded_qty = math.floor(quantity * (10 ** precision)) / (10 ** precision)
            if rounded_qty < min_quantity:
                return None
            return rounded_qty
        except:
            return None

    def toggle_bot(self):
        if self.running:
            self.running = False
            self.start_btn.configure(text="Start Bot")
            self.running_label.configure(text="")
        else:
            base = self.base_var.get()
            quote = self.quote_var.get()
            symbol = f"{base}/{quote}"
            if not base or not quote or symbol not in self.exchange.markets:
                messagebox.showerror("Error", "Invalid trading pair.")
                return
            try:
                float(self.buy_th_entry.get())
                float(self.sell_th_entry.get())
                if not self.full_balance_var.get():
                    float(self.quantity_entry.get())
                self.running = True
                self.start_btn.configure(text="Stop Bot")
                self.running_label.configure(text="Running")
                self.initial_balance = self.get_total_usd()
                self.pre_trade_balance = self.initial_balance
                self.prices = []
                self.times = []
                self.buy_marks = []
                self.sell_marks = []
                self.can_buy = True
                self.holding_value = 0
                self.last_price = None
                self.holding_base = 0
                self.buy_price = 0
                threading.Thread(target=self.bot_loop, daemon=True).start()
            except ValueError:
                messagebox.showerror("Error", "Invalid input values.")

    def bot_loop(self):
        base = self.base_var.get()
        quote = self.quote_var.get()
        symbol = f"{base}/{quote}"
        try:
            buy_th = float(self.buy_th_entry.get())
            sell_th = float(self.sell_th_entry.get())
            quantity = float(self.quantity_entry.get()) if not self.full_balance_var.get() else None
        except ValueError:
            messagebox.showerror("Error", "Invalid input values.")
            self.toggle_bot()
            return

        precision, min_quantity = self.get_precision_and_min_quantity(symbol)

        while self.running:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                price = float(ticker['last'])
                now = datetime.now()
                self.prices.append(price)
                self.times.append(now)
                if len(self.prices) > 300:  # Limit data points to avoid high RAM
                    self.prices = self.prices[-300:]
                    self.times = self.times[-300:]

                trade_qty = quantity
                if self.full_balance_var.get():
                    quote_balance = float(self.exchange.fetch_balance()[quote]['free'])
                    trade_qty = quote_balance / price if price > 0 else 0

                formatted_qty = self.format_quantity(trade_qty, precision, min_quantity)

                if self.can_buy and price <= buy_th and formatted_qty:
                    try:
                        self.exchange.create_market_buy_order(symbol, formatted_qty)
                        self.buy_marks.append((now, price))
                        self.can_buy = False
                        self.holding_base = formatted_qty
                        self.buy_price = price
                        self.after(0, lambda: messagebox.showinfo("Order", f"Bought {formatted_qty} {base} at {price}"))
                    except Exception as e:
                        print(f"Buy order failed: {e}")
                        self.after(0, lambda: messagebox.showerror("Error", f"Buy order failed: {e}"))

                if not self.can_buy and price >= sell_th:
                    try:
                        base_balance = float(self.exchange.fetch_balance()[base]['free'])
                        sell_qty = min(trade_qty, base_balance) if trade_qty else base_balance
                        formatted_sell_qty = self.format_quantity(sell_qty, precision, min_quantity)
                        if formatted_sell_qty:
                            self.exchange.create_market_sell_order(symbol, formatted_sell_qty)
                            self.sell_marks.append((now, price))
                            self.can_buy = True
                            self.holding_base = 0
                            self.buy_price = 0
                            self.after(0, lambda: messagebox.showinfo("Order", f"Sold {formatted_sell_qty} {base} at {price}"))
                        else:
                            print(f"Sell order skipped: Quantity {sell_qty} below minimum {min_quantity}")
                    except Exception as e:
                        print(f"Sell order failed: {e}")
                        self.after(0, lambda: messagebox.showerror("Error", f"Sell order failed: {e}"))

                # Update holding value
                if not self.can_buy:
                    self.holding_value = self.holding_base * price
                    color = "#00ff00" if price > self.last_price else "#ff0000" if price < self.last_price else "#ffffff"
                    self.after(0, lambda c=color: self.holding_label.configure(text=f"Holding Value: ${self.holding_value:.2f}", fg=c))
                else:
                    self.after(0, lambda: self.holding_label.configure(text="Holding Value: $0.00", fg="#ffffff"))

                self.last_price = price

                self.after(0, self.update_chart)
                self.after(0, self.update_stats)
            except Exception as e:
                print(f"Error in bot loop: {e}")
            time.sleep(1)  # Update every second, low CPU

    def update_chart(self):
        self.ax.clear()
        self.ax.plot(self.times, self.prices, 'c-', label="Price")  # Cyan for visibility
        if self.buy_marks:
            buy_times, buy_prices = zip(*self.buy_marks)
            self.ax.scatter(buy_times, buy_prices, color='green', marker='^', label="Buy")
        if self.sell_marks:
            sell_times, sell_prices = zip(*self.sell_marks)
            self.ax.scatter(sell_times, sell_prices, color='red', marker='v', label="Sell")
        self.ax.legend(loc="upper left", labelcolor="#ffffff")
        self.ax.set_xlabel("Time", color="#ffffff")
        self.ax.set_ylabel("Price", color="#ffffff")
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def update_stats(self):
        total_usd = self.get_total_usd()
        self.balance_label.configure(text=f"Total Account Balance: ${total_usd:.2f}")
        if self.pre_trade_balance > 0:
            pnl = ((total_usd - self.pre_trade_balance) / self.pre_trade_balance) * 100
            color = "#00ff00" if pnl > 0 else "#ff0000" if pnl < 0 else "#ffffff"
            self.pnl_label.configure(text=f"PNL: {pnl:.2f}%", fg=color)

    def get_total_usd(self):
        try:
            balance = self.exchange.fetch_balance()
            total = 0.0
            for asset, info in balance['total'].items():
                amt = float(info)
                if amt > 0:
                    if asset == 'USDT':
                        total += amt
                    else:
                        try:
                            ticker = self.exchange.fetch_ticker(f"{asset}/USDT")
                            total += amt * float(ticker['last'])
                        except:
                            pass
            return total
        except:
            return 0.0

if __name__ == "__main__":
    app = CryptoBotApp()
    app.mainloop()