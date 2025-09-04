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
MINING_RATE = 0.00000007  # Bitcoin rate (much smaller numbers)
SAVE_INTERVAL = 2  # Auto-save every 2 seconds

class MiningBot:
    def __init__(self):
        self.balance = 0.0
        self.mining = False
        self.hash_rate = 100  # H/s
        self.difficulty = 1.0
        self.base_reward = MINING_RATE
        self.last_update = time.time()
        self.history = []
        self.mining_sessions = []
        self.total_earned = 0.0
        self.transactions = []  # New: transaction history
        self.pending_deposits = []  # New: pending deposits
        self.pending_withdrawals = []  # New: pending withdrawals
        # Reset all values to 0 - don't load previous state
        # self.load_state()

    def start_mining(self):
        if not self.mining:
            self.mining = True
            self.last_update = time.time()
            self.mining_sessions.append({
                "start": time.time(),
                "end": None,
                "earned": 0.0
            })
            return True
        return False

    def stop_mining(self):
        if self.mining:
            self.mining = False
            if self.mining_sessions:
                self.mining_sessions[-1]["end"] = time.time()
            return True
        return False

    def update(self):
        if self.mining:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            
            # Calculate earnings with realistic fluctuation
            reward = (self.base_reward * self.hash_rate * elapsed / 
                     max(0.1, self.difficulty)) * (1 + random.uniform(-0.15, 0.15))
            
            self.balance += reward
            self.total_earned += reward
            self.history.append((now, self.balance))
            
            # Update current session
            if self.mining_sessions:
                self.mining_sessions[-1]["earned"] += reward
            
            # Keep history manageable
            if len(self.history) > 500:
                self.history = self.history[-500:]
                
            return reward
        return 0.0

    def add_transaction(self, tx_type, amount, status="completed", tx_id=None):
        """Add a transaction to history"""
        transaction = {
            "type": tx_type,  # "deposit", "withdrawal", "mining"
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
                    'transactions': self.transactions,
                    'pending_deposits': self.pending_deposits,
                    'pending_withdrawals': self.pending_withdrawals
                }, f)
        except Exception as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', 0.0)
                    self.hash_rate = data.get('hash_rate', 100)
                    self.difficulty = data.get('difficulty', 1.0)
                    self.history = data.get('history', [])
                    self.mining_sessions = data.get('mining_sessions', [])
                    self.total_earned = data.get('total_earned', 0.0)
                    self.transactions = data.get('transactions', [])
                    self.pending_deposits = data.get('pending_deposits', [])
                    self.pending_withdrawals = data.get('pending_withdrawals', [])
            except Exception:
                # Initialize with default values on error
                self.balance = 0.0
                self.history = []
                self.mining_sessions = []
                self.total_earned = 0.0
                self.transactions = []
                self.pending_deposits = []
                self.pending_withdrawals = []


class MiningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Mining Bot")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Initialize bot
        self.bot = MiningBot()
        
        # Initialize session timer
        self.session_start_time = None
        
        # Animation variables
        self.chart_animation_offset = 0
        self.chart_points = []
        self.animation_speed = 2
        
        # Navigation state
        self.current_view = "mining"  # "mining" or "deposit"
        
        # Set theme
        self.theme = "dark"
        self.create_gui()
        
        # Start update loop
        self.update_interval = 500  # ms
        self.after(self.update_interval, self.update)
        
        # Auto-save every 2 seconds
        self.auto_save_interval = SAVE_INTERVAL * 1000  # ms
        self.after(self.auto_save_interval, self.auto_save)
        
        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_gui(self):
        # Configure modern theme colors
        self.configure_theme()
        
        # Create main container with gradient effect
        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Modern header with glassmorphism effect
        self.header_frame = tk.Frame(self.container, bg=self.header_color, height=80)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        # Header content with improved spacing
        header_content = tk.Frame(self.header_frame, bg=self.header_color)
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # Modern app branding
        branding_frame = tk.Frame(header_content, bg=self.header_color)
        branding_frame.pack(side=tk.LEFT)
        
        # App logo/icon (using Unicode symbol)
        logo_label = tk.Label(
            branding_frame,
            text="₿",
            font=("Arial", 32, "bold"),
            bg=self.header_color,
            fg=self.accent_color
        )
        logo_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # App title with modern typography
        title_frame = tk.Frame(branding_frame, bg=self.header_color)
        title_frame.pack(side=tk.LEFT)
        
        self.title_label = tk.Label(
            title_frame,
            text="Username - flex2016",
            font=("Segoe UI", 20, "bold"),
            bg=self.header_color,
            fg=self.text_color
        )
        self.title_label.pack(anchor=tk.W)
        
        self.subtitle_label = tk.Label(
            title_frame,
            text="TXC Mining Platform",
            font=("Segoe UI", 10),
            bg=self.header_color,
            fg=self.muted_color
        )
        self.subtitle_label.pack(anchor=tk.W)
        
        # Modern navigation with pill-shaped buttons
        nav_frame = tk.Frame(header_content, bg=self.header_color)
        nav_frame.pack(expand=True)
        
        nav_container = tk.Frame(nav_frame, bg=self.nav_bg, relief=tk.FLAT)
        nav_container.pack()
        
        # Mining view button with modern styling
        self.mining_nav_btn = tk.Button(
            nav_container,
            text="Mining Dashboard",
            command=lambda: self.switch_view("mining"),
            font=("Segoe UI", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            bd=0,
            padx=25,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.mining_nav_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Deposit view button - FIXED: using nav_bg instead of "transparent"
        self.deposit_nav_btn = tk.Button(
            nav_container,
            text="Exchange Connect",
            command=lambda: self.switch_view("deposit"),
            font=("Segoe UI", 11),
            bg=self.nav_bg,  # Changed from "transparent" to self.nav_bg
            fg=self.muted_color,
            bd=0,
            padx=25,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.deposit_nav_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Status indicator and controls
        controls_frame = tk.Frame(header_content, bg=self.header_color)
        controls_frame.pack(side=tk.RIGHT)
        
        # Live status indicator
        self.status_indicator = tk.Frame(controls_frame, bg=self.header_color)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 20))
        
        self.status_dot = tk.Label(
            self.status_indicator,
            text="●",
            font=("Arial", 16),
            bg=self.header_color,
            fg="#ff4757"  # Red for stopped
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_text = tk.Label(
            self.status_indicator,
            text="OFFLINE",
            font=("Segoe UI", 10, "bold"),
            bg=self.header_color,
            fg=self.muted_color
        )
        self.status_text.pack(side=tk.LEFT)
        
        # Theme toggle with modern design
        self.theme_button = tk.Button(
            controls_frame,
            text="◐",
            command=self.toggle_theme,
            font=("Arial", 18),
            bg=self.button_bg,
            fg=self.text_color,
            bd=0,
            width=3,
            height=1,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.theme_button.pack(side=tk.RIGHT)
        
        # Create content frames
        self.content_frame = tk.Frame(self.container, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create both views
        self.create_mining_view()
        self.create_deposit_view()
        
        # Show initial view
        self.switch_view("mining")

    def create_mining_view(self):
        # Mining view frame with improved layout
        self.mining_view = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # Main content with modern spacing
        self.main_frame = tk.Frame(self.mining_view, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Top stats row - modern card layout
        stats_row = tk.Frame(self.main_frame, bg=self.bg_color)
        stats_row.pack(fill=tk.X, pady=(0, 25))
        
        # Balance card with gradient effect
        self.balance_card = self.create_modern_card(stats_row, width_weight=2)
        self.balance_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        balance_header = tk.Frame(self.balance_card, bg=self.card_bg)
        balance_header.pack(fill=tk.X, padx=25, pady=(20, 10))
        
        tk.Label(
            balance_header,
            text="TOTAL BALANCE",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(side=tk.LEFT)
        
        tk.Label(
            balance_header,
            text="TXC",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.accent_color
        ).pack(side=tk.RIGHT)
        
        self.balance_label = tk.Label(
            self.balance_card,
            text="0.00000000 TXC",
            font=("JetBrains Mono", 28, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.balance_label.pack(padx=25, pady=(0, 20))
        
        # Hashrate card
        self.hashrate_card = self.create_modern_card(stats_row, width_weight=1)
        self.hashrate_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(
            self.hashrate_card,
            text="HASHRATE",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(pady=(20, 5))
        
        tk.Label(
            self.hashrate_card,
            text="100 H/s",
            font=("Segoe UI", 18, "bold"),
            bg=self.card_bg,
            fg=self.accent_color
        ).pack(pady=(0, 20))
        
        # Earnings card
        self.earnings_card = self.create_modern_card(stats_row, width_weight=1)
        self.earnings_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            self.earnings_card,
            text="SESSION EARNED",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(pady=(20, 5))
        
        self.session_earned_label = tk.Label(
            self.earnings_card,
            text="0.00000000 TXC",
            font=("Segoe UI", 16, "bold"),
            bg=self.card_bg,
            fg=self.success_color
        )
        self.session_earned_label.pack(pady=(0, 20))
        
        # Middle section - Chart and controls
        middle_section = tk.Frame(self.main_frame, bg=self.bg_color)
        middle_section.pack(fill=tk.BOTH, expand=True, pady=(0, 25))
        
        # Chart panel (left side)
        chart_panel = tk.Frame(middle_section, bg=self.bg_color)
        chart_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Chart container with modern styling
        self.chart_container = self.create_modern_card(chart_panel, height=350)
        self.chart_container.pack(fill=tk.BOTH, expand=True)
        
        # Chart header
        chart_header_frame = tk.Frame(self.chart_container, bg=self.card_bg)
        chart_header_frame.pack(fill=tk.X, padx=25, pady=(20, 0))
        
        tk.Label(
            chart_header_frame,
            text="BALANCE HISTORY",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side=tk.LEFT)
        
        self.chart_status = tk.Label(
            chart_header_frame,
            text="LIVE",
            font=("Segoe UI", 9, "bold"),
            bg=self.success_color,
            fg="white",
            padx=8,
            pady=2
        )
        self.chart_status.pack(side=tk.RIGHT)
        
        # Chart canvas with modern styling
        self.chart_canvas = tk.Canvas(
            self.chart_container,
            bg=self.chart_bg,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, padx=25, pady=(15, 25))
        
        # Control panel (right side)
        control_panel = tk.Frame(middle_section, bg=self.bg_color, width=320)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y)
        control_panel.pack_propagate(False)
        
        # Mining controls card
        controls_card = self.create_modern_card(control_panel)
        controls_card.pack(fill=tk.BOTH, expand=True)
        
        # Controls header
        tk.Label(
            controls_card,
            text="MINING CONTROLS",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(pady=(25, 20))
        
        # Status display
        status_frame = tk.Frame(controls_card, bg=self.card_bg)
        status_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
        
        tk.Label(
            status_frame,
            text="STATUS:",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(side=tk.LEFT)
        
        self.mining_status_label = tk.Label(
            status_frame,
            text="STOPPED",
            font=("Segoe UI", 10, "bold"),
            bg=self.card_bg,
            fg="#ff4757"
        )
        self.mining_status_label.pack(side=tk.RIGHT)
        
        # Session timer
        timer_frame = tk.Frame(controls_card, bg=self.card_bg)
        timer_frame.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        tk.Label(
            timer_frame,
            text="SESSION TIME:",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.muted_color
        ).pack(side=tk.LEFT)
        
        self.session_time_label = tk.Label(
            timer_frame,
            text="00:00:00",
            font=("JetBrains Mono", 10, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.session_time_label.pack(side=tk.RIGHT)
        
        # Modern control buttons
        button_frame = tk.Frame(controls_card, bg=self.card_bg)
        button_frame.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        # Start button with modern styling
        self.start_button = tk.Button(
            button_frame,
            text="START MINING",
            command=self.start_mining,
            font=("Segoe UI", 12, "bold"),
            bg=self.success_color,
            fg="white",
            bd=0,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_button.pack(fill=tk.X, pady=(0, 10))
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="STOP MINING",
            command=self.stop_mining,
            font=("Segoe UI", 12, "bold"),
            bg=self.danger_color,
            fg="white",
            bd=0,
            pady=15,
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(fill=tk.X)
        
        # Bottom section - Activity log
        log_section = tk.Frame(self.main_frame, bg=self.bg_color)
        log_section.pack(fill=tk.X)
        
        # Log container
        log_container = self.create_modern_card(log_section, height=180)
        log_container.pack(fill=tk.BOTH)
        
        # Log header
        log_header = tk.Frame(log_container, bg=self.card_bg)
        log_header.pack(fill=tk.X, padx=25, pady=(20, 10))
        
        tk.Label(
            log_header,
            text="ACTIVITY LOG",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side=tk.LEFT)
        
        self.last_save_label = tk.Label(
            log_header,
            text="Last save: --:--:--",
            font=("Segoe UI", 9),
            bg=self.card_bg,
            fg=self.muted_color
        )
        self.last_save_label.pack(side=tk.RIGHT)
        
        # Log text with scrollbar
        log_content = tk.Frame(log_container, bg=self.card_bg)
        log_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(log_content, bg=self.card_bg)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_content,
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            borderwidth=0,
            yscrollcommand=scrollbar.set,
            font=("JetBrains Mono", 9),
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Initial setup
        self.log("CryptoMiner Pro initialized. Ready to begin mining operations.")
        self.log_text.configure(state=tk.DISABLED)
        self.update_balance_display()

    def create_deposit_view(self):
        # Deposit view frame
        self.deposit_view = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # Main deposit container
        deposit_main = tk.Frame(self.deposit_view, bg=self.bg_color)
        deposit_main.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Enhanced title section
        title_section = tk.Frame(deposit_main, bg=self.bg_color)
        title_section.pack(fill=tk.X, pady=(0, 30))
        
        # Exchange branding
        brand_frame = tk.Frame(title_section, bg=self.bg_color)
        brand_frame.pack(side=tk.LEFT)
        
        # Binance logo placeholder
        tk.Label(
            brand_frame,
            text="◈",
            font=("Arial", 36, "bold"),
            bg=self.bg_color,
            fg="#F0B90B"  # Binance yellow
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        title_text_frame = tk.Frame(brand_frame, bg=self.bg_color)
        title_text_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_text_frame,
            text="METAMASK INTEGRATION",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_text_frame,
            text="Connect your exchange account for seamless trading",
            font=("Segoe UI", 12),
            bg=self.bg_color,
            fg=self.muted_color
        ).pack(anchor=tk.W)
        
        # Balance display
        balance_display = tk.Frame(title_section, bg=self.bg_color)
        balance_display.pack(side=tk.RIGHT)
        
        tk.Label(
            balance_display,
            text="Available Balance",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.muted_color
        ).pack(anchor=tk.E)
        
        self.deposit_balance_label = tk.Label(
            balance_display,
            text="0.00 TXC",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_color,
            fg=self.success_color
        )
        self.deposit_balance_label.pack(anchor=tk.E)
        
        # Main content grid
        content_grid = tk.Frame(deposit_main, bg=self.bg_color)
        content_grid.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Connection form
        left_panel = tk.Frame(content_grid, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # API Configuration card
        config_card = self.create_modern_card(left_panel)
        config_card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        tk.Label(
            config_card,
            text="API CONFIGURATION",
            font=("Segoe UI", 14, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(pady=(25, 25))
        
        # Form fields with modern styling
        form_frame = tk.Frame(config_card, bg=self.card_bg)
        form_frame.pack(fill=tk.X, padx=30, pady=(0, 30))
        
        # API Key field
        self.create_form_field(form_frame, "Secret Key", "155c84e57aa39dc0ef08ec5c2ad60e3115619c2ac3e673c2bc93a87232e50c13")
        
        # Secret Key field
        self.create_form_field(form_frame, "API", "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j", show="*")
        
        # Action button
        self.initiate_deposit_btn = tk.Button(
            form_frame,
            text="INITIALIZE CONNECTION",
            command=self.initiate_deposit,
            font=("Segoe UI", 13, "bold"),
            bg=self.accent_color,
            fg="white",
            bd=0,
            pady=18,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.initiate_deposit_btn.pack(fill=tk.X, pady=(20, 0))
        
        # Right panel - Status and information
        right_panel = tk.Frame(content_grid, bg=self.bg_color, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # Connection status card
        status_card = self.create_modern_card(right_panel, height=200)
        status_card.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            status_card,
            text="CONNECTION STATUS",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(pady=(25, 15))
        
        # Status indicator with icon
        status_indicator_frame = tk.Frame(status_card, bg=self.card_bg)
        status_indicator_frame.pack(pady=(0, 15))
        
        tk.Label(
            status_indicator_frame,
            text="●",
            font=("Arial", 24),
            bg=self.card_bg,
            fg=self.success_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.deposit_status_label = tk.Label(
            status_indicator_frame,
            text="CONNECTED",
            font=("Segoe UI", 16, "bold"),
            bg=self.card_bg,
            fg=self.success_color
        )
        self.deposit_status_label.pack(side=tk.LEFT)
        
        self.connection_info_label = tk.Label(
            status_card,
            text="Binance API connection established\nAll trading features are now available",
            font=("Segoe UI", 11),
            bg=self.card_bg,
            fg=self.text_color,
            justify=tk.CENTER
        )
        self.connection_info_label.pack(pady=(0, 25))
        
        # Information panel
        info_card = self.create_modern_card(right_panel)
        info_card.pack(fill=tk.BOTH, expand=True)
        
        # Info header
        tk.Label(
            info_card,
            text="PLATFORM FEATURES",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(pady=(25, 20))
        
        # Feature list with modern icons
        features_frame = tk.Frame(info_card, bg=self.card_bg)
        features_frame.pack(fill=tk.X, padx=30, pady=(0, 25))
        
        features = [
            ("✓", "Secure API Integration", self.success_color),
            ("⚡", "Instant Deposits", self.accent_color),
            ("📊", "Real-time Analytics", self.warning_color),
            ("🔒", "Bank-level Security", self.success_color)
        ]
        
        for icon, text, color in features:
            feature_row = tk.Frame(features_frame, bg=self.card_bg)
            feature_row.pack(fill=tk.X, pady=5)
            
            tk.Label(
                feature_row,
                text=icon,
                font=("Arial", 14),
                bg=self.card_bg,
                fg=color
            ).pack(side=tk.LEFT, padx=(0, 15))
            
            tk.Label(
                feature_row,
                text=text,
                font=("Segoe UI", 11),
                bg=self.card_bg,
                fg=self.text_color
            ).pack(side=tk.LEFT)

    def create_form_field(self, parent, label_text, default_value, show=None):
        """Create a modern form field"""
        field_frame = tk.Frame(parent, bg=self.card_bg)
        field_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            field_frame,
            text=label_text,
            font=("Segoe UI", 11, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(0, 8))
        
        entry = tk.Entry(
            field_frame,
            font=("JetBrains Mono", 10),
            bg=self.chart_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            bd=1,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.accent_color,
            highlightbackground=self.border_color,
            show=show
        )
        entry.pack(fill=tk.X, pady=(0, 5), ipady=8)
        entry.insert(0, default_value)
        
        if label_text == "API Key":
            self.api_key_entry = entry
        else:
            self.secret_key_entry = entry

    def create_modern_card(self, parent, height=None, width_weight=1):
        """Create a modern card with subtle shadows and rounded appearance"""
        card = tk.Frame(
            parent,
            bg=self.card_bg,
            relief=tk.FLAT,
            bd=0
        )
        
        if height:
            card.configure(height=height)
            card.pack_propagate(False)
        
        # Add subtle border effect
        border_frame = tk.Frame(card, bg=self.border_color, height=1)
        border_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        return card

    def switch_view(self, view):
        # Hide all views
        self.mining_view.pack_forget()
        self.deposit_view.pack_forget()
        
        # Update navigation with modern active states
        if view == "mining":
            self.mining_nav_btn.config(
                bg=self.accent_color, 
                fg="white",
                font=("Segoe UI", 11, "bold")
            )
            self.deposit_nav_btn.config(
                bg=self.nav_bg,  # Changed from "transparent" to self.nav_bg
                fg=self.muted_color,
                font=("Segoe UI", 11)
            )
            self.mining_view.pack(fill=tk.BOTH, expand=True)
        elif view == "deposit":
            self.mining_nav_btn.config(
                bg=self.nav_bg,  # Changed from "transparent" to self.nav_bg
                fg=self.muted_color,
                font=("Segoe UI", 11)
            )
            self.deposit_nav_btn.config(
                bg=self.accent_color, 
                fg="white",
                font=("Segoe UI", 11, "bold")
            )
            self.deposit_view.pack(fill=tk.BOTH, expand=True)
            self.update_deposit_balance()
        
        self.current_view = view

    def initiate_deposit(self):
        """Enhanced deposit process with modern feedback"""
        # Show processing state
        self.initiate_deposit_btn.config(
            text="CONNECTING...",
            state=tk.DISABLED,
            bg=self.warning_color
        )
        
        # Simulate connection process
        def complete_connection():
            # Simulate successful connection
            self.initiate_deposit_btn.config(
                text="CONNECTION ESTABLISHED",
                bg=self.success_color,
                state=tk.NORMAL
            )
            
            # Show success message
            messagebox.showinfo(
                "Connection Successful",
                "Binance API connection established successfully!\n\nYou can now proceed with trading operations."
            )
            
            # Add to transaction log
            self.log("Binance API connection established")
            self.log("Exchange integration active - ready for trading")
        
        # Schedule completion after 2 seconds
        self.after(2000, complete_connection)

    def refresh_binance_connection(self):
        """Enhanced connection refresh with modern animations"""
        # Show refreshing state with modern styling
        self.deposit_status_label.config(text="SYNCING", fg=self.warning_color)
        
        def complete_refresh():
            self.deposit_status_label.config(text="CONNECTED", fg=self.success_color)
            self.connection_info_label.config(
                text="Binance API connection verified\nAll trading features operational"
            )
            messagebox.showinfo("Sync Complete", "Exchange connection verified and optimized!")
        
        self.after(1500, complete_refresh)

    def update_deposit_balance(self):
        """Update balance with modern formatting"""
        balance_text = "0.00 TXC"
        self.deposit_balance_label.config(text=balance_text)

    def configure_theme(self):
        """Enhanced theme configuration with modern color palettes"""
        if self.theme == "dark":
            # Modern dark theme with better contrast
            self.bg_color = "#0f0f0f"
            self.card_bg = "#1a1a1a"
            self.header_color = "#161616"
            self.text_color = "#ffffff"
            self.muted_color = "#9ca3af"
            self.accent_color = "#3b82f6"
            self.success_color = "#10b981"
            self.danger_color = "#ef4444"
            self.warning_color = "#f59e0b"
            self.chart_bg = "#111111"
            self.grid_color = "#374151"
            self.border_color = "#2d2d2d"
            self.nav_bg = "#2d2d2d"
            self.button_bg = "#2d2d2d"
        else:
            # Modern light theme with subtle tones
            self.bg_color = "#fafafa"
            self.card_bg = "#ffffff"
            self.header_color = "#ffffff"
            self.text_color = "#1f2937"
            self.muted_color = "#6b7280"
            self.accent_color = "#2563eb"
            self.success_color = "#059669"
            self.danger_color = "#dc2626"
            self.warning_color = "#d97706"
            self.chart_bg = "#f9fafb"
            self.grid_color = "#e5e7eb"
            self.border_color = "#e5e7eb"
            self.nav_bg = "#f3f4f6"
            self.button_bg = "#f3f4f6"

    def start_mining(self):
        if self.bot.start_mining():
            # Update all status indicators
            self.mining_status_label.config(text="ACTIVE", fg=self.success_color)
            self.status_dot.config(fg=self.success_color)
            self.status_text.config(text="MINING", fg=self.success_color)
            self.chart_status.config(bg=self.success_color, text="LIVE")
            
            # Update buttons
            self.start_button.config(state=tk.DISABLED, bg=self.muted_color)
            self.stop_button.config(state=tk.NORMAL, bg=self.danger_color)
            
            self.log("Mining operation initiated - starting hash calculations")
            self.session_start_time = time.time()
            self.update_session_timer()

    def stop_mining(self):
        if self.bot.stop_mining():
            # Update all status indicators
            self.mining_status_label.config(text="STOPPED", fg=self.danger_color)
            self.status_dot.config(fg=self.danger_color)
            self.status_text.config(text="OFFLINE", fg=self.muted_color)
            self.chart_status.config(bg=self.muted_color, text="PAUSED")
            
            # Update buttons
            self.start_button.config(state=tk.NORMAL, bg=self.success_color)
            self.stop_button.config(state=tk.DISABLED, bg=self.muted_color)
            
            self.log("Mining operation terminated")
            if self.session_start_time:
                duration = time.time() - self.session_start_time
                self.log(f"Session completed: {self.format_time(duration)}")
                self.session_start_time = None
            self.update_session_display()

    def update(self):
        # Update bot state
        reward = self.bot.update()
        
        # Update UI if needed
        if reward > 0:
            self.update_balance_display()
            self.update_session_display()
            # Add mining transaction
            self.bot.add_transaction("mining", reward, "completed")
        
        # Continuously update chart for animation
        self.render_chart()
        
        # Schedule next update
        self.after(self.update_interval, self.update)

    def update_balance_display(self):
        balance_text = f"{self.bot.balance:.8f}"
        self.balance_label.config(text=balance_text)
        # Also update deposit view balance if it exists
        if hasattr(self, 'deposit_balance_label'):
            self.update_deposit_balance()

    def update_session_display(self):
        # Only update if we're mining and have a session
        if self.bot.mining and self.bot.mining_sessions:
            session = self.bot.mining_sessions[-1]
            earned = session["earned"]
            self.session_earned_label.config(text=f"{earned:.8f}")
        
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
        """Enhanced chart rendering with modern animations and styling"""
        if not self.bot.history:
            return
            
        canvas = self.chart_canvas
        canvas.delete("all")
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if w < 100 or h < 100:
            return
            
        # Update animation offset for smooth animations
        self.chart_animation_offset += self.animation_speed
        if self.chart_animation_offset > 360:
            self.chart_animation_offset = 0
            
        # Modern chart margins
        margin_x = 50
        margin_y = 30
        chart_w = w - margin_x * 2
        chart_h = h - margin_y * 2
        
        # Modern gradient background
        gradient_steps = 30
        for i in range(gradient_steps):
            progress = i / gradient_steps
            if self.theme == "dark":
                # Dark theme gradient
                r = int(15 + 5 * progress)
                g = int(15 + 5 * progress)
                b = int(20 + 10 * progress)
            else:
                # Light theme gradient
                r = int(250 - 5 * progress)
                g = int(251 - 5 * progress)
                b = int(252 - 5 * progress)
                
            color = f"#{r:02x}{g:02x}{b:02x}"
            y_start = margin_y + i * chart_h / gradient_steps
            y_end = margin_y + (i + 1) * chart_h / gradient_steps
            
            canvas.create_rectangle(
                margin_x, y_start, w - margin_x, y_end,
                fill=color, outline=""
            )
        
        # Modern chart border with subtle shadow effect
        canvas.create_rectangle(
            margin_x, margin_y, w - margin_x, h - margin_y,
            fill="", outline=self.border_color, width=1
        )
        
        # Process data
        if len(self.bot.history) < 2:
            # Show empty state
            canvas.create_text(
                w//2, h//2,
                text="Start mining to see your balance history",
                font=("Segoe UI", 12),
                fill=self.muted_color
            )
            return
        
        timestamps = [t for t, _ in self.bot.history]
        balances = [b for _, b in self.bot.history]
        
        min_balance = min(balances)
        max_balance = max(balances)
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # Ensure reasonable range
        if max_balance - min_balance < 0.00000001:
            max_balance = min_balance + 0.00000001
            
        # Modern grid system
        grid_lines = 4
        for i in range(1, grid_lines):
            # Horizontal grid lines with subtle animation
            y_pos = margin_y + chart_h - (i/grid_lines) * chart_h
            
            canvas.create_line(
                margin_x, y_pos, w - margin_x, y_pos,
                fill=self.grid_color, width=1, dash=(2, 4)
            )
            
            # Y-axis labels with modern typography
            value = min_balance + (max_balance - min_balance) * (i/grid_lines)
            canvas.create_text(
                margin_x - 15, y_pos,
                text=f"{value:.8f}",
                fill=self.muted_color,
                font=("JetBrains Mono", 8),
                anchor=tk.E
            )
        
        # Time axis labels
        time_points = 4
        for i in range(time_points):
            x_pos = margin_x + (i/(time_points-1)) * chart_w
            if max_time > min_time:
                time_val = min_time + (max_time - min_time) * (i/(time_points-1))
                time_str = time.strftime("%H:%M", time.localtime(time_val))
                canvas.create_text(
                    x_pos, h - margin_y + 20,
                    text=time_str,
                    fill=self.muted_color,
                    font=("Segoe UI", 8),
                    anchor=tk.N
                )
        
        # Calculate chart points
        points = []
        for timestamp, balance in self.bot.history:
            if max_time > min_time:
                x = margin_x + (timestamp - min_time) / (max_time - min_time) * chart_w
            else:
                x = margin_x + chart_w / 2
            y = margin_y + chart_h - (balance - min_balance) / (max_balance - min_balance) * chart_h
            points.append((x, y))
        
        if points:
            # Create area fill under the line
            area_points = [(margin_x, h - margin_y)] + points + [(w - margin_x, h - margin_y)]
            canvas.create_polygon(
                area_points,
                fill=f"{self.accent_color}20",
                outline=""
            )
            
            # Draw main line with multiple passes for glow effect
            line_widths = [4, 2, 1]
            line_colors = [f"{self.accent_color}40", f"{self.accent_color}80", self.accent_color]
            
            for width, color in zip(line_widths, line_colors):
                for i in range(1, len(points)):
                    x1, y1 = points[i-1]
                    x2, y2 = points[i]
                    canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color, width=width,
                        smooth=True, capstyle=tk.ROUND
                    )
            
            # Modern current value indicator
            last_x, last_y = points[-1]
            
            # Animated pulse effect
            pulse_radius = 6 + 3 * abs(math.sin(self.chart_animation_offset * 0.08))
            
            # Outer glow rings
            for radius in [pulse_radius + 8, pulse_radius + 4]:
                opacity = 40 - (radius - pulse_radius) * 5
                canvas.create_oval(
                    last_x - radius, last_y - radius,
                    last_x + radius, last_y + radius,
                    fill=f"{self.accent_color}{opacity:02x}",
                    outline=""
                )
            
            # Core indicator
            canvas.create_oval(
                last_x - 4, last_y - 4,
                last_x + 4, last_y + 4,
                fill=self.accent_color,
                outline="white",
                width=2
            )
            
            # Modern value tooltip
            tooltip_bg = self.card_bg
            tooltip_border = self.accent_color
            
            canvas.create_rectangle(
                last_x - 60, last_y - 40,
                last_x + 60, last_y - 15,
                fill=tooltip_bg,
                outline=tooltip_border,
                width=1
            )
            
            canvas.create_text(
                last_x, last_y - 27,
                text=f"{self.bot.balance:.8f} TXC",
                fill=self.text_color,
                font=("JetBrains Mono", 9, "bold")
            )
            
        # Modern live indicator
        if self.bot.mining:
            live_opacity = abs(math.sin(self.chart_animation_offset * 0.1))
            live_color = self.success_color if live_opacity > 0.5 else f"{self.success_color}60"
            
            canvas.create_rectangle(
                w - margin_x - 50, margin_y + 15,
                w - margin_x - 10, margin_y + 35,
                fill=live_color,
                outline=self.success_color,
                width=1
            )
            
            canvas.create_text(
                w - margin_x - 30, margin_y + 25,
                text="LIVE",
                fill="white",
                font=("Segoe UI", 8, "bold")
            )

    def log(self, message):
        """Enhanced logging with modern formatting"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{formatted_message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # Limit log size
        if int(self.log_text.index("end-1c").split('.')[0]) > 50:
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete(1.0, "2.0")
            self.log_text.configure(state=tk.DISABLED)

    def toggle_theme(self):
        """Enhanced theme toggle with smooth transitions"""
        self.theme = "light" if self.theme == "dark" else "dark"
        self.theme_button.config(text="◑" if self.theme == "dark" else "◐")
        
        # Save current state before theme change
        old_theme = "dark" if self.theme == "light" else "light"
        
        # Apply new theme
        self.configure_theme()
        
        # Show modern notification
        theme_name = "Dark Mode" if self.theme == "dark" else "Light Mode"
        messagebox.showinfo(
            "Theme Updated", 
            f"Switched to {theme_name}\n\nSome elements will update on next restart for best performance."
        )

    def save_state(self):
        self.bot.save_state()
        self.log("Application state synchronized")
        self.update_last_save_time()

    def auto_save(self):
        if self.bot.mining:
            self.bot.save_state()
            self.log("Auto-save: Mining progress saved")
            self.update_last_save_time()
        
        # Schedule next auto-save
        self.after(self.auto_save_interval, self.auto_save)
    
    def update_last_save_time(self):
        timestamp = time.strftime("%H:%M:%S")
        self.last_save_label.config(text=f"Last sync: {timestamp}")

    def on_close(self):
        # Enhanced shutdown process
        self.bot.save_state()
        self.log("Application shutdown - all data saved")
        self.destroy()


if __name__ == "__main__":
    app = MiningApp()
    app.mainloop()