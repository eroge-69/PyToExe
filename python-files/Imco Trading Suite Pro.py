import os
import sys
import time
import uuid
import json
import logging
import threading
import sqlite3
import bcrypt
import hashlib
import requests
import webbrowser
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Callable
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.fernet import Fernet
from abc import ABC, abstractmethod
from logging.handlers import RotatingFileHandler
from PIL import Image, ImageTk
import platform
import socket
import hmac
import base64
import random
import subprocess
import psutil
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ====================== APP CONFIGURATION ======================
APP_NAME = "IMCO Trading Suite PRO"
VERSION = "3.0.0"
COMPANY = "IMCO Trading Solutions"
TERMS_URL = "https://www.imcotradingsolutions.com/terms"
PRIVACY_URL = "https://www.imcotradingsolutions.com/privacy"
SUPPORT_EMAIL = "support@imcotradingsolutions.com"

# Color scheme
PRIMARY_COLOR = "#2A8CFF"
SECONDARY_COLOR = "#1E1E2D"
ACCENT_COLOR = "#FF6B35"
TEXT_COLOR = "#FFFFFF"
DARK_BG = "#12121A"
LIGHT_TEXT = "#E0E0E0"
SUCCESS_GREEN = "#4BB543"
ERROR_RED = "#FF3B30"
WARNING_YELLOW = "#FFCC00"
PANEL_BG = "#252538"
BORDER_COLOR = "#3A3A4D"
HOVER_COLOR = "#3A3A4D"
ACTIVE_COLOR = "#3A7BFF"
PANEL_HEADER_BG = "#2A2A3A"
INPUT_BG = "#2A2A3A"
SECURE_GREEN = "#2ECC71"
WARNING_ORANGE = "#F39C12"
DISCLAIMER_YELLOW = "#F1C40F"

# Fonts
TITLE_FONT = ("Segoe UI Semibold", 24, "bold")
HEADER_FONT = ("Segoe UI Semibold", 16, "bold")
SUBHEADER_FONT = ("Segoe UI Semibold", 14)
BODY_FONT = ("Segoe UI", 12)
SMALL_FONT = ("Segoe UI", 10)
MONOSPACE_FONT = ("Consolas", 10)
BUTTON_FONT = ("Segoe UI Semibold", 12)
STAT_FONT = ("Segoe UI Semibold", 11)
DISCLAIMER_FONT = ("Segoe UI", 9)

# Order Execution Constants
DEFAULT_SLIPPAGE_MODEL = {
    'small_cap': {'base': 0.0015, 'size_factor': 0.0002, 'volatility_factor': 0.8},
    'mid_cap': {'base': 0.0010, 'size_factor': 0.00015, 'volatility_factor': 0.6},
    'large_cap': {'base': 0.0005, 'size_factor': 0.0001, 'volatility_factor': 0.4},
    'etf': {'base': 0.0003, 'size_factor': 0.00005, 'volatility_factor': 0.3}
}

MARKET_IMPACT_MODEL = {
    'normal': {'size_exponent': 0.7, 'liquidity_factor': 0.3},
    'high_vol': {'size_exponent': 0.8, 'liquidity_factor': 0.5},
    'low_liquidity': {'size_exponent': 0.9, 'liquidity_factor': 0.7}
}

# ====================== DATA CLASSES ======================
@dataclass
class Account:
    broker: str
    account_id: str
    balance: float
    equity: float
    nickname: str = ""
    api_key: str = ""
    api_secret: str = ""
    is_active: bool = True
    last_sync: str = ""
    paper_trading: bool = True
    compliance_acknowledged: bool = False

@dataclass
class OrderExecution:
    order_id: str
    timestamp: str
    filled_quantity: float
    avg_fill_price: float
    slippage: float
    market_impact: float
    status: str
    remaining_quantity: float = 0.0
    execution_notes: str = ""
    trade_cost: float = 0.0

# ====================== SECURITY CONFIGURATION ======================
class SecurityConfig:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize security configuration with encryption keys"""
        self.ENCRYPTION_KEY = self._get_encryption_key()
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate the encryption key with secure storage"""
        try:
            key_dir = os.path.join(os.path.expanduser("~"), ".imco_secure")
            os.makedirs(key_dir, exist_ok=True)
            os.chmod(key_dir, 0o700)
            
            key_path = os.path.join(key_dir, "encryption_key")
            
            if os.path.exists(key_path):
                with open(key_path, "rb") as f:
                    return f.read()
            
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
                os.chmod(key_path, 0o600)
            return key
        except Exception as e:
            logging.error(f"Failed to get encryption key: {e}")
            return Fernet.generate_key()

# ====================== DATABASE HANDLER ======================
class SecureDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = os.path.join(os.path.expanduser("~"), ".imco_secure")
            os.makedirs(db_dir, exist_ok=True)
            os.chmod(db_dir, 0x700)
            db_path = os.path.join(db_dir, "imco_trading_secure.db")
        
        self.db_path = db_path
        self.conn = self._create_connection()
        self.cipher = Fernet(SecurityConfig().ENCRYPTION_KEY)
        self._lock = threading.Lock()
        self._create_tables()
        self._create_triggers()
        self._create_views()
        
    def _create_connection(self):
        """Create a thread-safe database connection with WAL mode"""
        conn = None
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                conn = sqlite3.connect(
                    self.db_path,
                    timeout=30,
                    isolation_level='IMMEDIATE',
                    check_same_thread=False
                )
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA busy_timeout=5000")
                conn.row_factory = sqlite3.Row
                return conn
            except sqlite3.Error as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise RuntimeError(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                time.sleep(1)
    
    def _create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                broker TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_secret TEXT NOT NULL,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                investible_cash REAL,
                margin_available REAL,
                last_updated TEXT,
                nickname TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                last_sync TEXT,
                paper_trading BOOLEAN DEFAULT TRUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                compliance_acknowledged BOOLEAN DEFAULT FALSE
            )""",
            
            """CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                amount REAL NOT NULL,
                avg_price REAL NOT NULL,
                slippage REAL,
                market_impact REAL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                execution_time REAL,
                order_type TEXT,
                side TEXT NOT NULL,
                additional_cost REAL,
                strategy TEXT,
                target_price REAL,
                stop_loss REAL,
                take_profit REAL,
                trade_cost REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(account_id) REFERENCES accounts(account_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS order_executions (
                execution_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                filled_quantity REAL NOT NULL,
                avg_fill_price REAL NOT NULL,
                slippage REAL NOT NULL,
                market_impact REAL NOT NULL,
                status TEXT NOT NULL,
                remaining_quantity REAL,
                execution_notes TEXT,
                trade_cost REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS settings (
                notifications BOOLEAN DEFAULT TRUE,
                slippage_warning REAL DEFAULT 0.5,
                default_broker TEXT,
                aggressiveness TEXT DEFAULT 'medium',
                default_view TEXT DEFAULT 'dashboard',
                default_order_type TEXT DEFAULT 'amount',
                default_strategy TEXT DEFAULT 'Market',
                two_factor BOOLEAN DEFAULT FALSE,
                target_price_threshold REAL DEFAULT 1.0,
                session_timeout INTEGER DEFAULT 1800
            )"""
        ]
        
        try:
            with self._lock, self.conn:
                for table in tables:
                    self.conn.execute(table)
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            raise RuntimeError(f"Database initialization error: {e}")

    def _create_triggers(self):
        triggers = [                
            """CREATE TRIGGER IF NOT EXISTS update_order_on_execution
                AFTER INSERT ON order_executions
                FOR EACH ROW
                BEGIN
                    UPDATE orders 
                    SET 
                        avg_price = (SELECT AVG(avg_fill_price) FROM order_executions WHERE order_id = NEW.order_id),
                        slippage = (SELECT AVG(slippage) FROM order_executions WHERE order_id = NEW.order_id),
                        market_impact = (SELECT AVG(market_impact) FROM order_executions WHERE order_id = NEW.order_id),
                        trade_cost = (SELECT SUM(trade_cost) FROM order_executions WHERE order_id = NEW.order_id),
                        status = CASE 
                            WHEN NEW.remaining_quantity = 0 THEN 'filled'
                            WHEN NEW.remaining_quantity > 0 THEN 'partial'
                            ELSE status
                        END
                    WHERE order_id = NEW.order_id;
                END;"""
        ]
        
        try:
            with self._lock, self.conn:
                for trigger in triggers:
                    self.conn.execute(trigger)
        except Exception as e:
            logging.error(f"Error creating triggers: {e}")

    def _create_views(self):
        views = [
            """CREATE VIEW IF NOT EXISTS order_execution_metrics AS
                SELECT 
                    o.order_id,
                    o.symbol,
                    o.side,
                    o.amount,
                    o.quantity,
                    o.avg_price,
                    o.slippage,
                    o.market_impact,
                    o.additional_cost,
                    o.trade_cost,
                    o.execution_time,
                    COUNT(e.execution_id) as execution_count,
                    SUM(e.filled_quantity) as total_filled,
                    SUM(e.remaining_quantity) as total_remaining
                FROM orders o
                LEFT JOIN order_executions e ON o.order_id = e.order_id
                GROUP BY o.order_id;""",
                
            """CREATE VIEW IF NOT EXISTS execution_quality AS
                SELECT 
                    o.order_id,
                    o.symbol,
                    o.side,
                    o.quantity,
                    o.avg_price,
                    o.slippage * 100 as slippage_pct,
                    o.market_impact * 100 as market_impact_pct,
                    o.trade_cost,
                    o.execution_time,
                    (SELECT COUNT(*) FROM order_executions WHERE order_id = o.order_id) as execution_count,
                    (SELECT SUM(filled_quantity) FROM order_executions WHERE order_id = o.order_id) as total_filled,
                    (SELECT AVG(slippage * 100) FROM order_executions WHERE order_id = o.order_id) as avg_slippage_pct,
                    (SELECT AVG(market_impact * 100) FROM order_executions WHERE order_id = o.order_id) as avg_market_impact_pct,
                    (SELECT SUM(trade_cost) FROM order_executions WHERE order_id = o.order_id) as total_trade_cost
                FROM orders o;"""
        ]
        
        try:
            with self._lock, self.conn:
                for view in views:
                    self.conn.execute(view)
        except Exception as e:
            logging.error(f"Error creating views: {e}")

    def encrypt_data(self, data: str) -> str:
        if not data:
            return ""
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logging.error(f"Encryption failed: {e}")
            raise RuntimeError("Failed to encrypt sensitive data")

    def decrypt_data(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            raise RuntimeError("Failed to decrypt sensitive data")

    def add_account(self, account: Account) -> bool:
        try:
            encrypted_key = self.encrypt_data(account.api_key)
            encrypted_secret = self.encrypt_data(account.api_secret)
            
            with self._lock, self.conn:
                self.conn.execute(
                    """INSERT INTO accounts (
                        account_id, broker, api_key, api_secret, balance, equity,
                        investible_cash, margin_available, last_updated, nickname, is_active, 
                        last_sync, paper_trading, compliance_acknowledged
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        account.account_id,
                        account.broker,
                        encrypted_key,
                        encrypted_secret,
                        account.balance,
                        account.equity,
                        account.balance * 0.95,
                        account.balance * 0.90,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        account.nickname,
                        account.is_active,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        account.paper_trading,
                        account.compliance_acknowledged
                    )
                )
            return True
        except Exception as e:
            logging.error(f"Error adding account: {e}")
            raise RuntimeError(f"Error adding account: {e}")

    def get_accounts(self) -> List[Dict]:
        try:
            with self._lock:
                cursor = self.conn.execute(
                    "SELECT * FROM accounts WHERE is_active = TRUE"
                )
                accounts = []
                
                for row in cursor.fetchall():
                    account = dict(row)
                    try:
                        account['api_key'] = self.decrypt_data(account['api_key'])
                        account['api_secret'] = self.decrypt_data(account['api_secret'])
                    except Exception as e:
                        logging.error(f"Failed to decrypt credentials for account {account['account_id']}: {e}")
                        continue
                    accounts.append(account)
                    
                return accounts
        except Exception as e:
            logging.error(f"Error getting accounts: {e}")
            raise RuntimeError(f"Error getting accounts: {e}")

def get_orders(self, limit: int = 100, offset: int = 0) -> List[Dict]:
    try:
        with self._lock:
            cursor = self.conn.execute(
                """SELECT o.*, a.broker, a.nickname as account_nickname 
                FROM orders o 
                JOIN accounts a ON o.account_id = a.account_id
                ORDER BY o.timestamp DESC
                LIMIT ? OFFSET ?""",
                (limit, offset)
            )
            
            orders = []
            for row in cursor.fetchall():
                order = dict(row)
                if 'amount' in order and 'quantity' in order and float(order['quantity']) > 0:
                    order['price_per_share'] = float(order['amount']) / float(order['quantity'])
                else:
                    order['price_per_share'] = 0.0
                
                exec_cursor = self.conn.execute(
                    "SELECT * FROM order_executions WHERE order_id = ? ORDER BY timestamp",
                    (order['order_id'],)
                )
                order['executions'] = [dict(e) for e in exec_cursor.fetchall()]
                
                orders.append(order)
            return orders
    except Exception as e:
        logging.error(f"Error getting orders: {e}")
        return []

    def get_order_executions(self, order_id: str) -> List[Dict]:
        try:
            with self._lock:
                cursor = self.conn.execute(
                    "SELECT * FROM order_executions WHERE order_id = ? ORDER BY timestamp",
                    (order_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting order executions: {e}")
            return []

    def add_order_execution(self, execution: OrderExecution) -> bool:
        try:
            with self._lock, self.conn:
                self.conn.execute(
                    """INSERT INTO order_executions (
                        execution_id, order_id, timestamp, filled_quantity, 
                        avg_fill_price, slippage, market_impact, status, 
                        remaining_quantity, execution_notes, trade_cost
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        str(uuid.uuid4()),
                        execution.order_id,
                        execution.timestamp,
                        execution.filled_quantity,
                        execution.avg_fill_price,
                        execution.slippage,
                        execution.market_impact,
                        execution.status,
                        execution.remaining_quantity,
                        execution.execution_notes,
                        execution.trade_cost
                    )
                )
            return True
        except Exception as e:
            logging.error(f"Error adding order execution: {e}")
            raise RuntimeError(f"Error adding order execution: {e}")

    def get_settings(self) -> Dict:
        try:
            with self._lock:
                cursor = self.conn.execute("SELECT * FROM settings LIMIT 1")
                row = cursor.fetchone()
                return dict(row) if row else {}
        except Exception as e:
            logging.error(f"Error getting settings: {e}")
            return {}

    def close(self):
        try:
            if hasattr(self, 'conn'):
                with self._lock:
                    self.conn.close()
        except Exception as e:
            logging.error(f"Error closing database: {e}")

# ====================== ORDER EXECUTION ENGINE ======================
class OrderExecutionEngine:
    def __init__(self, broker_api: 'SecureBrokerAPI'):
        self.broker_api = broker_api
        self.active_orders = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._order_semaphore = threading.Semaphore(5)  # Limit concurrent orders
        
    def execute_order(self, order_details: Dict) -> Dict:
        """Execute an order with thread-safe concurrency control"""
        with self._order_semaphore:
            try:
                initial_result = self._execute_initial_order(order_details)
                
                if initial_result.get('status') == 'filled':
                    return initial_result
                
                order_id = initial_result['order_id']
                with self._lock:
                    self.active_orders[order_id] = {
                        'original_order': order_details,
                        'remaining_quantity': float(order_details['quantity']) - float(initial_result.get('filled_quantity', 0)),
                        'last_update': datetime.now(),
                        'status': 'partial' if initial_result.get('filled_quantity', 0) > 0 else 'pending'
                    }
                
                # Submit monitoring task with error handling
                future = self._executor.submit(self._monitor_order, order_id)
                future.add_done_callback(self._handle_monitor_exception)
                
                return initial_result
                
            except Exception as e:
                logging.error(f"Order execution failed: {str(e)}")
                return {
                    'status': 'failed',
                    'error': str(e),
                    'order_id': order_details.get('client_order_id', str(uuid.uuid4()))
                }
    
    def _handle_monitor_exception(self, future):
        """Handle exceptions from order monitoring tasks"""
        try:
            future.result()
        except Exception as e:
            logging.error(f"Order monitoring failed: {str(e)}")
    
    def _execute_initial_order(self, order_details: Dict) -> Dict:
        """Execute the initial order with market impact adjustment"""
        symbol = order_details['symbol']
        market_data = self.broker_api.get_market_data(symbol)
        current_price = market_data['last_price']
        
        adjusted_order = self._adjust_for_market_impact(order_details, market_data)
        result = self.broker_api.place_order(adjusted_order)
        
        if 'avg_fill_price' in result:
            avg_price = float(result['avg_fill_price'])
            filled_qty = float(result.get('filled_quantity', order_details['quantity']))
            
            slippage = (avg_price - current_price) / current_price if order_details['side'] == 'buy' \
                      else (current_price - avg_price) / current_price
                      
            market_impact = self._calculate_market_impact(
                symbol, 
                filled_qty, 
                current_price, 
                order_details.get('aggressiveness', 'medium')
            )
            
            trade_cost = (slippage + market_impact) * (filled_qty * avg_price)
            
            result.update({
                'slippage': slippage,
                'market_impact': market_impact,
                'trade_cost': trade_cost,
                'execution_notes': "Initial execution"
            })
        
        return result
    
    def _adjust_for_market_impact(self, order_details: Dict, market_data: Dict) -> Dict:
        """Adjust order parameters based on estimated market impact"""
        symbol = order_details['symbol']
        quantity = float(order_details['quantity'])
        current_price = market_data['last_price']
        aggressiveness = order_details.get('aggressiveness', 'medium')
        
        symbol_type = self._classify_symbol(symbol)
        impact_params = MARKET_IMPACT_MODEL['normal']
        
        size_ratio = quantity / market_data.get('avg_daily_volume', 1000000)
        
        # Convert aggressiveness to numeric value
        agg_map = {'low': 3, 'medium': 5, 'high': 8}
        agg_value = agg_map.get(aggressiveness, 5)
        
        market_impact = (
            impact_params['liquidity_factor'] * 
            (size_ratio ** impact_params['size_exponent']) * 
            (1 + (10 - agg_value) / 10))
        
        if 'limit_price' in order_details:
            limit_price = float(order_details['limit_price'])
            if order_details['side'] == 'buy':
                adjusted_price = limit_price * (1 + market_impact)
            else:
                adjusted_price = limit_price * (1 - market_impact)
                
            order_details['limit_price'] = str(adjusted_price)
        
        return order_details
    
    def _calculate_market_impact(self, symbol: str, quantity: float, current_price: float, aggressiveness: str) -> float:
        """Calculate estimated market impact of an order"""
        symbol_type = self._classify_symbol(symbol)
        impact_params = MARKET_IMPACT_MODEL['normal']
        
        size_ratio = quantity / 1000000
        
        # Convert aggressiveness to numeric value
        agg_map = {'low': 3, 'medium': 5, 'high': 8}
        agg_value = agg_map.get(aggressiveness, 5)
        
        market_impact = (
            impact_params['liquidity_factor'] * 
            (size_ratio ** impact_params['size_exponent']) * 
            (1 + (10 - agg_value) / 10))
        
        return market_impact
    
    def _calculate_slippage(self, symbol: str, quantity: float, current_price: float, aggressiveness: str) -> float:
        """Calculate estimated slippage for an order"""
        symbol_type = self._classify_symbol(symbol)
        slippage_params = DEFAULT_SLIPPAGE_MODEL.get(symbol_type, DEFAULT_SLIPPAGE_MODEL['large_cap'])
        
        size_factor = quantity * slippage_params['size_factor']
        volatility_factor = 1.0
        
        # Convert aggressiveness to numeric value
        agg_map = {'low': 3, 'medium': 5, 'high': 8}
        agg_value = agg_map.get(aggressiveness, 5)
        
        base_slippage = slippage_params['base'] * volatility_factor
        size_adjusted_slippage = size_factor * volatility_factor
        urgency_adjusted_slippage = (1 + (10 - agg_value)/10) * (base_slippage + size_adjusted_slippage)
        
        return urgency_adjusted_slippage
    
    def _classify_symbol(self, symbol: str) -> str:
        """Classify a symbol based on market capitalization"""
        if symbol.endswith('.TO') or symbol.endswith('.V'):
            return 'small_cap'
        elif any(s in symbol for s in ['AAPL', 'MSFT', 'GOOG', 'AMZN']):
            return 'large_cap'
        else:
            return 'mid_cap'
    
    def _monitor_order(self, order_id: str) -> None:
        """Monitor an order's execution status"""
        while not self._stop_event.is_set():
            try:
                with self._lock:
                    if order_id not in self.active_orders:
                        break
                        
                    order_info = self.active_orders[order_id]
                    if order_info['status'] == 'filled':
                        break
                
                status = self.broker_api.get_order_status(order_id)
                
                if status.get('status') == 'filled':
                    self._record_completed_order(order_id, status)
                    break
                    
                elif status.get('status') == 'partially_filled':
                    self._handle_partial_fill(order_id, status)
                    
                with self._lock:
                    if (datetime.now() - order_info['last_update']).total_seconds() > 30:
                        self._adapt_order_strategy(order_id)
                    
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Error monitoring order {order_id}: {str(e)}")
                time.sleep(10)
    
    def _handle_partial_fill(self, order_id: str, status: Dict) -> None:
        """Handle a partial fill of an order"""
        with self._lock:
            if order_id not in self.active_orders:
                return
                
            order_info = self.active_orders[order_id]
            filled_qty = float(status.get('filled_quantity', 0))
            remaining_qty = float(status.get('remaining_quantity', order_info['remaining_quantity']))
            avg_price = float(status.get('avg_fill_price', 0))
            
            original_price = float(order_info['original_order'].get('limit_price', avg_price))
            slippage = (avg_price - original_price) / original_price if order_info['original_order']['side'] == 'buy' \
                      else (original_price - avg_price) / original_price
            
            market_impact = self._calculate_market_impact(
                order_info['original_order']['symbol'],
                filled_qty,
                original_price,
                order_info['original_order'].get('aggressiveness', 'medium')
            )
            
            trade_cost = (slippage + market_impact) * (filled_qty * avg_price)
            
            execution = OrderExecution(
                order_id=order_id,
                timestamp=datetime.now().isoformat(),
                filled_quantity=filled_qty,
                avg_fill_price=avg_price,
                slippage=slippage,
                market_impact=market_impact,
                status='partial',
                remaining_quantity=remaining_qty,
                execution_notes=f"Partial fill - {filled_qty} shares at {avg_price}",
                trade_cost=trade_cost
            )
            
            self.broker_api.db.add_order_execution(execution)
            
            order_info['remaining_quantity'] = remaining_qty
            order_info['status'] = 'partial'
            order_info['last_update'] = datetime.now()
    
    def _record_completed_order(self, order_id: str, status: Dict) -> None:
        """Record a completed order"""
        with self._lock:
            if order_id not in self.active_orders:
                return
                
            order_info = self.active_orders[order_id]
            filled_qty = float(status.get('filled_quantity', order_info['original_order']['quantity']))
            avg_price = float(status.get('avg_fill_price', 0))
            
            original_price = float(order_info['original_order'].get('limit_price', avg_price))
            slippage = (avg_price - original_price) / original_price if order_info['original_order']['side'] == 'buy' \
                      else (original_price - avg_price) / original_price
            
            market_impact = self._calculate_market_impact(
                order_info['original_order']['symbol'],
                filled_qty,
                original_price,
                order_info['original_order'].get('aggressiveness', 'medium')
            )
            
            trade_cost = (slippage + market_impact) * (filled_qty * avg_price)
            
            execution = OrderExecution(
                order_id=order_id,
                timestamp=datetime.now().isoformat(),
                filled_quantity=filled_qty,
                avg_fill_price=avg_price,
                slippage=slippage,
                market_impact=market_impact,
                status='filled',
                remaining_quantity=0,
                execution_notes="Order fully filled",
                trade_cost=trade_cost
            )
            
            self.broker_api.db.add_order_execution(execution)
            
            order_info['status'] = 'filled'
            order_info['remaining_quantity'] = 0
            order_info['last_update'] = datetime.now()
            
            del self.active_orders[order_id]
    
    def _adapt_order_strategy(self, order_id: str) -> None:
        """Adapt order strategy based on market conditions"""
        with self._lock:
            if order_id not in self.active_orders:
                return
                
            order_info = self.active_orders[order_id]
            original_order = order_info['original_order']
            
            market_data = self.broker_api.get_market_data(original_order['symbol'])
            current_price = market_data['last_price']
            
            if original_order.get('limit_price'):
                limit_price = float(original_order['limit_price'])
                price_diff = abs(current_price - limit_price) / limit_price
                
                if price_diff > 0.01:
                    new_order = original_order.copy()
                    new_order['limit_price'] = str(current_price)
                    new_order['client_order_id'] = order_id
                    
                    try:
                        self.broker_api.modify_order(order_id, new_order)
                        order_info['last_update'] = datetime.now()
                        
                        execution = OrderExecution(
                            order_id=order_id,
                            timestamp=datetime.now().isoformat(),
                            filled_quantity=0,
                            avg_fill_price=0,
                            slippage=0,
                            market_impact=0,
                            status='modified',
                            remaining_quantity=order_info['remaining_quantity'],
                            execution_notes=f"Order modified - new price {current_price}",
                            trade_cost=0
                        )
                        
                        self.broker_api.db.add_order_execution(execution)
                        
                    except Exception as e:
                        logging.error(f"Failed to modify order {order_id}: {str(e)}")
    
    def stop(self):
        """Stop all order monitoring"""
        self._stop_event.set()
        self._executor.shutdown(wait=False)

# ====================== BROKER API ABSTRACTIONS ======================
class SecureBrokerAuth(ABC):
    def __init__(self):
        self.last_used = None
        self.usage_count = 0
        self.rate_limit = 60
        self.rate_limit_reset = time.time() + 60
        self._lock = threading.Lock()
        
    def __call__(self, r):
        """Apply authentication to a request with rate limiting"""
        current_time = time.time()
        
        with self._lock:
            if current_time > self.rate_limit_reset:
                self.usage_count = 0
                self.rate_limit_reset = current_time + 60
                
            if self.usage_count >= self.rate_limit:
                raise RuntimeError("API rate limit exceeded")
                
            self.usage_count += 1
            self.last_used = current_time
        
        return self._secure_request(r)
        
    @abstractmethod
    def _secure_request(self, r):
        pass

class IBAuth(SecureBrokerAuth):
    def __init__(self, api_key, api_secret):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self._token = None
        self._token_expiry = 0
        self._token_lock = threading.Lock()
    
    def _secure_request(self, r):
        """Secure the request with OAuth token"""
        with self._token_lock:
            if time.time() > self._token_expiry:
                self._refresh_token()
                
            r.headers.update({
                'Authorization': f"Bearer {self._token}",
                'X-API-Key': self.api_key,
                'X-API-Nonce': str(int(time.time() * 1000)),
                'X-API-Signature': self._generate_signature(r)
            })
        return r
    
    def _refresh_token(self):
        """Refresh the OAuth token"""
        auth_url = "https://api.ibkr.com/v1/api/oauth/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.api_secret
        }
        
        response = self._retry_request(
            "POST", auth_url, data=auth_data, 
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self._token = data['access_token']
            self._token_expiry = time.time() + data['expires_in'] - 60
        else:
            raise ConnectionError(f"Failed to refresh IBKR token: {response.text}")
    
    def _generate_signature(self, r):
        """Generate a request signature"""
        timestamp = str(int(time.time() * 1000))
        message = f"{r.method}{r.path_url}{timestamp}{r.body if r.body else ''}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

class SecureBrokerAPI(ABC):
    def __init__(self, auth: SecureBrokerAuth):
        self.auth = auth
        self.session = self._create_session()
        self.session.auth = auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': f'{APP_NAME}/{VERSION}',
            'X-Request-ID': str(uuid.uuid4())
        })
        self.connected = False
        self.last_error = None
        self.connection_time = None
        self.request_timeout = 30
        self._lock = threading.Lock()
        self.execution_engine = OrderExecutionEngine(self)
        self.db = SecureDatabase()
    
    def _create_session(self):
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def get_account_balance(self) -> Dict:
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict:
        pass
    
    @abstractmethod
    def place_order(self, order: Dict) -> Dict:
        pass
    
    @abstractmethod
    def modify_order(self, order_id: str, order: Dict) -> Dict:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: str, start: str, end: str) -> List[Dict]:
        pass

    def _handle_rate_limit(self, response):
        """Handle API rate limiting"""
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logging.warning(f"Rate limited, retrying after {retry_after} seconds")
            time.sleep(retry_after)
            return True
        return False

    def _validate_response(self, response):
        """Validate API response and handle errors"""
        if response.status_code == 401:
            self.connected = False
            raise ConnectionError("Invalid API credentials")
            
        if response.status_code == 403:
            raise ConnectionError("Insufficient permissions")
            
        if not 200 <= response.status_code < 300:
            raise ConnectionError(f"API request failed: {response.text}")
            
        try:
            data = response.json()
            
            if isinstance(data, dict) and 'error' in data:
                raise ConnectionError(data['error'])
                
            return data
        except ValueError:
            raise ConnectionError("Invalid JSON response")

    def _secure_request(self, method, url, **kwargs):
        """Make a secure API request with error handling"""
        try:
            kwargs.setdefault('timeout', self.request_timeout)
            response = self.session.request(method, url, **kwargs)
            
            if self._handle_rate_limit(response):
                return self._secure_request(method, url, **kwargs)
                
            return self._validate_response(response)
        except requests.exceptions.SSLError as e:
            raise ConnectionError(f"SSL error: {str(e)}")
        except requests.exceptions.Timeout:
            raise ConnectionError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error: {str(e)}")

class SecureIBKRAPI(SecureBrokerAPI):
    BASE_URL = "https://api.ibkr.com/v1/api"
    
    def connect(self) -> bool:
        try:
            response = self._secure_request("GET", f"{self.BASE_URL}/iserver/auth/status")
            if response.get('authenticated', False):
                self.connected = True
                self.connection_time = datetime.now()
                return True
            else:
                raise ConnectionError("Not authenticated with IBKR")
        except Exception as e:
            self.last_error = str(e)
            self.connected = False
            raise ConnectionError(f"Failed to connect to Interactive Brokers: {str(e)}")

    def get_account_balance(self) -> Dict:
        response = self._secure_request("GET", f"{self.BASE_URL}/portfolio/accounts")
        account_id = response[0]['accountId']
        
        summary = self._secure_request("GET", 
            f"{self.BASE_URL}/portfolio/{account_id}/summary")
        
        return {
            'balance': float(summary['totalCashValue']),
            'equity': float(summary['netLiquidation']),
            'buying_power': float(summary['buyingPower']),
            'last_updated': datetime.now().isoformat()
        }

    def get_market_data(self, symbol: str) -> Dict:
        contracts = self._secure_request("GET", 
            f"{self.BASE_URL}/trsrv/stocks?symbols={symbol}")
        
        if not contracts or symbol not in contracts:
            raise ValueError(f"Symbol {symbol} not found")
            
        conid = contracts[symbol][0]['contracts'][0]['conid']
        
        response = self._secure_request("GET", 
            f"{self.BASE_URL}/iserver/marketdata/snapshot?conids={conid}&fields=31,84,86")
        
        if not response:
            raise ValueError("No market data returned")
            
        data = response[0]
        return {
            'symbol': symbol,
            'bid_price': float(data['31']),
            'ask_price': float(data['84']),
            'last_price': float(data['86']),
            'timestamp': datetime.now().isoformat(),
            'avg_daily_volume': 1000000
        }

    def place_order(self, order: Dict) -> Dict:
        contracts = self._secure_request("GET", 
            f"{self.BASE_URL}/trsrv/stocks?symbols={order['symbol']}")
        
        if not contracts or order['symbol'] not in contracts:
            raise ValueError(f"Symbol {order['symbol']} not found")
            
        conid = contracts[order['symbol']][0]['contracts'][0]['conid']
        
        payload = {
            "acctId": self.auth.account_id,
            "conid": conid,
            "secType": f"{order['symbol']}:STK",
            "orderType": "LMT" if order.get('limit_price') else "MKT",
            "side": order['side'].upper(),
            "tif": order.get('time_in_force', 'DAY'),
            "quantity": float(order['quantity']),
            "outsideRTH": True
        }
        
        if order.get('limit_price'):
            payload['price'] = float(order['limit_price'])
        
        response = self._secure_request("POST", 
            f"{self.BASE_URL}/iserver/account/{self.auth.account_id}/order", 
            json=payload)
        
        if isinstance(response, list) and len(response) > 0:
            if 'error' in response[0]:
                raise ConnectionError(response[0]['error'])
            
            order_id = response[0].get('id', str(uuid.uuid4()))
            status = response[0].get('order_status', 'Pending')
            
            status_mapping = {
                'Pending': 'pending',
                'PreSubmitted': 'pending',
                'Submitted': 'pending',
                'Filled': 'filled',
                'Cancelled': 'cancelled',
                'Expired': 'expired',
                'Rejected': 'rejected'
            }
            
            return {
                'order_id': order_id,
                'status': status_mapping.get(status, 'pending'),
                'avg_fill_price': float(response[0].get('avg_price', 0)),
                'filled_quantity': float(response[0].get('filledQuantity', 0)),
                'remaining_quantity': float(response[0].get('remainingQuantity', float(order['quantity'])))
            }
        else:
            raise ConnectionError("Unexpected response from IBKR")

    def modify_order(self, order_id: str, order: Dict) -> Dict:
        self.cancel_order(order_id)
        return self.place_order(order)

    def cancel_order(self, order_id: str) -> bool:
        response = self._secure_request("DELETE", 
            f"{self.BASE_URL}/iserver/account/{self.auth.account_id}/order/{order_id}")
        return response is not None

    def get_order_status(self, order_id: str) -> Dict:
        response = self._secure_request("GET", 
            f"{self.BASE_URL}/iserver/account/order/status/{order_id}")
        
        status_mapping = {
            'Pending': 'pending',
            'PreSubmitted': 'pending',
            'Submitted': 'pending',
            'Filled': 'filled',
            'Cancelled': 'cancelled',
            'Expired': 'expired',
            'Rejected': 'rejected'
        }
        
        return {
            'order_id': order_id,
            'status': status_mapping.get(response.get('order_status', 'pending'), 'pending'),
            'avg_fill_price': float(response.get('avg_price', 0)),
            'filled_quantity': float(response.get('filledQuantity', 0)),
            'remaining_quantity': float(response.get('remainingQuantity', 0))
        }

    def get_positions(self) -> List[Dict]:
        response = self._secure_request("GET", f"{self.BASE_URL}/portfolio/positions")
        return [{
            'symbol': pos['contractDesc'],
            'quantity': float(pos['position']),
            'avg_price': float(pos['avgCost'])
        } for pos in response]

    def get_historical_data(self, symbol: str, timeframe: str, start: str, end: str) -> List[Dict]:
        contracts = self._secure_request("GET", 
            f"{self.BASE_URL}/trsrv/stocks?symbols={symbol}")
        
        if not contracts or symbol not in contracts:
            raise ValueError(f"Symbol {symbol} not found")
            
        conid = contracts[symbol][0]['contracts'][0]['conid']
        
        tf_mapping = {
            '1m': '1min',
            '5m': '5mins',
            '15m': '15mins',
            '1h': '1h',
            '1d': '1d'
        }
        
        if timeframe not in tf_mapping:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
            
        params = {
            'conid': conid,
            'period': '1y',
            'bar': tf_mapping[timeframe]
        }
        
        response = self._secure_request("GET", 
            f"{self.BASE_URL}/iserver/marketdata/history", params=params)
        
        return [{
            'time': bar['t'],
            'open': float(bar['o']),
            'high': float(bar['h']),
            'low': float(bar['l']),
            'close': float(bar['c']),
            'volume': float(bar['v'])
        } for bar in response['data']]

# ====================== BROKER MANAGEMENT ======================
class SecureBrokerFactory:
    @staticmethod
    def create_broker(credentials: Dict) -> SecureBrokerAPI:
        auth = IBAuth(credentials['api_key'], credentials['api_secret'])
        return SecureIBKRAPI(auth)

class SecureBrokerConnectionManager:
    def __init__(self, db: SecureDatabase):
        self.brokers = {}
        self.active_broker = None
        self.db = db
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def add_broker(self, name: str, broker: SecureBrokerAPI):
        with self.lock:
            self.brokers[name] = broker
    
    def connect_all(self):
        results = {}
        
        for name, broker in self.brokers.items():
            try:
                if broker.connect():
                    results[name] = True
                    logging.info(f"Connected to {name}")
                else:
                    results[name] = False
                    logging.warning(f"Failed to connect to {name}")
            except Exception as e:
                results[name] = str(e)
                logging.error(f"Error connecting to {name}: {str(e)}")
        
        return results
    
    def set_active_broker(self, name: str):
        with self.lock:
            if name in self.brokers:
                self.active_broker = self.brokers[name]
                return True
            return False
    
    def get_active_broker(self) -> SecureBrokerAPI:
        with self.lock:
            return self.active_broker
    
    def execute_order(self, order: Dict) -> Dict:
        if not self.active_broker:
            raise ValueError("No active broker selected")
            
        required_fields = ['symbol', 'quantity', 'side']
        if not all(field in order for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields}")
            
        try:
            return self.active_broker.execution_engine.execute_order(order)
        except Exception as e:
            logging.error(f"Order execution failed: {str(e)}")
            raise

# ====================== UI COMPONENTS ======================
class LoadingDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Processing", message="Please wait..."):
        super().__init__(master)
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self._center_window()
        
        # Create container frame
        container = ctk.CTkFrame(self, fg_color=SECONDARY_COLOR)
        container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Add loading animation
        self.loading_canvas = ctk.CTkCanvas(container, width=100, height=100, bg=SECONDARY_COLOR, highlightthickness=0)
        self.loading_canvas.pack(pady=(20, 10))
        
        # Create loading text
        self.label = ctk.CTkLabel(
            container, 
            text=message, 
            font=BODY_FONT,
            text_color=LIGHT_TEXT
        )
        self.label.pack(pady=(0, 20))
        
        # Create progress bar
        self.progress = ctk.CTkProgressBar(
            container, 
            mode='indeterminate',
            height=4,
            fg_color="#333344",
            progress_color=PRIMARY_COLOR
        )
        self.progress.pack(fill="x", padx=30, pady=(0, 20))
        self.progress.start()
        
        # Create cancel button
        self.cancel_button = ctk.CTkButton(
            container, 
            text="Cancel", 
            command=self._on_cancel,
            fg_color=ERROR_RED,
            hover_color="#D63031",
            width=100,
            height=30
        )
        self.cancel_button.pack(pady=(0, 10))
        
        self.cancelled = False
        
        # Start animation
        self._animate_loading()
    
    def _animate_loading(self):
        """Animate the loading spinner"""
        self.loading_canvas.delete("all")
        size = 80
        x, y = 50, 50
        radius = 30
        width = 8
        
        # Draw outer circle
        self.loading_canvas.create_oval(
            x-radius, y-radius, x+radius, y+radius,
            outline="#333344", width=width
        )
        
        # Draw animated arc
        for i in range(0, 360, 30):
            start = i + (time.time() * 50) % 360
            extent = 90
            self.loading_canvas.create_arc(
                x-radius, y-radius, x+radius, y+radius,
                start=start, extent=extent,
                outline=PRIMARY_COLOR, width=width,
                style="arc"
            )
        
        self.after(50, self._animate_loading)
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_cancel(self):
        self.cancelled = True
        self.destroy()
    
    def update_message(self, new_message):
        self.label.configure(text=new_message)
        self.update()

class ComplianceDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str, compliance_type: str, version: str):
        super().__init__(master)
        
        self.title(title)
        self.geometry("900x700")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.compliance_type = compliance_type
        self.version = version
        self.result = False
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Main container
        container = ctk.CTkFrame(self, fg_color=SECONDARY_COLOR)
        container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text=title,
            font=TITLE_FONT,
            text_color=PRIMARY_COLOR
        ).pack(side="left")
        
        # Content frame
        content_frame = ctk.CTkFrame(container, fg_color=DARK_BG)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollable text
        scroll_frame = ctk.CTkScrollableFrame(content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            scroll_frame,
            text=message,
            font=BODY_FONT,
            wraplength=800,
            justify="left"
        ).pack(fill="both", expand=True, padx=10, pady=10)
        
        # Checkbox frame
        checkbox_frame = ctk.CTkFrame(container, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.accept_var = ctk.BooleanVar(value=False)
        terms_check = ctk.CTkCheckBox(
            checkbox_frame,
            text="I acknowledge and agree to the above terms",
            variable=self.accept_var,
            font=BODY_FONT
        )
        terms_check.pack(anchor="w", pady=(0, 10))
        
        # Buttons frame
        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(fill="x", padx=20, pady=(0, 20))
        
        # Decline button
        ctk.CTkButton(
            buttons,
            text="Decline",
            command=self._on_decline,
            fg_color=ERROR_RED,
            hover_color="#D63031",
            width=120,
            height=40
        ).pack(side="left", padx=10)
        
        # Accept button
        self.accept_button = ctk.CTkButton(
            buttons,
            text="Accept",
            command=self._on_accept,
            fg_color=SECURE_GREEN,
            hover_color="#27AE60",
            width=120,
            height=40,
            state="disabled"
        )
        self.accept_button.pack(side="right", padx=10)
        
        self.accept_var.trace_add("write", lambda *_: self._update_accept_button())
        
        self._center_window()
        self.grab_set()
        self.transient(master)
        self.wait_visibility()
        self.focus_set()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _update_accept_button(self):
        if self.accept_var.get():
            self.accept_button.configure(state="normal")
        else:
            self.accept_button.configure(state="disabled")

    def _on_accept(self):
        self.result = True
        self.destroy()
    
    def _on_decline(self):
        self.result = False
        self.destroy()
    
    def _on_close(self):
        self.result = False
        self.destroy()

class AppLoadingScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.title(f"{APP_NAME} - Loading")
        self.geometry("500x300")
        self.resizable(False, False)
        self.overrideredirect(True)
        
        self._center_window()
        
        # Main container
        container = ctk.CTkFrame(self, fg_color=SECONDARY_COLOR)
        container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(container, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", padx=20, pady=(40, 20))
        
        ctk.CTkLabel(
            logo_frame,
            text="IMCO",
            font=("Segoe UI Semibold", 32),
            text_color=PRIMARY_COLOR
        ).pack(side="top", pady=(0, 5))
        
        ctk.CTkLabel(
            logo_frame,
            text="Trading Suite PRO",
            font=("Segoe UI", 14),
            text_color=LIGHT_TEXT
        ).pack(side="top")
        
        # Loading message
        self.loading_label = ctk.CTkLabel(
            container,
            text="Initializing application...",
            font=BODY_FONT,
            text_color=LIGHT_TEXT
        )
        self.loading_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            container, 
            mode='indeterminate',
            height=4,
            fg_color="#333344",
            progress_color=PRIMARY_COLOR
        )
        self.progress.pack(fill="x", padx=50, pady=(0, 30))
        self.progress.start()
        
        # Version info
        ctk.CTkLabel(
            container,
            text=f"Version {VERSION}",
            font=SMALL_FONT,
            text_color="#555566"
        ).pack(side="bottom", pady=10)
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def update_message(self, message: str):
        self.loading_label.configure(text=message)
        self.update()

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str):
        super().__init__(master)
        
        self.title(title)
        self.geometry("500x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self._center_window()
        
        # Main container
        container = ctk.CTkFrame(self, fg_color=SECONDARY_COLOR)
        container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Error icon
        icon_frame = ctk.CTkFrame(container, fg_color="transparent")
        icon_frame.pack(pady=(30, 20))
        
        ctk.CTkLabel(
            icon_frame,
            text="⚠️",
            font=("Segoe UI", 48)
        ).pack()
        
        # Error message
        ctk.CTkLabel(
            container,
            text=message,
            font=BODY_FONT,
            text_color=LIGHT_TEXT,
            wraplength=400,
            justify="center"
        ).pack(pady=(0, 30), padx=30)
        
        # OK button
        ctk.CTkButton(
            container,
            text="OK",
            command=self.destroy,
            width=120,
            height=40,
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR
        ).pack()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

# ====================== MAIN APPLICATION ======================
class ImcoTradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.current_account = None
        self.is_admin = False
        self.order_preview_data = None
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize UI components
        self._setup_window((1400, 900))
        self._configure_appearance("Dark")
        
        # Initialize loading screen
        self.loading_screen = AppLoadingScreen(self)
        self.after(100, self._initialize_app)

    def _initialize_app(self):
        """Initialize application components"""
        try:
            self.loading_screen.update_message("Initializing database...")
            self.db = SecureDatabase()
            
            self.loading_screen.update_message("Setting up broker manager...")
            self.broker_manager = SecureBrokerConnectionManager(self.db)
            
            self.loading_screen.update_message("Configuring interface...")
            self.loading_screen.destroy()
            self.show_main_app()
        except Exception as e:
            self.loading_screen.destroy()
            ErrorDialog(self, "Initialization Error", f"Failed to initialize application:\n{str(e)}")
            self.destroy()

    def _setup_window(self, size: tuple) -> None:
        """Configure main window settings"""
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(1200, 800)
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def _configure_appearance(self, mode: str):
        """Configure the application's visual appearance"""
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
        
        # Configure custom color mappings
        color_map = {
            "primary": PRIMARY_COLOR,
            "secondary": SECONDARY_COLOR,
            "accent": ACCENT_COLOR,
            "text": TEXT_COLOR,
            "dark_bg": DARK_BG,
            "light_text": LIGHT_TEXT,
            "success": SUCCESS_GREEN,
            "error": ERROR_RED,
            "warning": WARNING_YELLOW,
            "panel_bg": PANEL_BG,
            "border": BORDER_COLOR,
            "hover": HOVER_COLOR,
            "active": ACTIVE_COLOR
        }
        
        # Update CTk theme settings
        for color_name, color_value in color_map.items():
            ctk.ThemeManager.theme[color_name] = color_value

    def show_main_app(self):
        """Show the main application interface"""
        self.clear_window()
        self.is_admin = False
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_container = ctk.CTkFrame(self, fg_color=SECONDARY_COLOR, corner_radius=0)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        self._create_sidebar(main_container)
        self._create_status_bar(main_container)
        self._create_content_area(main_container)

        self.show_order_management()

    def _create_sidebar(self, parent):
        """Create the sidebar navigation"""
        sidebar = ctk.CTkFrame(
            parent,
            width=220,
            corner_radius=0,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR
        )
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)

        # Logo section
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", padx=10, pady=(15, 20))
        
        ctk.CTkLabel(
            logo_frame,
            text="IMCO",
            font=("Segoe UI Semibold", 24),
            text_color=PRIMARY_COLOR
        ).pack(side="top", pady=(0, 5))
        
        ctk.CTkLabel(
            logo_frame,
            text="Trading Suite",
            font=("Segoe UI", 12),
            text_color=LIGHT_TEXT
        ).pack(side="top")

        # Navigation buttons
        nav_buttons = [
            ("Order Management", "💱", self.show_order_management),
            ("History", "📋", self.show_order_history),
            ("Link Account", "🔗", self.show_link_account),
            ("Support", "🛟", lambda: webbrowser.open("https://www.imcotradingsolutions.com/support"))
        ]

        for text, icon, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {text}",
                command=command,
                fg_color="transparent",
                anchor="w",
                hover_color=HOVER_COLOR,
                font=BODY_FONT,
                height=45,
                corner_radius=5,
                border_spacing=15
            )
            btn.pack(fill="x", padx=5, pady=2)

    def _create_status_bar(self, parent):
        """Create the status bar with legal disclaimer"""
        self.status_bar = ctk.CTkFrame(
            parent,
            height=35,
            fg_color="#1E1E2D",
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Add legal disclaimer
        disclaimer = ctk.CTkLabel(
            self.status_bar,
            text="For self-directed investors only. Not financial advice. Trading involves risk.",
            font=DISCLAIMER_FONT,
            text_color=DISCLAIMER_YELLOW
        )
        disclaimer.pack(side="left", padx=10)
        
        # Add terms/privacy links
        links = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        links.pack(side="right", padx=10)
        
        ctk.CTkButton(
            links,
            text="Terms",
            command=lambda: webbrowser.open(TERMS_URL),
            width=60,
            height=20,
            font=SMALL_FONT,
            fg_color="transparent",
            hover_color=HOVER_COLOR,
            text_color=PRIMARY_COLOR
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            links,
            text="Privacy",
            command=lambda: webbrowser.open(PRIVACY_URL),
            width=60,
            height=20,
            font=SMALL_FONT,
            fg_color="transparent",
            hover_color=HOVER_COLOR,
            text_color=PRIMARY_COLOR
        ).pack(side="left")

    def _create_content_area(self, parent):
        """Create the main content area"""
        self.content_area = ctk.CTkFrame(
            parent,
            fg_color=PANEL_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        self.content_area.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    def _load_broker_connections(self):
        """Load any saved broker connections"""
        try:
            accounts = self.db.get_accounts()
            for account in accounts:
                broker = SecureBrokerFactory.create_broker({
                    'api_key': account['api_key'],
                    'api_secret': account['api_secret']
                })
                self.broker_manager.add_broker(account['broker'], broker)
                
                if len(accounts) == 1:  # Auto-select if only one account
                    self.broker_manager.set_active_broker(account['broker'])
        except Exception as e:
            logging.error(f"Error loading broker connections: {str(e)}")

    def show_broker_compliance_dialog(self):
        """Show broker-specific compliance dialog before linking account"""
        broker_name = "Interactive Brokers"
        
        message = f"""By linking your {broker_name} account, you acknowledge and agree to:

1. Comply with {broker_name}'s API Terms of Service
2. Use the API only as permitted by your broker agreement
3. Acknowledge that IMCO is not affiliated with {broker_name}

You must review and agree to {broker_name}'s API Terms before proceeding:
https://www.interactivebrokers.com/api/doc.html

Trading involves substantial risk of loss and is not suitable for all investors.
"""
        
        dialog = ComplianceDialog(
            self,
            title=f"{broker_name} Compliance Agreement",
            message=message,
            compliance_type="broker_compliance",
            version="1.0"
        )
        
        self.wait_window(dialog)
        return dialog.result

    def show_risk_disclosure(self):
        """Show mandatory risk disclosure dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Risk Disclosure Agreement")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Create main container
        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header,
            text="Risk Disclosure Statement",
            font=TITLE_FONT,
            text_color=WARNING_ORANGE
        ).pack(side="left")
        
        # Add scrollable content
        scroll_frame = ctk.CTkScrollableFrame(container)
        scroll_frame.pack(fill="both", expand=True)
        
        # Risk disclosure content
        risk_content = f"""
        IMPORTANT RISK DISCLOSURE - {APP_NAME} {VERSION}
        
        Trading securities involves substantial risk of loss and is not suitable for all investors. 
        Before using this software, please carefully consider the following risks:
        
        1. MARKET RISK
        The value of investments may fluctuate due to market conditions, economic changes, 
        or other factors. You may lose more than your original investment.
        
        2. LIQUIDITY RISK
        Some securities may become illiquid, making it difficult to execute trades 
        or obtain accurate pricing.
        
        3. SYSTEM RISK
        Technical failures, connectivity issues, or software errors may prevent order 
        execution or cause delays.
        
        4. BROKER RISK
        All trades are executed by your broker. {COMPANY} is not responsible for 
        execution quality, failed trades, or broker insolvency.
        
        5. MODEL RISK
        Execution estimates are based on mathematical models and historical data. 
        Actual results may vary significantly.
        
        6. LEVERAGE RISK
        Margin trading amplifies both gains and losses, potentially resulting in losses 
        exceeding deposited funds.
        
        ACKNOWLEDGMENT:
        By using this software, you confirm that:
        - You understand these risks
        - You have sufficient trading experience and knowledge
        - You accept full responsibility for all trading decisions
        - You have read and agree to our full Terms of Service
        """
        
        ctk.CTkLabel(
            scroll_frame,
            text=risk_content,
            font=BODY_FONT,
            wraplength=700,
            justify="left"
        ).pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add acceptance checkbox
        accept_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            container,
            text="I acknowledge and accept these risks",
            variable=accept_var,
            font=BODY_FONT
        ).pack(pady=(15, 0))
        
        # Add buttons
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(15, 0))
        
        def on_accept():
            if accept_var.get():
                dialog.destroy()
            else:
                ErrorDialog(self, "Required", "You must accept the risk disclosure to continue")
        
        ctk.CTkButton(
            button_frame,
            text="Accept",
            command=on_accept,
            fg_color=SECURE_GREEN,
            hover_color="#27AE60"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Decline",
            command=dialog.destroy,
            fg_color=ERROR_RED,
            hover_color="#D63031"
        ).pack(side="right", padx=5)
        
        # Center dialog
        self._center_window(dialog)

    def show_order_management(self):
        """Display the order management interface"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Create header
        self._create_header("Order Management")

        # Create order form frame
        order_frame = self._create_frame(
            parent=self.content_area,
            row=1,
            border_width=1,
            fg_color=DARK_BG,
            corner_radius=5
        )
        order_frame.grid_columnconfigure(1, weight=1)

        # Get settings
        settings = self.db.get_settings()
        
        # Define form fields configuration
        form_fields = [
            ("Account", "account_var", "dropdown", None, True),
            ("Ticker", "ticker_entry", "entry", None, True),
            ("Order Type", "order_type_var", "radio", ["Dollar Amount", "Share Quantity"], True),
            ("Amount/Shares", "amount_entry", "entry", None, True),
            ("Target Price ($)", "target_price_entry", "entry", None, False),
            ("Aggressiveness", "aggressiveness_var", "radio", ["Low", "Medium", "High"], True),
            ("Target Price Threshold (%)", "target_price_threshold_var", "slider", 0.1, 5.0, 0.1, settings.get('target_price_threshold', 1.0))
        ]

        # Create form fields
        for i, (label, attr, field_type, *args) in enumerate(form_fields):
            self._create_form_field(
                parent=order_frame,
                row=i,
                label=label,
                attr=attr,
                field_type=field_type,
                required=args[-1],
                args=args[:-1]
            )

        # Create action buttons
        self._create_action_buttons(
            parent=order_frame,
            row=len(form_fields)+1,
            buttons=[
                ("Preview Order", self.preview_order, PRIMARY_COLOR, ACTIVE_COLOR),
                ("Submit Order", self.confirm_order, ACCENT_COLOR, "#FF5B35")
            ]
        )

        # Create preview frame (hidden initially)
        self.preview_frame = self._create_frame(
            parent=self.content_area,
            row=2,
            border_width=1,
            fg_color=DARK_BG,
            corner_radius=5
        )
        self.preview_frame.grid_remove()

    def preview_order(self):
        """Preview the order with execution estimates"""
        # Validate account selection
        accounts = self.db.get_accounts()
        if not accounts:
            ErrorDialog(self, "Error", "No accounts available")
            return

        selected_account = self.account_var.get()
        if not selected_account or selected_account == "No accounts available":
            ErrorDialog(self, "Error", "Please select an account")
            return

        # Get form values
        account_idx = [f"{acc['broker']} ({acc['account_id']})" for acc in accounts].index(selected_account)
        account = accounts[account_idx]
        ticker = self.ticker_entry.get().upper()
        order_type = self.order_type_var.get()
        amount_or_shares = self.amount_entry.get()
        target_price = self.target_price_entry.get()
        aggressiveness = self.aggressiveness_var.get().lower()
        target_price_threshold = self.target_price_threshold_var.get()

        # Validate required fields
        if not all([ticker, amount_or_shares]):
            ErrorDialog(self, "Error", "Ticker and amount/shares are required")
            return

        # Parse numeric values
        try:
            if order_type == "amount":
                amount = float(amount_or_shares)
                shares = None
            else:
                shares = float(amount_or_shares)
                amount = None

            target_price = float(target_price) if target_price else None
        except ValueError:
            ErrorDialog(self, "Error", "Invalid numeric values")
            return

        # Show loading dialog
        loading = LoadingDialog(self, "Calculating Execution", "Estimating market impact...")
        
        def calculate_execution():
            """Calculate order execution estimates in a background thread"""
            try:
                broker = self.broker_manager.get_active_broker()
                if not broker:
                    self.after(0, lambda: ErrorDialog(self, "Error", "No active broker connection"))
                    return

                # Get market data
                market_data = broker.get_market_data(ticker)
                current_price = market_data['last_price']
                
                # Calculate estimated shares/amount
                estimated_shares = amount / current_price if amount else shares
                estimated_amount = shares * current_price if shares else amount
                
                # Calculate size ratio for market impact
                avg_daily_volume = market_data.get('avg_daily_volume', 1000000)
                size_ratio = estimated_shares / avg_daily_volume
                
                # Simplified symbol classification (would use actual classification)
                symbol_type = "large_cap"  
                
                # Get slippage model parameters
                slippage_params = DEFAULT_SLIPPAGE_MODEL.get(symbol_type, DEFAULT_SLIPPAGE_MODEL['large_cap'])
                
                # Calculate base slippage
                base_slippage = slippage_params['base']
                size_adjusted_slippage = estimated_shares * slippage_params['size_factor']
                
                # Convert aggressiveness to numeric value
                agg_map = {'low': 3, 'medium': 5, 'high': 8}
                agg_value = agg_map.get(aggressiveness, 5)
                
                urgency_factor = (1 + (10 - agg_value)/10)
                total_slippage = (base_slippage + size_adjusted_slippage) * urgency_factor
                
                # Market impact calculation
                impact_params = MARKET_IMPACT_MODEL['normal']
                market_impact = (
                    impact_params['liquidity_factor'] * 
                    (size_ratio ** impact_params['size_exponent']) * 
                    urgency_factor)
                
                # Estimate execution time
                execution_time = max(1, min(60, (30 * size_ratio) / (agg_value / 5)))
                
                # Estimate fill rate (0-1)
                fill_rate = min(1.0, 0.95 * (agg_value / 10) * (1 - size_ratio))
                
                # Calculate estimated price with slippage and market impact
                if target_price is not None:
                    estimated_price = target_price
                    price_range = (
                        target_price * (1 - (total_slippage + market_impact)),
                        target_price * (1 + (total_slippage + market_impact))
                    )
                else:
                    if order_type == "buy":
                        estimated_price = current_price * (1 + total_slippage + market_impact)
                        price_range = (
                            current_price * (1 + total_slippage),
                            current_price * (1 + total_slippage + 2 * market_impact))
                        
                    else:
                        estimated_price = current_price * (1 - total_slippage - market_impact)
                        price_range = (
                            current_price * (1 - total_slippage - 2 * market_impact),
                            current_price * (1 - total_slippage))
                        
                
                estimated_additional_cost = (total_slippage + market_impact) * estimated_amount

                # Store preview data
                self.order_preview_data = {
                    "account": account,
                    "ticker": ticker,
                    "amount": amount,
                    "shares": shares,
                    "target_price": target_price,
                    "aggressiveness": aggressiveness,
                    "target_price_threshold": target_price_threshold,
                    "estimated_market_impact": market_impact * 100,
                    "estimated_slippage": total_slippage * 100,
                    "estimated_time": execution_time,
                    "estimated_additional_cost": estimated_additional_cost,
                    "current_price": current_price,
                    "estimated_fill_rate": fill_rate,
                    "estimated_price": estimated_price,
                    "price_range": price_range,
                    "size_ratio": size_ratio,
                    "avg_daily_volume": avg_daily_volume
                }

                self.after(0, lambda: self._display_preview(loading))
                
            except Exception as e:
                loading.destroy()
                self.after(0, lambda: ErrorDialog(self, "Error", f"Failed to preview order:\n{str(e)}"))
        
        # Start calculation in background thread
        threading.Thread(target=calculate_execution, daemon=True).start()

    def _display_preview(self, loading_dialog):
        """Display the order preview with calculated execution estimates"""
        loading_dialog.destroy()
        self.preview_frame.grid()
        
        # Clear previous preview content
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Create preview header
        self._create_header("Order Preview", parent=self.preview_frame)

        # Create preview container
        preview_container = self._create_frame(parent=self.preview_frame, fg_color="transparent")
        preview_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        preview = self.order_preview_data
        aggressiveness_map = {
            1: "Low",
            2: "Medium",
            3: "High"
        }
        
        preview_content = [
            ("Broker", "Interactive Brokers"),
            ("Account", f"{preview['account']['account_id']}"),
            ("Ticker", preview['ticker']),
            ("Amount" if preview['amount'] is not None else "Shares",
             f"${preview['amount']:,.2f}" if preview['amount'] else f"{preview['shares']:,.2f} shares"),
            ("Estimated Shares" if preview['amount'] is not None else "Estimated Amount",
             f"{preview['amount'] / preview['current_price']:,.2f} shares" if preview['amount'] else f"${preview['shares'] * preview['current_price']:,.2f}"),
            ("Current Price", f"${preview['current_price']:,.2f}"),
            ("Target Price", f"${preview['target_price']:,.2f}" if preview['target_price'] else "Market Order"),
            ("Aggressiveness", aggressiveness_map.get(preview['aggressiveness'], "Medium")),
            ("Size Ratio", f"{preview['size_ratio']:.4f} of daily volume"),
            ("Estimated Execution Price", f"${preview['estimated_price']:,.2f}"),
            ("Price Range", f"${preview['price_range'][0]:,.2f} - ${preview['price_range'][1]:,.2f}"),
            ("Estimated Market Impact", f"{preview['estimated_market_impact']:.2f}%"),
            ("Estimated Slippage", f"{preview['estimated_slippage']:.2f}%"),
            ("Estimated Additional Cost", f"${preview['estimated_additional_cost']:,.2f}"),
            ("Estimated Execution Time", f"{preview['estimated_time']:.1f} seconds"),
            ("Estimated Fill Rate", f"{preview['estimated_fill_rate']:.1%}")
        ]

        # Create preview items
        for label, value in preview_content:
            self._create_preview_item(
                parent=preview_container,
                label=label,
                value=value
            )

        # Add disclaimer
        self._create_disclaimer(
            parent=self.preview_frame,
            text="Execution estimates are based on proprietary models and historical market data. Actual execution may vary."
        )

    def confirm_order(self):
        """Confirm and submit the order"""
        if not self.order_preview_data:
            ErrorDialog(self, "Error", "Please preview the order first")
            return

        # Show confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Order",
            "Are you sure you want to submit this order?",
            parent=self
        )
        
        if not confirm:
            return

        loading = LoadingDialog(self, "Submitting Order", "Executing trade...")
        
        def submit_order():
            try:
                preview = self.order_preview_data
                
                order_details = {
                    'symbol': preview['ticker'],
                    'quantity': preview['shares'] if preview['shares'] else preview['amount'] / preview['current_price'],
                    'side': 'buy',  # Would be determined by UI
                    'aggressiveness': preview['aggressiveness'],
                    'account_id': preview['account']['account_id']
                }
                
                if preview['target_price']:
                    order_details['limit_price'] = preview['target_price']
                
                result = self.broker_manager.execute_order(order_details)
                
                if result.get('status') == 'filled':
                    self.after(0, lambda: messagebox.showinfo(
                        "Order Executed",
                        f"Order filled at {result['avg_fill_price']:.2f}",
                        parent=self
                    ))
                else:
                    self.after(0, lambda: messagebox.showinfo(
                        "Order Placed",
                        f"Order {result['status']} with ID: {result['order_id']}",
                        parent=self
                    ))
                
                loading.destroy()
                
            except Exception as e:
                loading.destroy()
                self.after(0, lambda: ErrorDialog(self, "Error", f"Order submission failed:\n{str(e)}"))
        
        threading.Thread(target=submit_order, daemon=True).start()

    def show_order_history(self):
        """Display the order history interface"""
        self.clear_content_area()
        
        # Create header
        self._create_header("Order History")
        
        # Create history frame
        history_frame = self._create_frame(
            parent=self.content_area,
            row=1,
            border_width=1,
            fg_color=DARK_BG,
            corner_radius=5
        )
        
        # Add filter controls
        filter_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filter:",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).pack(side="left", padx=(0, 10))
        
        self.history_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All", "Filled", "Pending", "Cancelled"],
            font=BODY_FONT,
            width=150
        )
        self.history_filter.pack(side="left", padx=(0, 10))
        self.history_filter.set("All")
        
        ctk.CTkButton(
            filter_frame,
            text="Refresh",
            command=self._refresh_history,
            width=100,
            height=30,
            font=BODY_FONT,
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR
        ).pack(side="left")
        
        # Create history table
        columns = ["ID", "Symbol", "Side", "Quantity", "Price", "Status", "Time"]
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100, anchor="center")
        
        self.history_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load initial data
        self._refresh_history()

    def _refresh_history(self):
        """Refresh the order history data"""
        loading = LoadingDialog(self, "Loading History", "Fetching order history...")
        
        def load_history():
            try:
                orders = self.db.get_orders()
                filter_value = self.history_filter.get()
                
                filtered_orders = [
                    order for order in orders 
                    if filter_value == "All" or order['status'].lower() == filter_value.lower()
                ]
                
                self.history_tree.delete(*self.history_tree.get_children())
                
                for order in filtered_orders:
                    self.history_tree.insert("", "end", values=(
                        order['order_id'][:8],
                        order['symbol'],
                        order['side'],
                        f"{order['quantity']:.2f}",
                        f"${order['avg_price']:.2f}" if order['avg_price'] else "-",
                        order['status'].capitalize(),
                        order['timestamp'][:19]
                    ))
                
                loading.destroy()
                
            except Exception as e:
                loading.destroy()
                ErrorDialog(self, "Error", f"Failed to load order history:\n{str(e)}")
        
        threading.Thread(target=load_history, daemon=True).start()

    def show_link_account(self):
        """Display the account linking interface"""
        self.clear_content_area()
        
        # Create header
        self._create_header("Link Broker Account")
        
        # Create link frame
        link_frame = self._create_frame(
            parent=self.content_area,
            row=1,
            border_width=1,
            fg_color=DARK_BG,
            corner_radius=5
        )
        link_frame.grid_columnconfigure(1, weight=1)
        
        # Broker selection
        ctk.CTkLabel(
            link_frame,
            text="Broker:",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.broker_var = ctk.StringVar(value="Interactive Brokers")
        broker_dropdown = ctk.CTkComboBox(
            link_frame,
            variable=self.broker_var,
            values=["Interactive Brokers"],
            font=BODY_FONT,
            width=200,
            state="readonly"
        )
        broker_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # API Key
        ctk.CTkLabel(
            link_frame,
            text="API Key:",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.api_key_entry = ctk.CTkEntry(
            link_frame,
            font=BODY_FONT,
            width=300,
            fg_color=INPUT_BG,
            border_color=BORDER_COLOR
        )
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # API Secret
        ctk.CTkLabel(
            link_frame,
            text="API Secret:",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.api_secret_entry = ctk.CTkEntry(
            link_frame,
            font=BODY_FONT,
            width=300,
            show="*",
            fg_color=INPUT_BG,
            border_color=BORDER_COLOR
        )
        self.api_secret_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Account Nickname
        ctk.CTkLabel(
            link_frame,
            text="Nickname:",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.account_nickname_entry = ctk.CTkEntry(
            link_frame,
            font=BODY_FONT,
            width=200,
            fg_color=INPUT_BG,
            border_color=BORDER_COLOR
        )
        self.account_nickname_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Paper Trading
        self.paper_trading_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            link_frame,
            text="Paper Trading",
            variable=self.paper_trading_var,
            font=BODY_FONT
        ).grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Link button
        ctk.CTkButton(
            link_frame,
            text="Link Account",
            command=self._link_broker_account,
            width=200,
            height=40,
            font=BUTTON_FONT,
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR
        ).grid(row=5, column=0, columnspan=2, pady=20)

    def _link_broker_account(self):
        """Link a new broker account"""
        broker = self.broker_var.get()
        api_key = self.api_key_entry.get()
        api_secret = self.api_secret_entry.get()
        nickname = self.account_nickname_entry.get()
        paper_trading = self.paper_trading_var.get()
        
        if not all([broker, api_key, api_secret]):
            ErrorDialog(self, "Error", "Please fill in all required fields")
            return
        
        # Show compliance dialog
        if not self.show_broker_compliance_dialog():
            return
        
        loading = LoadingDialog(self, "Linking Account", "Connecting to broker...")
        
        def connect_account():
            try:
                # Create broker instance and test connection
                broker_api = SecureBrokerFactory.create_broker({
                    'api_key': api_key,
                    'api_secret': api_secret
                })
                
                if not broker_api.connect():
                    raise ConnectionError("Failed to connect to broker")
                
                # Get account balance
                balance_info = broker_api.get_account_balance()
                
                # Create account record
                account = Account(
                    broker=broker,
                    account_id=str(uuid.uuid4()),
                    balance=balance_info['balance'],
                    equity=balance_info['equity'],
                    nickname=nickname,
                    api_key=api_key,
                    api_secret=api_secret,
                    paper_trading=paper_trading
                )
                
                self.db.add_account(account)
                self.broker_manager.add_broker(broker, broker_api)
                self.broker_manager.set_active_broker(broker)
                
                loading.destroy()
                messagebox.showinfo(
                    "Success",
                    f"Account linked successfully!\nBalance: ${balance_info['balance']:,.2f}",
                    parent=self
                )
                
                self.show_order_management()
                
            except Exception as e:
                loading.destroy()
                ErrorDialog(self, "Error", f"Failed to link account:\n{str(e)}")
        
        threading.Thread(target=connect_account, daemon=True).start()

    def _create_header(self, title: str, parent=None):
        """Create a section header"""
        if parent is None:
            parent = self.content_area
            
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text=title,
            font=TITLE_FONT,
            text_color=PRIMARY_COLOR
        ).pack(side="left")

    def _create_frame(self, parent, row=None, **kwargs):
        """Create a styled frame"""
        frame = ctk.CTkFrame(parent, **kwargs)
        
        if row is not None:
            frame.grid(row=row, column=0, sticky="nsew", padx=10, pady=(0, 10))
            frame.grid_columnconfigure(0, weight=1)
        else:
            frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        return frame

    def _create_form_field(self, parent, row, label, attr, field_type, required, args):
        """Create a form field with label"""
        # Label
        label_text = f"{label}{' *' if required else ''}"
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).grid(row=row, column=0, padx=10, pady=10, sticky="w")
        
        # Field
        if field_type == "entry":
            entry = ctk.CTkEntry(
                parent,
                font=BODY_FONT,
                width=200,
                fg_color=INPUT_BG,
                border_color=BORDER_COLOR
            )
            entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            setattr(self, attr, entry)
            
        elif field_type == "dropdown":
            accounts = self.db.get_accounts()
            options = [f"{acc['broker']} ({acc['account_id']})" for acc in accounts] if accounts else ["No accounts available"]
            
            dropdown = ctk.CTkComboBox(
                parent,
                values=options,
                font=BODY_FONT,
                width=200,
                state="readonly"
            )
            dropdown.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            setattr(self, attr, dropdown)
            
            if accounts:
                dropdown.set(options[0])
            
        elif field_type == "radio":
            var = ctk.StringVar(value=args[0])
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=1, padx=10, pady=10, sticky="w")
            
            for i, option in enumerate(args):
                radio = ctk.CTkRadioButton(
                    frame,
                    text=option,
                    variable=var,
                    value=option,
                    font=BODY_FONT
                )
                radio.pack(side="left", padx=(0, 10))
                
            setattr(self, attr, var)
            
        elif field_type == "slider":
            min_val, max_val, step, default = args
            var = ctk.DoubleVar(value=default)
            
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            
            slider = ctk.CTkSlider(
                frame,
                variable=var,
                from_=min_val,
                to=max_val,
                number_of_steps=int((max_val - min_val) / step),
                width=150,
                fg_color=PRIMARY_COLOR
            )
            slider.pack(side="left", padx=(0, 10))
            
            value_label = ctk.CTkLabel(
                frame,
                textvariable=var,
                font=BODY_FONT
            )
            value_label.pack(side="left")
            
            setattr(self, attr, var)

    def _create_action_buttons(self, parent, row, buttons):
        """Create action buttons"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        for text, command, fg_color, hover_color in buttons:
            btn = ctk.CTkButton(
                frame,
                text=text,
                command=command,
                width=150,
                height=40,
                font=BUTTON_FONT,
                fg_color=fg_color,
                hover_color=hover_color
            )
            btn.pack(side="left", padx=10)

    def _create_preview_item(self, parent, label, value):
        """Create a preview item row"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=label + ":",
            font=BODY_FONT,
            text_color=LIGHT_TEXT,
            width=200,
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame,
            text=value,
            font=BODY_FONT,
            text_color=TEXT_COLOR,
            anchor="w"
        ).pack(side="left")

    def _create_disclaimer(self, parent, text):
        """Create a disclaimer label"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text=text,
            font=SMALL_FONT,
            text_color=WARNING_ORANGE,
            wraplength=800,
            justify="center"
        ).pack(fill="x", padx=10, pady=5)

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.winfo_children():
            widget.destroy()

    def clear_content_area(self):
        """Clear the content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def _center_window(self, window=None):
        """Center a window on screen"""
        window = window or self
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _on_app_close(self):
        """Handle application close"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?", parent=self):
            try:
                if hasattr(self, 'broker_manager'):
                    for broker in self.broker_manager.brokers.values():
                        if hasattr(broker, 'execution_engine'):
                            broker.execution_engine.stop()
                
                if hasattr(self, 'db'):
                    self.db.close()
                
                self.destroy()
            except Exception as e:
                logging.error(f"Error during shutdown: {e}")
                self.destroy()

# ====================== APPLICATION ENTRY POINT ======================
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler('imco_trading.log', maxBytes=5*1024*1024, backupCount=3)
        ]
    )
    
    # Create and run application
    app = ImcoTradingApp()
    app.mainloop()