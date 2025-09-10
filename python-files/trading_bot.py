import ccxt
import time
import random  # For simulating direction (long/short)
import logging
import os
import json

# Setup logging
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting trading bot")

# Load API keys from config.json or environment variables
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    API_KEY = config.get('API_KEY', 'YOUR_API_KEY')
    API_SECRET = config.get('API_SECRET', 'YOUR_SECRET_KEY')
except FileNotFoundError:
    API_KEY = os.getenv('API_KEY', 'YOUR_API_KEY')
    API_SECRET = os.getenv('API_SECRET', 'YOUR_SECRET_KEY')

# User settings
EXCHANGE = 'binance'  # Or 'bybit', etc.
NUM_COINS = 100  # Number of coins
AMOUNT_PER_TRADE = 10  # Amount per trade in USDT (e.g., 10 USDT)
LEVERAGE = 10  # Leverage
NUM_GRIDS = 5  # Number of grid levels
GRID_SPACING_PERCENT = 1  # Spacing between grids in percent (e.g., 1%)
TP_PERCENT = 5  # Take Profit percentage
SL_PERCENT = 3  # Stop Loss percentage
SLEEP_INTERVAL = 60  # Check every 60 seconds

# Initialize exchange (for futures)
exchange = ccxt.binanceusdm({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {'defaultType': 'future'},
})

# Function to get top 100 trading pairs (based on volume)
def get_top_pairs(num=100):
    try:
        markets = exchange.fetch_markets()
        futures_markets = [m for m in markets if m['type'] == 'future' and m['quote'] == 'USDT']
        tickers = exchange.fetch_tickers([m['symbol'] for m in futures_markets])
        sorted_tickers = sorted(tickers.items(), key=lambda x: x[1].get('quoteVolume', 0), reverse=True)
        top_symbols = [symbol for symbol, ticker in sorted_tickers[:num]]
        logging.info(f"Fetched {len(top_symbols)} trading pairs")
        return top_symbols
    except Exception as e:
        logging.error(f"Error fetching top pairs: {e}")
        return []

# Function to set leverage
def set_leverage(symbol, leverage):
    try:
        exchange.set_leverage(leverage, symbol)
        logging.info(f"Leverage set to {leverage}x for {symbol}")
    except Exception as e:
        logging.error(f"Error setting leverage for {symbol}: {e}")

# Function to open grid position
def open_grid_position(symbol, direction, amount, num_grids, grid_spacing_percent, tp_percent, sl_percent):
    try:
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Decide direction: long (buy) or short (sell) – random here, can be customized
        is_long = random.choice([True, False]) if direction is None else (direction == 'long')
        
        side = 'buy' if is_long else 'sell'
        opposite_side = 'sell' if is_long else 'buy'
        
        logging.info(f"Opening {num_grids} grid {side} positions for {symbol} at price {current_price}")
        
        positions = []
        for i in range(num_grids):
            # Calculate price for each grid level
            price_offset = current_price * (grid_spacing_percent / 100) * (i + 1)
            entry_price = current_price - price_offset if is_long else current_price + price_offset
            
            # Place limit order
            order = exchange.create_limit_order(
                symbol,
                side,
                amount,
                entry_price,
                {'leverage': LEVERAGE}
            )
            positions.append(order)
            logging.info(f"Grid {i+1}: {side} order placed at {entry_price} for {symbol}")
        
        # Calculate average entry price
        avg_entry_price = sum([o['price'] for o in positions]) / num_grids if positions else current_price
        
        # Set TP and SL
        tp_price = avg_entry_price * (1 + tp_percent/100) if is_long else avg_entry_price * (1 - tp_percent/100)
        sl_price = avg_entry_price * (1 - sl_percent/100) if is_long else avg_entry_price * (1 + sl_percent/100)
        
        # Place TP and SL orders
        exchange.create_order(symbol, 'limit', opposite_side, amount * num_grids, tp_price, {'reduceOnly': True, 'triggerPrice': tp_price, 'type': 'takeProfit'})
        exchange.create_order(symbol, 'stop', opposite_side, amount * num_grids, sl_price, {'reduceOnly': True, 'triggerPrice': sl_price, 'type': 'stopLoss'})
        
        logging.info(f"TP set at {tp_price}, SL at {sl_price} for {symbol}")
        
    except Exception as e:
        logging.error(f"Error opening position for {symbol}: {e}")

# Main execution
try:
    top_symbols = get_top_pairs(NUM_COINS)
    for symbol in top_symbols:
        set_leverage(symbol, LEVERAGE)
        open_grid_position(symbol, direction=None, amount=AMOUNT_PER_TRADE, num_grids=NUM_GRIDS, 
                           grid_spacing_percent=GRID_SPACING_PERCENT, tp_percent=TP_PERCENT, sl_percent=SL_PERCENT)
        time.sleep(1)  # Avoid rate limit

    # Monitoring loop
    while True:
        logging.info("Monitoring positions...")
        time.sleep(SLEEP_INTERVAL)
except Exception as e:
    logging.error(f"Main loop error: {e}")