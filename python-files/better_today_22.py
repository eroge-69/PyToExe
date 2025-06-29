import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, ttk
import os
import json
import time
import threading
import pyotp
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import deque
import base64
import socket
import hashlib
from growwapi import GrowwAPI
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ========= SECURITY CONFIGURATION =========
USER_PASSWORD = "Sujatha123"  # Change before deployment
SALT = b'SuperTrendTrader'    # Change before deployment
# =========================================

# ========= TRADING CONSTANTS =========
MAX_TRADES_PER_DAY = 15
ORDER_TIMEOUT_MINUTES = 5
SUPERTREND_PERIOD1 = 5
SUPERTREND_MULTIPLIER1 = 1.5
SUPERTREND_PERIOD2 = 8
SUPERTREND_MULTIPLIER2 = 1.8
MACD_FAST_PERIOD = 8
MACD_SLOW_PERIOD = 16
MACD_SIGNAL_PERIOD = 7

# Volatility thresholds (ATR as percentage of price)
VOLATILITY_THRESHOLDS = {
    "LOW": 0.003,    # 0.3%
    "MEDIUM": 0.007, # 0.7%
    "HIGH": 0.012    # 1.2%
}

# News events (for simulation) - format: (event_time, event_name)
NEWS_EVENTS = [
    (datetime.now().replace(hour=10, minute=0, second=0), "RBI Policy"),
    (datetime.now().replace(hour=14, minute=0, second=0), "Fed Meeting")
]

CHOPPINESS_THRESHOLD = 61.8  # Fibonacci threshold for choppy market
# =====================================

class SecureStorage:
    def __init__(self, password, user_id):
        self.password = password.encode()
        self.user_id = user_id.encode()
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT + self.user_id,
            iterations=100000,
        )
        self.key = base64.urlsafe_b64encode(self.kdf.derive(self.password))
        self.cipher = Fernet(self.key)
        self.filename = f'groww_config_{user_id}.bin'
    
    def save_credentials(self, api_key, api_secret):
        data = {
            'api_key': api_key,
            'api_secret': api_secret,
            'timestamp': time.time(),
            'user_id': self.user_id.decode()
        }
        encrypted = self.cipher.encrypt(json.dumps(data).encode())
        with open(self.filename, 'wb') as f:
            f.write(encrypted)
    
    def load_credentials(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'rb') as f:
                    data = json.loads(self.cipher.decrypt(f.read()).decode())
                    if data.get('user_id') != self.user_id.decode():
                        return None, None
                    if time.time() - data['timestamp'] < 12 * 3600:
                        return data['api_key'], data['api_secret']
            return None, None
        except:
            return None, None

class TradeLogger:
    def __init__(self, user_id):
        self.user_id = user_id
        self.log_file = f"trades_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        self.initialize_log_file()
    
    def initialize_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("timestamp,action,index,symbol,price,quantity,position_type,volatility_regime,exit_reason\n")
    
    def log_trade(self, action, index, symbol, price, quantity, position_type, volatility_regime, exit_reason=""):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp},{action},{index},{symbol},{price},{quantity},{position_type},{volatility_regime},{exit_reason}\n")

class MarketState:
    def __init__(self, trader):
        self.trader = trader
        self.current_state = None

    def detect_state(self, index, df, atr, current_price):
        volatility_ratio = atr / current_price
        adx = self.trader.indicator_status[index].get("adx", 0)
        ci = self.calculate_choppiness(df) if len(df) >= 14 else 0

        if volatility_ratio > VOLATILITY_THRESHOLDS["HIGH"] and adx < 20:
            return "CRASH"
        elif adx > 25:
            return "TRENDING"
        elif ci > CHOPPINESS_THRESHOLD:
            return "RANGING"
        else:
            return "BREAKOUT"

    def calculate_choppiness(self, df, period=14):
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift())
        tr3 = abs(df['low'] - df['close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        max_high = df['high'].rolling(period).max()
        min_low = df['low'].rolling(period).min()
        
        ci = 100 * np.log10((atr.rolling(period).sum()) / 
             (max_high - min_low)) / np.log10(period)
        return ci.iloc[-1] if not ci.empty else 0

    def handle_state(self, index, state):
        if state == "CRASH":
            # Implement crash protocol: wider stops, smaller positions
            self.trader.STOP_LOSS = int(self.trader.STOP_LOSS * 1.8)
            self.trader.POSITION_SIZE_MULTIPLIER = 0.5
            self.trader.ENTRY_STRATEGY = "REVERSAL_ONLY"
            self.trader.volatility_regime = "CRASH"
        elif state == "TRENDING":
            self.trader.STOP_LOSS = 10  # default
            self.trader.POSITION_SIZE_MULTIPLIER = 1.0
            self.trader.ENTRY_STRATEGY = "TREND_FOLLOWING"
            self.trader.volatility_regime = "TRENDING"
        elif state == "RANGING":
            self.trader.STOP_LOSS = int(self.trader.STOP_LOSS * 0.7)
            self.trader.POSITION_SIZE_MULTIPLIER = 0.7
            self.trader.ENTRY_STRATEGY = "RANGE_BOUND"
            self.trader.volatility_regime = "RANGING"
        else:  # BREAKOUT
            self.trader.STOP_LOSS = 10
            self.trader.POSITION_SIZE_MULTIPLIER = 1.2
            self.trader.ENTRY_STRATEGY = "BREAKOUT"
            self.trader.volatility_regime = "BREAKOUT"

class IndexOptionsTrader:
    INDEX_CONFIG = {
        "NIFTY": {
            "strike_step": 50,
            "lot_size": 75,
            "option_prefix": "NIFTY",
            "cash_symbol": "NSE_NIFTY"
        },
        "BANKNIFTY": {
            "strike_step": 100,
            "lot_size": 25,
            "option_prefix": "BANKNIFTY",
            "cash_symbol": "NSE_BANKNIFTY"
        },
        "FINNIFTY": {
            "strike_step": 50,
            "lot_size": 40,
            "option_prefix": "FINNIFTY",
            "cash_symbol": "NSE_FINNIFTY"
        }
    }
    
    def __init__(self, api_key, api_secret, user_id, indices):
        self.user_id = user_id
        self.API_AUTH_TOKEN = "eyJraWQiOiJaTUtjVXciLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjI1Mzk1MjczMTAsImlhdCI6MTc1MTEyNzMxMCwibmJmIjoxNzUxMTI3MzEwLCJzdWIiOiJ7XCJ0b2tlblJlZklkXCI6XCJhMGZiZTY3Yi00Nzg5LTQ2MTMtOTA4MC0yNzM0MTBjNjM4ZTRcIixcInZlbmRvckludGVncmF0aW9uS2V5XCI6XCJlMzFmZjIzYjA4NmI0MDZjODg3NGIyZjZkODQ5NTMxM1wiLFwidXNlckFjY291bnRJZFwiOlwiNjVhMzA2YjEtYmJmYy00Yjc5LWFkOWItOTZmMzRhODgxODgwXCIsXCJkZXZpY2VJZFwiOlwiZTBlZmQzMjktNDJmZC01ZjJjLWJjNTEtYjA2Y2M0NWNiNWRhXCIsXCJzZXNzaW9uSWRcIjpcImZmMzQ3MjRkLTJhZjgtNGJmYy04NjAwLWI5ZmE1ZTdjNTIwOVwiLFwiYWRkaXRpb25hbERhdGFcIjpcIno1NC9NZzltdjE2WXdmb0gvS0EwYkdVeHA2aXIyTksxeEZjNGJ5L2oxWEJSTkczdTlLa2pWZDNoWjU1ZStNZERhWXBOVi9UOUxIRmtQejFFQisybTdRPT1cIixcInJvbGVcIjpcImF1dGgtdG90cFwiLFwic291cmNlSXBBZGRyZXNzXCI6XCIyNDAxOjQ5MDA6NjFiZjphMGQ2OmQ0MjQ6NzQwNDo5NzI3OjU0NDEsMTcyLjcwLjIxOC4xNzksMzUuMjQxLjIzLjEyM1wiLFwidHdvRmFFeHBpcnlUc1wiOjI1Mzk1MjczMTAxODF9IiwiaXNzIjoiYXBleC1hdXRoLXByb2QtYXBwIn0.7HedhbCPK6ICKqO_LOaQ-j5VPtR56Or7se9BrLUpS2fugekDOdG8o3SAQ0f8KrbvrBoBIH1iHzGN0wnAPQoy6g"
        self.totp_gen = pyotp.TOTP("B4HDG2ESVDCTPLULTTSWNB5JVJYORPRQ")
        self.totp = self.totp_gen.now()
        self.access_token = GrowwAPI.get_access_token(self.API_AUTH_TOKEN, self.totp) 
        self.groww = GrowwAPI(self.access_token)
        
        # Trading parameters
        self.BASE_PROFIT_TARGET = 8
        self.STOP_LOSS = 10
        self.TRAIL_AMOUNT = 5
        self.ATR_PERIOD = 4
        self.ADX_PERIOD = 5
        self.MARKET_TREND_THRESHOLD = 12
        
        # Trading state
        self.current_position = None
        self.stop_loss_price = None
        self.trailing_stop_activated = False
        self.highest_price_since_entry = 0
        self.price_data = {index: deque(maxlen=100) for index in indices}
        self.last_candle_time = {index: None for index in indices}
        self.trade_count = 0
        self.last_trade_day = None
        self.pending_orders = {}
        self.previous_close = {index: 0 for index in indices}
        self.current_candle = {index: None for index in indices}
        self.active_trade_lock = threading.Lock()
        self.running = False
        self.last_status_print = time.time()
        self.indicator_status = {index: {"st1": None, "st2": None, "macd": None, "adx": None, "trend": "SIDEWAYS"} for index in indices}
        self.last_trade_time = None
        self.last_position_print = 0
        self.partial_booked = False
        self.position_entry_time = None
        self.last_trade_direction = None
        self.volatility_adjusted = False
        self.higher_timeframe_cache = {index: {'timestamp': None, 'data': None} for index in indices}
        self.indices = indices
        self.volatility_regime = "MEDIUM"
        self.ENTRY_STRATEGY = "TREND_FOLLOWING"
        self.POSITION_SIZE_MULTIPLIER = 1.0
        self.news_schedule = NEWS_EVENTS
        
        # New attributes
        self.logger = TradeLogger(user_id)
        self.cooldown_active = False
        self.cooldown_end = None
        self.chart_data = {index: deque(maxlen=200) for index in indices}
        self.signals = {index: deque(maxlen=200) for index in indices}
        self.trade_history = []
        self.account_value = 1000000  # Starting capital (should be fetched from API)
        
        # Market state handler
        self.market_state = MarketState(self)
        
        # Initialize previous close for each index
        for index in indices:
            self.previous_close[index] = self.get_previous_close(index)
            print(f"📅 User: {user_id} | {index} Previous Close: {self.previous_close[index]:.2f}")
            
            # Seed initial data
            for i in range(20):
                self.price_data[index].append({
                    'timestamp': datetime.now() - timedelta(minutes=3*(20-i)),
                    'open': self.previous_close[index],
                    'high': self.previous_close[index],
                    'low': self.previous_close[index],
                    'close': self.previous_close[index]
                })

    def get_previous_close(self, index):
        try:
            if not self.check_internet_connection():
                raise ConnectionError("No internet connection")

            ltp_response = self.groww.get_ltp(
                segment=GrowwAPI.SEGMENT_CASH,
                exchange_trading_symbols=self.INDEX_CONFIG[index]["cash_symbol"]
            )

            ltp = ltp_response.get(self.INDEX_CONFIG[index]["cash_symbol"])
            if ltp and ltp > 0:
                print(f"✅ Using LTP as Previous Close for {index}: {ltp:.2f}")
                return ltp
            else:
                raise ValueError("LTP unavailable")
        except Exception as e:
            print(f"⚠️ Failed to fetch previous close for {index}: {str(e)}")
            return 25000 if index == "NIFTY" else 50000 if index == "BANKNIFTY" else 20000

    def check_internet_connection(self):
        try:
            socket.gethostbyname('api.groww.in')
            return True
        except:
            return False

    def calculate_gap(self, index):
        try:
            if not self.check_internet_connection():
                return 0
                
            ltp_response = self.groww.get_ltp(
                segment=GrowwAPI.SEGMENT_CASH, 
                exchange_trading_symbols=self.INDEX_CONFIG[index]["cash_symbol"]
            )
            current_price = ltp_response.get(self.INDEX_CONFIG[index]["cash_symbol"], self.previous_close[index])
            gap_percent = abs((current_price - self.previous_close[index]) / self.previous_close[index]) * 100
            return gap_percent
        except Exception as e:
            print(f"Error calculating gap for {index}: {str(e)}")
            return 0

    def get_nearest_expiry(self):
        today = datetime.now().date()
        days_until_thurs = (3 - today.weekday()) % 7
        if days_until_thurs == 0 and datetime.now().time() < datetime.strptime("15:30", "%H:%M").time():
            return today.strftime("%d-%b-%Y").upper()
        expiry_date = today + timedelta(days=7 if days_until_thurs == 0 else days_until_thurs)
        return expiry_date.strftime("%d-%b-%Y").upper()

    def reset_trade_count_if_new_day(self):
        today = datetime.now().date()
        if self.last_trade_day != today:
            self.trade_count = 0
            self.last_trade_day = today
            print(f"♻️ Trade count reset for new day: {today.strftime('%Y-%m-%d')}")

    def is_market_open(self):
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return now.weekday() < 5 and market_open <= now <= market_close
    
    def is_within_first_15_minutes(self):
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        first_15_end = now.replace(hour=9, minute=30, second=0, microsecond=0)
        return market_open <= now <= first_15_end
    
    def is_after_230(self):
        now = datetime.now()
        return now.time() >= datetime.strptime("14:30", "%H:%M").time()

    def get_order_status(self, order_id):
        try:
            if not self.check_internet_connection():
                return {"order_status": "NETWORK_ERROR"}
                
            # Fixed: Pass order_id as named parameter
            order_detail = self.groww.get_order_detail(groww_order_id=order_id)
            return order_detail
        except Exception as e:
            print(f"Error getting order status: {str(e)}")
            return {"order_status": "ERROR"}

    def get_ltp(self, symbol):
        """Improved LTP retrieval with error handling"""
        try:
            if not self.check_internet_connection():
                return 0
                
            response = self.groww.get_ltp(
                segment=GrowwAPI.SEGMENT_FNO,
                exchange_trading_symbols=symbol
            )
            return response.get(symbol, 0)
        except Exception as e:
            print(f"LTP retrieval error for {symbol}: {str(e)}")
            return 0

    def manage_position(self):
        """Position management with layered exit conditions in priority order"""
        failure_count = 0
        exit_reason = ""
        while self.current_position and self.running:
            try:
                if not self.is_market_open():
                    time.sleep(60)
                    continue

                if not self.check_internet_connection():
                    time.sleep(10)
                    continue

                # Use the symbol directly without prefix
                symbol = self.current_position['symbol']
                ltp = self.get_ltp(symbol)

                if ltp <= 0:
                    failure_count += 1
                    print(f"⚠️ Invalid LTP for {symbol} (attempt {failure_count}/5)")
                    if failure_count >= 5:
                        print("🔴 Too many failures, closing position.")
                        exit_reason = "LTP_FAILURE"
                        self.close_position(exit_reason)
                        break
                    time.sleep(5)
                    continue
                else:
                    failure_count = 0  # Reset on success

                # Get current candle data for indicators
                df = self.get_candle_df(self.current_position['index'])
                current_price = ltp
                entry_price = self.current_position['entry_price']
                position_type = self.current_position['type']
                
                # ===== EXIT CONDITION 1: STOP LOSS/TRAILING STOP =====
                # Update highest price for trailing stop
                if current_price > self.highest_price_since_entry:
                    self.highest_price_since_entry = current_price
                    
                    # Activate trailing after hitting profit target
                    if not self.trailing_stop_activated and current_price >= entry_price + self.PROFIT_TARGET:
                        self.trailing_stop_activated = True
                        self.stop_loss_price = self.highest_price_since_entry - self.TRAIL_AMOUNT
                        print(f"[TRAIL] 🔵 Activated at: {self.stop_loss_price:.2f}")

                    # Update trailing stop
                    elif self.trailing_stop_activated:
                        new_stop = self.highest_price_since_entry - self.TRAIL_AMOUNT
                        if new_stop > self.stop_loss_price:
                            self.stop_loss_price = new_stop
                            print(f"[TRAIL] 🔄 Updated to: {new_stop:.2f}")

                # Check stop loss hit (highest priority)
                if self.stop_loss_price is not None and current_price <= self.stop_loss_price:
                    exit_reason = "STOP_LOSS"
                    print(f"❗ SL Hit! LTP: {current_price}, SL: {self.stop_loss_price}")
                    self.close_position(exit_reason)
                    break

                # ===== EXIT CONDITION 2: SUPERTREND REVERSAL =====
                if len(df) >= SUPERTREND_PERIOD1:
                    supertrend = self.calculate_supertrend(df, SUPERTREND_PERIOD1, SUPERTREND_MULTIPLIER1)
                    current_st = supertrend.iloc[-1]
                    
                    # For CALL positions - exit when SuperTrend turns RED
                    if position_type == "CALL" and not current_st:
                        exit_reason = "SUPERTREND_REVERSAL"
                        print("❗ SuperTrend turned RED - exiting CALL position")
                        self.close_position(exit_reason)
                        break
                        
                    # For PUT positions - exit when SuperTrend turns GREEN
                    elif position_type == "PUT" and current_st:
                        exit_reason = "SUPERTREND_REVERSAL"
                        print("❗ SuperTrend turned GREEN - exiting PUT position")
                        self.close_position(exit_reason)
                        break

                # ===== EXIT CONDITION 3: VOLATILITY-BASED PARTIAL PROFITS =====
                if len(df) >= self.ATR_PERIOD:
                    atr = self.calculate_atr(df, self.ATR_PERIOD).iloc[-1]
                    
                    # Adjust trail distance based on volatility
                    trail_distance = max(5, min(20, int(atr * 0.7)))
                    self.TRAIL_AMOUNT = trail_distance
                    
                    # Calculate profit metrics
                    profit = current_price - entry_price
                    atr_ratio = profit / atr if atr > 0 else 0
                    
                    # Book partial profits at key volatility milestones
                    if atr_ratio > 2.5 and not self.partial_booked:
                        self.book_partial_profit(current_price, qty_percent=50)
                    elif atr_ratio > 1.8 and not self.partial_booked:
                        self.book_partial_profit(current_price, qty_percent=30)

                # ===== EXIT CONDITION 4: TIME-BASED EXIT =====
                current_duration = (datetime.now() - self.position_entry_time).seconds
                if current_duration < 600 and not self.trailing_stop_activated:  # First 10 minutes
                    time.sleep(5)
                    continue

                # Max position duration (2 hours)
                if current_duration > 7200:
                    exit_reason = "TIME_EXPIRY"
                    print("🕒 Max position duration reached - closing")
                    self.close_position(exit_reason)
                    break

                time.sleep(5)
            except Exception as e:
                print(f"Position monitoring error: {str(e)}")
                # Attempt to recover position info
                if not self.verify_position():
                    print("🛑 Position verification failed - closing management")
                    self.current_position = None
                time.sleep(10)
                
    def verify_position(self):
        """Verify position still exists with broker"""
        if not self.current_position:
            return False
            
        positions = self.get_user_positions()
        for pos in positions:
            if pos['symbol'] == self.current_position['symbol']:
                return True
        return False

    def book_partial_profit(self, current_price, qty_percent=50):
        try:
            if not self.is_market_open() or not self.check_internet_connection():
                return
                
            symbol = self.current_position['symbol']
            qty = int(self.current_position['quantity'] * qty_percent / 100)
            if qty <= 0:
                return
                
            close_response = self.groww.place_order(
                trading_symbol=symbol,
                quantity=qty,
                price=0,  # Market order
                validity=GrowwAPI.VALIDITY_DAY,
                exchange=GrowwAPI.EXCHANGE_NSE,
                segment=GrowwAPI.SEGMENT_FNO,
                product=GrowwAPI.PRODUCT_NRML,
                order_type=GrowwAPI.ORDER_TYPE_MARKET,
                transaction_type=GrowwAPI.TRANSACTION_TYPE_SELL,
            )
            
            if 'order_id' in close_response:
                # Adjust position
                self.current_position['quantity'] -= qty
                self.partial_booked = True
                
                # Log partial exit
                self.logger.log_trade("PARTIAL_EXIT", self.current_position['index'], symbol, 
                                     current_price, qty,
                                     self.current_position['type'],
                                     self.volatility_regime,
                                     "PARTIAL_PROFIT")
                
                # Record partial exit
                self.trade_history.append({
                    'entry_time': self.current_position['entry_time'],
                    'exit_time': datetime.now(),
                    'index': self.current_position['index'],
                    'symbol': symbol,
                    'entry_price': self.current_position['entry_price'],
                    'exit_price': current_price,
                    'type': self.current_position['type'] + f" (Partial {qty_percent}%)",
                    'volatility': self.volatility_regime,
                    'exit_reason': "PARTIAL_PROFIT"
                })
                
                print(f"🎯 Booked {qty_percent}% profit @ {current_price:.2f}")
        except Exception as e:
            print(f"Partial booking error: {str(e)}")

    def close_position(self, exit_reason=""):
        if not self.current_position:
            return
            
        try:
            if not self.is_market_open() or not self.check_internet_connection():
                return
                
            symbol = self.current_position['symbol']
            current_price = self.get_ltp(symbol) or self.current_position['entry_price']
            
            if current_price <= 0:
                print(f"⚠️ Failed to get LTP for closing {symbol}. Using entry price as fallback.")
                current_price = self.current_position['entry_price']
            
            close_response = self.groww.place_order(
                trading_symbol=self.current_position['symbol'],
                quantity=self.current_position['quantity'],
                price=0,  # Market order
                validity=GrowwAPI.VALIDITY_DAY,
                exchange=GrowwAPI.EXCHANGE_NSE,
                segment=GrowwAPI.SEGMENT_FNO,
                product=GrowwAPI.PRODUCT_NRML,
                order_type=GrowwAPI.ORDER_TYPE_MARKET,
                transaction_type=GrowwAPI.TRANSACTION_TYPE_SELL,
            )
            
            if 'order_id' in close_response:
                order_id = close_response['order_id']
                self.pending_orders[order_id] = {
                    'symbol': self.current_position['symbol'],
                    'placed_time': datetime.now(),
                    'type': 'EXIT',
                    'status': 'OPEN'
                }
                
                # Log exit trade
                self.logger.log_trade("EXIT", self.current_position['index'], 
                                     self.current_position['symbol'], 
                                     current_price, self.current_position['quantity'],
                                     self.current_position['type'],
                                     self.volatility_regime,
                                     exit_reason)
                
                # Start cooldown period
                self.start_cooldown()
                
                # Record trade in history
                self.trade_history.append({
                    'entry_time': self.current_position['entry_time'],
                    'exit_time': datetime.now(),
                    'index': self.current_position['index'],
                    'symbol': self.current_position['symbol'],
                    'entry_price': self.current_position['entry_price'],
                    'exit_price': current_price,
                    'type': self.current_position['type'],
                    'volatility': self.volatility_regime,
                    'exit_reason': exit_reason
                })
                
                print(f"✅ Position closed for {self.current_position['symbol']} ({exit_reason})")
                self.last_trade_time = datetime.now()
        except Exception as e:
            print(f"Error closing position: {str(e)}")
        finally:
            self.current_position = None
            self.stop_loss_price = None
            self.trailing_stop_activated = False
            self.highest_price_since_entry = 0
            self.partial_booked = False
            self.volatility_adjusted = False
            self.position_entry_time = None

    def start_cooldown(self, minutes=3):
        self.cooldown_active = True
        self.cooldown_end = datetime.now() + timedelta(minutes=minutes)
        print(f"⏱️ Cooldown started for {minutes} minutes")
    
    def get_cooldown_remaining(self):
        if not self.cooldown_active or not self.cooldown_end:
            return 0
        return max(0, (self.cooldown_end - datetime.now()).total_seconds())

    def monitor_pending_orders(self):
        if not self.is_market_open():
            return
            
        current_time = datetime.now()
        orders_to_remove = []
        
        for order_id, order_info in list(self.pending_orders.items()):
            try:
                if not self.check_internet_connection():
                    continue
                    
                order_detail = self.get_order_status(order_id)
                current_status = order_detail.get('order_status', 'UNKNOWN')
                order_info['status'] = current_status
                
                if current_status == "COMPLETE":
                    orders_to_remove.append(order_id)
                    if order_info['type'] == 'ENTRY':
                        if self.verify_position_by_order(order_info):
                            self.setup_position(order_info, order_detail)
                elif current_status in ["CANCELLED", "REJECTED"]:
                    orders_to_remove.append(order_id)
                    print(f"❌ Order {order_id} {current_status}")
                elif current_status == "OPEN":
                    time_elapsed = (current_time - order_info['placed_time']).total_seconds() / 60
                    if time_elapsed >= ORDER_TIMEOUT_MINUTES:
                        try:
                            # Fixed: Pass order_id as named parameter
                            cancel_response = self.groww.cancel_order(groww_order_id=order_id)
                            if cancel_response.get('status') == 'CANCELLED':
                                print(f"⌛ Timeout - Cancelled order {order_id}")
                                orders_to_remove.append(order_id)
                        except Exception as e:
                            print(f"Cancel order error: {str(e)}")
            except Exception as e:
                print(f"Error monitoring order {order_id}: {str(e)}")
        
        for order_id in orders_to_remove:
            self.pending_orders.pop(order_id, None)

    def verify_position_by_order(self, order_info):
        try:
            position_response = self.groww.get_position_for_trading_symbol(
                trading_symbol=order_info['symbol'],
                segment=GrowwAPI.SEGMENT_FNO
            )
            
            if position_response and position_response.get('quantity', 0) > 0:
                print(f"✅ Position verified for {order_info['symbol']} (Order ID: {order_info.get('order_id', 'N/A')})")
                return True
            else:
                print(f"⚠️ Position not found for {order_info['symbol']} after order completion")
                return False
        except Exception as e:
            print(f"Position verification error: {str(e)}")
            return False

    def setup_position(self, order_info, order_detail):
        if self.current_position:
            return
            
        executed_price = order_detail.get('average_price', order_info['entry_price'])
        
        self.current_position = {
            'index': order_info['index'],
            'symbol': order_info['symbol'],  # Store without prefix
            'quantity': order_info['quantity'],
            'entry_price': executed_price,
            'type': order_info['position_type'],
            'entry_time': datetime.now()
        }
        self.position_entry_time = datetime.now()
        self.stop_loss_price = executed_price - self.STOP_LOSS
        self.trade_count += 1
        self.highest_price_since_entry = executed_price
        self.last_trade_time = datetime.now()
        self.last_trade_direction = order_info['position_type']
        self.partial_booked = False
        self.volatility_adjusted = False
        
        # Log entry trade
        self.logger.log_trade("ENTRY", order_info['index'], 
                             order_info['symbol'], 
                             executed_price, 
                             order_info['quantity'],
                             order_info['position_type'],
                             self.volatility_regime)
        
        print(f"📊 Position setup: {order_info['symbol']}")
        print(f"Entry: {executed_price:.2f} | SL: {self.stop_loss_price:.2f} | Target: +{self.PROFIT_TARGET}")
        
        threading.Thread(target=self.manage_position, daemon=True).start()

    def calculate_supertrend(self, df, period, multiplier):
        hl2 = (df['high'] + df['low']) / 2
        atr = multiplier * (df['high'] - df['low']).rolling(period).mean()
        upper_band = hl2 + atr
        lower_band = hl2 - atr
        
        supertrend = [True] * len(df)
        for i in range(1, len(df)):
            if df['close'].iloc[i] > upper_band.iloc[i-1]:
                supertrend[i] = True
            elif df['close'].iloc[i] < lower_band.iloc[i-1]:
                supertrend[i] = False
            else:
                supertrend[i] = supertrend[i-1]
        return supertrend

    def calculate_macd(self, df, fast_period=12, slow_period=21, signal_period=9):
        ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram

    def calculate_ema(self, df, period=21):
        return df['close'].ewm(span=period, adjust=False).mean()

    def calculate_atr(self, df, period=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(period).mean()
    
    def calculate_adx(self, df, period=14):
        df['tr0'] = abs(df['high'] - df['low'])
        df['tr1'] = abs(df['high'] - df['close'].shift())
        df['tr2'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr0','tr1','tr2']].max(axis=1)
        
        df['upmove'] = df['high'] - df['high'].shift()
        df['downmove'] = df['low'].shift() - df['low']
        df['plus_dm'] = np.where((df['upmove'] > df['downmove']) & (df['upmove']>0), df['upmove'], 0)
        df['minus_dm'] = np.where((df['downmove'] > df['upmove']) & (df['downmove']>0), df['downmove'], 0)
        
        df['plus_di'] = 100 * (df['plus_dm'].ewm(span=period, adjust=False).mean() / 
                              df['tr'].ewm(span=period, adjust=False).mean())
        df['minus_di'] = 100 * (df['minus_dm'].ewm(span=period, adjust=False).mean() / 
                               df['tr'].ewm(span=period, adjust=False).mean())
        df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        df['adx'] = df['dx'].ewm(span=period, adjust=False).mean()
        return df['adx'], df['plus_di'], df['minus_di']
    
    def calculate_dynamic_target(self, atr):
        base_target = self.BASE_PROFIT_TARGET
        volatility_factor = max(1.0, min(4.0, atr / 8))
        return int(base_target * volatility_factor)

    def update_candle_data(self, index, current_price):
        current_time = datetime.now()
        
        if self.last_candle_time[index] is None:
            self.last_candle_time[index] = current_time
            self.current_candle[index] = {
                'timestamp': current_time,
                'open': current_price,
                'high': current_price,
                'low': current_price,
                'close': current_price
            }
            self.chart_data[index].append({
                'timestamp': current_time,
                'price': current_price
            })
            return False
        
        if (current_time - self.last_candle_time[index]).total_seconds() >= 180:
            self.price_data[index].append(self.current_candle[index])
            self.current_candle[index] = {
                'timestamp': current_time,
                'open': current_price,
                'high': current_price,
                'low': current_price,
                'close': current_price
            }
            self.last_candle_time[index] = current_time
            
            self.chart_data[index].append({
                'timestamp': current_time,
                'price': current_price
            })
            
            if self.indicator_status[index]["st1"] is not None and self.indicator_status[index]["st2"] is not None:
                self.signals[index].append({
                    'timestamp': current_time,
                    'st1': self.indicator_status[index]["st1"],
                    'st2': self.indicator_status[index]["st2"],
                    'macd': self.indicator_status[index]["macd"],
                    'adx': self.indicator_status[index]["adx"],
                    'trend': self.indicator_status[index]["trend"]
                })
            
            return True
        else:
            self.current_candle[index]['high'] = max(self.current_candle[index]['high'], current_price)
            self.current_candle[index]['low'] = min(self.current_candle[index]['low'], current_price)
            self.current_candle[index]['close'] = current_price
            return False

    def get_candle_df(self, index):
        if not self.price_data[index]:
            return pd.DataFrame()
        return pd.DataFrame(self.price_data[index])
    
    def get_chart_data(self, index):
        if not self.chart_data[index] or not self.signals[index]:
            return pd.DataFrame(), pd.DataFrame()
            
        price_df = pd.DataFrame(self.chart_data[index])
        signals_df = pd.DataFrame(self.signals[index])
        merged = pd.merge_asof(price_df, signals_df, on='timestamp', direction='nearest')
        return price_df, merged

    def get_option_symbol(self, index, expiry_date, strike, option_type):
        expiry_obj = datetime.strptime(expiry_date, "%d-%b-%Y")
        year_code = expiry_obj.strftime("%y")
        month_code = expiry_obj.strftime("%b").upper()
        day_code = expiry_obj.strftime("%d")
        strike_str = str(int(strike))
        return f"{self.INDEX_CONFIG[index]['option_prefix']}{year_code}{month_code}{strike_str}{option_type}"

    def get_option_ltps(self, index, call_symbol, put_symbol):
        call_ltp, put_ltp = 0, 0
        try:
            if not self.check_internet_connection():
                return 0, 0
                
            call_ltp = self.get_ltp(call_symbol)
            put_ltp = self.get_ltp(put_symbol)
        except Exception as e:
            print(f"Error getting option LTPs: {str(e)}")
        return call_ltp, put_ltp

    def print_indicator_status(self, index):
        try:
            if not self.price_data[index]:
                return ""
                
            df = self.get_candle_df(index)
            if len(df) < 2:
                return ""
                
            df['st1'] = self.calculate_supertrend(df, SUPERTREND_PERIOD1, SUPERTREND_MULTIPLIER1)
            df['st2'] = self.calculate_supertrend(df, SUPERTREND_PERIOD2, SUPERTREND_MULTIPLIER2)
            
            macd, signal, _ = self.calculate_macd(df)
            ema_21 = self.calculate_ema(df, 21)
            
            if macd is not None and signal is not None:
                df['macd'] = macd
                df['signal'] = signal
                last_macd = df.iloc[-1]['macd']
                last_signal = df.iloc[-1]['signal']
                
                if last_macd > last_signal:
                    macd_status = "BULLISH"
                else:
                    macd_status = "BEARISH"
            else:
                macd_status = "N/A"
            
            # Calculate ADX for trend strength
            adx, plus_di, minus_di = self.calculate_adx(df, self.ADX_PERIOD)
            last_adx = adx.iloc[-1] if adx is not None else 0
            last_plus_di = plus_di.iloc[-1] if plus_di is not None else 0
            last_minus_di = minus_di.iloc[-1] if minus_di is not None else 0
            
            # Determine market trend
            if last_adx > self.MARKET_TREND_THRESHOLD:
                if last_plus_di > last_minus_di:
                    trend_status = "UPTREND"
                else:
                    trend_status = "DOWNTREND"
            else:
                trend_status = "SIDEWAYS"
            
            self.indicator_status[index] = {
                "st1": df.iloc[-1]['st1'],
                "st2": df.iloc[-1]['st2'],
                "macd": macd_status,
                "adx": last_adx,
                "trend": trend_status
            }
            
            status_text = f"\n📊 {index} Indicator Status (3-min):\n"
            status_text += f"Market Trend: {trend_status} (ADX: {last_adx:.2f}, +DI: {last_plus_di:.2f}, -DI: {last_minus_di:.2f})\n"
            status_text += f"SuperTrend(7,1.5): {'🟢 GREEN' if self.indicator_status[index]['st1'] else '🔴 RED'}\n"
            status_text += f"SuperTrend(10,2): {'🟢 GREEN' if self.indicator_status[index]['st2'] else '🔴 RED'}\n"
            status_text += f"EMA 21: {ema_21.iloc[-1]:.2f} | Price {'ABOVE' if df.iloc[-1]['close'] > ema_21.iloc[-1] else 'BELOW'}\n"
            
            if macd_status == "BULLISH":
                status_text += f"MACD: 🟢 BULLISH (MACD: {last_macd:.2f}, Signal: {last_signal:.2f})\n"
            else:
                status_text += f"MACD: 🔴 BEARISH (MACD: {last_macd:.2f}, Signal: {last_signal:.2f})\n"
            
            if trend_status == "UPTREND":
                status_text += "Trade Bias: 🟢 Strong CALL opportunities\n"
            elif trend_status == "DOWNTREND":
                status_text += "Trade Bias: 🔴 Strong PUT opportunities\n"
            else:
                status_text += "Trade Bias: ⚠️ Sideways market - cautious trading\n"
                
            status_text += f"Current {index}: {df.iloc[-1]['close']:.2f}\n"
            status_text += "-"*40
            
            return status_text
        except Exception as e:
            print(f"Error printing indicators status: {str(e)}")
            return ""

    def get_user_positions(self):
        try:
            if not self.check_internet_connection():
                return []
                
            user_positions_response = self.groww.get_positions_for_user(
                segment=GrowwAPI.SEGMENT_FNO,
            )
            
            if not user_positions_response or 'positions' not in user_positions_response:
                return []
                
            positions = []
            for position in user_positions_response['positions']:
                trading_symbol = position.get('trading_symbol') or position.get('tradingSymbol', '')
                quantity = position.get('quantity', 0)
                
                if quantity > 0 and trading_symbol:
                    positions.append({
                        'symbol': trading_symbol,
                        'quantity': quantity,
                        'average_price': position.get('net_price', 0.0),
                        'segment': position.get('segment', 'FNO')
                    })
            return positions
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []

    def has_any_position(self, index):
        positions = self.get_user_positions()
        for position in positions:
            if position['symbol'].startswith(self.INDEX_CONFIG[index]["option_prefix"]):
                return True
        return False

    def should_enter_trade(self, position_type):
        # Skip trades after 2:30 PM
        if self.is_after_230():
            print("⏰ Skipping trade after 2:30 PM")
            return False
            
        # Check for imminent news events
        if self.is_news_event_imminent():
            print("⏰ High-impact news event imminent - skipping trade")
            return False
            
        # Check cooldown status
        if self.cooldown_active:
            remaining = self.get_cooldown_remaining()
            if remaining > 0:
                print(f"⏱️ Waiting for cooldown: {int(remaining)}s remaining")
                return False
            else:
                self.cooldown_active = False
                
        # Re-entry protocol
        if self.last_trade_direction == position_type:
            time_since_last = (datetime.now() - self.last_trade_time).total_seconds() / 60
            if time_since_last < 5:
                print(f"⚡ Same-direction re-entry allowed ({position_type})")
                return True
                
        if self.last_trade_time is None:
            return True
            
        # Minimum time between trades
        time_since_last_trade = (datetime.now() - self.last_trade_time).total_seconds() / 60
        return time_since_last_trade >= 5

    def is_news_event_imminent(self):
        """Check if high-impact news is within 30 minutes"""
        current_time = datetime.now()
        for event_time, event_name in self.news_schedule:
            if 0 < (event_time - current_time).total_seconds() < 1800:
                print(f"⚠️ High-impact news ({event_name}) within 30 minutes - avoiding trade")
                return True
        return False

    def print_position_details(self):
        positions = self.get_user_positions()
        if not positions:
            print("📭 No positions found")
            return
            
        print("\n" + "="*50)
        print(f"📊 CURRENT POSITIONS ({datetime.now().strftime('%H:%M:%S')})")
        print("="*50)
        for idx, pos in enumerate(positions, 1):
            print(f"{idx}. Symbol: {pos['symbol']}")
            print(f"   Quantity: {pos['quantity']}")
            print(f"   Avg Price: {pos['average_price']:.2f}")
            print(f"   Segment: {pos['segment']}")
            print("-"*40)
        print("="*50 + "\n")

    def detect_volatility_breakout(self, df):
        """Detect breakout from consolidation"""
        if len(df) < 6:
            return None
            
        recent_range = df['high'][-5:].max() - df['low'][-5:].min()
        current_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        
        if current_range > 1.8 * recent_range:
            if df['close'].iloc[-1] > df['high'][-6:-1].max():
                return "BULLISH_BREAKOUT"
            elif df['close'].iloc[-1] < df['low'][-6:-1].min():
                return "BEARISH_BREAKOUT"
        return None

    def calculate_position_size(self, index, symbol, volatility_params):
        base_size = self.INDEX_CONFIG[index]["lot_size"]
        account_risk = 0.01  # 1% of account per trade
        
        if self.account_value:
            option_price = self.get_ltp(symbol)
            if option_price <= 0:
                return base_size
                
            dollar_risk = self.account_value * account_risk
            position_size = min(
                int(dollar_risk / (option_price * volatility_params["stop_loss_multiplier"])),
                int(base_size * volatility_params["position_size"] * self.POSITION_SIZE_MULTIPLIER)
            )
            return max(1, position_size)  # Ensure minimum 1 lot
        return base_size

    def adjust_for_volatility(self, atr, current_price):
        volatility_ratio = atr / current_price
        
        if volatility_ratio < VOLATILITY_THRESHOLDS["LOW"]:
            return {
                "stop_loss_multiplier": 0.8,
                "target_multiplier": 0.9,
                "position_size": 0.7
            }
        elif volatility_ratio > VOLATILITY_THRESHOLDS["HIGH"]:
            return {
                "stop_loss_multiplier": 1.5,
                "target_multiplier": 1.8,
                "position_size": 1.2,
                "trail_multiplier": 1.3
            }
        else:
            return {
                "stop_loss_multiplier": 1.0,
                "target_multiplier": 1.0,
                "position_size": 1.0
            }

    def reconcile_positions(self):
        """Reconcile system state with actual positions from broker"""
        print("🔍 Reconciling positions...")
        # Check for unmanaged positions
        broker_positions = self.get_user_positions()
        managed_positions = [self.current_position['symbol']] if self.current_position else []
        
        for position in broker_positions:
            if position['symbol'] not in managed_positions:
                print(f"⚠️ Found unmanaged position: {position['symbol']}")
                self.setup_position_from_broker(position)
        
        # Verify stop loss for current position
        if self.current_position and not self.stop_loss_price:
            print("⚠️ Missing stop loss for current position. Setting up...")
            self.setup_stop_loss()
            
        # Check for positions that should be managed but aren't
        if self.current_position and not any(pos['symbol'] == self.current_position['symbol'] for pos in broker_positions):
            print(f"⚠️ Position {self.current_position['symbol']} not found in broker positions - resetting")
            self.current_position = None

    def setup_position_from_broker(self, position):
        """Setup position management for broker-found position"""
        # Infer position type from symbol
        position_type = "CALL" if position['symbol'].endswith('CE') else "PUT"
        
        self.current_position = {
            'index': self.get_index_from_symbol(position['symbol']),
            'symbol': position['symbol'],
            'quantity': position['quantity'],
            'entry_price': position['average_price'],
            'type': position_type,
            'entry_time': datetime.now() - timedelta(minutes=5)  # Approximate
        }
        self.position_entry_time = self.current_position['entry_time']
        self.setup_stop_loss()
        self.highest_price_since_entry = position['average_price']
        
        # Start management thread
        threading.Thread(target=self.manage_position, daemon=True).start()
        print(f"✅ Started managing broker-found position: {position['symbol']}")
        
    def get_index_from_symbol(self, symbol):
        """Extract index name from option symbol"""
        for index in self.INDEX_CONFIG:
            if symbol.startswith(self.INDEX_CONFIG[index]['option_prefix']):
                return index
        return "UNKNOWN"  # Fallback

    def setup_stop_loss(self):
        """Initialize stop loss parameters"""
        if not self.current_position:
            return
        
        self.stop_loss_price = self.current_position['entry_price'] - self.STOP_LOSS
        self.trailing_stop_activated = False
        print(f"🛡️ Stop loss set at {self.stop_loss_price:.2f} for {self.current_position['symbol']}")

    def main_trading_logic(self):
        if not self.active_trade_lock.acquire(blocking=False):
            return
            
        try:
            self.reset_trade_count_if_new_day()
            
            if self.trade_count >= MAX_TRADES_PER_DAY:
                print(f"⛔ Max trades reached for today ({self.trade_count}/{MAX_TRADES_PER_DAY})")
                return
            
            # Print position details every 15 seconds
            current_time = time.time()
            if current_time - self.last_position_print >= 15:
                self.print_position_details()
                self.last_position_print = current_time
            
            # Skip trading if any position exists in any index
            for index in self.indices:
                if self.has_any_position(index):
                    print(f"⛔ Existing position found in {index} - skipping trading cycle")
                    return
            
            if self.current_position or self.pending_orders:
                print("⏳ Existing position/pending orders - skipping trade")
                return
            
            for index in self.indices:
                try:
                    index_ltp = self.previous_close[index]
                    if not self.check_internet_connection():
                        continue
                        
                    ltp_response = self.groww.get_ltp(
                        segment=GrowwAPI.SEGMENT_CASH,
                        exchange_trading_symbols=self.INDEX_CONFIG[index]["cash_symbol"]
                    )
                    index_ltp = ltp_response.get(self.INDEX_CONFIG[index]["cash_symbol"], self.previous_close[index])
                except Exception as e:
                    print(f"Error getting {index} LTP: {str(e)}")
                
                if current_time - self.last_status_print >= 30:
                    status_text = self.print_indicator_status(index)
                    if status_text:
                        print(status_text)
                    self.last_status_print = current_time
                
                gap_percent = self.calculate_gap(index)
                
                market_status = "🟢 LIVE" if self.is_market_open() else "🔴 CLOSED"
                gap_status = f" | Gap: {gap_percent:.4f}%"
                print(f"\n{market_status} | {index}: {index_ltp:.2f}{gap_status}")
                
                if self.is_within_first_15_minutes() and gap_percent > 0.10:
                    print(f"⛔ Significant gap detected ({gap_percent:.4f}% > 0.10%). Skipping trade for {index}.")
                    continue
                
                if not self.is_market_open():
                    print("🔒 Market closed - no trading")
                    return
                
                new_candle_created = self.update_candle_data(index, index_ltp)
                
                expiry_date = self.get_nearest_expiry()
                strike_step = self.INDEX_CONFIG[index]["strike_step"]
                atm_strike = round(index_ltp / strike_step) * strike_step
                
                call_symbol = self.get_option_symbol(index, expiry_date, atm_strike, "CE")
                put_symbol = self.get_option_symbol(index, expiry_date, atm_strike, "PE")
                
                call_ltp, put_ltp = self.get_option_ltps(index, call_symbol, put_symbol)
                
                print(f"📅 {index} Expiry: {expiry_date} | ATM Strike: {atm_strike}")
                print(f"CALL: {call_symbol} @ {call_ltp:.2f}")
                print(f"PUT: {put_symbol} @ {put_ltp:.2f}")
                
                if not new_candle_created:
                    continue
                
                df = self.get_candle_df(index)
                min_data_points = max(SUPERTREND_PERIOD1, SUPERTREND_PERIOD2, MACD_SLOW_PERIOD) + 5
                if len(df) < min_data_points:
                    print(f"⚠️ Insufficient data for {index} ({len(df)} candles, need {min_data_points})")
                    continue
                
                try:
                    df['st1'] = self.calculate_supertrend(df, SUPERTREND_PERIOD1, SUPERTREND_MULTIPLIER1)
                    df['st2'] = self.calculate_supertrend(df, SUPERTREND_PERIOD2, SUPERTREND_MULTIPLIER2)
                    
                    macd, signal, _ = self.calculate_macd(df)
                    ema_21 = self.calculate_ema(df, 21)
                    
                    # Calculate ATR for dynamic targets
                    atr = self.calculate_atr(df, self.ATR_PERIOD).iloc[-1]
                    
                    # Adjust parameters for volatility
                    volatility_params = self.adjust_for_volatility(atr, index_ltp)
                    self.PROFIT_TARGET = int(self.BASE_PROFIT_TARGET * volatility_params["target_multiplier"])
                    self.STOP_LOSS = int(10 * volatility_params["stop_loss_multiplier"])  # base SL is 10
                    
                    # Detect market state and adjust strategy
                    market_state = self.market_state.detect_state(index, df, atr, index_ltp)
                    self.market_state.handle_state(index, market_state)
                    print(f"📊 {index} Market State: {market_state} | Strategy: {self.ENTRY_STRATEGY}")
                    
                    # Calculate ADX for market trend
                    adx, plus_di, minus_di = self.calculate_adx(df, self.ADX_PERIOD)
                    last_adx = adx.iloc[-1] if adx is not None else 0
                    last_plus_di = plus_di.iloc[-1] if plus_di is not None else 0
                    last_minus_di = minus_di.iloc[-1] if minus_di is not None else 0
                    
                    # Determine market trend
                    if last_adx > self.MARKET_TREND_THRESHOLD:
                        if last_plus_di > last_minus_di:
                            trend_status = "UPTREND"
                        else:
                            trend_status = "DOWNTREND"
                    else:
                        trend_status = "SIDEWAYS"
                    
                    self.indicator_status[index]["trend"] = trend_status
                    self.indicator_status[index]["adx"] = last_adx
                    
                    print(f"\n📊 {index} Market Status:")
                    print(f"Market Trend: {trend_status} (ADX: {last_adx:.2f}, +DI: {last_plus_di:.2f}, -DI: {last_minus_di:.2f})")
                    
                    last_row = df.iloc[-1]
                    st1_green = last_row['st1']
                    st2_green = last_row['st2']
                    macd_value = last_row.get('macd', 0)
                    signal_value = last_row.get('signal', 0)
                    macd_bullish = macd_value > signal_value
                    price_above_ema = last_row['close'] > ema_21.iloc[-1]
                    
                    # Check for volatility breakout
                    breakout_signal = self.detect_volatility_breakout(df)
                    if breakout_signal and self.ENTRY_STRATEGY in ["BREAKOUT", "TREND_FOLLOWING"]:
                        print(f"🚀 Volatility breakout detected: {breakout_signal}")
                        if breakout_signal == "BULLISH_BREAKOUT":
                            if self.should_enter_trade("CALL"):
                                print(f"\n🚀 {index} VOLATILITY BREAKOUT - CALL Entry Conditions Met!")
                                call_ltp, _ = self.get_option_ltps(index, call_symbol, put_symbol)
                                if call_ltp > 0:
                                    self.place_order(index, call_symbol, "CALL", volatility_params)
                        else:
                            if self.should_enter_trade("PUT"):
                                print(f"\n🚀 {index} VOLATILITY BREAKOUT - PUT Entry Conditions Met!")
                                _, put_ltp = self.get_option_ltps(index, call_symbol, put_symbol)
                                if put_ltp > 0:
                                    self.place_order(index, put_symbol, "PUT", volatility_params)
                        continue
                    
                    # Strong trend entry - only requires SuperTrend confirmation
                    if trend_status == "UPTREND" and st1_green:
                        if self.should_enter_trade("CALL"):
                            print(f"\n🚀 {index} STRONG UPTREND - CALL Entry Conditions Met!")
                            call_ltp, _ = self.get_option_ltps(index, call_symbol, put_symbol)
                            if call_ltp > 0:
                                self.place_order(index, call_symbol, "CALL", volatility_params)
                                
                    elif trend_status == "DOWNTREND" and not st1_green:
                        if self.should_enter_trade("PUT"):
                            print(f"\n🚀 {index} STRONG DOWNTREND - PUT Entry Conditions Met!")
                            _, put_ltp = self.get_option_ltps(index, call_symbol, put_symbol)
                            if put_ltp > 0:
                                self.place_order(index, put_symbol, "PUT", volatility_params)

                    # Regular entry - requires both SuperTrends and MACD confirmation
                    elif st1_green and st2_green and macd_bullish and price_above_ema:
                        if self.should_enter_trade("CALL"):
                            print(f"\n🚀 {index} CALL Entry Conditions Met!")
                            call_ltp, _ = self.get_option_ltps(index, call_symbol, put_symbol)
                            if call_ltp > 0:
                                self.place_order(index, call_symbol, "CALL", volatility_params)
                                
                    elif not st1_green and not st2_green and not macd_bullish and not price_above_ema:
                        if self.should_enter_trade("PUT"):
                            print(f"\n🚀 {index} PUT Entry Conditions Met!")
                            _, put_ltp = self.get_option_ltps(index, call_symbol, put_symbol)
                            if put_ltp > 0:
                                self.place_order(index, put_symbol, "PUT", volatility_params)
                    else:
                        print(f"➖ {index} No clear trade signal - waiting for next opportunity")
                except Exception as e:
                    print(f"Error calculating indicators for {index}: {str(e)}")
                    continue
        finally:
            self.active_trade_lock.release()

    def place_order(self, index, symbol, position_type, volatility_params):
        try:
            # Calculate position size
            quantity = self.calculate_position_size(index, symbol, volatility_params)
            print(f"📤 Placing MARKET order for {index}: {position_type} {symbol} (Qty: {quantity})")
            place_order_response = self.groww.place_order(
                trading_symbol=symbol,
                quantity=quantity,
                price=0,  # Market order
                validity=GrowwAPI.VALIDITY_DAY,
                exchange=GrowwAPI.EXCHANGE_NSE,
                segment=GrowwAPI.SEGMENT_FNO,
                product=GrowwAPI.PRODUCT_NRML,
                order_type=GrowwAPI.ORDER_TYPE_MARKET,
                transaction_type=GrowwAPI.TRANSACTION_TYPE_BUY,
            )
            print(place_order_response)
            
            if place_order_response.get('order_id'):
                order_id = place_order_response['order_id']
                self.pending_orders[order_id] = {
                    'placed_time': datetime.now(),
                    'index': index,
                    'symbol': symbol,
                    'quantity': quantity,
                    'position_type': position_type,
                    'type': 'ENTRY',
                    'status': 'OPEN'
                }
                print(f"✅ Order placed for {index}! ID: {order_id}")
                self.last_trade_time = datetime.now()
            else:
                print(f"⚠️ Order placement failed for {index}")
        except Exception as e:
            print(f"Order placement error for {index}: {str(e)}")

    def start_trading(self):
        self.running = True
        print("\n" + "="*50)
        print(f"🚀 Starting Volatility-Adaptive Multi-Index Trader for {self.user_id}")
        print("="*50)
        print(f"Trading Indices: {', '.join(self.indices)}")
        print(f"Timeframe: 3-minute candles")
        print(f"Strategy: SuperTrend + MACD + ADX with Volatility Adaptation")
        print(f"Risk Management: Layered exit system with priority-based triggers")
        print(f"Exit Priority: 1. Stop Loss 2. SuperTrend Reversal 3. Partial Profits 4. Time")
        print(f"Max trades/day: {MAX_TRADES_PER_DAY}")
        print("-"*50)
        
        self.print_position_details()
        print("Starting main loop...")
        
        last_reconcile = time.time()
        
        while self.running:
            try:
                if self.is_market_open():
                    # Reconcile every 5 minutes
                    if time.time() - last_reconcile > 300:
                        self.reconcile_positions()
                        last_reconcile = time.time()
                    
                    self.monitor_pending_orders()
                    if not self.current_position and not self.pending_orders:
                        self.main_trading_logic()
                else:
                    print("🔒 Market closed - trading paused")
                    time.sleep(60)
                    
                time.sleep(15)
            except KeyboardInterrupt:
                print("\nStopping trader...")
                break
            except Exception as e:
                print(f"Main loop error: {str(e)}")
                time.sleep(30)
                
    def stop_trading(self):
        self.running = False

class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Volatility-Adaptive Options Trader")
        self.root.geometry("1200x700")  # Adjusted height for new layout
        self.root.configure(bg='#0a0a2a')
        self.user_id = None
        self.api_key = None
        self.api_secret = None
        self.trader = None
        self.timer_running = False
        self.daily_api_valid = False
        self.selected_indices = ["NIFTY", "BANKNIFTY", "FINNIFTY"]
        
        self.cooldown_var = tk.StringVar()
        self.cooldown_var.set("Cooldown: Ready")
        self.volatility_var = tk.StringVar()
        self.volatility_var.set("Volatility: MEDIUM")
        
        self.create_widgets()
        self.authenticate_user()
    
    def create_widgets(self):
        self.root.option_add("*Font", "Arial 10")
        self.root.option_add("*Background", "#0a0a2a")
        self.root.option_add("*Foreground", "white")
        
        # Main container frame
        main_frame = tk.Frame(self.root, bg="#0a0a2a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel for controls (40% width)
        left_panel = tk.Frame(main_frame, bg="#0a0a2a", width=400)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
        
        # Right panel for trading log (60% width)
        right_panel = tk.Frame(main_frame, bg="#0a0a2a")
        right_panel.pack(side="right", fill="both", expand=True)
        
        # ========= LEFT PANEL =========
        # Header
        header = tk.Frame(left_panel, bg="#1a1a4a")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Volatility-Adaptive Options Trader", 
                font=("Georgia", 16, "bold"), bg="#1a1a4a", fg="#FFD700").pack(pady=10)
        
        # Index selection frame
        index_frame = tk.LabelFrame(left_panel, text="Select Indices to Trade",
                                  bg="#0a0a2a", fg="white", font=("Arial", 10, "bold"))
        index_frame.pack(fill="x", padx=5, pady=5)
        
        self.index_vars = {
            "NIFTY": tk.BooleanVar(value=True),
            "BANKNIFTY": tk.BooleanVar(value=True),
            "FINNIFTY": tk.BooleanVar(value=True)
        }
        
        tk.Checkbutton(index_frame, text="NIFTY", variable=self.index_vars["NIFTY"], 
                      bg="#0a0a2a", fg="white", selectcolor="#1a1a4a").pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(index_frame, text="BANKNIFTY", variable=self.index_vars["BANKNIFTY"], 
                      bg="#0a0a2a", fg="white", selectcolor="#1a1a4a").pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(index_frame, text="FINNIFTY", variable=self.index_vars["FINNIFTY"], 
                      bg="#0a0a2a", fg="white", selectcolor="#1a1a4a").pack(side=tk.LEFT, padx=10)
        
        # Status frame
        status_frame = tk.LabelFrame(left_panel, text="System Status", 
                                   bg="#0a0a2a", fg="white", font=("Arial", 10, "bold"))
        status_frame.pack(fill="x", padx=5, pady=5)
        
        # Status grid
        status_grid = tk.Frame(status_frame, bg="#0a0a2a")
        status_grid.pack(fill="x", padx=5, pady=5)
        
        tk.Label(status_grid, text="Authentication:", anchor="w", bg="#0a0a2a").grid(row=0, column=0, sticky="w", pady=2)
        self.auth_status = tk.Label(status_grid, text="🔒 Locked", fg="red", bg="#0a0a2a")
        self.auth_status.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(status_grid, text="User ID:", anchor="w", bg="#0a0a2a").grid(row=1, column=0, sticky="w", pady=2)
        self.user_status = tk.Label(status_grid, text="Not set", fg="yellow", bg="#0a0a2a")
        self.user_status.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(status_grid, text="API Status:", anchor="w", bg="#0a0a2a").grid(row=2, column=0, sticky="w", pady=2)
        self.api_status = tk.Label(status_grid, text="Not configured", fg="orange", bg="#0a0a2a")
        self.api_status.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(status_grid, text="Active Indices:", anchor="w", bg="#0a0a2a").grid(row=3, column=0, sticky="w", pady=2)
        self.indices_status = tk.Label(status_grid, text="None", fg="cyan", bg="#0a0a2a")
        self.indices_status.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Trading state frame
        trading_state_frame = tk.LabelFrame(left_panel, text="Trading State", 
                                          bg="#0a0a2a", fg="white", font=("Arial", 10, "bold"))
        trading_state_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(trading_state_frame, text="Cooldown:", bg="#0a0a2a").pack(anchor="w", padx=10, pady=2)
        cooldown_label = tk.Label(trading_state_frame, textvariable=self.cooldown_var, 
                                 fg="green", bg="#0a0a2a", font=("Arial", 9, "bold"))
        cooldown_label.pack(anchor="w", padx=10, pady=2)
        
        tk.Label(trading_state_frame, text="Volatility Regime:", bg="#0a0a2a").pack(anchor="w", padx=10, pady=2)
        volatility_label = tk.Label(trading_state_frame, textvariable=self.volatility_var, 
                                 fg="#FF9900", bg="#0a0a2a", font=("Arial", 9, "bold"))
        volatility_label.pack(anchor="w", padx=10, pady=2)
        
        # Buttons frame
        button_frame = tk.Frame(left_panel, bg="#0a0a2a")
        button_frame.pack(fill="x", padx=5, pady=15)
        
        # Configure button styles
        button_style = {"font": ("Arial", 10, "bold"), "height": 2, "width": 15}
        
        self.trade_btn = tk.Button(button_frame, text="Start Trading", 
                                  command=self.handle_trade_setup,
                                  bg="#2a5a2a", fg="white", **button_style)
        self.trade_btn.pack(side=tk.LEFT, padx=5)
        
        reconcile_btn = tk.Button(button_frame, text="Reconcile Positions", 
                                 command=self.manual_reconcile,
                                 bg="#5a5a0a", fg="white", **button_style)
        reconcile_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(button_frame, text="Exit", command=self.root.destroy,
                           bg="#5a0a0a", fg="white", **button_style)
        exit_btn.pack(side=tk.RIGHT, padx=5)
        
        # ========= RIGHT PANEL =========
        log_frame = tk.LabelFrame(right_panel, text="Trading Log", 
                                bg="#0a0a2a", fg="white", font=("Arial", 10, "bold"))
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, bg="#000022", fg="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Redirect stdout and stderr to the log text widget
        import sys
        sys.stdout = TextRedirector(self.log_text, "stdout")
        sys.stderr = TextRedirector(self.log_text, "stderr")
    
    def authenticate_user(self):
        password = simpledialog.askstring("Authentication", 
                                         "Enter application password:", 
                                         show='*')
        if not password or password != USER_PASSWORD:
            messagebox.showerror("Access Denied", "Invalid application password")
            self.root.destroy()
            return
        
        self.auth_status.config(text="✅ Authenticated", fg="green")
        
        user_id = simpledialog.askstring("User Setup", 
                                        "Enter your user ID (email/username):")
        if not user_id:
            messagebox.showerror("Error", "User ID is required")
            self.root.destroy()
            return
            
        self.user_id = user_id
        self.user_status.config(text=f"👤 {user_id}")
        self.configure_api()
    
    def configure_api(self):
        storage = SecureStorage(USER_PASSWORD, self.user_id)
        self.api_key, self.api_secret = storage.load_credentials()
        
        if self.api_key and self.api_secret:
            self.api_status.config(text="API: Valid", fg="green")
            self.daily_api_valid = True
            self.trade_btn.config(state=tk.NORMAL, bg="#2a7a2a")
        else:
            self.api_status.config(text="API: Needs Setup", fg="orange")
            self.daily_api_valid = False
            self.trade_btn.config(state=tk.NORMAL, bg="#5a5a0a")
    
    def get_daily_credentials(self):
        api_key = simpledialog.askstring("API Setup", "Enter Groww API Key:")
        if not api_key:
            return False
            
        api_secret = simpledialog.askstring("API Setup", 
                                           "Enter Groww API Secret:", 
                                           show='*')
        if not api_secret:
            return False
            
        storage = SecureStorage(USER_PASSWORD, self.user_id)
        storage.save_credentials(api_key, api_secret)
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_status.config(text="API: Valid", fg="green")
        self.daily_api_valid = True
        return True
    
    def handle_trade_setup(self):
        # Get selected indices
        self.selected_indices = [index for index, var in self.index_vars.items() if var.get()]
        if not self.selected_indices:
            messagebox.showerror("Error", "Please select at least one index to trade")
            return
            
        self.indices_status.config(text=", ".join(self.selected_indices))
        
        if not self.daily_api_valid:
            if not self.get_daily_credentials():
                return
        
        if self.trader and self.trader.running:
            messagebox.showinfo("Trading Status", "Trading is already running!")
            return
            
        if not self.api_key or not self.api_secret:
            messagebox.showerror("Error", "API credentials missing")
            return
            
        self.trader = IndexOptionsTrader(self.api_key, self.api_secret, self.user_id, self.selected_indices)
        trading_thread = threading.Thread(target=self.trader.start_trading, daemon=True)
        trading_thread.start()
        self.trade_btn.config(text="Stop Trading", bg="#7a2a2a", command=self.stop_trading)
        messagebox.showinfo("Trade Setup", "Trading started successfully!")
    
    def manual_reconcile(self):
        if self.trader:
            self.trader.reconcile_positions()
            messagebox.showinfo("Reconcile", "Position reconciliation completed!")
    
    def stop_trading(self):
        if self.trader:
            self.trader.stop_trading()
            self.trade_btn.config(text="Start Trading", bg="#2a7a2a", command=self.handle_trade_setup)
            messagebox.showinfo("Trade Setup", "Trading stopped successfully!")
    
    def update_status_display(self):
        if not self.trader:
            self.cooldown_var.set("Cooldown: N/A")
            self.volatility_var.set("Volatility: N/A")
            return
            
        # Update cooldown status
        remaining = self.trader.get_cooldown_remaining()
        if remaining > 0:
            self.cooldown_var.set(f"⏱️ Cooldown: {int(remaining)}s remaining")
        else:
            self.cooldown_var.set("✅ Cooldown: Ready")
            
        # Update volatility status
        self.volatility_var.set(f"Volatility: {self.trader.volatility_regime}")

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
    
    def write(self, string):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, string, (self.tag,))
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)
    
    def flush(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()
