import tkinter as tk
from tkinter import ttk, messagebox
import math

class UniversalTradingCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Trading Calculator - Forex, Commodities, Indices, Crypto & Stocks")
        self.root.geometry("1000x800")
        self.root.configure(bg='#1a1a2e')

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#1a1a2e', foreground='#eee')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#1a1a2e', foreground='#eee')
        style.configure('Custom.TLabel', background='#16213e', foreground='white')
        style.configure('Custom.TEntry', fieldbackground='white')
        style.configure('Custom.TCombobox', fieldbackground='white')

        # All trading instruments with their specifications
        self.trading_instruments = {
            # FOREX MAJOR PAIRS
            'EURUSD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Pairs'},
            'GBPUSD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Pairs'},
            'USDJPY': {'type': 'forex', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Major Pairs'},
            'USDCHF': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Pairs'},
            'USDCAD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Pairs'},
            'AUDUSD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Pairs'},
            'NZDUSD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Pairs'},

            # FOREX MINOR PAIRS
            'EURGBP': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'EURAUD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'EURCHF': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'EURJPY': {'type': 'forex', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'GBPJPY': {'type': 'forex', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'GBPCHF': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'AUDJPY': {'type': 'forex', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'CADJPY': {'type': 'forex', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Minor Pairs'},
            'CHFJPY': {'type': 'forex', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Minor Pairs'},

            # FOREX EXOTIC PAIRS
            'USDTRY': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},
            'USDZAR': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},
            'USDMXN': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},
            'USDSEK': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},
            'USDNOK': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},
            'USDSGD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},
            'USDHKD': {'type': 'forex', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Exotic Pairs'},

            # COMMODITIES
            'XAUUSD': {'type': 'commodity', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Precious Metals', 'point_value': 1.0},
            'XAGUSD': {'type': 'commodity', 'pip_location': 3, 'pip_value_base': 0.001, 'min_lot': 0.01, 'category': 'Precious Metals', 'point_value': 5.0},
            'XPTUSD': {'type': 'commodity', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Precious Metals', 'point_value': 1.0},
            'XPDUSD': {'type': 'commodity', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Precious Metals', 'point_value': 1.0},
            'USOIL': {'type': 'commodity', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Energy', 'point_value': 10.0},
            'UKOIL': {'type': 'commodity', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Energy', 'point_value': 10.0},
            'NGAS': {'type': 'commodity', 'pip_location': 3, 'pip_value_base': 0.001, 'min_lot': 0.01, 'category': 'Energy', 'point_value': 10.0},

            # INDICES
            'US30': {'type': 'index', 'pip_location': 0, 'pip_value_base': 1.0, 'min_lot': 0.01, 'category': 'US Indices', 'point_value': 1.0},
            'SPX500': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'US Indices', 'point_value': 1.0},
            'NAS100': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'US Indices', 'point_value': 1.0},
            'GER30': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'European Indices', 'point_value': 1.0},
            'UK100': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'European Indices', 'point_value': 1.0},
            'FRA40': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'European Indices', 'point_value': 1.0},
            'JPN225': {'type': 'index', 'pip_location': 0, 'pip_value_base': 1.0, 'min_lot': 0.01, 'category': 'Asian Indices', 'point_value': 5.0},
            'AUS200': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'Asian Indices', 'point_value': 1.0},
            'HK50': {'type': 'index', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'Asian Indices', 'point_value': 1.0},

            # CRYPTOCURRENCIES
            'BTCUSD': {'type': 'crypto', 'pip_location': 1, 'pip_value_base': 0.1, 'min_lot': 0.01, 'category': 'Major Crypto', 'point_value': 1.0},
            'ETHUSD': {'type': 'crypto', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Major Crypto', 'point_value': 1.0},
            'LTCUSD': {'type': 'crypto', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Major Crypto', 'point_value': 1.0},
            'XRPUSD': {'type': 'crypto', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Major Crypto', 'point_value': 1.0},
            'ADAUSD': {'type': 'crypto', 'pip_location': 4, 'pip_value_base': 0.0001, 'min_lot': 0.01, 'category': 'Alt Coins', 'point_value': 1.0},
            'DOTUSD': {'type': 'crypto', 'pip_location': 3, 'pip_value_base': 0.001, 'min_lot': 0.01, 'category': 'Alt Coins', 'point_value': 1.0},
            'LINKUSD': {'type': 'crypto', 'pip_location': 3, 'pip_value_base': 0.001, 'min_lot': 0.01, 'category': 'Alt Coins', 'point_value': 1.0},
            'SOLUSD': {'type': 'crypto', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Alt Coins', 'point_value': 1.0},
            'AVAXUSD': {'type': 'crypto', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Alt Coins', 'point_value': 1.0},
            'BNBUSD': {'type': 'crypto', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 0.01, 'category': 'Alt Coins', 'point_value': 1.0},

            # INDIVIDUAL STOCKS (Popular ones)
            'AAPL': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'MSFT': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'GOOGL': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'AMZN': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'TSLA': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'NVDA': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'META': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'NFLX': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Tech Stocks', 'point_value': 1.0},
            'JPM': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Financial Stocks', 'point_value': 1.0},
            'BAC': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Financial Stocks', 'point_value': 1.0},
            'WMT': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Consumer Stocks', 'point_value': 1.0},
            'JNJ': {'type': 'stock', 'pip_location': 2, 'pip_value_base': 0.01, 'min_lot': 1, 'category': 'Healthcare Stocks', 'point_value': 1.0}
        }

        # Sample rates for calculations
        self.sample_rates = {
            # Forex rates
            'EURUSD': 1.0900, 'GBPUSD': 1.2650, 'USDJPY': 147.50, 'USDCHF': 0.8920, 'USDCAD': 1.3680,
            'AUDUSD': 0.6720, 'NZDUSD': 0.6150, 'EURGBP': 0.8617, 'EURAUD': 1.6220, 'EURCHF': 0.9723,
            'EURJPY': 160.85, 'GBPJPY': 186.69, 'GBPCHF': 1.1280, 'AUDJPY': 99.13, 'CADJPY': 107.80,
            'CHFJPY': 165.30, 'USDTRY': 27.45, 'USDZAR': 18.95, 'USDMXN': 17.12, 'USDSEK': 10.85,
            'USDNOK': 10.95, 'USDSGD': 1.3450, 'USDHKD': 7.8200,

            # Commodities
            'XAUUSD': 1925.50, 'XAGUSD': 23.45, 'XPTUSD': 895.20, 'XPDUSD': 1245.80,
            'USOIL': 78.45, 'UKOIL': 82.30, 'NGAS': 2.850,

            # Indices
            'US30': 34250.5, 'SPX500': 4385.2, 'NAS100': 15420.8, 'GER30': 15890.3,
            'UK100': 7450.2, 'FRA40': 7320.5, 'JPN225': 32450.8, 'AUS200': 7180.5, 'HK50': 18250.3,

            # Cryptocurrencies
            'BTCUSD': 43250.5, 'ETHUSD': 2650.8, 'LTCUSD': 68.45, 'XRPUSD': 0.6250,
            'ADAUSD': 0.4580, 'DOTUSD': 5.850, 'LINKUSD': 14.25, 'SOLUSD': 98.45,
            'AVAXUSD': 34.80, 'BNBUSD': 285.50,

            # Stocks
            'AAPL': 175.25, 'MSFT': 338.50, 'GOOGL': 125.80, 'AMZN': 142.30, 'TSLA': 248.50,
            'NVDA': 485.20, 'META': 315.40, 'NFLX': 425.80, 'JPM': 148.60, 'BAC': 28.95,
            'WMT': 158.40, 'JNJ': 162.30
        }

        self.setup_ui()

    def setup_ui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#1a1a2e')
        title_frame.pack(pady=15)

        title_label = ttk.Label(title_frame, text="Universal Trading Calculator", style='Title.TLabel')
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="Forex • Commodities • Indices • Crypto • Stocks", 
                                  font=('Arial', 11), background='#1a1a2e', foreground='#16a085')
        subtitle_label.pack()

        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=15, pady=10)

        # Tab 1: Pip/Point Value Calculator
        self.pip_value_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(self.pip_value_frame, text='📊 Pip/Point Value')
        self.setup_pip_value_tab()

        # Tab 2: Profit/Loss Calculator
        self.profit_loss_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(self.profit_loss_frame, text='💰 Profit/Loss')
        self.setup_profit_loss_tab()

        # Tab 3: Position Size Calculator
        self.position_size_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(self.position_size_frame, text='⚖️ Position Size')
        self.setup_position_size_tab()

        # Tab 4: Instrument Browser
        self.browser_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(self.browser_frame, text='🔍 Instruments')
        self.setup_browser_tab()

        # Tab 5: Reference
        self.reference_frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(self.reference_frame, text='📖 Reference')
        self.setup_reference_tab()

        # Footer
        footer_frame = tk.Frame(self.root, bg='#1a1a2e')
        footer_frame.pack(side='bottom', fill='x', pady=5)

        footer_label = tk.Label(footer_frame, text="© 2025 Universal Trading Calculator - Trade All Markets Responsibly", 
                               bg='#1a1a2e', fg='#95a5a6', font=('Arial', 8))
        footer_label.pack()

    def get_instruments_by_type(self, instrument_type=None, category=None):
        """Get instruments filtered by type and/or category"""
        instruments = []
        for symbol, info in self.trading_instruments.items():
            if instrument_type and info['type'] != instrument_type:
                continue
            if category and info['category'] != category:
                continue
            instruments.append(symbol)
        return sorted(instruments)

    def setup_pip_value_tab(self):
        # Input section
        input_frame = tk.LabelFrame(self.pip_value_frame, text="Calculate Pip/Point Value", 
                                   bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        input_frame.pack(pady=20, padx=20, fill='x')

        # Instrument type filter
        ttk.Label(input_frame, text="Asset Type:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.pip_type_var = tk.StringVar(value='All')
        type_combo = ttk.Combobox(input_frame, textvariable=self.pip_type_var,
                                 values=['All', 'forex', 'commodity', 'index', 'crypto', 'stock'], 
                                 style='Custom.TCombobox', width=15)
        type_combo.grid(row=0, column=1, padx=10, pady=8)
        type_combo.bind('<<ComboboxSelected>>', self.update_instrument_list)

        # Instrument selection
        ttk.Label(input_frame, text="Instrument:", style='Custom.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.pip_instrument_var = tk.StringVar(value='EURUSD')
        self.pip_instrument_combo = ttk.Combobox(input_frame, textvariable=self.pip_instrument_var,
                                               values=list(self.trading_instruments.keys()), 
                                               style='Custom.TCombobox', width=15)
        self.pip_instrument_combo.grid(row=1, column=1, padx=10, pady=8)

        # Position size
        ttk.Label(input_frame, text="Position Size:", style='Custom.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=8)
        self.pip_size_var = tk.StringVar(value='1.0')
        pip_size_entry = ttk.Entry(input_frame, textvariable=self.pip_size_var, style='Custom.TEntry', width=15)
        pip_size_entry.grid(row=2, column=1, padx=10, pady=8)

        # Quick size buttons
        size_frame = tk.Frame(input_frame, bg='#16213e')
        size_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(size_frame, text="0.01", command=lambda: self.pip_size_var.set('0.01'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(size_frame, text="0.1", command=lambda: self.pip_size_var.set('0.1'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(size_frame, text="1.0", command=lambda: self.pip_size_var.set('1.0'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(size_frame, text="10.0", command=lambda: self.pip_size_var.set('10.0'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)

        # Calculate button
        calculate_pip_btn = tk.Button(input_frame, text="Calculate Value", 
                                     command=self.calculate_pip_value,
                                     bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                                     relief='raised', bd=3)
        calculate_pip_btn.grid(row=4, column=0, columnspan=2, pady=15)

        # Results section
        self.pip_result_frame = tk.LabelFrame(self.pip_value_frame, text="Results", 
                                            bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        self.pip_result_frame.pack(pady=10, padx=20, fill='both', expand=True)

        self.pip_result_text = tk.Text(self.pip_result_frame, height=12, bg='white', 
                                      font=('Consolas', 10), wrap='word')
        scrollbar_pip = tk.Scrollbar(self.pip_result_frame, orient='vertical', command=self.pip_result_text.yview)
        self.pip_result_text.configure(yscrollcommand=scrollbar_pip.set)

        self.pip_result_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_pip.pack(side='right', fill='y')

    def setup_profit_loss_tab(self):
        # Input section
        input_frame = tk.LabelFrame(self.profit_loss_frame, text="Calculate Profit/Loss", 
                                   bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        input_frame.pack(pady=20, padx=20, fill='x')

        # Instrument
        ttk.Label(input_frame, text="Instrument:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.pl_instrument_var = tk.StringVar(value='EURUSD')
        pl_instrument_combo = ttk.Combobox(input_frame, textvariable=self.pl_instrument_var,
                                         values=list(self.trading_instruments.keys()), 
                                         style='Custom.TCombobox', width=15)
        pl_instrument_combo.grid(row=0, column=1, padx=10, pady=8)

        # Entry price
        ttk.Label(input_frame, text="Entry Price:", style='Custom.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.pl_entry_var = tk.StringVar(value='1.1000')
        pl_entry_entry = ttk.Entry(input_frame, textvariable=self.pl_entry_var, style='Custom.TEntry', width=15)
        pl_entry_entry.grid(row=1, column=1, padx=10, pady=8)

        # Exit price
        ttk.Label(input_frame, text="Exit Price:", style='Custom.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=8)
        self.pl_exit_var = tk.StringVar(value='1.1050')
        pl_exit_entry = ttk.Entry(input_frame, textvariable=self.pl_exit_var, style='Custom.TEntry', width=15)
        pl_exit_entry.grid(row=2, column=1, padx=10, pady=8)

        # Position size
        ttk.Label(input_frame, text="Position Size:", style='Custom.TLabel').grid(row=3, column=0, sticky='w', padx=10, pady=8)
        self.pl_size_var = tk.StringVar(value='1.0')
        pl_size_entry = ttk.Entry(input_frame, textvariable=self.pl_size_var, style='Custom.TEntry', width=15)
        pl_size_entry.grid(row=3, column=1, padx=10, pady=8)

        # Trade direction
        ttk.Label(input_frame, text="Direction:", style='Custom.TLabel').grid(row=4, column=0, sticky='w', padx=10, pady=8)
        self.pl_direction_var = tk.StringVar(value='Buy')
        pl_direction_combo = ttk.Combobox(input_frame, textvariable=self.pl_direction_var,
                                         values=['Buy', 'Sell'], style='Custom.TCombobox', width=15)
        pl_direction_combo.grid(row=4, column=1, padx=10, pady=8)

        # Calculate button
        calculate_pl_btn = tk.Button(input_frame, text="Calculate P&L",
                                    command=self.calculate_profit_loss,
                                    bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                                    relief='raised', bd=3)
        calculate_pl_btn.grid(row=5, column=0, columnspan=2, pady=15)

        # Results section
        self.pl_result_frame = tk.LabelFrame(self.profit_loss_frame, text="Results",
                                           bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        self.pl_result_frame.pack(pady=10, padx=20, fill='both', expand=True)

        self.pl_result_text = tk.Text(self.pl_result_frame, height=12, bg='white',
                                     font=('Consolas', 10), wrap='word')
        scrollbar_pl = tk.Scrollbar(self.pl_result_frame, orient='vertical', command=self.pl_result_text.yview)
        self.pl_result_text.configure(yscrollcommand=scrollbar_pl.set)

        self.pl_result_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_pl.pack(side='right', fill='y')

    def setup_position_size_tab(self):
        # Input section
        input_frame = tk.LabelFrame(self.position_size_frame, text="Calculate Position Size",
                                   bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        input_frame.pack(pady=20, padx=20, fill='x')

        # Instrument
        ttk.Label(input_frame, text="Instrument:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.ps_instrument_var = tk.StringVar(value='EURUSD')
        ps_instrument_combo = ttk.Combobox(input_frame, textvariable=self.ps_instrument_var,
                                         values=list(self.trading_instruments.keys()), 
                                         style='Custom.TCombobox', width=15)
        ps_instrument_combo.grid(row=0, column=1, padx=10, pady=8)

        # Account balance
        ttk.Label(input_frame, text="Account Balance ($):", style='Custom.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.ps_balance_var = tk.StringVar(value='10000')
        ps_balance_entry = ttk.Entry(input_frame, textvariable=self.ps_balance_var, style='Custom.TEntry', width=15)
        ps_balance_entry.grid(row=1, column=1, padx=10, pady=8)

        # Risk percentage
        ttk.Label(input_frame, text="Risk % per Trade:", style='Custom.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=8)
        self.ps_risk_pct_var = tk.StringVar(value='2')
        ps_risk_pct_entry = ttk.Entry(input_frame, textvariable=self.ps_risk_pct_var, style='Custom.TEntry', width=15)
        ps_risk_pct_entry.grid(row=2, column=1, padx=10, pady=8)

        # Stop loss distance
        ttk.Label(input_frame, text="Stop Loss Distance:", style='Custom.TLabel').grid(row=3, column=0, sticky='w', padx=10, pady=8)
        self.ps_sl_var = tk.StringVar(value='20')
        ps_sl_entry = ttk.Entry(input_frame, textvariable=self.ps_sl_var, style='Custom.TEntry', width=15)
        ps_sl_entry.grid(row=3, column=1, padx=10, pady=8)

        # Calculate button
        calculate_ps_btn = tk.Button(input_frame, text="Calculate Position Size",
                                    command=self.calculate_position_size,
                                    bg='#2ecc71', fg='white', font=('Arial', 11, 'bold'),
                                    relief='raised', bd=3)
        calculate_ps_btn.grid(row=4, column=0, columnspan=2, pady=15)

        # Results section
        self.ps_result_frame = tk.LabelFrame(self.position_size_frame, text="Results",
                                           bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        self.ps_result_frame.pack(pady=10, padx=20, fill='both', expand=True)

        self.ps_result_text = tk.Text(self.ps_result_frame, height=12, bg='white',
                                     font=('Consolas', 10), wrap='word')
        scrollbar_ps = tk.Scrollbar(self.ps_result_frame, orient='vertical', command=self.ps_result_text.yview)
        self.ps_result_text.configure(yscrollcommand=scrollbar_ps.set)

        self.ps_result_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_ps.pack(side='right', fill='y')

    def setup_browser_tab(self):
        # Browser frame with categories
        browser_main = tk.Frame(self.browser_frame, bg='#16213e')
        browser_main.pack(fill='both', expand=True, padx=20, pady=20)

        # Left panel - categories
        left_panel = tk.LabelFrame(browser_main, text="Asset Categories", 
                                  bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        left_panel.pack(side='left', fill='y', padx=(0, 10))

        categories = [
            ('All Instruments', 'all'),
            ('Forex Major Pairs', 'Major Pairs'),
            ('Forex Minor Pairs', 'Minor Pairs'),
            ('Forex Exotic Pairs', 'Exotic Pairs'),
            ('Precious Metals', 'Precious Metals'),
            ('Energy Commodities', 'Energy'),
            ('Stock Indices', 'US Indices'),
            ('European Indices', 'European Indices'),
            ('Asian Indices', 'Asian Indices'),
            ('Major Cryptocurrencies', 'Major Crypto'),
            ('Alt Coins', 'Alt Coins'),
            ('Tech Stocks', 'Tech Stocks'),
            ('Financial Stocks', 'Financial Stocks'),
            ('Consumer Stocks', 'Consumer Stocks'),
            ('Healthcare Stocks', 'Healthcare Stocks')
        ]

        for i, (display_name, category) in enumerate(categories):
            btn = tk.Button(left_panel, text=display_name, 
                           command=lambda cat=category: self.show_category(cat),
                           bg='#3498db', fg='white', font=('Arial', 9),
                           width=20, relief='raised')
            btn.pack(pady=2, padx=5, fill='x')

        # Right panel - instrument list
        right_panel = tk.LabelFrame(browser_main, text="Instruments", 
                                   bg='#16213e', fg='white', font=('Arial', 12, 'bold'))
        right_panel.pack(side='right', fill='both', expand=True)

        self.browser_text = tk.Text(right_panel, height=20, bg='white', 
                                   font=('Consolas', 9), wrap='word')
        scrollbar_browser = tk.Scrollbar(right_panel, orient='vertical', command=self.browser_text.yview)
        self.browser_text.configure(yscrollcommand=scrollbar_browser.set)

        self.browser_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_browser.pack(side='right', fill='y')

        # Show all instruments by default
        self.show_category('all')

    def setup_reference_tab(self):
        # Reference information
        ref_text = tk.Text(self.reference_frame, bg='white', font=('Consolas', 9), wrap='word')
        scrollbar_ref = tk.Scrollbar(self.reference_frame, orient='vertical', command=ref_text.yview)
        ref_text.configure(yscrollcommand=scrollbar_ref.set)

        ref_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_ref.pack(side='right', fill='y')

        reference_content = """UNIVERSAL TRADING CALCULATOR - COMPLETE REFERENCE GUIDE

═══════════════════════════════════════════════════════════════════════════════

🌍 FOREX MARKETS
═══════════════════════════════════════════════════════════════════════════════

MAJOR PAIRS (Most Liquid):
• EUR/USD - Euro vs US Dollar
• GBP/USD - British Pound vs US Dollar  
• USD/JPY - US Dollar vs Japanese Yen
• USD/CHF - US Dollar vs Swiss Franc
• USD/CAD - US Dollar vs Canadian Dollar
• AUD/USD - Australian Dollar vs US Dollar
• NZD/USD - New Zealand Dollar vs US Dollar

MINOR PAIRS (Cross Currencies):
• EUR/GBP, EUR/AUD, EUR/CHF, EUR/JPY
• GBP/JPY, GBP/CHF, AUD/JPY, CAD/JPY, CHF/JPY

EXOTIC PAIRS (Higher Spreads):
• USD/TRY (Turkish Lira), USD/ZAR (South African Rand)
• USD/MXN (Mexican Peso), USD/SEK (Swedish Krona)

🥇 COMMODITIES
═══════════════════════════════════════════════════════════════════════════════

PRECIOUS METALS:
• XAU/USD (Gold) - Traditional safe haven
• XAG/USD (Silver) - Industrial & investment metal
• XPT/USD (Platinum) - Automotive industry metal
• XPD/USD (Palladium) - Catalytic converter metal

ENERGY COMMODITIES:
• US Oil (WTI Crude) - West Texas Intermediate
• UK Oil (Brent Crude) - North Sea crude oil
• Natural Gas - Clean burning fossil fuel

📈 STOCK INDICES
═══════════════════════════════════════════════════════════════════════════════

US INDICES:
• US30 (Dow Jones) - 30 large US companies
• SPX500 (S&P 500) - 500 largest US companies
• NAS100 (Nasdaq 100) - 100 largest non-financial companies

EUROPEAN INDICES:
• GER30 (DAX) - 30 largest German companies
• UK100 (FTSE 100) - 100 largest UK companies
• FRA40 (CAC 40) - 40 largest French companies

ASIAN INDICES:
• JPN225 (Nikkei 225) - 225 Japanese companies
• AUS200 (ASX 200) - 200 largest Australian companies
• HK50 (Hang Seng) - Hong Kong stock market index

₿ CRYPTOCURRENCIES
═══════════════════════════════════════════════════════════════════════════════

MAJOR CRYPTOCURRENCIES:
• BTC/USD (Bitcoin) - Digital gold, store of value
• ETH/USD (Ethereum) - Smart contract platform
• LTC/USD (Litecoin) - Digital silver, faster transactions
• XRP/USD (Ripple) - Cross-border payment solution

ALT COINS:
• ADA/USD (Cardano) - Proof-of-stake blockchain
• DOT/USD (Polkadot) - Multi-chain protocol
• LINK/USD (Chainlink) - Decentralized oracle network
• SOL/USD (Solana) - High-speed blockchain
• AVAX/USD (Avalanche) - Scalable smart contracts
• BNB/USD (Binance Coin) - Exchange utility token

🏢 INDIVIDUAL STOCKS
═══════════════════════════════════════════════════════════════════════════════

TECHNOLOGY STOCKS:
• AAPL (Apple) - Consumer electronics
• MSFT (Microsoft) - Software and cloud services
• GOOGL (Alphabet/Google) - Search and advertising
• AMZN (Amazon) - E-commerce and cloud
• TSLA (Tesla) - Electric vehicles
• NVDA (NVIDIA) - Graphics and AI chips
• META (Meta/Facebook) - Social media
• NFLX (Netflix) - Streaming entertainment

FINANCIAL STOCKS:
• JPM (JPMorgan Chase) - Investment banking
• BAC (Bank of America) - Commercial banking

CONSUMER & HEALTHCARE:
• WMT (Walmart) - Retail chain
• JNJ (Johnson & Johnson) - Healthcare products

📊 CALCULATION SPECIFICATIONS
═══════════════════════════════════════════════════════════════════════════════

FOREX PIPS:
• Standard pairs: 4th decimal place (0.0001)
• JPY pairs: 2nd decimal place (0.01)
• Standard lot: 100,000 units
• Mini lot: 10,000 units (0.1)
• Micro lot: 1,000 units (0.01)

COMMODITY POINTS:
• Gold/Silver: $1 per point per lot
• Oil: $10 per point per lot
• Varies by broker and contract size

INDEX POINTS:
• US30: $1 per point
• SPX500/NAS100: $1 per point (typically)
• European indices: €1 per point
• Point values vary by broker

CRYPTO POINTS:
• Usually $1 per point per unit
• Highly volatile - use smaller position sizes
• 24/7 trading unlike traditional markets

STOCK POINTS:
• $1 per point per share
• No leverage for individual stocks in many regions
• Dividend considerations for long positions

⚖️ RISK MANAGEMENT BY ASSET CLASS
═══════════════════════════════════════════════════════════════════════════════

FOREX TRADING:
• Risk 1-3% per trade
• Popular with retail traders
• High liquidity, tight spreads
• 24/5 trading (Monday-Friday)

COMMODITY TRADING:
• Risk 2-5% per trade
• Affected by supply/demand fundamentals
• Weather, geopolitical events impact prices
• Gold often used as safe haven

INDEX TRADING:
• Risk 1-4% per trade
• Represents broader market sentiment
• Less volatile than individual stocks
• Good for trend following strategies

CRYPTO TRADING:
• Risk 1-2% per trade (high volatility)
• 24/7 trading
• Extreme price movements possible
• Regulatory risks to consider

STOCK TRADING:
• Risk 1-3% per trade
• Company-specific fundamentals important
• Earnings reports cause volatility
• Dividend dates affect pricing

💡 TRADING SESSIONS & OPTIMAL TIMES
═══════════════════════════════════════════════════════════════════════════════

FOREX SESSIONS:
• Sydney: 22:00-07:00 GMT
• Tokyo: 00:00-09:00 GMT  
• London: 08:00-17:00 GMT
• New York: 13:00-22:00 GMT

BEST OVERLAP TIMES:
• London-NY: 13:00-17:00 GMT (highest volume)
• Tokyo-London: 08:00-09:00 GMT

COMMODITY TRADING:
• Most active during London/NY sessions
• Oil: Affected by US inventory reports (Wednesdays)
• Gold: Active during uncertainty periods

INDEX TRADING:
• Most active during respective market hours
• US indices: 14:30-21:00 GMT
• European indices: 08:00-16:30 GMT
• Asian indices: 01:00-08:00 GMT

CRYPTO TRADING:
• 24/7 trading available
• Higher volatility during US/European hours
• Weekend trading available (unlike other markets)

⚠️ IMPORTANT DISCLAIMERS
═══════════════════════════════════════════════════════════════════════════════

• Sample rates used for calculations - use live rates for trading
• Point/pip values may vary between brokers
• Leverage regulations differ by country and asset class
• Past performance doesn't guarantee future results
• Consider spreads, commissions, and overnight fees
• Practice with demo accounts before live trading
• Never risk more than you can afford to lose
• Seek professional advice for large investments

© 2025 Universal Trading Calculator - Trade All Markets Responsibly
        """

        ref_text.insert('1.0', reference_content)
        ref_text.config(state='disabled')

    def update_instrument_list(self, event=None):
        """Update instrument list based on selected type"""
        selected_type = self.pip_type_var.get()
        if selected_type == 'All':
            instruments = list(self.trading_instruments.keys())
        else:
            instruments = self.get_instruments_by_type(selected_type)

        self.pip_instrument_combo['values'] = instruments
        if instruments:
            self.pip_instrument_var.set(instruments[0])

    def show_category(self, category):
        """Show instruments in selected category"""
        self.browser_text.delete('1.0', tk.END)

        if category == 'all':
            # Show all instruments organized by type
            content = "ALL TRADING INSTRUMENTS\n"
            content += "=" * 80 + "\n\n"

            types = {'forex': 'FOREX CURRENCIES', 'commodity': 'COMMODITIES', 
                    'index': 'STOCK INDICES', 'crypto': 'CRYPTOCURRENCIES', 'stock': 'INDIVIDUAL STOCKS'}

            for asset_type, title in types.items():
                content += f"{title}\n"
                content += "-" * len(title) + "\n"

                instruments = self.get_instruments_by_type(asset_type)
                for symbol in instruments:
                    info = self.trading_instruments[symbol]
                    rate = self.sample_rates.get(symbol, 'N/A')
                    content += f"{symbol:<12} | {info['category']:<20} | Rate: {rate}\n"
                content += "\n"
        else:
            # Show specific category
            instruments = []
            for symbol, info in self.trading_instruments.items():
                if info['category'] == category:
                    instruments.append(symbol)

            if instruments:
                content = f"{category.upper()}\n"
                content += "=" * len(category) + "\n\n"

                for symbol in sorted(instruments):
                    info = self.trading_instruments[symbol]
                    rate = self.sample_rates.get(symbol, 'N/A')
                    content += f"{symbol:<12} | Type: {info['type']:<10} | Rate: {rate:<12} | Min Lot: {info['min_lot']}\n"
            else:
                content = "No instruments found in this category."

        self.browser_text.insert('1.0', content)

    def calculate_pip_value(self):
        try:
            instrument = self.pip_instrument_var.get()
            position_size = float(self.pip_size_var.get())

            if instrument not in self.trading_instruments:
                messagebox.showerror("Error", f"Instrument {instrument} not supported")
                return

            info = self.trading_instruments[instrument]
            asset_type = info['type']
            pip_value_base = info['pip_value_base']
            point_value = info.get('point_value', 1.0)

            # Calculate based on asset type
            if asset_type == 'forex':
                # Forex calculation (lot-based)
                standard_lot_size = 100000
                total_position = standard_lot_size * position_size
                pip_value_quote = total_position * pip_value_base

                quote_currency = instrument[3:] if len(instrument) == 6 else 'USD'
                if quote_currency == 'USD':
                    pip_value_usd = pip_value_quote
                elif instrument in self.sample_rates:
                    if quote_currency == 'JPY':
                        pip_value_usd = pip_value_quote / self.sample_rates[instrument]
                    else:
                        pip_value_usd = pip_value_quote * self.sample_rates[instrument]
                else:
                    pip_value_usd = pip_value_quote

                unit_label = "lots"

            elif asset_type in ['commodity', 'index', 'crypto', 'stock']:
                # Point-based calculation
                pip_value_usd = pip_value_base * position_size * point_value
                pip_value_quote = pip_value_usd
                unit_label = "units" if asset_type != 'stock' else "shares"

            # Display results
            self.pip_result_text.delete('1.0', tk.END)
            result = f"""
{asset_type.upper()} VALUE CALCULATION RESULTS
{"=" * 60}

Instrument: {instrument}
Asset Type: {asset_type.title()}
Category: {info['category']}
Position Size: {position_size} {unit_label}
Current Rate: {self.sample_rates.get(instrument, 'N/A')}

POINT/PIP SPECIFICATIONS:
{"=" * 60}
Point/Pip Location: {info['pip_location']}{'th' if info['pip_location'] > 1 else 'st' if info['pip_location'] == 1 else 'nd' if info['pip_location'] == 2 else 'rd'} decimal place
Point/Pip Size: {pip_value_base}
Point Value Multiplier: {point_value}
Minimum Position: {info['min_lot']} {unit_label}

CALCULATED VALUES:
{"=" * 60}
Per Point/Pip Value: ${pip_value_usd:.2f}

SCENARIOS FOR {instrument}:
{"=" * 60}
• 1 point/pip move: ${pip_value_usd * 1:.2f}
• 5 point/pip move: ${pip_value_usd * 5:.2f}
• 10 point/pip move: ${pip_value_usd * 10:.2f}
• 25 point/pip move: ${pip_value_usd * 25:.2f}
• 50 point/pip move: ${pip_value_usd * 50:.2f}
• 100 point/pip move: ${pip_value_usd * 100:.2f}

POSITION SIZE ALTERNATIVES:
{"=" * 60}"""

            # Add position size alternatives based on asset type
            if asset_type == 'forex':
                alternatives = [0.01, 0.1, 1.0, 5.0, 10.0]
                for alt_size in alternatives:
                    if asset_type == 'forex':
                        alt_total = 100000 * alt_size
                        alt_pip_value = (alt_total * pip_value_base)
                        if quote_currency == 'USD':
                            alt_value_usd = alt_pip_value
                        elif instrument in self.sample_rates:
                            if quote_currency == 'JPY':
                                alt_value_usd = alt_pip_value / self.sample_rates[instrument]
                            else:
                                alt_value_usd = alt_pip_value * self.sample_rates[instrument]
                        else:
                            alt_value_usd = alt_pip_value

                    result += f"\n{alt_size} lots: ${alt_value_usd:.2f} per pip"
            else:
                alternatives = [0.1, 1.0, 5.0, 10.0, 100.0]
                for alt_size in alternatives:
                    alt_value = pip_value_base * alt_size * point_value
                    result += f"\n{alt_size} {unit_label}: ${alt_value:.2f} per point"

            result += f"""

TRADING CONSIDERATIONS:
{"=" * 60}
• Asset Class: {asset_type.title()}
• Typical Trading Hours: {"24/5" if asset_type == 'forex' else "24/7" if asset_type == 'crypto' else "Market Hours"}
• Volatility: {"Moderate" if asset_type == 'forex' else "High" if asset_type == 'crypto' else "Variable"}
• Leverage Available: {"High" if asset_type in ['forex', 'commodity', 'index'] else "Low/None" if asset_type == 'stock' else "Variable"}

⚠️  Note: Values calculated using sample rates.
Use real-time rates from your broker for actual trading.
            """
            self.pip_result_text.insert('1.0', result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def calculate_profit_loss(self):
        try:
            instrument = self.pl_instrument_var.get()
            entry_price = float(self.pl_entry_var.get())
            exit_price = float(self.pl_exit_var.get())
            position_size = float(self.pl_size_var.get())
            direction = self.pl_direction_var.get().lower()

            if instrument not in self.trading_instruments:
                messagebox.showerror("Error", f"Instrument {instrument} not supported")
                return

            info = self.trading_instruments[instrument]
            asset_type = info['type']
            pip_decimal_places = info['pip_location']

            # Calculate price difference
            price_diff = exit_price - entry_price
            if direction == 'sell':
                price_diff = -price_diff

            # Convert to points/pips
            points = price_diff * (10 ** pip_decimal_places)

            # Calculate point/pip value
            if asset_type == 'forex':
                standard_lot_size = 100000
                total_position = standard_lot_size * position_size
                pip_value_base = info['pip_value_base']
                pip_value_quote = total_position * pip_value_base

                quote_currency = instrument[3:] if len(instrument) == 6 else 'USD'
                if quote_currency == 'USD':
                    point_value_usd = pip_value_quote
                elif instrument in self.sample_rates:
                    if quote_currency == 'JPY':
                        point_value_usd = pip_value_quote / self.sample_rates[instrument]
                    else:
                        point_value_usd = pip_value_quote * self.sample_rates[instrument]
                else:
                    point_value_usd = pip_value_quote
            else:
                point_value_multiplier = info.get('point_value', 1.0)
                point_value_usd = info['pip_value_base'] * position_size * point_value_multiplier

            # Calculate P&L
            profit_loss = points * point_value_usd
            return_pct = (profit_loss / 10000) * 100  # Assuming $10k account

            # Display results
            self.pl_result_text.delete('1.0', tk.END)
            trade_status = "PROFITABLE" if profit_loss > 0 else "LOSS" if profit_loss < 0 else "BREAKEVEN"

            result = f"""
{asset_type.upper()} PROFIT/LOSS CALCULATION
{"=" * 60}

TRADE DETAILS:
Instrument: {instrument} ({info['category']})
Asset Type: {asset_type.title()}
Direction: {direction.upper()}
Entry Price: {entry_price}
Exit Price: {exit_price}
Position Size: {position_size} {"lots" if asset_type == 'forex' else "units" if asset_type != 'stock' else "shares"}

PRICE MOVEMENT:
{"=" * 60}
Price Difference: {price_diff:.6f}
Points/Pips: {points:.1f}
Point/Pip Value: ${point_value_usd:.2f}

FINANCIAL RESULT:
{"=" * 60}
PROFIT/LOSS: ${profit_loss:.2f}

TRADE OUTCOME: {trade_status}
Result: {'Profit' if profit_loss > 0 else 'Loss' if profit_loss < 0 else 'Breakeven'} of ${abs(profit_loss):.2f}
Return %: {return_pct:.2f}% (on $10k account)

ANALYSIS:
{"=" * 60}
• Points/Pips captured: {abs(points):.1f}
• Direction: {'Favorable' if profit_loss > 0 else 'Unfavorable' if profit_loss < 0 else 'Neutral'}
• Efficiency: ${abs(profit_loss/points if points != 0 else 0):.2f} per point

WHAT-IF SCENARIOS:
{"=" * 60}
If held for 10 more points in same direction: ${profit_loss + (10 * point_value_usd):.2f}
If held for 25 more points in same direction: ${profit_loss + (25 * point_value_usd):.2f}
If held for 50 more points in same direction: ${profit_loss + (50 * point_value_usd):.2f}

RISK METRICS:
{"=" * 60}
• Points risked: {abs(points):.1f}
• Value per point: ${point_value_usd:.2f}
• Asset volatility: {"High" if asset_type == 'crypto' else "Medium" if asset_type in ['commodity', 'index'] else "Low-Medium"}

⚠️  Calculations based on sample rates. Actual results may vary
with spreads, commissions, overnight fees, and real-time pricing.
            """
            self.pl_result_text.insert('1.0', result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def calculate_position_size(self):
        try:
            instrument = self.ps_instrument_var.get()
            account_balance = float(self.ps_balance_var.get())
            risk_percentage = float(self.ps_risk_pct_var.get())
            stop_loss_distance = float(self.ps_sl_var.get())

            if instrument not in self.trading_instruments:
                messagebox.showerror("Error", f"Instrument {instrument} not supported")
                return

            info = self.trading_instruments[instrument]
            asset_type = info['type']
            risk_amount = account_balance * (risk_percentage / 100)

            # Calculate point/pip value for minimum position
            min_position = info['min_lot']

            if asset_type == 'forex':
                standard_lot_size = 100000
                total_position = standard_lot_size * min_position
                pip_value_base = info['pip_value_base']
                pip_value_quote = total_position * pip_value_base

                quote_currency = instrument[3:] if len(instrument) == 6 else 'USD'
                if quote_currency == 'USD':
                    point_value_usd = pip_value_quote
                elif instrument in self.sample_rates:
                    if quote_currency == 'JPY':
                        point_value_usd = pip_value_quote / self.sample_rates[instrument]
                    else:
                        point_value_usd = pip_value_quote * self.sample_rates[instrument]
                else:
                    point_value_usd = pip_value_quote

                # Scale to 1 lot for calculation
                point_value_per_lot = point_value_usd / min_position
                unit_label = "lots"

            else:
                point_value_multiplier = info.get('point_value', 1.0)
                point_value_per_unit = info['pip_value_base'] * point_value_multiplier
                point_value_per_lot = point_value_per_unit
                unit_label = "units" if asset_type != 'stock' else "shares"

            # Calculate optimal position size
            optimal_position = risk_amount / (stop_loss_distance * point_value_per_lot)

            # Ensure minimum position size
            if optimal_position < info['min_lot']:
                optimal_position = info['min_lot']
                actual_risk = optimal_position * stop_loss_distance * point_value_per_lot
                actual_risk_pct = (actual_risk / account_balance) * 100
            else:
                actual_risk = risk_amount
                actual_risk_pct = risk_percentage

            # Calculate potential profit scenarios
            tp_scenarios = [
                ("1:1 Risk/Reward", stop_loss_distance, actual_risk),
                ("2:1 Risk/Reward", stop_loss_distance * 2, actual_risk * 2),
                ("3:1 Risk/Reward", stop_loss_distance * 3, actual_risk * 3)
            ]

            # Display results
            self.ps_result_text.delete('1.0', tk.END)
            result = f"""
{asset_type.upper()} POSITION SIZE CALCULATION
{"=" * 60}

ACCOUNT & RISK PARAMETERS:
Instrument: {instrument} ({info['category']})
Asset Type: {asset_type.title()}
Account Balance: ${account_balance:,.2f}
Target Risk %: {risk_percentage}%
Target Risk Amount: ${risk_amount:.2f}
Stop Loss Distance: {stop_loss_distance} points

INSTRUMENT SPECIFICATIONS:
{"=" * 60}
Minimum Position: {info['min_lot']} {unit_label}
Point Value (per {unit_label[:-1] if unit_label.endswith('s') else unit_label}): ${point_value_per_lot:.2f}
Current Price: {self.sample_rates.get(instrument, 'N/A')}

RECOMMENDED POSITION SIZE:
{"=" * 60}
Optimal Position: {optimal_position:.2f} {unit_label}
Actual Risk: ${actual_risk:.2f}
Actual Risk %: {actual_risk_pct:.2f}%

POSITION SIZE ALTERNATIVES:
{"=" * 60}
Conservative (50%): {optimal_position * 0.5:.2f} {unit_label}
Recommended (100%): {optimal_position:.2f} {unit_label}
Aggressive (150%): {optimal_position * 1.5:.2f} {unit_label}
Very Aggressive (200%): {optimal_position * 2.0:.2f} {unit_label}

RISK ANALYSIS:
{"=" * 60}
Maximum Loss (SL hit): ${actual_risk:.2f}
Remaining Balance: ${account_balance - actual_risk:,.2f}
Risk per Point: ${point_value_per_lot * optimal_position:.2f}

PROFIT POTENTIAL:
{"=" * 60}"""

            for scenario_name, tp_distance, profit_amount in tp_scenarios:
                result += f"\n{scenario_name} ({tp_distance:.0f} pts): +${profit_amount:.2f}"

            result += f"""

MARGIN REQUIREMENTS (Estimated):
{"=" * 60}"""

            if asset_type == 'forex':
                # Forex typically 1:100 leverage
                estimated_margin = (optimal_position * 100000 * self.sample_rates.get(instrument, 1)) / 100
                result += f"\nEstimated Margin (1:100): ${estimated_margin:,.2f}"
            elif asset_type in ['commodity', 'index']:
                # Commodities/indices vary widely
                result += f"\nMargin varies by broker and instrument"
            elif asset_type == 'crypto':
                # Crypto leverage varies
                result += f"\nCrypto margin varies (1:2 to 1:100)"
            else:  # stocks
                full_value = optimal_position * self.sample_rates.get(instrument, 100)
                result += f"\nFull Value (no leverage): ${full_value:,.2f}"

            result += f"""

Free Margin Available: ${account_balance - estimated_margin if asset_type == 'forex' else account_balance:,.2f}

ASSET-SPECIFIC CONSIDERATIONS:
{"=" * 60}"""

            if asset_type == 'forex':
                result += """
• 24/5 trading available
• High liquidity, tight spreads
• Economic news impacts prices
• Carry costs for overnight positions"""
            elif asset_type == 'commodity':
                result += """
• Supply/demand fundamentals important
• Weather and geopolitical events
• Storage and transportation costs
• Seasonal patterns may apply"""
            elif asset_type == 'index':
                result += """
• Reflects broader market sentiment
• Affected by economic indicators
• Lower volatility than individual stocks
• Good for trend following strategies"""
            elif asset_type == 'crypto':
                result += """
• 24/7 trading available
• Extremely high volatility
• Regulatory risks to consider
• Technology and adoption factors"""
            elif asset_type == 'stock':
                result += """
• Company fundamentals important
• Earnings reports cause volatility
• Dividend considerations
• Sector-specific factors"""

            result += f"""

RISK MANAGEMENT REMINDERS:
{"=" * 60}
• Never risk more than you can afford to lose
• Consider market volatility for this asset class
• Use proper stop losses on every trade
• Keep position sizes consistent with strategy
• Monitor economic calendars for major events
• Consider correlation with other positions

⚠️  Position size calculations are estimates. Always verify
with your broker's platform before placing trades.
            """

            self.ps_result_text.insert('1.0', result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except ZeroDivisionError:
            messagebox.showerror("Error", "Stop loss distance cannot be zero")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalTradingCalculatorGUI(root)
    root.mainloop()
