import ccxt
import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
import pandas as pd
import numpy as np
import talib
from scipy.signal import argrelextrema
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import os
import warnings
from tqdm import tqdm
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ================= GLOBAL CONFIGURATION =================
# Risk and multiprocessing settings
RISK_FREE_RATE = 0.02
MAX_WORKERS = os.cpu_count() // 2

# Pattern detection parameters
PATTERN_SENSITIVITY = 0.01  # Stricter sensitivity
PATTERN_LOOKBACK = 10
ZIGZAG_LENGTH = 3
ZIGZAG_DEPTH = 5
ZIGZAG_NUM_PIVOTS = 6

# Weights for multi-timeframe signals
WEIGHT_5M = 0.2
WEIGHT_15M = 0.5  # Primary timeframe
WEIGHT_1H = 0.3

# Increased signal threshold for high accuracy
SIGNAL_THRESHOLD = 2.0

# ================= DATA FUNCTIONS =================
def get_crypto_assets():
    """Return a list of cryptocurrencies to analyze on Binance."""
    return ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BNB/USDT', 'ADA/USDT']

def get_fx_pairs():
    """Return a list of major FX pairs to analyze on Oanda."""
    return ['EUR_USD', 'USD_JPY', 'GBP_USD', 'AUD_USD', 'USD_CHF']

def fetch_binance_data(symbol, timeframe, limit=100):
    """Fetch OHLCV data from Binance."""
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching Binance data for {symbol}: {e}")
        return None

def fetch_oanda_data(instrument, granularity, count=100):
    """Fetch candle data from Oanda."""
    try:
        api = API(access_token='your_oanda_api_key', environment="practice")  # Replace with your API key
        params = {"count": count, "granularity": granularity}
        r = InstrumentsCandles(instrument=instrument, params=params)
        api.request(r)
        candles = r.response['candles']
        df = pd.DataFrame([{
            'timestamp': candle['time'],
            'open': float(candle['mid']['o']),
            'high': float(candle['mid']['h']),
            'low': float(candle['mid']['l']),
            'close': float(candle['mid']['c']),
            'volume': candle['volume']
        } for candle in candles])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching Oanda data for {instrument}: {e}")
        return None

def fetch_data(asset, timeframes=['5m', '15m', '1h']):
    """Fetch data for an asset across multiple timeframes."""
    data = {}
    for tf in timeframes:
        if 'USDT' in asset:
            df = fetch_binance_data(asset, tf)
        else:
            df = fetch_oanda_data(asset.replace('/', '_'), tf)
        if df is not None:
            data[tf] = df
    return data if data else None

def heikin_ashi(df):
    """Convert OHLC data to Heikin-Ashi candles."""
    ha_df = df.copy()
    ha_df['HA_Close'] = (ha_df['open'] + ha_df['high'] + ha_df['low'] + ha_df['close']) / 4
    
    # Initialize HA_Open
    ha_open = [(ha_df['open'].iloc[0] + ha_df['close'].iloc[0]) / 2]
    
    # Calculate subsequent HA_Open values
    for i in range(1, len(ha_df)):
        ha_open.append((ha_open[i-1] + ha_df['HA_Close'].iloc[i-1]) / 2)
    
    ha_df['HA_Open'] = ha_open
    ha_df['HA_High'] = ha_df[['high', 'HA_Open', 'HA_Close']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['low', 'HA_Open', 'HA_Close']].min(axis=1)
    
    return ha_df

# ================= TECHNICAL INDICATORS =================
def calculate_indicators(df):
    """Calculate technical indicators using Heikin-Ashi data."""
    df = df.copy()
    df['ATR'] = talib.ATR(df['HA_High'], df['HA_Low'], df['HA_Close'], timeperiod=7)
    df['RSI'] = talib.RSI(df['HA_Close'], timeperiod=7)
    df['ADX'] = talib.ADX(df['HA_High'], df['HA_Low'], df['HA_Close'], timeperiod=7)
    df['SMA_50'] = talib.SMA(df['HA_Close'], timeperiod=50)
    return df

# ================= PATTERN DETECTION =================
def detect_zigzag_pivots(df):
    """Detect pivot points using a zigzag algorithm."""
    prices = df['HA_Close'].values
    highs = argrelextrema(prices, np.greater, order=ZIGZAG_LENGTH)[0]
    lows = argrelextrema(prices, np.less, order=ZIGZAG_LENGTH)[0]
    pivot_indices = np.concatenate([highs, lows])
    pivot_indices.sort()
    
    pivots = []
    for i in pivot_indices:
        if len(pivots) < 2:
            pivots.append((i, prices[i], 'high' if i in highs else 'low'))
        else:
            last_price = pivots[-1][1]
            change = abs(prices[i] - last_price) / last_price
            if change > PATTERN_SENSITIVITY:
                pivots.append((i, prices[i], 'high' if i in highs else 'low'))
    
    return pivots[-ZIGZAG_NUM_PIVOTS:]

def detect_geometric_patterns(df, pivots):
    """Detect geometric patterns with stricter conditions."""
    patterns = {
        'rising_wedge': False,
        'falling_wedge': False,
        'ascending_triangle': False,
        'descending_triangle': False,
        'channel': False
    }
    
    if len(pivots) < 5:
        return patterns
    
    prices = [p[1] for p in pivots[-5:]]
    types = [p[2] for p in pivots[-5:]]
    
    # Rising Wedge (bearish)
    if (types == ['low', 'high', 'low', 'high', 'low'] and 
        prices[0] < prices[2] < prices[4] and 
        prices[1] < prices[3] and 
        (prices[3] - prices[1]) < (prices[1] - prices[0])):
        patterns['rising_wedge'] = True
    
    # Falling Wedge (bullish)
    if (types == ['high', 'low', 'high', 'low', 'high'] and 
        prices[0] > prices[2] > prices[4] and 
        prices[1] > prices[3] and 
        (prices[1] - prices[3]) < (prices[0] - prices[1])):
        patterns['falling_wedge'] = True
    
    # Ascending Triangle (bullish)
    if (types == ['low', 'high', 'low', 'high', 'low'] and 
        abs(prices[1] - prices[3]) < (prices[1] * 0.005) and  # Allowing small variance
        prices[0] < prices[2] < prices[4]):
        patterns['ascending_triangle'] = True
    
    return patterns

def detect_elliott_waves(pivots):
    """Detect simplified Elliott Wave patterns."""
    waves = {'impulse': False}
    if len(pivots) >= 5:
        types = [p[2] for p in pivots[-5:]]
        if types == ['low', 'high', 'low', 'high', 'low']:
            waves['impulse'] = True
    return waves

def detect_smc_confluence(df):
    """Detect SMC confluence zones with trend filter."""
    confluence = {'bullish': False, 'bearish': False}
    
    # Calculate order blocks
    high_ob = df['HA_High'].rolling(window=5).max().shift(1)
    low_ob = df['HA_Low'].rolling(window=5).min().shift(1)
    
    # Check confluence with trend
    if (df['HA_Close'].iloc[-1] > high_ob.iloc[-1] and 
        df['HA_Close'].iloc[-1] > df['SMA_50'].iloc[-1]):
        confluence['bullish'] = True
    elif (df['HA_Close'].iloc[-1] < low_ob.iloc[-1] and 
          df['HA_Close'].iloc[-1] < df['SMA_50'].iloc[-1]):
        confluence['bearish'] = True
    
    return confluence

# ================= SIGNAL GENERATION =================
def generate_signals(df_5m, df_15m, df_1h):
    """Generate high-accuracy signals with multi-timeframe alignment."""
    # Process data for each timeframe
    processed_data = {}
    for tf, df in zip(['5m', '15m', '1h'], [df_5m, df_15m, df_1h]):
        if df is None:
            return 'Hold', None, None, []
        
        ha_df = heikin_ashi(df)
        processed_df = calculate_indicators(ha_df)
        processed_data[tf] = processed_df
    
    # Analyze patterns and confluence
    scores = {}
    for tf, df in processed_data.items():
        pivots = detect_zigzag_pivots(df)
        patterns = detect_geometric_patterns(df, pivots)
        waves = detect_elliott_waves(pivots)
        confluence = detect_smc_confluence(df)
        
        score = 0
        if patterns['rising_wedge'] or patterns['descending_triangle']:
            score -= 1.5
        if patterns['falling_wedge'] or patterns['ascending_triangle'] or patterns['channel']:
            score += 1.5
        if waves['impulse']:
            score += 0.7
        if confluence['bullish']:
            score += 0.7
        if confluence['bearish']:
            score -= 0.7
        if df['RSI'].iloc[-1] > 70:
            score -= 0.5
        elif df['RSI'].iloc[-1] < 30:
            score += 0.5
        if df['ADX'].iloc[-1] > 25:
            score *= 1.3
        
        scores[tf] = score
    
    # Combine scores
    total_score = (scores['5m'] * WEIGHT_5M + 
                   scores['15m'] * WEIGHT_15M + 
                   scores['1h'] * WEIGHT_1H)
    
    # Generate signal with strict conditions
    signal = 'Hold'
    entry = stop_loss = None
    targets = []
    
    if (scores['5m'] > 0 and scores['15m'] > 0 and scores['1h'] > 0 and 
        total_score >= SIGNAL_THRESHOLD):
        signal = 'Buy'
        entry = processed_data['15m']['HA_Close'].iloc[-1]
        atr = processed_data['15m']['ATR'].iloc[-1]
        stop_loss = processed_data['15m']['HA_Low'].rolling(5).min().iloc[-1] - 0.5 * atr
        targets = [entry + 1.5 * atr, entry + 3 * atr]
    elif (scores['5m'] < 0 and scores['15m'] < 0 and scores['1h'] < 0 and 
          total_score <= -SIGNAL_THRESHOLD):
        signal = 'Sell'
        entry = processed_data['15m']['HA_Close'].iloc[-1]
        atr = processed_data['15m']['ATR'].iloc[-1]
        stop_loss = processed_data['15m']['HA_High'].rolling(5).max().iloc[-1] + 0.5 * atr
        targets = [entry - 1.5 * atr, entry - 3 * atr]
    
    return signal, entry, stop_loss, targets

# ================= MAIN EXECUTION =================
def analyze_asset(asset):
    """Analyze a single asset."""
    try:
        data = fetch_data(asset)
        if not data or len(data) < 3:  # Need all 3 timeframes
            return None
            
        signal, entry, stop_loss, targets = generate_signals(
            data.get('5m'), 
            data.get('15m'), 
            data.get('1h')
        )
        
        return {
            'asset': asset,
            'signal': signal,
            'entry': entry,
            'stop_loss': stop_loss,
            'targets': targets
        }
    except Exception as e:
        print(f"Error analyzing {asset}: {e}")
        return None

def main():
    """Execute the trading bot."""
    crypto_assets = get_crypto_assets()
    fx_assets = get_fx_pairs()
    all_assets = crypto_assets + fx_assets

    results = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(analyze_asset, asset): asset for asset in all_assets}
        for future in tqdm(as_completed(futures), total=len(all_assets), desc="Analyzing Assets"):
            result = future.result()
            if result:
                results.append(result)

    # Display results
    print("\n=== Trading Signals ===")
    for res in results:
        print(f"\nAsset: {res['asset']}")
        print(f"Signal: {res['signal']}")
        if res['signal'] != 'Hold':
            print(f"Entry: {res['entry']:.5f}")
            print(f"Stop Loss: {res['stop_loss']:.5f}")
            print(f"Targets: {[f'{t:.5f}' for t in res['targets']]}")

if __name__ == "__main__":
    main()