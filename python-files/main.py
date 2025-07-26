import tkinter as tk
import customtkinter as ctk
import pandas as pd
import numpy as np
from binance import Client
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from matplotlib.figure import Figure
import ta
import os
import webbrowser
import tkinter.ttk as ttk
from tkcalendar import Calendar
import glob


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

Logo = resource_path("Logo.png")


# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


class TradingBot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuantumTrade AI - Binance Trading Bot")
        self.geometry("1400x900")

        # Register cleanup function for when window closes
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure grid layout properly
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Main content area
        self.grid_rowconfigure(0, weight=0)  # Header (fixed height)
        self.grid_rowconfigure(2, weight=0)  # Status bar (fixed height)

        # Create status_var early to prevent errors
        self.status_var = tk.StringVar(value="Ready to connect to Binance")

        # Set application icon
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        # Variables
        self.api_key = tk.StringVar()
        self.api_secret = tk.StringVar()
        self.model_type = tk.StringVar(value="Random Forest")
        self.training_days = tk.StringVar(value="7")
        self.symbol = tk.StringVar(value="BTCUSDT")
        self.balance = tk.StringVar(value="1000.00")
        self.position_size = tk.IntVar(value=10)
        self.take_profit = tk.DoubleVar(value=2.0)
        self.stop_loss = tk.DoubleVar(value=1.0)
        self.update_interval = tk.IntVar(value=5)
        self.trading_active = False
        self.client = None
        self.model = None
        self.current_position = None
        self.trades = []
        self.all_symbols = []  # To store all available symbols
        self.backtest_trades = []  # Store backtest trades for CSV export
        self.last_backtest_csv = None  # Store last generated backtest CSV filename

        # Indicators with default values
        self.indicators = {
            "SMA_short": tk.IntVar(value=5),
            "SMA_medium": tk.IntVar(value=10),
            "SMA_long": tk.IntVar(value=20),
            "EMA_short": tk.IntVar(value=5),
            "EMA_medium": tk.IntVar(value=10),
            "Volatility_short": tk.IntVar(value=5),
            "Volatility_long": tk.IntVar(value=10),
            "RSI": tk.IntVar(value=14),
            "BB_window": tk.IntVar(value=20),
            "BB_std": tk.DoubleVar(value=2.0),
            "Stoch_RSI": tk.IntVar(value=14),
            "MACD_fast": tk.IntVar(value=12),
            "MACD_slow": tk.IntVar(value=26),
            "MACD_signal": tk.IntVar(value=9),
            "OBV": tk.BooleanVar(value=True)
        }

        # Create header frame with proper height
        self.header_frame = ctk.CTkFrame(self, height=80)
        self.header_frame.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Application title
        title_label = ctk.CTkLabel(self.header_frame, text="QuantumTrade AI",
                                   font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Status indicators
        self.status_frame = ctk.CTkFrame(self.header_frame)
        self.status_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        self.connection_status = ctk.CTkLabel(self.status_frame, text="Disconnected",
                                              fg_color="gray", corner_radius=10,
                                              padx=10, pady=3)
        self.connection_status.grid(row=0, column=0, padx=5)

        self.model_status = ctk.CTkLabel(self.status_frame, text="Model: Not Trained",
                                         fg_color="gray", corner_radius=10,
                                         padx=10, pady=3)
        self.model_status.grid(row=0, column=1, padx=5)

        self.trading_status = ctk.CTkLabel(self.status_frame, text="Trading: Stopped",
                                           fg_color="gray", corner_radius=10,
                                           padx=10, pady=3)
        self.trading_status.grid(row=0, column=2, padx=5)

        # Create main tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=10, pady=(2, 10), sticky="nsew")
        self.tab_view.grid_rowconfigure(0, weight=1)

        # Add tabs
        self.tab_view.add("Account")
        self.tab_view.add("Indicators")
        self.tab_view.add("Training")
        self.tab_view.add("Trading")
        self.tab_view.add("History")
        self.tab_view.add("Backtest")

        # Configure each tab to expand properly
        for tab_name in ["Account", "Indicators", "Training", "Trading", "History", "Backtest"]:
            tab = self.tab_view.tab(tab_name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)

        # Build each tab
        self.setup_account_tab()
        self.setup_indicator_tab()
        self.setup_training_tab()
        self.setup_trading_tab()
        self.setup_history_tab()
        self.setup_backtest_tab()

        # Status bar
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w",
                                  height=20, font=("Arial", 10))
        status_bar.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Setup database
        self.db_setup()

        # Start the update loop
        self.after(1000, self.update_logs)

    # NEW FUNCTION: Clean up CSV files on exit
    def on_closing(self):
        """Delete all CSV files in the directory when closing the application"""
        self.log_message("Cleaning up CSV files before exit...")

        # Get all CSV files in the current directory
        csv_files = glob.glob('*.csv')

        # Delete each CSV file
        for file in csv_files:
            try:
                os.remove(file)
                self.log_message(f"Deleted: {file}")
            except Exception as e:
                self.log_message(f"Error deleting {file}: {str(e)}")

        # Close the database connection
        self.conn.close()

        # Destroy the window
        self.destroy()

    # NEW FUNCTION: Show backtest trades in a table
    def show_backtest_trades(self):
        """Open a new window showing the backtest trades in a table"""
        if not self.last_backtest_csv:
            self.log_message("No backtest trades to display. Run a backtest first.")
            return

        try:
            # Create new window
            trade_window = ctk.CTkToplevel(self)
            trade_window.title("Backtest Trade List")
            trade_window.geometry("1200x600")

            # Create frame for treeview
            tree_frame = ctk.CTkFrame(trade_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            # Read CSV file
            df = pd.read_csv(self.last_backtest_csv)

            # Create treeview
            columns = list(df.columns)
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

            # Create scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            # Define columns and headings
            for col in columns:
                # Format column names
                col_name = col.replace('_', ' ').title()
                tree.heading(col, text=col_name)

                # Set column widths
                if 'time' in col:
                    tree.column(col, width=150, anchor="center")
                elif 'price' in col or 'dollar' in col:
                    tree.column(col, width=100, anchor="e")
                elif 'percent' in col:
                    tree.column(col, width=80, anchor="e")
                else:
                    tree.column(col, width=80, anchor="center")

            # Add data to treeview
            for index, row in df.iterrows():
                values = []
                for col in columns:
                    val = row[col]

                    # Format numerical values
                    if isinstance(val, (int, float)):
                        if 'time' in col:
                            # Skip formatting for datetime columns
                            values.append(val)
                        elif 'percent' in col:
                            values.append(f"{val:.2f}%")
                        else:
                            values.append(f"{val:.2f}")
                    else:
                        values.append(val)

                tree.insert("", "end", values=values)

            # Layout
            tree.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")

            # Add close button
            close_btn = ctk.CTkButton(trade_window, text="Close",
                                      command=trade_window.destroy,
                                      width=100, height=30)
            close_btn.pack(pady=10)

            self.log_message(f"Displaying backtest trades from {self.last_backtest_csv}")

        except Exception as e:
            self.log_message(f"Error displaying backtest trades: {str(e)}")

    # Validation method for float entries
    def validate_float(self, new_value):
        if new_value == "":
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    def setup_account_tab(self):
        tab = self.tab_view.tab("Account")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)  # Add this to make content expand
        # API Frame
        api_frame = ctk.CTkFrame(tab, fg_color="transparent")
        api_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # API Key
        ctk.CTkLabel(api_frame, text="Binance API Key:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5,
                                                                                  sticky="w")
        api_entry = ctk.CTkEntry(api_frame, textvariable=self.api_key, width=400,
                                 placeholder_text="Enter your Binance API Key")
        api_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # API Secret
        ctk.CTkLabel(api_frame, text="API Secret:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5,
                                                                             sticky="w")
        secret_entry = ctk.CTkEntry(api_frame, textvariable=self.api_secret, show="*", width=400,
                                    placeholder_text="Enter your Binance API Secret")
        secret_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Connect Button
        connect_btn = ctk.CTkButton(api_frame, text="Connect to Binance",
                                    command=self.connect_binance, width=150,
                                    fg_color="#2e8b57", hover_color="#3cb371")
        connect_btn.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        ToolTip(connect_btn, "Connect to your Binance account using API credentials")

        # Documentation link
        docs_btn = ctk.CTkButton(api_frame, text="How to get API Keys",
                                 command=self.open_api_docs, width=150,
                                 fg_color="#1e3f5a", hover_color="#2a5278")
        docs_btn.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        ToolTip(docs_btn, "Open Binance API documentation in your browser")

        # Trading settings frame
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)

        # Symbol Search
        ctk.CTkLabel(settings_frame, text="Search Pair:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5,
                                                                                   sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(settings_frame, textvariable=self.search_var, width=200,
                                    placeholder_text="Type to search...")
        search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ToolTip(search_entry, "Search for a cryptocurrency pair")

        # Bind the search function
        self.search_var.trace_add("write", self.filter_symbols)

        # Symbol Selection
        ctk.CTkLabel(settings_frame, text="Trading Pair:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5,
                                                                                    sticky="w")
        self.symbol_combo = ctk.CTkComboBox(settings_frame, variable=self.symbol, width=200,
                                            dropdown_font=("Arial", 10))
        self.symbol_combo.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ToolTip(self.symbol_combo, "Select the cryptocurrency pair you want to trade")

        # Default symbols
        default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        self.symbol_combo.configure(values=default_symbols)
        self.all_symbols = default_symbols  # Initialize with default symbols

        # Balance with validation
        ctk.CTkLabel(settings_frame, text="Account Balance ($):", font=("Arial", 12)).grid(row=2, column=0, padx=10,
                                                                                           pady=5, sticky="w")
        vcmd = (self.register(self.validate_float), '%P')
        balance_entry = ctk.CTkEntry(settings_frame, textvariable=self.balance, width=200,
                                     validate="key", validatecommand=vcmd)
        balance_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ToolTip(balance_entry, "Set your available trading balance in USD")

    def filter_symbols(self, *args):
        """Filter the symbol list based on search text"""
        search_text = self.search_var.get().upper()
        if not search_text:
            # Show all symbols if search is empty
            self.symbol_combo.configure(values=self.all_symbols)
        else:
            # Filter symbols that contain the search text
            filtered = [s for s in self.all_symbols if search_text in s]
            self.symbol_combo.configure(values=filtered)

            # If there's only one match, select it
            if len(filtered) == 1:
                self.symbol.set(filtered[0])

    def open_api_docs(self):
        webbrowser.open("https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072")

    def setup_indicator_tab(self):
        tab = self.tab_view.tab("Indicators")
        tab.grid_columnconfigure(0, weight=1)

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Section header
        ctk.CTkLabel(scroll_frame, text="Indicator Configuration",
                     font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3,
                                                      padx=10, pady=10, sticky="w")

        ctk.CTkLabel(scroll_frame, text="Adjust parameters for each technical indicator:",
                     font=("Arial", 12)).grid(row=1, column=0, columnspan=3,
                                              padx=10, pady=(0, 20), sticky="w")

        # Create indicator cards
        row = 2
        for name, var in self.indicators.items():
            # Create card frame
            card_frame = ctk.CTkFrame(scroll_frame, border_width=1, corner_radius=5)
            card_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
            card_frame.grid_columnconfigure(1, weight=1)

            # Card title
            title = name.replace('_', ' ').title()
            ctk.CTkLabel(card_frame, text=title, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5,
                                                                                  sticky="w")

            # Special handling for OBV (checkbox instead of slider)
            if name == "OBV":
                cb = ctk.CTkCheckBox(card_frame, text="Enable OBV Indicator", variable=var,
                                     font=("Arial", 11))
                cb.grid(row=0, column=1, padx=10, pady=5, sticky="e")
                ToolTip(cb, "Toggle On-Balance Volume indicator")
                row += 1
                continue

            # Slider for other indicators
            label = ctk.CTkLabel(card_frame, text="Period:", font=("Arial", 11))
            label.grid(row=0, column=1, padx=(20, 5), pady=5, sticky="e")

            # Special range for BB standard deviation
            if name == "BB_std":
                slider = ctk.CTkSlider(card_frame, from_=1, to=3, variable=var, number_of_steps=20)
                slider.set(float(var.get()))
                value_label = ctk.CTkLabel(card_frame, text=f"{var.get():.1f}", font=("Arial", 11))
            else:
                slider = ctk.CTkSlider(card_frame, from_=1, to=100, variable=var)
                value_label = ctk.CTkLabel(card_frame, text=str(var.get()), font=("Arial", 11))

            slider.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="ew")
            value_label.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

            # Update label when slider changes
            def update_label(val, label=value_label, var=var, name=name):
                if name == "BB_std":
                    label.configure(text=f"{float(val):.1f}")
                else:
                    label.configure(text=str(int(float(val))))

            slider.configure(command=update_label)
            row += 1

            # Add tooltip
            ToolTip(card_frame, f"Adjust parameters for {title} indicator")

    def setup_training_tab(self):
        tab = self.tab_view.tab("Training")
        tab.grid_columnconfigure(0, weight=1)

        # Training settings frame
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(settings_frame, text="Model Configuration",
                     font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2,
                                                      padx=10, pady=10, sticky="w")

        # Model selection
        ctk.CTkLabel(settings_frame, text="Machine Learning Model:",
                     font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        model_combo = ctk.CTkComboBox(settings_frame, variable=self.model_type,
                                      values=["Random Forest", "Gradient Boosting"],
                                      font=("Arial", 11))
        model_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        ToolTip(model_combo, "Select machine learning algorithm for signal generation")

        # Training days
        ctk.CTkLabel(settings_frame, text="Training Data Period:",
                     font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        days_combo = ctk.CTkComboBox(settings_frame, variable=self.training_days,
                                     values=["7", "14", "30"], font=("Arial", 11))
        days_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        ToolTip(days_combo, "Select number of days of historical data for training")

        # Train button
        train_btn = ctk.CTkButton(settings_frame, text="Train Model",
                                  command=self.train_model, width=150,
                                  fg_color="#2e8b57", hover_color="#3cb371",
                                  font=("Arial", 12, "bold"))
        train_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=20)
        ToolTip(train_btn, "Start training the machine learning model")

        # Training status frame
        status_frame = ctk.CTkFrame(tab)
        status_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(status_frame, text="Training Status",
                     font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.train_status = ctk.CTkLabel(status_frame, text="Model not trained",
                                         font=("Arial", 11), justify="left")
        self.train_status.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Accuracy display
        self.accuracy_var = tk.StringVar(value="Accuracy: -")
        accuracy_label = ctk.CTkLabel(status_frame, textvariable=self.accuracy_var,
                                      font=("Arial", 11))
        accuracy_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(status_frame, orientation="horizontal",
                                               mode="determinate", height=15)
        self.progress_bar.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

    def setup_trading_tab(self):
        tab = self.tab_view.tab("Trading")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Trading parameters frame
        param_frame = ctk.CTkFrame(tab)
        param_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(param_frame, text="Trading Parameters",
                     font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3,
                                                      padx=10, pady=10, sticky="w")

        # Position size
        ctk.CTkLabel(param_frame, text="Position Size (%):",
                     font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        pos_slider = ctk.CTkSlider(param_frame, from_=1, to=100, variable=self.position_size)
        pos_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        pos_label = ctk.CTkLabel(param_frame, textvariable=self.position_size,
                                 font=("Arial", 11))
        pos_label.grid(row=1, column=2, padx=10, pady=5)
        ToolTip(pos_slider, "Set percentage of account to risk per trade")

        # Take profit
        ctk.CTkLabel(param_frame, text="Take Profit (%):",
                     font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tp_slider = ctk.CTkSlider(param_frame, from_=0.1, to=10, variable=self.take_profit,
                                  number_of_steps=99)
        tp_slider.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        tp_label = ctk.CTkLabel(param_frame, textvariable=self.take_profit,
                                font=("Arial", 11))
        tp_label.grid(row=2, column=2, padx=10, pady=5)
        ToolTip(tp_slider, "Set profit target percentage for each trade")

        # Stop loss
        ctk.CTkLabel(param_frame, text="Stop Loss (%):",
                     font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        sl_slider = ctk.CTkSlider(param_frame, from_=0.1, to=10, variable=self.stop_loss,
                                  number_of_steps=99)
        sl_slider.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        sl_label = ctk.CTkLabel(param_frame, textvariable=self.stop_loss,
                                font=("Arial", 11))
        sl_label.grid(row=3, column=2, padx=10, pady=5)
        ToolTip(sl_slider, "Set maximum loss percentage for each trade")

        # Update interval
        ctk.CTkLabel(param_frame, text="Analysis Interval (sec):",
                     font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        interval_slider = ctk.CTkSlider(param_frame, from_=1, to=60, variable=self.update_interval)
        interval_slider.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        interval_label = ctk.CTkLabel(param_frame, textvariable=self.update_interval,
                                      font=("Arial", 11))
        interval_label.grid(row=4, column=2, padx=10, pady=5)
        ToolTip(interval_slider, "Set how often the bot analyzes the market")

        # Start/Stop button
        self.trade_btn = ctk.CTkButton(param_frame, text="Start Trading",
                                       command=self.toggle_trading, width=150,
                                       font=("Arial", 12, "bold"))
        self.trade_btn.grid(row=5, column=0, columnspan=3, padx=10, pady=20)

        # Logs frame
        log_frame = ctk.CTkFrame(tab)
        log_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="Trading Log",
                     font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Log text area
        self.log_text = tk.Text(log_frame, wrap="word", bg="#2b2b2b", fg="white",
                                insertbackground="white", state="disabled",
                                font=("Consolas", 10))
        self.log_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(log_frame, command=self.log_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Initialize logs
        self.log_message("QuantumTrade AI initialized. Connect to Binance and train model to begin trading.")

    def setup_history_tab(self):
        tab = self.tab_view.tab("History")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(tab, text="Trade History",
                     font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Treeview for database
        columns = ("id", "timestamp", "symbol", "direction", "entry_price", "exit_price",
                   "position_size", "commission", "pnl_percent", "pnl_dollar")

        # Create frame for treeview and buttons
        tree_frame = ctk.CTkFrame(tab)
        tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("direction", text="Direction")
        self.tree.heading("entry_price", text="Entry Price")
        self.tree.heading("exit_price", text="Exit Price")
        self.tree.heading("position_size", text="Position Size")
        self.tree.heading("commission", text="Commission")
        self.tree.heading("pnl_percent", text="PnL %")
        self.tree.heading("pnl_dollar", text="PnL $")

        # Set column widths
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("timestamp", width=150, anchor="center")
        self.tree.column("symbol", width=80, anchor="center")
        self.tree.column("direction", width=70, anchor="center")
        self.tree.column("entry_price", width=90, anchor="center")
        self.tree.column("exit_price", width=90, anchor="center")
        self.tree.column("position_size", width=100, anchor="center")
        self.tree.column("commission", width=90, anchor="center")
        self.tree.column("pnl_percent", width=70, anchor="center")
        self.tree.column("pnl_dollar", width=90, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Buttons frame
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Delete buttons
        del_btn = ctk.CTkButton(btn_frame, text="Delete Selected",
                                command=self.delete_selected, width=120,
                                fg_color="#8b0000", hover_color="#a52a2a")
        del_btn.pack(side="left", padx=10, pady=5)
        ToolTip(del_btn, "Remove selected trade from history")

        del_all_btn = ctk.CTkButton(btn_frame, text="Delete All",
                                    command=self.delete_all, width=120,
                                    fg_color="#8b0000", hover_color="#a52a2a")
        del_all_btn.pack(side="left", padx=10, pady=5)
        ToolTip(del_all_btn, "Clear entire trade history")

        # Refresh button
        refresh_btn = ctk.CTkButton(btn_frame, text="Refresh",
                                    command=self.load_db_data, width=120)
        refresh_btn.pack(side="right", padx=10, pady=5)
        ToolTip(refresh_btn, "Reload trade history")

        # Export button
        export_btn = ctk.CTkButton(btn_frame, text="Export to CSV",
                                   command=self.export_to_csv, width=120,
                                   fg_color="#1e3f5a", hover_color="#2a5278")
        export_btn.pack(side="right", padx=10, pady=5)
        ToolTip(export_btn, "Export trade history to CSV file")

        # Load initial data
        self.load_db_data()

    def setup_backtest_tab(self):
        tab = self.tab_view.tab("Backtest")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(tab, text="Strategy Backtesting",
                     font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Date selection frame
        date_frame = ctk.CTkFrame(tab, fg_color="transparent")
        date_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        date_frame.grid_columnconfigure(0, weight=1)
        date_frame.grid_columnconfigure(1, weight=1)
        date_frame.grid_columnconfigure(2, weight=1)

        # Start date
        ctk.CTkLabel(date_frame, text="Start Date:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5,
                                                                              sticky="e")
        self.start_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.start_date.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ToolTip(self.start_date, "Start date for backtesting period")

        # Calendar button for start date
        cal_btn_start = ctk.CTkButton(date_frame, text="📅", width=30, command=self.pick_start_date)
        cal_btn_start.grid(row=0, column=1, padx=(130, 0), pady=5, sticky="w")

        # End date
        ctk.CTkLabel(date_frame, text="End Date:", font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=5,
                                                                            sticky="e")
        self.end_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.end_date.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        ToolTip(self.end_date, "End date for backtesting period")

        # Calendar button for end date
        cal_btn_end = ctk.CTkButton(date_frame, text="📅", width=30, command=self.pick_end_date)
        cal_btn_end.grid(row=0, column=3, padx=(130, 0), pady=5, sticky="w")

        # Set default dates (last 30 days)
        end = datetime.now()
        start = end - timedelta(days=30)
        self.start_date.insert(0, start.strftime("%Y-%m-%d"))
        self.end_date.insert(0, end.strftime("%Y-%m-%d"))

        # Commission settings
        self.commission_enabled = tk.BooleanVar(value=False)
        commission_check = ctk.CTkCheckBox(date_frame, text="Enable Commission",
                                           variable=self.commission_enabled,
                                           font=("Arial", 12))
        commission_check.grid(row=0, column=4, padx=10, pady=5, sticky="w")
        ToolTip(commission_check, "Include commission in backtest calculations")

        ctk.CTkLabel(date_frame, text="Commission %:", font=("Arial", 12)).grid(row=0, column=5, padx=10, pady=5,
                                                                                sticky="e")
        self.commission_percent = tk.DoubleVar(value=0.1)
        commission_entry = ctk.CTkEntry(date_frame, textvariable=self.commission_percent, width=60)
        commission_entry.grid(row=0, column=6, padx=10, pady=5, sticky="w")
        ToolTip(commission_entry, "Commission percentage per trade")

        # Run backtest button
        backtest_btn = ctk.CTkButton(date_frame, text="Run Backtest",
                                     command=self.run_backtest, width=120,
                                     fg_color="#2e8b57", hover_color="#3cb371")
        backtest_btn.grid(row=0, column=7, padx=10, pady=5, sticky="e")
        ToolTip(backtest_btn, "Run backtest with current settings")

        # NEW: Trade List button
        trade_list_btn = ctk.CTkButton(date_frame, text="Trade List",
                                       command=self.show_backtest_trades, width=120,
                                       fg_color="#4b0082", hover_color="#6a5acd")
        trade_list_btn.grid(row=0, column=8, padx=10, pady=5, sticky="e")
        ToolTip(trade_list_btn, "View detailed backtest trade list")

        # Create results container frame
        results_container = ctk.CTkFrame(tab)
        results_container.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        results_container.grid_rowconfigure(0, weight=1)
        results_container.grid_columnconfigure(0, weight=1)
        results_container.grid_columnconfigure(1, weight=0)  # Metrics column (fixed width)

        # Graph frame
        graph_frame = ctk.CTkFrame(results_container)
        graph_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(0, weight=1)

        # Metrics frame
        metrics_frame = ctk.CTkFrame(results_container, width=300)
        metrics_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        metrics_frame.grid_propagate(False)  # Keep fixed width
        metrics_frame.grid_rowconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(0, weight=1)

        # Performance metrics header
        ctk.CTkLabel(metrics_frame, text="Performance Metrics",
                     font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Create metrics labels with initial values
        self.initial_balance_label = ctk.CTkLabel(metrics_frame, text="Initial Balance: $0.00",
                                                  font=("Arial", 12), anchor="w")
        self.initial_balance_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")

        self.final_balance_label = ctk.CTkLabel(metrics_frame, text="Final Balance: $0.00",
                                                font=("Arial", 12), anchor="w")
        self.final_balance_label.grid(row=2, column=0, padx=10, pady=2, sticky="w")

        self.profit_label = ctk.CTkLabel(metrics_frame, text="Profit: $0.00 (0.00%)",
                                         font=("Arial", 12), anchor="w")
        self.profit_label.grid(row=3, column=0, padx=10, pady=2, sticky="w")

        self.trades_label = ctk.CTkLabel(metrics_frame, text="Trades: 0",
                                         font=("Arial", 12), anchor="w")
        self.trades_label.grid(row=4, column=0, padx=10, pady=2, sticky="w")

        # Separator
        separator = ttk.Separator(metrics_frame, orient='horizontal')
        separator.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # Confusion matrix header
        ctk.CTkLabel(metrics_frame, text="Confusion Matrix",
                     font=("Arial", 14, "bold")).grid(row=6, column=0, padx=10, pady=(5, 5), sticky="w")

        # Create confusion matrix labels
        self.tp_label = ctk.CTkLabel(metrics_frame, text="True Positive: 0.00%",
                                     font=("Arial", 12), anchor="w")
        self.tp_label.grid(row=7, column=0, padx=10, pady=2, sticky="w")

        self.tn_label = ctk.CTkLabel(metrics_frame, text="True Negative: 0.00%",
                                     font=("Arial", 12), anchor="w")
        self.tn_label.grid(row=8, column=0, padx=10, pady=2, sticky="w")

        self.fp_label = ctk.CTkLabel(metrics_frame, text="False Positive: 0.00%",
                                     font=("Arial", 12), anchor="w")
        self.fp_label.grid(row=9, column=0, padx=10, pady=2, sticky="w")

        self.fn_label = ctk.CTkLabel(metrics_frame, text="False Negative: 0.00%",
                                     font=("Arial", 12), anchor="w")
        self.fn_label.grid(row=10, column=0, padx=10, pady=2, sticky="w")

        # Separator
        separator2 = ttk.Separator(metrics_frame, orient='horizontal')
        separator2.grid(row=11, column=0, padx=10, pady=10, sticky="ew")

        # Commission label
        self.commission_label = ctk.CTkLabel(metrics_frame, text="Commission: 0.00%",
                                             font=("Arial", 12), anchor="w")
        self.commission_label.grid(row=12, column=0, padx=10, pady=2, sticky="w")

        # Matplotlib figure (in graph frame)
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def pick_start_date(self):
        self.show_calendar(self.start_date)

    def pick_end_date(self):
        self.show_calendar(self.end_date)

    def show_calendar(self, target_entry):
        """Create a calendar popup for date selection"""
        top = tk.Toplevel(self)
        top.title("Select Date")
        top.geometry("300x280")
        top.attributes('-topmost', True)

        # Create calendar widget
        cal = Calendar(top, selectmode='day', date_pattern='y-mm-dd')
        cal.pack(padx=10, pady=10, fill="both", expand=True)

        # Set current date from entry if valid
        current_date = target_entry.get()
        try:
            if current_date:
                year, month, day = map(int, current_date.split('-'))
                cal.selection_set(datetime(year, month, day))
        except:
            pass

        # Confirm button
        def set_date():
            target_entry.delete(0, tk.END)
            target_entry.insert(0, cal.get_date())
            top.destroy()

        btn_frame = ctk.CTkFrame(top)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(btn_frame, text="Cancel", command=top.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="OK", command=set_date).pack(side="right", padx=5)

    def db_setup(self):
        self.conn = sqlite3.connect('trading_bot.db')
        self.c = self.conn.cursor()

        # Create trades table if not exists
        self.c.execute('''CREATE TABLE IF NOT EXISTS trades
                          (
                              id
                              INTEGER
                              PRIMARY
                              KEY
                              AUTOINCREMENT,
                              timestamp
                              DATETIME,
                              symbol
                              TEXT,
                              direction
                              TEXT,
                              entry_price
                              REAL,
                              exit_price
                              REAL,
                              position_size
                              REAL,
                              commission
                              REAL,
                              pnl_percent
                              REAL,
                              pnl_dollar
                              REAL
                          )''')
        self.conn.commit()

    def connect_binance(self):
        try:
            self.client = Client(self.api_key.get(), self.api_secret.get())
            self.log_message("Successfully connected to Binance")
            self.status_var.set("Connected to Binance")
            self.connection_status.configure(text="Connected", fg_color="green")

            # Get available symbols
            exchange_info = self.client.get_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith('USDT')]
            self.all_symbols = sorted(symbols)
            self.symbol_combo.configure(values=self.all_symbols)
            self.log_message(f"Loaded {len(self.all_symbols)} trading pairs")

        except Exception as e:
            self.log_message(f"Connection failed: {str(e)}")
            self.status_var.set("Connection failed")
            self.connection_status.configure(text="Disconnected", fg_color="red")

    def log_message(self, message):
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
        self.status_var.set(message)

    def update_logs(self):
        # This method would update logs from background threads
        self.after(1000, self.update_logs)

    def train_model(self):
        if not self.client:
            self.log_message("Error: Not connected to Binance")
            return

        try:
            self.log_message("Starting model training...")
            self.status_var.set("Training model...")
            self.progress_bar.set(0.2)

            # Get training days
            days = int(self.training_days.get())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Fetch historical data
            self.log_message(f"Fetching historical data for {self.symbol.get()}...")
            klines = self.client.get_historical_klines(
                self.symbol.get(),
                Client.KLINE_INTERVAL_1HOUR,
                start_date.strftime("%d %b %Y %H:%M:%S"),
                end_date.strftime("%d %b %Y %H:%M:%S")
            )
            self.progress_bar.set(0.4)

            # Create DataFrame
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                       'close_time', 'quote_asset_volume', 'trades',
                       'taker_buy_base', 'taker_buy_quote', 'ignore']
            df = pd.DataFrame(klines, columns=columns)

            # Convert to numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Calculate indicators
            self.log_message("Calculating indicators...")
            df = self.calculate_indicators(df)
            self.progress_bar.set(0.6)

            # Prepare training data
            self.log_message("Preparing training data...")
            X, y = self.prepare_training_data(df)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            self.log_message(f"Training {self.model_type.get()} model...")
            if self.model_type.get() == "Random Forest":
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = GradientBoostingClassifier(n_estimators=100, random_state=42)

            model.fit(X_train_scaled, y_train)
            self.progress_bar.set(0.8)

            # Evaluate
            train_acc = accuracy_score(y_train, model.predict(X_train_scaled))
            test_acc = accuracy_score(y_test, model.predict(X_test_scaled))

            # Save model
            self.model = model
            self.scaler = scaler

            # Save to CSV
            df.to_csv(f"training_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", index=False)

            # Update UI
            self.accuracy_var.set(f"Train Accuracy: {train_acc:.2%}, Test Accuracy: {test_acc:.2%}")
            self.train_status.configure(text=f"Model trained on {len(df)} samples")
            self.model_status.configure(text="Model: Trained", fg_color="green")
            self.log_message(f"Model training completed. Accuracy: {test_acc:.2%}")
            self.status_var.set("Model training complete")
            self.progress_bar.set(1.0)

        except Exception as e:
            self.log_message(f"Training failed: {str(e)}")
            self.status_var.set("Training failed")
            self.model_status.configure(text="Model: Failed", fg_color="red")
            self.progress_bar.set(0)

    def calculate_indicators(self, df):
        # Simple Moving Averages
        df['SMA_5'] = df['close'].rolling(window=self.indicators["SMA_short"].get()).mean()
        df['SMA_10'] = df['close'].rolling(window=self.indicators["SMA_medium"].get()).mean()
        df['SMA_20'] = df['close'].rolling(window=self.indicators["SMA_long"].get()).mean()

        # Exponential Moving Averages
        df['EMA_5'] = df['close'].ewm(span=self.indicators["EMA_short"].get(), adjust=False).mean()
        df['EMA_10'] = df['close'].ewm(span=self.indicators["EMA_medium"].get(), adjust=False).mean()

        # Volatility
        df['Volatility_5'] = df['close'].rolling(window=self.indicators["Volatility_short"].get()).std()
        df['Volatility_10'] = df['close'].rolling(window=self.indicators["Volatility_long"].get()).std()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        avg_gain = gain.rolling(window=self.indicators["RSI"].get()).mean()
        avg_loss = loss.rolling(window=self.indicators["RSI"].get()).mean()

        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        window = self.indicators["BB_window"].get()
        std = self.indicators["BB_std"].get()

        sma = df['close'].rolling(window=window).mean()
        rolling_std = df['close'].rolling(window=window).std()

        df['BB_upper'] = sma + (rolling_std * std)
        df['BB_lower'] = sma - (rolling_std * std)

        # Stochastic RSI
        stoch_rsi = (df['RSI'] - df['RSI'].rolling(window=self.indicators["Stoch_RSI"].get()).min())
        stoch_rsi /= (df['RSI'].rolling(window=self.indicators["Stoch_RSI"].get()).max() -
                      df['RSI'].rolling(window=self.indicators["Stoch_RSI"].get()).min())
        df['Stoch_RSI'] = stoch_rsi * 100

        # MACD
        exp1 = df['close'].ewm(span=self.indicators["MACD_fast"].get(), adjust=False).mean()
        exp2 = df['close'].ewm(span=self.indicators["MACD_slow"].get(), adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=self.indicators["MACD_signal"].get(), adjust=False).mean()

        # OBV
        if self.indicators["OBV"].get():
            df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

        return df.dropna()

    def prepare_training_data(self, df):
        # Calculate returns
        df['returns'] = df['close'].pct_change() * 100

        # Create target - 1 for long, -1 for short, 0 for hold
        threshold = 0.005  # 0.5% threshold
        df['target'] = 0
        df.loc[df['close'].shift(-1) > (1 + threshold) * df['close'], 'target'] = 1  # Long
        df.loc[df['close'].shift(-1) < (1 - threshold) * df['close'], 'target'] = -1  # Short

        # Select features
        features = ['returns', 'SMA_5', 'SMA_10', 'SMA_20', 'EMA_5', 'EMA_10',
                    'Volatility_5', 'Volatility_10', 'RSI', 'BB_upper', 'BB_lower',
                    'Stoch_RSI', 'MACD', 'MACD_signal']

        if 'OBV' in df.columns:
            features.append('OBV')

        # Prepare X and y
        X = df[features]
        y = df['target']

        return X, y

    def toggle_trading(self):
        if not self.trading_active:
            if not self.model:
                self.log_message("Error: Model not trained")
                return

            self.trading_active = True
            self.trade_btn.configure(text="Stop Trading", fg_color="#8b0000", hover_color="#a52a2a")
            self.status_var.set("Trading active")
            self.trading_status.configure(text="Trading: Active", fg_color="green")
            self.log_message("Trading started")

            # Start trading in a separate thread
            threading.Thread(target=self.trade_loop, daemon=True).start()
        else:
            self.trading_active = False
            self.trade_btn.configure(text="Start Trading", fg_color="#2e8b57", hover_color="#3cb371")
            self.status_var.set("Trading stopped")
            self.trading_status.configure(text="Trading: Stopped", fg_color="gray")
            self.log_message("Trading stopped")

    def trade_loop(self):
        while self.trading_active:
            try:
                # Determine the maximum window size needed for indicators
                max_window = max(
                    self.indicators["SMA_long"].get(),  # 20
                    self.indicators["BB_window"].get(),  # 20
                    self.indicators["Stoch_RSI"].get(),  # 14
                    self.indicators["MACD_slow"].get(),  # 26
                    self.indicators["RSI"].get(),  # 14
                    30  # Additional buffer
                )

                # Fetch enough historical data to calculate all indicators
                klines = self.client.get_klines(
                    symbol=self.symbol.get(),
                    interval=Client.KLINE_INTERVAL_5MINUTE,
                    limit=max_window + 10  # Fetch extra data
                )

                # Create DataFrame with all candles
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                           'close_time', 'quote_asset_volume', 'trades',
                           'taker_buy_base', 'taker_buy_quote', 'ignore']
                df = pd.DataFrame(klines, columns=columns)

                # Convert to numeric
                numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']
                df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                # Calculate indicators
                df = self.calculate_indicators(df)

                # Check if we have data after calculations
                if len(df) == 0:
                    self.log_message("Warning: No data after indicator calculation. Skipping prediction.")
                    time.sleep(self.update_interval.get())
                    continue

                # Use only the latest row for prediction
                latest_row = df.iloc[[-1]]

                # Prepare for prediction
                X, _ = self.prepare_training_data(latest_row)

                # Skip if no features
                if X.empty:
                    self.log_message("Warning: Feature set empty. Skipping prediction.")
                    time.sleep(self.update_interval.get())
                    continue

                X_scaled = self.scaler.transform(X)

                # Predict
                prediction = self.model.predict(X_scaled)[0]

                # Get current price
                ticker = self.client.get_symbol_ticker(symbol=self.symbol.get())
                current_price = float(ticker['price'])

                # Execute trade based on prediction
                if prediction == 1:  # Long signal
                    self.execute_trade("LONG", current_price)
                elif prediction == -1:  # Short signal
                    self.execute_trade("SHORT", current_price)
                else:  # Hold
                    self.log_message(f"HOLD signal at {current_price}")

                # Check for exit conditions
                self.check_exit_conditions(current_price)

                # Sleep for the specified interval
                time.sleep(self.update_interval.get())

            except Exception as e:
                self.log_message(f"Trading error: {str(e)}")
                time.sleep(5)

    def execute_trade(self, direction, price):
        # Only one position at a time
        if self.current_position:
            self.log_message(f"Ignoring {direction} signal - position already open")
            return

        # Calculate position size - handle empty balance
        try:
            current_balance = float(self.balance.get())
        except ValueError:
            current_balance = 0.0
            self.log_message("Invalid balance value, using 0.0")

        position_value = current_balance * (self.position_size.get() / 100)
        quantity = position_value / price

        # Create trade
        trade = {
            'timestamp': datetime.now(),
            'symbol': self.symbol.get(),
            'direction': direction,
            'entry_price': price,
            'quantity': quantity,
            'position_size': position_value,
            'take_profit': price * (1 + (self.take_profit.get() / 100)) if direction == "LONG" else price * (
                    1 - (self.take_profit.get() / 100)),
            'stop_loss': price * (1 - (self.stop_loss.get() / 100)) if direction == "LONG" else price * (
                    1 + (self.stop_loss.get() / 100)),
            'exit_price': None,
            'commission': position_value * 0.001,  # 0.1% commission
            'pnl_percent': None,
            'pnl_dollar': None
        }

        # Save to memory
        self.current_position = trade
        self.trades.append(trade)

        # Log
        self.log_message(f"{direction} position opened at {price:.4f}, Size: ${position_value:.2f}")

        # Update status
        self.status_var.set(f"{direction} position open")

    def check_exit_conditions(self, current_price):
        if not self.current_position:
            return

        trade = self.current_position
        direction = trade['direction']

        # Check take profit
        if ((direction == "LONG" and current_price >= trade['take_profit']) or
                (direction == "SHORT" and current_price <= trade['take_profit'])):
            self.close_trade("Take Profit", current_price)
            return

        # Check stop loss
        if ((direction == "LONG" and current_price <= trade['stop_loss']) or
                (direction == "SHORT" and current_price >= trade['stop_loss'])):
            self.close_trade("Stop Loss", current_price)
            return

    def close_trade(self, reason, price):
        trade = self.current_position
        direction = trade['direction']

        # Calculate PnL
        if direction == "LONG":
            pnl_percent = ((price - trade['entry_price']) / trade['entry_price']) * 100
        else:  # SHORT
            pnl_percent = ((trade['entry_price'] - price) / trade['entry_price']) * 100

        pnl_dollar = trade['position_size'] * (pnl_percent / 100)

        # Deduct commission
        total_commission = trade['commission'] + (trade['position_size'] * 0.001)  # Entry + exit commission
        net_pnl_dollar = pnl_dollar - total_commission
        net_pnl_percent = (net_pnl_dollar / trade['position_size']) * 100

        # Update trade
        trade['exit_price'] = price
        trade['pnl_percent'] = net_pnl_percent
        trade['pnl_dollar'] = net_pnl_dollar
        trade['commission'] = total_commission

        # Update balance
        try:
            current_balance = float(self.balance.get())
            new_balance = current_balance + net_pnl_dollar
            self.balance.set(f"{new_balance:.2f}")
        except ValueError:
            self.log_message("Invalid balance during trade close")

        # Save to database
        self.save_trade_to_db(trade)

        # Log
        self.log_message(f"{direction} position closed at {price:.4f} ({reason})")
        self.log_message(f"PnL: ${net_pnl_dollar:.2f} ({net_pnl_percent:.2f}%)")

        # Clear current position
        self.current_position = None
        self.status_var.set("No position open")

    def save_trade_to_db(self, trade):
        try:
            self.c.execute('''INSERT INTO trades
                              (timestamp, symbol, direction, entry_price, exit_price, position_size, commission,
                               pnl_percent, pnl_dollar)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (trade['timestamp'], trade['symbol'], trade['direction'], trade['entry_price'],
                            trade['exit_price'],
                            trade['position_size'], trade['commission'], trade['pnl_percent'], trade['pnl_dollar']))
            self.conn.commit()
            self.log_message("Trade saved to database")
        except Exception as e:
            self.log_message(f"Database error: {str(e)}")

    def load_db_data(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch data
        try:
            self.c.execute("SELECT * FROM trades ORDER BY timestamp DESC")
            rows = self.c.fetchall()

            for row in rows:
                # Format numbers
                formatted = list(row)
                formatted[4] = f"{formatted[4]:.4f}"  # entry_price
                formatted[5] = f"{formatted[5]:.4f}" if formatted[5] else ""  # exit_price
                formatted[6] = f"${formatted[6]:.2f}"  # position_size
                formatted[7] = f"${formatted[7]:.4f}"  # commission
                formatted[8] = f"{formatted[8]:.2f}%" if formatted[8] else ""  # pnl_percent
                formatted[9] = f"${formatted[9]:.2f}" if formatted[9] else ""  # pnl_dollar

                self.tree.insert("", "end", values=formatted)

        except Exception as e:
            self.log_message(f"Database load error: {str(e)}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        trade_id = self.tree.item(item, "values")[0]

        try:
            self.c.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
            self.conn.commit()
            self.tree.delete(item)
            self.log_message(f"Deleted trade ID {trade_id}")
        except Exception as e:
            self.log_message(f"Delete error: {str(e)}")

    def delete_all(self):
        try:
            self.c.execute("DELETE FROM trades")
            self.conn.commit()
            self.load_db_data()
            self.log_message("All trades deleted")
        except Exception as e:
            self.log_message(f"Delete all error: {str(e)}")

    def export_to_csv(self):
        try:
            # Get all trades
            self.c.execute("SELECT * FROM trades ORDER BY timestamp DESC")
            rows = self.c.fetchall()

            if not rows:
                self.log_message("No trades to export")
                return

            # Create DataFrame
            columns = ["id", "timestamp", "symbol", "direction", "entry_price",
                       "exit_price", "position_size", "commission", "pnl_percent", "pnl_dollar"]
            df = pd.DataFrame(rows, columns=columns)

            # Save to CSV
            filename = f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            self.log_message(f"Exported {len(df)} trades to {filename}")

        except Exception as e:
            self.log_message(f"Export failed: {str(e)}")

    def run_backtest(self):
        if not self.client:
            self.log_message("Error: Not connected to Binance")
            return

        try:
            # Get dates
            start_date = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date.get(), "%Y-%m-%d")

            if start_date >= end_date:
                self.log_message("Error: Start date must be before end date")
                return

            self.log_message(f"Starting backtest from {start_date} to {end_date}")

            # Fetch historical data
            klines = self.client.get_historical_klines(
                self.symbol.get(),
                Client.KLINE_INTERVAL_1HOUR,
                start_date.strftime("%d %b %Y %H:%M:%S"),
                end_date.strftime("%d %b %Y %H:%M:%S")
            )

            # Create DataFrame
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                       'close_time', 'quote_asset_volume', 'trades',
                       'taker_buy_base', 'taker_buy_quote', 'ignore']
            df = pd.DataFrame(klines, columns=columns)

            # Convert to numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Calculate indicators
            df = self.calculate_indicators(df)

            # Prepare for prediction
            X, _ = self.prepare_training_data(df)
            X_scaled = self.scaler.transform(X)

            # Predict
            df['signal'] = self.model.predict(X_scaled)

            # Calculate actual market movements using same threshold as training
            threshold = 0.005  # 0.5% threshold
            df['actual_movement'] = 0
            df.loc[df['close'].shift(-1) > (1 + threshold) * df['close'], 'actual_movement'] = 1  # Positive movement
            df.loc[df['close'].shift(-1) < (1 - threshold) * df['close'], 'actual_movement'] = -1  # Negative movement

            # Get commission settings
            commission_enabled = self.commission_enabled.get()
            commission_percent = self.commission_percent.get() / 100  # Convert to decimal

            # Simulate trading - handle balance conversion
            try:
                initial_balance = float(self.balance.get())
            except ValueError:
                initial_balance = 1000.0

            balance = initial_balance
            position = None
            self.backtest_trades = []  # Reset backtest trades

            for i, row in df.iterrows():
                current_price = row['close']

                # Close position if we have one
                if position:
                    # Check exit conditions
                    if ((position['direction'] == "LONG" and
                         (current_price >= position['take_profit'] or
                          current_price <= position['stop_loss'])) or
                            (position['direction'] == "SHORT" and
                             (current_price <= position['take_profit'] or
                              current_price >= position['stop_loss']))):

                        # Calculate PnL
                        if position['direction'] == "LONG":
                            pnl_percent_before = ((current_price - position['entry_price']) / position[
                                'entry_price']) * 100
                        else:  # SHORT
                            pnl_percent_before = ((position['entry_price'] - current_price) / position[
                                'entry_price']) * 100

                        pnl_dollar_before = position['position_size'] * (pnl_percent_before / 100)

                        # Calculate commission if enabled
                        commission = position['position_size'] * commission_percent * 2 if commission_enabled else 0
                        net_pnl_dollar = pnl_dollar_before - commission
                        net_pnl_percent = (net_pnl_dollar / position['position_size']) * 100

                        # Create trade record
                        trade_record = {
                            'entry_time': position['timestamp'],
                            'exit_time': row['timestamp'],
                            'symbol': self.symbol.get(),
                            'direction': position['direction'],
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'position_size': position['position_size'],
                            'pnl_percent_before': pnl_percent_before,
                            'pnl_dollar_before': pnl_dollar_before,
                            'commission_percent': commission_percent * 100 if commission_enabled else 0,
                            'commission_dollar': commission,
                            'pnl_percent_after': net_pnl_percent,
                            'pnl_dollar_after': net_pnl_dollar
                        }
                        self.backtest_trades.append(trade_record)

                        # Update position
                        position['exit_price'] = current_price
                        position['pnl_percent'] = net_pnl_percent
                        position['pnl_dollar'] = net_pnl_dollar
                        position['commission'] = commission

                        # Update balance
                        balance += net_pnl_dollar

                        position = None

                # Open new position if signal and no current position
                if position is None and row['signal'] != 0:
                    direction = "LONG" if row['signal'] == 1 else "SHORT"
                    position_value = balance * (self.position_size.get() / 100)
                    quantity = position_value / current_price

                    position = {
                        'timestamp': row['timestamp'],
                        'symbol': self.symbol.get(),
                        'direction': direction,
                        'entry_price': current_price,
                        'position_size': position_value,
                        'take_profit': current_price * (
                                    1 + (self.take_profit.get() / 100)) if direction == "LONG" else current_price * (
                                    1 - (self.take_profit.get() / 100)),
                        'stop_loss': current_price * (
                                    1 - (self.stop_loss.get() / 100)) if direction == "LONG" else current_price * (
                                    1 + (self.stop_loss.get() / 100))
                    }

            # Calculate confusion matrix metrics
            tp, tn, fp, fn = self.calculate_confusion_metrics(df)
            total = len(df) - 1  # Exclude last row with no future data

            # Calculate percentages
            tp_percent = (tp / total) * 100 if total > 0 else 0
            tn_percent = (tn / total) * 100 if total > 0 else 0
            fp_percent = (fp / total) * 100 if total > 0 else 0
            fn_percent = (fn / total) * 100 if total > 0 else 0

            # Final balance and profit
            final_balance = balance
            profit = final_balance - initial_balance
            profit_pct = (profit / initial_balance) * 100

            # Update UI with metrics
            self.initial_balance_label.configure(text=f"Initial Balance: ${initial_balance:.2f}")
            self.final_balance_label.configure(text=f"Final Balance: ${final_balance:.2f}")
            self.profit_label.configure(text=f"Profit: ${profit:.2f} ({profit_pct:.2f}%)")
            self.trades_label.configure(text=f"Trades: {len(self.backtest_trades)}")

            # Update confusion matrix labels
            self.tp_label.configure(text=f"True Positive: {tp_percent:.2f}%")
            self.tn_label.configure(text=f"True Negative: {tn_percent:.2f}%")
            self.fp_label.configure(text=f"False Positive: {fp_percent:.2f}%")
            self.fn_label.configure(text=f"False Negative: {fn_percent:.2f}%")

            # Update commission label
            if commission_enabled:
                self.commission_label.configure(text=f"Commission: {commission_percent * 100:.2f}% per trade")
            else:
                self.commission_label.configure(text="Commission: Disabled")

            # Plot results
            self.ax.clear()
            self.ax.plot(df['timestamp'], df['close'], label='Price', color='blue')

            # Plot trades
            for trade in self.backtest_trades:
                if trade['direction'] == "LONG":
                    color = 'green'
                    marker = '^'
                else:
                    color = 'red'
                    marker = 'v'

                self.ax.plot(trade['entry_time'], trade['entry_price'], marker=marker, markersize=8, color=color)
                self.ax.plot(trade['exit_time'], trade['exit_price'], marker='o', markersize=8, color=color)

            self.ax.set_title(f"Backtest Results for {self.symbol.get()}", fontsize=12)
            self.ax.set_xlabel("Date", fontsize=10)
            self.ax.set_ylabel("Price", fontsize=10)
            self.ax.legend(fontsize=9)
            self.ax.grid(True)
            self.fig.autofmt_xdate()
            self.canvas.draw()

            # Export trade list to CSV
            self.last_backtest_csv = self.export_backtest_trades()

            self.log_message(f"Backtest completed. Profit: ${profit:.2f} ({profit极pct:.2f}%)")
            self.log_message(
                f"TP: {tp_percent:.2f}%, TN: {tn_percent:.2f}%, FP: {fp_percent:.2f}%, FN: {fn_percent:.2f}%")

        except Exception as e:
            self.log_message(f"Backtest error: {str(e)}")

    def calculate_confusion_metrics(self, df):
        """Calculate confusion matrix metrics for backtest results"""
        # We'll exclude the last row since it has no future movement
        valid_df = df[:-1].copy()

        # Initialize counters
        true_positive = 0
        true_negative = 0
        false_positive = 0
        false_negative = 0

        # Compare predictions vs actual movements
        for _, row in valid_df.iterrows():
            predicted = row['signal']
            actual = row['actual_movement']

            # Long predictions
            if predicted == 1:
                if actual == 1:
                    true_positive += 1
                else:
                    false_positive += 1
            # Short predictions
            elif predicted == -1:
                if actual == -1:
                    true_positive += 1
                else:
                    false_positive += 1
            # Hold predictions
            else:  # predicted == 0
                if actual == 0:
                    true_negative += 1
                else:
                    false_negative += 1

        return true_positive, true_negative, false_positive, false_negative

    def export_backtest_trades(self):
        """Export backtest trades to CSV file with detailed information"""
        if not self.backtest_trades:
            self.log_message("No trades to export from backtest")
            return None

        try:
            # Create DataFrame
            df = pd.DataFrame(self.backtest_trades)

            # Format columns for better readability
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['exit_time'] = pd.to_datetime(df['exit_time'])

            # Format numerical values to two decimal places
            for col in df.columns:
                if 'percent' in col or 'dollar' in col or 'price' in col or 'size' in col:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)

            # Save to CSV
            filename = f"backtest_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)

            self.log_message(f"Exported {len(df)} backtest trades to {filename}")
            return filename
        except Exception as e:
            self.log_message(f"Error exporting backtest trades: {str(e)}")
            return None


if __name__ == "__main__":
    app = TradingBot()
    app.mainloop()