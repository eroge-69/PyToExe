import upstox_client
import pandas as pd
import threading
import time
import tkinter as tk
from tkinter import messagebox
from upstox_client.rest import ApiException

# Global data storage
data = {}  # {instrument_key: {'ltp': float, 'cp': float}}
ik_to_symbol = {}  # {instrument_key: symbol}
credentials = {}  # To store API_KEY, API_SECRET, REDIRECT_URI

# List of F&O eligible stock symbols (expand as needed; ~30 common ones for simplicity)
FO_SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ICICIBANK', 'KOTAKBANK', 'BHARTIARTL',
    'ITC', 'LT', 'AXISBANK', 'MARUTI', 'ASIANPAINT', 'SUNPHARMA', 'WIPRO', 'NTPC', 'TITAN',
    'NESTLEIND', 'ULTRACEMCO', 'ONGC', 'SBIN', 'BAJFINANCE', 'TECHM', 'POWERGRID', 'COALINDIA',
    'TATAMOTORS', 'JSWSTEEL', 'HCLTECH', 'ADANIPORTS', 'INDUSINDBK'
]

def get_credentials_gui():
    """Create a GUI to collect API credentials."""
    def submit():
        credentials['API_KEY'] = entry_api_key.get().strip()
        credentials['API_SECRET'] = entry_api_secret.get().strip()
        credentials['REDIRECT_URI'] = entry_redirect_uri.get().strip()
        if not all([credentials['API_KEY'], credentials['API_SECRET'], credentials['REDIRECT_URI']]):
            messagebox.showerror("Error", "Please fill in all fields.")
        else:
            root.destroy()  # Close GUI on valid submission

    root = tk.Tk()
    root.title("Upstox API Credentials")
    root.geometry("400x200")

    tk.Label(root, text="API Key:").pack(pady=5)
    entry_api_key = tk.Entry(root, width=50)
    entry_api_key.pack(pady=5)

    tk.Label(root, text="API Secret:").pack(pady=5)
    entry_api_secret = tk.Entry(root, width=50, show="*")
    entry_api_secret.pack(pady=5)

    tk.Label(root, text="Redirect URI:").pack(pady=5)
    entry_redirect_uri = tk.Entry(root, width=50)
    entry_redirect_uri.pack(pady=5)

    tk.Button(root, text="Submit", command=submit).pack(pady=10)

    root.mainloop()

def get_access_token():
    """OAuth flow to get access token using GUI credentials."""
    try:
        login_manager = upstox_client.OAuthManager(
            client_id=credentials['API_KEY'],
            client_secret=credentials['API_SECRET'],
            redirect_uri=credentials['REDIRECT_URI']
        )
        login_url = login_manager.get_login_url()
        print(f"Visit this URL to login: {login_url}")
        full_url = input("After login and redirect, paste the full redirect URL here: ").strip()
        code = full_url.split('code=')[1].split('&')[0] if 'code=' in full_url else input("Enter the code from the URL: ").strip()
        access_token = login_manager.get_access_token(code)
        print("Access token obtained successfully.")
        return access_token
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def on_message(message):
    """Callback for WebSocket messages."""
    global data
    if message.get('type') == 'live_feed':
        feeds = message.get('feeds', {})
        for ik, feed in feeds.items():
            ltpc = feed.get('ltpc', {})
            if 'ltp' in ltpc and 'cp' in ltpc:
                data[ik] = {
                    'ltp': float(ltpc['ltp']),
                    'cp': float(ltpc['cp'])
                }

def print_top_gainers_losers():
    """Thread to print top gainers/losers every 60 seconds."""
    while True:
        time.sleep(60)
        if not data or len(ik_to_symbol) == 0:
            print("Waiting for data...")
            continue
        changes = []
        for ik, d in data.items():
            if ik in ik_to_symbol and d.get('ltp') and d.get('cp') and d['cp'] > 0:
                change_pct = (d['ltp'] - d['cp']) / d['cp'] * 100
                symbol = ik_to_symbol[ik]
                changes.append((symbol, change_pct, d['ltp']))
        if changes:
            gainers = sorted(changes, key=lambda x: x[1], reverse=True)[:5]
            losers = sorted(changes, key=lambda x: x[1])[:5]
            print("\n--- Top 5 Gainers (Pre-Open F&O Stocks) ---")
            for symbol, change, ltp in gainers:
                print(f"{symbol}: {change:.2f}% (LTP: {ltp})")
            print("\n--- Top 5 Losers (Pre-Open F&O Stocks) ---")
            for symbol, change, ltp in losers:
                print(f"{symbol}: {change:.2f}% (LTP: {ltp})")
            print(f"--- Updated at {time.strftime('%H:%M:%S')} (Based on {len(changes)} stocks) ---\n")
        else:
            print("No valid data yet. Ensure running during pre-open (9:00-9:15 AM IST).\n")

def main():
    global ik_to_symbol
    # Get credentials via GUI
    get_credentials_gui()
    if not credentials:
        print("No credentials provided. Exiting.")
        return

    # Get access token
    access_token = get_access_token()
    if not access_token:
        return

    # Setup configuration
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token

    # Download instruments CSV (public, no auth needed)
    try:
        url = 'https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz'
        df = pd.read_csv(url, compression='gzip')
        eq_df = df[(df['trading_symbol'].isin(FO_SYMBOLS)) & 
                   (df['instrument_type'] == 'EQ') & 
                   (df['exchange'] == 'NSE')]
        instrument_keys = list(eq_df['instrument_key'].values)
        ik_to_symbol = dict(zip(eq_df['instrument_key'], eq_df['trading_symbol']))
        print(f"Subscribed to {len(instrument_keys)} F&O stocks: {list(ik_to_symbol.values())}")
    except Exception as e:
        print(f"Error fetching instruments: {e}")
        return

    # Setup WebSocket streamer (V3 for full data)
    api_client = upstox_client.ApiClient(configuration)
    streamer = upstox_client.MarketDataStreamerV3(api_client, instrument_keys, "ltpc")  # 'ltpc' mode for LTP/CP

    # Attach callbacks
    streamer.on("message", on_message)

    # Start print thread
    print_thread = threading.Thread(target=print_top_gainers_losers, daemon=True)
    print_thread.start()

    print("Connected to Upstox WebSocket. Waiting for pre-open data...")
    try:
        streamer.connect()
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    main()