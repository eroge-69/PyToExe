import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class GoldCFDTradingBot:
    def __init__(self):
        self.symbol = "GC=F"  # Gold futures
        self.timeframes = ['1d', '4h', '1h', '30m', '15m', '5m']
        self.timeframe_weights = {
            '1d': 0.25,
            '4h': 0.20,
            '1h': 0.20,
            '30m': 0.15,
            '15m': 0.10,
            '5m': 0.10
        }

    def get_data(self, period="30d", interval="1h"):
        """Fetch gold price data"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period=period, interval=interval)
            if len(data) == 0:
                raise Exception("No data received")
            return data
        except:
            print("Error fetching GC=F data. Trying alternative symbols...")
            # Try alternative symbols
            alternatives = ["XAUUSD=X", "GLD", "IAU"]
            for alt in alternatives:
                try:
                    ticker = yf.Ticker(alt)
                    data = ticker.history(period=period, interval=interval)
                    if len(data) > 0:
                        print(f"Using {alt} data")
                        return data
                except:
                    continue
            
            # If all fail, create dummy data for demonstration
            print("Using simulated data for demonstration")
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                                end=datetime.now(), freq='1H')
            np.random.seed(42)
            base_price = 2000
            prices = base_price + np.cumsum(np.random.randn(len(dates)) * 2)
            
            data = pd.DataFrame({
                'Open': prices + np.random.randn(len(dates)) * 0.5,
                'High': prices + np.abs(np.random.randn(len(dates)) * 2),
                'Low': prices - np.abs(np.random.randn(len(dates)) * 2),
                'Close': prices,
                'Volume': np.random.randint(1000, 10000, len(dates))
            }, index=dates)
            
            return data

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI without TA-Lib"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD without TA-Lib"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        if len(histogram) < 2:
            return 'neutral'
        return 'bullish' if histogram.iloc[-1] > histogram.iloc[-2] else 'bearish'

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands without TA-Lib"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = prices.iloc[-1]
        upper = upper_band.iloc[-1]
        lower = lower_band.iloc[-1]
        
        if current_price > upper:
            return 'upper'
        elif current_price < lower:
            return 'lower'
        else:
            return 'middle'

    def calculate_atr(self, data, period=14):
        """Calculate Average True Range without TA-Lib"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).mean()
        
        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else data['Close'].iloc[-1] * 0.02

    def identify_fvg(self, data):
        """Identify Fair Value Gaps"""
        fvgs = []
        for i in range(2, len(data)):
            # Bullish FVG: Previous candle low > Current candle high
            if data['Low'].iloc[i-2] > data['High'].iloc[i]:
                fvgs.append({
                    'type': 'bullish_fvg',
                    'top': data['Low'].iloc[i-2],
                    'bottom': data['High'].iloc[i],
                    'index': i,
                    'strength': (data['Low'].iloc[i-2] - data['High'].iloc[i]) / data['Close'].iloc[i]
                })
            
            # Bearish FVG: Previous candle high < Current candle low
            elif data['High'].iloc[i-2] < data['Low'].iloc[i]:
                fvgs.append({
                    'type': 'bearish_fvg',
                    'top': data['Low'].iloc[i],
                    'bottom': data['High'].iloc[i-2],
                    'index': i,
                    'strength': (data['Low'].iloc[i] - data['High'].iloc[i-2]) / data['Close'].iloc[i]
                })
        
        return fvgs[-5:] if fvgs else []  # Return last 5 FVGs

    def identify_liquidity_sweeps(self, data):
        """Identify liquidity sweeps (stop hunts)"""
        sweeps = []
        lookback = min(20, len(data) - 1)
        
        for i in range(lookback, len(data)):
            recent_data = data.iloc[i-lookback:i]
            recent_high = recent_data['High'].max()
            recent_low = recent_data['Low'].min()
            current_candle = data.iloc[i]
            
            # Buy side liquidity sweep (break high then close lower)
            if (current_candle['High'] > recent_high and 
                current_candle['Close'] < current_candle['Open']):
                sweeps.append({
                    'type': 'buy_side_sweep',
                    'price': current_candle['High'],
                    'index': i,
                    'strength': (current_candle['High'] - recent_high) / current_candle['Close']
                })
            
            # Sell side liquidity sweep (break low then close higher)
            if (current_candle['Low'] < recent_low and 
                current_candle['Close'] > current_candle['Open']):
                sweeps.append({
                    'type': 'sell_side_sweep',
                    'price': current_candle['Low'],
                    'index': i,
                    'strength': (recent_low - current_candle['Low']) / current_candle['Close']
                })
        
        return sweeps[-3:] if sweeps else []

    def identify_market_structure(self, data):
        """Identify market structure shifts and breaks of structure"""
        structure = {'trend': 'sideways', 'bos': False, 'shift': False, 'strength': 0}
        
        if len(data) < 20:
            return structure
        
        # Calculate swing highs and lows using a simple method
        window = min(10, len(data) // 4)
        swing_highs = []
        swing_lows = []
        
        for i in range(window, len(data) - window):
            # Check if current point is a swing high
            is_swing_high = True
            is_swing_low = True
            
            for j in range(i - window, i + window + 1):
                if j != i:
                    if data['High'].iloc[j] >= data['High'].iloc[i]:
                        is_swing_high = False
                    if data['Low'].iloc[j] <= data['Low'].iloc[i]:
                        is_swing_low = False
            
            if is_swing_high:
                swing_highs.append((i, data['High'].iloc[i]))
            if is_swing_low:
                swing_lows.append((i, data['Low'].iloc[i]))
        
        # Analyze trend based on recent swing points
        if len(swing_highs) >= 3 and len(swing_lows) >= 3:
            recent_highs = [price for _, price in swing_highs[-3:]]
            recent_lows = [price for _, price in swing_lows[-3:]]
            
            # Check for uptrend (higher highs and higher lows)
            if (recent_highs[-1] > recent_highs[-2] > recent_highs[-3] and 
                recent_lows[-1] > recent_lows[-2]):
                structure['trend'] = 'uptrend'
                structure['strength'] = (recent_highs[-1] - recent_highs[-3]) / recent_highs[-3]
            
            # Check for downtrend (lower highs and lower lows)
            elif (recent_highs[-1] < recent_highs[-2] < recent_highs[-3] and 
                  recent_lows[-1] < recent_lows[-2]):
                structure['trend'] = 'downtrend'
                structure['strength'] = (recent_highs[-3] - recent_highs[-1]) / recent_highs[-3]
            
            # Check for break of structure
            current_price = data['Close'].iloc[-1]
            if structure['trend'] == 'uptrend' and current_price < recent_lows[-2]:
                structure['bos'] = True
                structure['shift'] = True
            elif structure['trend'] == 'downtrend' and current_price > recent_highs[-2]:
                structure['bos'] = True
                structure['shift'] = True
        
        return structure

    def identify_ote_zone(self, data):
        """Identify Optimal Trade Entry (61.8-78.6% retracement)"""
        lookback = min(50, len(data))
        recent_data = data.tail(lookback)
        recent_high = recent_data['High'].max()
        recent_low = recent_data['Low'].min()
        range_size = recent_high - recent_low
        
        ote_high = recent_low + (range_size * 0.786)  # 78.6% retracement
        ote_low = recent_low + (range_size * 0.618)   # 61.8% retracement
        
        current_price = data['Close'].iloc[-1]
        in_ote = ote_low <= current_price <= ote_high
        
        return {
            'ote_high': ote_high,
            'ote_low': ote_low,
            'in_ote': in_ote,
            'current_price': current_price,
            'retracement_level': (current_price - recent_low) / range_size if range_size > 0 else 0
        }

    def identify_imbalances(self, data):
        """Identify Imbalances (large momentum candles)"""
        imbalances = []
        
        # Calculate average candle body size
        body_sizes = abs(data['Close'] - data['Open'])
        avg_body = body_sizes.rolling(20).mean()
        
        for i in range(20, len(data)):
            current_body = body_sizes.iloc[i]
            avg_body_current = avg_body.iloc[i]
            
            # Large imbalance candle (body > 2x average)
            if current_body > avg_body_current * 2:
                imb_type = 'bullish_imb' if data['Close'].iloc[i] > data['Open'].iloc[i] else 'bearish_imb'
                imbalances.append({
                    'type': imb_type,
                    'strength': current_body / avg_body_current,
                    'price': data['Close'].iloc[i],
                    'index': i,
                    'body_size': current_body
                })
        
        return imbalances[-3:] if imbalances else []

    def identify_ssl_bsl(self, data):
        """Identify Sell Side Liquidity and Buy Side Liquidity"""
        ssl_levels = []  # Support levels (below price)
        bsl_levels = []  # Resistance levels (above price)
        
        lookback = min(20, len(data) - 1)
        
        for i in range(lookback, len(data)):
            window_data = data.iloc[i-lookback:i]
            local_high = window_data['High'].max()
            local_low = window_data['Low'].min()
            current_high = data['High'].iloc[i]
            current_low = data['Low'].iloc[i]
            
            # Identify significant levels
            if current_high >= local_high:
                bsl_levels.append({
                    'price': current_high,
                    'strength': (current_high - window_data['High'].mean()) / window_data['High'].std() if window_data['High'].std() > 0 else 0,
                    'index': i
                })
            
            if current_low <= local_low:
                ssl_levels.append({
                    'price': current_low,
                    'strength': (window_data['Low'].mean() - current_low) / window_data['Low'].std() if window_data['Low'].std() > 0 else 0,
                    'index': i
                })
        
        return {
            'ssl_levels': ssl_levels[-3:] if ssl_levels else [],
            'bsl_levels': bsl_levels[-3:] if bsl_levels else []
        }

    def calculate_technical_indicators(self, data):
        """Calculate various technical indicators"""
        indicators = {}
        
        try:
            # RSI
            indicators['rsi'] = self.calculate_rsi(data['Close'])
            
            # MACD
            indicators['macd_signal'] = self.calculate_macd(data['Close'])
            
            # Moving Averages
            indicators['sma_20'] = data['Close'].rolling(20).mean().iloc[-1]
            indicators['sma_50'] = data['Close'].rolling(50).mean().iloc[-1] if len(data) > 50 else data['Close'].iloc[-1]
            indicators['ma_trend'] = 'bullish' if indicators['sma_20'] > indicators['sma_50'] else 'bearish'
            
            # Bollinger Bands
            indicators['bb_position'] = self.calculate_bollinger_bands(data['Close'])
            
            # Volume analysis
            if 'Volume' in data.columns:
                avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
                current_volume = data['Volume'].iloc[-1]
                indicators['volume_strength'] = current_volume / avg_volume if avg_volume > 0 else 1
            else:
                indicators['volume_strength'] = 1
            
            # Price momentum
            price_change = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / data['Close'].iloc[-5]
            indicators['momentum'] = 'bullish' if price_change > 0.01 else 'bearish' if price_change < -0.01 else 'neutral'
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            # Fallback values
            indicators = {
                'rsi': 50,
                'macd_signal': 'neutral',
                'sma_20': data['Close'].iloc[-1],
                'sma_50': data['Close'].iloc[-1],
                'ma_trend': 'neutral',
                'bb_position': 'middle',
                'volume_strength': 1,
                'momentum': 'neutral'
            }
        
        return indicators

    def analyze_timeframe(self, interval):
        """Analyze a specific timeframe"""
        try:
            # Adjust period based on interval
            period_map = {
                '1d': '90d',
                '4h': '60d',
                '1h': '30d',
                '30m': '15d',
                '15m': '7d',
                '5m': '3d'
            }
            
            period = period_map.get(interval, '30d')
            data = self.get_data(period=period, interval=interval)
            
            if len(data) < 20:
                print(f"Insufficient data for {interval}")
                return None
            
            analysis = {
                'timeframe': interval,
                'fvgs': self.identify_fvg(data),
                'liquidity_sweeps': self.identify_liquidity_sweeps(data),
                'market_structure': self.identify_market_structure(data),
                'ote_zone': self.identify_ote_zone(data),
                'imbalances': self.identify_imbalances(data),
                'ssl_bsl': self.identify_ssl_bsl(data),
                'technical_indicators': self.calculate_technical_indicators(data),
                'current_price': data['Close'].iloc[-1],
                'atr': self.calculate_atr(data)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing {interval}: {e}")
            return None

    def generate_trade_signal(self, analysis):
        """Generate trade signal based on analysis"""
        if not analysis:
            return None
        
        buy_score = 0
        sell_score = 0
        confidence_factors = []
        
        # FVG Analysis (15% weight)
        fvg_weight = 0.15
        bullish_fvgs = [fvg for fvg in analysis['fvgs'] if fvg['type'] == 'bullish_fvg']
        bearish_fvgs = [fvg for fvg in analysis['fvgs'] if fvg['type'] == 'bearish_fvg']
        
        if bullish_fvgs:
            buy_score += fvg_weight
            confidence_factors.append(('Bullish FVG', fvg_weight))
        if bearish_fvgs:
            sell_score += fvg_weight
            confidence_factors.append(('Bearish FVG', fvg_weight))
        
        # Market Structure (25% weight)
        structure_weight = 0.25
        structure = analysis['market_structure']
        
        if structure['trend'] == 'uptrend':
            buy_score += structure_weight
            confidence_factors.append(('Uptrend', structure_weight))
        elif structure['trend'] == 'downtrend':
            sell_score += structure_weight
            confidence_factors.append(('Downtrend', structure_weight))
        
        # Break of Structure bonus/penalty
        if structure['bos']:
            if structure['trend'] == 'uptrend':
                sell_score += 0.1  # Trend might be changing
            else:
                buy_score += 0.1
            confidence_factors.append(('Break of Structure', 0.1))
        
        # OTE Zone (15% weight)
        ote_weight = 0.15
        if analysis['ote_zone']['in_ote']:
            # In OTE zone, favor trend direction
            if structure['trend'] == 'uptrend':
                buy_score += ote_weight
            elif structure['trend'] == 'downtrend':
                sell_score += ote_weight
            confidence_factors.append(('In OTE Zone', ote_weight))
        
        # Liquidity Sweeps (10% weight)
        sweep_weight = 0.10
        if analysis['liquidity_sweeps']:
            last_sweep = analysis['liquidity_sweeps'][-1]
            if last_sweep['type'] == 'sell_side_sweep':
                buy_score += sweep_weight
                confidence_factors.append(('Sell Side Sweep', sweep_weight))
            else:
                sell_score += sweep_weight
                confidence_factors.append(('Buy Side Sweep', sweep_weight))
        
        # Technical Indicators (20% weight)
        tech = analysis['technical_indicators']
        
        # RSI (5% weight)
        if tech['rsi'] < 30:
            buy_score += 0.05
            confidence_factors.append(('RSI Oversold', 0.05))
        elif tech['rsi'] > 70:
            sell_score += 0.05
            confidence_factors.append(('RSI Overbought', 0.05))
        
        # MACD (5% weight)
        if tech['macd_signal'] == 'bullish':
            buy_score += 0.05
            confidence_factors.append(('MACD Bullish', 0.05))
        elif tech['macd_signal'] == 'bearish':
            sell_score += 0.05
            confidence_factors.append(('MACD Bearish', 0.05))
        
        # Moving Average Trend (5% weight)
        if tech['ma_trend'] == 'bullish':
            buy_score += 0.05
            confidence_factors.append(('MA Bullish', 0.05))
        elif tech['ma_trend'] == 'bearish':
            sell_score += 0.05
            confidence_factors.append(('MA Bearish', 0.05))
        
        # Momentum (5% weight)
        if tech['momentum'] == 'bullish':
            buy_score += 0.05
            confidence_factors.append(('Momentum Bullish', 0.05))
        elif tech['momentum'] == 'bearish':
            sell_score += 0.05
            confidence_factors.append(('Momentum Bearish', 0.05))
        
        # Imbalances (10% weight)
        imb_weight = 0.10
        if analysis['imbalances']:
            recent_imb = analysis['imbalances'][-1]
            if recent_imb['type'] == 'bullish_imb':
                buy_score += imb_weight
                confidence_factors.append(('Bullish Imbalance', imb_weight))
            else:
                sell_score += imb_weight
                confidence_factors.append(('Bearish Imbalance', imb_weight))
        
        # Determine signal
        total_score = buy_score + sell_score
        if total_score == 0:
            return {
                'signal': 'HOLD',
                'confidence': 0.3,
                'buy_score': buy_score,
                'sell_score': sell_score,
                'factors': confidence_factors
            }
        
        if buy_score > sell_score:
            confidence = min(buy_score, 0.95)
            signal = 'BUY'
        elif sell_score > buy_score:
            confidence = min(sell_score, 0.95)
            signal = 'SELL'
        else:
            confidence = 0.4
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'factors': confidence_factors
        }

    def calculate_trade_levels(self, analysis, signal):
        """Calculate stop loss and take profit levels"""
        if not analysis or not signal or signal['signal'] == 'HOLD':
            return None
        
        current_price = analysis['current_price']
        atr = analysis['atr']
        
        # Risk management multipliers
        stop_loss_multiplier = 1.5
        take_profit_multiplier = 2.5
        
        # Adjust multipliers based on confidence
        confidence_adj = signal['confidence']
        if confidence_adj > 0.8:
            take_profit_multiplier = 3.0
        elif confidence_adj < 0.5:
            stop_loss_multiplier = 1.0
            take_profit_multiplier = 2.0
        
        if signal['signal'] == 'BUY':
            stop_loss = current_price - (atr * stop_loss_multiplier)
            take_profit = current_price + (atr * take_profit_multiplier)
            
            # Adjust based on support levels
            ssl_levels = analysis['ssl_bsl']['ssl_levels']
            if ssl_levels:
                nearest_support = max([level['price'] for level in ssl_levels 
                                     if level['price'] < current_price], default=stop_loss)
                stop_loss = max(stop_loss, nearest_support - (atr * 0.2))
        
        else:  # SELL
            stop_loss = current_price + (atr * stop_loss_multiplier)
            take_profit = current_price - (atr * take_profit_multiplier)
            
            # Adjust based on resistance levels
            bsl_levels = analysis['ssl_bsl']['bsl_levels']
            if bsl_levels:
                nearest_resistance = min([level['price'] for level in bsl_levels 
                                        if level['price'] > current_price], default=stop_loss)
                stop_loss = min(stop_loss, nearest_resistance + (atr * 0.2))
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            'entry_price': round(current_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'risk_amount': round(risk, 2),
            'reward_amount': round(reward, 2)
        }

    def estimate_profit_time(self, signal, analysis):
        """Estimate time to reach profit target"""
        if not signal or signal['signal'] == 'HOLD':
            return "No trade signal"
        
        # Base estimation on confidence and market conditions
        base_hours = 48  # Base 48 hours
        
        # Confidence factor (higher confidence = potentially faster)
        confidence_multiplier = 2.5 - (signal['confidence'] * 2)
        
        # Market structure factor
        structure = analysis['market_structure']
        if structure['bos']:
            confidence_multiplier *= 0.6  # Faster with structure break
        if structure['trend'] != 'sideways':
            confidence_multiplier *= 0.8  # Faster in trending market
        
        # OTE zone factor
        if analysis['ote_zone']['in_ote']:
            confidence_multiplier *= 0.7  # Faster in optimal entry zone
        
        # Volatility factor (higher ATR = potentially faster moves)
        atr_ratio = analysis['atr'] / analysis['current_price']
        if atr_ratio > 0.02:  # High volatility
            confidence_multiplier *= 0.8
        elif atr_ratio < 0.01:  # Low volatility
            confidence_multiplier *= 1.3
        
        estimated_hours = base_hours * confidence_multiplier
        
        # Convert to readable format
        if estimated_hours < 24:
            return f"{int(estimated_hours)} hours"
        else:
            days = int(estimated_hours / 24)
            hours = int(estimated_hours % 24)
            return f"{days} days, {hours} hours"

    def multi_timeframe_analysis(self):
        """Perform multi-timeframe analysis"""
        print("🔍 Starting Multi-Timeframe Analysis for Gold...")
        print("=" * 60)
        
        all_analyses = {}
        weighted_signals = {'buy_score': 0, 'sell_score': 0, 'total_confidence': 0}
        
        for timeframe in self.timeframes:
            print(f"\n📊 Analyzing {timeframe} timeframe...")
            analysis = self.analyze_timeframe(timeframe)
            
            if analysis:
                all_analyses[timeframe] = analysis
                signal = self.generate_trade_signal(analysis)
                
                if signal:
                    weight = self.timeframe_weights[timeframe]
                    weighted_signals['buy_score'] += signal['buy_score'] * weight
                    weighted_signals['sell_score'] += signal['sell_score'] * weight
                    weighted_signals['total_confidence'] += signal['confidence'] * weight
                    
                    print(f"   Signal: {signal['signal']} (Confidence: {signal['confidence']:.2f})")
                    print(f"   Current Price: ${analysis['current_price']:.2f}")
                    print(f"   Market Structure: {analysis['market_structure']['trend']}")
                    print(f"   FVGs: {len(analysis['fvgs'])}, Sweeps: {len(analysis['liquidity_sweeps'])}")
        
        return all_analyses, weighted_signals

    def generate_final_recommendation(self, all_analyses, weighted_signals):
        """Generate final trading recommendation"""
        print("\n" + "=" * 60)
        print("🎯 FINAL TRADING RECOMMENDATION")
        print("=" * 60)
        
        # Determine overall signal
        if weighted_signals['buy_score'] > weighted_signals['sell_score']:
            final_signal = 'BUY'
            confidence = min(weighted_signals['buy_score'], 0.95)
        elif weighted_signals['sell_score'] > weighted_signals['buy_score']:
            final_signal = 'SELL'
            confidence = min(weighted_signals['sell_score'], 0.95)
        else:
            final_signal = 'HOLD'
            confidence = 0.4
        
        print(f"📈 SIGNAL: {final_signal}")
        print(f"🎯 CONFIDENCE: {confidence:.1%}")
        print(f"📊 Buy Score: {weighted_signals['buy_score']:.2f}")
        print(f"📊 Sell Score: {weighted_signals['sell_score']:.2f}")
        
        # Use primary timeframe (1h) for trade levels
        primary_analysis = all_analyses.get('1h') or list(all_analyses.values())[0]
        signal_dict = {
            'signal': final_signal,
            'confidence': confidence,
            'buy_score': weighted_signals['buy_score'],
            'sell_score': weighted_signals['sell_score']
        }
        
        trade_levels = self.calculate_trade_levels(primary_analysis, signal_dict)
        
        if trade_levels:
            print(f"\n💰 TRADE SETUP:")
            print(f"   Entry Price: ${trade_levels['entry_price']}")
            print(f"   Stop Loss: ${trade_levels['stop_loss']}")
            print(f"   Take Profit: ${trade_levels['take_profit']}")
            print(f"   Risk/Reward: 1:{trade_levels['risk_reward_ratio']}")
            print(f"   Risk Amount: ${trade_levels['risk_amount']}")
            print(f"   Reward Amount: ${trade_levels['reward_amount']}")
            
            # Time estimation
            time_estimate = self.estimate_profit_time(signal_dict, primary_analysis)
            print(f"   Estimated Time to Target: {time_estimate}")
        
        # Market context
        print(f"\n🌍 MARKET CONTEXT:")
        structure = primary_analysis['market_structure']
        print(f"   Market Structure: {structure['trend'].upper()}")
        print(f"   Break of Structure: {'Yes' if structure['bos'] else 'No'}")
        print(f"   Current Price: ${primary_analysis['current_price']:.2f}")
        print(f"   ATR (Volatility): ${primary_analysis['atr']:.2f}")
        
        # OTE Zone info
        ote = primary_analysis['ote_zone']
        print(f"   In OTE Zone: {'Yes' if ote['in_ote'] else 'No'}")
        if ote['in_ote']:
            print(f"   OTE Range: ${ote['ote_low']:.2f} - ${ote['ote_high']:.2f}")
        
        # Risk warnings
        print(f"\n⚠️  RISK CONSIDERATIONS:")
        if confidence < 0.6:
            print("   - Low confidence signal - consider smaller position size")
        if structure['bos']:
            print("   - Market structure break detected - increased volatility expected")
        if primary_analysis['technical_indicators']['rsi'] > 80 or primary_analysis['technical_indicators']['rsi'] < 20:
            print("   - Extreme RSI levels - potential reversal risk")
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'trade_levels': trade_levels,
            'time_estimate': time_estimate,
            'market_context': {
                'structure': structure,
                'ote_zone': ote,
                'current_price': primary_analysis['current_price'],
                'atr': primary_analysis['atr']
            }
        }

    def run_analysis(self):
        """Run complete trading analysis"""
        try:
            print("🚀 Gold CFD Trading Bot - Advanced ICT Analysis")
            print("=" * 60)
            print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Multi-timeframe analysis
            all_analyses, weighted_signals = self.multi_timeframe_analysis()
            
            if not all_analyses:
                print("❌ No data available for analysis")
                return None
            
            # Generate final recommendation
            recommendation = self.generate_final_recommendation(all_analyses, weighted_signals)
            
            # Additional insights
            self.print_detailed_insights(all_analyses)
            
            print("\n" + "=" * 60)
            print("✅ Analysis Complete!")
            print("⚠️  Remember: This is for educational purposes only.")
            print("💡 Always do your own research and manage risk appropriately.")
            
            return recommendation
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return None

    def print_detailed_insights(self, all_analyses):
        """Print detailed market insights"""
        print(f"\n🔬 DETAILED MARKET INSIGHTS:")
        print("-" * 40)
        
        # Get primary timeframe data
        primary_tf = '1h'
        if primary_tf not in all_analyses:
            primary_tf = list(all_analyses.keys())[0]
        
        analysis = all_analyses[primary_tf]
        
        # FVG Analysis
        fvgs = analysis['fvgs']
        if fvgs:
            print(f"📊 Fair Value Gaps ({len(fvgs)} found):")
            for i, fvg in enumerate(fvgs[-3:], 1):  # Show last 3
                print(f"   {i}. {fvg['type'].replace('_', ' ').title()}")
                print(f"      Range: ${fvg['bottom']:.2f} - ${fvg['top']:.2f}")
                print(f"      Strength: {fvg['strength']:.4f}")
        
        # Liquidity Sweeps
        sweeps = analysis['liquidity_sweeps']
        if sweeps:
            print(f"\n🎯 Liquidity Sweeps ({len(sweeps)} found):")
            for i, sweep in enumerate(sweeps, 1):
                print(f"   {i}. {sweep['type'].replace('_', ' ').title()}")
                print(f"      Price: ${sweep['price']:.2f}")
                print(f"      Strength: {sweep['strength']:.4f}")
        
        # Imbalances
        imbalances = analysis['imbalances']
        if imbalances:
            print(f"\n⚡ Market Imbalances ({len(imbalances)} found):")
            for i, imb in enumerate(imbalances, 1):
                print(f"   {i}. {imb['type'].replace('_', ' ').title()}")
                print(f"      Price: ${imb['price']:.2f}")
                print(f"      Strength: {imb['strength']:.2f}x average")
        
        # Support/Resistance Levels
        ssl_bsl = analysis['ssl_bsl']
        print(f"\n🏗️  Key Levels:")
        if ssl_bsl['ssl_levels']:
            print(f"   Support Levels:")
            for level in ssl_bsl['ssl_levels'][-2:]:  # Show last 2
                print(f"      ${level['price']:.2f} (Strength: {level['strength']:.2f})")
        
        if ssl_bsl['bsl_levels']:
            print(f"   Resistance Levels:")
            for level in ssl_bsl['bsl_levels'][-2:]:  # Show last 2
                print(f"      ${level['price']:.2f} (Strength: {level['strength']:.2f})")
        
        # Technical Summary
        tech = analysis['technical_indicators']
        print(f"\n📈 Technical Summary:")
        print(f"   RSI: {tech['rsi']:.1f} ({'Oversold' if tech['rsi'] < 30 else 'Overbought' if tech['rsi'] > 70 else 'Neutral'})")
        print(f"   MACD: {tech['macd_signal'].title()}")
        print(f"   MA Trend: {tech['ma_trend'].title()}")
        print(f"   BB Position: {tech['bb_position'].title()}")
        print(f"   Volume Strength: {tech['volume_strength']:.2f}x")
        print(f"   Momentum: {tech['momentum'].title()}")

    def get_market_sentiment(self):
        """Get overall market sentiment summary"""
        try:
            analysis = self.analyze_timeframe('1h')
            if not analysis:
                return "Unable to determine market sentiment"
            
            signal = self.generate_trade_signal(analysis)
            structure = analysis['market_structure']
            
            sentiment_parts = []
            
            # Trend component
            if structure['trend'] == 'uptrend':
                sentiment_parts.append("📈 Bullish trend")
            elif structure['trend'] == 'downtrend':
                sentiment_parts.append("📉 Bearish trend")
            else:
                sentiment_parts.append("↔️ Sideways trend")
            
            # Signal component
            if signal:
                if signal['confidence'] > 0.7:
                    sentiment_parts.append(f"Strong {signal['signal']} signal")
                elif signal['confidence'] > 0.5:
                    sentiment_parts.append(f"Moderate {signal['signal']} signal")
                else:
                    sentiment_parts.append("Weak signal")
            
            # Volatility component
            atr_ratio = analysis['atr'] / analysis['current_price']
            if atr_ratio > 0.025:
                sentiment_parts.append("High volatility")
            elif atr_ratio < 0.01:
                sentiment_parts.append("Low volatility")
            else:
                sentiment_parts.append("Normal volatility")
            
            return " | ".join(sentiment_parts)
            
        except Exception as e:
            return f"Error getting sentiment: {e}"

# Usage example and demonstration
def main():
    """Main function to demonstrate the bot"""
    bot = GoldCFDTradingBot()
    
    # Run complete analysis
    result = bot.run_analysis()
    
    # Quick sentiment check
    print(f"\n🎭 Market Sentiment: {bot.get_market_sentiment()}")
    
    return result

if __name__ == "__main__":
    main()

