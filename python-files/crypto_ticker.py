import tkinter as tk
from tkinter import Canvas, Label, Frame
import asyncio
import websockets
import json
import threading
from queue import Queue
from collections import deque
import ssl
import time

# --- CONFIGURATION ---
# Add or remove symbols here. Use Binance Futures format (e.g., 'BTCUSDT')
SYMBOLS = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT') 
FUTURES_STREAM_URL = "wss://fstream.binance.com"

# --- LAYOUT & SPEED CONTROL (Adjust these values) ---
WINDOW_WIDTH = 1000  # Wider for horizontal layout
WINDOW_HEIGHT = 200  # Shorter
SECONDS_BETWEEN_UPDATES = 5.0 # Set to 1.0 for 1-sec updates, 0.5 for faster, etc.

# --- FONT SIZES (Adjust these numbers) ---
PRICE_FONT_SIZE = 25
SYMBOL_FONT_SIZE = 16

# --- VISUALS ---
MAX_PRICES_IN_CHART = 75
GUI_UPDATE_INTERVAL_MS = 100
BACKGROUND_COLOR = 'black'
TRANSPARENT_COLOR = '#000001'
FONT_COLOR = 'white'
PRICE_UP_COLOR = '#26a69a'
PRICE_DOWN_COLOR = '#ef5350'
CHART_LINE_COLOR = '#6c757d'
FONT_PRICE = ("Arial", PRICE_FONT_SIZE, "bold")
FONT_SYMBOL = ("Arial", SYMBOL_FONT_SIZE)

# --- WebSocket Data Fetching (No changes needed here) ---
def fetch_crypto_data(queue):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async def listen():
        streams = '/'.join([f"{s.lower()}@aggTrade" for s in SYMBOLS])
        uri = f"{FUTURES_STREAM_URL}/stream?streams={streams}"
        print(f"Connecting to: {uri}")
        while True:
            try:
                async with websockets.connect(uri, ssl=ssl_context) as websocket:
                    print("Connected to Binance Futures WebSocket.")
                    while True:
                        message = await websocket.recv()
                        payload = json.loads(message)
                        if 'stream' in payload and 'data' in payload:
                            symbol_from_stream = payload['stream'].split('@')[0].upper()
                            price = float(payload['data']['p'])
                            queue.put((symbol_from_stream, price))
            except Exception as e:
                print(f"WebSocket error: {type(e).__name__} - {e}. Reconnecting...")
                await asyncio.sleep(5)
    asyncio.run(listen())

class MultiCryptoTicker:
    def __init__(self, root):
        self.root = root
        self.labels_price = {}
        self.charts = {}
        self.prices_data = {}
        self.last_prices = {}
        # New: Dictionary to track the last update time for each symbol
        self.last_update_time = {}

        self.setup_window()

        # A main frame to hold all the coin sections horizontally
        main_frame = Frame(self.root, bg=BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        for symbol in SYMBOLS:
            self.create_coin_section(symbol, main_frame)

        self.data_queue = Queue()
        self.thread = threading.Thread(target=fetch_crypto_data, args=(self.data_queue,), daemon=True)
        self.thread.start()
        self.process_queue()

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

    def create_coin_section(self, symbol, parent_frame):
        # NEW: Place each section side-by-side in the parent frame
        section_frame = Frame(parent_frame, bg=BACKGROUND_COLOR)
        section_frame.pack(side='left', padx=20, expand=True, fill='x')
        
        display_symbol = symbol.replace('USDT', '/USDT')
        symbol_label = Label(section_frame, text=display_symbol, font=FONT_SYMBOL, bg=BACKGROUND_COLOR, fg='gray')
        symbol_label.pack()

        price_label = Label(section_frame, text="Loading...", font=FONT_PRICE, bg=BACKGROUND_COLOR, fg=FONT_COLOR)
        price_label.pack()
        self.labels_price[symbol] = price_label

        chart_canvas = Canvas(section_frame, width=WINDOW_WIDTH/len(SYMBOLS)-50, height=45, bg=BACKGROUND_COLOR, highlightthickness=0)
        chart_canvas.pack(pady=10)
        self.charts[symbol] = chart_canvas

        self.prices_data[symbol] = deque(maxlen=MAX_PRICES_IN_CHART)
        self.last_prices[symbol] = 0.0
        self.last_update_time[symbol] = 0.0 # Initialize update time

    def process_queue(self):
        try:
            while not self.data_queue.empty():
                symbol, new_price = self.data_queue.get_nowait()
                
                # NEW: Check if enough time has passed to update this symbol's display
                current_time = time.time()
                if current_time - self.last_update_time.get(symbol, 0) > SECONDS_BETWEEN_UPDATES:
                    self.update_display(symbol, new_price)
                    self.last_update_time[symbol] = current_time # Reset timer
        finally:
            self.root.after(GUI_UPDATE_INTERVAL_MS, self.process_queue)

    def update_display(self, symbol, price):
        if symbol not in SYMBOLS: return
        
        if price > self.last_prices.get(symbol, 0):
            self.labels_price[symbol].config(fg=PRICE_UP_COLOR)
        elif price < self.last_prices.get(symbol, 0):
            self.labels_price[symbol].config(fg=PRICE_DOWN_COLOR)
        
        self.last_prices[symbol] = price
        price_format = f"{price:,.2f}" if price >= 10 else f"{price:,.4f}"
        self.labels_price[symbol].config(text=price_format)

        self.prices_data[symbol].append(price)
        self.draw_chart(symbol)

    def draw_chart(self, symbol):
        canvas = self.charts[symbol]
        prices = self.prices_data[symbol]
        canvas.delete("all")
        if len(prices) < 2: return
        min_p, max_p = min(prices), max(prices)
        price_range = max_p - min_p if max_p > min_p else 1
        points = []
        canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <=1: return
        for i, price in enumerate(prices):
            x = (i / (MAX_PRICES_IN_CHART - 1)) * canvas_w
            y = canvas_h - ((price - min_p) / price_range) * canvas_h
            points.extend([x, y])
        if len(points) > 3:
            canvas.create_line(points, fill=CHART_LINE_COLOR, width=2, smooth=True) # Added smooth=True
            
    def start_move(self, event): self.x, self.y = event.x, event.y
    def stop_move(self, event): self.x, self.y = None, None
    def do_move(self, event):
        self.root.geometry(f"+{self.root.winfo_x() + event.x - self.x}+{self.root.winfo_y() + event.y - self.y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiCryptoTicker(root)
    root.mainloop()