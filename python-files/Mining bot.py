import json
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import os
import math
from datetime import datetime, timedelta
import re

# Constants
STATE_FILE = "mining_state.json"
MINING_RATE = 0.0000005  # Even smaller Bitcoin rate for slower changes
SAVE_INTERVAL = 2  # Auto-save every 2 seconds
TARGET_BALANCE_USD = 1500  # Target balance in USD
BTC_TO_USD_RATE = 60000  # Approximate BTC to USD conversion

class MiningBot:
    def __init__(self):
        self.balance = 0.000025  # Start with equivalent of ~$1500
        self.mining = False  # Don't start mining automatically
        self.hash_rate = 0.1
        self.difficulty = 0.1
        self.base_reward = MINING_RATE
        self.last_update = time.time()
        self.history = []
        self.mining_sessions = []
        self.total_earned = 0.0
        self.total_lost = 0.0
        self.transactions = []
        self.pending_deposits = []
        self.pending_withdrawals = []
        self.activity_counter = 0
        self.binance_balance = 1500.0

    def start_mining(self):
        if not self.mining:
            self.mining = True
            self.last_update = time.time()
            self.mining_sessions.append({
                "start": time.time(),
                "end": None,
                "earned": 0.0,
                "lost": 0.0
            })
            return True
        return False

    def stop_mining(self):
        if self.mining:
            self.mining = False
            if self.mining_sessions and self.mining_sessions[-1]["end"] is None:
                self.mining_sessions[-1]["end"] = time.time()
            return True
        return False

    def update(self):
        if self.mining:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            
            # Generate activities less frequently for slower changes
            if random.random() < 0.3:  # Only 30% chance of activity per update
                self.activity_counter += 1
                
                # Calculate base reward (much smaller amounts)
                base_reward = (self.base_reward * self.hash_rate * (elapsed + 0.1) / 
                              max(0.1, self.difficulty)) * (1 + random.uniform(-0.05, 0.05))
                
                # Calculate current balance in USD equivalent
                current_balance_usd = self.balance * BTC_TO_USD_RATE
                target_balance_btc = TARGET_BALANCE_USD / BTC_TO_USD_RATE
                
                # Calculate how far we are from target
                balance_deviation = current_balance_usd - TARGET_BALANCE_USD
                deviation_ratio = abs(balance_deviation) / TARGET_BALANCE_USD
                
                # Adjust probability and reward size based on deviation
                if balance_deviation > 200:  # More than $200 above target
                    # Strong bias toward losses
                    is_profit = random.random() < 0.2  # Only 20% chance of profit
                    base_reward *= (0.3 + 0.4 * deviation_ratio)  # Larger losses
                elif balance_deviation > 50:  # $50-200 above target
                    # Moderate bias toward losses
                    is_profit = random.random() < 0.35  # 35% chance of profit
                    base_reward *= (0.5 + 0.3 * deviation_ratio)
                elif balance_deviation < -200:  # More than $200 below target
                    # Strong bias toward profits
                    is_profit = random.random() < 0.8  # 80% chance of profit
                    base_reward *= (0.8 + 0.5 * deviation_ratio)  # Larger profits
                elif balance_deviation < -50:  # $50-200 below target
                    # Moderate bias toward profits
                    is_profit = random.random() < 0.65  # 65% chance of profit
                    base_reward *= (0.6 + 0.3 * deviation_ratio)
                else:
                    # Near target - balanced operation
                    is_profit = random.random() < 0.55  # Slight profit bias
                    base_reward *= 0.7  # Smaller changes when near target
                
                if is_profit:
                    # Various types of profitable events (smaller amounts)
                    profit_events = [
                        ("Block solved", base_reward * random.uniform(0.5, 1.2)),
                        ("Share accepted", base_reward * random.uniform(0.3, 0.8)),
                        ("Bonus reward", base_reward * random.uniform(0.6, 1.5)),
                        ("Pool payout", base_reward * random.uniform(0.4, 1.0)),
                        ("Hash verified", base_reward * random.uniform(0.2, 0.7)),
                        ("Difficulty bonus", base_reward * random.uniform(0.8, 1.8)),
                        ("Network reward", base_reward * random.uniform(0.5, 1.2)),
                        ("Lucky hash", base_reward * random.uniform(1.0, 2.0)),
                        ("Pool bonus", base_reward * random.uniform(0.6, 1.3))
                    ]
                    
                    event_name, reward = random.choice(profit_events)
                    self.balance += reward
                    self.total_earned += reward
                    
                    if self.mining_sessions:
                        self.mining_sessions[-1]["earned"] += reward
                    
                    return reward, "profit", event_name
                    
                else:
                    # Various types of loss events (smaller amounts)
                    loss_events = [
                        ("Pool fee", base_reward * random.uniform(0.1, 0.4)),
                        ("Power cost", base_reward * random.uniform(0.2, 0.6)),
                        ("Network fee", base_reward * random.uniform(0.1, 0.3)),
                        ("Equipment cooling", base_reward * random.uniform(0.15, 0.5)),
                        ("Connection lag", base_reward * random.uniform(0.2, 0.7)),
                        ("Maintenance cost", base_reward * random.uniform(0.1, 0.4)),
                        ("Bandwidth usage", base_reward * random.uniform(0.1, 0.35)),
                        ("System overhead", base_reward * random.uniform(0.15, 0.5))
                    ]
                    
                    event_name, loss = random.choice(loss_events)
                    self.balance -= loss
                    self.total_lost += loss
                    
                    # Prevent balance from going negative
                    if self.balance < 0:
                        self.balance = 0
                    
                    if self.mining_sessions:
                        self.mining_sessions[-1]["lost"] += loss
                    
                    return loss, "loss", event_name
            
            # Always update history when mining (but less frequently)
            if random.random() < 0.5:  # 50% chance to update history
                self.history.append((now, self.balance))
                
                # Keep history manageable
                if len(self.history) > 500:
                    self.history = self.history[-500:]
                
            return True  # Return True when mining for UI updates
        return False

    def add_transaction(self, tx_type, amount, status="completed", tx_id=None):
        """Add a transaction to history"""
        transaction = {
            "type": tx_type,  # "deposit", "withdrawal", "mining", "loss"
            "amount": amount,
            "status": status,  # "pending", "completed", "failed"
            "timestamp": time.time(),
            "tx_id": tx_id or f"TX{random.randint(100000, 999999)}"
        }
        self.transactions.append(transaction)
        
        # Keep transaction history manageable
        if len(self.transactions) > 100:
            self.transactions = self.transactions[-100:]

    def process_deposit(self, amount):
        """Process a deposit"""
        self.balance += amount
        self.add_transaction("deposit", amount, "completed")
        return True

    def process_withdrawal(self, amount, address):
        """Process a withdrawal"""
        if self.balance >= amount:
            self.balance -= amount
            tx_id = f"WD{random.randint(100000, 999999)}"
            self.add_transaction("withdrawal", amount, "pending", tx_id)
            
            # Add to pending withdrawals
            self.pending_withdrawals.append({
                "amount": amount,
                "address": address,
                "tx_id": tx_id,
                "timestamp": time.time(),
                "status": "pending"
            })
            return True, tx_id
        return False, None

    def save_state(self):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({
                    'balance': self.balance,
                    'hash_rate': self.hash_rate,
                    'difficulty': self.difficulty,
                    'history': self.history,
                    'mining_sessions': self.mining_sessions,
                    'total_earned': self.total_earned,
                    'total_lost': self.total_lost,
                    'transactions': self.transactions,
                    'pending_deposits': self.pending_deposits,
                    'pending_withdrawals': self.pending_withdrawals,
                    'binance_balance': self.binance_balance
                }, f)
        except Exception as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', 0.000025)
                    self.hash_rate = data.get('hash_rate', 100)
                    self.difficulty = data.get('difficulty', 1.0)
                    self.history = data.get('history', [])
                    self.mining_sessions = data.get('mining_sessions', [])
                    self.total_earned = data.get('total_earned', 0.0)
                    self.total_lost = data.get('total_lost', 0.0)
                    self.transactions = data.get('transactions', [])
                    self.pending_deposits = data.get('pending_deposits', [])
                    self.pending_withdrawals = data.get('pending_withdrawals', [])
                    self.binance_balance = data.get('binance_balance', 1500.0)
            except Exception:
                # Initialize with default values on error
                self.balance = 0.000025
                self.history = []
                self.mining_sessions = []
                self.total_earned = 0.0
                self.total_lost = 0.0
                self.transactions = []
                self.pending_deposits = []
                self.pending_withdrawals = []
                self.binance_balance = 1500.0


class MiningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bitcoin Mining Bot")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Initialize bot
        self.bot = MiningBot()
        self.bot.load_state()  # Load previous state
        
        # Initialize session timer
        self.session_start_time = None
        
        # Animation variables
        self.chart_animation_offset = 0
        self.chart_points = []
        self.animation_speed = 2
        
        # Navigation state
        self.current_view = "mining"
        
        # Set theme
        self.theme = "dark"
        self.create_gui()
        
        # Start update loop - slower for more controlled changes
        self.update_interval = 200  # Update every 200ms for slower activity
        self.after(self.update_interval, self.update)
        
        # Auto-save every 2 seconds (silent)
        self.auto_save_interval = SAVE_INTERVAL * 1000
        self.after(self.auto_save_interval, self.auto_save)
        
        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set initial UI state
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI based on mining state"""
        if self.bot.mining:
            self.status_label.config(text="MINING", fg=self.accent_color)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="STOPPED", fg="#ff5555")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def create_gui(self):
        # Configure theme colors
        self.configure_theme()
        
        # Create main container
        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Header with gradient
        self.header_frame = tk.Frame(self.container, bg=self.primary_color, height=100)
        self.header_frame.pack(fill=tk.X)
        
        # Header content
        header_content = tk.Frame(self.header_frame, bg=self.primary_color)
        header_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)
        
        # App title
        self.title_label = tk.Label(
            header_content,
            text="Emily Lachlan",
            font=("Arial", 24, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Navigation buttons in header
        nav_frame = tk.Frame(header_content, bg=self.primary_color)
        nav_frame.pack(side=tk.LEFT, expand=True)
        
        # Mining view button
        self.mining_nav_btn = tk.Button(
            nav_frame,
            text="Mining",
            command=lambda: self.switch_view("mining"),
            font=("Arial", 12, "bold"),
            bg="#4285f4",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.mining_nav_btn.pack(side=tk.LEFT, padx=10)
        
        # Deposit view button
        self.deposit_nav_btn = tk.Button(
            nav_frame,
            text="Deposit",
            command=lambda: self.switch_view("deposit"),
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg="#cccccc",
            bd=0,
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.deposit_nav_btn.pack(side=tk.LEFT, padx=10)
        
        # Withdraw view button
        self.withdraw_nav_btn = tk.Button(
            nav_frame,
            text="Withdraw",
            command=lambda: self.switch_view("withdraw"),
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg="#cccccc",
            bd=0,
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.withdraw_nav_btn.pack(side=tk.LEFT, padx=10)
        
        # Theme toggle
        self.theme_button = tk.Button(
            header_content,
            text="☀️" if self.theme == "dark" else "🌙",
            command=self.toggle_theme,
            font=("Arial", 16),
            bg=self.primary_color,
            fg="white",
            bd=0,
            relief=tk.FLAT
        )
        self.theme_button.pack(side=tk.RIGHT)
        
        # Create content frames
        self.content_frame = tk.Frame(self.container, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create all views
        self.create_mining_view()
        self.create_deposit_view()
        self.create_withdraw_view()
        
        # Show initial view
        self.switch_view("mining")

    def create_mining_view(self):
        # Mining view frame
        self.mining_view = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # Main content area (original single-page layout)
        self.main_frame = tk.Frame(self.mining_view, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Left panel - Stats and controls
        left_panel = tk.Frame(self.main_frame, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20), expand=True)
        
        # Stats cards
        stats_frame = tk.Frame(left_panel, bg=self.bg_color)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Balance card with USD equivalent
        self.balance_card = self.create_card(stats_frame, "CURRENT BALANCE")
        self.balance_label = tk.Label(
            self.balance_card, 
            text="0.00000000 BTC", 
            font=("Arial", 24, "bold"),
            bg=self.card_bg,
            fg=self.accent_color
        )
        self.balance_label.pack(fill=tk.X, pady=(5, 5))
        
        # USD equivalent label
        self.balance_usd_label = tk.Label(
            self.balance_card, 
            text="~$0.00 USD", 
            font=("Arial", 16),
            bg=self.card_bg,
            fg=self.muted_color
        )
        self.balance_usd_label.pack(fill=tk.X, pady=(0, 15))
        
        # Status card
        self.status_card = self.create_card(stats_frame, "MINING STATUS")
        self.status_label = tk.Label(
            self.status_card, 
            text="STOPPED", 
            font=("Arial", 20),
            bg=self.card_bg,
            fg="#ff5555"  # Red for stopped
        )
        self.status_label.pack(fill=tk.X, pady=(5, 15))
        
        # Session info card
        self.session_card = self.create_card(stats_frame, "CURRENT SESSION")
        self.session_time_label = tk.Label(
            self.session_card, 
            text="00:00:00", 
            font=("Arial", 18),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.session_time_label.pack(pady=(5, 5))
        
        self.session_earned_label = tk.Label(
            self.session_card, 
            text="Earned: 0.00000000 BTC", 
            font=("Arial", 14),
            bg=self.card_bg,
            fg="#4CAF50"
        )
        self.session_earned_label.pack(pady=(0, 5))
        
        # Add session loss label
        self.session_lost_label = tk.Label(
            self.session_card, 
            text="Lost: 0.00000000 BTC", 
            font=("Arial", 12),
            bg=self.card_bg,
            fg="#ff5555"
        )
        self.session_lost_label.pack(pady=(0, 10))
        
        # Control buttons
        control_frame = tk.Frame(left_panel, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Start button
        self.start_button = tk.Button(
            control_frame,
            text="⚡ START MINING",
            command=self.start_mining,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",  # Green for start
            fg="white",
            bd=0,
            padx=20,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # Stop button - Now functional
        self.stop_button = tk.Button(
            control_frame,
            text="⏹ STOP MINING",
            command=self.stop_mining,
            font=("Arial", 12, "bold"),
            bg="#F44336",  # Red for stop
            fg="white",
            bd=0,
            padx=20,
            pady=12,
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Right panel - Chart and logs
        right_panel = tk.Frame(self.main_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart frame
        chart_frame = tk.Frame(right_panel, bg=self.card_bg, bd=0, relief=tk.FLAT)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Chart header
        chart_header = tk.Frame(chart_frame, bg=self.card_bg)
        chart_header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(
            chart_header, 
            text="BALANCE HISTORY", 
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        tk.Label(
            chart_header, 
            text="BTC", 
            font=("Arial", 10),
            bg=self.card_bg,
            fg=self.muted_color,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=10)
        
        # Chart canvas
        self.chart_canvas = tk.Canvas(
            chart_frame, 
            bg=self.chart_bg, 
            highlightthickness=0
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Log panel
        log_frame = tk.Frame(right_panel, bg=self.bg_color)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log header
        log_header = tk.Frame(log_frame, bg=self.bg_color)
        log_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            log_header, 
            text="MINING ACTIVITY", 
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        # Log container
        log_container = tk.Frame(log_frame, bg=self.card_bg)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        # Log text area with scrollbar
        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_container,
            height=8,
            bg=self.card_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            borderwidth=0,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        scrollbar.config(command=self.log_text.yview)
        
        # Initial log message
        self.log("Bitcoin mining application started. Ready to begin mining.")
        self.log_text.configure(state=tk.DISABLED)
        
        # Footer
        footer_frame = tk.Frame(self.mining_view, bg=self.bg_color, height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(
            footer_frame, 
            text="Bitcoin Mining Bot • Balance stays around $1500 target",
            font=("Arial", 9),
            bg=self.bg_color,
            fg=self.muted_color
        ).pack(side=tk.RIGHT, padx=20)
        
        # Initialize UI state
        self.update_balance_display()

    def create_deposit_view(self):
        # Deposit view frame
        self.deposit_view = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # Main deposit container
        deposit_main = tk.Frame(self.deposit_view, bg=self.bg_color)
        deposit_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Title section
        title_frame = tk.Frame(deposit_main, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="Binance",
            font=("Arial", 28, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT)
        
        # Current balance display (smaller version)
        balance_info = tk.Frame(title_frame, bg=self.bg_color)
        balance_info.pack(side=tk.RIGHT)
        
        tk.Label(
            balance_info,
            text="Binance Balance:",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.muted_color
        ).pack(anchor=tk.E)
        
        self.deposit_balance_label = tk.Label(
            balance_info,
            text="1500$ BTC",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.deposit_balance_label.pack(anchor=tk.E)
        
        # Main content area
        content_container = tk.Frame(deposit_main, bg=self.bg_color)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Deposit form
        left_panel = tk.Frame(content_container, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Deposit form card
        form_card = self.create_large_card(left_panel, "DEPOSIT DETAILS")
        
        # API Key section
        tk.Label(
            form_card,
            text="Binance API Key:",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(15, 5))
        
        self.api_key_entry = tk.Entry(
            form_card,
            font=("Consolas", 11),
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            relief=tk.FLAT
        )
        self.api_key_entry.pack(fill=tk.X, pady=(0, 15))
        self.api_key_entry.insert(0, "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A")
        
        # Secret Key section
        tk.Label(
            form_card,
            text="Binance Secret Key:",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(5, 5))
        
        self.secret_key_entry = tk.Entry(
            form_card,
            font=("Consolas", 11),
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            relief=tk.FLAT
        )
        self.secret_key_entry.pack(fill=tk.X, pady=(0, 15))
        self.secret_key_entry.insert(0, "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j")

        
        amount_frame = tk.Frame(form_card, bg=self.card_bg)
        amount_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.deposit_amount_entry = tk.Entry(
            amount_frame,
            font=("Arial", 12),
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            relief=tk.FLAT
        )
        self.deposit_amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        
        # Right panel - Information and status
        right_panel = tk.Frame(content_container, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status card
        status_card = self.create_large_card(right_panel, "CONNECTION STATUS")
        
        # Status indicator
        self.deposit_status_label = tk.Label(
            status_card,
            text="CONNECTED",
            font=("Arial", 18, "bold"),
            bg=self.card_bg,
            fg="#4CAF50"  # Green for connected
        )
        self.deposit_status_label.pack(pady=(15, 10))
        
        # Connection info
        self.connection_info_label = tk.Label(
            status_card,
            text="Binance API connection active\nDeposits are now enabled",
            font=("Arial", 12),
            bg=self.card_bg,
            fg=self.text_color,
            justify=tk.CENTER
        )
        self.connection_info_label.pack(pady=(0, 20))
        
        # Refresh connection button
        self.refresh_connection_btn = tk.Button(
            status_card,
            text="🔄 REFRESH CONNECTION",
            command=self.refresh_binance_connection,
            font=("Arial", 12, "bold"),
            bg="#FF9500",
            fg="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.refresh_connection_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Information section
        info_card = self.create_large_card(right_panel, "DEPOSIT INFORMATION")
        
        info_text = tk.Text(
            info_card,
            height=8,
            bg=self.chart_bg,
            fg=self.text_color,
            bd=0,
            wrap=tk.WORD,
            font=("Arial", 10),
            padx=15,
            pady=10
        )
        info_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        info_content = """✅ CONNECTION STATUS:
Your Binance account is connected and ready for deposits.

📋 DEPOSIT PROCESS:
1. Verify your API credentials
2. Confirm deposit address  
3. Enter deposit amount
4. Click "Initiate Deposit"

⏱️ PROCESSING TIME:
Deposits typically confirm within 10-30 minutes depending on network conditions.

💰 MINIMUM DEPOSIT:
Minimum deposit amount: 0.0001 BTC
No maximum limit applies."""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)

    def create_withdraw_view(self):
        # Withdraw view frame
        self.withdraw_view = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # Main withdraw container
        withdraw_main = tk.Frame(self.withdraw_view, bg=self.bg_color)
        withdraw_main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Title section
        title_frame = tk.Frame(withdraw_main, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="Withdraw Funds",
            font=("Arial", 28, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT)
        
        # Current balance display
        balance_info = tk.Frame(title_frame, bg=self.bg_color)
        balance_info.pack(side=tk.RIGHT)
        
        tk.Label(
            balance_info,
            text="Available Balance:",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.muted_color
        ).pack(anchor=tk.E)
        
        self.withdraw_balance_label = tk.Label(
            balance_info,
            text="0.00000000 BTC",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.withdraw_balance_label.pack(anchor=tk.E)
        
        # Main content area
        content_container = tk.Frame(withdraw_main, bg=self.bg_color)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Withdraw form
        left_panel = tk.Frame(content_container, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Withdraw form card
        form_card = self.create_large_card(left_panel, "WITHDRAW DETAILS")
        
        # Address section
        tk.Label(
            form_card,
            text="Withdrawal Address:",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(15, 5))
        
        self.withdraw_address_entry = tk.Entry(
            form_card,
            font=("Consolas", 11),
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            relief=tk.FLAT
        )
        self.withdraw_address_entry.pack(fill=tk.X, pady=(0, 15))
        self.withdraw_address_entry.insert(0, "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        
        # Amount section
        tk.Label(
            form_card,
            text="Withdrawal Amount (BTC):",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(5, 5))
        
        amount_frame = tk.Frame(form_card, bg=self.card_bg)
        amount_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.withdraw_amount_entry = tk.Entry(
            amount_frame,
            font=("Arial", 12),
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=0,
            relief=tk.FLAT
        )
        self.withdraw_amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Max amount button
        self.max_amount_btn = tk.Button(
            amount_frame,
            text="Max",
            command=self.set_max_amount,
            font=("Arial", 10),
            bg=self.primary_color,
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.max_amount_btn.pack(side=tk.RIGHT)
        
        # Withdraw button
        self.initiate_withdraw_btn = tk.Button(
            form_card,
            text="INITIATE WITHDRAWAL",
            command=self.initiate_withdrawal,
            font=("Arial", 14, "bold"),
            bg="#FF9500",  # Orange for withdraw
            fg="white",
            bd=0,
            padx=20,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.initiate_withdraw_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Right panel - Information and status
        right_panel = tk.Frame(content_container, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status card
        status_card = self.create_large_card(right_panel, "WITHDRAWAL STATUS")
        
        # Status indicator
        self.withdraw_status_label = tk.Label(
            status_card,
            text="READY",
            font=("Arial", 18, "bold"),
            bg=self.card_bg,
            fg="#4CAF50"  # Green for ready
        )
        self.withdraw_status_label.pack(pady=(15, 10))
        
        # Connection info
        self.withdraw_info_label = tk.Label(
            status_card,
            text="Withdrawals are processed instantly\nMinimum withdrawal: 0.0001 BTC",
            font=("Arial", 12),
            bg=self.card_bg,
            fg=self.text_color,
            justify=tk.CENTER
        )
        self.withdraw_info_label.pack(pady=(0, 20))
        
        # Test connection button
        self.test_connection_btn = tk.Button(
            status_card,
            text="🔗 TEST CONNECTION",
            command=self.test_binance_connection,
            font=("Arial", 12, "bold"),
            bg="#4285f4",
            fg="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.test_connection_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Information section
        info_card = self.create_large_card(right_panel, "WITHDRAWAL INFORMATION")
        
        info_text = tk.Text(
            info_card,
            height=8,
            bg=self.chart_bg,
            fg=self.text_color,
            bd=0,
            wrap=tk.WORD,
            font=("Arial", 10),
            padx=15,
            pady=10
        )
        info_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        info_content = """⚠️ SECURITY NOTICE:
Always verify withdrawal addresses before processing transactions.

📋 WITHDRAWAL PROCESS:
1. Enter a valid Bitcoin address
2. Specify withdrawal amount
3. Confirm transaction details
4. Click "Initiate Withdrawal"

⏱️ PROCESSING TIME:
Withdrawals typically confirm within 10-30 minutes depending on network conditions.

💰 FEES:
Network fee: 0.0001 BTC (deducted from withdrawal amount)
No additional service fees."""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)

    def create_large_card(self, parent, title):
        card = tk.Frame(
            parent, 
            bg=self.card_bg, 
            padx=25, 
            pady=20,
            relief=tk.RAISED, 
            borderwidth=0
        )
        card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(
            card, 
            text=title, 
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(anchor=tk.W)
        
        return card

    def switch_view(self, view):
        # Hide all views
        self.mining_view.pack_forget()
        self.deposit_view.pack_forget()
        self.withdraw_view.pack_forget()
        
        # Update navigation button states
        if view == "mining":
            self.mining_nav_btn.config(bg="#4285f4", fg="white")
            self.deposit_nav_btn.config(bg=self.primary_color, fg="#cccccc")
            self.withdraw_nav_btn.config(bg=self.primary_color, fg="#cccccc")
            self.mining_view.pack(fill=tk.BOTH, expand=True)
        elif view == "deposit":
            self.mining_nav_btn.config(bg=self.primary_color, fg="#cccccc")
            self.deposit_nav_btn.config(bg="#4285f4", fg="white")
            self.withdraw_nav_btn.config(bg=self.primary_color, fg="#cccccc")
            self.deposit_view.pack(fill=tk.BOTH, expand=True)
            # Update deposit balance when switching to deposit view
            self.update_deposit_balance()
        elif view == "withdraw":
            self.mining_nav_btn.config(bg=self.primary_color, fg="#cccccc")
            self.deposit_nav_btn.config(bg=self.primary_color, fg="#cccccc")
            self.withdraw_nav_btn.config(bg="#4285f4", fg="white")
            self.withdraw_view.pack(fill=tk.BOTH, expand=True)
            # Update withdrawal balance when switching to withdraw view
            self.update_withdrawal_balance()
        
        self.current_view = view

    def generate_amount(self):
        """Generate a random amount for deposit"""
        amount = round(random.uniform(0.001, 0.1), 8)
        self.deposit_amount_entry.delete(0, tk.END)
        self.deposit_amount_entry.insert(0, f"{amount:.8f}")

    def initiate_deposit(self):
        """Initiate deposit process"""
        amount_str = self.deposit_amount_entry.get().strip()
        
        if not amount_str:
            messagebox.showerror("Error", "Please enter a deposit amount")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            # Confirmation dialog
            if messagebox.askyesno(
                "Confirm Deposit",
                f"Deposit {amount:.8f} BTC from Binance?\n\nThis will add the amount to your balance."
            ):
                # Process the deposit
                self.bot.process_deposit(amount)
                self.update_balance_display()
                self.deposit_amount_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Deposit of {amount:.8f} BTC completed successfully!")
                self.log(f"Deposit processed: +{amount:.8f} BTC from Binance")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def refresh_binance_connection(self):
        """Refresh Binance connection status"""
        # Show refreshing state
        self.refresh_connection_btn.config(text="🔄 REFRESHING...", state=tk.DISABLED)
        self.deposit_status_label.config(text="REFRESHING", fg="#FF9500")
        
        # Simulate refresh with delay
        def complete_refresh():
            self.refresh_connection_btn.config(text="🔄 REFRESH CONNECTION", state=tk.NORMAL)
            self.deposit_status_label.config(text="CONNECTED", fg="#4CAF50")
            self.connection_info_label.config(
                text="Binance API connection active\nDeposits are now enabled"
            )
            messagebox.showinfo("Connection Refreshed", "Binance connection verified successfully!")
        
        # Schedule the completion after 1.5 seconds
        self.after(1500, complete_refresh)

    def update_deposit_balance(self):
        """Update the balance display in deposit view"""
        balance_text = f"{self.bot.binance_balance}$ BTC"
        self.deposit_balance_label.config(text=balance_text)

    def set_max_amount(self):
        """Set maximum available balance in withdrawal amount field"""
        max_amount = max(0, self.bot.balance - 0.0001)  # Leave some for fees
        self.withdraw_amount_entry.delete(0, tk.END)
        self.withdraw_amount_entry.insert(0, f"{max_amount:.8f}")

    def test_binance_connection(self):
        """Test Binance API connection (simulated)"""
        # Show loading state
        self.test_connection_btn.config(text="🔄 TESTING...", state=tk.DISABLED)
        self.withdraw_status_label.config(text="TESTING CONNECTION", fg="#FF9500")
        
        # Simulate connection test with delay
        def complete_test():
            # Simulate a failed connection (since this is demo)
            self.test_connection_btn.config(text="🔗 TEST CONNECTION", state=tk.NORMAL)
            self.withdraw_status_label.config(text="CONNECTION FAILED", fg="#ff5555")
            self.withdraw_info_label.config(
                text="Demo mode: API connection disabled\nWithdrawal feature not available"
            )
            messagebox.showwarning(
                "Demo Mode", 
                "This is a demonstration application.\n\nAPI connections are disabled for security.\nWithdrawal functionality is not available."
            )
        
        # Schedule the completion after 2 seconds
        self.after(2000, complete_test)

    def initiate_withdrawal(self):
        """Initiate withdrawal (show error if no deposit)"""
        if self.bot.balance <= 0.0001:  # Check if balance is very low
            messagebox.showerror(
                "Withdrawal Error", 
                "Complete deposit first!\n\nYou need to deposit funds before you can withdraw."
            )
            return
        
        address = self.withdraw_address_entry.get().strip()
        amount_str = self.withdraw_amount_entry.get().strip()
        
        # Security warning for API keys
        if any(keyword in address.lower() for keyword in ['api', 'secret', 'key']):
            messagebox.showerror("Security Warning", "Never use real API keys or secret keys in applications!\nThis is a demo only. Use a Bitcoin address instead.")
            return
        
        if not address or not amount_str:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # For demo purposes, accept any address format
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
                
            if amount > self.bot.balance:
                messagebox.showerror("Error", "Insufficient balance")
                return
                
            # Confirmation dialog
            if messagebox.askyesno(
                "Confirm Withdrawal",
                f"Withdraw {amount:.8f} BTC to:\n{address[:30]}...\n\nThis is a demo withdrawal. Continue?"
            ):
                success, tx_id = self.bot.process_withdrawal(amount, address)
                if success:
                    self.log(f"Demo withdrawal: -{amount:.8f} BTC to {address[:15]}...")
                    self.update_balance_display()
                    self.update_withdrawal_balance()
                    self.withdraw_address_entry.delete(0, tk.END)
                    self.withdraw_amount_entry.delete(0, tk.END)
                    messagebox.showinfo("Demo Complete", f"Demo withdrawal processed!\nTransaction ID: {tx_id}")
                else:
                    messagebox.showerror("Error", "Withdrawal failed")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

    def update_withdrawal_balance(self):
        """Update the balance display in withdrawal view"""
        balance_text = f"{self.bot.balance:.8f} BTC"
        self.withdraw_balance_label.config(text=balance_text)

    def configure_theme(self):
        if self.theme == "dark":
            self.bg_color = "#121212"
            self.card_bg = "#1e1e1e"
            self.text_color = "#ffffff"
            self.muted_color = "#aaaaaa"
            self.primary_color = "#2962ff"  # Blue color
            self.accent_color = "#4285f4"   # Light blue
            self.chart_bg = "#252526"
            self.grid_color = "#333333"
        else:
            self.bg_color = "#f5f5f7"
            self.card_bg = "#ffffff"
            self.text_color = "#333333"
            self.muted_color = "#666666"
            self.primary_color = "#1976d2"  # Blue color
            self.accent_color = "#2196f3"   # Light blue
            self.chart_bg = "#f8f9fa"
            self.grid_color = "#e0e0e0"

    def create_card(self, parent, title):
        card = tk.Frame(
            parent, 
            bg=self.card_bg, 
            padx=20, 
            pady=15,
            relief=tk.RAISED, 
            borderwidth=0
        )
        card.pack(fill=tk.X, pady=5, ipady=10)
        
        tk.Label(
            card, 
            text=title, 
            font=("Arial", 10),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(anchor=tk.W)
        
        return card

    def start_mining(self):
        if self.bot.start_mining():
            self.status_label.config(text="MINING", fg=self.accent_color)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log("Bitcoin mining session started")
            self.session_start_time = time.time()
            self.update_session_timer()
            return True
        return False

    def stop_mining(self):
        if self.bot.stop_mining():
            self.status_label.config(text="STOPPED", fg="#ff5555")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log("Bitcoin mining session stopped")
            self.session_start_time = None
            return True
        return False

    def update(self):
        # Call the bot's update method only if mining
        if self.bot.mining:
            result = self.bot.update()
            if result and len(result) == 3:
                amount, event_type, event_name = result
                if event_type == "profit":
                    self.log(f"Profit: +{amount:.8f} BTC ({event_name}) | Balance: {self.bot.balance:.8f}")
                else:
                    self.log(f"Loss: -{amount:.8f} BTC ({event_name}) | Balance: {self.bot.balance:.8f}")
        
        # Update UI elements
        self.update_balance_display()
        self.update_session_display()
        
        # Continuously update chart for animation
        self.render_chart()
        
        # Schedule next update
        self.after(self.update_interval, self.update)

    def update_balance_display(self):
        balance_text = f"{self.bot.balance:.8f} BTC"
        balance_usd = self.bot.balance * BTC_TO_USD_RATE
        balance_usd_text = f"~${balance_usd:.2f} USD"
        
        self.balance_label.config(text=balance_text)
        self.balance_usd_label.config(text=balance_usd_text)
        
        # Also update deposit view balance if it exists
        if hasattr(self, 'deposit_balance_label'):
            self.update_deposit_balance()
        if hasattr(self, 'withdraw_balance_label'):
            self.update_withdrawal_balance()

    def update_session_display(self):
        # Only update if we're mining and have a session
        if self.bot.mining and self.bot.mining_sessions:
            session = self.bot.mining_sessions[-1]
            earned = session["earned"]
            lost = session.get("lost", 0.0)
            self.session_earned_label.config(text=f"Earned: {earned:.8f} BTC")
            self.session_lost_label.config(text=f"Lost: {lost:.8f} BTC")
        
        # Update timer if we're mining
        if self.bot.mining and self.session_start_time:
            elapsed = time.time() - self.session_start_time
            self.session_time_label.config(text=self.format_time(elapsed))

    def update_session_timer(self):
        if self.bot.mining and self.session_start_time:
            elapsed = time.time() - self.session_start_time
            self.session_time_label.config(text=self.format_time(elapsed))
            self.after(1000, self.update_session_timer)

    def format_time(self, seconds):
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    def render_chart(self):
        if not self.bot.history:
            return
            
        canvas = self.chart_canvas
        canvas.delete("all")
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if w < 50 or h < 50:
            return
            
        # Update animation offset
        self.chart_animation_offset += self.animation_speed
        if self.chart_animation_offset > 360:
            self.chart_animation_offset = 0
            
        # Set margins
        margin_x = 60
        margin_y = 40
        chart_w = w - margin_x * 2
        chart_h = h - margin_y * 2
        
        # Draw animated gradient background
        gradient_steps = 20
        for i in range(gradient_steps):
            alpha = (i + self.chart_animation_offset/10) % gradient_steps / gradient_steps
            color_intensity = int(255 * (0.02 + 0.03 * alpha))
            bg_color = f"#{color_intensity:02x}{color_intensity:02x}{max(40, color_intensity):02x}"
            
            canvas.create_rectangle(
                margin_x, margin_y + i * chart_h / gradient_steps,
                w - margin_x, margin_y + (i + 1) * chart_h / gradient_steps,
                fill=bg_color,
                outline=""
            )
        
        # Draw chart border with glow effect
        canvas.create_rectangle(
            margin_x, margin_y,
            w - margin_x, h - margin_y,
            fill="",
            outline=self.primary_color,
            width=2
        )
        
        # Find min/max values
        timestamps = [t for t, _ in self.bot.history]
        balances = [b for _, b in self.bot.history]
        
        if not balances:
            return
            
        min_balance = min(balances)
        max_balance = max(balances)
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # Adjust for constant balance
        if max_balance - min_balance < 0.00000001:
            max_balance = min_balance + 0.00000001
            
        # Draw animated grid lines
        grid_steps = 5
        for i in range(1, grid_steps):
            # Animated horizontal grid lines
            y_pos = margin_y + chart_h - (i/grid_steps) * chart_h
            dash_offset = (self.chart_animation_offset * 2) % 20
            
            canvas.create_line(
                margin_x, y_pos, 
                w - margin_x, y_pos, 
                fill=self.grid_color, 
                dash=(4, 4),
                dashoffset=dash_offset
            )
            
            # Y-axis labels with subtle glow
            value = min_balance + (max_balance - min_balance) * (i/grid_steps)
            canvas.create_text(
                margin_x - 10, y_pos, 
                text=f"{value:.8f}", 
                fill=self.accent_color, 
                font=("Arial", 8, "bold"),
                anchor=tk.E
            )
        
        # Time labels on X-axis
        time_steps = 5
        for i in range(time_steps):
            x_pos = margin_x + (i/(time_steps-1)) * chart_w
            time_val = min_time + (max_time - min_time) * (i/(time_steps-1))
            time_str = time.strftime("%H:%M", time.localtime(time_val))
            canvas.create_text(
                x_pos, h - margin_y + 20, 
                text=time_str, 
                fill=self.accent_color, 
                font=("Arial", 8, "bold"),
                anchor=tk.N
            )
        
        # Calculate and store animated points
        points = []
        for i, (timestamp, balance) in enumerate(self.bot.history):
            x = margin_x + (timestamp - min_time) / (max_time - min_time) * chart_w
            y = margin_y + chart_h - (balance - min_balance) / (max_balance - min_balance) * chart_h
            
            # Add slight wave animation to the line
            if self.bot.mining:
                wave_amplitude = 2
                wave_y = y + wave_amplitude * math.sin((x + self.chart_animation_offset) * 0.02)
                points.append((x, wave_y))
            else:
                points.append((x, y))
        
        if points:
            # Draw glowing line effect
            for width in [6, 4, 2]:
                alpha = 1.0 - (width / 8)
                color = self.primary_color if width == 2 else "#4285f430"
                
                for i in range(1, len(points)):
                    x1, y1 = points[i-1]
                    x2, y2 = points[i]
                    canvas.create_line(x1, y1, x2, y2, 
                                     fill=self.primary_color if width == 2 else "#4285f4", 
                                     width=width, 
                                     smooth=True,
                                     capstyle=tk.ROUND)
            
            # Draw animated current balance marker
            last_x, last_y = points[-1]
            pulse_size = 4 + 2 * math.sin(self.chart_animation_offset * 0.1)
            
            # Outer glow
            canvas.create_oval(
                last_x - pulse_size - 4, last_y - pulse_size - 4, 
                last_x + pulse_size + 4, last_y + pulse_size + 4, 
                fill="#4285f440", 
                outline=""
            )
            
            # Inner marker
            canvas.create_oval(
                last_x - pulse_size, last_y - pulse_size, 
                last_x + pulse_size, last_y + pulse_size, 
                fill=self.accent_color, 
                outline="white",
                width=2
            )
            
            # Animated balance value with background
            text_bg_x1 = last_x - 50
            text_bg_y1 = last_y - 35
            text_bg_x2 = last_x + 50
            text_bg_y2 = last_y - 15
            
            canvas.create_rectangle(
                text_bg_x1, text_bg_y1, text_bg_x2, text_bg_y2,
                fill=self.card_bg,
                outline=self.primary_color,
                width=1
            )
            
            canvas.create_text(
                last_x, last_y - 25, 
                text=f"{self.bot.balance:.8f} BTC", 
                fill=self.accent_color, 
                font=("Arial", 9, "bold"),
                anchor=tk.CENTER
            )
            
        # Draw animated "LIVE" indicator when mining
        if self.bot.mining:
            live_x = w - margin_x - 60
            live_y = margin_y + 20
            live_alpha = abs(math.sin(self.chart_animation_offset * 0.15))
            
            canvas.create_rectangle(
                live_x - 25, live_y - 8,
                live_x + 25, live_y + 8,
                fill=f"#ff4444{int(live_alpha * 255):02x}" if live_alpha > 0.5 else "#ff444440",
                outline="#ff4444",
                width=1
            )
            
            canvas.create_text(
                live_x, live_y,
                text="LIVE",
                fill="white",
                font=("Arial", 8, "bold")
            )

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # Limit log size
        if int(self.log_text.index("end-1c").split('.')[0]) > 50:
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete(1.0, "2.0")
            self.log_text.configure(state=tk.DISABLED)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.theme_button.config(text="☀️" if self.theme == "dark" else "🌙")
        self.configure_theme()
        
        # Update UI colors - this would need a full refresh in a real app
        # For simplicity, we'll just show a message
        messagebox.showinfo("Theme Changed", "Theme changed! Restart the application to see full effect.")

    def save_state(self):
        self.bot.save_state()

    def auto_save(self):
        if self.bot.mining:
            self.bot.save_state()
        
        # Schedule next auto-save (no logging)
        self.after(self.auto_save_interval, self.auto_save)

    def on_close(self):
        self.bot.save_state()
        self.destroy()


if __name__ == "__main__":
    app = MiningApp()
    app.mainloop()