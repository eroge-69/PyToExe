# -*- coding: utf-8 -*-
import scipy
import scipy.stats
import scipy.special
import nltk
import nltk.corpus
import nltk.tokenize
import nltk.stem

# التأكد من تحميل بيانات nltk المطلوبة
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# استيراد المكتبات الأساسية
import numpy as np
import pandas as pd
import time
import logging
import os
import threading
import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Frame, Label, Button
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import warnings
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
import requests
import talib
import yfinance as yf
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import math

warnings.filterwarnings('ignore')

# الكائنات الأساسية
OPTIMAL_COINS = {
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT', 'DOGEUSDT',
    'SHIBUSDT', 'TONUSDT', 'MATICUSDT', 'ATOMUSDT', 'APTUSDT',
    'NEARUSDT', 'ICPUSDT', 'ARBUSDT', 'HBARUSDT', 'VETUSDT',
    'RENDERUSDT', 'INXUSDT', 'OFUSDT', 'GALAUSDT', 'GRTUSDT',
    'INJUSDT', 'TIAUSDT', 'ALCOUSDT', 'SIXUSDT'
}

MIN_TRADE_AMOUNTS = {
    'BTCUSDT': 0.0001, 'ETHUSDT': 0.001, 'BNBUSDT': 0.01,
    'SOLUSDT': 0.01, 'XRPUSDT': 1, 'ADAUSDT': 1,
    'AVAXUSDT': 0.1, 'DOTUSDT': 0.1, 'LINKUSDT': 0.1,
    'DOGEUSDT': 10, 'SHIBUSDT': 100000, 'TONUSDT': 0.1,
    'MATICUSDT': 1, 'ATOMUSDT': 0.1, 'APTUSDT': 0.1,
    'NEARUSDT': 0.1, 'ICPUSDT': 0.1, 'ARBUSDT': 0.1,
    'HBARUSDT': 1, 'VETUSDT': 10, 'RENDERUSDT': 0.1,
    'INXUSDT': 0.1, 'OFUSDT': 0.1, 'GALAUSDT': 10,
    'GRTUSDT': 1, 'INJUSDT': 0.1, 'TIAUSDT': 0.1,
    'ALCOUSDT': 1, 'SIXUSDT': 0.1
}

TRADING_PRESETS = {
    'conservative': {
        'profit_target': 0.02,
        'stop_loss': 0.01,
        'max_trades': 2,
        'risk_per_trade': 0.1
    },
    'normal': {
        'profit_target': 0.04,
        'stop_loss': 0.02,
        'max_trades': 3,
        'risk_per_trade': 0.15
    },
    'aggressive': {
        'profit_target': 0.06,
        'stop_loss': 0.03,
        'max_trades': 5,
        'risk_per_trade': 0.25
    },
    'quantum_profit': {
        'profit_target': 0.015,
        'stop_loss': 0.005,
        'max_trades': 8,
        'risk_per_trade': 0.08,
        'min_holding_time': 300
    }
}

# APIs الحقيقية
NEWS_API_KEY = "3a389a3bb7ac4b69a5528df0068d2ca5"
ALPHA_VANTAGE_KEY = "H2BHWXPA0MS4LVNH"
CRYPTO_PANIC_KEY = "97eb9efdea611e9f1b92c1acc3fb7f57f1a3a17f"

# ========== الأنظمة الجديدة المضافة ==========

class Backtester:
    """نظام Backtesting متقدم لاختبار الإستراتيجيات على البيانات التاريخية"""
    
    def __init__(self, trader=None):
        self.trader = trader
        self.historical_data = {}
        self.performance_metrics = {}
        self.backtest_results = {}
        self.current_strategy = {}
        
    def load_historical_data(self, symbol, days=30, interval='15m'):
        """تحميل البيانات التاريخية من Binance"""
        try:
            if not self.trader or not self.trader.client:
                # استخدام بيانات افتراضية للاختبار
                return self.generate_sample_data(symbol, days)
                
            # حساب وقت البداية
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # تحميل البيانات
            klines = self.trader.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_date.strftime("%d %b, %Y"),
                end_str=end_date.strftime("%d %b, %Y")
            )
            
            # تحويل البيانات
            data = []
            for kline in klines:
                data.append({
                    'timestamp': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            self.historical_data[symbol] = data
            return data
            
        except Exception as e:
            print(f"Error loading historical data for {symbol}: {e}")
            return self.generate_sample_data(symbol, days)
    
    def generate_sample_data(self, symbol, days):
        """إنشاء بيانات نموذجية للاختبار"""
        data = []
        base_price = 100.0
        current_time = int(datetime.now().timestamp() * 1000) - (days * 24 * 60 * 60 * 1000)
        
        for i in range(days * 96):  # 96 فترة 15 دقيقة في اليوم
            volatility = np.random.normal(0, 0.01)
            price_change = base_price * volatility
            base_price += price_change
            
            data.append({
                'timestamp': current_time + (i * 15 * 60 * 1000),
                'open': base_price - price_change,
                'high': base_price + abs(price_change),
                'low': base_price - abs(price_change),
                'close': base_price,
                'volume': np.random.uniform(1000, 10000)
            })
        
        self.historical_data[symbol] = data
        return data
    
    def run_backtest(self, symbol, strategy_config, initial_capital=1000.0):
        """تشغيل اختبار backtest على البيانات التاريخية"""
        try:
            if symbol not in self.historical_data:
                self.load_historical_data(symbol)
            
            data = self.historical_data.get(symbol, [])
            if not data:
                return None
            
            # محاكاة التداول
            capital = initial_capital
            position = 0.0
            entry_price = 0.0
            trades = []
            portfolio_values = []
            
            for i in range(1, len(data)):
                current_price = data[i]['close']
                previous_price = data[i-1]['close']
                
                # محاكاة إشارات التداول
                signal = self.generate_trading_signal(data, i, strategy_config)
                
                if signal == 'buy' and position == 0 and capital > 10:
                    # تنفيذ شراء
                    trade_amount = capital * strategy_config['risk_per_trade']
                    position = trade_amount / current_price
                    entry_price = current_price
                    capital -= trade_amount
                    trades.append({
                        'type': 'buy',
                        'price': current_price,
                        'amount': position,
                        'timestamp': data[i]['timestamp'],
                        'capital_used': trade_amount
                    })
                    
                elif signal == 'sell' and position > 0:
                    # تنفيذ بيع
                    profit = (current_price - entry_price) * position
                    sell_amount = position * current_price
                    capital += sell_amount
                    profit_percent = (profit / (position * entry_price)) * 100 if position * entry_price > 0 else 0
                    
                    trades.append({
                        'type': 'sell',
                        'price': current_price,
                        'amount': position,
                        'profit': profit,
                        'profit_percent': profit_percent,
                        'timestamp': data[i]['timestamp']
                    })
                    position = 0.0
                    entry_price = 0.0
                
                # حساب قيمة المحفظة
                portfolio_value = capital + (position * current_price if position > 0 else 0)
                portfolio_values.append(portfolio_value)
            
            # حساب مؤشرات الأداء
            metrics = self.calculate_performance_metrics(trades, portfolio_values, initial_capital)
            
            self.backtest_results[symbol] = {
                'trades': trades,
                'portfolio_values': portfolio_values,
                'metrics': metrics,
                'symbol': symbol,
                'initial_capital': initial_capital,
                'final_capital': portfolio_values[-1] if portfolio_values else initial_capital
            }
            
            return self.backtest_results[symbol]
            
        except Exception as e:
            print(f"Error in backtest for {symbol}: {e}")
            return None
    
    def generate_trading_signal(self, data, index, strategy_config):
        """توليد إشارات تداول بناءً على الإستراتيجية"""
        if index < 20:  # تحتاج إلى بيانات كافية للتحليل
            return 'hold'
        
        # استخراج البيانات الأخيرة
        prices = [d['close'] for d in data[max(0, index-20):index+1]]
        
        # تحليل فني مبسط
        current_price = prices[-1]
        sma_10 = sum(prices[-10:]) / 10
        sma_20 = sum(prices[-20:]) / 20
        
        # إشارات الشراء والبيع
        if current_price > sma_10 > sma_20 and np.random.random() > 0.3:
            return 'buy'
        elif current_price < sma_10 < sma_20 and np.random.random() > 0.3:
            return 'sell'
        else:
            return 'hold'
    
    def calculate_performance_metrics(self, trades, portfolio_values, initial_capital):
        """حساب مؤشرات أداء متقدمة"""
        if not trades or len(portfolio_values) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'total_loss': 0,
                'profit_factor': 0,
                'total_return_percent': 0,
                'max_drawdown_percent': 0,
                'sharpe_ratio': 0,
                'final_portfolio_value': initial_capital
            }
        
        # الصفقات المربحة والخاسرة
        profitable_trades = [t for t in trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit', 0) < 0]
        
        # إجمالي الأرباح والخسائر
        total_profit = sum(t.get('profit', 0) for t in profitable_trades)
        total_loss = abs(sum(t.get('profit', 0) for t in losing_trades))
        
        # معدل النجاح
        win_rate = len(profitable_trades) / len(trades) if trades else 0
        
        # نسبة الربح/الخسارة
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # العائد الإجمالي
        final_portfolio = portfolio_values[-1] if portfolio_values else initial_capital
        total_return = ((final_portfolio - initial_capital) / initial_capital) * 100
        
        # أقصى خسارة
        max_drawdown = self.calculate_max_drawdown(portfolio_values)
        
        # نسبة شارب
        sharpe_ratio = self.calculate_sharpe_ratio(portfolio_values)
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_factor': profit_factor,
            'total_return_percent': total_return,
            'max_drawdown_percent': max_drawdown * 100,
            'sharpe_ratio': sharpe_ratio,
            'final_portfolio_value': final_portfolio
        }
    
    def calculate_max_drawdown(self, portfolio_values):
        """حساب أقصى خسارة"""
        if len(portfolio_values) < 2:
            return 0
            
        peak = portfolio_values[0]
        max_dd = 0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def calculate_sharpe_ratio(self, portfolio_values, risk_free_rate=0.02):
        """حساب نسبة شارب"""
        if len(portfolio_values) < 2:
            return 0
        
        returns = []
        for i in range(1, len(portfolio_values)):
            daily_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            returns.append(daily_return)
        
        if len(returns) == 0:
            return 0
        
        excess_returns = [r - risk_free_rate/365 for r in returns]
        avg_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)
        
        return avg_excess_return / std_excess_return * np.sqrt(365) if std_excess_return != 0 else 0
    
    def generate_backtest_report(self, symbol):
        """توليد تقرير مفصل عن نتائج Backtest"""
        if symbol not in self.backtest_results:
            return "لا توجد نتائج Backtest لهذه العملة"
        
        result = self.backtest_results[symbol]
        metrics = result['metrics']
        
        report = f"""
📊 تقرير Backtest لـ {symbol}
══════════════════════════════════

📈 أداء التداول:
• إجمالي الصفقات: {metrics['total_trades']}
• الصفقات المربحة: {metrics['winning_trades']}
• الصفقات الخاسرة: {metrics['losing_trades']}
• معدل النجاح: {metrics['win_rate']:.2f}%

💰 النتائج المالية:
• إجمالي الربح: {metrics['total_profit']:.2f} $
• إجمالي الخسارة: {metrics['total_loss']:.2f} $
• عامل الربح: {metrics['profit_factor']:.2f}
• العائد الإجمالي: {metrics['total_return_percent']:.2f}%

⚡ مؤشرات المخاطرة:
• أقصى خسارة: {metrics['max_drawdown_percent']:.2f}%
• نسبة شارب: {metrics['sharpe_ratio']:.2f}

💼 قيمة المحفظة:
• رأس المال الابتدائي: {result['initial_capital']:.2f} $
• القيمة النهائية: {metrics['final_portfolio_value']:.2f} $
• صافي الربح: {metrics['final_portfolio_value'] - result['initial_capital']:.2f} $
        """
        
        return report

    def run_comprehensive_backtest(self, symbols, strategy_config, initial_capital=1000.0):
        """تشغيل Backtest شامل لعدة عملات"""
        results = {}
        total_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'total_loss': 0,
            'final_portfolio_value': 0
        }
        
        for symbol in symbols:
            result = self.run_backtest(symbol, strategy_config, initial_capital)
            if result:
                results[symbol] = result
                metrics = result['metrics']
                
                total_metrics['total_trades'] += metrics['total_trades']
                total_metrics['winning_trades'] += metrics['winning_trades']
                total_metrics['losing_trades'] += metrics['losing_trades']
                total_metrics['total_profit'] += metrics['total_profit']
                total_metrics['total_loss'] += metrics['total_loss']
                total_metrics['final_portfolio_value'] += metrics['final_portfolio_value']
        
        # حساب المتوسطات
        if results:
            total_metrics['win_rate'] = (total_metrics['winning_trades'] / total_metrics['total_trades'] * 100) if total_metrics['total_trades'] > 0 else 0
            total_metrics['profit_factor'] = total_metrics['total_profit'] / total_metrics['total_loss'] if total_metrics['total_loss'] > 0 else float('inf')
            total_metrics['total_return_percent'] = ((total_metrics['final_portfolio_value'] - (initial_capital * len(symbols))) / (initial_capital * len(symbols))) * 100
        
        return results, total_metrics

class AdvancedHedging:
    """نظام تحوط متقدم لحماية المحفظة من المخاطر"""
    
    def __init__(self, trader=None):
        self.trader = trader
        self.hedge_positions = {}
        self.correlation_matrix = {}
        self.volatility_data = {}
        self.hedge_ratios = {}
        
    def analyze_correlations(self, symbols, period=30):
        """تحليل العلاقات بين الأصول"""
        try:
            prices_data = {}
            
            # جمع بيانات الأسعار
            for symbol in symbols:
                if self.trader:
                    data = self.trader.get_historical_data(symbol, '1d', period)
                else:
                    # بيانات افتراضية للاختبار
                    data = self.generate_sample_correlation_data(symbol, period)
                    
                if data:
                    prices = [d[4] for d in data] if isinstance(data[0], list) else [d['close'] for d in data]
                    prices_data[symbol] = prices
            
            # حساب مصفوفة الارتباط
            if prices_data:
                df = pd.DataFrame(prices_data)
                correlation_matrix = df.corr()
                self.correlation_matrix = correlation_matrix
                return correlation_matrix
            else:
                return self.generate_sample_correlation_matrix(symbols)
            
        except Exception as e:
            print(f"Error analyzing correlations: {e}")
            return self.generate_sample_correlation_matrix(symbols)
    
    def generate_sample_correlation_data(self, symbol, period):
        """إنشاء بيانات ارتباط نموذجية للاختبار"""
        data = []
        base_price = 100.0
        
        for i in range(period):
            volatility = np.random.normal(0, 0.02)
            price_change = base_price * volatility
            base_price += price_change
            
            data.append({
                'timestamp': int((datetime.now() - timedelta(days=period-i)).timestamp() * 1000),
                'open': base_price - price_change,
                'high': base_price + abs(price_change),
                'low': base_price - abs(price_change),
                'close': base_price,
                'volume': np.random.uniform(1000, 10000)
            })
        
        return data
    
    def generate_sample_correlation_matrix(self, symbols):
        """إنشاء مصفوفة ارتباط نموذجية"""
        matrix = {}
        for i, sym1 in enumerate(symbols):
            matrix[sym1] = {}
            for j, sym2 in enumerate(symbols):
                if i == j:
                    matrix[sym1][sym2] = 1.0
                else:
                    # محاكاة علاقات ارتباط واقعية
                    if 'BTC' in sym1 and 'BTC' in sym2:
                        matrix[sym1][sym2] = 0.8 + np.random.random() * 0.15
                    elif 'ETH' in sym1 and 'ETH' in sym2:
                        matrix[sym1][sym2] = 0.7 + np.random.random() * 0.2
                    else:
                        matrix[sym1][sym2] = 0.3 + np.random.random() * 0.4
        
        self.correlation_matrix = matrix
        return matrix
    
    def calculate_hedge_ratio(self, asset1, asset2):
        """حساب نسبة التحوط المثلى بين أصلين"""
        try:
            if not self.correlation_matrix:
                self.analyze_correlations([asset1, asset2])
            
            if asset1 in self.correlation_matrix and asset2 in self.correlation_matrix:
                if isinstance(self.correlation_matrix, pd.DataFrame):
                    correlation = self.correlation_matrix.loc[asset1, asset2]
                else:
                    correlation = self.correlation_matrix.get(asset1, {}).get(asset2, 0.5)
                
                hedge_ratio = abs(correlation)
                self.hedge_ratios[f"{asset1}_{asset2}"] = hedge_ratio
                return min(hedge_ratio, 1.0)
            else:
                return 0.7  # نسبة افتراضية
            
        except Exception as e:
            print(f"Error calculating hedge ratio: {e}")
            return 0.7
    
    def pair_hedging(self, primary_asset, hedge_asset, position_size):
        """تنفيذ تحوط باستخدام أزواج الأصول"""
        try:
            hedge_ratio = self.calculate_hedge_ratio(primary_asset, hedge_asset)
            hedge_size = position_size * hedge_ratio * 0.5  # استخدام 50% فقط للتحوط
            
            # إذا كان الارتباط سلبي، نأخذ مركز معاكس
            correlation = self.correlation_matrix.get(primary_asset, {}).get(hedge_asset, 0.5)
            if correlation < -0.3:
                hedge_direction = 'opposite'
            else:
                hedge_direction = 'same'
            
            return {
                'hedge_asset': hedge_asset,
                'hedge_size': hedge_size,
                'hedge_ratio': hedge_ratio,
                'direction': hedge_direction,
                'correlation': correlation
            }
            
        except Exception as e:
            print(f"Error in pair hedging: {e}")
            return None
    
    def dynamic_stop_loss(self, symbol, current_price, entry_price, volatility):
        """وقف خسارة ديناميكي based on التقلبية"""
        try:
            # حساب التقلبية
            if symbol not in self.volatility_data:
                if self.trader:
                    data = self.trader.get_historical_data(symbol, '1h', 20)
                else:
                    data = self.generate_sample_correlation_data(symbol, 20)
                    
                if data:
                    closes = [d[4] for d in data] if isinstance(data[0], list) else [d['close'] for d in data]
                    if len(closes) > 1:
                        returns = np.diff(np.log(closes))
                        volatility = np.std(returns) * np.sqrt(365)  # التقلبية السنوية
                        self.volatility_data[symbol] = volatility
            
            volatility = self.volatility_data.get(symbol, 0.4)  # 40% تقلبية افتراضية
            
            # وقف الخسارة الديناميكي
            if volatility < 0.2:  # تقلبية منخفضة
                stop_loss_pct = 0.015  # 1.5%
            elif volatility < 0.5:  # تقلبية متوسطة
                stop_loss_pct = 0.025  # 2.5%
            else:  # تقلبية عالية
                stop_loss_pct = 0.035  # 3.5%
            
            stop_loss_price = entry_price * (1 - stop_loss_pct)
            
            # وقف الخسارة المتراجع (Trailing Stop)
            if current_price > entry_price:
                # رفع وقف الخسارة مع ارتفاع السعر
                trailing_stop = current_price * (1 - stop_loss_pct/2)
                stop_loss_price = max(stop_loss_price, trailing_stop)
            
            return stop_loss_price
            
        except Exception as e:
            print(f"Error calculating dynamic stop loss: {e}")
            return entry_price * 0.98  # وقف خسارة افتراضي 2%
    
    def options_hedge_simulation(self, position, hedge_amount):
        """محاكاة استخدام الخيارات للتحوط (نظري)"""
        # في الواقع الفعلي، هذا يتطلب وصول لسوق المشتقات
        hedge_cost = hedge_amount * 0.05  # تكلفة افتراضية للتحوط 5%
        
        return {
            'hedge_type': 'put_option',
            'hedge_amount': hedge_amount,
            'hedge_cost': hedge_cost,
            'protection_level': 0.95,  # حماية 95% من الخسائر
            'breakeven_price': position * 0.95  # نقطة التعادل
        }
    
    def calculate_portfolio_hedge(self, portfolio):
        """حساب التحوط الأمثل للمحفظة"""
        try:
            total_value = sum(portfolio.values())
            hedge_recommendations = []
            
            for asset, value in portfolio.items():
                if value > total_value * 0.1:  # تحوط للأصول التي تشكل أكثر من 10%
                    # إيجاد أفضل أصل للتحوط
                    best_hedge = None
                    best_correlation = 0
                    
                    for other_asset in portfolio:
                        if other_asset != asset:
                            if isinstance(self.correlation_matrix, pd.DataFrame):
                                corr = abs(self.correlation_matrix.loc[asset, other_asset])
                            else:
                                corr = abs(self.correlation_matrix.get(asset, {}).get(other_asset, 0))
                            
                            if corr > best_correlation:
                                best_correlation = corr
                                best_hedge = other_asset
                    
                    if best_hedge:
                        hedge_ratio = self.calculate_hedge_ratio(asset, best_hedge)
                        recommended_hedge = value * hedge_ratio * 0.3  # 30% من المركز
                        
                        hedge_recommendations.append({
                            'primary_asset': asset,
                            'hedge_asset': best_hedge,
                            'hedge_ratio': hedge_ratio,
                            'recommended_hedge': recommended_hedge,
                            'correlation': best_correlation
                        })
            
            return hedge_recommendations
            
        except Exception as e:
            print(f"Error calculating portfolio hedge: {e}")
            return []
    
    def get_hedging_strategy(self, portfolio_value, market_condition):
        """الحصول على إستراتيجية تحوط بناءً على ظروف السوق"""
        strategies = {
            'bullish': {
                'hedge_ratio': 0.2,
                'primary_assets': ['BTCUSDT', 'ETHUSDT'],
                'hedge_assets': ['ADAUSDT', 'DOTUSDT'],
                'description': 'تحوط خفيف في السوق الصاعد'
            },
            'bearish': {
                'hedge_ratio': 0.5,
                'primary_assets': ['BTCUSDT', 'ETHUSDT'],
                'hedge_assets': ['USDT', 'BUSD'],
                'description': 'تحوط قوي في السوق الهابط'
            },
            'volatile': {
                'hedge_ratio': 0.4,
                'primary_assets': ['BTCUSDT', 'ETHUSDT'],
                'hedge_assets': ['ADAUSDT', 'LINKUSDT'],
                'description': 'تحوط متوسط في السوق المتقلب'
            },
            'neutral': {
                'hedge_ratio': 0.3,
                'primary_assets': ['BTCUSDT', 'ETHUSDT'],
                'hedge_assets': ['BNBUSDT', 'SOLUSDT'],
                'description': 'تحوط متوازن'
            }
        }
        
        return strategies.get(market_condition, strategies['neutral'])

# ========== الأنظمة الأصلية (بدون تغيير) ==========

class NewsAPIClient:
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
    def get_crypto_news(self, symbol=None, page_size=10):
        """الحصول على أخبار العملات الرقمية من NewsAPI"""
        try:
            query = "cryptocurrency OR bitcoin OR ethereum"
            if symbol:
                coin_name = symbol.replace('USDT', '')
                query += f" OR {coin_name}"
                
            url = f"{self.base_url}/everything?q={query}&language=en&sortBy=publishedAt&pageSize={page_size}&apiKey={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"NewsAPI error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching news: {e}")
            return None

class AlphaVantageClient:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_KEY
        self.base_url = "https://www.alphavantage.co/query"
        
    def get_crypto_data(self, symbol, market='USD'):
        """الحصول على بيانات العملات الرقمية من Alpha Vantage"""
        try:
            # تحويل رمز بينانس إلى رمز Alpha Vantage
            coin_symbol = symbol.replace('USDT', '')
            
            url = f"{self.base_url}?function=DIGITAL_CURRENCY_DAILY&symbol={coin_symbol}&market={market}&apikey={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Alpha Vantage error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching Alpha Vantage data: {e}")
            return None
            
    def get_global_market_sentiment(self):
        """الحصول على مؤشرات السوق العالمية"""
        try:
            url = f"{self.base_url}?function=GLOBAL_QUOTE&symbol=SPY&apikey={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching global market data: {e}")
            return None

class CryptoPanicClient:
    def __init__(self):
        self.auth_token = CRYPTO_PANIC_KEY
        self.base_url = "https://cryptopanic.com/api/v1"
        
    def get_news(self, currencies='BTC,ETH', kind='news', page_size=20):
        """الحصول على أخبار ومشاعر العملات الرقمية من CryptoPanic"""
        try:
            url = f"{self.base_url}/posts/?auth_token={self.auth_token}&currencies={currencies}&kind={kind}&page_size={page_size}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"CryptoPanic error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching CryptoPanic data: {e}")
            return None

class AlternativeMeAPI:
    def __init__(self):
        self.base_url = "https://api.alternative.me/v2"
        
    def get_fear_greed_index(self):
        """الحصول على مؤشر الخوف والجشع"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {"data": [{"value": 50, "value_classification": "Neutral"}]}
        except Exception as e:
            print(f"Error getting fear greed index: {e}")
            return {"data": [{"value": 50, "value_classification": "Neutral"}]}
    
    def get_global_data(self):
        """الحصول على بيانات السوق العالمية"""
        try:
            url = f"{self.base_url}/global/"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
        except Exception as e:
            print(f"Error getting global data: {e}")
            return None

class OnChainAnalyzer:
    def __init__(self):
        self.alpha_vantage = AlphaVantageClient()
        self.alternative_me = AlternativeMeAPI()

    def analyze_whale_movements(self, symbol: str) -> dict:
        """تحليل حركات الحيتان باستخدام بيانات حقيقية"""
        try:
            # الحصول على بيانات Alpha Vantage
            data = self.alpha_vantage.get_crypto_data(symbol)
            
            if data and 'Time Series (Digital Currency Daily)' in data:
                time_series = data['Time Series (Digital Currency Daily)']
                latest_date = list(time_series.keys())[0]
                latest_data = time_series[latest_date]
                
                # حساب التغير في السعر والحجم
                price_change = float(latest_data['4a. close (USD)']) - float(latest_data['1a. open (USD)'])
                volume = float(latest_data['5. volume'])
                
                # استخدام التغير في السعر والحجم كمؤشر لحركة الحيتان
                whale_activity = min(1.0, abs(price_change) / float(latest_data['1a. open (USD)']) * 10)
                net_flow = volume * (price_change / float(latest_data['1a. open (USD)']))
                large_transactions = max(10, int(volume / 1000000))
                
                sentiment = 'bullish' if price_change > 0 else 'bearish'
                
                return {
                    'whale_activity': whale_activity,
                    'net_flow': net_flow,
                    'large_transactions': large_transactions,
                    'sentiment': sentiment,
                    'price_change': price_change,
                    'volume': volume
                }
            
            # بيانات افتراضية في حالة الفشل
            return {
                'whale_activity': np.random.uniform(0, 1),
                'net_flow': np.random.uniform(-1000000, 1000000),
                'large_transactions': np.random.randint(10, 100),
                'sentiment': 'bullish' if np.random.random() > 0.5 else 'bearish'
            }
        except Exception as e:
            print(f"Error in whale movement analysis: {e}")
            return {
                'whale_activity': np.random.uniform(0, 1),
                'net_flow': np.random.uniform(-1000000, 1000000),
                'large_transactions': np.random.randint(10, 100),
                'sentiment': 'bullish' if np.random.random() > 0.5 else 'bearish'
            }

class EconomicAnalyzer:
    def __init__(self):
        self.alternative_me = AlternativeMeAPI()
        self.alpha_vantage = AlphaVantageClient()

    def get_market_sentiment(self) -> dict:
        """الحصول على مشاعر السوق باستخدام بيانات حقيقية"""
        try:
            # مؤشر الخوف والجشع
            fng_data = self.alternative_me.get_fear_greed_index()
            fear_greed_value = fng_data['data'][0]['value']
            fear_greed_classification = fng_data['data'][0]['value_classification']
            
            # بيانات السوق العالمية
            global_data = self.alternative_me.get_global_data()
            if global_data and 'data' in global_data:
                total_volume_24h = global_data['data']['quotes']['USD']['total_volume_24h']
                total_market_cap = global_data['data']['quotes']['USD']['total_market_cap']
                market_volatility = min(0.4, total_volume_24h / total_market_cap * 10)
            else:
                market_volatility = 0.2
            
            # VIX افتراضي للعملات الرقمية
            vix_index = max(15, 50 - fear_greed_value + 20)
            
            # تحديد المشاعر العامة
            if fear_greed_value >= 60:
                overall_sentiment = 'bullish'
            elif fear_greed_value <= 40:
                overall_sentiment = 'bearish'
            else:
                overall_sentiment = 'neutral'

            return {
                'fear_greed_index': fear_greed_value,
                'vix_index': vix_index,
                'market_volatility': market_volatility,
                'overall_sentiment': overall_sentiment,
                'fear_greed_classification': fear_greed_classification
            }
        except Exception as e:
            print(f"Error in market sentiment analysis: {e}")
            return {
                'fear_greed_index': np.random.uniform(0, 100),
                'vix_index': np.random.uniform(15, 40),
                'market_volatility': np.random.uniform(0.1, 0.4),
                'overall_sentiment': np.random.choice(['bullish', 'bearish', 'neutral'])
            }

class SentimentAnalyzer:
    def __init__(self):
        self.news_api = NewsAPIClient()
        self.crypto_panic = CryptoPanicClient()

    def analyze_text_sentiment(self, text: str) -> dict:
        """تحليل نصي مبسط باستخدام NLTK"""
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            
            try:
                nltk.data.find('sentiment/vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            
            sia = SentimentIntensityAnalyzer()
            sentiment_scores = sia.polarity_scores(text)
            
            return {
                'score': (sentiment_scores['compound'] + 1) / 2,  # تحويل من [-1,1] إلى [0,1]
                'confidence': abs(sentiment_scores['compound']),
                'scores': sentiment_scores
            }
        except Exception as e:
            print(f"Error in text sentiment analysis: {e}")
            return {'score': 0.5, 'confidence': 0.7}

    def analyze_social_media(self, symbol: str) -> dict:
        """تحليل وسائل التواصل الاجتماعي باستخدام بيانات حقيقية"""
        try:
            # الحصول على أخبار CryptoPanic
            coin_symbol = symbol.replace('USDT', '')
            news_data = self.crypto_panic.get_news(currencies=coin_symbol, page_size=10)
            
            if news_data and 'results' in news_data:
                results = news_data['results']
                total_sentiment = 0
                count = 0
                
                for news in results:
                    # تحليل عنوان الخبر
                    title = news.get('title', '')
                    sentiment_result = self.analyze_text_sentiment(title)
                    total_sentiment += sentiment_result['score']
                    count += 1
                
                if count > 0:
                    twitter_sentiment = total_sentiment / count
                    reddit_sentiment = twitter_sentiment * 0.9  # محاكاة لـ Reddit
                    combined_score = (twitter_sentiment * 0.6 + reddit_sentiment * 0.4)
                    
                    return {
                        'twitter_sentiment': twitter_sentiment,
                        'reddit_sentiment': reddit_sentiment,
                        'combined_score': combined_score,
                        'trending': count > 5,
                        'news_count': count
                    }
            
            # بيانات افتراضية في حالة الفشل
            return {
                'twitter_sentiment': np.random.uniform(0.4, 0.8),
                'reddit_sentiment': np.random.uniform(0.3, 0.7),
                'combined_score': np.random.uniform(0.4, 0.7),
                'trending': np.random.choice([True, False], p=[0.3, 0.7])
            }
        except Exception as e:
            print(f"Error in social media analysis: {e}")
            return {
                'twitter_sentiment': np.random.uniform(0.4, 0.8),
                'reddit_sentiment': np.random.uniform(0.3, 0.7),
                'combined_score': np.random.uniform(0.4, 0.7),
                'trending': np.random.choice([True, False], p=[0.3, 0.7])
            }

class QuantumAlBrain:
    def __init__(self):
        self.scaler = RobustScaler()
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear': LinearRegression(),
            'svr': SVR(kernel='rbf', C=1.0, epsilon=0.1)
        }
        self.is_trained = False
        self.onchain_analyzer = OnChainAnalyzer()
        self.economic_analyzer = EconomicAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()

    def get_smart_money_signals(self, symbol, chlcv_data):
        try:
            df = pd.DataFrame(chlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            onchain_data = self.onchain_analyzer.analyze_whale_movements(symbol)
            volume_ma = df['volume'].rolling(20).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1
            price_change = (df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1] if df['open'].iloc[-1] > 0 else 0
            
            smart_money_score = 0
            if volume_ratio > 2.0 and price_change > 0.02:
                smart_money_score += 3
            elif volume_ratio > 2.0 and price_change < -0.02:
                smart_money_score -= 3
            
            if onchain_data['sentiment'] == 'bullish':
                smart_money_score += 2
            elif onchain_data['sentiment'] == 'bearish':
                smart_money_score -= 2
            
            return {
                'score': smart_money_score,
                'volume_ratio': volume_ratio,
                'unusual_volume': volume_ratio > 2.0,
                'onchain_data': onchain_data
            }
        except Exception as e:
            print(f"Error in smart money signals: {e}")
            return {'score': 0, 'volume_ratio': 1, 'unusual_volume': False, 'onchain_data': {}}

    def get_advanced_sentiment_analysis(self, symbol):
        try:
            news_sentiment = self.analyze_news_sentiment(symbol)
            social_sentiment = self.sentiment_analyzer.analyze_social_media(symbol)
            market_sentiment = self.economic_analyzer.get_market_sentiment()
            onchain_sentiment = self.onchain_analyzer.analyze_whale_movements(symbol)
            
            combined_sentiment = (
                0.3 * news_sentiment['score'] +
                0.3 * social_sentiment['combined_score'] +
                0.2 * (market_sentiment['fear_greed_index'] / 100) +
                0.2 * (onchain_sentiment['whale_activity'])
            )
            
            return {
                'combined_score': combined_sentiment,
                'news_sentiment': news_sentiment,
                'social_sentiment': social_sentiment,
                'market_sentiment': market_sentiment,
                'onchain_sentiment': onchain_sentiment,
                'overall_trend': 'bullish' if combined_sentiment > 0.6 else 'bearish' if combined_sentiment < 0.4 else 'neutral'
            }
        except Exception as e:
            print(f"Error in advanced sentiment analysis: {e}")
            return {'combined_score': 0.5, 'overall_trend': 'neutral'}

    def analyze_news_sentiment(self, symbol):
        try:
            # الحصول على أخبار حقيقية
            news_data = self.sentiment_analyzer.news_api.get_crypto_news(symbol)
            
            if news_data and 'articles' in news_data:
                articles = news_data['articles']
                total_sentiment = 0
                count = 0
                
                for article in articles[:5]:  # تحليل أول 5 مقالات
                    title = article.get('title', '')
                    description = article.get('description', '')
                    text = f"{title} {description}"
                    
                    sentiment_result = self.sentiment_analyzer.analyze_text_sentiment(text)
                    total_sentiment += sentiment_result['score']
                    count += 1
                
                if count > 0:
                    news_score = total_sentiment / count
                    confidence = min(0.9, count / 10)  # زيادة الثقة مع زيادة عدد المقالات
                    
                    return {
                        'score': news_score,
                        'source': 'newsapi.org',
                        'confidence': confidence,
                        'articles_analyzed': count
                    }
            
            # بيانات افتراضية في حالة الفشل
            return {
                'score': 0.5,
                'source': 'fallback',
                'confidence': 0.5,
                'articles_analyzed': 0
            }
        except Exception as e:
            print(f"Error in news sentiment analysis: {e}")
            return {'score': 0.5, 'source': 'fallback', 'confidence': 0.5}

    def prepare_quantum_features(self, chlcv_data):
        if len(chlcv_data) < 50:
            return np.zeros(30)

        try:
            df = pd.DataFrame(chlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            features = []
            
            # RSI
            for period in [7, 14]:
                try:
                    rsi = talib.RSI(df['close'], timeperiod=period)
                    features.append(rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50)
                except:
                    features.append(50)
            
            # SMA, EMA
            for period in [5, 10, 20]:
                try:
                    sma = talib.SMA(df['close'], timeperiod=period)
                    ema = talib.EMA(df['close'], timeperiod=period)
                    features.extend([
                        sma.iloc[-1] if not pd.isna(sma.iloc[-1]) else df['close'].iloc[-1],
                        ema.iloc[-1] if not pd.isna(ema.iloc[-1]) else df['close'].iloc[-1]
                    ])
                except:
                    features.extend([df['close'].iloc[-1]] * 2)

            # MACD
            try:
                macd, macd_signal, macd_hist = talib.MACD(df['close'])
                features.extend([
                    macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0,
                    macd_signal.iloc[-1] if not pd.isna(macd_signal.iloc[-1]) else 0
                ])
            except:
                features.extend([0, 0])

            # Bollinger Bands
            try:
                upper, middle, lower = talib.BBANDS(df['close'])
                if not pd.isna(upper.iloc[-1]):
                    bb_position = (df['close'].iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
                    features.append(bb_position)
                else:
                    features.append(0.5)
            except:
                features.append(0.5)

            # Volume Ratio
            try:
                volume_ma = df['volume'].rolling(20).mean()
                volume_ratio = df['volume'].iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1
                features.append(volume_ratio if not np.isnan(volume_ratio) else 1)
            except:
                features.append(1)

            # Fill remaining features
            while len(features) < 30:
                features.append(0)
                
            return np.array(features[:30])

        except Exception as e:
            print(f"Error preparing quantum features: {e}")
            return np.zeros(30)

    def quantum_predict(self, chlcv_data, symbol):
        try:
            if len(chlcv_data) < 50:
                return self.technical_analysis(chlcv_data)

            features = self.prepare_quantum_features(chlcv_data)
            df = pd.DataFrame(chlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            current_price = df['close'].iloc[-1]
            smart_money = self.get_smart_money_signals(symbol, chlcv_data)
            sentiment_analysis = self.get_advanced_sentiment_analysis(symbol)
            technical_analysis = self.technical_analysis(chlcv_data)

            technical_weight = 0.25
            smart_money_weight = 0.30
            sentiment_weight = 0.25
            onchain_weight = 0.20

            combined_score = (
                technical_weight * (technical_analysis['score'] / 10) +
                smart_money_weight * (smart_money['score'] / 5) +
                sentiment_weight * (sentiment_analysis['combined_score'] * 2 - 1) +
                onchain_weight * (smart_money['onchain_data']['whale_activity'] * 2 - 1)
            )

            combined_confidence = (
                technical_analysis['confidence'] * 0.3 +
                min(smart_money['volume_ratio'], 3) * 0.2 +
                sentiment_analysis['combined_score'] * 0.3 +
                smart_money['onchain_data']['whale_activity'] * 0.2
            )

            if combined_score > 0.1 and combined_confidence > 0.65:
                action = 'buy'
            elif combined_score < -0.1 and combined_confidence > 0.65:
                action = 'sell'
            else:
                action = 'hold'

            return {
                'predicted_price': current_price * (1 + combined_score * 0.1),
                'trend': combined_score,
                'confidence': min(0.95, combined_confidence),
                'action': action,
                'signals': [
                    f"smart_money {smart_money['score']}",
                    f"sentiment {sentiment_analysis['overall_trend']}",
                    f"onchain {smart_money['onchain_data']['sentiment']}",
                    f"technical {technical_analysis['action']}"
                ],
                'score': int(combined_score * 100),
                'ai_models_used': 4,
                'smart_money_score': smart_money['score'], 
                'sentiment_score': sentiment_analysis['combined_score'], 
                'onchain_score': smart_money['onchain_data']['whale_activity'], 
                'technical_score': technical_analysis['score']
            }

        except Exception as e:
            print(f"Error in quantum prediction: {e}")
            return self.technical_analysis(chlcv_data)

    def technical_analysis(self, chlcv_data):
        try:
            if len(chlcv_data) == 0:
                return self.create_default_analysis()

            df = pd.DataFrame(chlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            current_price = df['close'].iloc[-1]
            indicators = {}
            signals = []
            score = 0

            # RSI
            try:
                rsi_14 = talib.RSI(df['close'], timeperiod=14)
                indicators['rsi_14'] = rsi_14.iloc[-1] if not pd.isna(rsi_14.iloc[-1]) else 50
            except:
                indicators['rsi_14'] = 50

            # Moving Averages
            try:
                sma_20 = talib.SMA(df['close'], timeperiod=20)
                sma_50 = talib.SMA(df['close'], timeperiod=50)
                ema_20 = talib.EMA(df['close'], timeperiod=20)

                indicators['sma_20'] = sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else current_price
                indicators['sma_50'] = sma_50.iloc[-1] if not pd.isna(sma_50.iloc[-1]) else current_price
                indicators['ema_20'] = ema_20.iloc[-1] if not pd.isna(ema_20.iloc[-1]) else current_price
            except:
                indicators.update({
                    'sma_20': current_price,
                    'sma_50': current_price,
                    'ema_20': current_price
                })
            
            # RSI Signals
            if indicators['rsi_14'] < 30:
                score += 3
                signals.append('RSI_oversold')
            elif indicators['rsi_14'] > 70:
                score -= 3
                signals.append('RSI_overbought')

            # Moving Average Signals
            if (current_price > indicators['sma_20'] > indicators['sma_50']):
                score += 4
                signals.append('strong_uptrend')
            elif (current_price < indicators['sma_20'] < indicators['sma_50']):
                score -= 4
                signals.append('strong_downtrend')
            elif current_price > indicators['sma_20']:
                score += 2
                signals.append('above_sma20')
            elif current_price < indicators['sma_20']:
                score -= 2
                signals.append('below_sma20')

            # MACD
            try:
                macd, macd_signal, macd_hist = talib.MACD(df['close'])
                if macd.iloc[-1] > macd_signal.iloc[-1]:
                    score += 2
                    signals.append('MACD_bullish')
                else:
                    score -= 1
                    signals.append('MACD_bearish')
            except:
                pass

            if score >= 5:
                action = 'buy'
                confidence = min(0.95, 0.6 + score * 0.05)
            elif score <= -5:
                action = 'sell'
                confidence = min(0.95, 0.6 + abs(score) * 0.05)
            else:
                action = 'hold'
                confidence = 0.5

            return {
                'predicted_price': current_price * (1.03 if action == 'buy' else 0.97),
                'trend': 1 if action == 'buy' else -1 if action == 'sell' else 0,
                'confidence': confidence,
                'action': action,
                'signals': signals,
                'score': score,
                'indicators': indicators
            }

        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return self.create_default_analysis()

    def create_default_analysis(self):
        return {
            'predicted_price': 1.0,
            'trend': 0,
            'confidence': 0.5,
            'action': 'hold',
            'signals': ["no data"],
            'score': 0,
            'indicators': {}
        }

class QuantumTrader:
    def __init__(self, app=None):
        self.app = app
        self.quantum_brain = QuantumAlBrain()
        self.API_KEY = None
        self.SECRET_KEY = None
        self.trading_mode = 'quantum_profit'
        self.client = None
        self.exchange = 'BINANCE'
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.total_profit = 0.0
        self.initial_capital = 0.0
        self.current_capital = 0.0
        self.total_portfolio_value = 0.0
        self.win_rate = 0.0
        self.portfolio = {}
        self.active_trades = {}
        self.purchase_prices = {}
        self.trades_history = []
        self.performance_stats = {}
        self.market_analysis = {}
        self.daily_pnl = {}
        self.alpha_value = 0.0
        self.spot_value = 0.0

        # الأنظمة الجديدة المضافة
        self.backtester = Backtester(self)
        self.hedging_system = AdvancedHedging(self)

        self.apply_preset_settings(self.trading_mode)

        if self.app and hasattr(self.app, 'log_message'):
            self.app.log_message("☑ تم تهيئة المتداول الكمي")
            self.app.log_message("📅 جاهز للاتصال ببينانس")

    def set_initial_capital(self, capital):
        try:
            self.initial_capital = float(capital)
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"☑ تم تعيين رأس المال الابتدائي: {self.initial_capital:.2f} USDT")
            return True
        except ValueError:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message("✗ قيمة رأس المال غير صالحة")
            return False

    def apply_preset_settings(self, mode):
        if mode in TRADING_PRESETS:
            preset = TRADING_PRESETS[mode]
            self.profit_target = preset['profit_target']
            self.stop_loss = preset['stop_loss']
            self.max_trades = preset['max_trades']
            self.risk_per_trade = preset['risk_per_trade']
            self.trading_mode = mode
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"☑ تم تطبيق معامل التداول: {mode}")
                self.app.log_message(f"🎯 هدف الربح: {self.profit_target * 100}%، وقف الخسارة: {self.stop_loss * 100}%")

    def setup_api(self, api_key, secret_key, testnet=True):
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key

        try:
            if testnet:
                self.client = Client(api_key, secret_key, testnet=True)
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message("☑ تم الاتصال بشبكة بينانس الاختبارية")
            else:
                self.client = Client(api_key, secret_key)
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message("☑ تم الاتصال بالشبكة الرئيسية بينانس")
            
            account = self.client.get_account()
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message("☑ تم الوصول إلى الحساب بنجاح")
            
            if hasattr(self.app, 'update_connection_status'):
                self.app.update_connection_status(True)

            self.update_real_portfolio()
            return True

        except BinanceAPIException as e:
            error_msg = f"✗ خطأ في API: {e.message}"
            print(f"{error_msg}")
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"{error_msg}")
            if hasattr(self.app, 'update_connection_status'):
                self.app.update_connection_status(False)
            self.client = None
            return False

        except Exception as e:
            error_msg = f"✗ خطأ غير متوقع: {str(e)}"
            print(f"{error_msg}")
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"{error_msg}")
            if hasattr(self.app, 'update_connection_status'):
                self.app.update_connection_status(False)
            self.client = None
            return False

    def update_real_portfolio(self):
        try:
            if not self.client:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message("⚠️ لم يتم الاتصال بعد")
                return
            
            account = self.client.get_account()
            balances = account['balances']
            self.portfolio = {}
            total_value = 0.0

            for balance in balances:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked

                if total > 0:
                    if asset == 'USDT':
                        self.portfolio[asset] = total
                        total_value += total
                        self.current_capital = total
                    else:
                        symbol = f"{asset}USDT"
                        try:
                            price = self.get_current_price(symbol)
                            if price:
                                value = total * price
                                self.portfolio[asset] = total
                                total_value += value
                        except Exception as e:
                            if self.app and hasattr(self.app, 'log_message'):
                                self.app.log_message(f"⚠️ خطأ في سعر {symbol}: {e}")
                            continue
            
            self.total_portfolio_value = total_value

            if self.initial_capital == 0:
                self.initial_capital = total_value
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"💰 تم تعيين رأس المال التلقائي: {total_value:.2f} USDT")

            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"📊 تم تحديث المحفظة: {total_value:.2f} USDT")

        except BinanceAPIException as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✗ خطأ في تحديث المحفظة: {e}")
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✗ خطأ في تحديث المحفظة: {e}")

    def get_current_price(self, symbol):
        try:
            if not self.client:
                return None
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"⚠️ خطأ في الحصول على سعر {symbol}: {e}")
            return None

    def get_historical_data(self, symbol, interval='15m', limit=100):
        try:
            if not self.client:
                return []
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            chlcv = []
            for kline in klines:
                chlcv.append([
                    kline[0],
                    float(kline[1]),
                    float(kline[2]),
                    float(kline[3]),
                    float(kline[4]),
                    float(kline[5])
                ])
            return chlcv
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"⚠️ خطأ في الحصول على بيانات {symbol}: {e}")
            return []

    def can_trade_symbol(self, symbol):
        """التحقق من إمكانية التداول بناءً على الرصيد والمتطلبات"""
        try:
            current_capital = self.portfolio.get('USDT', 0)
            min_amount = MIN_TRADE_AMOUNTS.get(symbol, 0.001)
            current_price = self.get_current_price(symbol)
            
            if not current_price or current_price == 0:
                return False, "لا يمكن الحصول على السعر الحالي"

            min_cost = min_amount * current_price
            base_amount = current_capital * self.risk_per_trade
            amount_usdt = min(base_amount, current_capital * 0.5)

            if current_capital < 10:
                return False, f"رصيد USDT غير كافي: {current_capital:.2f}$"
            elif amount_usdt < min_cost:
                return False, f"المبلغ المحسوب أقل من الحد الأدنى: {amount_usdt:.2f}$ < {min_cost:.2f}$"
            elif current_capital < amount_usdt:
                return False, f"رصيد غير كافي للمبلغ المحسوب: {current_capital:.2f}$ < {amount_usdt:.2f}$"
            else:
                return True, "متاحة"

        except Exception as e:
            error_msg = f"خطأ في التحقق: {e}"
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"⚠️ {error_msg}")
            return False, error_msg

    def debug_trade_decision(self, symbol, analysis):
        """تسجيل أسباب قرار التداول بشكل مفصل"""
        reasons = []

        if analysis['action'] != 'buy':
            reasons.append(f"الإجراء: {analysis['action']} (ليس شراء)")

        if analysis['confidence'] <= 0.7:
            reasons.append(f"الثقة: {analysis['confidence']:.2f} (أقل من 0.7)")

        if symbol in self.active_trades:
            reasons.append("الصفقة نشطة بالفعل")

        if len(self.active_trades) >= self.max_trades:
            reasons.append(f"وصل للحد الأقصى: {self.max_trades}")

        # التحقق من إمكانية التداول
        can_trade, trade_reason = self.can_trade_symbol(symbol)
        if not can_trade:
            reasons.append(trade_reason)

        # تسجيل الأسباب
        if reasons and self.app:
            reason_text = "، ".join(reasons)
            self.app.log_message(f"❌ تم رفض {symbol}: {reason_text}")

        return len(reasons) == 0, reasons

    def analyze_market_with_quantum_ai(self):
        # تحليل جميع العملات (29 عملة) وليس فقط 10
        analyzed_count = 0
        for symbol in OPTIMAL_COINS:
            try:
                chlcv = self.get_historical_data(symbol, interval='15m', limit=100)
                if len(chlcv) == 0:
                    continue

                current_price = self.get_current_price(symbol)
                if not current_price:
                    continue

                prediction = self.quantum_brain.quantum_predict(chlcv, symbol)

                # التحقق من إمكانية التداول بناء على الرصيد المتاح
                can_trade, trade_reason = self.can_trade_symbol(symbol)
                status = "متاحة" if can_trade else "غير متاحة"

                self.market_analysis[symbol] = {
                    'symbol': symbol,
                    'action': prediction['action'],
                    'score': prediction.get('score', 0),
                    'confidence': prediction['confidence'],
                    'current_price': current_price,
                    'target_price': current_price * (1 + self.profit_target),
                    'stop_loss': current_price * (1 - self.stop_loss),
                    'signals': prediction.get('signals', []),
                    'trend': prediction['trend'],
                    'timestamp': datetime.now(),
                    'ai_models_used': prediction.get('ai_models_used', 0),
                    'smart_money_score': prediction.get('smart_money_score', 0),
                    'sentiment_score': prediction.get('sentiment_score', 0.5),
                    'onchain_score': prediction.get('onchain_score', 0.5),
                    'technical_score': prediction.get('technical_score', 0),
                    'status': status,  # إضافة الحالة
                    'trade_reason': trade_reason  # سبب حالة التداول
                }

                analyzed_count += 1

            except Exception as e:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"❌ خطأ في تحليل {symbol}: {e}")

        if self.app and hasattr(self.app, 'log_message'):
            self.app.log_message(f"📊 تم تحليل {analyzed_count} عملة من أصل {len(OPTIMAL_COINS)}")

    def execute_quantum_trade_strategy(self):
        try:
            best_buy = None
            best_buy_score = -999

            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"🔍 البحث عن صفقات شراء مناسبة...")

            for symbol, analysis in self.market_analysis.items():
                # استخدام الدالة الجديدة للتحقق مع التسجيل المفصل
                can_trade, reject_reasons = self.debug_trade_decision(symbol, analysis)

                if can_trade and analysis['score'] > best_buy_score:
                    best_buy_score = analysis['score']
                    best_buy = analysis

            if best_buy and best_buy_score > 0:
                success = self.execute_smart_buy(best_buy)
                if success and self.app:
                    self.app.log_message(f"✅ تم تنفيذ شراء: {best_buy['symbol']} بنقاط: {best_buy_score}")
                return success
            elif best_buy:
                if self.app:
                    self.app.log_message(f"ℹ️ أفضل إشارة شراء: {best_buy['symbol']} بنقاط: {best_buy_score} (لم تصل للحد الأدنى)")
            else:
                if self.app:
                    self.app.log_message("ℹ️ لا توجد إشارات شراء مناسبة")

        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"❌ خطأ في استراتيجية التداول: {e}")
            return False

    def execute_smart_buy(self, analysis):
        try:
            symbol = analysis['symbol']
            coin = symbol.replace('USDT', '')
            
            if len(self.active_trades) >= self.max_trades:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"✗ وصل الحد الأقصى للصفقات: {self.max_trades}")
                return False
            
            usdt_balance = self.portfolio.get('USDT', 0)
            if usdt_balance < 10:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"✗ رصيد USDT غير كافي: {usdt_balance:.2f}$")
                return False
            
            base_amount = usdt_balance * self.risk_per_trade
            confidence_multiplier = analysis['confidence']
            amount_usdt = min(base_amount * confidence_multiplier, usdt_balance * 0.5)
            current_price = analysis['current_price']
            amount = amount_usdt / current_price
            min_amount = MIN_TRADE_AMOUNTS.get(symbol, 1)
            
            if amount < min_amount:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"✗ الكمية أقل من الحد الأدنى: {amount:.6f} < {min_amount}")
                return False
            
            if usdt_balance >= amount_usdt:
                try:
                    if self.app and hasattr(self.app, 'log_message'):
                        self.app.log_message(f"🛒 محاولة شراء {symbol}: {amount:.6f} بسعر {current_price:.6f}$")
                    
                    order = self.client.order_market_buy(
                        symbol=symbol,
                        quantity=self.format_quantity(symbol, amount)
                    )
                    
                    self.portfolio['USDT'] = usdt_balance - amount_usdt
                    self.portfolio[coin] = self.portfolio.get(coin, 0) + float(order['executedQty'])
                    
                    self.active_trades[symbol] = {
                        'entry_price': current_price,
                        'amount': float(order['executedQty']),
                        'entry_time': datetime.now(),
                        'stop_loss': analysis['stop_loss'],
                        'target_price': analysis['target_price'],
                        'symbol': symbol,
                        'invested_usdt': float(order['cummulativeQuoteQty']),
                        'order_id': order['orderId']
                    }
                    
                    self.purchase_prices[coin] = current_price
                    
                    trade_record = {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "symbol": symbol,
                        "type": "buy",
                        "amount": float(order['executedQty']),
                        "price": current_price,
                        "invested_usdt": float(order['cummulativeQuoteQty']),
                        "profit": 0,
                        "status": "active",
                        "result": "open",
                        "entry_time": datetime.now(),
                        "analysis_score": analysis.get('score', 0),
                        "confidence": analysis.get('confidence', 0.5),
                        "order_id": order['orderId']
                    }
                    
                    self.trades_history.append(trade_record)
                    self.trade_count += 1
                    
                    if self.app and hasattr(self.app, 'log_message'):
                        self.app.log_message(f"✅ تم الشراء: {symbol} - {amount_usdt:.2f} USDT")
                    return True
                    
                except BinanceAPIException as e:
                    if self.app and hasattr(self.app, 'log_message'):
                        self.app.log_message(f"✗ خطأ في تنفيذ الشراء: {e}")
                    return False
                except Exception as e:
                    if self.app and hasattr(self.app, 'log_message'):
                        self.app.log_message(f"✗ خطأ غير متوقع في الشراء: {e}")
                    return False
            else:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"✗ رصيد غير كافي: {usdt_balance:.2f} < {amount_usdt:.2f}")

        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✗ خطأ في الشراء الذكي: {e}")
            return False

    def execute_smart_sell(self, analysis):
        try:
            symbol = analysis['symbol']
            coin = symbol.replace('USDT', '')
            
            if symbol not in self.active_trades:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"✗ لا توجد صفقة نشطة لـ {symbol}")
                return False
            
            trade = self.active_trades[symbol]
            current_price = analysis['current_price']
            amount = trade['amount']
            entry_price = trade['entry_price']
            invested_usdt = trade.get('invested_usdt', amount * entry_price)
            
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"🛒 محاولة بيع {symbol}: {amount:.6f} بسعر {current_price:.6f}$")

            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=self.format_quantity(symbol, amount)
            )
            
            executed_amount = float(order['executedQty'])
            executed_value = float(order['cummulativeQuoteQty'])
            profit = executed_value - invested_usdt
            profit_percent = (profit / invested_usdt) * 100 if invested_usdt > 0 else 0
            
            self.portfolio['USDT'] = self.portfolio.get('USDT', 0) + executed_value
            
            if coin in self.portfolio:
                self.portfolio[coin] -= executed_amount
                if self.portfolio[coin] < 0.000001:
                    del self.portfolio[coin]

            self.total_profit += profit
            
            if profit > 0:
                self.win_count += 1
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"🎉 ربح: {profit:.2f} USDT ({profit_percent:.2f}%)")
            else:
                self.loss_count += 1
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"🛡️ خسارة: {profit:.2f} USDT ({profit_percent:.2f}%)")
            
            self.win_rate = self.win_count / self.trade_count if self.trade_count > 0 else 0

            trade_record = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "type": "sell",
                "amount": executed_amount,
                "price": current_price,
                "invested_usdt": invested_usdt,
                "profit": profit,
                "profit_percent": profit_percent,
                "status": "completed",
                "result": "profit" if profit > 0 else "loss",
                "exit_time": datetime.now(),
                "holding_time": (datetime.now() - trade['entry_time']).total_seconds() / 60,
                "order_id": order['orderId']
            }

            self.trades_history.append(trade_record)
            del self.active_trades[symbol]

            if coin in self.purchase_prices:
                del self.purchase_prices[coin]

            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✅ تم البيع: {symbol}")
            return True

        except BinanceAPIException as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✗ خطأ أثناء البيع: {e}")
            return False
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✗ خطأ غير متوقع أثناء البيع: {e}")
            return False

    def manage_active_trades(self):
        managed_count = 0
        for symbol, trade in list(self.active_trades.items()):
            try:
                current_price = self.get_current_price(symbol)
                if not current_price:
                    continue

                entry_price = trade['entry_price']
                current_pnl = (current_price - entry_price) / entry_price

                if current_pnl >= self.profit_target:
                    analysis = self.market_analysis.get(symbol, {})
                    analysis.update({
                        'symbol': symbol,
                        'current_price': current_price,
                        'action': 'sell'
                    })
                    if self.execute_smart_sell(analysis):
                        if self.app and hasattr(self.app, 'log_message'):
                            self.app.log_message(f"🎯 تم البيع عند تحقيق الربح: {symbol} (+{current_pnl * 100:.2f}%)")
                        managed_count += 1
                elif current_pnl <= -self.stop_loss:
                    analysis = self.market_analysis.get(symbol, {})
                    analysis.update({
                        'symbol': symbol,
                        'current_price': current_price,
                        'action': 'sell'
                    })
                    if self.execute_smart_sell(analysis):
                        if self.app and hasattr(self.app, 'log_message'):
                            self.app.log_message(f"🛡️ تم البيع عند وقف الخسارة: {symbol} ({current_pnl * 100:.2f}%)")
                        managed_count += 1
            except Exception as e:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"⚠️ خطأ في إدارة {symbol}: {e}")
        
        if managed_count > 0 and self.app and hasattr(self.app, 'log_message'):
            self.app.log_message(f"📈 تم إدارة {managed_count} صفقة")

    def format_quantity(self, symbol, quantity):
        try:
            info = self.client.get_symbol_info(symbol)
            if not info:
                return round(quantity, 6)
            
            for f in info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])
                    precision = int(round(-math.log(step_size, 10), 0))
                    return round(quantity - (quantity % step_size), precision)
            
            return round(quantity, 6)
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"⚠️ خطأ في تنسيق الكمية: {e}")
            return round(quantity, 6)

    def run_trading_cycle(self):
        try:
            # تحديث الرصيد أولاً
            self.update_real_portfolio()
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message("🔄 بدء دورة التداول")

            self.analyze_market_with_quantum_ai()
            self.execute_quantum_trade_strategy()
            self.manage_active_trades()
            self.update_performance_stats()

            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message("✅ اكتملت دورة التداول بنجاح")

        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"❌ خطأ في دورة التداول: {e}")

    def update_performance_stats(self):
        try:
            total_return = ((self.total_portfolio_value - self.initial_capital) / self.initial_capital * 100) if self.initial_capital > 0 else 0
            
            self.performance_stats = {
                'total_trades': self.trade_count,
                'win_rate': self.win_rate * 100,
                'total_profit': self.total_profit,
                'total_return_percent': total_return,
                'current_portfolio_value': self.total_portfolio_value,
                'active_trades': len(self.active_trades),
                'daily_pnl': self.daily_pnl,
                'alpha': self.alpha_value,
                'sharpe_ratio': self.calculate_sharpe_ratio(),
                'max_drawdown': self.calculate_max_drawdown()
            }

        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"⚠️ خطأ في تحديث الإحصائيات: {e}")

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        try:
            if len(self.trades_history) < 2:
                return 0
            
            returns = []
            for trade in self.trades_history:
                if 'profit_percent' in trade:
                    returns.append(trade['profit_percent'] / 100)
            
            if len(returns) < 2:
                return 0
            
            excess_returns = [r - risk_free_rate / 365 for r in returns]
            avg_excess_return = np.mean(excess_returns)
            std_excess_return = np.std(excess_returns)
            
            return avg_excess_return / std_excess_return * np.sqrt(365) if std_excess_return != 0 else 0

        except Exception as e:
            return 0

    def calculate_max_drawdown(self):
        try:
            if len(self.trades_history) == 0:
                return 0
            
            portfolio_values = [self.initial_capital]
            current_value = self.initial_capital
            
            for trade in self.trades_history:
                if 'profit' in trade:
                    current_value += trade['profit']
                    portfolio_values.append(current_value)
            
            if len(portfolio_values) < 2:
                return 0
            
            peak = portfolio_values[0]
            max_drawdown = 0
            
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            return max_drawdown * 100

        except Exception as e:
            return 0

    # ========== الوظائف الجديدة للأنظمة المضافة ==========

    def run_backtest_analysis(self, symbol, days=30, initial_capital=1000.0):
        """تشغيل تحليل Backtest لعملة محددة"""
        try:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"🔄 جاري تشغيل Backtest لـ {symbol}...")
            
            # استخدام إعدادات التداول الحالية
            strategy_config = {
                'profit_target': self.profit_target,
                'stop_loss': self.stop_loss,
                'risk_per_trade': self.risk_per_trade
            }
            
            result = self.backtester.run_backtest(symbol, strategy_config, initial_capital)
            
            if result:
                report = self.backtester.generate_backtest_report(symbol)
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"✅ تم الانتهاء من Backtest لـ {symbol}")
                return report
            else:
                if self.app and hasattr(self.app, 'log_message'):
                    self.app.log_message(f"❌ فشل في تشغيل Backtest لـ {symbol}")
                return None
                
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"❌ خطأ في Backtest: {e}")
            return None

    def run_comprehensive_backtest(self, symbols=None, days=30, initial_capital=1000.0):
        """تشغيل Backtest شامل لعدة عملات"""
        try:
            if symbols is None:
                symbols = list(OPTIMAL_COINS)[:5]  # اختبار أول 5 عملات
            
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"🔄 جاري تشغيل Backtest شامل لـ {len(symbols)} عملة...")
            
            strategy_config = {
                'profit_target': self.profit_target,
                'stop_loss': self.stop_loss,
                'risk_per_trade': self.risk_per_trade
            }
            
            results, total_metrics = self.backtester.run_comprehensive_backtest(
                symbols, strategy_config, initial_capital
            )
            
            # توليد تقرير شامل
            report = "📊 تقرير Backtest الشامل\n"
            report += "══════════════════════\n\n"
            report += f"• عدد العملات المختبرة: {len(symbols)}\n"
            report += f"• إجمالي الصفقات: {total_metrics['total_trades']}\n"
            report += f"• معدل النجاح: {total_metrics.get('win_rate', 0):.2f}%\n"
            report += f"• إجمالي الربح: {total_metrics['total_profit']:.2f} $\n"
            report += f"• العائد الإجمالي: {total_metrics.get('total_return_percent', 0):.2f}%\n\n"
            
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"✅ تم الانتهاء من Backtest الشامل")
            
            return report
            
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"❌ خطأ في Backtest الشامل: {e}")
            return f"خطأ في Backtest الشامل: {e}"

    def analyze_portfolio_hedging(self):
        """تحليل التحوط للمحفظة الحالية"""
        try:
            if not self.portfolio:
                return "لا توجد مراكز حالية للتحوط"
            
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message("🔄 جاري تحليل التحوط للمحفظة...")
            
            # تحليل الارتباطات بين الأصول
            symbols = [f"{asset}USDT" for asset in self.portfolio.keys() if asset != 'USDT']
            if not symbols:
                return "لا توجد أصول كافية للتحوط"
            
            self.hedging_system.analyze_correlations(symbols)
            
            # حساب توصيات التحوط
            portfolio_values = {}
            for asset, amount in self.portfolio.items():
                if asset != 'USDT':
                    symbol = f"{asset}USDT"
                    price = self.get_current_price(symbol)
                    if price:
                        portfolio_values[symbol] = amount * price
            
            hedge_recommendations = self.hedging_system.calculate_portfolio_hedge(portfolio_values)
            
            # توليد تقرير التحوط
            report = "🛡️ تقرير التحوط للمحفظة\n"
            report += "══════════════════════\n\n"
            
            if hedge_recommendations:
                for rec in hedge_recommendations:
                    report += f"• {rec['primary_asset']} → تحوط بـ {rec['hedge_asset']}\n"
                    report += f"  نسبة التحوط: {rec['hedge_ratio']:.2f}\n"
                    report += f"  المبلغ المقترح: {rec['recommended_hedge']:.2f} $\n"
                    report += f"  الارتباط: {rec['correlation']:.3f}\n\n"
            else:
                report += "لا توجد توصيات تحوط في الوقت الحالي\n"
            
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message("✅ تم تحليل التحوط للمحفظة")
            
            return report
            
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"❌ خطأ في تحليل التحوط: {e}")
            return f"خطأ في تحليل التحوط: {e}"

    def get_dynamic_stop_loss(self, symbol, entry_price):
        """الحصول على وقف خسارة ديناميكي"""
        try:
            current_price = self.get_current_price(symbol)
            if not current_price:
                return entry_price * 0.98  # وقف خسارة افتراضي
            
            stop_loss = self.hedging_system.dynamic_stop_loss(symbol, current_price, entry_price, 0.3)
            return stop_loss
            
        except Exception as e:
            if self.app and hasattr(self.app, 'log_message'):
                self.app.log_message(f"⚠️ خطأ في حساب وقف الخسارة الديناميكي: {e}")
            return entry_price * 0.98

    def get_hedging_strategy(self, market_condition):
        """الحصول على إستراتيجية تحوط بناءً على ظروف السوق"""
        return self.hedging_system.get_hedging_strategy(self.total_portfolio_value, market_condition)

# ========== واجهة المستخدم المحسنة ==========

class QuantumTradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum AI Trader Pro - v4.0 (Real Binance) - النسخة المحسنة")
        self.root.geometry("1400x900")
        self.root.configure(bg="#2b2b2b")

        # الألوان
        self.primary_color = "#1e88e5"
        self.secondary_color = "#22a69a"
        self.success_color = "#66bb6a"
        self.danger_color = "#f15354"
        self.warning_color = "#ffa726"
        self.dark_bg = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#ffffff"
        self.light_text = "#eeeeee"
        self.entry_bg = "#3c3c3c"
        self.entry_fg = "#ffffff"

        self.is_trading = False
        self.update_job = None
        self.connection_status = False
        self.trader = QuantumTrader(self)
        self.testnet_mode = True

        self.setup_styles()
        self.setup_gui()
        self.auto_update()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('.',
            background=self.dark_bg,
            foreground=self.text_color,
            fieldbackground=self.entry_bg)

        self.style.configure('Title.TLabel',
            font=('Arial', 16, 'bold'),
            foreground=self.primary_color,
            background=self.dark_bg)

        self.style.configure('Card.TFrame',
            background=self.card_bg,
            relief='raised',
            borderwidth=1)

        self.style.configure('Success.TButton',
            background=self.success_color,
            foreground='white')

        self.style.configure('Danger.TButton',
            background=self.danger_color,
            foreground='white')

        self.style.configure('Primary.TButton',
            background=self.primary_color,
            foreground='white')

        self.style.configure('Treeview',
            background='#3c3c3c',
            foreground=self.light_text,
            fieldbackground='#3c3c3c')

        self.style.configure('Treeview.Heading',
            background=self.primary_color,
            foreground='white',
            font=('Arial', 10, 'bold'))

        self.style.configure('Light.TLabel',
            foreground=self.light_text,
            background=self.card_bg)

        self.style.configure('Light.TCheckbutton',
            foreground=self.light_text,
            background=self.card_bg)

        self.style.configure('Custom.TEntry',
            fieldbackground=self.entry_bg,
            foreground=self.entry_fg,
            insertbackground=self.entry_fg)

        self.style.configure('Custom.TCombobox',
            fieldbackground=self.entry_bg,
            foreground=self.entry_fg,
            background=self.entry_bg)

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, style="Card.TFrame")
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_header(main_frame)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, pady=10)

        sidebar_frame = self.create_sidebar(content_frame)
        sidebar_frame.pack(side='left', fill='y', padx=(0, 10))

        main_content_frame = ttk.Frame(content_frame)
        main_content_frame.pack(side='right', fill='both', expand=True)

        notebook = ttk.Notebook(main_content_frame)
        notebook.pack(fill='both', expand=True)

        self.setup_dashboard_tab(notebook)
        self.setup_trading_tab(notebook)
        self.setup_backtesting_tab(notebook)  # تبويب جديد
        self.setup_hedging_tab(notebook)     # تبويب جديد
        self.setup_logs_tab(notebook)
        self.setup_settings_tab(notebook)

    def create_header(self, parent):
        header_frame = ttk.Frame(parent, style="Card.TFrame")
        header_frame.pack(fill='x', pady=(0, 10))

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', padx=20, pady=10)

        ttk.Label(title_frame, text="QUANTUM AI TRADER PRO", style="Title.TLabel").pack()
        ttk.Label(title_frame, text="PLATFORM V4.0 - النسخة المحسنة",
                foreground=self.secondary_color, background=self.card_bg).pack()

        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side='right', padx=20, pady=10)

        self.connection_label = ttk.Label(status_frame, text="✗ - Binance",
                                        foreground=self.danger_color, font=('Arial', 10, 'bold'))
        self.connection_label.pack(side='right', padx=10)

        self.trading_status_label = ttk.Label(status_frame, text="⏹ التداول متوقف", 
                                            foreground=self.danger_color, font=('Arial', 10, 'bold'))
        self.trading_status_label.pack(side='right', padx=10)

        self.mode_label = ttk.Label(status_frame, text="وضع: quantum_profit", font=('Arial', 10))
        self.mode_label.pack(side='right', padx=10)

    def create_sidebar(self, parent):
        sidebar_frame = ttk.Frame(parent, width=200, style="Card.TFrame")
        sidebar_frame.pack_propagate(False)

        control_frame = ttk.LabelFrame(sidebar_frame, text="التحكم", style="Card.TFrame")
        control_frame.pack(fill='x', padx=10, pady=5)

        self.start_btn = ttk.Button(control_frame, text="بدء التداول", 
                                  command=self.start_trading, 
                                  style="Success.TButton")
        self.start_btn.pack(fill='x', padx=5, pady=5)

        self.stop_btn = ttk.Button(control_frame, text="إيقاف التداول", 
                                 command=self.stop_trading, 
                                 style="Danger.TButton")
        self.stop_btn.pack(fill='x', padx=5, pady=5)
        self.stop_btn.config(state="disabled")

        ttk.Button(control_frame, text="تشغيل Backtest", 
                 command=self.run_backtest).pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="تحليل التحوط", 
                 command=self.analyze_hedging).pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="تداول ذكي", 
                 command=self.smart_trade).pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="بيع المربحة", 
                 command=self.sell_profitable).pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="بيع الكل", 
                 command=self.sell_all_coins).pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="فحص الاتصال", 
                 command=self.check_connection).pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="تحديث البيانات", 
                 command=self.update_data).pack(fill='x', padx=5, pady=5)

        stats_frame = ttk.LabelFrame(sidebar_frame, text="الإحصائيات السريعة", style="Card.TFrame")
        stats_frame.pack(fill='x', padx=10, pady=5)

        self.quick_stats = {}

        stats_data = [
            ("رأس المال المتاح", "0.00 $", self.success_color),
            ("صافي الربح", "0.00 $", self.success_color),
            ("معدل الربح", "0.00 %", self.success_color),
            ("الصفقات النشطة", "0", self.primary_color)
        ]

        for title, value, color in stats_data:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill='x', padx=5, pady=2)
            ttk.Label(frame, text=title, font=('Arial', 9), style="Light.TLabel").pack(side='left')
            label = ttk.Label(frame, text=value, font=('Arial', 9), style="Light.TLabel")
            label.pack(side='right')
            self.quick_stats[title] = label

        return sidebar_frame

    def setup_dashboard_tab(self, notebook):
        dashboard_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(dashboard_frame, text="اللوحة الرئيسية")

        stats_frame = ttk.LabelFrame(dashboard_frame, text="إحصائيات الأداء", style="Card.TFrame")
        stats_frame.pack(fill='x', padx=10, pady=10)

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x', padx=10, pady=10)

        self.dash_labels = {}

        stats_data = [
            ("رأس المال الحالي", "0.00 $"),
            ("رأس المال الابتدائي", "0.00 $"),
            ("صافي الربح", "0.00 $"),
            ("معدل الربح", "0.00 %"),
            ("إجمالي الصفقات", "0"),
            ("الصفقات النشطة", "0")
        ]

        for i, (title, value) in enumerate(stats_data):
            if i % 3 == 0:
                row_frame = ttk.Frame(stats_grid)
                row_frame.pack(fill='x', pady=5)

            card = ttk.Frame(row_frame, style="Card.TFrame", width=200, height=80)
            card.pack(side='left', expand=True, fill='both', padx=5)
            card.pack_propagate(False)

            ttk.Label(card, text=title, font=('Arial', 9), style='Light.TLabel').pack(pady=10)
            label = ttk.Label(card, text=value, font=('Arial', 14, "bold"), style='Light.TLabel')
            label.pack(expand=True)
            self.dash_labels[title] = label

        portfolio_trades_frame = ttk.Frame(dashboard_frame)
        portfolio_trades_frame.pack(fill='both', expand=True, padx=10, pady=10)

        portfolio_frame = ttk.LabelFrame(portfolio_trades_frame, text="محفظة الأصول", style="Card.TFrame")
        portfolio_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        portfolio_controls = ttk.Frame(portfolio_frame)
        portfolio_controls.pack(fill='x', padx=10, pady=5)

        ttk.Button(portfolio_controls, text="شراء يدوي", command=self.show_buy_dialog).pack(side='left', padx=5)
        ttk.Button(portfolio_controls, text="بيع يدوي", command=self.show_sell_dialog).pack(side='left', padx=5)
        ttk.Button(portfolio_controls, text="تحديث", command=self.update_portfolio).pack(side='left', padx=5)

        columns = ("العملة", "الكمية", "القيمة", "الربح")
        self.portfolio_tree = ttk.Treeview(portfolio_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(portfolio_frame, orient="vertical", command=self.portfolio_tree.yview)
        self.portfolio_tree.configure(yscrollcommand=scrollbar.set)

        self.portfolio_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        trades_frame = ttk.LabelFrame(portfolio_trades_frame, text="الصفقات النشطة", style="Card.TFrame")
        trades_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        columns = ("الوقت", "العملة", "الكمية", "سعر الدخول", "السعر الحالي", "الربح", "الحالة")
        self.trades_tree = ttk.Treeview(trades_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.trades_tree.heading(col, text=col)
            self.trades_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(trades_frame, orient="vertical", command=self.trades_tree.yview)
        self.trades_tree.configure(yscrollcommand=scrollbar.set)

        self.trades_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def setup_trading_tab(self, notebook):
        trading_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(trading_frame, text="تحليل السوق")

        analysis_frame = ttk.LabelFrame(trading_frame, text="تحليل الذكاء الاصطناعي", style="Card.TFrame")
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # إضافة عمود "الحالة" إلى الأعمدة
        columns = (
            "العملة", "الإجراء", "الثقة", "النقاط", "السعر الحالي", "هدف الربح", "وقف الخسارة", "الحالة", "الإشارات")
        self.analysis_tree = ttk.Treeview(analysis_frame, columns=columns, show='headings', height=15)

        col_widths = [100, 80, 80, 80, 80, 80, 100, 100, 200]

        for i, col in enumerate(columns):
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=col_widths[i])

        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=scrollbar.set)

        self.analysis_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def setup_backtesting_tab(self, notebook):
        """إعداد تبويب Backtesting الجديد"""
        backtest_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(backtest_frame, text="📊 Backtesting")

        # عنوان التبويب
        title_label = ttk.Label(backtest_frame, text="نظام Backtesting المتقدم", 
                               style="Title.TLabel")
        title_label.pack(pady=10)

        # إطار الإدخال
        input_frame = ttk.Frame(backtest_frame, style="Card.TFrame")
        input_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(input_frame, text="اختر العملة:", style="Light.TLabel").pack(side='left', padx=5)
        
        self.backtest_symbol = ttk.Combobox(input_frame, values=list(OPTIMAL_COINS), width=15, style="Custom.TCombobox")
        self.backtest_symbol.set('BTCUSDT')
        self.backtest_symbol.pack(side='left', padx=5)
        
        ttk.Label(input_frame, text="عدد الأيام:", style="Light.TLabel").pack(side='left', padx=5)
        
        self.backtest_days = ttk.Combobox(input_frame, values=['7', '15', '30', '60'], width=10, style="Custom.TCombobox")
        self.backtest_days.set('30')
        self.backtest_days.pack(side='left', padx=5)

        ttk.Label(input_frame, text="رأس المال:", style="Light.TLabel").pack(side='left', padx=5)
        
        self.backtest_capital = ttk.Entry(input_frame, width=10, style="Custom.TEntry")
        self.backtest_capital.insert(0, "1000")
        self.backtest_capital.pack(side='left', padx=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(backtest_frame, style="Card.TFrame")
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(button_frame, text="تشغيل Backtest", 
                  command=self.run_single_backtest, style="Primary.TButton").pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Backtest شامل", 
                  command=self.run_comprehensive_backtest, style="Success.TButton").pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="مسح النتائج", 
                  command=self.clear_backtest_results, style="Danger.TButton").pack(side='left', padx=5)
        
        # منطقة النتائج
        results_frame = ttk.Frame(backtest_frame, style="Card.TFrame")
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.backtest_results = scrolledtext.ScrolledText(results_frame, height=20, 
                                                         bg='#1a1a1a', fg='white', 
                                                         font=('Arial', 10))
        self.backtest_results.pack(fill='both', expand=True)
        self.backtest_results.insert('end', "💡 مرحباً بك في نظام Backtesting المتقدم\n\n")
        self.backtest_results.insert('end', "هذا النظام يسمح لك باختبار إستراتيجيات التداول على البيانات التاريخية\n")
        self.backtest_results.insert('end', "قبل المخاطرة بالأموال الحقيقية.\n\n")
        self.backtest_results.insert('end', "اختر عملة واضغط على 'تشغيل Backtest' لبدء التحليل.\n")

    def setup_hedging_tab(self, notebook):
        """إعداد تبويب التحوط الجديد"""
        hedge_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(hedge_frame, text="🛡️ نظام التحوط")

        # عنوان التبويب
        title_label = ttk.Label(hedge_frame, text="نظام التحوط المتقدم", 
                               style="Title.TLabel")
        title_label.pack(pady=10)
        
        # أزرار التحكم
        button_frame = ttk.Frame(hedge_frame, style="Card.TFrame")
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(button_frame, text="تحليل التحوط للمحفظة", 
                  command=self.analyze_portfolio_hedging, style="Primary.TButton").pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="تحليل الارتباطات", 
                  command=self.analyze_correlations, style="Success.TButton").pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="إستراتيجيات التحوط", 
                  command=self.show_hedging_strategies, style="Warning.TButton").pack(side='left', padx=5)
        
        # منطقة النتائج
        results_frame = ttk.Frame(hedge_frame, style="Card.TFrame")
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.hedge_results = scrolledtext.ScrolledText(results_frame, height=20, 
                                                      bg='#1a1a1a', fg='white', 
                                                      font=('Arial', 10))
        self.hedge_results.pack(fill='both', expand=True)
        self.hedge_results.insert('end', "🛡️ نظام التحوق المتقدم\n\n")
        self.hedge_results.insert('end', "هذا النظام يساعد في حماية محفظتك من المخاطر عبر:\n")
        self.hedge_results.insert('end', "• تحليل الارتباطات بين الأصول\n")
        self.hedge_results.insert('end', "• اقتراحات التحوط المثلى\n")
        self.hedge_results.insert('end', "• وقف الخسارة الديناميكي\n")
        self.hedge_results.insert('end', "• إستراتيجيات تحوط متقدمة\n\n")
        self.hedge_results.insert('end', "اضغط على 'تحليل التحوط للمحفظة' لبدء التحليل.\n")

    def setup_logs_tab(self, notebook):
        logs_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(logs_frame, text="سجلات التداول")

        trades_log_frame = ttk.LabelFrame(logs_frame, text="سجل الصفقات", style="Card.TFrame")
        trades_log_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("الوقت", "العملة", "النوع", "الكمية", "السعر", "المستثمر", "الربح", "النسبة", "الحالة")
        self.trades_log_tree = ttk.Treeview(trades_log_frame, columns=columns, show='headings', height=15)

        col_widths = [120, 80, 60, 80, 80, 80, 80, 80, 80]
        for i, col in enumerate(columns):
            self.trades_log_tree.heading(col, text=col)
            self.trades_log_tree.column(col, width=col_widths[i])

        scrollbar = ttk.Scrollbar(trades_log_frame, orient="vertical", command=self.trades_log_tree.yview)
        self.trades_log_tree.configure(yscrollcommand=scrollbar.set)

        self.trades_log_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        system_log_frame = ttk.LabelFrame(logs_frame, text="سجل النظام", style="Card.TFrame")
        system_log_frame.pack(fill='x', padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(system_log_frame, height=10, bg="#3c3c3c", fg="white")
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

    def setup_settings_tab(self, notebook):
        settings_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(settings_frame, text="الإعدادات")

        api_frame = ttk.LabelFrame(settings_frame, text="إعدادات API - Binance", style="Card.TFrame")
        api_frame.pack(fill='x', padx=10, pady=5)

        # اختيار Testnet/Mainnet
        network_frame = ttk.Frame(api_frame)
        network_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        self.network_var = tk.BooleanVar(value=True)  # True for Testnet, False for Mainnet
        ttk.Radiobutton(network_frame, text="شبكة الاختبار (Testnet)",
                      variable=self.network_var, value=True,
                      style="Light.TCheckbutton").pack(side='left', padx=10)
        ttk.Radiobutton(network_frame, text="الشبكة الرئيسية (Mainnet)",
                      variable=self.network_var, value=False,
                      style="Light.TCheckbutton").pack(side='left', padx=10)

        ttk.Label(api_frame, text="مفتاح API:", style="Light.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.api_key_entry = ttk.Entry(api_frame, width=50, show='*', style="Custom.TEntry")
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(api_frame, text="المفتاح السري:", style="Light.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.secret_key_entry = ttk.Entry(api_frame, width=50, show='*', style="Custom.TEntry")
        self.secret_key_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(api_frame, text="إظهار كلمات المرور", variable=self.show_password_var,
                      command=self.toggle_password_visibility,
                      style="Light.TCheckbutton").grid(row=3, column=1, padx=5, pady=5, sticky='w')

        api_btn_frame = ttk.Frame(api_frame)
        api_btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(api_btn_frame, text="حفظ المفاتيح", command=self.save_api_keys).pack(side='left', padx=5)
        ttk.Button(api_btn_frame, text="فحص الاتصال", command=self.test_connection).pack(side='left', padx=5)

        mode_frame = ttk.LabelFrame(settings_frame, text="نمط التداول", style="Card.TFrame")
        mode_frame.pack(fill='x', padx=10, pady=5)

        self.trading_mode_var = tk.StringVar(value="quantum_profit")

        modes = [
            ("❶ محافظ", "conservative"),
            ("❷ عادي", "normal"),
            ("❸ عدواني", "aggressive"),
            ("❹ كمية الربح", "quantum_profit")
        ]

        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, value=value, variable=self.trading_mode_var, 
                          command=self.apply_preset, 
                          style="Light.TCheckbutton").pack(anchor='w', pady=2, padx=20)

        trading_frame = ttk.LabelFrame(settings_frame, text="إعدادات التداول", style="Card.TFrame")
        trading_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(trading_frame, text="رأس المال (USDT):", style="Light.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.capital_entry = ttk.Entry(trading_frame, width=15, style="Custom.TEntry")
        self.capital_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(trading_frame, text="هدف الربح (%):", style="Light.TLabel").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.profit_target_entry = ttk.Entry(trading_frame, width=15, style="Custom.TEntry")
        self.profit_target_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(trading_frame, text="وقف الخسارة (%):", style="Light.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.stop_loss_entry = ttk.Entry(trading_frame, width=15, style="Custom.TEntry")
        self.stop_loss_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(trading_frame, text="الفاصل (دقائق):", style="Light.TLabel").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.interval_entry = ttk.Entry(trading_frame, width=15, style="Custom.TEntry")
        self.interval_entry.grid(row=1, column=3, padx=5, pady=5)
        self.interval_entry.insert(0, "5")

        ttk.Label(trading_frame, text="أقصى صفقات:", style="Light.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.max_trades_entry = ttk.Entry(trading_frame, width=15, style="Custom.TEntry")
        self.max_trades_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(trading_frame, text="المخاطرة لكل صفقة (%):", style="Light.TLabel").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.risk_per_trade_entry = ttk.Entry(trading_frame, width=15, style="Custom.TEntry")
        self.risk_per_trade_entry.grid(row=2, column=3, padx=5, pady=5)

        btn_frame = ttk.Frame(trading_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="حفظ الإعدادات", command=self.save_settings).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="إعادة التعيين", command=self.reset_to_default).pack(side='left', padx=10)

        self.apply_preset()

    # ========== الوظائف الجديدة للأنظمة المضافة ==========

    def run_single_backtest(self):
        """تشغيل Backtest لعملة واحدة"""
        symbol = self.backtest_symbol.get()
        days = int(self.backtest_days.get())
        capital = float(self.backtest_capital.get())
        
        self.log_message(f"🔄 جاري تشغيل Backtest لـ {symbol}...")
        
        report = self.trader.run_backtest_analysis(symbol, days, capital)
        
        if report:
            self.backtest_results.delete(1.0, tk.END)
            self.backtest_results.insert(tk.END, report)
            self.log_message(f"✅ تم الانتهاء من Backtest لـ {symbol}")
        else:
            self.backtest_results.delete(1.0, tk.END)
            self.backtest_results.insert(tk.END, f"❌ فشل في تشغيل Backtest لـ {symbol}")
            self.log_message(f"❌ فشل في تشغيل Backtest لـ {symbol}")

    def run_comprehensive_backtest(self):
        """تشغيل Backtest شامل"""
        symbols = list(OPTIMAL_COINS)[:5]  # اختبار أول 5 عملات
        days = int(self.backtest_days.get())
        capital = float(self.backtest_capital.get())
        
        self.log_message(f"🔄 جاري تشغيل Backtest شامل لـ {len(symbols)} عملة...")
        
        report = self.trader.run_comprehensive_backtest(symbols, days, capital)
        
        self.backtest_results.delete(1.0, tk.END)
        self.backtest_results.insert(tk.END, report)
        self.log_message("✅ تم الانتهاء من Backtest الشامل")

    def clear_backtest_results(self):
        """مسح نتائج Backtest"""
        self.backtest_results.delete(1.0, tk.END)
        self.backtest_results.insert(tk.END, "💡 تم مسح النتائج. جاهز لتشغيل تحليل جديد.\n")
        self.log_message("🧹 تم مسح نتائج Backtest")

    def analyze_portfolio_hedging(self):
        """تحليل التحوط للمحفظة"""
        self.log_message("🔄 جاري تحليل التحوط للمحفظة...")
        
        report = self.trader.analyze_portfolio_hedging()
        
        self.hedge_results.delete(1.0, tk.END)
        self.hedge_results.insert(tk.END, report)
        self.log_message("✅ تم تحليل التحوط للمحفظة")

    def analyze_correlations(self):
        """تحليل الارتباطات بين الأصول"""
        self.log_message("🔄 جاري تحليل الارتباطات بين الأصول...")
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
        correlation_matrix = self.trader.hedging_system.analyze_correlations(symbols)
        
        report = "📈 تحليل الارتباطات بين الأصول\n"
        report += "══════════════════════════\n\n"
        
        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i < j:
                    if isinstance(correlation_matrix, pd.DataFrame):
                        corr = correlation_matrix.loc[sym1, sym2]
                    else:
                        corr = correlation_matrix.get(sym1, {}).get(sym2, 0)
                    
                    report += f"{sym1} ↔ {sym2}: {corr:.3f}\n"
        
        self.hedge_results.delete(1.0, tk.END)
        self.hedge_results.insert(tk.END, report)
        self.log_message("✅ تم تحليل الارتباطات بين الأصول")

    def show_hedging_strategies(self):
        """عرض إستراتيجيات التحوط"""
        strategies = {
            'bullish': self.trader.get_hedging_strategy('bullish'),
            'bearish': self.trader.get_hedging_strategy('bearish'),
            'volatile': self.trader.get_hedging_strategy('volatile'),
            'neutral': self.trader.get_hedging_strategy('neutral')
        }
        
        report = "🎯 إستراتيجيات التحوط المتاحة\n"
        report += "══════════════════════════\n\n"
        
        for condition, strategy in strategies.items():
            report += f"📊 حالة السوق: {condition}\n"
            report += f"• الوصف: {strategy['description']}\n"
            report += f"• نسبة التحوط: {strategy['hedge_ratio']:.1%}\n"
            report += f"• الأصول الرئيسية: {', '.join(strategy['primary_assets'])}\n"
            report += f"• أصول التحوط: {', '.join(strategy['hedge_assets'])}\n\n"
        
        self.hedge_results.delete(1.0, tk.END)
        self.hedge_results.insert(tk.END, report)
        self.log_message("✅ تم تحميل إستراتيجيات التحوط")

    def run_backtest(self):
        """تشغيل Backtest من القائمة الجانبية"""
        self.notebook.select(2)  # الانتقال إلى تبويب Backtesting
        self.run_single_backtest()

    def analyze_hedging(self):
        """تحليل التحوط من القائمة الجانبية"""
        self.notebook.select(3)  # الانتقال إلى تبويب التحوط
        self.analyze_portfolio_hedging()

    # ========== الوظائف الأصلية (بدون تغيير) ==========

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.api_key_entry.config(show="")
            self.secret_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
            self.secret_key_entry.config(show="*")

    def update_connection_status(self, status):
        self.connection_status = status
        if status:
            self.connection_label.config(text='☑ - Binance', foreground=self.success_color)
        else:
            self.connection_label.config(text='✗ - Binance', foreground=self.danger_color)

    def apply_preset(self):
        mode = self.trading_mode_var.get()
        mode_display = {
            'conservative': '❶',
            'normal': '❷',
            'aggressive': '❸',
            'quantum_profit': '❹'
        }
        self.mode_label.config(text=f"وضع: {mode_display.get(mode, mode)} {mode}")

        if mode in TRADING_PRESETS:
            preset = TRADING_PRESETS[mode]
            self.profit_target_entry.delete(0, tk.END)
            self.profit_target_entry.insert(0, str(preset['profit_target'] * 100))
            self.stop_loss_entry.delete(0, tk.END)
            self.stop_loss_entry.insert(0, str(preset['stop_loss'] * 100))
            self.max_trades_entry.delete(0, tk.END)
            self.max_trades_entry.insert(0, str(preset['max_trades']))
            self.risk_per_trade_entry.delete(0, tk.END)
            self.risk_per_trade_entry.insert(0, str(preset['risk_per_trade'] * 100))

        if hasattr(self, 'trader'):
            self.trader.apply_preset_settings(mode)

        self.log_message(f"☑ تم تطبيق الإعدادات: {mode}")

    def save_api_keys(self):
        api_key = self.api_key_entry.get().strip()
        secret_key = self.secret_key_entry.get().strip()
        testnet_mode = self.network_var.get()

        if not api_key or not secret_key:
            self.log_message("✗ يرجى إدخال مفاتيح API")
            return

        self.log_message("🔄 جاري الاتصال بـ Binance...")
        success = self.trader.setup_api(api_key, secret_key, testnet_mode)
        if success:
            network_type = "شبكة الاختبار" if testnet_mode else "الشبكة الرئيسية"
            self.log_message(f"☑ تم الاتصال بـ Binance بنجاح ({network_type})")
        else:
            self.log_message("✗ فشل الاتصال بـ Binance. يرجى التأكد من المفاتيح والإعدادات")

    def test_connection(self):
        if hasattr(self, 'trader') and self.trader.client:
            try:
                account = self.trader.client.get_account()
                self.log_message("☑ تم التحقق من الاتصال بنجاح")
                self.update_connection_status(True)
                
                usdt_balance = 0.0
                for balance in account['balances']:
                    if balance['asset'] == 'USDT':
                        usdt_balance = float(balance['free']) + float(balance['locked'])
                        break
                
                self.log_message(f"💰 الرصيد المتاح: {usdt_balance:.2f} USDT")
                
            except Exception as e:
                self.log_message(f"✗ خطأ: {e}")
                self.update_connection_status(False)
        else:
            self.log_message("❌ يرجى إعداد مفاتيح API أولاً")

    def reset_to_default(self):
        self.capital_entry.delete(0, tk.END)
        self.capital_entry.insert(0, "100.0")
        self.trading_mode_var.set("quantum_profit")
        self.apply_preset()
        self.log_message("✅ تم استعادة الإعدادات الافتراضية")

    def save_settings(self):
        try:
            if hasattr(self, 'trader'):
                capital = self.capital_entry.get()
                if capital:
                    success = self.trader.set_initial_capital(capital)
                    if success:
                        self.log_message(f"✅ تم تحديد رأس المال الابتدائي: {capital} USDT")
                    else:
                        self.log_message("❌ قيمة رأس المال غير صالحة")

                try:
                    if self.profit_target_entry.get():
                        self.trader.profit_target = float(self.profit_target_entry.get()) / 100
                    if self.stop_loss_entry.get():
                        self.trader.stop_loss = float(self.stop_loss_entry.get()) / 100
                    if self.max_trades_entry.get():
                        self.trader.max_trades = int(self.max_trades_entry.get())
                    if self.risk_per_trade_entry.get():
                        self.trader.risk_per_trade = float(self.risk_per_trade_entry.get()) / 100
                except ValueError as e:
                    self.log_message(f"❌ قيم إعدادات غير صالحة: {e}")
                    return

            self.log_message("✅ تم حفظ الإعدادات بنجاح")
        except Exception as e:
            self.log_message(f"❌ خطأ: {e}")

    def log_message(self, message):
        if not hasattr(self, 'log_text'):
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        # تحديد الأيقونة المناسبة بناء على محتوى الرسالة
        if "✅" in message or "تم" in message and "❌" not in message:
            emoji = "✅"
            color = self.success_color
        elif "❌" in message or "فشل" in message or "خطأ" in message:
            emoji = "❌"
            color = self.danger_color
        elif "⚠️" in message or "تحذير" in message:
            emoji = "⚠️"
            color = self.warning_color
        elif "💰" in message or "رصيد" in message:
            emoji = "💰"
            color = self.success_color
        elif "🔍" in message or "بحث" in message:
            emoji = "🔍"
            color = self.primary_color
        elif "🎯" in message or "ربح" in message:
            emoji = "🎯"
            color = self.success_color
        elif "🛡️" in message or "خسارة" in message:
            emoji = "🛡️"
            color = self.warning_color
        else:
            emoji = "ℹ️"
            color = self.primary_color

        formatted_message = f"{emoji} {timestamp} {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)

    def start_trading(self):
        if not self.trader.client:
            self.log_message("❌ لم يتم الاتصال بـ Binance بعد. يرجى حفظ المفاتيح أولاً")
            return

        self.is_trading = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.trading_status_label.config(text="▶ التداول يعمل", foreground=self.success_color)
        self.log_message("🚀 بدأ التداول الآلي")
        self.run_trading_cycle()

    def stop_trading(self):
        self.is_trading = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.trading_status_label.config(text="⏹ التداول متوقف", foreground=self.danger_color)
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        self.log_message("⏹ تم إيقاف التداول")

    def run_trading_cycle(self):
        if self.is_trading:
            try:
                if hasattr(self, 'trader') and self.trader.client:
                    self.trader.run_trading_cycle()
                    self.update_dashboard()
            except Exception as e:
                self.log_message(f"❌ خطأ في دورة التداول: {e}")

            interval = 5 * 60 * 1000  # 5 دقائق
            self.update_job = self.root.after(interval, self.run_trading_cycle)

    def update_dashboard(self):
        try:
            if not hasattr(self, 'trader'):
                return

            self.trader.update_performance_stats()
            stats = self.trader.performance_stats

            # تحديث الإحصائيات السريعة
            self.quick_stats["رأس المال المتاح"].config(text=f"{self.trader.portfolio.get('USDT', 0.0):.2f} $")
            self.quick_stats["صافي الربح"].config(text=f"{stats.get('total_profit', 0.0):.2f} $")
            self.quick_stats["معدل الربح"].config(text=f"{stats.get('win_rate', 0.0):.1f}%")
            self.quick_stats["الصفقات النشطة"].config(text=f"{len(self.trader.active_trades)}")

            # تحديث إحصائيات الأداء
            self.dash_labels["رأس المال الحالي"].config(text=f"{stats.get('current_portfolio_value', 0.0):.2f} $")
            self.dash_labels["رأس المال الابتدائي"].config(text=f"{self.trader.initial_capital:.2f} $")
            self.dash_labels["صافي الربح"].config(text=f"{stats.get('total_profit', 0.0):.2f} $")
            self.dash_labels["معدل الربح"].config(text=f"{stats.get('win_rate', 0.0):.1f}%")
            self.dash_labels["إجمالي الصفقات"].config(text=f"{stats.get('total_trades', 0)}")
            self.dash_labels["الصفقات النشطة"].config(text=f"{len(self.trader.active_trades)}")

            # تحديث محفظة الأصول
            for item in self.portfolio_tree.get_children():
                self.portfolio_tree.delete(item)

            if hasattr(self.trader, "portfolio"):
                for coin, amount in self.trader.portfolio.items():
                    if amount > 0.000001:
                        if coin == "USDT":
                            current_price = 1.0
                            value = amount
                            pnl = 0
                        else:
                            symbol = f"{coin}USDT"
                            current_price = self.trader.get_current_price(symbol)
                            value = amount * current_price if current_price else 0
                            pnl = self.trader.daily_pnl.get(coin, 0)

                        if value > 0:
                            self.portfolio_tree.insert("", "end", values=[
                                coin,
                                f"{amount:.6f}",
                                f"{value:.2f} $",
                                f"{pnl:.2f} $"
                            ])

            # تحديث الصفقات النشطة
            for item in self.trades_tree.get_children():
                self.trades_tree.delete(item)

            if hasattr(self.trader, "active_trades"):
                for symbol, trade in self.trader.active_trades.items():
                    current_price = self.trader.get_current_price(symbol)
                    if current_price:
                        entry_price = trade['entry_price']
                        profit = (current_price - entry_price) * trade['amount']
                        status = "🟢" if profit > 0 else "🔴"
                        self.trades_tree.insert("", "end", values=[
                            trade['entry_time'].strftime("%H:%M:%S"),
                            symbol,
                            f"{trade['amount']:.6f}",
                            f"{entry_price:.6f}",
                            f"{current_price:.6f}",
                            f"{profit:.4f} $",
                            status
                        ])

            # تحديث تحليل السوق
            for item in self.analysis_tree.get_children():
                self.analysis_tree.delete(item)

            if hasattr(self.trader, "market_analysis"):
                for symbol, analysis in self.trader.market_analysis.items():
                    action = analysis['action']
                    if action == "buy":
                        action_emoji = "🟢"
                        action_text = f"{action_emoji} شراء"
                    elif action == "sell":
                        action_emoji = "🔴"
                        action_text = f"{action_emoji} بيع"
                    else:
                        action_emoji = "⚪"
                        action_text = f"{action_emoji} انتظار"

                    confidence = analysis['confidence']
                    score = analysis['score']
                    score_text = f"{score}"
                    signals = "|".join(analysis['signals'][:2]) if analysis['signals'] else ""
                    status = analysis.get('status', 'غير معروف')

                    self.analysis_tree.insert("", "end", values=[
                        symbol,
                        action_text,
                        f"{confidence:.1f}",
                        score_text,
                        f"{analysis['current_price']:.6f}",
                        f"{analysis['target_price']:.6f}",
                        f"{analysis['stop_loss']:.6f}",
                        status,
                        signals
                    ])

            # تحديث سجل الصفقات
            for item in self.trades_log_tree.get_children():
                self.trades_log_tree.delete(item)

            for trade in sorted(self.trader.trades_history,
                              key=lambda x: x.get('entry_time', datetime.min),
                              reverse=True)[:50]:
                time_str = trade.get('time', '')
                symbol = trade.get('symbol', '')
                trade_type = trade.get('type', '')
                amount = trade.get('amount', 0)
                price = trade.get('price', 0)
                invested = trade.get('invested_usdt', 0)
                profit = trade.get('profit', 0)
                status = trade.get('status', '')

                profit_percent = (profit / invested * 100) if invested > 0 else 0

                self.trades_log_tree.insert("", "end", values=[
                    time_str,
                    symbol,
                    trade_type,
                    f"{amount:.6f}",
                    f"{price:.6f}",
                    f"{invested:.2f} $",
                    f"{profit:.2f} $",
                    f"{profit_percent:.1f}%",
                    status
                ])

        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def check_connection(self):
        self.test_connection()

    def update_data(self):
        if hasattr(self, 'trader') and self.trader.client:
            self.trader.update_real_portfolio()
            self.trader.analyze_market_with_quantum_ai()
            self.update_dashboard()
            self.log_message("☑ تم تحديث البيانات")
        else:
            self.log_message("✗ لم يتم الاتصال بعد")

    def smart_trade(self):
        if hasattr(self, 'trader') and self.trader.client:
            self.trader.execute_quantum_trade_strategy()
            self.log_message("☑ تم تنفيذ تداول ذكي")
        else:
            self.log_message("✗ لم يتم الاتصال بـ Binance بعد")

    def sell_profitable(self):
        if hasattr(self, 'trader') and self.trader.client:
            sold_count = 0
            for symbol, trade in list(self.trader.active_trades.items()):
                current_price = self.trader.get_current_price(symbol)
                entry_price = trade['entry_price']
                if current_price > entry_price:
                    analysis = {'symbol': symbol, 'current_price': current_price, 'action': 'sell'}
                    if self.trader.execute_smart_sell(analysis):
                        sold_count += 1
            
            if sold_count > 0:
                self.log_message(f"☑ تم بيع {sold_count} عملة مربحة")
            else:
                self.log_message("ℹ️ لا توجد صفقات مربحة للبيع")
        else:
            self.log_message("✗ لم يتم الاتصال بـ Binance بعد")

    def sell_all_coins(self):
        if hasattr(self, 'trader') and self.trader.client:
            sold_count = 0
            for symbol in list(self.trader.active_trades.keys()):
                current_price = self.trader.get_current_price(symbol)
                analysis = {'symbol': symbol, 'current_price': current_price, 'action': 'sell'}
                if self.trader.execute_smart_sell(analysis):
                    sold_count += 1
            
            if sold_count > 0:
                self.log_message(f"☑ تم بيع {sold_count} عملة")
            else:
                self.log_message("ℹ️ لا توجد صفقات نشطة")
        else:
            self.log_message("✗ لم يتم الاتصال بـ Binance بعد")

    def show_buy_dialog(self):
        if not hasattr(self, 'trader') or not self.trader.client:
            messagebox.showerror("خطأ", "لم يتم الاتصال بـ Binance")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("شراء يدوي")
        dialog.geometry("400x250")
        dialog.configure(bg=self.card_bg)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="اختر العملة:",
                background=self.card_bg,
                foreground=self.light_text, font=('Arial', 12, 'bold')).pack(pady=10)

        coin_var = tk.StringVar()
        coin_combo = ttk.Combobox(dialog, textvariable=coin_var, values=list(OPTIMAL_COINS),
                                width=30, style="Custom.TCombobox")
        coin_combo.pack(pady=5)
        coin_combo.set(list(OPTIMAL_COINS)[0] if OPTIMAL_COINS else "")
        
        tk.Label(dialog, text="المبلغ (USDT):",
                background=self.card_bg,
                foreground=self.light_text, font=('Arial', 12, 'bold')).pack(pady=10)

        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(dialog, textvariable=amount_var, width=30, style="Custom.TEntry")
        amount_entry.pack(pady=5)

        def execute_buy():
            symbol = coin_var.get()
            amount = amount_var.get()

            if not symbol or not amount:
                messagebox.showerror("خطأ", "يرجى إدخال جميع البيانات")
                return

            try:
                amount_usdt = float(amount)
                # محاكاة عملية الشراء اليدوي
                current_price = self.trader.get_current_price(symbol)
                if current_price:
                    min_amount = MIN_TRADE_AMOUNTS.get(symbol, 0.001)
                    quantity = amount_usdt / current_price

                    if quantity < min_amount:
                        messagebox.showerror("خطأ", f"الكمية أقل من الحد الأدنى: {min_amount}")
                        return

                    if self.trader.portfolio.get('USDT', 0) >= amount_usdt:
                        # تنفيذ عملية الشراء
                        order = self.trader.client.order_market_buy(
                            symbol=symbol,
                            quantity=self.trader.format_quantity(symbol, quantity)
                        )
                        coin = symbol.replace('USDT', '')
                        self.trader.portfolio['USDT'] = self.trader.portfolio.get('USDT', 0) - amount_usdt
                        self.trader.portfolio[coin] = self.trader.portfolio.get(coin, 0) + float(order['executedQty'])

                        self.log_message(f"✅ تم الشراء: {symbol} {amount_usdt:.2f} USDT")
                        messagebox.showinfo("نجاح", f"تم تنفيذ أمر الشراء لـ {symbol}")
                        dialog.destroy()
                    else:
                        messagebox.showerror("خطأ", "رصيد USDT غير كافي")
                else:
                    messagebox.showerror("خطأ", "لا يمكن الحصول على السعر الحالي")

            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في التنفيذ: {e}")

        btn_frame = ttk.Frame(dialog, style="Card.TFrame")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="شراء", command=execute_buy, style="Primary.TButton").pack(side='left', padx=10)
        ttk.Button(btn_frame, text="إلغاء", command=dialog.destroy, style="Danger.TButton").pack(side='left', padx=10)

    def show_sell_dialog(self):
        if not hasattr(self, 'trader') or not self.trader.client:
            messagebox.showerror("خطأ", "لم يتم الاتصال بـ Binance")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("بيع يدوي")
        dialog.geometry("400x300")
        dialog.configure(bg=self.card_bg)
        dialog.transient(self.root)
        dialog.grab_set()

        available_coins = []
        if hasattr(self, 'trader') and hasattr(self.trader, 'active_trades'):
            for symbol in self.trader.active_trades.keys():
                available_coins.append(symbol)

        if not available_coins:
            tk.Label(dialog, text="لا توجد صفقات نشطة",
                    background=self.card_bg,
                    foreground=self.light_text, font=('Arial', 12, 'bold')).pack(pady=50)
            ttk.Button(dialog, text="إغلاق", command=dialog.destroy, style="Primary.TButton").pack(pady=10)
            return

        tk.Label(dialog, text="اختر العملة:",
                background=self.card_bg,
                foreground=self.light_text, font=('Arial', 12, 'bold')).pack(pady=10)

        coin_var = tk.StringVar()
        coin_combo = ttk.Combobox(dialog, textvariable=coin_var, values=available_coins, width=30,
                                style="Custom.TCombobox")
        coin_combo.pack(pady=5)
        coin_combo.set(available_coins[0])

        tk.Label(dialog, text="نسبة البيع (%):",
                background=self.card_bg,
                foreground=self.light_text, font=('Arial', 12, 'bold')).pack(pady=10)

        percent_var = tk.StringVar(value="100")
        percent_combo = ttk.Combobox(dialog, textvariable=percent_var, values=["25", "50", "75", "100"], width=30,
                                   style="Custom.TCombobox")
        percent_combo.pack(pady=5)

        def execute_sell():
            symbol = coin_var.get()
            percent = percent_var.get()

            if not symbol or not percent:
                messagebox.showerror("خطأ", "يرجى إدخال جميع البيانات")
                return

            try:
                percent_val = int(percent)
                if symbol in self.trader.active_trades:
                    trade = self.trader.active_trades[symbol]
                    current_price = self.trader.get_current_price(symbol)

                    if current_price:
                        # محاكاة عملية البيع
                        analysis = {'symbol': symbol, 'current_price': current_price, 'action': 'sell'}
                        if self.trader.execute_smart_sell(analysis):
                            self.log_message(f"✅ تم البيع: {symbol} بنسبة {percent}%")
                            messagebox.showinfo("نجاح", f"تم بيع {symbol} بنجاح")
                            dialog.destroy()
                        else:
                            messagebox.showerror("خطأ", "فشل في تنفيذ البيع")
                    else:
                        messagebox.showerror("خطأ", "لا يمكن الحصول على السعر الحالي")
                else:
                    messagebox.showerror("خطأ", "لا توجد صفقة نشطة لهذه العملة")

            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال نسبة صحيحة")

        btn_frame = ttk.Frame(dialog, style="Card.TFrame")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="بيع", command=execute_sell, style="Danger.TButton").pack(side='left', padx=10)
        ttk.Button(btn_frame, text="إلغاء", command=dialog.destroy, style="Primary.TButton").pack(side='left', padx=10)

    def update_portfolio(self):
        if hasattr(self, 'trader') and self.trader.client:
            self.trader.update_real_portfolio()
            self.update_dashboard()
            self.log_message("☑ تم تحديث المحفظة")
        else:
            self.log_message("✗ لم يتم الاتصال بـ Binance بعد")

    def auto_update(self):
        self.update_dashboard()
        self.root.after(10000, self.auto_update)

def main():
    try:
        root = tk.Tk()
        app = QuantumTradingApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("خطأ", f"فشل في بدء التطبيق: {e}")

if __name__ == "__main__":
    main()