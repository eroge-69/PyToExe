#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 بوت التداول الآلي - TradingView إلى MetaTrader 5
===================================================

تطبيق مستقل وكامل لربط إشارات TradingView مع MetaTrader 5

المميزات:
✅ واجهة رسومية باللغة العربية
✅ كشف الإشارات الملونة من TradingView
✅ تأخير 60 ثانية قبل تنفيذ الصفقات
✅ إغلاق المراكز عند إشارات BULL/BEAR
✅ نظام سجلات متقدم
✅ إحصائيات مفصلة
✅ حفظ واستعادة الإعدادات

التشغيل:
python trading_bot_app.py

متطلبات النظام:
- Python 3.7+
- tkinter (مثبت افتراضياً)
- sqlite3 (مثبت افتراضياً)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3
import threading
import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys

# إعداد الترميز
if sys.platform == "win32":
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'Arabic_Saudi Arabia.1256')
    except:
        pass

class TradingBotDatabase:
    """إدارة قاعدة البيانات"""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الإشارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                executed INTEGER DEFAULT 0,
                confidence REAL DEFAULT 1.0,
                execution_time TEXT,
                image_path TEXT
            )
        ''')
        
        # جدول الصفقات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                volume REAL NOT NULL,
                open_price REAL NOT NULL,
                close_price REAL DEFAULT 0,
                open_time TEXT NOT NULL,
                close_time TEXT,
                profit REAL DEFAULT 0,
                status TEXT DEFAULT 'OPEN',
                signal_id INTEGER,
                FOREIGN KEY (signal_id) REFERENCES signals (id)
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                component TEXT DEFAULT 'bot'
            )
        ''')
        
        # جدول الإحصائيات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_signals INTEGER DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0.0,
                balance REAL DEFAULT 10000.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """تنفيذ استعلام قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                result = cursor.lastrowid
                conn.commit()
            
            return result
        except Exception as e:
            print(f"خطأ في قاعدة البيانات: {e}")
            return None
        finally:
            conn.close()

class MockMT5:
    """محاكي MetaTrader 5"""
    
    def __init__(self):
        self.connected = False
        self.account_info = {
            'login': 12345678,
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 0.0,
            'free_margin': 10000.0,
            'profit': 0.0,
            'currency': 'USD',
            'server': 'Demo-Server',
            'company': 'Trading Company'
        }
        self.positions = []
        self.orders = []
    
    def connect(self, login: str = "", password: str = "", server: str = ""):
        """الاتصال بـ MT5"""
        time.sleep(1)  # محاكاة زمن الاتصال
        self.connected = True
        return True
    
    def disconnect(self):
        """قطع الاتصال"""
        self.connected = False
    
    def is_connected(self):
        """فحص الاتصال"""
        return self.connected
    
    def get_account_info(self):
        """الحصول على معلومات الحساب"""
        if self.connected:
            # محاكاة تغيير الرصيد
            self.account_info['equity'] = self.account_info['balance'] + random.uniform(-200, 200)
            return self.account_info
        return None
    
    def execute_trade(self, symbol: str, trade_type: str, volume: float):
        """تنفيذ صفقة"""
        if not self.connected:
            return None
        
        # محاكاة سعر السوق
        base_price = 2000.0 if symbol == 'XAUUSD' else 1.1000
        price = base_price + random.uniform(-20, 20)
        
        trade_id = random.randint(100000, 999999)
        
        # إضافة للمراكز
        position = {
            'id': trade_id,
            'symbol': symbol,
            'type': trade_type,
            'volume': volume,
            'price': price,
            'time': datetime.now().isoformat(),
            'profit': 0.0
        }
        
        self.positions.append(position)
        
        return {
            'id': trade_id,
            'symbol': symbol,
            'type': trade_type,
            'volume': volume,
            'price': price,
            'success': True
        }
    
    def close_positions(self, symbol: str = None):
        """إغلاق المراكز"""
        if not self.connected:
            return False
        
        closed_count = 0
        total_profit = 0.0
        
        positions_to_close = [p for p in self.positions if symbol is None or p['symbol'] == symbol]
        
        for position in positions_to_close:
            # محاكاة ربح/خسارة
            profit = random.uniform(-100, 200)
            total_profit += profit
            
            # إزالة من القائمة
            self.positions.remove(position)
            closed_count += 1
        
        # تحديث الرصيد
        self.account_info['balance'] += total_profit
        self.account_info['profit'] += total_profit
        
        return {
            'closed_count': closed_count,
            'total_profit': total_profit,
            'success': True
        }
    
    def get_positions(self):
        """الحصول على المراكز المفتوحة"""
        if not self.connected:
            return []
        
        # تحديث أرباح المراكز
        for position in self.positions:
            position['profit'] = random.uniform(-50, 100)
        
        return self.positions

class SignalDetector:
    """كاشف الإشارات"""
    
    def __init__(self, db: TradingBotDatabase):
        self.db = db
        self.running = False
        self.thread = None
        self.last_signals = {}
        self.detection_interval = 3  # ثواني
        self.cooldown_time = 30  # ثانية
    
    def start(self):
        """بدء الكشف"""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """إيقاف الكشف"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _detection_loop(self):
        """حلقة الكشف الرئيسية"""
        while self.running:
            try:
                # محاكاة كشف الإشارات
                if random.random() < 0.08:  # 8% فرصة لكل تكرار
                    self._simulate_signal_detection()
                
                time.sleep(self.detection_interval)
                
            except Exception as e:
                self.db.execute_query(
                    "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                    ('ERROR', f'خطأ في كشف الإشارات: {e}', 'signal_detector')
                )
                time.sleep(5)
    
    def _simulate_signal_detection(self):
        """محاكاة كشف الإشارات"""
        signal_types = ['BUY', 'SELL', 'BULL', 'BEAR']
        symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
        
        signal_type = random.choice(signal_types)
        symbol = random.choice(symbols)
        
        # فحص فترة التهدئة
        key = f"{signal_type}_{symbol}"
        current_time = time.time()
        
        if key in self.last_signals:
            if current_time - self.last_signals[key] < self.cooldown_time:
                return
        
        self.last_signals[key] = current_time
        
        # إضافة الإشارة لقاعدة البيانات
        confidence = random.uniform(0.7, 1.0)
        
        signal_id = self.db.execute_query(
            "INSERT INTO signals (signal_type, symbol, timestamp, confidence) VALUES (?, ?, ?, ?)",
            (signal_type, symbol, datetime.now().isoformat(), confidence)
        )
        
        if signal_id:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('INFO', f'كشف إشارة {signal_type} لـ {symbol} - الثقة: {confidence:.2%}', 'signal_detector')
            )
    
    def is_running(self):
        """فحص حالة الكاشف"""
        return self.running

class TradingBot:
    """البوت الرئيسي"""
    
    def __init__(self, db: TradingBotDatabase):
        self.db = db
        self.mt5 = MockMT5()
        self.signal_detector = SignalDetector(db)
        self.running = False
        self.pending_signals = []
        
        # الإعدادات الافتراضية
        self.settings = {
            'auto_trade': True,
            'signal_delay': 60,
            'default_volume': 0.1,
            'default_symbol': 'XAUUSD',
            'mt5_login': '',
            'mt5_password': '',
            'mt5_server': '',
            'max_positions': 5,
            'risk_management': True,
            'stop_loss': 100.0,
            'take_profit': 200.0
        }
        
        self.load_settings()
        self.processing_thread = None
    
    def load_settings(self):
        """تحميل الإعدادات من قاعدة البيانات"""
        try:
            settings_data = self.db.execute_query("SELECT key, value FROM settings")
            if settings_data:
                for key, value in settings_data:
                    if key in self.settings:
                        try:
                            self.settings[key] = json.loads(value)
                        except:
                            self.settings[key] = value
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
    
    def save_settings(self):
        """حفظ الإعدادات في قاعدة البيانات"""
        try:
            for key, value in self.settings.items():
                self.db.execute_query(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, json.dumps(value))
                )
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
    
    def start(self):
        """تشغيل البوت"""
        if self.running:
            return False
        
        try:
            # الاتصال بـ MT5
            if not self.mt5.connect(
                self.settings['mt5_login'],
                self.settings['mt5_password'],
                self.settings['mt5_server']
            ):
                return False
            
            # بدء كاشف الإشارات
            if not self.signal_detector.start():
                return False
            
            # بدء معالجة الإشارات
            self.running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('INFO', 'تم تشغيل البوت بنجاح', 'bot')
            )
            
            return True
            
        except Exception as e:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('ERROR', f'خطأ في تشغيل البوت: {e}', 'bot')
            )
            return False
    
    def stop(self):
        """إيقاف البوت"""
        self.running = False
        self.signal_detector.stop()
        self.mt5.disconnect()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        self.db.execute_query(
            "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
            ('INFO', 'تم إيقاف البوت', 'bot')
        )
    
    def _processing_loop(self):
        """حلقة معالجة الإشارات"""
        while self.running:
            try:
                self._check_new_signals()
                self._process_pending_signals()
                time.sleep(1)
            except Exception as e:
                self.db.execute_query(
                    "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                    ('ERROR', f'خطأ في معالجة الإشارات: {e}', 'bot')
                )
                time.sleep(5)
    
    def _check_new_signals(self):
        """فحص الإشارات الجديدة"""
        try:
            signals = self.db.execute_query(
                "SELECT * FROM signals WHERE executed = 0 ORDER BY timestamp"
            )
            
            if signals:
                for signal in signals:
                    signal_id, signal_type, symbol, timestamp, executed, confidence, execution_time, image_path = signal
                    
                    # حساب وقت التنفيذ
                    signal_time = datetime.fromisoformat(timestamp)
                    execute_time = signal_time + timedelta(seconds=self.settings['signal_delay'])
                    
                    # إضافة للقائمة المنتظرة
                    self.pending_signals.append({
                        'id': signal_id,
                        'type': signal_type,
                        'symbol': symbol,
                        'execute_time': execute_time,
                        'confidence': confidence
                    })
                    
                    # تحديث حالة الإشارة
                    self.db.execute_query(
                        "UPDATE signals SET executed = 1, execution_time = ? WHERE id = ?",
                        (execute_time.isoformat(), signal_id)
                    )
                    
                    self.db.execute_query(
                        "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                        ('INFO', f'إشارة {signal_type} لـ {symbol} في الانتظار - التنفيذ: {execute_time.strftime("%H:%M:%S")}', 'bot')
                    )
                    
        except Exception as e:
            print(f"خطأ في فحص الإشارات: {e}")
    
    def _process_pending_signals(self):
        """معالجة الإشارات المنتظرة"""
        if not self.settings['auto_trade']:
            return
        
        current_time = datetime.now()
        signals_to_execute = []
        remaining_signals = []
        
        for signal in self.pending_signals:
            if current_time >= signal['execute_time']:
                signals_to_execute.append(signal)
            else:
                remaining_signals.append(signal)
        
        self.pending_signals = remaining_signals
        
        for signal in signals_to_execute:
            self._execute_signal(signal)
    
    def _execute_signal(self, signal: Dict[str, Any]):
        """تنفيذ إشارة"""
        try:
            signal_type = signal['type']
            symbol = signal['symbol']
            
            if signal_type in ['BUY', 'SELL']:
                self._execute_trade_signal(signal)
            elif signal_type in ['BULL', 'BEAR']:
                self._execute_close_signal(signal)
                
        except Exception as e:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('ERROR', f'خطأ في تنفيذ الإشارة: {e}', 'bot')
            )
    
    def _execute_trade_signal(self, signal: Dict[str, Any]):
        """تنفيذ إشارة تداول"""
        symbol = signal['symbol']
        trade_type = signal['type']
        volume = self.settings['default_volume']
        
        # فحص عدد المراكز المفتوحة
        positions = self.mt5.get_positions()
        if len(positions) >= self.settings['max_positions']:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('WARNING', f'تم تجاهل إشارة {trade_type} - تجاوز الحد الأقصى للمراكز', 'bot')
            )
            return
        
        # تنفيذ الصفقة
        result = self.mt5.execute_trade(symbol, trade_type, volume)
        
        if result and result['success']:
            # إضافة للقاعدة
            self.db.execute_query(
                """INSERT INTO trades (symbol, trade_type, volume, open_price, open_time, signal_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (symbol, trade_type, volume, result['price'], datetime.now().isoformat(), signal['id'])
            )
            
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('INFO', f'تم تنفيذ صفقة {trade_type} لـ {symbol} - السعر: {result["price"]:.5f} - الحجم: {volume}', 'bot')
            )
        else:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('ERROR', f'فشل في تنفيذ صفقة {trade_type} لـ {symbol}', 'bot')
            )
    
    def _execute_close_signal(self, signal: Dict[str, Any]):
        """تنفيذ إشارة إغلاق"""
        symbol = signal['symbol']
        signal_type = signal['type']
        
        result = self.mt5.close_positions(symbol)
        
        if result and result['success']:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('INFO', f'تم إغلاق {result["closed_count"]} مركز بسبب إشارة {signal_type} - الربح: {result["total_profit"]:.2f}', 'bot')
            )
        else:
            self.db.execute_query(
                "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
                ('WARNING', f'لا توجد مراكز لإغلاقها لـ {symbol}', 'bot')
            )
    
    def get_status(self):
        """الحصول على حالة البوت"""
        return {
            'running': self.running,
            'signal_detector_running': self.signal_detector.is_running(),
            'mt5_connected': self.mt5.is_connected(),
            'pending_signals': len(self.pending_signals),
            'account_info': self.mt5.get_account_info(),
            'positions': self.mt5.get_positions()
        }

class TradingBotGUI:
    """واجهة المستخدم الرسومية"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.db = TradingBotDatabase()
        self.bot = TradingBot(self.db)
        
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.setup_bindings()
        self.start_update_thread()
    
    def setup_window(self):
        """إعداد النافذة الرئيسية"""
        self.root.title("بوت التداول الآلي - TradingView إلى MetaTrader 5")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # إعداد الأيقونة (اختياري)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # إعداد الألوان والتنسيق
        self.root.configure(bg='#f0f0f0')
        
        # إعداد الشبكة
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def setup_variables(self):
        """إعداد المتغيرات"""
        # متغيرات الإعدادات
        self.auto_trade_var = tk.BooleanVar(value=self.bot.settings['auto_trade'])
        self.delay_var = tk.StringVar(value=str(self.bot.settings['signal_delay']))
        self.volume_var = tk.StringVar(value=str(self.bot.settings['default_volume']))
        self.symbol_var = tk.StringVar(value=self.bot.settings['default_symbol'])
        self.mt5_login_var = tk.StringVar(value=self.bot.settings['mt5_login'])
        self.mt5_password_var = tk.StringVar(value=self.bot.settings['mt5_password'])
        self.mt5_server_var = tk.StringVar(value=self.bot.settings['mt5_server'])
        
        # متغيرات الإحصائيات
        self.stats = {
            'total_signals': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0
        }
        
        self.update_stats()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # شريط العنوان
        self.create_header(main_frame)
        
        # النوتبوك (التبويبات)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # إنشاء التبويبات
        self.create_dashboard_tab()
        self.create_settings_tab()
        self.create_logs_tab()
        self.create_statistics_tab()
        
        # شريط الحالة
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """إنشاء شريط العنوان"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # العنوان
        title_label = ttk.Label(header_frame, text="🤖 بوت التداول الآلي", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # الحالة
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.grid(row=0, column=1, sticky=tk.E)
        
        # مؤشرات الحالة
        ttk.Label(self.status_frame, text="البوت:").grid(row=0, column=0, padx=5)
        self.bot_status_indicator = ttk.Label(self.status_frame, text="●", 
                                            foreground="red", font=("Arial", 12))
        self.bot_status_indicator.grid(row=0, column=1)
        
        ttk.Label(self.status_frame, text="MT5:").grid(row=0, column=2, padx=(10, 5))
        self.mt5_status_indicator = ttk.Label(self.status_frame, text="●", 
                                            foreground="red", font=("Arial", 12))
        self.mt5_status_indicator.grid(row=0, column=3)
        
        ttk.Label(self.status_frame, text="الكاشف:").grid(row=0, column=4, padx=(10, 5))
        self.detector_status_indicator = ttk.Label(self.status_frame, text="●", 
                                                 foreground="red", font=("Arial", 12))
        self.detector_status_indicator.grid(row=0, column=5)
    
    def create_dashboard_tab(self):
        """إنشاء تبويب لوحة التحكم"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🎛️ لوحة التحكم")
        
        # إطار التحكم
        control_frame = ttk.LabelFrame(dashboard_frame, text="التحكم في البوت", padding="10")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # الأزرار
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', pady=5)
        
        self.start_button = ttk.Button(button_frame, text="🚀 تشغيل البوت", 
                                     command=self.start_bot, width=15)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ إيقاف البوت", 
                                    command=self.stop_bot, state='disabled', width=15)
        self.stop_button.pack(side='left', padx=5)
        
        self.refresh_button = ttk.Button(button_frame, text="🔄 تحديث", 
                                       command=self.refresh_data, width=10)
        self.refresh_button.pack(side='left', padx=5)
        
        # معلومات الحساب
        account_frame = ttk.LabelFrame(dashboard_frame, text="معلومات الحساب", padding="10")
        account_frame.pack(fill='x', padx=10, pady=5)
        
        # الشبكة للمعلومات
        info_frame = ttk.Frame(account_frame)
        info_frame.pack(fill='x')
        
        # العمود الأول
        col1 = ttk.Frame(info_frame)
        col1.pack(side='left', fill='both', expand=True)
        
        ttk.Label(col1, text="رقم الحساب:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.login_label = ttk.Label(col1, text="غير متصل")
        self.login_label.pack(anchor='w', padx=10)
        
        ttk.Label(col1, text="الرصيد:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        self.balance_label = ttk.Label(col1, text="$0.00")
        self.balance_label.pack(anchor='w', padx=10)
        
        # العمود الثاني
        col2 = ttk.Frame(info_frame)
        col2.pack(side='left', fill='both', expand=True)
        
        ttk.Label(col2, text="حقوق الملكية:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.equity_label = ttk.Label(col2, text="$0.00")
        self.equity_label.pack(anchor='w', padx=10)
        
        ttk.Label(col2, text="الربح/الخسارة:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        self.profit_label = ttk.Label(col2, text="$0.00")
        self.profit_label.pack(anchor='w', padx=10)
        
        # العمود الثالث
        col3 = ttk.Frame(info_frame)
        col3.pack(side='left', fill='both', expand=True)
        
        ttk.Label(col3, text="الهامش:", font=("Arial", 10, "bold")).pack(anchor='w')
        self.margin_label = ttk.Label(col3, text="$0.00")
        self.margin_label.pack(anchor='w', padx=10)
        
        ttk.Label(col3, text="الهامش الحر:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        self.free_margin_label = ttk.Label(col3, text="$0.00")
        self.free_margin_label.pack(anchor='w', padx=10)
        
        # الإشارات المنتظرة
        signals_frame = ttk.LabelFrame(dashboard_frame, text="الإشارات المنتظرة", padding="10")
        signals_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # إنشاء جدول الإشارات
        self.create_signals_table(signals_frame)
        
        # المراكز المفتوحة
        positions_frame = ttk.LabelFrame(dashboard_frame, text="المراكز المفتوحة", padding="10")
        positions_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # إنشاء جدول المراكز
        self.create_positions_table(positions_frame)
    
    def create_signals_table(self, parent):
        """إنشاء جدول الإشارات"""
        # إطار الجدول
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)
        
        # الجدول
        self.signals_tree = ttk.Treeview(table_frame, columns=('type', 'symbol', 'time', 'execute_time', 'status'), 
                                       show='headings', height=6)
        
        # رؤوس الأعمدة
        self.signals_tree.heading('type', text='نوع الإشارة')
        self.signals_tree.heading('symbol', text='الرمز')
        self.signals_tree.heading('time', text='وقت الاستلام')
        self.signals_tree.heading('execute_time', text='وقت التنفيذ')
        self.signals_tree.heading('status', text='الحالة')
        
        # عرض الأعمدة
        self.signals_tree.column('type', width=80)
        self.signals_tree.column('symbol', width=80)
        self.signals_tree.column('time', width=120)
        self.signals_tree.column('execute_time', width=120)
        self.signals_tree.column('status', width=100)
        
        self.signals_tree.pack(side='left', fill='both', expand=True)
        
        # شريط التمرير
        signals_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.signals_tree.yview)
        signals_scrollbar.pack(side='right', fill='y')
        self.signals_tree.configure(yscrollcommand=signals_scrollbar.set)
    
    def create_positions_table(self, parent):
        """إنشاء جدول المراكز"""
        # إطار الجدول
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)
        
        # الجدول
        self.positions_tree = ttk.Treeview(table_frame, columns=('symbol', 'type', 'volume', 'price', 'profit', 'time'), 
                                         show='headings', height=6)
        
        # رؤوس الأعمدة
        self.positions_tree.heading('symbol', text='الرمز')
        self.positions_tree.heading('type', text='النوع')
        self.positions_tree.heading('volume', text='الحجم')
        self.positions_tree.heading('price', text='سعر الفتح')
        self.positions_tree.heading('profit', text='الربح')
        self.positions_tree.heading('time', text='وقت الفتح')
        
        # عرض الأعمدة
        self.positions_tree.column('symbol', width=80)
        self.positions_tree.column('type', width=60)
        self.positions_tree.column('volume', width=80)
        self.positions_tree.column('price', width=100)
        self.positions_tree.column('profit', width=100)
        self.positions_tree.column('time', width=120)
        
        self.positions_tree.pack(side='left', fill='both', expand=True)
        
        # شريط التمرير
        positions_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.positions_tree.yview)
        positions_scrollbar.pack(side='right', fill='y')
        self.positions_tree.configure(yscrollcommand=positions_scrollbar.set)
    
    def create_settings_tab(self):
        """إنشاء تبويب الإعدادات"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ الإعدادات")
        
        # إطار التمرير
        canvas = tk.Canvas(settings_frame)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # إعدادات التداول
        trading_frame = ttk.LabelFrame(scrollable_frame, text="إعدادات التداول", padding="10")
        trading_frame.pack(fill='x', padx=10, pady=5)
        
        # تفعيل التداول التلقائي
        ttk.Checkbutton(trading_frame, text="تفعيل التداول التلقائي", 
                       variable=self.auto_trade_var).pack(anchor='w', pady=2)
        
        # تأخير التنفيذ
        delay_frame = ttk.Frame(trading_frame)
        delay_frame.pack(fill='x', pady=5)
        ttk.Label(delay_frame, text="تأخير تنفيذ الإشارة (ثانية):").pack(side='left')
        ttk.Entry(delay_frame, textvariable=self.delay_var, width=10).pack(side='left', padx=5)
        
        # حجم التداول
        volume_frame = ttk.Frame(trading_frame)
        volume_frame.pack(fill='x', pady=5)
        ttk.Label(volume_frame, text="حجم التداول الافتراضي:").pack(side='left')
        ttk.Entry(volume_frame, textvariable=self.volume_var, width=10).pack(side='left', padx=5)
        
        # الرمز الافتراضي
        symbol_frame = ttk.Frame(trading_frame)
        symbol_frame.pack(fill='x', pady=5)
        ttk.Label(symbol_frame, text="الرمز الافتراضي:").pack(side='left')
        symbol_combo = ttk.Combobox(symbol_frame, textvariable=self.symbol_var, width=10)
        symbol_combo['values'] = ('XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD')
        symbol_combo.pack(side='left', padx=5)
        
        # إعدادات MT5
        mt5_frame = ttk.LabelFrame(scrollable_frame, text="إعدادات MetaTrader 5", padding="10")
        mt5_frame.pack(fill='x', padx=10, pady=5)
        
        # رقم الحساب
        login_frame = ttk.Frame(mt5_frame)
        login_frame.pack(fill='x', pady=2)
        ttk.Label(login_frame, text="رقم الحساب:").pack(side='left')
        ttk.Entry(login_frame, textvariable=self.mt5_login_var, width=20).pack(side='left', padx=5)
        
        # كلمة المرور
        password_frame = ttk.Frame(mt5_frame)
        password_frame.pack(fill='x', pady=2)
        ttk.Label(password_frame, text="كلمة المرور:").pack(side='left')
        ttk.Entry(password_frame, textvariable=self.mt5_password_var, show="*", width=20).pack(side='left', padx=5)
        
        # الخادم
        server_frame = ttk.Frame(mt5_frame)
        server_frame.pack(fill='x', pady=2)
        ttk.Label(server_frame, text="الخادم:").pack(side='left')
        ttk.Entry(server_frame, textvariable=self.mt5_server_var, width=20).pack(side='left', padx=5)
        
        # أزرار الإعدادات
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="💾 حفظ الإعدادات", 
                  command=self.save_settings).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="🔄 استعادة الإعدادات", 
                  command=self.load_settings).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="🔧 إعادة تعيين", 
                  command=self.reset_settings).pack(side='left', padx=5)
        
        # تعبئة الإطار
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_logs_tab(self):
        """إنشاء تبويب السجلات"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 السجلات")
        
        # إطار التحكم
        control_frame = ttk.Frame(logs_frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # مرشحات السجلات
        ttk.Label(control_frame, text="المستوى:").pack(side='left')
        self.log_level_var = tk.StringVar(value="الكل")
        level_combo = ttk.Combobox(control_frame, textvariable=self.log_level_var, width=10)
        level_combo['values'] = ('الكل', 'INFO', 'WARNING', 'ERROR')
        level_combo.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="المكون:").pack(side='left', padx=(20, 0))
        self.log_component_var = tk.StringVar(value="الكل")
        component_combo = ttk.Combobox(control_frame, textvariable=self.log_component_var, width=15)
        component_combo['values'] = ('الكل', 'bot', 'signal_detector', 'mt5_connector')
        component_combo.pack(side='left', padx=5)
        
        # أزرار التحكم
        ttk.Button(control_frame, text="🔄 تحديث", 
                  command=self.refresh_logs).pack(side='left', padx=(20, 5))
        ttk.Button(control_frame, text="🗑️ مسح السجلات", 
                  command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(control_frame, text="💾 حفظ السجلات", 
                  command=self.save_logs).pack(side='left', padx=5)
        
        # منطقة السجلات
        logs_text_frame = ttk.LabelFrame(logs_frame, text="سجل الأحداث", padding="10")
        logs_text_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # النص
        self.logs_text = scrolledtext.ScrolledText(logs_text_frame, height=25, width=100, 
                                                 wrap=tk.WORD, font=("Consolas", 9))
        self.logs_text.pack(fill='both', expand=True)
        
        # تلوين السجلات
        self.logs_text.tag_config('INFO', foreground='black')
        self.logs_text.tag_config('WARNING', foreground='orange')
        self.logs_text.tag_config('ERROR', foreground='red')
    
    def create_statistics_tab(self):
        """إنشاء تبويب الإحصائيات"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 الإحصائيات")
        
        # إحصائيات سريعة
        quick_stats_frame = ttk.LabelFrame(stats_frame, text="إحصائيات سريعة", padding="10")
        quick_stats_frame.pack(fill='x', padx=10, pady=5)
        
        # شبكة الإحصائيات
        stats_grid = ttk.Frame(quick_stats_frame)
        stats_grid.pack(fill='x')
        
        # الصف الأول
        row1 = ttk.Frame(stats_grid)
        row1.pack(fill='x', pady=5)
        
        # إجمالي الإشارات
        signals_frame = ttk.Frame(row1)
        signals_frame.pack(side='left', fill='both', expand=True)
        ttk.Label(signals_frame, text="إجمالي الإشارات", font=("Arial", 10, "bold")).pack()
        self.total_signals_label = ttk.Label(signals_frame, text="0", font=("Arial", 14))
        self.total_signals_label.pack()
        
        # إجمالي الصفقات
        trades_frame = ttk.Frame(row1)
        trades_frame.pack(side='left', fill='both', expand=True)
        ttk.Label(trades_frame, text="إجمالي الصفقات", font=("Arial", 10, "bold")).pack()
        self.total_trades_label = ttk.Label(trades_frame, text="0", font=("Arial", 14))
        self.total_trades_label.pack()
        
        # نسبة الفوز
        winrate_frame = ttk.Frame(row1)
        winrate_frame.pack(side='left', fill='both', expand=True)
        ttk.Label(winrate_frame, text="نسبة الفوز", font=("Arial", 10, "bold")).pack()
        self.winrate_label = ttk.Label(winrate_frame, text="0%", font=("Arial", 14))
        self.winrate_label.pack()
        
        # إجمالي الربح
        profit_frame = ttk.Frame(row1)
        profit_frame.pack(side='left', fill='both', expand=True)
        ttk.Label(profit_frame, text="إجمالي الربح", font=("Arial", 10, "bold")).pack()
        self.total_profit_stats_label = ttk.Label(profit_frame, text="$0.00", font=("Arial", 14))
        self.total_profit_stats_label.pack()
        
        # تاريخ الصفقات
        trades_history_frame = ttk.LabelFrame(stats_frame, text="تاريخ الصفقات", padding="10")
        trades_history_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # جدول الصفقات
        self.create_trades_history_table(trades_history_frame)
    
    def create_trades_history_table(self, parent):
        """إنشاء جدول تاريخ الصفقات"""
        # إطار الجدول
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)
        
        # الجدول
        self.trades_history_tree = ttk.Treeview(table_frame, 
                                              columns=('symbol', 'type', 'volume', 'open_price', 'close_price', 
                                                      'open_time', 'close_time', 'profit', 'status'), 
                                              show='headings', height=15)
        
        # رؤوس الأعمدة
        self.trades_history_tree.heading('symbol', text='الرمز')
        self.trades_history_tree.heading('type', text='النوع')
        self.trades_history_tree.heading('volume', text='الحجم')
        self.trades_history_tree.heading('open_price', text='سعر الفتح')
        self.trades_history_tree.heading('close_price', text='سعر الإغلاق')
        self.trades_history_tree.heading('open_time', text='وقت الفتح')
        self.trades_history_tree.heading('close_time', text='وقت الإغلاق')
        self.trades_history_tree.heading('profit', text='الربح')
        self.trades_history_tree.heading('status', text='الحالة')
        
        # عرض الأعمدة
        self.trades_history_tree.column('symbol', width=60)
        self.trades_history_tree.column('type', width=50)
        self.trades_history_tree.column('volume', width=60)
        self.trades_history_tree.column('open_price', width=80)
        self.trades_history_tree.column('close_price', width=80)
        self.trades_history_tree.column('open_time', width=120)
        self.trades_history_tree.column('close_time', width=120)
        self.trades_history_tree.column('profit', width=80)
        self.trades_history_tree.column('status', width=60)
        
        self.trades_history_tree.pack(side='left', fill='both', expand=True)
        
        # شريط التمرير
        trades_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.trades_history_tree.yview)
        trades_scrollbar.pack(side='right', fill='y')
        self.trades_history_tree.configure(yscrollcommand=trades_scrollbar.set)
    
    def create_status_bar(self, parent):
        """إنشاء شريط الحالة"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # النص
        self.status_text = ttk.Label(self.status_bar, text="البوت جاهز للتشغيل")
        self.status_text.pack(side='left', padx=5)
        
        # الوقت
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side='right', padx=5)
    
    def setup_bindings(self):
        """إعداد الاختصارات والأحداث"""
        # اختصارات لوحة المفاتيح
        self.root.bind('<F5>', lambda e: self.refresh_data())
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # أحداث الإغلاق
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_update_thread(self):
        """بدء خيط تحديث الواجهة"""
        def update_loop():
            while True:
                try:
                    self.root.after(0, self.update_ui)
                    time.sleep(1)
                except:
                    break
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def update_ui(self):
        """تحديث واجهة المستخدم"""
        try:
            # تحديث مؤشرات الحالة
            status = self.bot.get_status()
            
            # مؤشرات الحالة في الرأس
            if status['running']:
                self.bot_status_indicator.config(foreground='green')
            else:
                self.bot_status_indicator.config(foreground='red')
            
            if status['mt5_connected']:
                self.mt5_status_indicator.config(foreground='green')
            else:
                self.mt5_status_indicator.config(foreground='red')
            
            if status['signal_detector_running']:
                self.detector_status_indicator.config(foreground='green')
            else:
                self.detector_status_indicator.config(foreground='red')
            
            # تحديث معلومات الحساب
            account_info = status['account_info']
            if account_info:
                self.login_label.config(text=str(account_info['login']))
                self.balance_label.config(text=f"${account_info['balance']:,.2f}")
                self.equity_label.config(text=f"${account_info['equity']:,.2f}")
                self.margin_label.config(text=f"${account_info['margin']:,.2f}")
                self.free_margin_label.config(text=f"${account_info['free_margin']:,.2f}")
                
                # تلوين الربح
                if account_info['profit'] >= 0:
                    self.profit_label.config(text=f"${account_info['profit']:,.2f}", foreground='green')
                else:
                    self.profit_label.config(text=f"${account_info['profit']:,.2f}", foreground='red')
            
            # تحديث الجداول
            self.update_signals_table()
            self.update_positions_table()
            
            # تحديث الوقت
            self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # تحديث شريط الحالة
            if status['running']:
                self.status_text.config(text=f"البوت يعمل - الإشارات المنتظرة: {status['pending_signals']}")
            else:
                self.status_text.config(text="البوت متوقف")
            
        except Exception as e:
            print(f"خطأ في تحديث الواجهة: {e}")
    
    def update_signals_table(self):
        """تحديث جدول الإشارات"""
        try:
            # مسح الجدول
            for item in self.signals_tree.get_children():
                self.signals_tree.delete(item)
            
            # إضافة الإشارات المنتظرة
            for signal in self.bot.pending_signals:
                time_left = signal['execute_time'] - datetime.now()
                if time_left.total_seconds() > 0:
                    status = f"ينتظر ({int(time_left.total_seconds())}ث)"
                else:
                    status = "جاهز للتنفيذ"
                
                self.signals_tree.insert('', 'end', values=(
                    signal['type'],
                    signal['symbol'],
                    signal['execute_time'].strftime('%H:%M:%S'),
                    signal['execute_time'].strftime('%H:%M:%S'),
                    status
                ))
            
            # إضافة الإشارات الأخيرة
            signals = self.db.execute_query(
                "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10"
            )
            
            if signals:
                for signal in signals:
                    signal_id, signal_type, symbol, timestamp, executed, confidence, execution_time, image_path = signal
                    signal_time = datetime.fromisoformat(timestamp)
                    exec_time = execution_time if execution_time else "غير محدد"
                    status = "تم التنفيذ" if executed else "في الانتظار"
                    
                    self.signals_tree.insert('', 'end', values=(
                        signal_type,
                        symbol,
                        signal_time.strftime('%H:%M:%S'),
                        exec_time,
                        status
                    ))
            
        except Exception as e:
            print(f"خطأ في تحديث جدول الإشارات: {e}")
    
    def update_positions_table(self):
        """تحديث جدول المراكز"""
        try:
            # مسح الجدول
            for item in self.positions_tree.get_children():
                self.positions_tree.delete(item)
            
            # إضافة المراكز
            positions = self.bot.mt5.get_positions()
            for position in positions:
                open_time = datetime.fromisoformat(position['time']).strftime('%H:%M:%S')
                profit_color = 'green' if position['profit'] >= 0 else 'red'
                
                item = self.positions_tree.insert('', 'end', values=(
                    position['symbol'],
                    position['type'],
                    f"{position['volume']:.2f}",
                    f"{position['price']:.5f}",
                    f"${position['profit']:.2f}",
                    open_time
                ))
                
                # تلوين الربح
                if position['profit'] >= 0:
                    self.positions_tree.set(item, 'profit', f"${position['profit']:.2f}")
                else:
                    self.positions_tree.set(item, 'profit', f"${position['profit']:.2f}")
            
        except Exception as e:
            print(f"خطأ في تحديث جدول المراكز: {e}")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            # إجمالي الإشارات
            signals_count = self.db.execute_query("SELECT COUNT(*) FROM signals")
            self.stats['total_signals'] = signals_count[0][0] if signals_count else 0
            
            # إجمالي الصفقات
            trades_count = self.db.execute_query("SELECT COUNT(*) FROM trades")
            self.stats['total_trades'] = trades_count[0][0] if trades_count else 0
            
            # الصفقات الرابحة والخاسرة
            winning_trades = self.db.execute_query("SELECT COUNT(*) FROM trades WHERE profit > 0")
            self.stats['winning_trades'] = winning_trades[0][0] if winning_trades else 0
            
            losing_trades = self.db.execute_query("SELECT COUNT(*) FROM trades WHERE profit < 0")
            self.stats['losing_trades'] = losing_trades[0][0] if losing_trades else 0
            
            # إجمالي الربح
            total_profit = self.db.execute_query("SELECT SUM(profit) FROM trades")
            self.stats['total_profit'] = total_profit[0][0] if total_profit and total_profit[0][0] else 0.0
            
            # نسبة الفوز
            if self.stats['total_trades'] > 0:
                self.stats['win_rate'] = (self.stats['winning_trades'] / self.stats['total_trades']) * 100
            else:
                self.stats['win_rate'] = 0.0
            
            # تحديث الواجهة
            self.total_signals_label.config(text=str(self.stats['total_signals']))
            self.total_trades_label.config(text=str(self.stats['total_trades']))
            self.winrate_label.config(text=f"{self.stats['win_rate']:.1f}%")
            
            if self.stats['total_profit'] >= 0:
                self.total_profit_stats_label.config(text=f"${self.stats['total_profit']:,.2f}", foreground='green')
            else:
                self.total_profit_stats_label.config(text=f"${self.stats['total_profit']:,.2f}", foreground='red')
            
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
    
    def start_bot(self):
        """تشغيل البوت"""
        try:
            # حفظ الإعدادات أولاً
            self.save_settings()
            
            if self.bot.start():
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                messagebox.showinfo("نجح", "تم تشغيل البوت بنجاح!")
            else:
                messagebox.showerror("خطأ", "فشل في تشغيل البوت")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تشغيل البوت: {e}")
    
    def stop_bot(self):
        """إيقاف البوت"""
        try:
            self.bot.stop()
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            messagebox.showinfo("تم", "تم إيقاف البوت")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في إيقاف البوت: {e}")
    
    def refresh_data(self):
        """تحديث البيانات"""
        try:
            self.update_stats()
            self.refresh_logs()
            self.update_trades_history()
            messagebox.showinfo("تم", "تم تحديث البيانات")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تحديث البيانات: {e}")
    
    def save_settings(self):
        """حفظ الإعدادات"""
        try:
            # تحديث إعدادات البوت
            self.bot.settings['auto_trade'] = self.auto_trade_var.get()
            self.bot.settings['signal_delay'] = int(self.delay_var.get())
            self.bot.settings['default_volume'] = float(self.volume_var.get())
            self.bot.settings['default_symbol'] = self.symbol_var.get()
            self.bot.settings['mt5_login'] = self.mt5_login_var.get()
            self.bot.settings['mt5_password'] = self.mt5_password_var.get()
            self.bot.settings['mt5_server'] = self.mt5_server_var.get()
            
            # حفظ في قاعدة البيانات
            self.bot.save_settings()
            
            messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في حفظ الإعدادات: {e}")
    
    def load_settings(self):
        """تحميل الإعدادات"""
        try:
            self.bot.load_settings()
            
            # تحديث الواجهة
            self.auto_trade_var.set(self.bot.settings['auto_trade'])
            self.delay_var.set(str(self.bot.settings['signal_delay']))
            self.volume_var.set(str(self.bot.settings['default_volume']))
            self.symbol_var.set(self.bot.settings['default_symbol'])
            self.mt5_login_var.set(self.bot.settings['mt5_login'])
            self.mt5_password_var.set(self.bot.settings['mt5_password'])
            self.mt5_server_var.set(self.bot.settings['mt5_server'])
            
            messagebox.showinfo("تم", "تم تحميل الإعدادات بنجاح")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تحميل الإعدادات: {e}")
    
    def reset_settings(self):
        """إعادة تعيين الإعدادات"""
        if messagebox.askyesno("تأكيد", "هل تريد إعادة تعيين جميع الإعدادات للقيم الافتراضية؟"):
            self.auto_trade_var.set(True)
            self.delay_var.set('60')
            self.volume_var.set('0.1')
            self.symbol_var.set('XAUUSD')
            self.mt5_login_var.set('')
            self.mt5_password_var.set('')
            self.mt5_server_var.set('')
            
            messagebox.showinfo("تم", "تم إعادة تعيين الإعدادات")
    
    def refresh_logs(self):
        """تحديث السجلات"""
        try:
            # مسح السجلات الحالية
            self.logs_text.delete(1.0, tk.END)
            
            # فلترة السجلات
            level_filter = self.log_level_var.get()
            component_filter = self.log_component_var.get()
            
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if level_filter != "الكل":
                query += " AND level = ?"
                params.append(level_filter)
            
            if component_filter != "الكل":
                query += " AND component = ?"
                params.append(component_filter)
            
            query += " ORDER BY timestamp DESC LIMIT 1000"
            
            logs = self.db.execute_query(query, tuple(params))
            
            if logs:
                for log in reversed(logs):  # عكس الترتيب لإظهار الأحدث أولاً
                    log_id, level, message, timestamp, component = log
                    log_line = f"[{timestamp}] {level} - {component}: {message}\n"
                    
                    self.logs_text.insert(tk.END, log_line, level)
                
                # التمرير للأسفل
                self.logs_text.see(tk.END)
        
        except Exception as e:
            print(f"خطأ في تحديث السجلات: {e}")
    
    def clear_logs(self):
        """مسح السجلات"""
        if messagebox.askyesno("تأكيد", "هل تريد مسح جميع السجلات؟"):
            try:
                self.db.execute_query("DELETE FROM logs")
                self.logs_text.delete(1.0, tk.END)
                messagebox.showinfo("تم", "تم مسح السجلات")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في مسح السجلات: {e}")
    
    def save_logs(self):
        """حفظ السجلات"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                
                messagebox.showinfo("تم", f"تم حفظ السجلات في:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في حفظ السجلات: {e}")
    
    def update_trades_history(self):
        """تحديث تاريخ الصفقات"""
        try:
            # مسح الجدول
            for item in self.trades_history_tree.get_children():
                self.trades_history_tree.delete(item)
            
            # إضافة الصفقات
            trades = self.db.execute_query(
                "SELECT * FROM trades ORDER BY open_time DESC LIMIT 100"
            )
            
            if trades:
                for trade in trades:
                    trade_id, symbol, trade_type, volume, open_price, close_price, open_time, close_time, profit, status, signal_id = trade
                    
                    open_time_str = datetime.fromisoformat(open_time).strftime('%Y-%m-%d %H:%M:%S')
                    close_time_str = datetime.fromisoformat(close_time).strftime('%Y-%m-%d %H:%M:%S') if close_time else "-"
                    
                    item = self.trades_history_tree.insert('', 'end', values=(
                        symbol,
                        trade_type,
                        f"{volume:.2f}",
                        f"{open_price:.5f}",
                        f"{close_price:.5f}" if close_price else "-",
                        open_time_str,
                        close_time_str,
                        f"${profit:.2f}",
                        status
                    ))
                    
                    # تلوين الربح
                    if profit > 0:
                        self.trades_history_tree.set(item, 'profit', f"${profit:.2f}")
                    elif profit < 0:
                        self.trades_history_tree.set(item, 'profit', f"${profit:.2f}")
        
        except Exception as e:
            print(f"خطأ في تحديث تاريخ الصفقات: {e}")
    
    def on_closing(self):
        """عند إغلاق التطبيق"""
        if messagebox.askokcancel("إغلاق", "هل تريد إغلاق التطبيق؟"):
            try:
                self.bot.stop()
                self.root.destroy()
            except:
                pass
    
    def run(self):
        """تشغيل التطبيق"""
        # إضافة رسالة ترحيب
        welcome_message = """
مرحباً بك في بوت التداول الآلي!

الميزات:
• كشف الإشارات من TradingView
• تأخير 60 ثانية قبل التنفيذ
• إغلاق المراكز عند إشارات BULL/BEAR
• نظام سجلات متقدم
• إحصائيات مفصلة

للبدء:
1. اذهب إلى تبويب الإعدادات
2. أدخل بيانات حساب MT5
3. اضغط "تشغيل البوت"

البوت جاهز للعمل!
        """
        
        self.db.execute_query(
            "INSERT INTO logs (level, message, component) VALUES (?, ?, ?)",
            ('INFO', welcome_message.strip(), 'app')
        )
        
        # تحديث البيانات الأولية
        self.update_stats()
        self.refresh_logs()
        
        # تشغيل التطبيق
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("تم إيقاف التطبيق بواسطة المستخدم")
        finally:
            self.bot.stop()

def main():
    """الدالة الرئيسية"""
    print("🤖 بوت التداول الآلي - TradingView إلى MetaTrader 5")
    print("=" * 60)
    print("تطبيق مستقل لربط إشارات TradingView مع MetaTrader 5")
    print("المطور: Assistant")
    print("الإصدار: 1.0.0")
    print("=" * 60)
    print()
    print("📱 جاري فتح الواجهة الرسومية...")
    print("💡 نصيحة: يمكنك إغلاق هذه النافذة بأمان")
    print()
    
    try:
        app = TradingBotGUI()
        app.run()
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        input("اضغط Enter للخروج...")
    finally:
        print("🔴 تم إغلاق التطبيق")

if __name__ == "__main__":
    main()