import tkinter as tk
from tkinter import ttk
import urllib.request
import re
import webbrowser
import time

class StockScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Top Stocks Scanner")
        self.root.geometry("800x400")

        self.scan_button = tk.Button(root, text="Scan Market", command=self.scan_market)
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

    def parse_yahoo_gainers(self):
        url = "https://finance.yahoo.com/gainers?count=100&offset=0"
        content = self.fetch_url(url)
        stocks = []
        rows = re.findall(r'<tr class="[^"]*?simpTblRow[^"]*?">(.*?)</tr>', content, re.DOTALL)
        for row in rows:
            ticker = re.search(r'<a.*?title="([^"]+)" data-symbol="([^"]+)"', row)
            price = re.search(r'<td aria-label="Price \(Intraday\)"[^>]*><span[^>]*>([^<]+)</span>', row)
            pct_change = re.search(r'<td aria-label="% Change"[^>]*><span[^>]*>([^<]+)</span>', row)
            volume = re.search(r'<td aria-label="Volume"[^>]*><span[^>]*>([^<]+)</span>', row)
            avg_volume = re.search(r'<td aria-label="Avg Vol \(3 month\)"[^>]*><span[^>]*>([^<]+)</span>', row)
            if ticker and price and pct_change and volume and avg_volume:
                tick = ticker.group(2)
                pr = float(re.sub(r'[^\d.]', '', price.group(1)))
                pct = float(re.sub(r'[+%]', '', pct_change.group(1)))
                vol = self.parse_volume(volume.group(1))
                avg_vol = self.parse_volume(avg_volume.group(1))
                if pct >= 10 and 2 <= pr <= 20 and avg_vol > 0:
                    rel_vol = vol / avg_vol
                    if rel_vol >= 10:
                        stocks.append((tick, pr, pct, rel_vol, vol, avg_vol))
        return stocks

    def parse_volume(self, vol_str):
        vol_str = vol_str.replace(',', '')
        if 'M' in vol_str:
            return float(vol_str.replace('M', '')) * 1_000_000
        elif 'K' in vol_str:
            return float(vol_str.replace('K', '')) * 1_000
        elif 'B' in vol_str:
            return float(vol_str.replace('B', '')) * 1_000_000_000
        return float(vol_str)

    def parse_finviz_details(self, ticker):
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        content = self.fetch_url(url)
        sector_match = re.search(r'Sector</td><td width="40%" align="left">(?:<a[^>]*>)?([^<]+)', content)
        country_match = re.search(r'Country</td><td width="40%" align="left">(?:<a[^>]*>)?([^<]+)', content)
        float_match = re.search(r'Shs Float</td><td width="10%" align="right">(?:<a[^>]*>)?([^<]+)', content)
        sector = sector_match.group(1) if sector_match else "N/A"
        country = country_match.group(1) if country_match else "N/A"
        float_shares = self.parse_volume(float_match.group(1)) if float_match else 0
        return sector, country, float_shares / 1_000_000  # in millions

    def scan_market(self):
        self.tree.delete(*self.tree.get_children())
        candidates = self.parse_yahoo_gainers()
        for tick, pr, pct, rel_vol, _, _ in candidates:
            sector, country, float_m = self.parse_finviz_details(tick)
            if float_m < 20 and float_m > 0:
                self.tree.insert("", "end", values=(tick, f"${pr:.2f}", f"{pct:.2f}%", f"{rel_vol:.2f}x", f"{float_m:.2f}", sector, country))
        if not self.tree.get_children():
            tk.messagebox.showinfo("No Results", "No stocks match the criteria right now.")

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