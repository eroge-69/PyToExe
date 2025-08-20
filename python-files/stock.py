import tkinter as tk
from tkinter import ttk
import urllib.request
import re
import webbrowser
import datetime
import time

class StockScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Premarket Top Stocks Scanner")
        self.root.geometry("800x400")

        self.scan_button = tk.Button(root, text="Scan Market (Premarket)", command=self.scan_market)
        self.scan_button.pack(pady=10)

        self.tree = ttk.Treeview(root, columns=("Ticker", "Price", "% Up", "Rel Vol", "Float (M)", "Sector", "Country"), show="headings")
        self.tree.heading("Ticker", text="Ticker")
        self.tree.heading("Price", text="Price")
        self.tree.heading("% Up", text="% Up")
        self.tree.heading("Rel Vol", text="Rel Vol")
        self.tree.heading("Float (M)", text="Float (M)")
        self.tree.heading("Sector", text="Sector")
        self.tree.heading("Country", text="Country")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

    def fetch_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')

    def is_premarket(self):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))  # EDT
        hour = now.hour
        return 4 <= hour < 9 or (hour == 9 and now.minute <= 30)

    def parse_finviz_gainers(self):
        url = "https://finviz.com/screener.ashx?v=111&f=sh_avgvol_o50,sh_price_2to20&ft=3&o=-change"
        content = self.fetch_url(url)
        stocks = []
        rows = re.findall(r'<tr class="table-.*?">\s*<td[^>]*>.*?</td>\s*<td[^>]*><a href="quote\.ashx\?t=([^"]+)"[^>]*>[^<]+</a>.*?' +
                         r'<td[^>]*>[^<]*</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>([^<]+)</td>\s*' +
                         r'<td[^>]*>[^<]*</td>\s*<td[^>]*>([^<]+)</td>', content)
        for row in rows:
            ticker, price, change, volume = row
            price = float(re.sub(r'[^\d.]', '', price))
            pct = float(re.sub(r'[+%]', '', change))
            vol = self.parse_volume(volume)
            if pct >= 10 and 2 <= price <= 20:
                avg_vol = self.get_avg_volume(ticker)
                if avg_vol > 0:
                    rel_vol = vol / avg_vol
                    if rel_vol >= 10:
                        stocks.append((ticker, price, pct, rel_vol))
        return stocks

    def parse_volume(self, vol_str):
        vol_str = vol_str.replace(',', '')
        if 'M' in vol_str:
            return float(vol_str.replace('M', '')) * 1_000_000
        elif 'K' in vol_str:
            return float(vol_str.replace('K', '')) * 1_000
        return float(vol_str)

    def get_avg_volume(self, ticker):
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        content = self.fetch_url(url)
        avg_vol_match = re.search(r'Avg Volume</td><td[^>]*>([^<]+)</td>', content)
        return self.parse_volume(avg_vol_match.group(1)) if avg_vol_match else 0

    def parse_finviz_details(self, ticker):
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        content = self.fetch_url(url)
        sector_match = re.search(r'Sector</td><td[^>]*>(?:<a[^>]*>)?([^<]+)', content)
        country_match = re.search(r'Country</td><td[^>]*>(?:<a[^>]*>)?([^<]+)', content)
        float_match = re.search(r'Shs Float</td><td[^>]*>(?:<a[^>]*>)?([^<]+)', content)
        sector = sector_match.group(1) if sector_match else "N/A"
        country = country_match.group(1) if country_match else "N/A"
        float_shares = self.parse_volume(float_match.group(1)) if float_match else 0
        return sector, country, float_shares / 1_000_000

    def scan_market(self):
        if not self.is_premarket():
            tk.messagebox.showinfo("Market Hours", "Premarket scan available 4:00 AM to 9:30 AM EDT. Try regular hours scan.")
            return
        self.tree.delete(*self.tree.get_children())
        candidates = self.parse_finviz_gainers()
        for tick, pr, pct, rel_vol in candidates:
            sector, country, float_m = self.parse_finviz_details(tick)
            if float_m < 20 and float_m > 0:
                self.tree.insert("", "end", values=(tick, f"${pr:.2f}", f"{pct:.2f}%", f"{rel_vol:.2f}x", f"{float_m:.2f}", sector, country))
        if not self.tree.get_children():
            tk.messagebox.showinfo("No Results", "No stocks match the criteria in premarket.")

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        ticker = self.tree.item(item, "values")[0]
        news_url = f"https://finance.yahoo.com/quote/{ticker}/news"
        x_url = f"https://x.com/search?q={ticker}%20stock&src=typed_query"
        webbrowser.open(news_url)
        webbrowser.open(x_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockScanner(root)
    root.mainloop()