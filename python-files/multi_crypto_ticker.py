import tkinter as tk
from tkinter import Canvas, Label, Frame, simpledialog, messagebox
import asyncio
import websockets
import json
import threading
from queue import Queue
from collections import deque
import ssl
import time
import requests
import os
import sys
# === NEW: Imports for API authentication ===
import hmac
import hashlib
from urllib.parse import urlencode

# === DISABLE PROXY ===
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

# === SETTINGS ===
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 260 # --- MODIFIED: Increased height to fit new info
SECONDS_BETWEEN_UPDATES = 5.0
MAX_PRICES_IN_CHART = 75
GUI_UPDATE_INTERVAL_MS = 100

PRICE_FONT_SIZE = 25
SYMBOL_FONT_SIZE = 16
# === NEW: Font for position details ===
POSITION_FONT_SIZE = 11

BACKGROUND_COLOR = 'black'
TRANSPARENT_COLOR = '#000001'
FONT_COLOR = 'white'
PRICE_UP_COLOR = '#26a69a'
PRICE_DOWN_COLOR = '#ef5350'
CHART_LINE_COLOR = '#6c757d'
FONT_PRICE = ("Arial", PRICE_FONT_SIZE, "bold")
FONT_SYMBOL = ("Arial", SYMBOL_FONT_SIZE)
# === NEW: Font definition for position details ===
FONT_POSITION = ("Arial", POSITION_FONT_SIZE)
CLOCK_COLOR = "#878487"

FUTURES_STREAM_URL = "wss://fstream.binance.com"
REST_TICKER_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"
# === NEW: Authenticated endpoint for positions ===
FUTURES_API_URL = "https://fapi.binance.com"
POSITION_ENDPOINT = "/fapi/v2/positionRisk"

SYMBOLS_FILE = "symbols.txt"
CONFIG_FILE = "config.json" # === NEW ===

# === NEW: Function to load API keys ===
def load_api_keys():
    if not os.path.exists(CONFIG_FILE):
        print(f"ERROR: Configuration file '{CONFIG_FILE}' not found.")
        print("Please create it with your 'api_key' and 'api_secret'.")
        messagebox.showerror("Config Error", f"Configuration file '{CONFIG_FILE}' not found. The application will exit.")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        config = json.load(f)
        if "api_key" not in config or "api_secret" not in config:
            print("ERROR: 'api_key' or 'api_secret' not found in config.json.")
            messagebox.showerror("Config Error", "API Key/Secret not found in config.json. The application will exit.")
            sys.exit(1)
        return config["api_key"], config["api_secret"]

# --- MODIFIED: Load keys at the start ---
API_KEY, API_SECRET = load_api_keys()

def load_symbols():
    if not os.path.exists(SYMBOLS_FILE):
        with open(SYMBOLS_FILE, "w") as f:
            f.write("BTCUSDT,ETHUSDT,SOLUSDT")
    with open(SYMBOLS_FILE) as f:
        return [s.strip().upper() for s in f.read().split(',') if s.strip()]

SYMBOLS = load_symbols()

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def listen(queue):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    streams = '/'.join([f"{s.lower()}@aggTrade" for s in SYMBOLS])
    uri = f"{FUTURES_STREAM_URL}/stream?streams={streams}"
    while True:
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                while True:
                    message = await websocket.recv()
                    payload = json.loads(message)
                    if 'stream' in payload and 'data' in payload:
                        symbol = payload['stream'].split('@')[0].upper()
                        price = float(payload['data']['p'])
                        queue.put((symbol, price))
        except Exception as e:
            print(f"WebSocket error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

def run_data_fetcher(queue):
    loop = asyncio.new_event_loop()
    threading.Thread(target=start_async_loop, args=(loop,), daemon=True).start()
    loop.call_soon_threadsafe(asyncio.create_task, listen(queue))

def fetch_24h_changes(ticker_queue):
    while True:
        try:
            for symbol in SYMBOLS:
                response = requests.get(f"{REST_TICKER_URL}?symbol={symbol}", timeout=10)
                data = response.json()
                change = float(data['priceChangePercent'])
                ticker_queue.put((symbol, change))
            time.sleep(60)
        except requests.exceptions.ProxyError:
            print("⚠️ Proxy error: Check if your proxy/VPN is blocking requests.")
        except requests.exceptions.ConnectionError:
            print("⚠️ Connection error: Target unreachable. Check internet connection.")
        except Exception as e:
            print(f"24h API error: {e}")
        time.sleep(10)

# === NEW: Function to fetch open positions ===
def fetch_open_positions(position_queue, api_key, api_secret):
    while True:
        try:
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            query_string = urlencode(params)
            signature = hmac.new(api_secret.encode('utf-8'), msg=query_string.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
            params['signature'] = signature
            
            headers = {'X-MBX-APIKEY': api_key}
            url = f"{FUTURES_API_URL}{POSITION_ENDPOINT}?{urlencode(params)}"
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if isinstance(data, list):
                positions = {}
                for pos in data:
                    # We only care about positions with a non-zero amount
                    if float(pos['positionAmt']) != 0:
                        positions[pos['symbol']] = {
                            'entryPrice': float(pos['entryPrice']),
                            'positionAmt': float(pos['positionAmt']),
                            'unRealizedProfit': float(pos['unRealizedProfit'])
                        }
                position_queue.put(positions)
            else:
                print(f"Error fetching positions: {data}")

        except Exception as e:
            print(f"Position API error: {e}")
        time.sleep(5) # Fetch positions every 5 seconds


class MultiCryptoTicker:
    def __init__(self, root):
        self.root = root
        self.labels_price = {}
        self.labels_change = {}
        # === NEW: Dictionaries for position labels ===
        self.labels_position_entry = {}
        self.labels_position_size = {}
        self.labels_position_pnl = {}
        
        self.charts = {}
        self.prices_data = {}
        self.last_prices = {}
        self.last_update_time = {}

        self.setup_window()

        main_frame = Frame(self.root, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        coin_container = Frame(main_frame, bg=BACKGROUND_COLOR)
        coin_container.pack(side='left', expand=True, fill='both')

        for symbol in SYMBOLS:
            self.create_coin_section(symbol, coin_container)

        self.time_canvas = Canvas(main_frame, width=350, height=160, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.time_canvas.pack(side='right', padx=(20, 10), anchor='n') # --- MODIFIED: Anchor to top
        self.update_clock()
        
        add_btn = tk.Button(self.root, text="+", font=("Arial", 18), bg="gray20", fg="white", command=self.add_symbol_popup, borderwidth=0)
        add_btn.place(x=15, y=15, width=30, height=30)

        self.data_queue = Queue()
        self.ticker_queue = Queue()
        self.position_queue = Queue() # === NEW ===

        threading.Thread(target=run_data_fetcher, args=(self.data_queue,), daemon=True).start()
        threading.Thread(target=fetch_24h_changes, args=(self.ticker_queue,), daemon=True).start()
        # === NEW: Start the position fetcher thread ===
        threading.Thread(target=fetch_open_positions, args=(self.position_queue, API_KEY, API_SECRET), daemon=True).start()

        self.process_queue()
        self.process_24h_change()
        self.process_positions() # === NEW ===

    def setup_window(self):
        self.root.title("Crypto Futures Ticker")
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+200+200')
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", 1)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

    # --- MODIFIED: Function to create coin section with new labels ---
    def create_coin_section(self, symbol, parent_frame):
        section_frame = Frame(parent_frame, bg=BACKGROUND_COLOR)
        section_frame.pack(side='left', padx=20, expand=True, fill='x', anchor='n')

        display_symbol = symbol.replace('USDT', '/USDT')
        symbol_label = Label(section_frame, text=display_symbol, font=FONT_SYMBOL, bg=BACKGROUND_COLOR, fg='gray')
        symbol_label.pack()

        price_label = Label(section_frame, text="Loading...", font=FONT_PRICE, bg=BACKGROUND_COLOR, fg=FONT_COLOR)
        price_label.pack()
        self.labels_price[symbol] = price_label

        change_label = Label(section_frame, text="0.00%", font=("Arial", 14), bg=BACKGROUND_COLOR, fg='gray')
        change_label.pack()
        self.labels_change[symbol] = change_label

        chart_canvas = Canvas(section_frame, height=45, bg=BACKGROUND_COLOR, highlightthickness=0)
        chart_canvas.pack(pady=10, fill='x', expand=True)
        self.charts[symbol] = chart_canvas

        # === NEW: Frame and labels for open position details ===
        position_frame = Frame(section_frame, bg=BACKGROUND_COLOR)
        position_frame.pack(pady=5)
        
        entry_label = Label(position_frame, text="", font=FONT_POSITION, bg=BACKGROUND_COLOR, fg='gray')
        entry_label.pack()
        self.labels_position_entry[symbol] = entry_label

        size_label = Label(position_frame, text="", font=FONT_POSITION, bg=BACKGROUND_COLOR, fg='gray')
        size_label.pack()
        self.labels_position_size[symbol] = size_label

        pnl_label = Label(position_frame, text="", font=FONT_POSITION, bg=BACKGROUND_COLOR, fg='gray')
        pnl_label.pack()
        self.labels_position_pnl[symbol] = pnl_label

        self.prices_data[symbol] = deque(maxlen=MAX_PRICES_IN_CHART)
        self.last_prices[symbol] = 0.0
        self.last_update_time[symbol] = 0.0
        
    def process_queue(self):
        try:
            while not self.data_queue.empty():
                symbol, new_price = self.data_queue.get_nowait()
                current_time = time.time()
                if current_time - self.last_update_time.get(symbol, 0) > SECONDS_BETWEEN_UPDATES:
                    self.update_display(symbol, new_price)
                    self.last_update_time[symbol] = current_time
        finally:
            self.root.after(GUI_UPDATE_INTERVAL_MS, self.process_queue)

    def process_24h_change(self):
        try:
            while not self.ticker_queue.empty():
                symbol, change = self.ticker_queue.get_nowait()
                label = self.labels_change.get(symbol)
                if label:
                    label.config(text=f"{change:.2f}%", fg=PRICE_UP_COLOR if change >= 0 else PRICE_DOWN_COLOR)
        finally:
            self.root.after(1000, self.process_24h_change)

    # === NEW: Function to process and display position data ===
    def process_positions(self):
        try:
            # Get the latest full snapshot of all positions
            all_positions = None
            while not self.position_queue.empty():
                all_positions = self.position_queue.get_nowait()

            if all_positions is not None:
                # Iterate through the symbols displayed on the ticker
                for symbol in SYMBOLS:
                    entry_label = self.labels_position_entry[symbol]
                    size_label = self.labels_position_size[symbol]
                    pnl_label = self.labels_position_pnl[symbol]

                    # Check if there's an open position for this symbol
                    if symbol in all_positions:
                        pos = all_positions[symbol]
                        entry_price = pos['entryPrice']
                        pos_size = pos['positionAmt']
                        pnl = pos['unRealizedProfit']

                        entry_label.config(text=f"Entry: {entry_price:,.2f}")
                        size_label.config(text=f"Size: {pos_size}")
                        pnl_label.config(
                            text=f"PnL: {pnl:,.2f}",
                            fg=PRICE_UP_COLOR if pnl >= 0 else PRICE_DOWN_COLOR
                        )
                    else:
                        # If no open position, clear the labels
                        entry_label.config(text="")
                        size_label.config(text="")
                        pnl_label.config(text="")
        finally:
            # Check for new position data every second
            self.root.after(1000, self.process_positions)

    def update_display(self, symbol, price):
        if symbol not in self.labels_price:
            return
        label = self.labels_price[symbol]
        last_price = self.last_prices.get(symbol, 0)
        
        if price > last_price:
            color = PRICE_UP_COLOR
        elif price < last_price:
            color = PRICE_DOWN_COLOR
        else:
            color = FONT_COLOR
            
        label.config(fg=color)
        if price != last_price:
            self.root.after(1000, lambda: label.config(fg=FONT_COLOR))

        self.last_prices[symbol] = price
        price_text = f"{price:,.2f}" if price >= 10 else f"{price:,.4f}"
        label.config(text=price_text)

        self.prices_data[symbol].append(price)
        self.draw_chart(symbol)

    def draw_chart(self, symbol):
        canvas = self.charts[symbol]
        prices = self.prices_data[symbol]
        canvas.delete("all")
        if len(prices) < 2:
            return
        
        min_p, max_p = min(prices), max(prices)
        price_range = max_p - min_p if max_p > min_p else 1
        
        canvas.update_idletasks()
        canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()

        if canvas_w <= 1 or canvas_h <= 1: return
            
        points = []
        for i, price in enumerate(prices):
            x = (i / (MAX_PRICES_IN_CHART - 1)) * canvas_w
            y = canvas_h - ((price - min_p) / price_range * (canvas_h - 4)) - 2
            points.extend([x, y])
            
        if len(points) > 3:
            canvas.create_line(points, fill=CHART_LINE_COLOR, width=2, smooth=True)

    def update_clock(self):
        self.time_canvas.delete("all")
        current_time_str = time.strftime("%I:%M %p").lstrip('0')
        canvas_width = self.time_canvas.winfo_width()
        canvas_height = self.time_canvas.winfo_height()
        self.time_canvas.create_text(
            canvas_width / 2, canvas_height / 2, text=current_time_str,
            font=("Arial", 65, "bold"), fill=CLOCK_COLOR, anchor="center"
        )
        self.root.after(1000, self.update_clock)

    def start_move(self, event): self.x, self.y = event.x, event.y
    def stop_move(self, event): self.x, self.y = None, None
    def do_move(self, event):
        self.root.geometry(f"+{self.root.winfo_x() + event.x - self.x}+{self.root.winfo_y() + event.y - self.y}")

    def add_symbol_popup(self):
        result = simpledialog.askstring("Add Symbols", "Enter new coin symbols (comma separated, e.g., ADAUSDT,XRPUSDT):")
        if result:
            current_symbols = set(load_symbols())
            new_symbols = {s.strip().upper() for s in result.split(",") if s.strip()}
            all_symbols = sorted(list(current_symbols.union(new_symbols)))
            
            with open(SYMBOLS_FILE, "w") as f:
                f.write(",".join(all_symbols))
                
            messagebox.showinfo("Restart Required", "New coins have been added. The application will now restart to apply changes.")
            python = sys.executable
            os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiCryptoTicker(root)
    root.mainloop()