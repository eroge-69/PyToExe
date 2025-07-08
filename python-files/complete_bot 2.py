#!/usr/bin/env python3
"""
بوت التداول الآلي - ربط TradingView مع MetaTrader 5
=======================================================

هذا البوت يقوم بربط إشارات TradingView مع منصة MetaTrader 5 لتنفيذ الصفقات تلقائياً

الميزات:
- كشف الإشارات من TradingView (أحمر/أزرق)
- تأخير دقيقة واحدة قبل تنفيذ الصفقة
- دعم إشارات BUY/SELL و BULL/BEAR
- واجهة تحكم عبر المتصفح
- مراقبة الحساب والصفقات

طريقة الاستخدام:
1. تأكد من تثبيت Python 3.8+
2. قم بتثبيت المكتبات المطلوبة (انظر قائمة REQUIRED_PACKAGES أدناه)
3. شغل الملف: python complete_bot.py
4. افتح المتصفح على http://localhost:5000

المكتبات المطلوبة:
pip install flask flask-socketio opencv-python pyautogui pillow numpy sqlalchemy werkzeug MetaTrader5

ملاحظة: للاستخدام الحقيقي، تأكد من تثبيت MetaTrader5 وإعداد الحساب بشكل صحيح
"""

import os
import sys
import logging
import threading
import time
import json
import base64
import io
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# التحقق من المكتبات المطلوبة
REQUIRED_PACKAGES = [
    'flask', 'flask_socketio', 'cv2', 'pyautogui', 
    'PIL', 'numpy', 'sqlalchemy', 'werkzeug'
]

def check_dependencies():
    """التحقق من وجود المكتبات المطلوبة"""
    missing = []
    for package in REQUIRED_PACKAGES:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ المكتبات التالية مفقودة:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nلتثبيت المكتبات المطلوبة:")
        print("pip install flask flask-socketio opencv-python pyautogui pillow numpy sqlalchemy werkzeug")
        print("\nللحصول على MetaTrader5:")
        print("pip install MetaTrader5")
        return False
    return True

if not check_dependencies():
    sys.exit(1)

# استيراد المكتبات
try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_socketio import SocketIO, emit
    import cv2
    import numpy as np
    import pyautogui
    from PIL import Image
    import sqlalchemy
    from werkzeug.middleware.proxy_fix import ProxyFix
except ImportError as e:
    print(f"❌ خطأ في استيراد المكتبات: {e}")
    sys.exit(1)

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# قاعدة البيانات
# ==============================================================================

class Database:
    """إدارة قاعدة البيانات"""
    
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الإشارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL,
                executed BOOLEAN DEFAULT 0,
                execution_time TEXT,
                confidence REAL,
                image_data TEXT
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
                close_price REAL,
                open_time TEXT NOT NULL,
                close_time TEXT,
                profit REAL,
                status TEXT DEFAULT 'OPEN',
                signal_id INTEGER
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                component TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query, params=None):
        """تنفيذ استعلام قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid
            conn.commit()
        
        conn.close()
        return result
    
    def get_signals(self, limit=100):
        """الحصول على الإشارات"""
        return self.execute(
            "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        )
    
    def add_signal(self, signal_type, symbol, confidence=1.0, image_data=None):
        """إضافة إشارة جديدة"""
        return self.execute(
            """INSERT INTO signals (signal_type, symbol, timestamp, confidence, image_data) 
               VALUES (?, ?, ?, ?, ?)""",
            (signal_type, symbol, datetime.now().isoformat(), confidence, image_data)
        )
    
    def get_trades(self, limit=50):
        """الحصول على الصفقات"""
        return self.execute(
            "SELECT * FROM trades ORDER BY open_time DESC LIMIT ?", 
            (limit,)
        )
    
    def add_trade(self, symbol, trade_type, volume, open_price):
        """إضافة صفقة جديدة"""
        return self.execute(
            """INSERT INTO trades (symbol, trade_type, volume, open_price, open_time) 
               VALUES (?, ?, ?, ?, ?)""",
            (symbol, trade_type, volume, open_price, datetime.now().isoformat())
        )
    
    def add_log(self, level, message, component='bot'):
        """إضافة سجل جديد"""
        return self.execute(
            "INSERT INTO logs (level, message, timestamp, component) VALUES (?, ?, ?, ?)",
            (level, message, datetime.now().isoformat(), component)
        )

# ==============================================================================
# محرك كشف الإشارات
# ==============================================================================

class SignalDetector:
    """كاشف الإشارات من TradingView"""
    
    def __init__(self, database, socketio):
        self.db = database
        self.socketio = socketio
        self.running = False
        self.thread = None
        self.last_signal_time = {}
        self.cooldown = 5  # ثواني بين الإشارات
        
        # نطاقات الألوان للكشف (HSV)
        self.color_ranges = {
            'BUY': {
                'lower': np.array([100, 100, 100]),  # الأزرق
                'upper': np.array([130, 255, 255])
            },
            'SELL': {
                'lower': np.array([0, 100, 100]),    # الأحمر
                'upper': np.array([10, 255, 255])
            },
            'BULL': {
                'lower': np.array([40, 100, 100]),   # الأخضر
                'upper': np.array([80, 255, 255])
            },
            'BEAR': {
                'lower': np.array([0, 100, 100]),    # الأحمر
                'upper': np.array([10, 255, 255])
            }
        }
        
        logger.info("تم تهيئة كاشف الإشارات")
    
    def start(self):
        """بدء كشف الإشارات"""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._detection_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("تم تشغيل كاشف الإشارات")
        return True
    
    def stop(self):
        """إيقاف كشف الإشارات"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("تم إيقاف كاشف الإشارات")
    
    def _detection_loop(self):
        """حلقة الكشف الرئيسية"""
        while self.running:
            try:
                # التقاط الشاشة
                screenshot = self._capture_screen()
                if screenshot is None:
                    time.sleep(1)
                    continue
                
                # كشف الإشارات
                signals = self._detect_signals(screenshot)
                
                # معالجة الإشارات المكتشفة
                for signal in signals:
                    self._process_signal(signal, screenshot)
                
                time.sleep(0.5)  # فحص كل نصف ثانية
                
            except Exception as e:
                logger.error(f"خطأ في حلقة الكشف: {e}")
                time.sleep(1)
    
    def _capture_screen(self):
        """التقاط لقطة شاشة"""
        try:
            screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"خطأ في التقاط الشاشة: {e}")
            return None
    
    def _detect_signals(self, image):
        """كشف الإشارات في الصورة"""
        signals = []
        
        try:
            # تحويل إلى HSV للكشف الأفضل عن الألوان
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # كشف كل نوع إشارة
            for signal_type, color_range in self.color_ranges.items():
                mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # حد أدنى للمساحة
                        x, y, w, h = cv2.boundingRect(contour)
                        confidence = min(area / 1000, 1.0)
                        
                        signals.append({
                            'type': signal_type,
                            'position': (x, y, w, h),
                            'confidence': confidence,
                            'area': area
                        })
            
            # إزالة المكرر
            signals = self._filter_duplicate_signals(signals)
            
        except Exception as e:
            logger.error(f"خطأ في كشف الإشارات: {e}")
        
        return signals
    
    def _filter_duplicate_signals(self, signals):
        """إزالة الإشارات المكررة"""
        if len(signals) <= 1:
            return signals
        
        filtered = []
        for signal in signals:
            is_duplicate = False
            for existing in filtered:
                if (signal['type'] == existing['type'] and
                    abs(signal['position'][0] - existing['position'][0]) < 50 and
                    abs(signal['position'][1] - existing['position'][1]) < 50):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(signal)
        
        return filtered
    
    def _process_signal(self, signal, screenshot):
        """معالجة الإشارة المكتشفة"""
        signal_type = signal['type']
        current_time = time.time()
        
        # فحص فترة الانتظار
        if signal_type in self.last_signal_time:
            if current_time - self.last_signal_time[signal_type] < self.cooldown:
                return
        
        self.last_signal_time[signal_type] = current_time
        
        try:
            # تحويل الصورة إلى base64
            screenshot_base64 = self._image_to_base64(screenshot)
            
            # حفظ الإشارة في قاعدة البيانات
            signal_id = self.db.add_signal(
                signal_type=signal_type,
                symbol='XAUUSD',
                confidence=signal['confidence'],
                image_data=screenshot_base64
            )
            
            # إرسال الإشارة للواجهة
            self.socketio.emit('signal_detected', {
                'type': signal_type,
                'symbol': 'XAUUSD',
                'timestamp': datetime.now().isoformat(),
                'confidence': signal['confidence']
            })
            
            logger.info(f"تم كشف إشارة: {signal_type} (الثقة: {signal['confidence']:.2f})")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشارة: {e}")
    
    def _image_to_base64(self, image):
        """تحويل الصورة إلى base64"""
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            logger.error(f"خطأ في تحويل الصورة: {e}")
            return None
    
    def is_running(self):
        """فحص ما إذا كان الكاشف يعمل"""
        return self.running

# ==============================================================================
# موصل MT5 (نسخة محاكاة)
# ==============================================================================

class MT5Connector:
    """موصل MetaTrader 5"""
    
    def __init__(self, database, socketio):
        self.db = database
        self.socketio = socketio
        self.connected = False
        self.account_info = {
            'login': 12345,
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 0.0,
            'free_margin': 10000.0,
            'margin_level': 0.0
        }
        self.default_volume = 0.1
        
        logger.info("تم تهيئة موصل MT5")
    
    def connect(self):
        """الاتصال بـ MT5"""
        try:
            # محاكاة الاتصال
            self.connected = True
            
            # تحديث معلومات الحساب
            self.account_info['equity'] = self.account_info['balance'] + random.uniform(-100, 100)
            
            logger.info(f"تم الاتصال بـ MT5 - الحساب: {self.account_info['login']}")
            
            # إرسال حالة الاتصال
            self.socketio.emit('mt5_status', {
                'connected': True,
                'account': self.account_info['login'],
                'balance': self.account_info['balance'],
                'equity': self.account_info['equity']
            })
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في الاتصال بـ MT5: {e}")
            return False
    
    def disconnect(self):
        """قطع الاتصال"""
        try:
            self.connected = False
            logger.info("تم قطع الاتصال من MT5")
            self.socketio.emit('mt5_status', {'connected': False})
        except Exception as e:
            logger.error(f"خطأ في قطع الاتصال: {e}")
    
    def is_connected(self):
        """فحص الاتصال"""
        return self.connected
    
    def get_account_info(self):
        """الحصول على معلومات الحساب"""
        if not self.connected:
            return None
        
        # تحديث الأرصدة (محاكاة)
        self.account_info['equity'] = self.account_info['balance'] + random.uniform(-50, 50)
        return self.account_info
    
    def execute_trade(self, symbol, trade_type, volume=None):
        """تنفيذ صفقة"""
        if not self.connected:
            logger.error("غير متصل بـ MT5")
            return None
        
        try:
            if volume is None:
                volume = self.default_volume
            
            # سعر محاكي
            base_price = 2000.0 if symbol == 'XAUUSD' else 1.1000
            price = base_price + random.uniform(-5, 5)
            
            # حفظ الصفقة في قاعدة البيانات
            trade_id = self.db.add_trade(
                symbol=symbol,
                trade_type=trade_type,
                volume=volume,
                open_price=price
            )
            
            # إرسال معلومات الصفقة
            self.socketio.emit('trade_executed', {
                'symbol': symbol,
                'type': trade_type,
                'volume': volume,
                'price': price,
                'time': datetime.now().isoformat()
            })
            
            logger.info(f"تم تنفيذ الصفقة: {trade_type} {volume} {symbol} بسعر {price}")
            
            return {
                'id': trade_id,
                'symbol': symbol,
                'type': trade_type,
                'volume': volume,
                'price': price
            }
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الصفقة: {e}")
            return None
    
    def close_position(self, symbol):
        """إغلاق المراكز"""
        if not self.connected:
            return False
        
        try:
            # محاكاة إغلاق المراكز
            profit = random.uniform(-50, 100)
            
            self.socketio.emit('trade_closed', {
                'symbol': symbol,
                'profit': profit,
                'time': datetime.now().isoformat()
            })
            
            logger.info(f"تم إغلاق المراكز لـ {symbol} - الربح: {profit}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق المراكز: {e}")
            return False
    
    def get_positions(self):
        """الحصول على المراكز المفتوحة"""
        if not self.connected:
            return []
        
        # محاكاة المراكز
        trades = self.db.get_trades(10)
        positions = []
        
        for trade in trades:
            if len(trade) >= 8 and trade[9] == 'OPEN':  # status column
                positions.append({
                    'ticket': trade[0],
                    'symbol': trade[1],
                    'type': trade[2],
                    'volume': trade[3],
                    'price_open': trade[4],
                    'price_current': trade[4] + random.uniform(-1, 1),
                    'profit': random.uniform(-25, 50)
                })
        
        return positions

# ==============================================================================
# البوت الرئيسي
# ==============================================================================

class TradingBot:
    """البوت الرئيسي للتداول"""
    
    def __init__(self, database, socketio):
        self.db = database
        self.socketio = socketio
        self.running = False
        
        # المكونات
        self.signal_detector = SignalDetector(database, socketio)
        self.mt5_connector = MT5Connector(database, socketio)
        
        # الإعدادات
        self.settings = {
            'enabled': False,
            'auto_trade': True,
            'signal_delay': 60,  # ثانية (دقيقة واحدة كما طُلب)
            'default_volume': 0.1,
            'default_symbol': 'XAUUSD',
            'max_positions': 1,
            'close_on_opposite': True
        }
        
        self.pending_signals = []
        self.processing_thread = None
        
        logger.info("تم تهيئة البوت")
    
    def start(self):
        """تشغيل البوت"""
        if self.running:
            return False
        
        try:
            # الاتصال بـ MT5
            if not self.mt5_connector.connect():
                logger.error("فشل في الاتصال بـ MT5")
                return False
            
            # تشغيل كاشف الإشارات
            if not self.signal_detector.start():
                logger.error("فشل في تشغيل كاشف الإشارات")
                return False
            
            # تشغيل معالج الإشارات
            self.running = True
            self.processing_thread = threading.Thread(target=self._processing_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.db.add_log('INFO', 'تم تشغيل البوت بنجاح')
            self.socketio.emit('bot_status', self.get_status())
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تشغيل البوت: {e}")
            return False
    
    def stop(self):
        """إيقاف البوت"""
        try:
            self.running = False
            
            # إيقاف المكونات
            self.signal_detector.stop()
            self.mt5_connector.disconnect()
            
            # انتظار انتهاء المعالجة
            if self.processing_thread:
                self.processing_thread.join(timeout=5)
            
            self.db.add_log('INFO', 'تم إيقاف البوت')
            self.socketio.emit('bot_status', self.get_status())
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت: {e}")
    
    def get_status(self):
        """الحصول على حالة البوت"""
        try:
            return {
                'running': self.running,
                'signal_detector_running': self.signal_detector.is_running(),
                'mt5_connected': self.mt5_connector.is_connected(),
                'pending_signals': len(self.pending_signals),
                'account_info': self.mt5_connector.get_account_info(),
                'open_positions': len(self.mt5_connector.get_positions()),
                'settings': self.settings
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على الحالة: {e}")
            return {'error': str(e)}
    
    def update_settings(self, new_settings):
        """تحديث الإعدادات"""
        try:
            self.settings.update(new_settings)
            self.db.add_log('INFO', f'تم تحديث الإعدادات: {new_settings}')
            self.socketio.emit('settings_updated', self.settings)
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث الإعدادات: {e}")
            return False
    
    def _processing_loop(self):
        """حلقة معالجة الإشارات"""
        while self.running:
            try:
                self._check_new_signals()
                self._process_pending_signals()
                self._send_updates()
                time.sleep(1)
            except Exception as e:
                logger.error(f"خطأ في معالجة الإشارات: {e}")
                time.sleep(5)
    
    def _check_new_signals(self):
        """فحص الإشارات الجديدة"""
        try:
            # الحصول على الإشارات غير المنفذة
            signals = self.db.execute(
                "SELECT * FROM signals WHERE executed = 0 ORDER BY timestamp"
            )
            
            for signal in signals:
                signal_id, signal_type, symbol, timestamp, price, executed, execution_time, confidence, image_data = signal
                
                # إضافة للقائمة المعلقة
                execute_time = datetime.fromisoformat(timestamp) + timedelta(seconds=self.settings['signal_delay'])
                
                self.pending_signals.append({
                    'id': signal_id,
                    'type': signal_type,
                    'symbol': symbol,
                    'execute_time': execute_time
                })
                
                # تحديد كمنفذة
                self.db.execute(
                    "UPDATE signals SET executed = 1 WHERE id = ?",
                    (signal_id,)
                )
            
        except Exception as e:
            logger.error(f"خطأ في فحص الإشارات الجديدة: {e}")
    
    def _process_pending_signals(self):
        """معالجة الإشارات المعلقة"""
        current_time = datetime.now()
        
        signals_to_process = []
        remaining_signals = []
        
        for signal in self.pending_signals:
            if current_time >= signal['execute_time']:
                signals_to_process.append(signal)
            else:
                remaining_signals.append(signal)
        
        self.pending_signals = remaining_signals
        
        for signal in signals_to_process:
            self._execute_signal(signal)
    
    def _execute_signal(self, signal):
        """تنفيذ الإشارة"""
        try:
            if not self.settings['auto_trade']:
                self.db.add_log('INFO', f'التداول الآلي معطل، تجاهل الإشارة: {signal["type"]}')
                return
            
            signal_type = signal['type']
            symbol = signal['symbol']
            
            if signal_type in ['BUY', 'SELL']:
                self._execute_trade_signal(signal_type, symbol)
            elif signal_type in ['BULL', 'BEAR']:
                self._execute_close_signal(signal_type, symbol)
            
            # تحديث وقت التنفيذ
            self.db.execute(
                "UPDATE signals SET execution_time = ? WHERE id = ?",
                (datetime.now().isoformat(), signal['id'])
            )
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الإشارة: {e}")
            self.db.add_log('ERROR', f'خطأ في تنفيذ الإشارة: {e}')
    
    def _execute_trade_signal(self, signal_type, symbol):
        """تنفيذ إشارة التداول"""
        try:
            # إغلاق المراكز المعاكسة إذا كان مفعلاً
            if self.settings['close_on_opposite']:
                self.mt5_connector.close_position(symbol)
            
            # فحص حد المراكز
            positions = self.mt5_connector.get_positions()
            symbol_positions = [p for p in positions if p['symbol'] == symbol]
            
            if len(symbol_positions) >= self.settings['max_positions']:
                self.db.add_log('WARNING', f'تم الوصول للحد الأقصى من المراكز لـ {symbol}')
                return
            
            # تنفيذ الصفقة
            result = self.mt5_connector.execute_trade(
                symbol=symbol,
                trade_type=signal_type,
                volume=self.settings['default_volume']
            )
            
            if result:
                self.db.add_log('INFO', f'تم تنفيذ الصفقة: {signal_type} {symbol}')
                self.socketio.emit('trade_notification', {
                    'type': 'success',
                    'message': f'تم تنفيذ الصفقة: {signal_type} {symbol}'
                })
            else:
                self.db.add_log('ERROR', f'فشل في تنفيذ الصفقة: {signal_type} {symbol}')
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ إشارة التداول: {e}")
    
    def _execute_close_signal(self, signal_type, symbol):
        """تنفيذ إشارة الإغلاق"""
        try:
            success = self.mt5_connector.close_position(symbol)
            
            if success:
                self.db.add_log('INFO', f'تم إغلاق المراكز بسبب إشارة {signal_type} لـ {symbol}')
                self.socketio.emit('trade_notification', {
                    'type': 'info',
                    'message': f'تم إغلاق المراكز بسبب إشارة {signal_type}'
                })
            else:
                self.db.add_log('ERROR', f'فشل في إغلاق المراكز لـ {symbol}')
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ إشارة الإغلاق: {e}")
    
    def _send_updates(self):
        """إرسال التحديثات"""
        try:
            # حالة البوت
            self.socketio.emit('bot_status', self.get_status())
            
            # معلومات الحساب
            account_info = self.mt5_connector.get_account_info()
            if account_info:
                self.socketio.emit('account_update', account_info)
            
            # المراكز
            positions = self.mt5_connector.get_positions()
            self.socketio.emit('positions_update', positions)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال التحديثات: {e}")

# ==============================================================================
# واجهة الويب
# ==============================================================================

# قالب HTML للواجهة
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوت التداول الآلي - TradingView إلى MetaTrader</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { border-radius: 8px; }
        .log-container { 
            height: 300px; overflow-y: auto; background: #f8f9fa; 
            border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;
            font-family: monospace; font-size: 0.9em;
        }
        .signal-card { animation: fadeIn 0.5s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .status-indicator { 
            display: inline-block; width: 12px; height: 12px; 
            border-radius: 50%; margin-left: 8px;
        }
        .status-online { background-color: #28a745; }
        .status-offline { background-color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand">
                <i class="fas fa-robot me-2"></i>
                بوت التداول الآلي
            </span>
            <span class="navbar-text">
                <span id="connection-status" class="badge bg-secondary">
                    <span class="status-indicator status-offline"></span>
                    جاري الاتصال...
                </span>
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <!-- لوحة التحكم -->
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-cogs me-2"></i>لوحة التحكم</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button id="start-bot" class="btn btn-success btn-lg">
                                <i class="fas fa-play me-2"></i>تشغيل البوت
                            </button>
                            <button id="stop-bot" class="btn btn-danger btn-lg" disabled>
                                <i class="fas fa-stop me-2"></i>إيقاف البوت
                            </button>
                        </div>
                        
                        <hr>
                        
                        <div class="row text-center">
                            <div class="col-6">
                                <div class="border rounded p-2">
                                    <small class="text-muted">حالة البوت</small>
                                    <div id="bot-status" class="fw-bold text-secondary">متوقف</div>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="border rounded p-2">
                                    <small class="text-muted">حالة MT5</small>
                                    <div id="mt5-status" class="fw-bold text-secondary">غير متصل</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- الإعدادات -->
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5><i class="fas fa-sliders-h me-2"></i>الإعدادات</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">تأخير الإشارة (ثانية)</label>
                            <input type="number" id="signal-delay" class="form-control" value="60" min="1" max="300">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">حجم الصفقة</label>
                            <input type="number" id="default-volume" class="form-control" value="0.1" min="0.01" step="0.01">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">الرمز الافتراضي</label>
                            <input type="text" id="default-symbol" class="form-control" value="XAUUSD">
                        </div>
                        
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="auto-trade" checked>
                            <label class="form-check-label">التداول الآلي</label>
                        </div>
                        
                        <button id="save-settings" class="btn btn-primary">
                            <i class="fas fa-save me-2"></i>حفظ الإعدادات
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- معلومات الحساب والإشارات -->
            <div class="col-md-8">
                <!-- معلومات الحساب -->
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5><i class="fas fa-user me-2"></i>معلومات الحساب</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3 text-center">
                                <small class="text-muted">الرصيد</small>
                                <div id="account-balance" class="h4 text-success">$0.00</div>
                            </div>
                            <div class="col-md-3 text-center">
                                <small class="text-muted">السيولة</small>
                                <div id="account-equity" class="h4 text-info">$0.00</div>
                            </div>
                            <div class="col-md-3 text-center">
                                <small class="text-muted">الهامش</small>
                                <div id="account-margin" class="h4 text-warning">$0.00</div>
                            </div>
                            <div class="col-md-3 text-center">
                                <small class="text-muted">رقم الحساب</small>
                                <div id="account-login" class="h4 text-muted">-</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- الإشارات المباشرة -->
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-signal me-2"></i>الإشارات المباشرة</h5>
                    </div>
                    <div class="card-body">
                        <div id="signals-container" class="row">
                            <div class="col-12 text-center text-muted">
                                <i class="fas fa-search fa-3x mb-3"></i>
                                <p>في انتظار الإشارات...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <!-- المراكز المفتوحة -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-chart-line me-2"></i>المراكز المفتوحة</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>الرمز</th>
                                        <th>النوع</th>
                                        <th>الحجم</th>
                                        <th>السعر</th>
                                        <th>الربح</th>
                                    </tr>
                                </thead>
                                <tbody id="positions-table">
                                    <tr>
                                        <td colspan="5" class="text-center text-muted">لا توجد مراكز مفتوحة</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- السجلات -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <h5><i class="fas fa-terminal me-2"></i>سجل البوت</h5>
                    </div>
                    <div class="card-body">
                        <div id="bot-logs" class="log-container">
                            <div class="text-muted">سيظهر سجل البوت هنا...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // إعداد الاتصال
        const socket = io();
        let isConnected = false;
        let botRunning = false;

        // عناصر الواجهة
        const startBtn = document.getElementById('start-bot');
        const stopBtn = document.getElementById('stop-bot');
        const botStatus = document.getElementById('bot-status');
        const mt5Status = document.getElementById('mt5-status');
        const connectionStatus = document.getElementById('connection-status');
        const signalsContainer = document.getElementById('signals-container');
        const positionsTable = document.getElementById('positions-table');
        const botLogs = document.getElementById('bot-logs');

        // أحداث الاتصال
        socket.on('connect', function() {
            isConnected = true;
            updateConnectionStatus('متصل', 'success');
        });

        socket.on('disconnect', function() {
            isConnected = false;
            updateConnectionStatus('منقطع', 'danger');
        });

        // أحداث البوت
        socket.on('bot_status', function(status) {
            updateBotStatus(status);
        });

        socket.on('signal_detected', function(signal) {
            addSignalToDisplay(signal);
            addLogMessage('INFO', `تم كشف إشارة: ${signal.type} لـ ${signal.symbol}`);
        });

        socket.on('trade_executed', function(trade) {
            addLogMessage('SUCCESS', `تم تنفيذ صفقة: ${trade.type} ${trade.symbol} بسعر ${trade.price}`);
        });

        socket.on('account_update', function(account) {
            updateAccountInfo(account);
        });

        socket.on('positions_update', function(positions) {
            updatePositions(positions);
        });

        // أزرار التحكم
        startBtn.addEventListener('click', function() {
            fetch('/api/bot/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogMessage('INFO', 'تم تشغيل البوت');
                    } else {
                        addLogMessage('ERROR', 'فشل في تشغيل البوت: ' + data.message);
                    }
                });
        });

        stopBtn.addEventListener('click', function() {
            fetch('/api/bot/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addLogMessage('INFO', 'تم إيقاف البوت');
                    } else {
                        addLogMessage('ERROR', 'فشل في إيقاف البوت: ' + data.message);
                    }
                });
        });

        // حفظ الإعدادات
        document.getElementById('save-settings').addEventListener('click', function() {
            const settings = {
                signal_delay: parseInt(document.getElementById('signal-delay').value),
                default_volume: parseFloat(document.getElementById('default-volume').value),
                default_symbol: document.getElementById('default-symbol').value,
                auto_trade: document.getElementById('auto-trade').checked
            };

            fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    addLogMessage('INFO', 'تم حفظ الإعدادات');
                } else {
                    addLogMessage('ERROR', 'فشل في حفظ الإعدادات');
                }
            });
        });

        // وظائف التحديث
        function updateConnectionStatus(status, type) {
            const indicator = connectionStatus.querySelector('.status-indicator');
            indicator.className = `status-indicator status-${type === 'success' ? 'online' : 'offline'}`;
            connectionStatus.innerHTML = `<span class="status-indicator status-${type === 'success' ? 'online' : 'offline'}"></span>${status}`;
            connectionStatus.className = `badge bg-${type}`;
        }

        function updateBotStatus(status) {
            if (status.running) {
                botStatus.textContent = 'يعمل';
                botStatus.className = 'fw-bold text-success';
                startBtn.disabled = true;
                stopBtn.disabled = false;
                botRunning = true;
            } else {
                botStatus.textContent = 'متوقف';
                botStatus.className = 'fw-bold text-danger';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                botRunning = false;
            }

            if (status.mt5_connected) {
                mt5Status.textContent = 'متصل';
                mt5Status.className = 'fw-bold text-success';
            } else {
                mt5Status.textContent = 'غير متصل';
                mt5Status.className = 'fw-bold text-danger';
            }

            if (status.account_info) {
                updateAccountInfo(status.account_info);
            }
        }

        function updateAccountInfo(account) {
            document.getElementById('account-balance').textContent = `$${account.balance ? account.balance.toFixed(2) : '0.00'}`;
            document.getElementById('account-equity').textContent = `$${account.equity ? account.equity.toFixed(2) : '0.00'}`;
            document.getElementById('account-margin').textContent = `$${account.margin ? account.margin.toFixed(2) : '0.00'}`;
            document.getElementById('account-login').textContent = account.login || '-';
        }

        function addSignalToDisplay(signal) {
            // مسح رسالة "في انتظار الإشارات"
            if (signalsContainer.querySelector('.text-muted')) {
                signalsContainer.innerHTML = '';
            }

            const signalCard = document.createElement('div');
            signalCard.className = 'col-md-6 mb-3 signal-card';

            const cardClass = signal.type === 'BUY' ? 'border-primary' : 
                             signal.type === 'SELL' ? 'border-danger' : 
                             signal.type === 'BULL' ? 'border-success' : 'border-warning';

            signalCard.innerHTML = `
                <div class="card ${cardClass}">
                    <div class="card-body text-center">
                        <h5 class="card-title">
                            <i class="fas fa-${signal.type === 'BUY' ? 'arrow-up' : 'arrow-down'} me-2"></i>
                            ${signal.type}
                        </h5>
                        <p class="card-text">
                            <strong>${signal.symbol}</strong><br>
                            <small class="text-muted">${new Date(signal.timestamp).toLocaleString('ar-SA')}</small><br>
                            <span class="badge bg-info">الثقة: ${(signal.confidence * 100).toFixed(1)}%</span>
                        </p>
                    </div>
                </div>
            `;

            signalsContainer.insertBefore(signalCard, signalsContainer.firstChild);

            // الاحتفاظ بآخر 6 إشارات فقط
            const signals = signalsContainer.querySelectorAll('.col-md-6');
            if (signals.length > 6) {
                for (let i = 6; i < signals.length; i++) {
                    signals[i].remove();
                }
            }
        }

        function updatePositions(positions) {
            if (positions.length === 0) {
                positionsTable.innerHTML = '<tr><td colspan="5" class="text-center text-muted">لا توجد مراكز مفتوحة</td></tr>';
                return;
            }

            positionsTable.innerHTML = positions.map(pos => {
                const profitClass = pos.profit >= 0 ? 'text-success' : 'text-danger';
                return `
                    <tr>
                        <td>${pos.symbol}</td>
                        <td>
                            <span class="badge bg-${pos.type === 'BUY' ? 'primary' : 'danger'}">
                                ${pos.type}
                            </span>
                        </td>
                        <td>${pos.volume}</td>
                        <td>${pos.price_open ? pos.price_open.toFixed(5) : '-'}</td>
                        <td class="${profitClass}">$${pos.profit ? pos.profit.toFixed(2) : '0.00'}</td>
                    </tr>
                `;
            }).join('');
        }

        function addLogMessage(level, message) {
            const time = new Date().toLocaleTimeString('ar-SA');
            const logClass = level === 'INFO' ? 'text-info' : 
                            level === 'SUCCESS' ? 'text-success' :
                            level === 'WARNING' ? 'text-warning' : 'text-danger';

            const logEntry = document.createElement('div');
            logEntry.className = `${logClass} mb-1`;
            logEntry.innerHTML = `[${time}] ${level}: ${message}`;

            botLogs.appendChild(logEntry);
            botLogs.scrollTop = botLogs.scrollHeight;

            // الاحتفاظ بآخر 100 سجل
            const logs = botLogs.querySelectorAll('div');
            if (logs.length > 100) {
                logs[0].remove();
            }
        }

        // تحميل البيانات الأولية
        fetch('/api/bot/status')
            .then(response => response.json())
            .then(status => updateBotStatus(status));

        fetch('/api/settings')
            .then(response => response.json())
            .then(settings => {
                document.getElementById('signal-delay').value = settings.signal_delay || 60;
                document.getElementById('default-volume').value = settings.default_volume || 0.1;
                document.getElementById('default-symbol').value = settings.default_symbol || 'XAUUSD';
                document.getElementById('auto-trade').checked = settings.auto_trade !== false;
            });
    </script>
</body>
</html>
'''

def create_app():
    """إنشاء تطبيق Flask"""
    app = Flask(__name__)
    app.secret_key = 'tradingview-mt5-bot-secret-key'
    
    # إعداد Socket.IO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # إعداد قاعدة البيانات
    db = Database()
    
    # إعداد البوت
    bot = TradingBot(db, socketio)
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/bot/start', methods=['POST'])
    def start_bot():
        try:
            success = bot.start()
            return jsonify({
                'status': 'success' if success else 'error',
                'message': 'تم تشغيل البوت' if success else 'فشل في تشغيل البوت'
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/api/bot/stop', methods=['POST'])
    def stop_bot():
        try:
            bot.stop()
            return jsonify({'status': 'success', 'message': 'تم إيقاف البوت'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/api/bot/status')
    def bot_status():
        try:
            return jsonify(bot.get_status())
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/api/settings', methods=['GET', 'POST'])
    def settings():
        if request.method == 'GET':
            return jsonify(bot.settings)
        else:
            try:
                new_settings = request.get_json()
                success = bot.update_settings(new_settings)
                return jsonify({
                    'status': 'success' if success else 'error',
                    'message': 'تم تحديث الإعدادات' if success else 'فشل في تحديث الإعدادات'
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
    
    return app, socketio, bot

# ==============================================================================
# نقطة البداية الرئيسية
# ==============================================================================

def main():
    """الوظيفة الرئيسية"""
    print("=" * 60)
    print("  🤖 بوت التداول الآلي - ربط TradingView مع MetaTrader 5")
    print("=" * 60)
    print()
    print("الميزات:")
    print("• كشف الإشارات من TradingView تلقائياً")
    print("• تأخير دقيقة واحدة قبل تنفيذ الصفقات")
    print("• دعم إشارات BUY/SELL و BULL/BEAR")
    print("• واجهة تحكم عربية سهلة الاستخدام")
    print("• مراقبة الحساب والصفقات مباشرة")
    print()
    print("🚀 جاري تشغيل الخادم...")
    print("📱 افتح المتصفح على: http://localhost:5000")
    print()
    print("⚠️  ملاحظة: هذه نسخة تجريبية تستخدم بيانات محاكاة")
    print("   للاستخدام الحقيقي، تأكد من تثبيت MetaTrader5 وإعداد الحساب")
    print()
    print("⌨️  اضغط Ctrl+C لإيقاف البوت")
    print("=" * 60)
    
    try:
        app, socketio, bot = create_app()
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n✅ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())