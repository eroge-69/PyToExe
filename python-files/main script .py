import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import requests
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from datetime import datetime
import platform
import os

if platform.system() == "Windows":
    import winsound

class PriceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Asset Crypto & Stock Tracker")

        # --- Asset Input Section ---
        tk.Label(root, text="Asset Type (crypto/stock):").grid(row=0, column=0, sticky="w")
        self.asset_type_entry = tk.Entry(root)
        self.asset_type_entry.insert(0, "crypto")
        self.asset_type_entry.grid(row=0, column=1)

        tk.Label(root, text="Symbol:").grid(row=1, column=0, sticky="w")
        self.asset_symbol_entry = tk.Entry(root)
        self.asset_symbol_entry.insert(0, "bitcoin")
        self.asset_symbol_entry.grid(row=1, column=1)

        tk.Label(root, text="Threshold:").grid(row=2, column=0, sticky="w")
        self.asset_threshold_entry = tk.Entry(root)
        self.asset_threshold_entry.insert(0, "0")
        self.asset_threshold_entry.grid(row=2, column=1)

        tk.Label(root, text="X% Change Alert:").grid(row=3, column=0, sticky="w")
        self.percent_alert_entry = tk.Entry(root)
        self.percent_alert_entry.insert(0, "5")
        self.percent_alert_entry.grid(row=3, column=1)

        self.assets = []
        self.asset_listbox = tk.Listbox(root, width=50)
        self.asset_listbox.grid(row=4, columnspan=2, padx=5, pady=5)

        self.add_asset_btn = tk.Button(root, text="Add Asset", command=self.add_asset)
        self.add_asset_btn.grid(row=5, column=0)

        self.remove_asset_btn = tk.Button(root, text="Remove Selected", command=self.remove_asset)
        self.remove_asset_btn.grid(row=5, column=1)

        self.save_button = tk.Button(root, text="💾 Save", command=self.save_assets)
        self.save_button.grid(row=6, column=0, pady=5)

        self.load_button = tk.Button(root, text="📂 Load", command=self.load_assets)
        self.load_button.grid(row=6, column=1, pady=5)

        # --- Email Settings ---
        self.email_enabled = tk.IntVar()
        tk.Checkbutton(root, text="Enable Email Alerts", variable=self.email_enabled).grid(row=7, columnspan=2, sticky="w")

        tk.Label(root, text="From Email:").grid(row=8, column=0, sticky="w")
        self.email_from = tk.Entry(root)
        self.email_from.grid(row=8, column=1)

        tk.Label(root, text="Password:").grid(row=9, column=0, sticky="w")
        self.email_pass = tk.Entry(root, show="*")
        self.email_pass.grid(row=9, column=1)

        tk.Label(root, text="To Email:").grid(row=10, column=0, sticky="w")
        self.email_to = tk.Entry(root)
        self.email_to.grid(row=10, column=1)

        # --- Remote Alert Settings ---
        tk.Label(root, text="Send Alerts To:").grid(row=11, column=0, sticky="w")
        self.alert_method = tk.StringVar(value="none")
        tk.OptionMenu(root, self.alert_method, "none", "telegram", "discord").grid(row=11, column=1)

        tk.Label(root, text="Telegram Bot Token / Discord Webhook:").grid(row=12, column=0, sticky="w")
        self.alert_token_entry = tk.Entry(root, width=40)
        self.alert_token_entry.grid(row=12, column=1)

        tk.Label(root, text="Telegram Chat ID (Telegram only):").grid(row=13, column=0, sticky="w")
        self.alert_chat_id_entry = tk.Entry(root)
        self.alert_chat_id_entry.grid(row=13, column=1)

        # --- Other Settings ---
        tk.Label(root, text="Interval (seconds):").grid(row=14, column=0, sticky="w")
        self.interval_entry = tk.Entry(root)
        self.interval_entry.insert(0, "60")
        self.interval_entry.grid(row=14, column=1)

        tk.Label(root, text="Sound Alert:").grid(row=15, column=0, sticky="w")
        self.sound_option = tk.StringVar(value="update")
        tk.OptionMenu(root, self.sound_option, "none", "update", "threshold").grid(row=15, column=1, sticky="w")

        # --- Console Log ---
        self.console = scrolledtext.ScrolledText(root, width=60, height=10, state="disabled")
        self.console.grid(row=16, columnspan=2, padx=5, pady=5)

        self.tracking = False
        self.track_button = tk.Button(root, text="Start Tracking", command=self.toggle_tracking)
        self.track_button.grid(row=17, column=0, pady=10)

        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.grid(row=17, column=1)

        self.load_assets()

    def log(self, message):
        self.console.config(state="normal")
        self.console.insert(tk.END, message + "\n")
        self.console.yview(tk.END)
        self.console.config(state="disabled")

    def add_asset(self):
        asset_type = self.asset_type_entry.get().strip().lower()
        symbol = self.asset_symbol_entry.get().strip().lower()
        try:
            threshold = float(self.asset_threshold_entry.get())
            percent_alert = float(self.percent_alert_entry.get())
        except:
            self.log("[Error] Invalid threshold or % alert")
            return
        if asset_type not in ("crypto", "stock"):
            self.log("[Error] Invalid asset type")
            return
        self.assets.append({
            "type": asset_type,
            "symbol": symbol,
            "threshold": threshold,
            "percent_alert": percent_alert,
            "prev_price": None
        })
        self.asset_listbox.insert(tk.END, f"{asset_type.upper()} - {symbol} - Threshold: {threshold} - %: {percent_alert}")

    def remove_asset(self):
        selection = self.asset_listbox.curselection()
        if selection:
            index = selection[0]
            self.asset_listbox.delete(index)
            del self.assets[index]

    def save_assets(self):
        try:
            with open("assets.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["type", "symbol", "threshold", "percent_alert"])
                for asset in self.assets:
                    writer.writerow([asset["type"], asset["symbol"], asset["threshold"], asset["percent_alert"]])
            self.log("✅ Assets saved.")
        except Exception as e:
            self.log(f"[Error] Saving assets: {e}")

    def load_assets(self):
        try:
            self.assets.clear()
            self.asset_listbox.delete(0, tk.END)
            with open("assets.csv", "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    asset = {
                        "type": row["type"],
                        "symbol": row["symbol"],
                        "threshold": float(row["threshold"]),
                        "percent_alert": float(row["percent_alert"]),
                        "prev_price": None
                    }
                    self.assets.append(asset)
                    self.asset_listbox.insert(tk.END, f"{asset['type'].upper()} - {asset['symbol']} - Threshold: {asset['threshold']} - %: {asset['percent_alert']}")
            self.log("📂 Assets loaded.")
        except Exception as e:
            self.log(f"[Error] Loading assets: {e}")

    def toggle_tracking(self):
        if not self.tracking:
            self.tracking = True
            self.track_button.config(text="Stop Tracking")
            threading.Thread(target=self.track_loop, daemon=True).start()
        else:
            self.tracking = False
            self.track_button.config(text="Start Tracking")

    def track_loop(self):
        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            self.log("[Error] Invalid interval")
            return
        while self.tracking:
            for asset in self.assets:
                self.update_asset(asset)
            time.sleep(interval)

    def update_asset(self, asset):
        symbol = asset["symbol"]
        asset_type = asset["type"]
        threshold = asset["threshold"]
        percent_alert = asset.get("percent_alert", 0)
        prev_price = asset.get("prev_price")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sound_mode = self.sound_option.get()

        if asset_type == "crypto":
            price = self.fetch_crypto_price(symbol)
        else:
            price = self.fetch_stock_price(symbol)

        if price is not None:
            self.log(f"{asset_type.upper()} {symbol.upper()} price: ${price}")
            self.export_to_csv(asset_type, symbol, price, timestamp)
            asset["prev_price"] = price

            if prev_price:
                change = abs((price - prev_price) / prev_price * 100)
                if change >= percent_alert:
                    self.log(f"⚠️ {symbol.upper()} moved {change:.2f}%!")
                    if self.email_enabled.get():
                        self.send_email(f"{symbol.upper()} {percent_alert}% Change!", f"Price changed by {change:.2f}% to ${price}")
                    self.send_remote_alert(f"{symbol.upper()} moved {change:.2f}% to ${price}")
                    if sound_mode != "none":
                        self.play_sound()

            if self.should_alert_value(price, threshold, sound_mode):
                self.play_sound()
                self.send_remote_alert(f"{asset_type.upper()} {symbol.upper()} price alert!\nPrice: ${price}")

    def should_alert_value(self, price, threshold, mode):
        try:
            if mode == "none":
                return False
            if mode == "update":
                return True
            if mode == "threshold" and price >= threshold:
                return True
        except:
            return False
        return False

    def play_sound(self):
        try:
            if platform.system() == "Windows":
                winsound.Beep(1000, 300)
            else:
                os.system('printf "\\a"')
        except Exception as e:
            self.log(f"[Error] Sound: {e}")

    def export_to_csv(self, asset_type, symbol, price, timestamp):
        filename = f"{asset_type}_prices.csv"
        try:
            with open(filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, symbol, price])
        except Exception as e:
            self.log(f"[Error] CSV: {e}")

    def fetch_crypto_price(self, asset_symbol):
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_symbol}&vs_currencies=usd"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data[asset_symbol]["usd"]
        except Exception as e:
            self.log(f"[Error] Crypto: {e}")
            return None

    def fetch_stock_price(self, ticker_symbol):
        try:
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period="1d")
            return data["Close"].iloc[-1]
        except Exception as e:
            self.log(f"[Error] Stock: {e}")
            return None

    def send_email(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_from.get()
            msg["To"] = self.email_to.get()
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email_from.get(), self.email_pass.get())
            server.sendmail(self.email_from.get(), self.email_to.get(), msg.as_string())
            server.quit()
            self.log("📧 Email sent.")
        except Exception as e:
            self.log(f"[Error] Email: {e}")

    def send_remote_alert(self, message):
        method = self.alert_method.get()
        token = self.alert_token_entry.get().strip()
        chat_id = self.alert_chat_id_entry.get().strip()

        try:
            if method == "telegram":
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": chat_id, "text": message}
                requests.post(url, data=payload)
                self.log("📩 Telegram alert sent.")
            elif method == "discord":
                payload = {"content": message}
                requests.post(token, json=payload)
                self.log("📩 Discord alert sent.")
        except Exception as e:
            self.log(f"[Error] Remote alert: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceTrackerApp(root)
    root.mainloop()