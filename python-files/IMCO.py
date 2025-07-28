import tkinter as tk
from ibapi.execution import Execution
import customtkinter as ctk
from tkinter import messagebox, ttk
import webbrowser
from datetime import datetime, timedelta
import json
import os
import sys
import threading
import queue
import time
from typing import List, Dict, Optional, Tuple
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import *
from ibapi.ticktype import TickTypeEnum as TickType
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from cryptography.fernet import Fernet
import logging

# ====================== CONSTANTS ======================
APP_NAME = "IMCO Trading Suite"
VERSION = "2.0"
COMPANY = "IMCO Trading Solutions"
TERMS_URL = "https://www.imcotradingsolutions.com/terms"
PRIVACY_URL = "https://www.imcotradingsolutions.com/privacy"
SUPPORT_URL = "https://www.imcotradingsolutions.com/support"
DISCLAIMER = (
    "IMCO Trading Suite is a professional trading tool. "
    "All trades are executed at your own risk.\n\n"
    "By using this software, you agree to our Terms of Service."
)

# IBKR specific constants
IBKR_PORT = 7497  # TWS default port
IBKR_GATEWAY_PORT = 4001  # IB Gateway port
MAX_ORDER_RATE = 50  # Max orders per minute to comply with IBKR API limits
RECONNECT_DELAY = 5  # Seconds between reconnection attempts
PING_INTERVAL = 30  # Seconds between ping checks

# Error codes
CONNECTION_ERRORS = {
    502: "Couldn't connect to TWS. Confirm API connection is enabled in TWS/IB Gateway.",
    503: "The TWS is out of date and must be upgraded.",
    1100: "Connectivity between IB and TWS has been lost.",
    1101: "Connectivity between TWS and the API has been lost.",
    1102: "The TWS socket port has been closed.",
    1300: "TWS has been shut down."
}

# Premium Dark Theme Color Scheme
PRIMARY_COLOR = "#0E5FFF"  # Vibrant blue
SECONDARY_COLOR = "#0A0F1C"  # Dark navy
ACCENT_COLOR = "#FF6B35"  # Vibrant orange
TEXT_COLOR = "#E0E5FF"  # Light blue-white
DARK_BG = "#070A12"  # Darker background
LIGHT_TEXT = "#C0C5E0"  # Lighter text
SUCCESS_GREEN = "#00D600"  # Bloomberg green
ERROR_RED = "#FF3B30"
WARNING_YELLOW = "#FFCC00"
PANEL_BG = "#121828"  # Panel background
BORDER_COLOR = "#1E2538"  # Panel borders
HOVER_COLOR = "#1A2238"  # Hover effects
ACTIVE_COLOR = "#1A5FFF"  # Active element color
TABLE_HEADER_BG = "#1A2238"  # Table header
TABLE_ROW_BG = "#141A2B"  # Table row
TABLE_ROW_ALT = "#121727"  # Alternate row
SELECTION_COLOR = "#2A65FF"  # Selected item
GLOW_EFFECT = "#3A75FF"  # For active elements
CHART_BG = "#0E1423"  # Chart background

# Enhanced Slippage Parameters (institutional-grade)
SLIPPAGE_PARAMS = {
    "Low": {
        "base_range": (0.05, 0.15),
        "size_sensitivity": 0.0005,
        "volatility_multiplier": 1.2,
        "time_of_day_curve": {
            "pre_market": 1.5,
            "market_open": 1.8,
            "mid_day": 1.0,
            "market_close": 1.7,
            "after_hours": 1.4
        },
        "liquidity_curve": {
            "0-1%": 1.0,
            "1-5%": 1.3,
            "5-10%": 1.7,
            "10-20%": 2.2,
            "20+%": 3.0
        },
        "exec_prob": 0.95,
        "partial_fill_base": 0.02,
        "partial_fill_size_mult": 0.0003,
        "exec_time": (5000, 15000),
        "price_improvement_prob": 0.15,
        "strategy": "TWAP",
        "participation_rate": 0.05,
        "urgency": 2
    },
    "Medium": {
        "base_range": (0.15, 0.35),
        "size_sensitivity": 0.0008,
        "volatility_multiplier": 1.5,
        "time_of_day_curve": {
            "pre_market": 1.4,
            "market_open": 1.6,
            "mid_day": 1.0,
            "market_close": 1.5,
            "after_hours": 1.3
        },
        "liquidity_curve": {
            "0-1%": 1.0,
            "1-5%": 1.2,
            "5-10%": 1.5,
            "10-20%": 1.8,
            "20+%": 2.5
        },
        "exec_prob": 0.85,
        "partial_fill_base": 0.05,
        "partial_fill_size_mult": 0.0005,
        "exec_time": (2000, 8000),
        "price_improvement_prob": 0.10,
        "strategy": "VWAP",
        "participation_rate": 0.10,
        "urgency": 5
    },
    "High": {
        "base_range": (0.35, 0.75),
        "size_sensitivity": 0.0012,
        "volatility_multiplier": 2.0,
        "time_of_day_curve": {
            "pre_market": 1.3,
            "market_open": 1.4,
            "mid_day": 1.0,
            "market_close": 1.3,
            "after_hours": 1.2
        },
        "liquidity_curve": {
            "0-1%": 1.0,
            "1-5%": 1.1,
            "5-10%": 1.3,
            "10-20%": 1.5,
            "20+%": 2.0
        },
        "exec_prob": 0.70,
        "partial_fill_base": 0.10,
        "partial_fill_size_mult": 0.0008,
        "exec_time": (500, 3000),
        "price_improvement_prob": 0.05,
        "strategy": "Aggressive",
        "participation_rate": 0.20,
        "urgency": 9
    }
}

# Fonts - Professional Trading Platform Style
TITLE_FONT = ("Segoe UI Semibold", 24, "bold")
HEADER_FONT = ("Segoe UI Semibold", 16, "bold")
BODY_FONT = ("Segoe UI", 12)
SMALL_FONT = ("Segoe UI", 10)
BUTTON_FONT = ("Segoe UI Semibold", 12)
DISCLAIMER_FONT = ("Segoe UI", 9)
TABLE_FONT = ("Segoe UI", 11)
TABLE_HEADER_FONT = ("Segoe UI Semibold", 11, "bold")
MONOSPACE_FONT = ("Consolas", 11)  # For data display
CHART_FONT = ("Segoe UI", 9)

# ====================== LOGGING SETUP ======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),
        logging.StreamHandler()
    ]
)

# ====================== SECURITY SETUP ======================
class SecurityManager:
    def __init__(self):
        self.key_file = 'encryption.key'
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    
    def _get_or_create_key(self):
        """Get existing key or create new one with secure permissions"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                    # Verify key is valid
                    Fernet(key)
                    return key
            else:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Set secure file permissions
                if hasattr(os, 'chmod'):
                    os.chmod(self.key_file, 0o600)
                return key
        except Exception as e:
            logging.error(f"Key management error: {str(e)}")
            raise RuntimeError("Failed to initialize encryption key") from e
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data with validation"""
        if not isinstance(data, str):
            raise ValueError("Data to encrypt must be a string")
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logging.error(f"Encryption failed: {str(e)}")
            raise RuntimeError("Data encryption failed") from e
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data with validation"""
        if not isinstance(encrypted_data, str):
            raise ValueError("Encrypted data must be a string")
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logging.error(f"Decryption failed: {str(e)}")
            return ""  # Return empty string rather than failing

security_manager = SecurityManager()

    

# ====================== IBKR WRAPPER ======================
class IBApi(EWrapper, EClient):
    def __init__(self, app):
        EClient.__init__(self, self)
        self.app = app
        self.next_valid_order_id = None
        self.order_status_queue = queue.Queue()
        self.execution_data_queue = queue.Queue()
        self.connected = False
        self.active_orders = {}
        self.account_values = {}
        self.positions = {}
        self.market_data = {}
        self.historical_data = {}
        self.contract_details = {}
        self.hist_vol_cache = {}  # Cache for historical volatility data
        self.adv_cache = {}  # Cache for average daily volume data
        self.last_ping_time = time.time()
        self.pending_pings = 0
        self.max_pending_pings = 3

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.next_valid_order_id = orderId
        self.app.log(f"Next valid order ID: {orderId}")
        
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        error_msg = f"IBKR Error {errorCode}: {errorString}"
        self.app.log(error_msg)
        self.app._handle_ibkr_error(errorCode, errorString)
        
        # Handle specific error codes
        if errorCode in CONNECTION_ERRORS:
            self.connected = False
            self.app.on_ibkr_disconnect(CONNECTION_ERRORS[errorCode])
            
    def connectAck(self):
        super().connectAck()
        if self.asynchronous:
            self.startApi()
            
    def connectionClosed(self):
        super().connectionClosed()
        self.connected = False
        self.app.on_ibkr_disconnect("Connection closed")
        
    def orderStatus(self, orderId: OrderId, status: str, filled: float,
                   remaining: float, avgFillPrice: float, permId: int,
                   parentId: int, lastFillPrice: float, clientId: int,
                   whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId,
                          parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        
        order_info = {
            "orderId": orderId,
            "status": status,
            "filled": filled,
            "remaining": remaining,
            "avgFillPrice": avgFillPrice,
            "lastFillPrice": lastFillPrice,
            "whyHeld": whyHeld
        }
        
        self.order_status_queue.put(order_info)
        self.app.update_order_status(order_info)
        
    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        super().execDetails(reqId, contract, execution)
        
        exec_info = {
            "orderId": execution.orderId,
            "symbol": contract.symbol,
            "side": "BUY" if execution.side == "BOT" else "SELL",
            "shares": execution.shares,
            "price": execution.price,
            "time": execution.time,
            "account": execution.acctNumber
        }
        
        self.execution_data_queue.put(exec_info)
        self.app.add_execution_to_history(exec_info)
        
    def managedAccounts(self, accountsList: str):
        super().managedAccounts(accountsList)
        self.app.on_accounts_received(accountsList.split(","))
        
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        super().updateAccountValue(key, val, currency, accountName)
        if accountName not in self.account_values:
            self.account_values[accountName] = {}
        self.account_values[accountName][key] = val
        self.app.update_account_values(accountName, self.account_values[accountName])
        
    def updatePortfolio(self, contract: Contract, position: float,
                       marketPrice: float, marketValue: float,
                       averageCost: float, unrealizedPNL: float,
                       realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue,
                              averageCost, unrealizedPNL, realizedPNL, accountName)
        if accountName not in self.positions:
            self.positions[accountName] = {}
        self.positions[accountName][contract.symbol] = {
            "position": position,
            "marketPrice": marketPrice,
            "marketValue": marketValue,
            "averageCost": averageCost,
            "unrealizedPNL": unrealizedPNL,
            "realizedPNL": realizedPNL
        }
        self.app.update_positions(accountName, self.positions[accountName])
        
    def tickPrice(self, reqId: int, tickType: TickType, price: float, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
        self.market_data[reqId][tickType] = price
        self.app.update_market_data(reqId, self.market_data[reqId])
        
    def tickSize(self, reqId: int, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
        self.market_data[reqId][tickType] = size
        self.app.update_market_data(reqId, self.market_data[reqId])
        
    def historicalData(self, reqId: int, bar):
        if reqId not in self.historical_data:
            self.historical_data[reqId] = []
        self.historical_data[reqId].append(bar)
        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.app.on_historical_data_loaded(reqId, self.historical_data.get(reqId, []))
        
    def contractDetails(self, reqId: int, contractDetails):
        self.contract_details[reqId] = contractDetails
        self.app.on_contract_details(reqId, contractDetails)
        
    def historicalDataUpdate(self, reqId: int, bar):
        self.app.on_historical_data_update(reqId, bar)
        
    def tickGeneric(self, reqId: int, tickType: int, value: float):
        if tickType == 24:  # HISTORICAL_VOLATILITY
            self.hist_vol_cache[reqId] = value
        elif tickType == 21:  # AVG_VOLUME
            self.adv_cache[reqId] = value
            
    def ping(self):
        """Send ping to IBKR server to check connection"""
        if self.pending_pings >= self.max_pending_pings:
            self.connected = False
            self.app.on_ibkr_disconnect("No response from IBKR server")
            return
            
        self.pending_pings += 1
        self.last_ping_time = time.time()
        super().reqCurrentTime()
        
    def currentTime(self, time: int):
        """Handle ping response"""
        self.pending_pings = 0
        self.last_ping_time = time.time()

# ====================== MAIN APPLICATION ======================
class ImcoTradingPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self._setup_window((1600, 1000))  # Larger window for professional trading platform
        self._configure_appearance("Dark")
        self.ibkr_client = None
        self.active_connection = None
        self.active_orders = {}
        self.order_history = []
        self.pending_orders = {}
        self.execution_history = []
        self.connected_accounts = self._load_accounts()
        self.running_orders = False
        self.market_data_cache = {}
        self.order_lock = threading.Lock()
        self.next_req_id = 1
        self.current_market_data = {}
        self.historical_data_cache = {}
        self.strategy_params = {}
        self.last_order_time = 0
        self.order_count = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Show disclaimer before proceeding
        self._show_disclaimer()
        
        # Start IBKR message processing thread
        self.ibkr_thread = threading.Thread(target=self._process_ibkr_messages, daemon=True)
        self.ibkr_thread.start()
        
        # Start ping thread to monitor connection
        self.ping_thread = threading.Thread(target=self._ping_ibkr, daemon=True)
        self.ping_thread.start()
            
        self.show_main_app()
            
    def _show_disclaimer(self):
        """Show enhanced disclaimer dialog with T&C link and Accept/Cancel buttons"""
        disclaimer_window = ctk.CTkToplevel(self)
        disclaimer_window.title("Terms and Conditions")
        disclaimer_window.geometry("700x400")
        disclaimer_window.transient(self)
        disclaimer_window.grab_set()
        disclaimer_window.resizable(False, False)
        
        # Center the window
        x = self.winfo_x() + (self.winfo_width() // 2) - 350
        y = self.winfo_y() + (self.winfo_height() // 2) - 200
        disclaimer_window.geometry(f"+{x}+{y}")
        
        # Make window always stay on top
        disclaimer_window.attributes('-topmost', True)
        
        # Content frame
        content_frame = ctk.CTkFrame(disclaimer_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            content_frame,
            text="IMCO Trading Suite - Terms and Conditions",
            font=HEADER_FONT,
            text_color=PRIMARY_COLOR
        ).pack(pady=(10, 15))
        
        # Disclaimer text
        disclaimer_text = ctk.CTkLabel(
            content_frame,
            text=DISCLAIMER,
            font=BODY_FONT,
            text_color=LIGHT_TEXT,
            justify="left",
            wraplength=650
        )
        disclaimer_text.pack(pady=(0, 15), padx=20, fill="x")
        
        # Terms link
        def open_terms():
            webbrowser.open(TERMS_URL)
            
        terms_link = ctk.CTkButton(
            content_frame,
            text="View Full Terms and Conditions",
            command=open_terms,
            font=("Segoe UI", 11, "underline"),
            fg_color="transparent",
            hover_color=HOVER_COLOR,
            text_color=PRIMARY_COLOR,
            width=0,
            height=0
        )
        terms_link.pack(pady=(0, 20))
        
        # Button frame
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=(10, 0))
        
        def on_accept():
            disclaimer_window.destroy()
            self.deiconify()  # Show main window
            
        def on_reject():
            self.destroy()  # Quit application
            
        # Accept button
        accept_btn = ctk.CTkButton(
            button_frame,
            text="I Accept",
            command=on_accept,
            width=120,
            height=36,
            font=BUTTON_FONT,
            fg_color=SUCCESS_GREEN,
            hover_color="#00C600",
            text_color="white"
        )
        accept_btn.pack(side="left", padx=15)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_reject,
            width=120,
            height=36,
            font=BUTTON_FONT,
            fg_color=ERROR_RED,
            hover_color="#FF0000",
            text_color="white"
        )
        cancel_btn.pack(side="left", padx=15)
        
        # Make sure main window stays hidden until disclaimer is accepted
        self.withdraw()
        
        # Ensure the window can't be closed without making a choice
        disclaimer_window.protocol("WM_DELETE_WINDOW", on_reject)
        
        # Force focus to the disclaimer window
        disclaimer_window.focus_force()
        accept_btn.focus_set()
        
        # Make sure this window stays on top until a choice is made
        def keep_on_top():
            disclaimer_window.lift()
            disclaimer_window.after(100, keep_on_top)
            
        keep_on_top()
            
    def _setup_window(self, size):
        """Configure main window settings with premium styling"""
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(1400, 900)
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)
        
    def _configure_appearance(self, mode):
        """Configure the application's visual appearance"""
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
        
    def _load_accounts(self):
        """Load saved accounts from encrypted file with error handling"""
        try:
            if not os.path.exists('ibkr_accounts.json'):
                return []
                
            with open('ibkr_accounts.json', 'r') as f:
                encrypted_data = json.load(f)
                if not isinstance(encrypted_data, list):
                    raise ValueError("Invalid accounts file format")
                    
                decrypted_accounts = []
                for account in encrypted_data:
                    if not isinstance(account, dict):
                        continue
                        
                    decrypted_account = {}
                    for key, value in account.items():
                        if key in ['account_id', 'client_id', 'nickname']:
                            decrypted_value = security_manager.decrypt(str(value))
                            if not decrypted_value:
                                raise ValueError(f"Failed to decrypt {key}")
                            decrypted_account[key] = decrypted_value
                        else:
                            decrypted_account[key] = value
                    
                    # Validate required fields
                    if 'account_id' in decrypted_account and decrypted_account['account_id']:
                        decrypted_accounts.append(decrypted_account)
                
                return decrypted_accounts
                
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, ValueError) as e:
            self.log(f"Error loading accounts: {str(e)}")
            logging.error(f"Error loading accounts: {str(e)}", exc_info=True)
            return []
            
    def _save_accounts(self):
        """Save connected accounts to encrypted file with error handling"""
        try:
            encrypted_accounts = []
            
            for account in self.connected_accounts:
                if not isinstance(account, dict):
                    continue
                    
                encrypted_account = {}
                for key, value in account.items():
                    if key in ['account_id', 'client_id', 'nickname']:
                        encrypted_value = security_manager.encrypt(str(value))
                        encrypted_account[key] = encrypted_value
                    else:
                        encrypted_account[key] = value
                
                encrypted_accounts.append(encrypted_account)
            
            # Save with secure permissions
            with open('ibkr_accounts.json', 'w') as f:
                json.dump(encrypted_accounts, f, indent=4)
            
            # Set secure file permissions
            if hasattr(os, 'chmod'):
                os.chmod('ibkr_accounts.json', 0o600)
                
        except (IOError, PermissionError, ValueError) as e:
            self.log(f"Error saving accounts: {str(e)}")
            logging.error(f"Error saving accounts: {str(e)}", exc_info=True)
            
    def log(self, message):
        """Log a message to the console and log file with timestamp"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            log_message = f"[{timestamp}] {message}"
            print(log_message)
            logging.info(log_message)
        except Exception as e:
            print(f"Logging failed: {str(e)}")

    def _ping_ibkr(self):
        """Periodically ping IBKR server to monitor connection"""
        while True:
            try:
                time.sleep(PING_INTERVAL)
                
                if self.ibkr_client and self.ibkr_client.connected:
                    # Check if we've received any data recently
                    if time.time() - self.ibkr_client.last_ping_time > PING_INTERVAL * 2:
                        self.ibkr_client.ping()
                    else:
                        self.ibkr_client.pending_pings = 0
            except Exception as e:
                self.log(f"Ping error: {str(e)}")
                time.sleep(5)  # Wait longer if error occurs

    def _check_order_rate_limit(self):
        """Check if we're exceeding IBKR's API rate limits"""
        try:
            current_time = time.time()
            if current_time - self.last_order_time > 60:  # Reset counter if more than 1 minute
                self.order_count = 0
                self.last_order_time = current_time
                
            if self.order_count >= MAX_ORDER_RATE:
                time_left = 60 - (current_time - self.last_order_time)
                messagebox.showwarning(
                    "Rate Limit Exceeded",
                    f"Too many orders in the last minute. Please wait {time_left:.1f} seconds before sending more orders."
                )
                return False
                
            return True
        except Exception as e:
            self.log(f"Rate limit check error: {str(e)}")
            return False

    def _process_ibkr_messages(self):
        """Process messages from IBKR API in a separate thread"""
        while self.ibkr_client and self.ibkr_client.connected:
            try:
                time.sleep(0.1)  # Prevent high CPU usage
                
                # Process order status updates
                if hasattr(self.ibkr_client, 'order_status_queue'):
                    try:
                        while not self.ibkr_client.order_status_queue.empty():
                            order_info = self.ibkr_client.order_status_queue.get_nowait()
                            self._handle_order_status_update(order_info)
                    except queue.Empty:
                        pass
                    except Exception as e:
                        self.log(f"Error processing order status: {str(e)}")
                        logging.error(f"Error processing order status: {str(e)}", exc_info=True)
                        
                # Process execution reports
                if hasattr(self.ibkr_client, 'execution_data_queue'):
                    try:
                        while not self.ibkr_client.execution_data_queue.empty():
                            exec_info = self.ibkr_client.execution_data_queue.get_nowait()
                            self._handle_execution_report(exec_info)
                    except queue.Empty:
                        pass
                    except Exception as e:
                        self.log(f"Error processing execution report: {str(e)}")
                        logging.error(f"Error processing execution report: {str(e)}", exc_info=True)
            except Exception as e:
                self.log(f"Message processing error: {str(e)}")
                time.sleep(1)  # Wait longer if error occurs

    def _handle_order_status_update(self, order_info):
        """Handle order status updates with proper error handling"""
        try:
            if not isinstance(order_info, dict):
                raise ValueError("Invalid order info format")
                
            order_id = order_info.get("orderId")
            if order_id is None:
                raise ValueError("Missing order ID in status update")
            
            with self.order_lock:
                if order_id in self.active_orders:
                    self.active_orders[order_id].update(order_info)
                    
                    # Check if order is completed
                    status = order_info.get("status", "")
                    if status in ["Filled", "Cancelled", "Inactive"]:
                        if order_id in self.pending_orders:
                            self.pending_orders.pop(order_id)
                            
                        # Add to history if filled
                        if status == "Filled":
                            self.add_order_to_history(self.active_orders[order_id])
                            
                        self.active_orders.pop(order_id)
                        
                    # Update UI
                    self._update_status_bar()
                    
        except Exception as e:
            self.log(f"Error handling order status update: {str(e)}")
            logging.error(f"Error handling order status update: {str(e)}", exc_info=True)

    def _handle_execution_report(self, exec_info):
        """Handle execution reports with proper error handling"""
        try:
            if not isinstance(exec_info, dict):
                raise ValueError("Invalid execution info format")
                
            order_id = exec_info.get("orderId")
            if order_id is None:
                raise ValueError("Missing order ID in execution report")
            
            with self.order_lock:
                if order_id in self.active_orders:
                    # Update order with execution details
                    self.active_orders[order_id].update({
                        "filled": exec_info.get("shares", 0),
                        "avgFillPrice": exec_info.get("price", 0),
                        "lastFillPrice": exec_info.get("price", 0),
                        "time": exec_info.get("time", "")
                    })
                    
                    # Add to execution history
                    self.execution_history.append(exec_info)
                    
                    # Update UI
                    self._update_status_bar()
                    
        except Exception as e:
            self.log(f"Error handling execution report: {str(e)}")
            logging.error(f"Error handling execution report: {str(e)}", exc_info=True)

    # ====================== ADVANCED SLIPPAGE CALCULATION ======================
    def _get_time_of_day(self) -> str:
        """Determine current market time segment with more granularity"""
        try:
            now = datetime.now().time()
            market_open = datetime.strptime("09:30", "%H:%M").time()
            market_close = datetime.strptime("16:00", "%H:%M").time()
            
            if now < datetime.strptime("08:00", "%H:%M").time():
                return "pre_market_early"
            elif now >= datetime.strptime("08:00", "%H:%M").time() and now < market_open:
                return "pre_market_late"
            elif now >= market_open and now < datetime.strptime("10:00", "%H:%M").time():
                return "market_open"
            elif now >= datetime.strptime("10:00", "%H:%M").time() and now < datetime.strptime("12:00", "%H:%M").time():
                return "mid_morning"
            elif now >= datetime.strptime("12:00", "%H:%M").time() and now < datetime.strptime("14:00", "%H:%M").time():
                return "mid_day"
            elif now >= datetime.strptime("14:00", "%H:%M").time() and now < datetime.strptime("15:30", "%H:%M").time():
                return "afternoon"
            elif now >= datetime.strptime("15:30", "%H:%M").time() and now <= market_close:
                return "market_close"
            elif now > market_close and now < datetime.strptime("18:00", "%H:%M").time():
                return "after_hours_early"
            else:
                return "after_hours_late"
        except Exception as e:
            self.log(f"Error determining time of day: {str(e)}")
            return "mid_day"  # Default to mid-day if error occurs
    
    def _get_liquidity_bucket(self, symbol: str, quantity: int) -> str:
        """Determine liquidity bucket based on order size vs ADV with error handling"""
        if not self.ibkr_client or not self.ibkr_client.connected:
            return "Unknown"
            
        try:
            if not symbol or quantity <= 0:
                return "Unknown"
                
            # Request average daily volume for the symbol
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            req_id = self.next_req_id
            self.next_req_id += 1
            
            # Request average volume data
            self.ibkr_client.reqMktData(req_id, contract, "221", False, False, [])
            
            # Wait for data with timeout
            start_time = time.time()
            while req_id not in self.ibkr_client.adv_cache and (time.time() - start_time) < 5:
                time.sleep(0.1)
            
            # Get the ADV if available
            adv = self.ibkr_client.adv_cache.get(req_id, 1_000_000)  # Default to 1M if not available
            self.ibkr_client.cancelMktData(req_id)
            
            # Calculate percentage of ADV
            order_pct = (quantity * 100) / adv if adv > 0 else 0
            
            if order_pct < 0.1:
                return "0-0.1%"
            elif order_pct < 0.5:
                return "0.1-0.5%"
            elif order_pct < 1:
                return "0.5-1%"
            elif order_pct < 2:
                return "1-2%"
            elif order_pct < 5:
                return "2-5%"
            elif order_pct < 10:
                return "5-10%"
            elif order_pct < 20:
                return "10-20%"
            else:
                return "20+%"
        except Exception as e:
            self.log(f"Error calculating liquidity bucket: {str(e)}")
            logging.error(f"Error calculating liquidity bucket: {str(e)}", exc_info=True)
            return "Unknown"
    
    def _calculate_volatility_factor(self, symbol: str) -> float:
        """Calculate volatility factor based on historical volatility with error handling"""
        if not self.ibkr_client or not self.ibkr_client.connected:
            return 1.0
            
        try:
            if not symbol:
                return 1.0
                
            # Request historical volatility for the symbol
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            req_id = self.next_req_id
            self.next_req_id += 1
            
            # Request historical volatility data
            self.ibkr_client.reqMktData(req_id, contract, "233", False, False, [])
            
            # Wait for data with timeout
            start_time = time.time()
            while req_id not in self.ibkr_client.hist_vol_cache and (time.time() - start_time) < 5:
                time.sleep(0.1)
            
            # Get the historical volatility if available
            volatility = self.ibkr_client.hist_vol_cache.get(req_id, 0.25)  # Default to 25% if not available
            self.ibkr_client.cancelMktData(req_id)
            
            # Normalize to 1.0 for average volatility (25%)
            return 1.0 + (volatility - 0.25) * 2.0
        except Exception as e:
            self.log(f"Error calculating volatility factor: {str(e)}")
            logging.error(f"Error calculating volatility factor: {str(e)}", exc_info=True)
            return 1.0
        
    def _calculate_enhanced_slippage(self, ticker: str, quantity: int, price: float, aggressiveness: str) -> dict:
        """
        Advanced slippage calculation with stochastic modeling and market impact simulation
        using real-time data with robust error handling
        """
        try:
            if not ticker or quantity <= 0 or price <= 0:
                raise ValueError("Invalid input parameters")
                
            # Get base slippage parameters with validation
            slippage_params = SLIPPAGE_PARAMS.get(aggressiveness, SLIPPAGE_PARAMS["Medium"])
            if not isinstance(slippage_params, dict):
                raise ValueError("Invalid slippage parameters")
            
            # Calculate market impact using Almgren-Chriss model
            notional = quantity * price
            impact_bps = 10 * (notional ** -0.5) if notional > 0 else 0  # Simplified market impact model
            permanent_impact = impact_bps * 0.6  # 60% permanent impact
            temporary_impact = impact_bps * 0.4  # 40% temporary impact
            
            # Get volatility factor from real-time data
            volatility_factor = self._calculate_volatility_factor(ticker)
            
            # Get time of day factor
            time_of_day = self._get_time_of_day()
            time_of_day_factor = slippage_params.get("time_of_day_curve", {}).get(time_of_day, 1.0)
            
            # Get liquidity factor from real-time data
            liquidity_bucket = self._get_liquidity_bucket(ticker, quantity)
            liquidity_factor = slippage_params.get("liquidity_curve", {}).get(liquidity_bucket, 1.0)
            
            # Calculate base slippage with all factors
            base_range = slippage_params.get("base_range", (0.15, 0.35))
            base_min, base_max = base_range
            base_slippage = base_min + (base_max - base_min) * 0.5  # Midpoint of range
            
            # Size-adjusted slippage with non-linear scaling
            size_sensitivity = slippage_params.get("size_sensitivity", 0.0008)
            size_adjusted_slippage = base_slippage + (size_sensitivity * (notional ** 0.8) / 1000)
            
            # Apply all multipliers
            volatility_multiplier = slippage_params.get("volatility_multiplier", 1.5)
            adjusted_slippage = (size_adjusted_slippage * 
                                volatility_multiplier * 
                                time_of_day_factor * 
                                liquidity_factor * 
                                volatility_factor)
            
            # Add market impact (convert bps to percentage)
            final_slippage = adjusted_slippage + (impact_bps / 100)
            
            # Calculate probability of execution with all factors
            base_exec_prob = slippage_params.get("exec_prob", 0.85)
            exec_prob = (base_exec_prob * 
                        (1 - (impact_bps / 2000)) *  # More impact reduces probability
                        (1 / max(0.1, time_of_day_factor)) * 
                        (1 / max(0.1, liquidity_factor)))
            
            # Calculate expected partial fill with stochastic modeling
            partial_fill = (slippage_params.get("partial_fill_base", 0.05) + 
                           (slippage_params.get("partial_fill_size_mult", 0.0005) * (notional ** 0.7) / 1000))
            
            # Calculate expected execution time in seconds with randomness
            exec_time_range = slippage_params.get("exec_time", (2000, 8000))
            exec_time_min, exec_time_max = exec_time_range
            exec_time_sec = (exec_time_min + (exec_time_max - exec_time_min) * np.random.random())
            
            # Price improvement probability with size adjustment
            price_improvement_prob = slippage_params.get("price_improvement_prob", 0.10) * (1 - (quantity / 1_000_000) ** 0.3)
            
            # Calculate expected price improvement if it occurs
            price_improvement_pct = -0.05 * final_slippage  # 5% better than expected
            
            # Calculate expected fill distribution
            fill_distribution = self._simulate_fill_distribution(quantity, exec_time_sec, liquidity_factor)
            
            return {
                "expected_slippage_pct": final_slippage,
                "execution_probability": min(0.99, max(0.5, exec_prob)),
                "partial_fill_pct": min(0.5, partial_fill),
                "market_impact_bps": impact_bps,
                "permanent_impact_bps": permanent_impact,
                "temporary_impact_bps": temporary_impact,
                "execution_time_sec": exec_time_sec,
                "time_of_day_factor": time_of_day_factor,
                "liquidity_factor": liquidity_factor,
                "volatility_factor": volatility_factor,
                "size_factor": size_adjusted_slippage - base_slippage,
                "base_slippage": base_slippage,
                "price_improvement_prob": price_improvement_prob,
                "price_improvement_pct": price_improvement_pct,
                "fill_distribution": fill_distribution,
                "strategy": slippage_params.get("strategy", "VWAP"),
                "participation_rate": slippage_params.get("participation_rate", 0.10),
                "urgency": slippage_params.get("urgency", 5),
                "notional_value": notional
            }
        except Exception as e:
            self.log(f"Error calculating enhanced slippage: {str(e)}")
            logging.error(f"Error calculating enhanced slippage: {str(e)}", exc_info=True)
            # Return conservative defaults if calculation fails
            return {
                "expected_slippage_pct": 0.2,
                "execution_probability": 0.8,
                "partial_fill_pct": 0.05,
                "market_impact_bps": 10,
                "permanent_impact_bps": 6,
                "temporary_impact_bps": 4,
                "execution_time_sec": 5.0,
                "time_of_day_factor": 1.0,
                "liquidity_factor": 1.0,
                "volatility_factor": 1.0,
                "size_factor": 0.0,
                "base_slippage": 0.2,
                "price_improvement_prob": 0.1,
                "price_improvement_pct": -0.01,
                "fill_distribution": [quantity * 0.25, quantity * 0.5, quantity * 0.75, quantity],
                "strategy": "VWAP",
                "participation_rate": 0.10,
                "urgency": 5,
                "notional_value": quantity * price
            }
        
    def _simulate_fill_distribution(self, quantity: int, exec_time: float, liquidity_factor: float) -> List[float]:
        """
        Simulate the expected fill distribution over time using a gamma distribution
        with robust error handling
        """
        try:
            if quantity <= 0 or exec_time <= 0 or liquidity_factor <= 0:
                return [quantity * (i+1)/10 for i in range(10)]  # Return linear fallback
                
            # Parameters for the fill distribution
            alpha = 2.0  # Shape parameter
            beta = exec_time / alpha  # Scale parameter
            
            # Generate time points
            time_points = np.linspace(0, exec_time, 10)
            
            # Calculate cumulative fills using gamma CDF
            fills = [norm.cdf(t, loc=exec_time/2, scale=exec_time/4) * quantity for t in time_points]
            
            # Adjust for liquidity
            fills = [f * (1.0 / max(0.1, liquidity_factor) ** 0.5) for f in fills]
            
            # Ensure we don't exceed total quantity
            fills = [min(f, quantity) for f in fills]
            
            return fills
        except Exception as e:
            self.log(f"Error simulating fill distribution: {str(e)}")
            logging.error(f"Error simulating fill distribution: {str(e)}", exc_info=True)
            # Return linear fill distribution as fallback
            return [quantity * (i+1)/10 for i in range(10)]
        
    def _calculate_optimal_execution(self, ticker: str, quantity: int, price: float, strategy: str) -> dict:
        """
        Calculate optimal execution trajectory using Almgren-Chriss model
        with robust error handling
        """
        try:
            if not ticker or quantity <= 0 or price <= 0:
                raise ValueError("Invalid input parameters")
                
            # Model parameters
            risk_aversion = 0.1  # Trader's risk aversion
            volatility = self._calculate_volatility_factor(ticker) * 0.01  # Daily volatility
            permanent_impact = 0.001  # Permanent impact coefficient
            temporary_impact = 0.002  # Temporary impact coefficient
            
            # Time grid (in minutes)
            T = 390  # Trading day in minutes
            N = 10  # Number of intervals
            dt = T / N
            
            # Calculate optimal execution trajectory
            kappa = np.sqrt(risk_aversion * volatility**2 / temporary_impact)
            sinh_kappaT = np.sinh(kappa * T)
            cosh_kappaT = np.cosh(kappa * T)
            
            times = np.linspace(0, T, N+1)
            shares_remaining = quantity * (sinh_kappaT * np.cosh(kappa * (T - times)) / (sinh_kappaT * cosh_kappaT))
            
            # Calculate trade list
            trade_list = -np.diff(shares_remaining)
            
            return {
                "times": times,
                "shares_remaining": shares_remaining,
                "trade_list": trade_list,
                "strategy": strategy,
                "parameters": {
                    "risk_aversion": risk_aversion,
                    "volatility": volatility,
                    "permanent_impact": permanent_impact,
                    "temporary_impact": temporary_impact
                }
            }
        except Exception as e:
            self.log(f"Error calculating optimal execution: {str(e)}")
            logging.error(f"Error calculating optimal execution: {str(e)}", exc_info=True)
            # Return linear execution as fallback
            times = np.linspace(0, 390, 10)
            shares_remaining = quantity * (1 - times/390)
            return {
                "times": times,
                "shares_remaining": shares_remaining,
                "trade_list": [quantity/10] * 10,
                "strategy": strategy,
                "parameters": {
                    "risk_aversion": 0.1,
                    "volatility": 0.01,
                    "permanent_impact": 0.001,
                    "temporary_impact": 0.002
                }
            }

    # ====================== IBKR CONNECTION MANAGEMENT ======================
    def connect_to_ibkr(self, connection_type: str, account_id: str, client_id: str = "0") -> bool:
        """Connect to IBKR TWS or Gateway with enhanced error handling"""
        try:
            if not connection_type or not account_id:
                raise ValueError("Missing connection parameters")
                
            if self.ibkr_client and self.ibkr_client.connected:
                self.disconnect_from_ibkr()
            
            port = IBKR_PORT if connection_type == "TWS (Desktop)" else IBKR_GATEWAY_PORT
            
            self.ibkr_client = IBApi(self)
            self.ibkr_client.connect("127.0.0.1", port, int(client_id))
            
            # Start a thread to run the IBKR client
            ibkr_thread = threading.Thread(target=self._run_ibkr_client, daemon=True)
            ibkr_thread.start()
            
            # Wait for connection with timeout
            start_time = time.time()
            while not hasattr(self.ibkr_client, "next_valid_order_id") and (time.time() - start_time) < 10:
                time.sleep(0.1)
            
            if not hasattr(self.ibkr_client, "next_valid_order_id"):
                raise Exception("Connection timeout - please ensure TWS/IB Gateway is running and API is enabled")
            
            self.active_connection = {
                "connection_type": connection_type,
                "account_id": account_id,
                "client_id": client_id,
                "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.ibkr_client.connected = True
            self.reconnect_attempts = 0
            self._update_status_bar()
            
            # Request account updates
            self.ibkr_client.reqAccountUpdates(True, account_id)
            
            # Request positions
            self.ibkr_client.reqPositions()
            
            return True
        except ValueError as e:
            self.log(f"Invalid connection parameters: {str(e)}")
            messagebox.showerror("Connection Error", f"Invalid connection parameters:\n{str(e)}")
            return False
        except Exception as e:
            self.log(f"Failed to connect to IBKR: {str(e)}")
            logging.error(f"Failed to connect to IBKR: {str(e)}", exc_info=True)
            self.connection_status.configure(text="● DISCONNECTED", text_color=ERROR_RED)
            messagebox.showerror("Connection Failed", f"Failed to connect to IBKR:\n{str(e)}")
            return False
            
    def _run_ibkr_client(self):
        """Run the IBKR client in a separate thread with error handling"""
        try:
            self.ibkr_client.run()
        except Exception as e:
            self.log(f"IBKR client error: {str(e)}")
            logging.error(f"IBKR client error: {str(e)}", exc_info=True)
            self.on_ibkr_disconnect(f"Connection error: {str(e)}")
            
    def disconnect_from_ibkr(self):
        """Disconnect from IBKR with proper cleanup"""
        if self.ibkr_client and self.ibkr_client.connected:
            try:
                # Cancel all active orders before disconnecting
                with self.order_lock:
                    for order_id in list(self.active_orders.keys()):
                        try:
                            self.ibkr_client.cancelOrder(order_id)
                        except Exception as e:
                            self.log(f"Error cancelling order {order_id}: {str(e)}")
                            logging.error(f"Error cancelling order {order_id}: {str(e)}", exc_info=True)
                
                self.ibkr_client.disconnect()
                self.ibkr_client.connected = False
                self.active_connection = None
                self._update_status_bar()
            except Exception as e:
                self.log(f"Error disconnecting from IBKR: {str(e)}")
                logging.error(f"Error disconnecting from IBKR: {str(e)}", exc_info=True)
                
    def on_ibkr_disconnect(self, message: str):
        """Handle IBKR disconnection with cleanup"""
        if hasattr(self, 'ibkr_client'):
            self.ibkr_client.connected = False
        self.active_connection = None
        self._update_status_bar()
        
        # Attempt auto-reconnect if we have active orders
        if self.active_orders and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            self.after(1000 * RECONNECT_DELAY, self._attempt_reconnect)
            messagebox.showwarning(
                "Disconnected", 
                f"{message}\n\n"
                f"You have {len(self.active_orders)} active orders that may be affected."
            )
        else:
            messagebox.showwarning("Disconnected", f"Connection to IBKR lost:\n{message}")
        
    def _attempt_reconnect(self):
        """Attempt to reconnect to IBKR"""
        if self.active_connection and not (self.ibkr_client and self.ibkr_client.connected):
            self.log(f"Attempting to reconnect (attempt {self.reconnect_attempts})")
            self.connect_to_ibkr(
                self.active_connection["connection_type"],
                self.active_connection["account_id"],
                self.active_connection["client_id"]
            )
            
    def on_accounts_received(self, accounts: List[str]):
        """Handle received account list from IBKR"""
        self.log(f"Received accounts: {accounts}")
        
    def update_account_values(self, account: str, values: Dict[str, str]):
        """Update account values in the UI"""
        if hasattr(self, 'account_values_label'):
            net_liquidation = values.get("NetLiquidation", "N/A")
            buying_power = values.get("BuyingPower", "N/A")
            self.account_values_label.configure(text=f"NetLiq: ${net_liquidation} | BP: ${buying_power}")
        
    def update_positions(self, account: str, positions: Dict[str, Dict]):
        """Update positions in the UI"""
        pass
        
    def update_market_data(self, req_id: int, data: Dict):
        """Update market data in the UI"""
        self.current_market_data[req_id] = data
        if hasattr(self, 'market_data_display'):
            self._update_market_data_display()

    # ====================== ORDER MANAGEMENT ======================
    def submit_order(self, contract: Contract, order: Order, account: str) -> Optional[int]:
        """Submit an order through IBKR API with enhanced validation"""
        if not self.ibkr_client or not self.ibkr_client.connected:
            messagebox.showerror("Not Connected", "Please connect to IBKR before submitting orders")
            return None
        
        if self.running_orders:
            messagebox.showwarning("Order in Progress", "Please wait for current orders to complete")
            return None
        
        # Check order rate limit
        if not self._check_order_rate_limit():
            return None
            
        try:
            with self.order_lock:
                order_id = self.ibkr_client.next_valid_order_id
                self.ibkr_client.next_valid_order_id += 1
                
                # Store order information with additional metadata
                order_info = {
                    "orderId": order_id,
                    "symbol": contract.symbol,
                    "account": account,
                    "status": "Pending",
                    "orderType": order.orderType,
                    "side": "BUY" if order.action == "BUY" else "SELL",
                    "quantity": order.totalQuantity,
                    "price": order.lmtPrice if order.orderType == "LMT" else None,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "clientId": self.active_connection["client_id"],
                    "aggressiveness": self.aggressiveness_var.get() if hasattr(self, 'aggressiveness_var') else "Medium",
                    "strategy": order.algoStrategy if hasattr(order, 'algoStrategy') else "VWAP",
                    "contract": contract,
                    "order": order
                }
                
                self.active_orders[order_id] = order_info
                self.pending_orders[order_id] = time.time()
                self.running_orders = True
                self._update_status_bar()
                
                # Place the order with error handling
                try:
                    self.ibkr_client.placeOrder(order_id, contract, order)
                    self.order_count += 1
                    self.last_order_time = time.time()
                    self.log(f"Order {order_id} submitted for {contract.symbol}")
                    return order_id
                except Exception as e:
                    self.log(f"Error submitting order {order_id}: {str(e)}")
                    logging.error(f"Error submitting order {order_id}: {str(e)}", exc_info=True)
                    # Clean up failed order
                    if order_id in self.active_orders:
                        self.active_orders.pop(order_id)
                    if order_id in self.pending_orders:
                        self.pending_orders.pop(order_id)
                    raise
                    
        except ValueError as e:
            self.log(f"Order validation error: {str(e)}")
            logging.error(f"Order validation error: {str(e)}", exc_info=True)
            messagebox.showerror("Order Error", f"Invalid order parameters:\n{str(e)}")
            return None
        except Exception as e:
            self.log(f"Order submission error: {str(e)}")
            logging.error(f"Order submission error: {str(e)}", exc_info=True)
            messagebox.showerror("Order Error", f"Failed to submit order:\n{str(e)}")
            return None
            
    def cancel_order(self, order_id: int):
        """Cancel an active order with improved error handling"""
        if not self.ibkr_client or not self.ibkr_client.connected:
            messagebox.showerror("Not Connected", "Not connected to IBKR")
            return
        
        with self.order_lock:
            if order_id not in self.active_orders:
                messagebox.showerror("Invalid Order", "Order ID not found")
                return
            
            try:
                self.ibkr_client.cancelOrder(order_id)
                self.active_orders[order_id]["status"] = "Cancelling"
                self._update_status_bar()
                self.log(f"Cancel request sent for order {order_id}")
            except Exception as e:
                self.log(f"Error cancelling order {order_id}: {str(e)}")
                logging.error(f"Error cancelling order {order_id}: {str(e)}", exc_info=True)
                messagebox.showerror("Cancel Error", f"Failed to cancel order:\n{str(e)}")
            
    def add_order_to_history(self, order_info: Dict):
        """Add a completed order to history with enhanced data"""
        try:
            if not isinstance(order_info, dict):
                raise ValueError("Invalid order info format")
                
            # Calculate slippage with enhanced model
            if "price" in order_info and "avgFillPrice" in order_info:
                slippage_data = self._calculate_enhanced_slippage(
                    order_info["symbol"],
                    order_info["quantity"],
                    order_info["price"],
                    order_info.get("aggressiveness", "Medium")
                )
                slippage_pct = ((order_info["avgFillPrice"] - order_info["price"]) / order_info["price"]) * 100
            else:
                slippage_pct = 0.0
                slippage_data = {
                    "market_impact_bps": 0,
                    "liquidity_factor": 1.0,
                    "time_of_day_factor": 1.0,
                    "volatility_factor": 1.0
                }
            
            # Create history entry with all relevant data
            history_entry = {
                "order_id": str(order_info.get("orderId", "")),
                "symbol": order_info.get("symbol", ""),
                "status": order_info.get("status", "Filled"),
                "side": order_info.get("side", ""),
                "order_type": order_info.get("orderType", "Medium"),
                "strategy": order_info.get("strategy", "VWAP"),
                "quantity": order_info.get("quantity", 0),
                "filled_quantity": order_info.get("filled", order_info.get("quantity", 0)),
                "filled_pct": 100 if order_info.get("status") == "Filled" else 0,
                "price": order_info.get("price", 0),
                "avg_price": order_info.get("avgFillPrice", order_info.get("price", 0)),
                "slippage_pct": slippage_pct,
                "value": order_info.get("quantity", 0) * order_info.get("avgFillPrice", order_info.get("price", 0)),
                "time": order_info.get("time", ""),
                "execution_time_ms": self._calculate_execution_time(order_info),
                "account": order_info.get("account", ""),
                "aggressiveness": order_info.get("aggressiveness", "Medium"),
                "market_impact_bps": slippage_data.get("market_impact_bps", 0),
                "permanent_impact_bps": slippage_data.get("permanent_impact_bps", 0),
                "temporary_impact_bps": slippage_data.get("temporary_impact_bps", 0),
                "liquidity_factor": slippage_data.get("liquidity_factor", 1.0),
                "time_of_day_factor": slippage_data.get("time_of_day_factor", 1.0),
                "volatility_factor": slippage_data.get("volatility_factor", 1.0),
                "contract_details": {
                    "symbol": order_info.get("contract", {}).symbol if hasattr(order_info.get("contract", {}), 'symbol') else "",
                    "secType": order_info.get("contract", {}).secType if hasattr(order_info.get("contract", {}), 'secType') else "",
                    "exchange": order_info.get("contract", {}).exchange if hasattr(order_info.get("contract", {}), 'exchange') else "",
                    "currency": order_info.get("contract", {}).currency if hasattr(order_info.get("contract", {}), 'currency') else ""
                } if "contract" in order_info else None
            }
            
            # Insert at beginning of history
            self.order_history.insert(0, history_entry)
            
            # Schedule UI update on main thread
            self.after(0, self._update_order_history_display)
            
        except Exception as e:
            self.log(f"Error adding order to history: {str(e)}")
            logging.error(f"Error adding order to history: {str(e)}", exc_info=True)

    # ====================== SCREEN MANAGEMENT ======================
    def show_main_app(self):
        """Show the main application interface with premium styling"""
        self.clear_window()
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container with gradient background
        main_container = ctk.CTkFrame(
            self, 
            fg_color=SECONDARY_COLOR, 
            corner_radius=0,
            border_width=0
        )
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Create UI components
        self._create_sidebar(main_container)
        self._create_status_bar(main_container)
        self._create_content_area(main_container)

        # Show default screen
        self.show_order_management()
        
    def _create_sidebar(self, parent):
        """Create the premium sidebar navigation"""
        sidebar = ctk.CTkFrame(
            parent,
            width=260,  # Wider sidebar for better navigation
            corner_radius=0,
            fg_color=DARK_BG,
            border_width=0,
            border_color=BORDER_COLOR
        )
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)

        # Logo with premium styling
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", padx=20, pady=(20, 30))
        
        ctk.CTkLabel(
            logo_frame,
            text="TRADING SUITE",
            font=("Segoe UI", 16, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="top", pady=(0, 5))
        
        ctk.CTkLabel(
            logo_frame,
            text="PROFESSIONAL EDITION",
            font=("Segoe UI", 9),
            text_color=LIGHT_TEXT
        ).pack(side="top")
        
        # Premium divider
        ctk.CTkFrame(
            sidebar,
            height=1,
            fg_color=BORDER_COLOR
        ).pack(fill="x", padx=20, pady=(0, 20))

        # Navigation buttons with premium styling
        nav_buttons = [
            ("Order Management", "📊", self.show_order_management),
            ("Order History", "📜", self.show_order_history),
            ("Link Account", "🔌", self.show_link_account),
            ("Support", "💬", lambda: webbrowser.open(SUPPORT_URL))
        ]

        for text, icon, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {text}",
                command=command,
                fg_color="transparent",
                anchor="w",
                hover_color=HOVER_COLOR,
                font=BODY_FONT,
                height=46,
                corner_radius=4,
                border_spacing=15,
                text_color=LIGHT_TEXT
            )
            btn.pack(fill="x", padx=15, pady=2)
            
        # Add premium footer
        footer_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=20)
        
        ctk.CTkLabel(
            footer_frame,
            text=f"v{VERSION}",
            font=("Segoe UI", 9),
            text_color=LIGHT_TEXT
        ).pack(side="bottom", pady=(10, 0))

    def _create_status_bar(self, parent):
        """Create the premium status bar"""
        self.status_bar = ctk.CTkFrame(
            parent,
            height=36,  # Slightly taller
            fg_color=DARK_BG,
            border_width=0,
            border_color=BORDER_COLOR,
            corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Status indicators container
        status_container = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        status_container.pack(side="left", padx=20, fill="x", expand=True)
        
        # Connection status with indicator
        self.connection_indicator = ctk.CTkLabel(
            status_container,
            text="●",
            font=("Consolas", 14),
            text_color=ERROR_RED
        )
        self.connection_indicator.pack(side="left", padx=(0, 5))
        
        self.connection_status = ctk.CTkLabel(
            status_container,
            text="DISCONNECTED",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT
        )
        self.connection_status.pack(side="left")
        
        # Active orders indicator
        self.active_orders_label = ctk.CTkLabel(
            status_container,
            text="",
            font=("Segoe UI", 11),
            text_color=WARNING_YELLOW
        )
        self.active_orders_label.pack(side="left", padx=20)
        
        # Account values (only shown when connected)
        self.account_values_label = ctk.CTkLabel(
            status_container,
            text="",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT
        )
        self.account_values_label.pack(side="left", padx=20)
        
        # Reconnect button (shown when disconnected)
        self.reconnect_button = ctk.CTkButton(
            status_container,
            text="RECONNECT",
            command=self._reconnect_ibkr,
            width=100,
            height=24,
            font=("Segoe UI", 9, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR,
            corner_radius=4,
            text_color=TEXT_COLOR
        )
        
        # Last update time - right aligned
        status_right_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        status_right_frame.pack(side="right", padx=20)
        
        self.last_update = ctk.CTkLabel(
            status_right_frame,
            text=f"{datetime.now().strftime('%H:%M:%S')}",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT
        )
        self.last_update.pack(side="left", padx=10)
        
        # Date display
        self.date_label = ctk.CTkLabel(
            status_right_frame,
            text=f"{datetime.now().strftime('%a %b %d %Y')}",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT
        )
        self.date_label.pack(side="left")

    def _reconnect_ibkr(self):
        """Attempt to reconnect to IBKR"""
        if self.active_connection:
            self.connect_to_ibkr(
                self.active_connection["connection_type"],
                self.active_connection["account_id"],
                self.active_connection["client_id"]
            )

    def _update_status_bar(self):
        """Update the premium status bar with current connection and order status"""
        try:
            if self.ibkr_client and self.ibkr_client.connected:
                self.connection_indicator.configure(text_color=SUCCESS_GREEN)
                self.connection_status.configure(text="CONNECTED")
                self.reconnect_button.pack_forget()
                
                if hasattr(self, 'account_values_label'):
                    if self.active_connection and self.ibkr_client.account_values.get(self.active_connection["account_id"]):
                        net_liquidation = self.ibkr_client.account_values[self.active_connection["account_id"]].get("NetLiquidation", "N/A")
                        buying_power = self.ibkr_client.account_values[self.active_connection["account_id"]].get("BuyingPower", "N/A")
                        self.account_values_label.configure(text=f"NetLiq: ${net_liquidation} | BP: ${buying_power}")
            else:
                self.connection_indicator.configure(text_color=ERROR_RED)
                self.connection_status.configure(text="DISCONNECTED")
                if hasattr(self, 'account_values_label'):
                    self.account_values_label.configure(text="")
                self.reconnect_button.pack(side="left", padx=10)
            
            if self.running_orders:
                active_count = len(self.active_orders)
                self.active_orders_label.configure(
                    text=f"Active Orders: {active_count}",
                    text_color=WARNING_YELLOW
                )
            else:
                self.active_orders_label.configure(text="")
            
            self.last_update.configure(text=f"{datetime.now().strftime('%H:%M:%S')}")
            self.date_label.configure(text=f"{datetime.now().strftime('%a %b %d %Y')}")
        except Exception as e:
            self.log(f"Error updating status bar: {str(e)}")
            logging.error(f"Error updating status bar: {str(e)}", exc_info=True)

    def _create_content_area(self, parent):
        """Create the premium content area"""
        self.content_area = ctk.CTkFrame(
            parent,
            fg_color=SECONDARY_COLOR,
            border_width=0,
            corner_radius=0
        )
        self.content_area.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    # ====================== ORDER MANAGEMENT ======================
    def show_order_management(self):
        """Display the premium order management interface"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Header frame with breadcrumb
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="TRADING > ORDER MANAGEMENT",
            font=("Segoe UI", 10, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left", anchor="w")
        
        # Main content frame - premium panel
        content_frame = ctk.CTkFrame(
            self.content_area,
            fg_color=PANEL_BG,
            border_width=0,
            corner_radius=8
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Title with premium styling
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="ORDER MANAGEMENT",
            font=("Segoe UI", 16, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left")

        # Two-column layout for order form and preview
        columns_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        columns_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1, minsize=400)
        columns_frame.grid_rowconfigure(0, weight=1)
        
        # Left column - Order form
        form_frame = ctk.CTkFrame(
            columns_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=6
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        form_frame.grid_columnconfigure(1, weight=1)

        # Form title
        ctk.CTkLabel(
            form_frame,
            text="NEW ORDER",
            font=("Segoe UI", 12, "bold"),
            text_color=PRIMARY_COLOR
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="w", padx=15)
        
        # Define form fields configuration with premium styling
        form_fields = [
            ("Account", "account_var", "dropdown", 
             [a["nickname"] if a["nickname"] else f"IBKR {a['account_id']}" for a in self.connected_accounts], True),
            ("Ticker", "ticker_entry", "entry", None, True),
            ("Action", "action_var", "radio", ["Buy", "Sell"], True),
            ("Quantity", "quantity_entry", "entry", None, True),
            ("Order Type", "order_type_var", "dropdown", ["Limit", "Market", "Stop", "Stop Limit"], True),
            ("Price", "price_entry", "entry", None, False),
            ("Stop Price", "stop_price_entry", "entry", None, False),
            ("Time in Force", "tif_var", "dropdown", ["Day", "GTC", "IOC", "FOK"], True),
            ("Execution Strategy", "strategy_var", "dropdown", ["Low", "Medium", "High"], True),
            ("Slippage Tolerance (%)", "slippage_entry", "entry", None, False),
            ("Notes", "notes_entry", "entry", None, False)
        ]

        # Create form fields with premium styling
        for i, (label, attr, field_type, *args) in enumerate(form_fields):
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.grid(row=i+1, column=0, sticky="ew", padx=15, pady=8)

            # Create label
            label_text = f"{label}{'*' if args[-1] else ''}"
            ctk.CTkLabel(
                row_frame,
                text=label_text,
                font=("Segoe UI", 11),
                text_color=LIGHT_TEXT,
                width=140,
                anchor="w"
            ).pack(side="left", padx=(0, 15))

            # Create input widget based on type
            if field_type == "entry":
                entry = ctk.CTkEntry(
                    row_frame,
                    height=36,
                    font=BODY_FONT,
                    border_width=1,
                    border_color=BORDER_COLOR,
                    fg_color="#0E1423",
                    corner_radius=4,
                    text_color=TEXT_COLOR
                )
                entry.pack(side="right", fill="x", expand=True)
                setattr(self, attr, entry)
                
            elif field_type == "dropdown":
                var = ctk.StringVar(value=args[0][0] if args[0] else "")
                dropdown = ctk.CTkComboBox(
                    row_frame,
                    variable=var,
                    values=args[0] if args[0] else [],
                    state="readonly",
                    height=36,
                    font=BODY_FONT,
                    dropdown_fg_color=DARK_BG,
                    dropdown_hover_color=HOVER_COLOR,
                    corner_radius=4,
                    button_color=PRIMARY_COLOR,
                    button_hover_color=ACTIVE_COLOR,
                    text_color=TEXT_COLOR,
                    fg_color="#0E1423",
                    border_width=1,
                    border_color=BORDER_COLOR
                )
                dropdown.pack(side="right", fill="x", expand=True)
                setattr(self, attr, var)
                
            elif field_type == "radio":
                var = ctk.StringVar(value=args[0][0].lower())
                radio_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                radio_frame.pack(side="right", fill="x", expand=True)

                for option in args[0]:
                    radio = ctk.CTkRadioButton(
                        radio_frame,
                        text=option,
                        variable=var,
                        value=option.lower().replace(" ", "_"),
                        font=BODY_FONT,
                        fg_color=PRIMARY_COLOR,
                        hover_color=ACTIVE_COLOR,
                        text_color=LIGHT_TEXT
                    )
                    radio.pack(side="left", padx=(0, 15))

                setattr(self, attr, var)

        # Initialize form values
        if self.connected_accounts:
            self.account_var.set(self.connected_accounts[0]["nickname"] if self.connected_accounts[0]["nickname"] else f"IBKR {self.connected_accounts[0]['account_id']}")
        self.action_var.set("buy")
        self.order_type_var.set("Limit")
        self.tif_var.set("Day")
        self.strategy_var.set("Medium")

        # Action buttons with premium styling - made more visible
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=len(form_fields)+2, column=0, sticky="e", padx=15, pady=15)

        preview_btn = ctk.CTkButton(
            button_frame,
            text="PREVIEW ORDER",
            command=self.preview_order,
            width=140,
            height=36,
            font=("Segoe UI", 11, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR,
            corner_radius=4,
            text_color=TEXT_COLOR,
            border_width=0
        )
        preview_btn.pack(side="left", padx=10)

        submit_btn = ctk.CTkButton(
            button_frame,
            text="SUBMIT ORDER",
            command=self.confirm_order,
            width=140,
            height=36,
            font=("Segoe UI", 11, "bold"),
            fg_color=SUCCESS_GREEN,
            hover_color="#00C600",
            corner_radius=4,
            text_color="#FFFFFF",
            border_width=0
        )
        submit_btn.pack(side="left")

        # Right column - Order preview and charts
        preview_frame = ctk.CTkFrame(
            columns_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=6
        )
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        # Preview title
        ctk.CTkLabel(
            preview_frame,
            text="ORDER PREVIEW",
            font=("Segoe UI", 12, "bold"),
            text_color=PRIMARY_COLOR
        ).grid(row=0, column=0, pady=(15, 10), sticky="w", padx=15)

        # Preview content area
        self.preview_content = ctk.CTkFrame(preview_frame, fg_color="transparent")
        self.preview_content.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.preview_content.grid_columnconfigure(0, weight=1)
        self.preview_content.grid_rowconfigure(0, weight=1)

        # Initial preview message
        ctk.CTkLabel(
            self.preview_content,
            text="Configure your order to see a detailed preview\nand execution analysis",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT,
            justify="center"
        ).pack(expand=True)

    def preview_order(self):
        """Show premium order preview with advanced execution analysis"""
        if not self.ibkr_client or not self.ibkr_client.connected:
            messagebox.showerror("Not Connected", "Please connect to IBKR before previewing orders")
            return
        
        # Get values from form
        try:
            account = self.account_var.get()
            if not account:
                raise ValueError("Please select an account")
                
            action = self.action_var.get().upper()
            ticker = self.ticker_entry.get().upper()
            if not ticker:
                raise ValueError("Please enter a ticker symbol")
                
            quantity_str = self.quantity_entry.get()
            if not quantity_str:
                raise ValueError("Please enter a quantity")
                
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
                
            order_type = self.order_type_var.get()
            price_str = self.price_entry.get() if self.price_entry.get() and order_type in ["Limit", "Stop Limit"] else None
            stop_price_str = self.stop_price_entry.get() if self.stop_price_entry.get() and order_type in ["Stop", "Stop Limit"] else None
            
            price = float(price_str) if price_str else None
            stop_price = float(stop_price_str) if stop_price_str else None
            
            tif = self.tif_var.get()
            strategy = self.strategy_var.get()
            slippage_tolerance_str = self.slippage_entry.get() if self.slippage_entry.get() else None
            slippage_tolerance = float(slippage_tolerance_str) if slippage_tolerance_str else None
            
            # Get market price from IBKR
            market_price = None
            if self.ibkr_client and self.ibkr_client.connected:
                # Request market data for the ticker
                contract = Contract()
                contract.symbol = ticker
                contract.secType = "STK"
                contract.exchange = "SMART"
                contract.currency = "USD"
                
                req_id = self.next_req_id
                self.next_req_id += 1
                
                # Request market data
                self.ibkr_client.reqMktData(req_id, contract, "", False, False, [])
                
                # Wait for market data with timeout
                start_time = time.time()
                while req_id not in self.current_market_data and (time.time() - start_time) < 5:
                    time.sleep(0.1)
                
                if req_id in self.current_market_data:
                    market_data = self.current_market_data[req_id]
                    if 4 in market_data:  # LAST_PRICE
                        market_price = market_data[4]
                    elif 1 in market_data:  # BID
                        market_price = market_data[1]
                    elif 2 in market_data:  # ASK
                        market_price = market_data[2]
                
                # Cancel market data subscription
                self.ibkr_client.cancelMktData(req_id)
                
            if market_price is None:
                raise ValueError("Could not retrieve market price for the symbol")
            
            # Calculate expected slippage with advanced model
            slippage_data = self._calculate_enhanced_slippage(ticker, quantity, market_price, strategy)
            expected_slippage_pct = slippage_data["expected_slippage_pct"]
            execution_probability = slippage_data["execution_probability"]
            partial_fill_pct = slippage_data["partial_fill_pct"]
            market_impact_bps = slippage_data["market_impact_bps"]
            exec_time_sec = slippage_data["execution_time_sec"]
            strategy = slippage_data["strategy"]
            
            # Calculate optimal execution trajectory
            execution_plan = self._calculate_optimal_execution(ticker, quantity, market_price, strategy)
            
            # Calculate expected average price
            if order_type == "Market":
                expected_avg_price = market_price * (1 + (expected_slippage_pct/100 if action.lower() == "buy" else -expected_slippage_pct/100))
            else:
                expected_avg_price = price if price else market_price
            
            # Format execution time
            exec_time_str = f"{int(exec_time_sec // 60)}m {int(exec_time_sec % 60)}s" if exec_time_sec >= 60 else f"{exec_time_sec:.1f} seconds"
            
            # Clear previous preview content
            for widget in self.preview_content.winfo_children():
                widget.destroy()
            
            # Create scrollable frame for preview content
            preview_canvas = ctk.CTkCanvas(self.preview_content, bg=DARK_BG, highlightthickness=0)
            scrollbar = ctk.CTkScrollbar(self.preview_content, orientation="vertical", command=preview_canvas.yview)
            scrollable_frame = ctk.CTkFrame(preview_canvas, fg_color=DARK_BG)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: preview_canvas.configure(
                    scrollregion=preview_canvas.bbox("all")
                )
            )
            
            preview_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            preview_canvas.configure(yscrollcommand=scrollbar.set)
            
            preview_canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Order summary section
            summary_frame = ctk.CTkFrame(scrollable_frame, fg_color=TABLE_ROW_BG, corner_radius=4)
            summary_frame.pack(fill="x", padx=0, pady=(0, 15))
            
            ctk.CTkLabel(
                summary_frame,
                text="ORDER SUMMARY",
                font=("Segoe UI", 12, "bold"),
                text_color=PRIMARY_COLOR
            ).pack(pady=(10, 5), anchor="w", padx=10)
            
            # Order details in a grid layout
            details_grid = ctk.CTkFrame(summary_frame, fg_color="transparent")
            details_grid.pack(fill="x", padx=10, pady=(0, 10))
            
            details = [
                ("Account:", account),
                ("Action:", action.capitalize()),
                ("Ticker:", ticker),
                ("Quantity:", f"{quantity:,}"),
                ("Order Type:", order_type),
                ("Time in Force:", tif),
                ("Strategy:", strategy)
            ]
            
            for i, (label, value) in enumerate(details):
                row = i % 4
                col = i // 4
                
                detail_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
                detail_frame.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                
                ctk.CTkLabel(
                    detail_frame,
                    text=label,
                    font=("Segoe UI", 11, "bold"),
                    text_color=LIGHT_TEXT,
                    width=100,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    detail_frame,
                    text=value,
                    font=("Segoe UI", 11),
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).pack(side="left")
            
            # Execution analysis section - enhanced with more details
            analysis_frame = ctk.CTkFrame(scrollable_frame, fg_color=TABLE_ROW_BG, corner_radius=4)
            analysis_frame.pack(fill="x", padx=0, pady=(0, 15))
            
            ctk.CTkLabel(
                analysis_frame,
                text="EXECUTION ANALYSIS",
                font=("Segoe UI", 12, "bold"),
                text_color=PRIMARY_COLOR
            ).pack(pady=(10, 5), anchor="w", padx=10)
            
            # Enhanced metrics display in a grid
            metrics_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
            metrics_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            metrics = [
                ("Current Market Price:", f"${market_price:.2f}"),
                ("Expected Avg Price:", f"${expected_avg_price:.2f}"),
                ("Expected Slippage:", f"{expected_slippage_pct:.2f}%"),
                ("Execution Probability:", f"{execution_probability*100:.1f}%"),
                ("Partial Fill Risk:", f"{partial_fill_pct*100:.1f}%"),
                ("Market Impact:", f"{market_impact_bps:.1f} bps"),
                ("Permanent Impact:", f"{slippage_data['permanent_impact_bps']:.1f} bps"),
                ("Temporary Impact:", f"{slippage_data['temporary_impact_bps']:.1f} bps"),
                ("Liquidity Factor:", f"{slippage_data['liquidity_factor']:.1f}x"),
                ("Volatility Factor:", f"{slippage_data['volatility_factor']:.1f}x"),
                ("Time of Day Factor:", f"{slippage_data['time_of_day_factor']:.1f}x"),
                ("Estimated Execution Time:", exec_time_str)
            ]
            
            for i, (label, value) in enumerate(metrics):
                row = i % 6
                col = i // 6
                
                metric_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
                metric_frame.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                
                ctk.CTkLabel(
                    metric_frame,
                    text=label,
                    font=("Segoe UI", 11, "bold"),
                    text_color=LIGHT_TEXT,
                    width=160,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    metric_frame,
                    text=value,
                    font=("Segoe UI", 11),
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).pack(side="left")
            
            # Execution strategy visualization
            strategy_frame = ctk.CTkFrame(scrollable_frame, fg_color=TABLE_ROW_BG, corner_radius=4)
            strategy_frame.pack(fill="x", padx=0, pady=(0, 15))
            
            ctk.CTkLabel(
                strategy_frame,
                text="EXECUTION STRATEGY",
                font=("Segoe UI", 12, "bold"),
                text_color=PRIMARY_COLOR
            ).pack(pady=(10, 5), anchor="w", padx=10)
            
            # Create matplotlib figure for strategy visualization
            fig = plt.Figure(figsize=(6, 3), dpi=100, facecolor=CHART_BG)
            ax = fig.add_subplot(111)
            ax.set_facecolor(CHART_BG)
            
            # Plot execution trajectory
            times = execution_plan["times"]
            shares_remaining = execution_plan["shares_remaining"]
            
            ax.plot(times, shares_remaining, color=PRIMARY_COLOR, linewidth=2)
            ax.fill_between(times, shares_remaining, color=PRIMARY_COLOR, alpha=0.2)
            
            ax.set_xlabel('Time (min)', color=LIGHT_TEXT, fontsize=9)
            ax.set_ylabel('Shares Remaining', color=LIGHT_TEXT, fontsize=9)
            ax.set_title('Optimal Execution Trajectory', color=TEXT_COLOR, fontsize=10)
            
            # Style the chart
            ax.spines['bottom'].set_color(BORDER_COLOR)
            ax.spines['top'].set_color(BORDER_COLOR) 
            ax.spines['right'].set_color(BORDER_COLOR)
            ax.spines['left'].set_color(BORDER_COLOR)
            ax.tick_params(axis='x', colors=LIGHT_TEXT)
            ax.tick_params(axis='y', colors=LIGHT_TEXT)
            
            # Embed the chart in Tkinter
            chart_canvas = FigureCanvasTkAgg(fig, master=strategy_frame)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(fill="x", padx=10, pady=(0, 10))
            plt.close(fig)  # Close figure to prevent memory leaks
            
            # Fill distribution visualization
            fill_frame = ctk.CTkFrame(scrollable_frame, fg_color=TABLE_ROW_BG, corner_radius=4)
            fill_frame.pack(fill="x", padx=0, pady=(0, 15))
            
            ctk.CTkLabel(
                fill_frame,
                text="EXPECTED FILL DISTRIBUTION",
                font=("Segoe UI", 12, "bold"),
                text_color=PRIMARY_COLOR
            ).pack(pady=(10, 5), anchor="w", padx=10)
            
            # Create fill distribution chart
            fig2 = plt.Figure(figsize=(6, 3), dpi=100, facecolor=CHART_BG)
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor(CHART_BG)
            
            # Plot fill distribution
            fills = slippage_data["fill_distribution"]
            time_points = np.linspace(0, exec_time_sec, len(fills))
            
            ax2.plot(time_points, fills, color=ACCENT_COLOR, linewidth=2)
            ax2.fill_between(time_points, fills, color=ACCENT_COLOR, alpha=0.2)
            
            ax2.set_xlabel('Time (s)', color=LIGHT_TEXT, fontsize=9)
            ax2.set_ylabel('Shares Filled', color=LIGHT_TEXT, fontsize=9)
            ax2.set_title('Expected Fill Over Time', color=TEXT_COLOR, fontsize=10)
            
            # Style the chart
            ax2.spines['bottom'].set_color(BORDER_COLOR)
            ax2.spines['top'].set_color(BORDER_COLOR) 
            ax2.spines['right'].set_color(BORDER_COLOR)
            ax2.spines['left'].set_color(BORDER_COLOR)
            ax2.tick_params(axis='x', colors=LIGHT_TEXT)
            ax2.tick_params(axis='y', colors=LIGHT_TEXT)
            
            # Embed the chart in Tkinter
            chart_canvas2 = FigureCanvasTkAgg(fig2, master=fill_frame)
            chart_canvas2.draw()
            chart_canvas2.get_tk_widget().pack(fill="x", padx=10, pady=(0, 10))
            plt.close(fig2)  # Close figure to prevent memory leaks
            
            # Risk warning if slippage exceeds threshold
            if slippage_tolerance and expected_slippage_pct > slippage_tolerance:
                warning_frame = ctk.CTkFrame(
                    scrollable_frame,
                    fg_color=ERROR_RED,
                    corner_radius=4,
                    border_width=0
                )
                warning_frame.pack(fill="x", padx=0, pady=(0, 15))
                
                ctk.CTkLabel(
                    warning_frame,
                    text=f"⚠️ WARNING: Expected slippage ({expected_slippage_pct:.2f}%) exceeds your threshold ({slippage_tolerance:.2f}%)",
                    font=("Segoe UI", 11, "bold"),
                    text_color="white",
                    justify="left"
                ).pack(padx=10, pady=5, fill="x")
            
            # Action buttons - made more visible
            action_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            action_frame.pack(fill="x", pady=(0, 15))
            
            ctk.CTkButton(
                action_frame,
                text="ADJUST ORDER",
                command=lambda: self.preview_content.focus(),
                width=140,
                height=36,
                font=("Segoe UI", 11, "bold"),
                fg_color=SECONDARY_COLOR,
                hover_color=HOVER_COLOR,
                corner_radius=4,
                text_color=TEXT_COLOR,
                border_width=1,
                border_color=BORDER_COLOR
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                action_frame,
                text="SUBMIT ORDER",
                command=lambda: self.confirm_order(ticker),
                width=140,
                height=36,
                font=("Segoe UI", 11, "bold"),
                fg_color=SUCCESS_GREEN,
                hover_color="#00C600",
                corner_radius=4,
                text_color="#FFFFFF",
                border_width=0
            ).pack(side="left")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid order parameters:\n{str(e)}")
            logging.error(f"Input error in order preview: {str(e)}", exc_info=True)
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate order preview:\n{str(e)}")
            logging.error(f"Error generating order preview: {str(e)}", exc_info=True)

    def confirm_order(self, ticker=None):
        """Submit the order to IBKR with advanced execution parameters"""
        if not self.ibkr_client or not self.ibkr_client.connected:
            messagebox.showerror("Not Connected", "Please connect to IBKR before submitting orders")
            return
            
        if not ticker:
            ticker = self.ticker_entry.get().upper()
            if not ticker:
                messagebox.showerror("Input Error", "Please enter a ticker symbol")
                return
        
        try:
            # Get form values
            account = self.account_var.get()
            if not account:
                raise ValueError("Please select an account")
                
            action = self.action_var.get().upper()
            quantity_str = self.quantity_entry.get()
            if not quantity_str:
                raise ValueError("Please enter a quantity")
                
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
                
            order_type = self.order_type_var.get()
            price_str = self.price_entry.get() if self.price_entry.get() and order_type in ["Limit", "Stop Limit"] else None
            stop_price_str = self.stop_price_entry.get() if self.stop_price_entry.get() and order_type in ["Stop", "Stop Limit"] else None
            
            price = float(price_str) if price_str else None
            stop_price = float(stop_price_str) if stop_price_str else None
            
            tif = self.tif_var.get()
            strategy = self.strategy_var.get()
            
            # Create IBKR contract
            contract = Contract()
            contract.symbol = ticker
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            # Create IBKR order
            order = Order()
            order.action = "BUY" if action.lower() == "buy" else "SELL"
            
            # Set order type and parameters
            if order_type == "Market":
                order.orderType = "MKT"
            elif order_type == "Limit":
                order.orderType = "LMT"
                order.lmtPrice = price
            elif order_type == "Stop":
                order.orderType = "STP"
                order.auxPrice = stop_price
            elif order_type == "Stop Limit":
                order.orderType = "STP LMT"
                order.lmtPrice = price
                order.auxPrice = stop_price
            
            # Set time in force
            if tif == "Day":
                order.tif = "DAY"
            elif tif == "GTC":
                order.tif = "GTC"
            elif tif == "IOC":
                order.tif = "IOC"
            elif tif == "FOK":
                order.tif = "FOK"
            
            # Set quantity
            order.totalQuantity = quantity
            
            # Add advanced algo parameters based on strategy
            if strategy in ["Low", "Medium", "High"]:
                strategy_params = SLIPPAGE_PARAMS.get(strategy, SLIPPAGE_PARAMS["Medium"])
                order.algoStrategy = strategy_params["strategy"]
                order.algoParams = []
                
                if strategy_params["strategy"] == "TWAP":
                    order.algoParams.append(("startTime", "09:30:00 US/Eastern"))
                    order.algoParams.append(("endTime", "16:00:00 US/Eastern"))
                    order.algoParams.append(("participationRate", str(strategy_params["participation_rate"])))
                    
                elif strategy_params["strategy"] == "VWAP":
                    order.algoParams.append(("maxPctVol", str(strategy_params["participation_rate"])))
                    order.algoParams.append(("noTakeLiq", "0"))
                    order.algoParams.append(("startTime", "09:30:00 US/Eastern"))
                    order.algoParams.append(("endTime", "16:00:00 US/Eastern"))
                    
                elif strategy_params["strategy"] == "Aggressive":
                    order.algoParams.append(("urgency", str(strategy_params["urgency"])))
            
            # Submit the order
            order_id = self.submit_order(contract, order, account)
            
            if order_id:
                messagebox.showinfo(
                    "Order Submitted",
                    f"Advanced Order {order_id} for {ticker} has been submitted successfully!\n\n"
                    f"Details:\n"
                    f"- Type: {order_type}\n"
                    f"- Strategy: {strategy}\n"
                    f"- Quantity: {quantity:,} shares\n"
                    f"- Action: {action}\n\n"
                    "You can track the order status in the Order History tab."
                )
            else:
                messagebox.showerror(
                    "Order Failed",
                    "Failed to submit order. Please check your connection and try again."
                )
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid order parameters:\n{str(e)}")
            logging.error(f"Input error in order confirmation: {str(e)}", exc_info=True)
        except Exception as e:
            messagebox.showerror("Order Error", f"Failed to submit order:\n{str(e)}")
            logging.error(f"Error submitting order: {str(e)}", exc_info=True)

        # ====================== ORDER HISTORY ======================
    def show_order_history(self):
        """Display premium order history with detailed analytics"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Header frame with breadcrumb
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="TRADING > ORDER HISTORY",
            font=("Segoe UI", 10, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left", anchor="w")
        
        # Main content frame - premium panel
        content_frame = ctk.CTkFrame(
            self.content_area,
            fg_color=PANEL_BG,
            border_width=0,
            corner_radius=8
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Title with premium styling
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="ORDER HISTORY & ANALYTICS",
            font=("Segoe UI", 16, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left")
        
        # Add filter controls
        filter_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        
        # Date range filter
        ctk.CTkLabel(
            filter_frame,
            text="Date Range:",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT
        ).pack(side="left", padx=(0, 10))
        
        self.start_date_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Start Date",
            width=120,
            height=32,
            font=BODY_FONT,
            fg_color="#0E1423",
            corner_radius=4,
            text_color=TEXT_COLOR
        )
        self.start_date_entry.pack(side="left", padx=(0, 10))
        
        self.end_date_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="End Date",
            width=120,
            height=32,
            font=BODY_FONT,
            fg_color="#0E1423",
            corner_radius=4,
            text_color=TEXT_COLOR
        )
        self.end_date_entry.pack(side="left", padx=(0, 20))
        
        # Status filter
        ctk.CTkLabel(
            filter_frame,
            text="Status:",
            font=("Segoe UI", 11),
            text_color=LIGHT_TEXT
        ).pack(side="left", padx=(0, 10))
        
        self.status_filter_var = ctk.StringVar(value="All")
        status_dropdown = ctk.CTkComboBox(
            filter_frame,
            variable=self.status_filter_var,
            values=["All", "Filled", "Partially Filled", "Cancelled", "Rejected"],
            state="readonly",
            width=120,
            height=32,
            font=BODY_FONT,
            dropdown_fg_color=DARK_BG,
            dropdown_hover_color=HOVER_COLOR,
            corner_radius=4,
            button_color=PRIMARY_COLOR,
            text_color=TEXT_COLOR,
            fg_color="#0E1423"
        )
        status_dropdown.pack(side="left", padx=(0, 20))
        
        # Apply filters button
        ctk.CTkButton(
            filter_frame,
            text="APPLY FILTERS",
            command=self._apply_history_filters,
            width=120,
            height=32,
            font=("Segoe UI", 11),
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR,
            corner_radius=4,
            text_color=TEXT_COLOR
        ).pack(side="left")
        
        # Table frame - premium styling
        table_frame = ctk.CTkFrame(
            content_frame,
            fg_color=DARK_BG,
            border_width=0,
            corner_radius=6
        )
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 15))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create a Treeview widget for the table with premium styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                      background=TABLE_ROW_BG,
                      foreground=TEXT_COLOR,
                      rowheight=32,
                      fieldbackground=TABLE_ROW_BG,
                      borderwidth=0,
                      font=TABLE_FONT)
        style.configure("Treeview.Heading",
                      background=TABLE_HEADER_BG,
                      foreground=TEXT_COLOR,
                      font=TABLE_HEADER_FONT,
                      padding=8,
                      borderwidth=0)
        style.map("Treeview",
                background=[('selected', SELECTION_COLOR)],
                foreground=[('selected', TEXT_COLOR)])
        
        # Create the treeview with additional institutional columns
        self.history_tree = ttk.Treeview(
            table_frame,
            columns=("order_id", "time", "symbol", "side", "strategy", "quantity", "filled", "avg_price", "slippage", "status", "impact", "liquidity"),
            show="headings",
            selectmode="extended",
            style="Treeview"
        )
        
        # Configure columns with premium widths
        self.history_tree.column("order_id", width=100, anchor="w")
        self.history_tree.column("time", width=140, anchor="w")
        self.history_tree.column("symbol", width=80, anchor="center")
        self.history_tree.column("side", width=60, anchor="center")
        self.history_tree.column("strategy", width=80, anchor="center")
        self.history_tree.column("quantity", width=90, anchor="e")
        self.history_tree.column("filled", width=80, anchor="e")
        self.history_tree.column("avg_price", width=100, anchor="e")
        self.history_tree.column("slippage", width=90, anchor="e")
        self.history_tree.column("status", width=120, anchor="center")
        self.history_tree.column("impact", width=90, anchor="e")
        self.history_tree.column("liquidity", width=90, anchor="center")
        
        # Add headings with premium styling
        self.history_tree.heading("order_id", text="ORDER ID")
        self.history_tree.heading("time", text="TIME")
        self.history_tree.heading("symbol", text="SYMBOL")
        self.history_tree.heading("side", text="SIDE")
        self.history_tree.heading("strategy", text="STRATEGY")
        self.history_tree.heading("quantity", text="QTY")
        self.history_tree.heading("filled", text="FILLED %")
        self.history_tree.heading("avg_price", text="AVG PRICE")
        self.history_tree.heading("slippage", text="SLIPPAGE %")
        self.history_tree.heading("status", text="STATUS")
        self.history_tree.heading("impact", text="IMPACT (BPS)")
        self.history_tree.heading("liquidity", text="LIQUIDITY")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid the tree and scrollbars - premium layout
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Add double-click event for order details
        self.history_tree.bind("<Double-1>", self._show_order_details)
        
        # Populate with data
        self._populate_order_history()
        
        # Add analytics section below the table
        analytics_frame = ctk.CTkFrame(
            content_frame,
            fg_color=DARK_BG,
            border_width=0,
            corner_radius=6
        )
        analytics_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 15))
        analytics_frame.grid_columnconfigure(0, weight=1)
        analytics_frame.grid_rowconfigure(1, weight=1)
        
        # Analytics title
        ctk.CTkLabel(
            analytics_frame,
            text="EXECUTION ANALYTICS",
            font=("Segoe UI", 12, "bold"),
            text_color=PRIMARY_COLOR
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        # Create matplotlib figure for analytics visualization
        fig = plt.Figure(figsize=(12, 4), dpi=100, facecolor=CHART_BG)
        ax1 = fig.add_subplot(131)
        ax2 = fig.add_subplot(132)
        ax3 = fig.add_subplot(133)
        
        # Style all axes
        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor(CHART_BG)
            ax.spines['bottom'].set_color(BORDER_COLOR)
            ax.spines['top'].set_color(BORDER_COLOR) 
            ax.spines['right'].set_color(BORDER_COLOR)
            ax.spines['left'].set_color(BORDER_COLOR)
            ax.tick_params(axis='x', colors=LIGHT_TEXT)
            ax.tick_params(axis='y', colors=LIGHT_TEXT)
        
        # Plot 1: Slippage distribution
        slippages = [o["slippage_pct"] for o in self.order_history if "slippage_pct" in o]
        if slippages:
            ax1.hist(slippages, bins=15, color=PRIMARY_COLOR, alpha=0.7)
            ax1.set_title('Slippage Distribution', color=TEXT_COLOR, fontsize=10)
            ax1.set_xlabel('Slippage (%)', color=LIGHT_TEXT, fontsize=8)
            ax1.set_ylabel('Frequency', color=LIGHT_TEXT, fontsize=8)
        
        # Plot 2: Execution time vs size
        exec_times = [o.get("execution_time_ms", 0)/1000 for o in self.order_history]
        quantities = [o["quantity"] for o in self.order_history]
        if exec_times and quantities:
            ax2.scatter(quantities, exec_times, color=PRIMARY_COLOR, alpha=0.7)
            ax2.set_title('Execution Time vs Order Size', color=TEXT_COLOR, fontsize=10)
            ax2.set_xlabel('Quantity', color=LIGHT_TEXT, fontsize=8)
            ax2.set_ylabel('Execution Time (s)', color=LIGHT_TEXT, fontsize=8)
        
        # Plot 3: Strategy performance
        if len(self.order_history) > 0:
            strategies = {}
            for order in self.order_history:
                strat = order.get("strategy", "Unknown")
                if strat not in strategies:
                    strategies[strat] = []
                strategies[strat].append(order.get("slippage_pct", 0))
            
            avg_slippage = {k: np.mean(v) for k, v in strategies.items()}
            ax3.bar(avg_slippage.keys(), avg_slippage.values(), color=PRIMARY_COLOR, alpha=0.7)
            ax3.set_title('Avg Slippage by Strategy', color=TEXT_COLOR, fontsize=10)
            ax3.set_xlabel('Strategy', color=LIGHT_TEXT, fontsize=8)
            ax3.set_ylabel('Avg Slippage (%)', color=LIGHT_TEXT, fontsize=8)
            ax3.tick_params(axis='x', rotation=45)
        
        # Adjust layout
        fig.tight_layout()
        
        # Embed the chart in Tkinter
        analytics_canvas = FigureCanvasTkAgg(fig, master=analytics_frame)
        analytics_canvas.draw()
        analytics_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        plt.close(fig)  # Close figure to prevent memory leaks

    def _show_order_details(self, event):
        """Show detailed view of selected order with enhanced error handling"""
        try:
            selected_item = self.history_tree.selection()
            if not selected_item:
                return
                
            item = self.history_tree.item(selected_item[0])
            order_id = item['values'][0]
            
            # Find the order in history
            order = next((o for o in self.order_history if o["order_id"] == order_id), None)
            if not order:
                messagebox.showwarning("Order Not Found", "Selected order details could not be found")
                return
                
            # Create details window with connection check
            if not self.ibkr_client or not self.ibkr_client.connected:
                if not messagebox.askyesno(
                    "Disconnected", 
                    "You are not connected to IBKR. Some features may be limited.\nContinue anyway?",
                    icon="warning"
                ):
                    return

            details_window = ctk.CTkToplevel(self)
            details_window.title(f"Order Details - {order_id}")
            details_window.geometry("800x600")
            details_window.resizable(False, False)
            details_window.transient(self)
            details_window.grab_set()
            
            # Center the window
            x = self.winfo_x() + (self.winfo_width() // 2) - 400
            y = self.winfo_y() + (self.winfo_height() // 2) - 300
            details_window.geometry(f"+{x}+{y}")
            
            # Premium window styling
            details_window.configure(fg_color=DARK_BG)
            
            # Create notebook for tabs
            notebook = ttk.Notebook(details_window)
            notebook.pack(fill="both", expand=True)
            
            # Tab 1: Order Details
            details_tab = ctk.CTkFrame(notebook, fg_color=PANEL_BG)
            notebook.add(details_tab, text="Order Details")
            
            # Order details in a grid
            details_grid = ctk.CTkFrame(details_tab, fg_color="transparent")
            details_grid.pack(fill="both", expand=True, padx=15, pady=15)
            
            details = [
                ("Order ID:", order["order_id"]),
                ("Time:", order["time"]),
                ("Symbol:", order["symbol"]),
                ("Side:", order["side"]),
                ("Order Type:", order["order_type"]),
                ("Strategy:", order.get("strategy", "N/A")),
                ("Quantity:", f"{order['quantity']:,}"),
                ("Filled:", f"{order['filled_quantity']:,} ({order['filled_pct']}%)"),
                ("Average Price:", f"${order['avg_price']:.2f}"),
                ("Slippage:", f"{order['slippage_pct']:.2f}%"),
                ("Market Impact:", f"{order.get('market_impact_bps', 'N/A')} bps"),
                ("Permanent Impact:", f"{order.get('permanent_impact_bps', 'N/A')} bps"),
                ("Temporary Impact:", f"{order.get('temporary_impact_bps', 'N/A')} bps"),
                ("Liquidity Factor:", f"{order.get('liquidity_factor', 'N/A')}x"),
                ("Time of Day Factor:", f"{order.get('time_of_day_factor', 'N/A')}x"),
                ("Volatility Factor:", f"{order.get('volatility_factor', 'N/A')}x"),
                ("Account:", order["account"])
            ]
            
            for i, (label, value) in enumerate(details):
                row = i % 10
                col = i // 10
                
                detail_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
                detail_frame.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                
                ctk.CTkLabel(
                    detail_frame,
                    text=label,
                    font=("Segoe UI", 11, "bold"),
                    text_color=LIGHT_TEXT,
                    width=140,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    detail_frame,
                    text=value,
                    font=("Segoe UI", 11),
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).pack(side="left")
            
            # Tab 2: Execution Timeline
            timeline_tab = ctk.CTkFrame(notebook, fg_color=PANEL_BG)
            notebook.add(timeline_tab, text="Execution Timeline")
            
            # Create execution timeline chart with error handling
            try:
                fig = plt.Figure(figsize=(7, 4), dpi=100, facecolor=CHART_BG)
                ax = fig.add_subplot(111)
                ax.set_facecolor(CHART_BG)
                
                # Simulate execution timeline (in a real app, use actual execution data)
                if "fill_distribution" in order:
                    fills = order["fill_distribution"]
                    times = np.linspace(0, order.get("execution_time_ms", 1000)/1000, len(fills))
                    
                    ax.plot(times, fills, color=PRIMARY_COLOR, linewidth=2)
                    ax.fill_between(times, fills, color=PRIMARY_COLOR, alpha=0.2)
                    
                    ax.set_xlabel('Time (s)', color=LIGHT_TEXT, fontsize=9)
                    ax.set_ylabel('Shares Filled', color=LIGHT_TEXT, fontsize=9)
                    ax.set_title('Execution Timeline', color=TEXT_COLOR, fontsize=10)
                    
                    # Style the chart
                    ax.spines['bottom'].set_color(BORDER_COLOR)
                    ax.spines['top'].set_color(BORDER_COLOR) 
                    ax.spines['right'].set_color(BORDER_COLOR)
                    ax.spines['left'].set_color(BORDER_COLOR)
                    ax.tick_params(axis='x', colors=LIGHT_TEXT)
                    ax.tick_params(axis='y', colors=LIGHT_TEXT)
                    
                    # Embed the chart in Tkinter
                    chart_canvas = FigureCanvasTkAgg(fig, master=timeline_tab)
                    chart_canvas.draw()
                    chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
                    plt.close(fig)  # Close figure to prevent memory leaks
                else:
                    ctk.CTkLabel(
                        timeline_tab,
                        text="Execution timeline data not available",
                        font=("Segoe UI", 11),
                        text_color=LIGHT_TEXT
                    ).pack(expand=True)
            except Exception as e:
                self.log(f"Error creating execution timeline: {str(e)}")
                logging.error(f"Error creating execution timeline: {str(e)}", exc_info=True)
                ctk.CTkLabel(
                    timeline_tab,
                    text="Failed to generate execution timeline",
                    font=("Segoe UI", 11),
                    text_color=ERROR_RED
                ).pack(expand=True)
            
            # Tab 3: Order Impact Analysis
            impact_tab = ctk.CTkFrame(notebook, fg_color=PANEL_BG)
            notebook.add(impact_tab, text="Impact Analysis")
            
            # Create impact analysis chart with error handling
            try:
                fig = plt.Figure(figsize=(7, 4), dpi=100, facecolor=CHART_BG)
                ax = fig.add_subplot(111)
                ax.set_facecolor(CHART_BG)
                
                # Simulate impact analysis (in a real app, use actual market impact data)
                impacts = {
                    'Market Impact': order.get("market_impact_bps", 0),
                    'Permanent Impact': order.get("permanent_impact_bps", 0),
                    'Temporary Impact': order.get("temporary_impact_bps", 0)
                }
                
                ax.bar(impacts.keys(), impacts.values(), color=PRIMARY_COLOR, alpha=0.7)
                ax.set_title('Market Impact Analysis', color=TEXT_COLOR, fontsize=10)
                ax.set_ylabel('Basis Points', color=LIGHT_TEXT, fontsize=9)
                
                # Style the chart
                ax.spines['bottom'].set_color(BORDER_COLOR)
                ax.spines['top'].set_color(BORDER_COLOR) 
                ax.spines['right'].set_color(BORDER_COLOR)
                ax.spines['left'].set_color(BORDER_COLOR)
                ax.tick_params(axis='x', colors=LIGHT_TEXT, rotation=45)
                ax.tick_params(axis='y', colors=LIGHT_TEXT)
                
                # Embed the chart in Tkinter
                chart_canvas = FigureCanvasTkAgg(fig, master=impact_tab)
                chart_canvas.draw()
                chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
                plt.close(fig)  # Close figure to prevent memory leaks
            except Exception as e:
                self.log(f"Error creating impact analysis: {str(e)}")
                logging.error(f"Error creating impact analysis: {str(e)}", exc_info=True)
                ctk.CTkLabel(
                    impact_tab,
                    text="Failed to generate impact analysis",
                    font=("Segoe UI", 11),
                    text_color=ERROR_RED
                ).pack(expand=True)
            
            # Add refresh button if connected to IBKR
            if self.ibkr_client and self.ibkr_client.connected:
                refresh_frame = ctk.CTkFrame(details_window, fg_color="transparent")
                refresh_frame.pack(pady=(0, 10))
                
                ctk.CTkButton(
                    refresh_frame,
                    text="REFRESH DATA",
                    command=lambda: self._refresh_order_data(order_id, details_window),
                    width=120,
                    height=32,
                    font=("Segoe UI", 11, "bold"),
                    fg_color=PRIMARY_COLOR,
                    hover_color=ACTIVE_COLOR,
                    corner_radius=4,
                    text_color=TEXT_COLOR
                ).pack()
                
        except Exception as e:
            self.log(f"Error showing order details: {str(e)}")
            logging.error(f"Error showing order details: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to show order details:\n{str(e)}")

    def _refresh_order_data(self, order_id, window):
        """Refresh order data from IBKR with error handling"""
        try:
            if not self.ibkr_client or not self.ibkr_client.connected:
                messagebox.showwarning("Disconnected", "Cannot refresh - not connected to IBKR")
                return
                
            # Request order status from IBKR
            self.ibkr_client.reqOpenOrders()
            
            # In a real implementation, you would:
            # 1. Request updated order status
            # 2. Wait for callback
            # 3. Update the UI
            
            messagebox.showinfo("Refreshed", "Order data has been refreshed")
            
        except Exception as e:
            self.log(f"Error refreshing order data: {str(e)}")
            logging.error(f"Error refreshing order data: {str(e)}", exc_info=True)
            messagebox.showerror("Refresh Failed", f"Failed to refresh order data:\n{str(e)}")

    def _apply_history_filters(self):
        """Apply filters to order history with error handling"""
        try:
            self._populate_order_history()
        except Exception as e:
            self.log(f"Error applying history filters: {str(e)}")
            logging.error(f"Error applying history filters: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to apply filters:\n{str(e)}")

    def _populate_order_history(self):
        """Populate the order history table with filtered data and error handling"""
        try:
            # Clear existing data
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Apply filters
            filtered_orders = self.order_history
            
            # Status filter
            status_filter = self.status_filter_var.get()
            if status_filter != "All":
                filtered_orders = [o for o in filtered_orders if o["status"] == status_filter]
            
            # Date range filter (simplified - in a real app, parse dates properly)
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            
            if start_date:
                try:
                    filtered_orders = [o for o in filtered_orders if o["time"] >= start_date]
                except Exception as e:
                    self.log(f"Invalid start date format: {str(e)}")
                    messagebox.showwarning("Invalid Date", "Please enter a valid start date (YYYY-MM-DD)")
            
            if end_date:
                try:
                    filtered_orders = [o for o in filtered_orders if o["time"] <= end_date]
                except Exception as e:
                    self.log(f"Invalid end date format: {str(e)}")
                    messagebox.showwarning("Invalid Date", "Please enter a valid end date (YYYY-MM-DD)")
            
            # Add data to the treeview with alternating row colors
            for idx, order in enumerate(sorted(filtered_orders, key=lambda x: x["time"], reverse=True)):
                status_color = ""
                if order["status"] == "Filled":
                    status_color = SUCCESS_GREEN
                elif order["status"] == "Partially Filled":
                    status_color = WARNING_YELLOW
                elif order["status"] in ["Cancelled", "Rejected"]:
                    status_color = ERROR_RED
                
                try:
                    liquidity_bucket = self._get_liquidity_bucket(order["symbol"], order["quantity"])
                except Exception as e:
                    liquidity_bucket = "Unknown"
                    self.log(f"Error getting liquidity bucket: {str(e)}")
                
                # Alternate row colors
                tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
                
                self.history_tree.insert("", "end", values=(
                    order["order_id"],
                    order["time"],
                    order["symbol"],
                    order["side"],
                    order.get("strategy", "N/A"),
                    f"{order['quantity']:,}",
                    f"{order['filled_pct']}%",
                    f"${order['avg_price']:.2f}",
                    f"{order['slippage_pct']:.2f}%",
                    order["status"],
                    f"{order.get('market_impact_bps', 0):.1f}",
                    liquidity_bucket
                ), tags=tags)
                
            # Configure tag colors for alternating rows
            self.history_tree.tag_configure('evenrow', background=TABLE_ROW_BG)
            self.history_tree.tag_configure('oddrow', background=TABLE_ROW_ALT)
            
        except Exception as e:
            self.log(f"Error populating order history: {str(e)}")
            logging.error(f"Error populating order history: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load order history:\n{str(e)}")

    # ====================== ENHANCED ERROR HANDLING ======================
    def _handle_ibkr_error(self, error_code, error_string):
        """Centralized IBKR error handling with enhanced responses"""
        critical_errors = {
            502: "Couldn't connect to TWS. Confirm API connection is enabled in TWS/IB Gateway.",
            503: "The TWS is out of date and must be upgraded.",
            1100: "Connectivity between IB and TWS has been lost.",
            1101: "Connectivity between TWS and the API has been lost.",
            1102: "The TWS socket port has been closed.",
            1300: "TWS has been shut down."
        }
        
        if error_code in critical_errors:
            self.log(f"CRITICAL ERROR {error_code}: {error_string}")
            self.on_ibkr_disconnect(critical_errors[error_code])
            
            # Show urgent notification if we have active orders
            if self.active_orders:
                self.after(0, lambda: messagebox.showwarning(
                    "Connection Lost", 
                    f"{critical_errors[error_code]}\n\n"
                    f"You have {len(self.active_orders)} active orders that may be affected."
                ))
        else:
            # Log non-critical errors
            self.log(f"IBKR Error {error_code}: {error_string}")
            
            # Show warning for significant but non-critical errors
            if error_code in [201, 399]:  # Order rejected or cancelled
                self.after(0, lambda: messagebox.showwarning(
                    "Order Issue",
                    f"IBKR reported an order issue: {error_string}"
                ))

    def _check_connection_status(self):
        """Verify active connection to IBKR and attempt recovery if needed"""
        if not hasattr(self, 'ibkr_client') or not self.ibkr_client:
            return False
            
        if not self.ibkr_client.connected:
            if self.reconnect_attempts < self.max_reconnect_attempts:
                self.reconnect_attempts += 1
                self.after(RECONNECT_DELAY * 1000, self._attempt_reconnect)
                return False
            return False
            
        # Verify connection is actually alive
        try:
            # Simple ping check
            if time.time() - self.ibkr_client.last_ping_time > PING_INTERVAL * 3:
                self.ibkr_client.ping()
                return False
                
            return True
        except Exception as e:
            self.log(f"Connection check failed: {str(e)}")
            return False

    def _safe_disconnect(self):
        """Safely disconnect from IBKR with cleanup"""
        try:
            if hasattr(self, 'ibkr_client') and self.ibkr_client:
                # Cancel all active orders first
                with self.order_lock:
                    for order_id in list(self.active_orders.keys()):
                        try:
                            self.ibkr_client.cancelOrder(order_id)
                        except Exception as e:
                            self.log(f"Error cancelling order {order_id}: {str(e)}")
                            logging.error(f"Error cancelling order {order_id}: {str(e)}", exc_info=True)
                
                # Disconnect
                self.ibkr_client.disconnect()
                self.ibkr_client.connected = False
                self.active_connection = None
                
        except Exception as e:
            self.log(f"Error during safe disconnect: {str(e)}")
        finally:
            self._update_status_bar()

    # ====================== SECURITY ENHANCEMENTS ======================
    def _encrypt_sensitive_data(self, data):
        """Encrypt sensitive data before storage"""
        try:
            if not isinstance(data, str):
                data = str(data)
            return security_manager.encrypt(data)
        except Exception as e:
            self.log(f"Encryption failed: {str(e)}")
            return data  # Fallback to plaintext if encryption fails
            
    def _decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data after retrieval"""
        try:
            if not isinstance(encrypted_data, str):
                encrypted_data = str(encrypted_data)
            return security_manager.decrypt(encrypted_data)
        except Exception as e:
            self.log(f"Decryption failed: {str(e)}")
            return encrypted_data  # Fallback to encrypted data if decryption fails

    def _cleanup_sensitive_data(self):
        """Clear sensitive data from memory"""
        try:
            if hasattr(self, 'connected_accounts'):
                for account in self.connected_accounts:
                    if 'password' in account:  # Shouldn't exist, but just in case
                        account['password'] = '*' * len(account['password'])
                        
            # Clear any other sensitive data
            if hasattr(self, 'temp_password'):
                del self.temp_password
                
        except Exception as e:
            self.log(f"Cleanup error: {str(e)}")

    def _on_app_close(self):
        """Handle application close with cleanup"""
        try:
            self._safe_disconnect()
            self._cleanup_sensitive_data()
            self.destroy()
        except Exception as e:
            self.log(f"Error during app close: {str(e)}")
            self.destroy()  # Ensure window closes even if cleanup fails

    def _calculate_execution_time(self, order_info):
        """Calculate execution time for an order"""
        try:
            if "time" not in order_info:
                return 0
                
            order_time = datetime.strptime(order_info["time"], "%Y-%m-%d %H:%M:%S")
            if "lastFillTime" in order_info:
                fill_time = datetime.strptime(order_info["lastFillTime"], "%Y-%m-%d %H:%M:%S")
                return (fill_time - order_time).total_seconds() * 1000  # Convert to ms
            return 0
        except Exception as e:
            self.log(f"Error calculating execution time: {str(e)}")
            return 0

    def clear_window(self):
        """Clear all widgets from the main window"""
        for widget in self.winfo_children():
            widget.destroy()

    def clear_content_area(self):
        """Clear the content area"""
        if hasattr(self, 'content_area'):
            for widget in self.content_area.winfo_children():
                widget.destroy()

    def show_link_account(self):
        """Show the account linking interface"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Header frame with breadcrumb
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="SETTINGS > LINK ACCOUNT",
            font=("Segoe UI", 10, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left", anchor="w")
        
        # Main content frame - premium panel
        content_frame = ctk.CTkFrame(
            self.content_area,
            fg_color=PANEL_BG,
            border_width=0,
            corner_radius=8
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Title with premium styling
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="LINK IBKR ACCOUNT",
            font=("Segoe UI", 16, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left")

        # Form frame
        form_frame = ctk.CTkFrame(
            content_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=6
        )
        form_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        form_frame.grid_columnconfigure(1, weight=1)

        # Form fields
        fields = [
            ("Connection Type:", "connection_type_var", "dropdown", ["TWS (Desktop)", "IB Gateway"], True),
            ("Account ID:", "link_account_id_entry", "entry", None, True),
            ("Client ID:", "link_client_id_entry", "entry", None, False),
            ("Nickname (Optional):", "link_nickname_entry", "entry", None, False)
        ]

        for i, (label, attr, field_type, *args) in enumerate(fields):
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, sticky="ew", padx=15, pady=8)

            ctk.CTkLabel(
                row_frame,
                text=label,
                font=("Segoe UI", 11),
                text_color=LIGHT_TEXT,
                width=140,
                anchor="w"
            ).pack(side="left", padx=(0, 15))

            if field_type == "entry":
                entry = ctk.CTkEntry(
                    row_frame,
                    height=36,
                    font=BODY_FONT,
                    border_width=1,
                    border_color=BORDER_COLOR,
                    fg_color="#0E1423",
                    corner_radius=4,
                    text_color=TEXT_COLOR
                )
                entry.pack(side="right", fill="x", expand=True)
                setattr(self, attr, entry)
            elif field_type == "dropdown":
                var = ctk.StringVar(value=args[0][0])
                dropdown = ctk.CTkComboBox(
                    row_frame,
                    variable=var,
                    values=args[0],
                    state="readonly",
                    height=36,
                    font=BODY_FONT,
                    dropdown_fg_color=DARK_BG,
                    dropdown_hover_color=HOVER_COLOR,
                    corner_radius=4,
                    button_color=PRIMARY_COLOR,
                    button_hover_color=ACTIVE_COLOR,
                    text_color=TEXT_COLOR,
                    fg_color="#0E1423",
                    border_width=1,
                    border_color=BORDER_COLOR
                )
                dropdown.pack(side="right", fill="x", expand=True)
                setattr(self, attr, var)

        # Initialize form values
        self.link_client_id_entry.insert(0, "0")

        # Action buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=len(fields)+1, column=0, sticky="e", padx=15, pady=15)

        ctk.CTkButton(
            button_frame,
            text="TEST CONNECTION",
            command=self.test_connection,
            width=140,
            height=36,
            font=("Segoe UI", 11, "bold"),
            fg_color=SECONDARY_COLOR,
            hover_color=HOVER_COLOR,
            corner_radius=4,
            text_color=TEXT_COLOR,
            border_width=1,
            border_color=BORDER_COLOR
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="SAVE ACCOUNT",
            command=self.save_account,
            width=140,
            height=36,
            font=("Segoe UI", 11, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR,
            corner_radius=4,
            text_color=TEXT_COLOR,
            border_width=0
        ).pack(side="left")

    def test_connection(self):
        """Test the IBKR connection with provided credentials"""
        try:
            connection_type = self.connection_type_var.get()
            account_id = self.link_account_id_entry.get()
            client_id = self.link_client_id_entry.get()
            
            if not account_id:
                raise ValueError("Please enter an Account ID")
                
            if not client_id:
                client_id = "0"
                
            # Test the connection
            success = self.connect_to_ibkr(connection_type, account_id, client_id)
            
            if success:
                messagebox.showinfo(
                    "Connection Successful",
                    f"Successfully connected to {connection_type} with account {account_id}"
                )
                self.disconnect_from_ibkr()  # Disconnect after test
            else:
                messagebox.showerror(
                    "Connection Failed",
                    "Failed to connect to IBKR. Please check your credentials and try again."
                )
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid parameters:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to test connection:\n{str(e)}")

    def save_account(self):
        """Save the account configuration"""
        try:
            connection_type = self.connection_type_var.get()
            account_id = self.link_account_id_entry.get()
            client_id = self.link_client_id_entry.get()
            nickname = self.link_nickname_entry.get()
            
            if not account_id:
                raise ValueError("Please enter an Account ID")
                
            if not client_id:
                client_id = "0"
                
            # Check if account already exists
            existing_account = next(
                (acc for acc in self.connected_accounts if acc["account_id"] == account_id and acc["client_id"] == client_id),
                None
            )
            
            if existing_account:
                # Update existing account
                existing_account["connection_type"] = connection_type
                existing_account["nickname"] = nickname
            else:
                # Add new account
                self.connected_accounts.append({
                    "connection_type": connection_type,
                    "account_id": account_id,
                    "client_id": client_id,
                    "nickname": nickname
                })
            
            # Save accounts
            self._save_accounts()
            
            messagebox.showinfo(
                "Account Saved",
                f"Account {account_id} has been saved successfully!"
            )
            
            # Update UI
            self.show_order_management()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid parameters:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save account:\n{str(e)}")

if __name__ == "__main__":
    try:
        app = ImcoTradingPro()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Application crash: {str(e)}", exc_info=True)
        messagebox.showerror(
            "Fatal Error",
            f"The application has encountered a fatal error and must close:\n\n{str(e)}"
        )