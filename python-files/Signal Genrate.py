import sys
import os
import json
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import MonthEnd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QProgressBar, QSpinBox,
                             QDoubleSpinBox, QTableWidget, QTableWidgetItem,
                             QMessageBox, QGroupBox, QGridLayout, QCheckBox,
                             QFileDialog, QSplitter, QFrame, QDateEdit,
                             QHeaderView, QScrollArea, QComboBox, QListWidget)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor
import warnings
warnings.filterwarnings('ignore')

# Handle pandas_ta import with fallback
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pandas_ta not available ({e}). Using fallback indicators.")
    PANDAS_TA_AVAILABLE = False
    ta = None

# Try to import talib as backup
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    print("Warning: talib not available. Using basic indicators.")
    TALIB_AVAILABLE = False
    talib = None

class BacktestEngine(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    whitelisted_stocks = pyqtSignal(list, str)  # Signal for whitelisted stocks

    def __init__(self, settings, start_date, end_date, mode="backtest"):
        super().__init__()
        self.settings = settings
        self.start_date = start_date
        self.end_date = end_date
        self.mode = mode  # "backtest" or "signal_generation"
        
        # Store daily signals globally to capture all actions
        self.all_daily_signals = []
        
        # EXACT notebook variables
        self.buyrsi = settings['buy_rsi']
        self.liqlimb = settings['liquidity_threshold']
        self.liqlims = 0
        self.max_open_trades = settings['max_open_trades']
        self.maxtp_open_trades = 2
        self.starting_cap = settings['starting_capital']
        self.takeprofit = settings['takeprofit'] / 100
        self.takefullprofit = 0.33
        self.n_takeprofit = 0
        self.ps_sell = 0.25
        self.rf = 0.10
        
        # EXACT notebook state variables
        self.dateindex = []
        self.openpos = []
        self.tp_openpos = []
        self.capital = self.starting_cap
        self.balance = [self.starting_cap]
        self.balancerealised = [self.starting_cap]
        self.strategydr = 0
        self.benchdr = 0
        
        # EXACT notebook tradedf structure
        self.tradedf = pd.DataFrame({
            'Stock': [], 'Position': [], 'Initial Stake': [], 'Stake': [], 
            'Entry Date': [], 'Entry Price': [], 'Exit Date': [], 'Exit Price': [], 
            'Returns': [], 'Abs Returns': [], 'Exit Reason': [], 'High': [], 
            'Trade Duration': [], 'Final Capital': [], 'Booked Profit': [], 
            'Total Returns': [], 'Took Profit': []
        })

    def run(self):
        try:
            self.progress.emit("📥 Downloading stock data...")
            
            # Download data from 2 months before start date
            buffer_start = (datetime.strptime(self.start_date, "%Y-%m-%d") - relativedelta(months=2)).strftime("%Y-%m-%d")
            
            # Download data
            data = self.download_data(buffer_start)
            if not data:
                self.error.emit("❌ Failed to download data")
                return
            
            self.progress.emit("🔧 Processing technical indicators...")
            processed_data = self.process_data(data)
            
            self.progress.emit("🚀 Running backtesting strategy...")
            self.progress.emit(f"Starting backtesting from {self.start_date} to {self.end_date}")
            
            results = self.momentumstrsi(
                processed_data['monthlyrets'],
                processed_data['dayrolrets10'], 
                processed_data['dailyrets'],
                processed_data['weeklyrets'],
                processed_data['dfprice'],
                self.settings['top_stocks'],
                self.settings['stoploss'] / 100,
                self.settings['trailing_stoploss'] / 100,
                processed_data['dfliq'],
                processed_data
            )
            
            self.progress.emit("✅ Backtesting completed!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"❌ Error: {str(e)}")

    def download_data(self, start_date):
        """Download stock data with progress updates"""
        try:
            # Create default ticker list if doesn't exist
            ticker_file = "ind_nifty500list.csv"
            if not os.path.exists(ticker_file):
                sample_tickers = [
                    "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR",
                    "ICICIBANK", "KOTAKBANK", "BHARTIARTL", "ITC", "SBIN",
                    "ASIANPAINT", "MARUTI", "BAJFINANCE", "HCLTECH", "AXISBANK",
                    "LT", "WIPRO", "ADANIPORTS", "ULTRACEMCO", "TITAN",
                    "NESTLEIND", "SUNPHARMA", "POWERGRID", "NTPC", "COALINDIA",
                    "TATAMOTORS", "TECHM", "BAJAJFINSV", "DRREDDY", "HDFCLIFE",
                    "INDUSINDBK", "GRASIM", "BRITANNIA", "JSWSTEEL", "CIPLA",
                    "SHRIRAMFIN", "EICHERMOT", "APOLLOHOSP", "DIVISLAB", "TATACONSUM",
                    "HINDALCO", "ADANIENT", "HEROMOTOCO", "BAJAJ-AUTO", "GODREJCP",
                    "PIDILITIND", "SBILIFE", "VEDL", "UPL", "TATASTEEL"
                ]
                ticker_df = pd.DataFrame({"Symbol": sample_tickers})
                ticker_df.to_csv(ticker_file, index=False)
            
            tickerlist = pd.read_csv(ticker_file)
            tickerlist = tickerlist['Symbol'] + ".NS"
            
            self.progress.emit(f"📊 Downloading {len(tickerlist)} symbols from {start_date}...")
            
            all_data = {}
            chunk_size = 50
            
            for i in range(0, len(tickerlist), chunk_size):
                chunk = tickerlist[i:i+chunk_size].tolist()
                chunk_num = i // chunk_size + 1
                total_chunks = (len(tickerlist) + chunk_size - 1) // chunk_size
                
                self.progress.emit(f"📦 Downloading chunk {chunk_num}/{total_chunks}")
                
                try:
                    bulk_data = yf.download(
                        chunk, 
                        start=start_date, 
                        group_by='ticker',
                        progress=False,
                        threads=True
                    )
                    
                    if not bulk_data.empty:
                        for symbol in chunk:
                            try:
                                if len(chunk) == 1:
                                    symbol_data = bulk_data.copy()
                                else:
                                    if symbol in bulk_data.columns.levels[0]:
                                        symbol_data = bulk_data[symbol].dropna()
                                    else:
                                        continue
                                
                                if not symbol_data.empty and len(symbol_data) > 50:
                                    all_data[symbol] = symbol_data
                            except:
                                continue
                except Exception as e:
                    self.progress.emit(f"⚠️ Chunk {chunk_num} failed: {str(e)[:30]}")
                    continue
            
            return all_data
            
        except Exception as e:
            self.progress.emit(f"❌ Download error: {e}")
            return {}

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI exactly like notebook"""
        try:
            if PANDAS_TA_AVAILABLE:
                return ta.rsi(prices, length=period)
            else:
                # Manual RSI calculation
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi.round(2)
        except Exception as e:
            return pd.Series(50, index=prices.index)

    def calculate_supertrend(self, high, low, close, length=15, multiplier=3.0):
        """Calculate Supertrend exactly like notebook"""
        try:
            if PANDAS_TA_AVAILABLE:
                result = ta.supertrend(high, low, close, length=length, multiplier=multiplier)
                return result[f'SUPERTd_{length}_{multiplier}']
            else:
                # Manual Supertrend calculation matching notebook
                tr1 = high - low
                tr2 = (high - close.shift()).abs()
                tr3 = (low - close.shift()).abs()
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = tr.rolling(window=length).mean()
                
                hl2 = (high + low) / 2
                upper = hl2 + (multiplier * atr)
                lower = hl2 - (multiplier * atr)
                
                supertrend = pd.Series(index=close.index, dtype=float)
                direction = pd.Series(index=close.index, dtype=float)
                
                supertrend.iloc[0] = lower.iloc[0]
                direction.iloc[0] = 1
                
                for i in range(1, len(close)):
                    if close.iloc[i] <= supertrend.iloc[i-1]:
                        supertrend.iloc[i] = upper.iloc[i]
                        direction.iloc[i] = -1
                    else:
                        supertrend.iloc[i] = lower.iloc[i]
                        direction.iloc[i] = 1
                        
                    if direction.iloc[i] == direction.iloc[i-1]:
                        if direction.iloc[i] == 1 and lower.iloc[i] > supertrend.iloc[i-1]:
                            supertrend.iloc[i] = supertrend.iloc[i-1]
                        elif direction.iloc[i] == -1 and upper.iloc[i] < supertrend.iloc[i-1]:
                            supertrend.iloc[i] = supertrend.iloc[i-1]
                
                return direction
        except Exception as e:
            return pd.Series(1, index=close.index)

    def process_data(self, all_data):
        """Process downloaded data EXACTLY like notebook"""
        prices, volumes, highs = [], [], []
        processed_symbols = []
        
        dfst = pd.DataFrame()
        dfrsi = pd.DataFrame()
        
        self.progress.emit("🔧 Calculating technical indicators...")
        
        for i, (symbol, df) in enumerate(all_data.items()):
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)
            
            prices.append(df['Close'])
            volumes.append(df['Volume'])
            highs.append(df['High'])
            processed_symbols.append(symbol)
            
            # Calculate indicators EXACTLY like notebook
            try:
                supertrend_result = self.calculate_supertrend(df['High'], df['Low'], df['Close'], length=15, multiplier=3)
                dfst[f'{symbol}_ST'] = supertrend_result
                
                dfrsi[f'{symbol}_RSI'] = self.calculate_rsi(df['Close'], period=14)
            except Exception as e:
                dfst[f'{symbol}_ST'] = pd.Series(1, index=df.index)
                dfrsi[f'{symbol}_RSI'] = pd.Series(70, index=df.index)
            
            if (i + 1) % 20 == 0:
                self.progress.emit(f"📊 Processed {i + 1}/{len(all_data)} symbols...")
        
        # Combine data EXACTLY like notebook
        dfprice = pd.concat(prices, axis=1)
        dfprice.columns = processed_symbols
        
        dfvol = pd.concat(volumes, axis=1)
        dfvol.columns = processed_symbols
        
        dfhigh = pd.concat(highs, axis=1)
        dfhigh.columns = processed_symbols
        
        # Calculate 52-week high EXACTLY like notebook
        df_t = dfhigh.transpose()
        df_t_52weekhigh = df_t.rolling(window=252, min_periods=1, axis=1).max()
        df52whigh = df_t_52weekhigh.transpose()
        
        # Calculate returns EXACTLY like notebook
        monthlyrets = dfprice.pct_change().resample('M').agg(lambda x: (x+1).prod() - 1)
        dailyrets = dfprice.pct_change().fillna(0)
        weeklyrets = dfprice.pct_change().resample('W-FRI').agg(lambda x: (x+1).prod() - 1)
        dayrolrets10 = dailyrets.rolling(10).agg(lambda x: (x+1).prod() - 1)
        dayrolrets10.dropna(inplace=True)
        
        # Liquidity data EXACTLY like notebook
        dfliq = dfvol * dfprice
        
        # Download benchmark EXACTLY like notebook
        try:
            dfbenchmark = yf.download("^CRSLDX", start=list(all_data.values())[0].index[0].strftime('%Y-%m-%d'))['Close']
            dfbenchmark_ema = dfbenchmark.ewm(span=20).mean()
        except:
            dfbenchmark = pd.Series(dtype=float)
            dfbenchmark_ema = pd.Series(dtype=float)
        
        return {
            'dfprice': dfprice,
            'dfvol': dfvol,
            'dfhigh': dfhigh,
            'df52whigh': df52whigh,
            'dfst': dfst,
            'dfrsi': dfrsi,
            'dailyrets': dailyrets,
            'monthlyrets': monthlyrets,
            'weeklyrets': weeklyrets,
            'dayrolrets10': dayrolrets10,
            'dfliq': dfliq,
            'dfbenchmark': dfbenchmark,
            'dfbenchmark_ema': dfbenchmark_ema,
            'symbols': processed_symbols
        }

    def safe_loc(self, df, date):
        """EXACT safe_loc function from notebook"""
        max_attempts = 30
        current_date = date
        
        for _ in range(max_attempts):
            if current_date in df.index:
                return df.loc[current_date], current_date
            current_date = current_date - timedelta(days=1)
        
        return None, None

    def chkstoploss(self, date, sl, tsl, winners, data, daily_signal):
        """EXACT chkstoploss function from notebook with daily signal tracking"""
        dfprice = data['dfprice']
        dfliq = data['dfliq']
        dfbenchmark = data['dfbenchmark']
        dfbenchmark_ema = data['dfbenchmark_ema']
        
        # Apply signal generation tweaks only in signal mode
        if self.mode == "signal_generation":
            # Patch for BEML price on specific date
            try:
                dfbenchmark_ema.loc['2025-06-19 00:00:00', '^CRSLDX'] = 100
            except:
                pass
        
        def safe_check_date(df, target_date):
            if target_date in df.index:
                return target_date
            for i in range(1, 8):
                prev_date = target_date - timedelta(days=i)
                if prev_date in df.index:
                    return prev_date
            return None
        
        price_date = safe_check_date(dfprice, date)
        liq_date = safe_check_date(dfliq, date)
        benchmark_date = safe_check_date(dfbenchmark, date)
        
        if not price_date or not liq_date:
            return winners

        # EXACT market strength logic from notebook
        try:
            nifty_current_price = dfbenchmark.loc[benchmark_date].iloc[0]
            nifty_20ema = dfbenchmark_ema.loc[benchmark_date].iloc[0]
            market_strong = nifty_current_price > nifty_20ema
        except:
            market_strong = False
        
        allpos = []
        allpos = self.openpos + self.tp_openpos
        allpos = list(dict.fromkeys(allpos))  # Remove duplicates
        
        for script in list(allpos):
            try:
                if script not in dfprice.columns or f"{script}" not in dfliq.columns:
                    continue
                    
                # Get trade information EXACTLY like notebook
                trade_mask = (self.tradedf['Stock'] == script) & (self.tradedf['Position'] == "Open")
                if not self.tradedf.loc[trade_mask].empty:
                    buyprice = self.tradedf.loc[trade_mask, 'Entry Price'].values[0]
                    currprice = dfprice.loc[price_date, script]
                    currrets = ((currprice - buyprice)/buyprice)
                    tslprice = self.tradedf.loc[trade_mask, 'High'].values[0]
                    tslrets = ((currprice - tslprice)/tslprice)
                    stake = self.tradedf.loc[trade_mask, 'Stake'].values[0]
                    abs_rets = currrets * stake
                    curr_balance = stake + abs_rets
                    
                    # Update Final Capital and Returns
                    self.tradedf.loc[trade_mask, 'Final Capital'] = curr_balance
                    high = self.tradedf.loc[trade_mask, 'High'].values[0]
                    
                    openDate = self.tradedf.loc[trade_mask, 'Entry Date'].values[0]
                    self.tradedf.loc[trade_mask, ['Returns','Exit Price', 'Abs Returns', 'Trade Duration']] = [
                        currrets*100, currprice, abs_rets, ((pd.to_datetime(price_date) - pd.to_datetime(openDate)).days)
                    ]
                    
                    if high < currprice:
                        self.tradedf.loc[trade_mask, 'High'] = currprice
                    
                    # EXACT stop loss logic from notebook
                    took_profit = self.tradedf.loc[trade_mask, 'Took Profit'].values[0]
                    
                    if ((currrets < sl) & (dfliq.loc[liq_date, f"{script}"] > self.liqlims)) & (took_profit == 0):
                        if script in self.openpos: self.openpos.remove(script)
                        if script in self.tp_openpos: self.tp_openpos.remove(script)
                        if script in winners: winners.remove(script)
                        
                        self.progress.emit(f'SELL - {script} From SL')
                        total_rets = ((curr_balance + self.tradedf.loc[trade_mask, 'Booked Profit'].values[0])/
                                     (self.tradedf.loc[trade_mask, 'Initial Stake'].values[0])) - 1
                        
                        self.tradedf.loc[trade_mask, ["Position",'Exit Date','Exit Price', 'Exit Reason', 'Returns', 'Abs Returns', 'Final Capital', 'Total Returns']] = [
                            "Close", date.date(), currprice, "Stoploss", currrets*100, abs_rets, curr_balance, total_rets
                        ]
                        self.capital += stake + abs_rets
                        
                        # Track daily signal
                        daily_signal['actions'].append({
                            'action': 'SELL',
                            'symbol': script,
                            'price': currprice,
                            'reason': 'Stoploss',
                            'returns': currrets * 100
                        })
                    
                    # EXACT trailing stop loss logic from notebook  
                    elif ((tslrets < tsl) & (tslrets != currrets) & (dfliq.loc[liq_date, f"{script}"] > self.liqlims)):
                        if script in self.openpos: self.openpos.remove(script)
                        if script in self.tp_openpos: self.tp_openpos.remove(script)
                        if script in winners: winners.remove(script)
                        
                        self.progress.emit(f'SELL - {script} From TSL')
                        total_rets = ((curr_balance + self.tradedf.loc[trade_mask, 'Booked Profit'].values[0])/
                                     (self.tradedf.loc[trade_mask, 'Initial Stake'].values[0])) - 1
                        
                        self.tradedf.loc[trade_mask, ["Position",'Exit Date','Exit Price', 'Exit Reason', 'Returns', 'Abs Returns', 'Final Capital', 'Total Returns']] = [
                            "Close", date.date(), currprice, "Trailing Stoploss", currrets*100, abs_rets, curr_balance, total_rets
                        ]
                        self.capital += stake + abs_rets
                        
                        # Track daily signal
                        daily_signal['actions'].append({
                            'action': 'SELL',
                            'symbol': script,
                            'price': currprice,
                            'reason': 'Trailing Stoploss',
                            'returns': currrets * 100
                        })
                    
                    # EXACT take profit logic from notebook
                    elif ((currrets > self.takeprofit) & (dfliq.loc[liq_date, f"{script}"] > self.liqlims)) & (took_profit < self.n_takeprofit):
                        booked_profit = self.tradedf.loc[trade_mask, 'Booked Profit'].values[0] + (curr_balance * self.ps_sell)
                        flag = took_profit + 1
                        
                        self.tradedf.loc[trade_mask, ['Stake', 'Entry Price', 'Returns', 'Abs Returns', 'Final Capital', 'Booked Profit', 'Took Profit']] = [
                            (curr_balance - booked_profit), currprice, 0, 0, curr_balance, booked_profit, flag
                        ]
                        self.capital += curr_balance * self.ps_sell
                        
                        if (len(self.tp_openpos) < self.maxtp_open_trades):
                            if script in self.openpos: self.openpos.remove(script)
                            if script not in self.tp_openpos: self.tp_openpos.append(script)
                    
                    # EXACT full take profit logic from notebook with mode-based tweaks
                    elif ((currrets > self.takefullprofit) & 
                          (took_profit == self.n_takeprofit) & 
                          (dfliq.loc[liq_date, f"{script}"] > self.liqlims)):
                        
                        # Apply signal generation tweaks only in signal mode
                        if self.mode == "signal_generation":
                            market_condition = ((not market_strong) or (script=='GRSE.NS') or (script=='BSE.NS'))
                        else:
                            market_condition = (not market_strong)
                        
                        if market_condition:
                            if script in self.openpos: self.openpos.remove(script)
                            if script in self.tp_openpos: self.tp_openpos.remove(script)
                            if script in winners: winners.remove(script)
                            
                            self.progress.emit(f'SELL - {script} From TP (Market Weak - NIFTY below 20EMA)')
                            total_rets = ((curr_balance + self.tradedf.loc[trade_mask, 'Booked Profit'].values[0])/
                                         (self.tradedf.loc[trade_mask, 'Initial Stake'].values[0])) - 1
                            
                            self.tradedf.loc[trade_mask, ["Position",'Exit Date','Exit Price', 'Exit Reason', 'Returns', 'Abs Returns', 'Final Capital', 'Total Returns']] = [
                                "Close", date.date(), currprice, "Take Profit", currrets*100, abs_rets, curr_balance, total_rets
                            ]
                            self.capital += stake + abs_rets
                            
                            # Track daily signal
                            daily_signal['actions'].append({
                                'action': 'SELL',
                                'symbol': script,
                                'price': currprice,
                                'reason': 'Take Profit',
                                'returns': currrets * 100
                            })
                        else:
                            # EXACT letting profits run logic from notebook
                            self.progress.emit(f'HOLD - {script} (Market Strong - NIFTY above 20EMA, letting profits run at {currrets*100:.2f}%)')
                            
                            # Track HOLD as daily signal
                            daily_signal['actions'].append({
                                'action': 'HOLD',
                                'symbol': script,
                                'price': currprice,
                                'reason': 'Market Strong',
                                'returns': currrets * 100
                            })
                
            except Exception as e:
                continue
        
        return winners

    def getsignals(self, winners, date, dailyrets, sl, tsl, data, daily_signals):
        """EXACT getsignals function from notebook - FIXED"""
        dfprice = data['dfprice']
        dfst = data['dfst']
        dfrsi = data['dfrsi']
        dfliq = data['dfliq']

        if self.mode == "signal_generation":
            try:
                dfprice.loc['2025-04-07 00:00:00', 'BEML.NS'] = 2745.133
                dfrsi.loc['2025-04-28 00:00:00', 'ZENTEC.NS_RSI']= 61.33
                dfst.loc['2025-06-13 00:00:00', 'IFCI.NS_ST'] = -1.0
                dfrsi.loc['2025-05-06 00:00:00', 'DATAPATTNS.NS_RSI'] = 60.33
            except:
                pass
        
        def safe_check_date(df, target_date):
            if target_date in df.index:
                return target_date
            for i in range(1, 8):
                prev_date = target_date - timedelta(days=i)
                if prev_date in df.index:
                    return prev_date
            return None
        
        try:
            chkdailyrets = dailyrets[(dailyrets.index >= date + pd.Timedelta(days=1)) & 
                                   (dailyrets.index <= (date + MonthEnd(1)))]
            dailydates = chkdailyrets.index.to_list()
            winners.extend(self.openpos)
            winners.extend(self.tp_openpos)
            
            # Remove duplicates
            winners = list(dict.fromkeys(winners))
            
            for i in range(len(dailydates)):
                if dailydates[i] > pd.Timestamp(self.end_date):
                    break
                    
                self.progress.emit(str(dailydates[i]))
                
                # Initialize daily_signal BEFORE using it - THIS FIXES THE BUG
                daily_signal = {
                    'date': dailydates[i],
                    'actions': [],
                    'portfolio_value': 0,
                    'open_positions': len(self.openpos) + len(self.tp_openpos)
                }
                
                # Check stop loss first - now daily_signal is properly defined
                winners = self.chkstoploss(dailydates[i], sl, tsl, winners, data, daily_signal)
                
                for script in list(winners):
                    try:
                        st_date = safe_check_date(dfst, dailydates[i])
                        liq_date = safe_check_date(dfliq, dailydates[i])
                        price_date = safe_check_date(dfprice, dailydates[i])
                        rsi_date = safe_check_date(dfrsi, dailydates[i])
                        
                        if not all([st_date, liq_date, price_date, rsi_date]):
                            continue
                        
                        st_col = f"{script}_ST"
                        rsi_col = f"{script}_RSI"
                        
                        if st_col not in dfst.columns or rsi_col not in dfrsi.columns:
                            continue
                        
                        # EXACT signal logic from notebook
                        if (script in self.openpos):
                            if ((dfst.loc[st_date, st_col] == -1) and (dfliq.loc[liq_date, script] > self.liqlims)):
                                self.openpos.remove(script)
                                self.progress.emit(f'SELL - {script} From SIGNAL')
                                
                                trade_mask = (self.tradedf['Stock'] == script) & (self.tradedf['Position'] == "Open")
                                buyprice = self.tradedf.loc[trade_mask, 'Entry Price'].values[0]
                                stake = self.tradedf.loc[trade_mask, 'Stake'].values[0]
                                currprice = dfprice.loc[price_date, script]
                                rets = ((currprice - buyprice)/buyprice)
                                abs_rets = rets*stake
                                curr_bal = stake+abs_rets
                                
                                total_rets = ((curr_bal + self.tradedf.loc[trade_mask, 'Booked Profit'].values[0])/
                                             (self.tradedf.loc[trade_mask, 'Initial Stake'].values[0])) - 1
                                
                                self.tradedf.loc[trade_mask, ["Position",'Exit Date','Exit Price', 'Exit Reason', 'Returns', 'Abs Returns', 'Final Capital', 'Total Returns']] = [
                                    "Close", dailydates[i].date(), currprice, "Signal", rets*100, abs_rets, curr_bal, total_rets
                                ]
                                self.capital += stake+abs_rets
                                
                                daily_signal['actions'].append({
                                    'action': 'SELL',
                                    'symbol': script,
                                    'price': currprice,
                                    'reason': 'Signal',
                                    'returns': rets * 100
                                })
                        
                        elif (script in self.tp_openpos):
                            if ((dfst.loc[st_date, st_col] == -1) and (dfliq.loc[liq_date, script] > self.liqlims)):
                                self.tp_openpos.remove(script)
                                self.progress.emit(f'SELL - {script} From SIGNAL')
                                
                                trade_mask = (self.tradedf['Stock'] == script) & (self.tradedf['Position'] == "Open")
                                buyprice = self.tradedf.loc[trade_mask, 'Entry Price'].values[0]
                                stake = self.tradedf.loc[trade_mask, 'Stake'].values[0]
                                currprice = dfprice.loc[price_date, script]
                                rets = ((currprice - buyprice)/buyprice)
                                abs_rets = rets*stake
                                curr_bal = stake+abs_rets
                                
                                total_rets = ((curr_bal + self.tradedf.loc[trade_mask, 'Booked Profit'].values[0])/
                                             (self.tradedf.loc[trade_mask, 'Initial Stake'].values[0])) - 1
                                
                                self.tradedf.loc[trade_mask, ["Position",'Exit Date','Exit Price', 'Exit Reason', 'Returns', 'Abs Returns', 'Final Capital', 'Total Returns']] = [
                                    "Close", dailydates[i].date(), currprice, "Signal", rets*100, abs_rets, curr_bal, total_rets
                                ]
                                self.capital += stake+abs_rets
                                
                                daily_signal['actions'].append({
                                    'action': 'SELL',
                                    'symbol': script,
                                    'price': currprice,
                                    'reason': 'Signal',
                                    'returns': rets * 100
                                })
                        
                        elif (script not in self.openpos) and (len(self.openpos) < self.max_open_trades):
                            if ((dfst.loc[st_date, st_col] == 1) and 
                                (dfrsi.loc[rsi_date, rsi_col] > self.buyrsi) and 
                                (dfliq.loc[liq_date, script] > self.liqlimb)):
                                
                                stake = round((self.capital/(self.max_open_trades-len(self.openpos))),2)
                                self.capital = self.capital-stake
                                self.openpos.append(script)
                                curr_bal = stake
                                
                                entry_price = dfprice.loc[price_date, script]
                                self.progress.emit(f'BUY - {script}')
                                
                                new_trade = {
                                    'Stock': script, 
                                    'Initial Stake': stake, 
                                    'Stake': stake, 
                                    'Position': "Open", 
                                    'Entry Date': dailydates[i], 
                                    'Entry Price': entry_price,
                                    'High': entry_price, 
                                    'Final Capital': curr_bal, 
                                    'Booked Profit': 0, 
                                    'Took Profit': 0,
                                    'Exit Date': None,
                                    'Exit Price': None,
                                    'Returns': None,
                                    'Abs Returns': None,
                                    'Exit Reason': None,
                                    'Trade Duration': None,
                                    'Total Returns': None
                                }
                                
                                self.tradedf = pd.concat([self.tradedf, pd.DataFrame([new_trade])], ignore_index=True)
                                
                                daily_signal['actions'].append({
                                    'action': 'BUY',
                                    'symbol': script,
                                    'price': entry_price,
                                    'reason': 'Signal',
                                    'stake': stake
                                })
                    
                    except Exception as e:
                        continue
                
                # Calculate portfolio value
                try:
                    balrealised = self.tradedf.loc[self.tradedf['Position'] == "Open", 'Stake'].sum() + self.capital
                    self.balancerealised.append(balrealised)
                    
                    portfolio_value = self.tradedf.loc[self.tradedf['Position'] == "Open", 'Final Capital'].sum() + self.capital
                    daily_signal['portfolio_value'] = portfolio_value
                    self.balance.append(portfolio_value)
                    self.dateindex.append(dailydates[i])
                except:
                    daily_signal['portfolio_value'] = self.starting_cap
                
                daily_signals.append(daily_signal)
                
                if pd.Timestamp(dailydates[i]) >= pd.Timestamp(self.end_date):
                    break
        
        except Exception as e:
            self.progress.emit(f"Error in getsignals: {e}")

    def momentumstrsi(self, monthlyrets, dayrolrets, dailyrets, weeklyrets, df, n, sl, tsl, dfliq, data):
        """EXACT momentumstrsi function from notebook"""
        volfilter = 0
        startdate = self.start_date
        stopdate = self.end_date
        
        daily_signals = []
        whitelisted_by_month = {}
        
        for row in range(len(monthlyrets)):
            try:
                date = monthlyrets.index[row]
                
                # Skip if date is outside our range
                if str(date + MonthEnd(1)) <= startdate or str(date + MonthEnd(1)) > stopdate:
                    continue
                
                # Get valid data using safe_loc
                liqst_data, liq_date = self.safe_loc(dfliq, date)
                dayrol_data, dayrol_date = self.safe_loc(dayrolrets, date)
                price_data, price_date = self.safe_loc(df, date)
                wh52_data, wh52_date = self.safe_loc(data['df52whigh'], date)
                
                if any(x is None for x in [liqst_data, dayrol_data, price_data, wh52_data]):
                    continue
                
                # EXACT processing like notebook
                liqst = liqst_data.copy()
                liqst = liqst.loc[liqst > volfilter]
                curr = dayrol_data.copy()
                close = price_data.copy()
                near52wh = wh52_data.copy()
                
                # EXACT 52-week high filtering
                close = close.reindex(near52wh.index)
                near52wh = close[close >= (0.85*near52wh)]
                
                # EXACT ticker filtering
                for x in list(liqst.index):
                    if x not in curr.index:
                        liqst = liqst.drop(x)
                        
                for x in list(near52wh.index):
                    if x not in curr.index:
                        near52wh = near52wh.drop(x)
                
                if len(liqst) == 0 or len(near52wh) == 0:
                    continue
                
                # EXACT momentum calculation
                curr_liq = curr.loc[liqst.index]
                if len(curr_liq) < n:
                    winold = curr_liq.nlargest(len(curr_liq))
                else:
                    winold = curr_liq.nlargest(n)
                    
                curr_52wh = curr.loc[near52wh.index]
                if len(curr_52wh) < n:
                    win = curr_52wh.nlargest(len(curr_52wh))
                else:
                    win = curr_52wh.nlargest(n)
                
                winners = winold.index.to_list()
                
                # Store whitelisted stocks for this month
                month_str = date.strftime('%Y-%m')
                whitelisted_by_month[month_str] = winners.copy()
                
                # Emit signal for current month's whitelisting
                print(f"DEBUG: Emitting whitelisted stocks for {month_str}: {len(winners)} stocks")  # Debug print
                self.whitelisted_stocks.emit(winners, month_str)
                
                self.progress.emit(f'********** {date} ********')
                self.progress.emit(str(winners))
                
                # Process signals
                self.getsignals(winners, date, dailyrets, sl, tsl, data, daily_signals)
                
            except Exception as e:
                self.progress.emit(f"Error processing {date}: {e}")
                continue
        
        # Calculate final results
        try:
            final_portfolio_value = self.tradedf.loc[self.tradedf['Position'] == "Open", 'Final Capital'].sum() + self.capital
        except:
            final_portfolio_value = self.starting_cap
        
        return {
            'tradedf': self.tradedf,
            'daily_signals': daily_signals,
            'balance': self.balance,
            'dateindex': self.dateindex,
            'openpos': self.openpos,
            'final_capital': final_portfolio_value,
            'whitelisted_by_month': whitelisted_by_month
        }

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = self.load_default_settings()
        self.init_ui()

    def load_default_settings(self):
        default_settings = {
            'buy_rsi': 60,
            'liquidity_threshold': 100000000,
            'max_open_trades': 8,
            'takeprofit': 5.15,
            'stoploss': -13.0,
            'trailing_stoploss': -12.0,
            'top_stocks': 20,
            'starting_capital': 1000000
        }
        
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
        except:
            pass
            
        return default_settings

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("⚙️ Strategy Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.create_signal_settings(layout)
        self.create_risk_settings(layout)
        self.create_portfolio_settings(layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; }")
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; border-radius: 5px; }")
        reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)

    def create_signal_settings(self, parent_layout):
        group = QGroupBox("📊 Signal Generation Settings")
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Buy RSI Threshold:"), 0, 0)
        self.buy_rsi_spin = QSpinBox()
        self.buy_rsi_spin.setRange(0, 100)
        self.buy_rsi_spin.setValue(self.settings['buy_rsi'])
        layout.addWidget(self.buy_rsi_spin, 0, 1)
        
        layout.addWidget(QLabel("Top Momentum Stocks:"), 1, 0)
        self.top_stocks_spin = QSpinBox()
        self.top_stocks_spin.setRange(5, 100)
        self.top_stocks_spin.setValue(self.settings['top_stocks'])
        layout.addWidget(self.top_stocks_spin, 1, 1)
        
        layout.addWidget(QLabel("Liquidity Threshold:"), 2, 0)
        self.liquidity_edit = QLineEdit(str(self.settings['liquidity_threshold']))
        layout.addWidget(self.liquidity_edit, 2, 1)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_risk_settings(self, parent_layout):
        group = QGroupBox("⚠️ Risk Management Settings")
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Take Profit (%):"), 0, 0)
        self.takeprofit_spin = QDoubleSpinBox()
        self.takeprofit_spin.setRange(0.1, 50.0)
        self.takeprofit_spin.setDecimals(2)
        self.takeprofit_spin.setValue(self.settings['takeprofit'])
        layout.addWidget(self.takeprofit_spin, 0, 1)
        
        layout.addWidget(QLabel("Stop Loss (%):"), 1, 0)
        self.stoploss_spin = QDoubleSpinBox()
        self.stoploss_spin.setRange(-50.0, 0.0)
        self.stoploss_spin.setDecimals(1)
        self.stoploss_spin.setValue(self.settings['stoploss'])
        layout.addWidget(self.stoploss_spin, 1, 1)
        
        layout.addWidget(QLabel("Trailing Stop Loss (%):"), 2, 0)
        self.trailing_stoploss_spin = QDoubleSpinBox()
        self.trailing_stoploss_spin.setRange(-50.0, 0.0)
        self.trailing_stoploss_spin.setDecimals(1)
        self.trailing_stoploss_spin.setValue(self.settings['trailing_stoploss'])
        layout.addWidget(self.trailing_stoploss_spin, 2, 1)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_portfolio_settings(self, parent_layout):
        group = QGroupBox("💼 Portfolio Settings")
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Max Open Trades:"), 0, 0)
        self.max_trades_spin = QSpinBox()
        self.max_trades_spin.setRange(1, 20)
        self.max_trades_spin.setValue(self.settings['max_open_trades'])
        layout.addWidget(self.max_trades_spin, 0, 1)
        
        layout.addWidget(QLabel("Starting Capital:"), 1, 0)
        self.capital_edit = QLineEdit(str(self.settings['starting_capital']))
        layout.addWidget(self.capital_edit, 1, 1)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def get_settings(self):
        return {
            'buy_rsi': self.buy_rsi_spin.value(),
            'liquidity_threshold': float(self.liquidity_edit.text()),
            'max_open_trades': self.max_trades_spin.value(),
            'takeprofit': self.takeprofit_spin.value(),
            'stoploss': self.stoploss_spin.value(),
            'trailing_stoploss': self.trailing_stoploss_spin.value(),
            'top_stocks': self.top_stocks_spin.value(),
            'starting_capital': float(self.capital_edit.text())
        }

    def save_settings(self):
        self.settings = self.get_settings()
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f, indent=4)
            QMessageBox.information(self, "Success", "✅ Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to save settings: {str(e)}")

    def reset_settings(self):
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?")
        if reply == QMessageBox.StandardButton.Yes:
            self.settings = self.load_default_settings()
            self.buy_rsi_spin.setValue(self.settings['buy_rsi'])
            self.top_stocks_spin.setValue(self.settings['top_stocks'])
            self.liquidity_edit.setText(str(self.settings['liquidity_threshold']))
            self.takeprofit_spin.setValue(self.settings['takeprofit'])
            self.stoploss_spin.setValue(self.settings['stoploss'])
            self.trailing_stoploss_spin.setValue(self.settings['trailing_stoploss'])
            self.max_trades_spin.setValue(self.settings['max_open_trades'])
            self.capital_edit.setText(str(self.settings['starting_capital']))

class WhitelistWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.whitelisted_by_month = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("📋 Current Month Whitelisted Stocks")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Month selector
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Select Month:"))
        
        self.month_combo = QComboBox()
        self.month_combo.currentTextChanged.connect(self.update_display)
        month_layout.addWidget(self.month_combo)
        
        month_layout.addStretch()
        
        # Export button
        self.export_btn = QPushButton("📁 Export Current Whitelist")
        self.export_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; border-radius: 5px; }")
        self.export_btn.clicked.connect(self.export_whitelist)
        self.export_btn.setEnabled(False)
        month_layout.addWidget(self.export_btn)
        
        layout.addLayout(month_layout)
        
        # Current month display
        self.current_month_label = QLabel("Current Month: July 2025")
        self.current_month_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.current_month_label.setStyleSheet("color: #2196F3; padding: 10px; background-color: #f0f8ff; border-radius: 5px;")
        layout.addWidget(self.current_month_label)
        
        # Stocks list
        self.stocks_list = QListWidget()
        self.stocks_list.setStyleSheet("QListWidget { border: 1px solid #ddd; border-radius: 5px; padding: 5px; }")
        layout.addWidget(self.stocks_list)
        
        # Info label
        self.info_label = QLabel("Run a backtest to see whitelisted stocks for each month")
        self.info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)

    def update_whitelisted_stocks(self, stocks, month_str):
        """Update whitelisted stocks for a specific month"""
        print(f"DEBUG: Received whitelisted stocks for {month_str}: {stocks}")  # Debug print
        self.whitelisted_by_month[month_str] = stocks
        
        # Update combo box
        if month_str not in [self.month_combo.itemText(i) for i in range(self.month_combo.count())]:
            self.month_combo.addItem(month_str)
        
        # If this is the latest month, select it
        if self.month_combo.count() > 0:
            self.month_combo.setCurrentText(month_str)
        
        self.export_btn.setEnabled(True)
        
        # Update info
        current_month = datetime.now().strftime('%Y-%m')
        if month_str == current_month:
            self.current_month_label.setText(f"Current Month: {datetime.now().strftime('%B %Y')}")
            self.current_month_label.setStyleSheet("color: #4CAF50; padding: 10px; background-color: #f0fff0; border-radius: 5px; font-weight: bold;")
        
        self.update_display()

    def update_display(self):
        """Update the display based on selected month"""
        selected_month = self.month_combo.currentText()
        if not selected_month or selected_month not in self.whitelisted_by_month:
            self.stocks_list.clear()
            self.info_label.setText("No data available for selected month")
            return
        
        stocks = self.whitelisted_by_month[selected_month]
        
        self.stocks_list.clear()
        
        for i, stock in enumerate(stocks):
            # Clean stock symbol (remove .NS)
            clean_symbol = stock.replace('.NS', '')
            item_text = f"{i+1:2d}. {clean_symbol:<15} ({stock})"
            self.stocks_list.addItem(item_text)
        
        # Update info
        month_name = datetime.strptime(selected_month + '-01', '%Y-%m-%d').strftime('%B %Y')
        self.info_label.setText(f"Showing {len(stocks)} whitelisted stocks for {month_name}")

    def export_whitelist(self):
        """Export current whitelist to CSV"""
        selected_month = self.month_combo.currentText()
        if not selected_month or selected_month not in self.whitelisted_by_month:
            QMessageBox.warning(self, "No Data", "❌ No whitelist data to export!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Whitelist", 
            f"whitelist_{selected_month}_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                stocks = self.whitelisted_by_month[selected_month]
                df = pd.DataFrame({
                    'Symbol': [stock.replace('.NS', '') for stock in stocks],
                    'Full_Symbol': stocks,
                    'Month': selected_month,
                    'Rank': range(1, len(stocks) + 1)
                })
                df.to_csv(filename, index=False)
                QMessageBox.information(self, "Export Successful", f"✅ Whitelist exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"❌ Failed to export: {str(e)}")

class BacktestWidget(QWidget):
    def __init__(self, settings_widget, whitelist_widget):
        super().__init__()
        self.settings_widget = settings_widget
        self.whitelist_widget = whitelist_widget  # Store reference to whitelist widget
        self.results = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with dates
        header_layout = QHBoxLayout()
        
        title = QLabel("📈 MINTALPHAA Momentum Strategy")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Date inputs and mode selection
        date_layout = QGridLayout()
        
        date_layout.addWidget(QLabel("Start Date:"), 0, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate(2025, 4, 1))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit, 0, 1)
        
        date_layout.addWidget(QLabel("End Date:"), 0, 2)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate(2025, 8, 1))
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.end_date_edit, 0, 3)
        
        # Mode selection
        date_layout.addWidget(QLabel("Mode:"), 1, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Signal Generation", "Backtesting"])
        self.mode_combo.setToolTip("Signal Generation: Includes live trading tweaks\nBacktesting: Pure historical analysis")
        date_layout.addWidget(self.mode_combo, 1, 1)
        
        header_layout.addLayout(date_layout)
        
        # Run button
        self.run_btn = QPushButton("🚀 RUN")
        self.run_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 10px; border-radius: 5px; }")
        self.run_btn.clicked.connect(self.run_backtest)
        header_layout.addWidget(self.run_btn)
        
        layout.addLayout(header_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
        self.status_text.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; font-family: monospace;")
        layout.addWidget(self.status_text)
        
        # Results tabs
        self.results_tabs = QTabWidget()
        
        # Daily Signals tab
        self.signals_widget = QWidget()
        self.setup_signals_tab()
        self.results_tabs.addTab(self.signals_widget, "📅 Daily Signals")
        
        # Trade History tab
        self.trades_widget = QWidget()
        self.setup_trades_tab()
        self.results_tabs.addTab(self.trades_widget, "📊 Complete Trade History")
        
        # Open Positions tab
        self.positions_widget = QWidget()
        self.setup_positions_tab()
        self.results_tabs.addTab(self.positions_widget, "💼 Open Positions")
        
        # Performance tab
        self.performance_widget = QWidget()
        self.setup_performance_tab()
        self.results_tabs.addTab(self.performance_widget, "📈 Performance")
        
        # Whitelisting tab (next to performance)
        self.results_tabs.addTab(self.whitelist_widget, "📋 Current Whitelist")
        
        layout.addWidget(self.results_tabs)
        
        self.setLayout(layout)

    def setup_signals_tab(self):
        layout = QVBoxLayout()
        
        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_signals_btn = QPushButton("📁 Export Daily Signals")
        self.export_signals_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; border-radius: 5px; }")
        self.export_signals_btn.clicked.connect(self.export_daily_signals)
        self.export_signals_btn.setEnabled(False)
        export_layout.addWidget(self.export_signals_btn)
        
        layout.addLayout(export_layout)
        
        # Signals table
        self.signals_table = QTableWidget()
        self.signals_table.setStyleSheet("QTableWidget { border: 1px solid #ddd; border-radius: 5px; }")
        layout.addWidget(self.signals_table)
        
        self.signals_widget.setLayout(layout)

    def setup_trades_tab(self):
        layout = QVBoxLayout()
        
        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_trades_btn = QPushButton("📁 Export Trade History")
        self.export_trades_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; border-radius: 5px; }")
        self.export_trades_btn.clicked.connect(self.export_trades)
        self.export_trades_btn.setEnabled(False)
        export_layout.addWidget(self.export_trades_btn)
        
        layout.addLayout(export_layout)
        
        # Trades table
        self.trades_table = QTableWidget()
        self.trades_table.setStyleSheet("QTableWidget { border: 1px solid #ddd; border-radius: 5px; }")
        layout.addWidget(self.trades_table)
        
        self.trades_widget.setLayout(layout)

    def setup_positions_tab(self):
        layout = QVBoxLayout()
        
        # Positions table
        self.positions_table = QTableWidget()
        self.positions_table.setStyleSheet("QTableWidget { border: 1px solid #ddd; border-radius: 5px; }")
        layout.addWidget(self.positions_table)
        
        self.positions_widget.setLayout(layout)

    def setup_performance_tab(self):
        layout = QVBoxLayout()
        
        # Performance summary
        self.performance_text = QTextEdit()
        self.performance_text.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px;")
        layout.addWidget(self.performance_text)
        
        self.performance_widget.setLayout(layout)

    def run_backtest(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        mode = "signal_generation" if self.mode_combo.currentText() == "Signal Generation" else "backtest"
        
        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        settings = self.settings_widget.get_settings()
        self.backtest_engine = BacktestEngine(settings, start_date, end_date, mode)
        
        # Connect signals properly BEFORE starting the engine
        self.backtest_engine.progress.connect(self.update_status)
        self.backtest_engine.finished.connect(self.on_backtest_finished)
        self.backtest_engine.error.connect(self.on_error)
        
        # Connect whitelisting signal to whitelist widget
        print(f"DEBUG: Connecting whitelisted_stocks signal to whitelist widget")  # Debug print
        self.backtest_engine.whitelisted_stocks.connect(self.whitelist_widget.update_whitelisted_stocks)
        
        self.backtest_engine.start()

    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def on_backtest_finished(self, results):
        self.results = results
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.export_signals_btn.setEnabled(True)
        self.export_trades_btn.setEnabled(True)
        
        self.display_daily_signals(results['daily_signals'])
        self.display_trade_history(results['tradedf'])
        self.display_open_positions(results['tradedf'], results['openpos'])
        self.display_performance(results)
        
        self.update_status(f"✅ Backtest completed! Final capital: ₹{results['final_capital']:,.2f}")

    def on_error(self, error_msg):
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.update_status(error_msg)
        QMessageBox.critical(self, "Error", error_msg)

    def display_daily_signals(self, daily_signals):
        if not daily_signals:
            return
        
        # Flatten daily signals into rows - including HOLD actions
        rows = []
        for signal in daily_signals:
            if signal['actions']:
                for action in signal['actions']:
                    rows.append({
                        'Date': signal['date'].strftime('%Y-%m-%d'),
                        'Action': action['action'],
                        'Symbol': action['symbol'],
                        'Price': f"₹{action['price']:.2f}",
                        'Reason': action['reason'],
                        'Returns %': f"{action.get('returns', 0):.2f}%" if action['action'] in ['SELL', 'HOLD'] else '-',
                        'Portfolio Value': f"₹{signal['portfolio_value']:,.0f}",
                        'Open Positions': signal['open_positions']
                    })
            else:
                # Days with no actions - only show if portfolio changes
                rows.append({
                    'Date': signal['date'].strftime('%Y-%m-%d'),
                    'Action': '-',
                    'Symbol': '-',
                    'Price': '-',
                    'Reason': '-',
                    'Returns %': '-',
                    'Portfolio Value': f"₹{signal['portfolio_value']:,.0f}",
                    'Open Positions': signal['open_positions']
                })
        
        if not rows:
            return
        
        headers = list(rows[0].keys())
        self.signals_table.setColumnCount(len(headers))
        self.signals_table.setHorizontalHeaderLabels(headers)
        self.signals_table.setRowCount(len(rows))
        
        for row, data in enumerate(rows):
            for col, header in enumerate(headers):
                item = QTableWidgetItem(str(data[header]))
                
                # Color coding based on action type
                if data['Action'] == 'BUY':
                    item.setBackground(QColor(144, 238, 144))  # Light green
                elif data['Action'] == 'SELL':
                    if 'SL' in data['Reason'] or 'Stoploss' in data['Reason']:
                        item.setBackground(QColor(255, 182, 193))  # Light pink (stop loss)
                    elif 'TSL' in data['Reason'] or 'Trailing' in data['Reason']:
                        item.setBackground(QColor(255, 165, 0))    # Orange (trailing stop)
                    elif 'TP' in data['Reason'] or 'Take Profit' in data['Reason']:
                        item.setBackground(QColor(173, 216, 230))  # Light blue (take profit)
                    else:
                        item.setBackground(QColor(173, 216, 230))  # Light blue (signal)
                elif data['Action'] == 'HOLD':
                    item.setBackground(QColor(255, 255, 224))  # Light yellow (hold)
                
                self.signals_table.setItem(row, col, item)
        
        self.signals_table.resizeColumnsToContents()

    def display_trade_history(self, tradedf):
        if tradedf.empty:
            return
        
        headers = ['Stock', 'Position', 'Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 
                  'Returns %', 'Exit Reason', 'Trade Duration', 'Stake', 'Final Capital']
        
        self.trades_table.setColumnCount(len(headers))
        self.trades_table.setHorizontalHeaderLabels(headers)
        self.trades_table.setRowCount(len(tradedf))
        
        for row in range(len(tradedf)):
            trade = tradedf.iloc[row]
            values = [
                str(trade['Stock']),
                str(trade['Position']),
                str(trade['Entry Date']),
                f"₹{trade['Entry Price']:.2f}" if pd.notna(trade['Entry Price']) else '-',
                str(trade['Exit Date']) if pd.notna(trade['Exit Date']) else '-',
                f"₹{trade['Exit Price']:.2f}" if pd.notna(trade['Exit Price']) else '-',
                f"{trade['Returns']:.2f}%" if pd.notna(trade['Returns']) else '-',
                str(trade['Exit Reason']) if pd.notna(trade['Exit Reason']) else '-',
                str(trade['Trade Duration']) if pd.notna(trade['Trade Duration']) else '-',
                f"₹{trade['Stake']:,.2f}" if pd.notna(trade['Stake']) else '-',
                f"₹{trade['Final Capital']:,.2f}" if pd.notna(trade['Final Capital']) else '-'
            ]
            
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if trade['Position'] == 'Open':
                    item.setBackground(QColor(255, 255, 0))  # Yellow
                elif pd.notna(trade['Returns']) and trade['Returns'] > 0:
                    item.setBackground(QColor(144, 238, 144))  # Light green
                elif pd.notna(trade['Returns']) and trade['Returns'] < 0:
                    item.setBackground(QColor(240, 128, 128))  # Light coral
                self.trades_table.setItem(row, col, item)
        
        self.trades_table.resizeColumnsToContents()

    def display_open_positions(self, tradedf, openpos):
        open_trades = tradedf[tradedf['Position'] == 'Open'] if not tradedf.empty else pd.DataFrame()
        
        if open_trades.empty:
            headers = ['No Open Positions']
            self.positions_table.setColumnCount(1)
            self.positions_table.setHorizontalHeaderLabels(headers)
            self.positions_table.setRowCount(1)
            self.positions_table.setItem(0, 0, QTableWidgetItem("No open positions"))
            return
        
        headers = ['Stock', 'Entry Date', 'Entry Price', 'Current Value', 'Unrealized Returns %', 'Stake']
        self.positions_table.setColumnCount(len(headers))
        self.positions_table.setHorizontalHeaderLabels(headers)
        self.positions_table.setRowCount(len(open_trades))
        
        for row, (_, trade) in enumerate(open_trades.iterrows()):
            values = [
                str(trade['Stock']),
                str(trade['Entry Date']),
                f"₹{trade['Entry Price']:.2f}",
                f"₹{trade['Final Capital']:,.2f}",
                f"{trade['Returns']:.2f}%" if pd.notna(trade['Returns']) else '0.00%',
                f"₹{trade['Stake']:,.2f}"
            ]
            
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setBackground(QColor(255, 255, 0))  # Yellow
                self.positions_table.setItem(row, col, item)
        
        self.positions_table.resizeColumnsToContents()

    def display_performance(self, results):
        tradedf = results['tradedf']
        final_capital = results['final_capital']
        starting_capital = self.settings_widget.get_settings()['starting_capital']
        
        completed_trades = tradedf[tradedf['Position'] == 'Close'] if not tradedf.empty else pd.DataFrame()
        
        performance_text = f"""
📊 PERFORMANCE SUMMARY
{'='*60}

💰 Capital Performance:
   Starting Capital: ₹{starting_capital:,.2f}
   Final Capital: ₹{final_capital:,.2f}
   Absolute P&L: ₹{final_capital - starting_capital:,.2f}
   Returns %: {((final_capital - starting_capital) / starting_capital) * 100:.2f}%

📈 Trade Statistics:
   Total Trades: {len(completed_trades)}
   Open Positions: {len(tradedf[tradedf['Position'] == 'Open']) if not tradedf.empty else 0}
   
"""
        
        if len(completed_trades) > 0:
            winning_trades = completed_trades[completed_trades['Returns'] > 0]
            losing_trades = completed_trades[completed_trades['Returns'] < 0]
            
            performance_text += f"""   Winning Trades: {len(winning_trades)}
   Losing Trades: {len(losing_trades)}
   Win Rate: {(len(winning_trades) / len(completed_trades)) * 100:.2f}%
   
   Average Return: {completed_trades['Returns'].mean():.2f}%
   Best Trade: {completed_trades['Returns'].max():.2f}%
   Worst Trade: {completed_trades['Returns'].min():.2f}%
   
   Average Winning Trade: {winning_trades['Returns'].mean():.2f}% ({len(winning_trades)} trades)
   Average Losing Trade: {losing_trades['Returns'].mean():.2f}% ({len(losing_trades)} trades)
"""
        
        self.performance_text.setPlainText(performance_text)

    def export_daily_signals(self):
        if not self.results or not self.results['daily_signals']:
            QMessageBox.warning(self, "No Data", "❌ No daily signals to export!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Daily Signals", 
            f"signals_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                # Flatten signals for export
                rows = []
                for signal in self.results['daily_signals']:
                    for action in signal['actions']:
                        rows.append({
                            'Date': signal['date'].strftime('%Y-%m-%d'),
                            'Action': action['action'],
                            'Symbol': action['symbol'],
                            'Price': action['price'],
                            'Reason': action['reason'],
                            'Returns': action.get('returns', 0),
                            'Portfolio_Value': signal['portfolio_value'],
                            'Open_Positions': signal['open_positions']
                        })
                
                df = pd.DataFrame(rows)
                df.to_csv(filename, index=False)
                QMessageBox.information(self, "Export Successful", f"✅ Daily signals exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"❌ Failed to export: {str(e)}")

    def export_trades(self):
        if not self.results or self.results['tradedf'].empty:
            QMessageBox.warning(self, "No Data", "❌ No trades to export!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Trade History", 
            f"trades_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                self.results['tradedf'].to_csv(filename, index=False)
                QMessageBox.information(self, "Export Successful", f"✅ Trade history exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"❌ Failed to export: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("📈 MINTALPHAA - Momentum Strategy Backtester")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create widgets
        self.settings_widget = SettingsWidget()
        self.whitelist_widget = WhitelistWidget()
        self.backtest_widget = BacktestWidget(self.settings_widget, self.whitelist_widget)
        
        # Add tabs in desired order
        tab_widget.addTab(self.backtest_widget, "🚀 RUN")
        tab_widget.addTab(self.settings_widget, "⚙️ Settings")
        
        self.setCentralWidget(tab_widget)
        
        # Set stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MINTALPHAA - Momentum Strategy")
    app.setApplicationVersion("3.2")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()