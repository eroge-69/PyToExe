import websocket
import json
import pandas as pd
import numpy as np
import talib
import asyncio
import threading
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class DerivPatternAnalyzer:
    def __init__(self, app_id=1089):  # Deriv demo app ID
        self.app_id = app_id
        self.ws = None
        self.data = pd.DataFrame()
        self.patterns = {}
        self.is_connected = False
        self.active_symbols = [
            'R_10', 'R_25', 'R_50', 'R_75', 'R_100',  # Volatility indices
            '1HZ10V', '1HZ25V', '1HZ50V', '1HZ75V', '1HZ100V'  # Jump indices
        ]
        
    def connect(self):
        """Connect to Deriv WebSocket API"""
        self.ws = websocket.WebSocketApp(
            f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Run WebSocket in separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        data = json.loads(message)
        
        if 'tick' in data:
            self.process_tick(data['tick'])
        elif 'history' in data:
            self.process_history(data['history'])
        elif 'error' in data:
            print(f"Error: {data['error']}")
            
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        self.is_connected = False
        
    def on_open(self, ws):
        print("WebSocket connection established")
        self.is_connected = True
        
    def subscribe_ticks(self, symbol):
        """Subscribe to tick data for a symbol"""
        if self.is_connected:
            request = {
                "ticks": symbol,
                "subscribe": 1
            }
            self.ws.send(json.dumps(request))
            
    def get_historical_data(self, symbol, count=1000):
        """Get historical data for backtesting"""
        request = {
            "ticks_history": symbol,
            "count": count,
            "end": "latest",
            "style": "ticks"
        }
        self.ws.send(json.dumps(request))
        
    def process_tick(self, tick_data):
        """Process incoming tick data"""
        new_data = pd.DataFrame([{
            'timestamp': datetime.now(),
            'epoch': tick_data['epoch'],
            'quote': float(tick_data['quote']),
            'symbol': tick_data.get('symbol', 'unknown')
        }])
        
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        
        # Keep only last 10,000 ticks to manage memory
        if len(self.data) > 10000:
            self.data = self.data.tail(10000)
            
        # Analyze patterns in real-time
        self.analyze_patterns()
        
    def process_history(self, history_data):
        """Process historical data"""
        ticks = history_data.get('prices', [])
        historical_df = pd.DataFrame([{
            'timestamp': datetime.fromtimestamp(tick['epoch']),
            'epoch': tick['epoch'],
            'quote': float(tick['quote']),
            'symbol': history_data.get('symbol', 'unknown')
        } for tick in ticks])
        
        self.data = pd.concat([self.data, historical_df], ignore_index=True)
        print(f"Loaded {len(historical_df)} historical ticks")
        
    def calculate_technical_indicators(self, df):
        """Calculate various technical indicators"""
        if len(df) < 50:  # Need sufficient data
            return df
            
        prices = df['quote'].values
        
        # Moving averages
        df['sma_20'] = talib.SMA(prices, timeperiod=20)
        df['sma_50'] = talib.SMA(prices, timeperiod=50)
        df['ema_12'] = talib.EMA(prices, timeperiod=12)
        df['ema_26'] = talib.EMA(prices, timeperiod=26)
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        
        # RSI
        df['rsi'] = talib.RSI(prices, timeperiod=14)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(prices)
        
        # Stochastic
        df['slowk'], df['slowd'] = talib.STOCH(
            df['high'].values if 'high' in df.columns else prices,
            df['low'].values if 'low' in df.columns else prices,
            prices,
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        
        # Volatility
        df['volatility'] = talib.STDDEV(prices, timeperiod=20)
        
        return df
        
    def detect_patterns(self, df):
        """Detect specific trading patterns"""
        patterns = {}
        prices = df['quote'].values
        
        if len(prices) < 100:
            return patterns
            
        # Mean reversion detection
        z_score = (prices[-1] - np.mean(prices)) / np.std(prices)
        patterns['mean_reversion'] = abs(z_score) > 2.0
        patterns['z_score'] = z_score
        
        # Support/Resistance levels
        patterns['support'], patterns['resistance'] = self.find_support_resistance(prices)
        
        # Trend detection
        patterns['trend'] = self.detect_trend(prices)
        
        # Volatility regime
        patterns['volatility_regime'] = self.detect_volatility_regime(prices)
        
        # Overbought/Oversold
        if 'rsi' in df.columns:
            patterns['overbought'] = df['rsi'].iloc[-1] > 70
            patterns['oversold'] = df['rsi'].iloc[-1] < 30
            
        return patterns
        
    def find_support_resistance(self, prices, window=50):
        """Find support and resistance levels"""
        if len(prices) < window:
            return None, None
            
        recent_prices = prices[-window:]
        
        # Use local minima and maxima
        support = np.min(recent_prices)
        resistance = np.max(recent_prices)
        
        return support, resistance
        
    def detect_trend(self, prices, window=30):
        """Detect current trend"""
        if len(prices) < window:
            return "neutral"
            
        recent = prices[-window:]
        x = np.arange(len(recent))
        slope, _, _, _, _ = stats.linregress(x, recent)
        
        if slope > 0.001:
            return "uptrend"
        elif slope < -0.001:
            return "downtrend"
        else:
            return "neutral"
            
    def detect_volatility_regime(self, prices, window=50):
        """Detect high/low volatility regime"""
        if len(prices) < window:
            return "normal"
            
        recent_volatility = np.std(prices[-window:])
        historical_volatility = np.std(prices[:-window]) if len(prices) > window else recent_volatility
        
        if recent_volatility > historical_volatility * 1.5:
            return "high_volatility"
        elif recent_volatility < historical_volatility * 0.5:
            return "low_volatility"
        else:
            return "normal"
            
    def analyze_patterns(self):
        """Main pattern analysis function"""
        if len(self.data) < 100:
            return
            
        # Calculate technical indicators
        df_with_indicators = self.calculate_technical_indicators(self.data.copy())
        
        # Detect patterns
        current_patterns = self.detect_patterns(df_with_indicators)
        
        # Store patterns for reporting
        self.patterns = current_patterns
        
        # Generate signals
        signals = self.generate_signals(df_with_indicators, current_patterns)
        
        if signals:
            self.alert_signals(signals)
            
    def generate_signals(self, df, patterns):
        """Generate trading signals based on detected patterns"""
        signals = []
        
        if len(df) < 2:
            return signals
            
        current_price = df['quote'].iloc[-1]
        previous_price = df['quote'].iloc[-2]
        
        # Mean reversion signal
        if patterns.get('mean_reversion', False):
            z_score = patterns.get('z_score', 0)
            if z_score > 2:
                signals.append({
                    'type': 'SELL',
                    'reason': f'Mean reversion - price {z_score:.2f} std above mean',
                    'confidence': min(abs(z_score) / 4, 0.9),
                    'timestamp': datetime.now()
                })
            elif z_score < -2:
                signals.append({
                    'type': 'BUY',
                    'reason': f'Mean reversion - price {abs(z_score):.2f} std below mean',
                    'confidence': min(abs(z_score) / 4, 0.9),
                    'timestamp': datetime.now()
                })
                
        # RSI signals
        if 'rsi' in df.columns:
            rsi = df['rsi'].iloc[-1]
            if rsi > 70:
                signals.append({
                    'type': 'SELL',
                    'reason': f'RSI overbought: {rsi:.2f}',
                    'confidence': 0.7,
                    'timestamp': datetime.now()
                })
            elif rsi < 30:
                signals.append({
                    'type': 'BUY',
                    'reason': f'RSI oversold: {rsi:.2f}',
                    'confidence': 0.7,
                    'timestamp': datetime.now()
                })
                
        # Trend following
        if patterns.get('trend') == 'uptrend' and current_price > previous_price:
            signals.append({
                'type': 'BUY',
                'reason': 'Uptrend continuation',
                'confidence': 0.6,
                'timestamp': datetime.now()
            })
        elif patterns.get('trend') == 'downtrend' and current_price < previous_price:
            signals.append({
                'type': 'SELL',
                'reason': 'Downtrend continuation',
                'confidence': 0.6,
                'timestamp': datetime.now()
            })
            
        return signals
        
    def alert_signals(self, signals):
        """Alert when trading signals are generated"""
        for signal in signals:
            if signal['confidence'] > 0.6:  # Only alert on high-confidence signals
                print(f"🚨 TRADING SIGNAL 🚨")
                print(f"Type: {signal['type']}")
                print(f"Reason: {signal['reason']}")
                print(f"Confidence: {signal['confidence']:.2f}")
                print(f"Time: {signal['timestamp']}")
                print("-" * 50)
                
    def generate_report(self):
        """Generate comprehensive pattern analysis report"""
        if len(self.data) < 100:
            print("Insufficient data for report")
            return
            
        print("\n" + "="*60)
        print("DERIV SYNTHETIC MARKETS PATTERN ANALYSIS REPORT")
        print("="*60)
        
        # Basic statistics
        print(f"\n📊 BASIC STATISTICS:")
        print(f"Total ticks analyzed: {len(self.data)}")
        print(f"Current price: {self.data['quote'].iloc[-1]:.4f}")
        print(f"Mean price: {self.data['quote'].mean():.4f}")
        print(f"Standard deviation: {self.data['quote'].std():.4f}")
        print(f"Price range: {self.data['quote'].min():.4f} - {self.data['quote'].max():.4f}")
        
        # Current patterns
        print(f"\n🎯 DETECTED PATTERNS:")
        for pattern, value in self.patterns.items():
            print(f"{pattern}: {value}")
            
        # Recommendations
        print(f"\n💡 TRADING INSIGHTS:")
        if self.patterns.get('mean_reversion'):
            z_score = self.patterns.get('z_score', 0)
            action = "SELL" if z_score > 0 else "BUY"
            print(f"Strong mean reversion opportunity - Consider {action}")
            
        if self.patterns.get('volatility_regime') == 'high_volatility':
            print("High volatility regime - Consider reducing position sizes")
            
        if self.patterns.get('trend') != 'neutral':
            print(f"Market in {self.patterns['trend']} - Trend-following strategies may work")
            
    def plot_analysis(self):
        """Create visualization of the analysis"""
        if len(self.data) < 100:
            print("Need more data for visualization")
            return
            
        plt.figure(figsize=(15, 10))
        
        # Price chart with moving averages
        plt.subplot(3, 1, 1)
        plt.plot(self.data['timestamp'], self.data['quote'], label='Price', linewidth=1)
        if 'sma_20' in self.data.columns:
            plt.plot(self.data['timestamp'], self.data['sma_20'], label='SMA 20', alpha=0.7)
        if 'sma_50' in self.data.columns:
            plt.plot(self.data['timestamp'], self.data['sma_50'], label='SMA 50', alpha=0.7)
        plt.title('Price Chart with Moving Averages')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # RSI
        plt.subplot(3, 1, 2)
        if 'rsi' in self.data.columns:
            plt.plot(self.data['timestamp'], self.data['rsi'], label='RSI', color='orange')
            plt.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
            plt.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
            plt.title('RSI Indicator')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
        # Volatility
        plt.subplot(3, 1, 3)
        if 'volatility' in self.data.columns:
            plt.plot(self.data['timestamp'], self.data['volatility'], label='Volatility', color='red')
            plt.title('Price Volatility')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
        plt.tight_layout()
        plt.show()

# Usage example
def main():
    # Initialize analyzer
    analyzer = DerivPatternAnalyzer()
    
    # Connect to Deriv
    print("Connecting to Deriv API...")
    analyzer.connect()
    
    # Wait for connection
    time.sleep(3)
    
    # Subscribe to a symbol (Volatility 75 Index)
    symbol = "R_75"
    print(f"Subscribing to {symbol}...")
    analyzer.subscribe_ticks(symbol)
    
    # Also get historical data
    analyzer.get_historical_data(symbol, count=1000)
    
    try:
        # Run analysis for 5 minutes
        print("Collecting data and analyzing patterns...")
        start_time = time.time()
        
        while time.time() - start_time < 300:  # Run for 5 minutes
            if len(analyzer.data) > 0:
                # Generate report every 30 seconds
                if int(time.time() - start_time) % 30 == 0:
                    analyzer.generate_report()
                    
            time.sleep(1)
            
        # Final analysis and plot
        print("\nFinal Analysis:")
        analyzer.generate_report()
        analyzer.plot_analysis()
        
    except KeyboardInterrupt:
        print("\nStopping analysis...")
        analyzer.generate_report()

if __name__ == "__main__":
    main()