import tkinter as tk
from tkinter import ttk, messagebox
import math

class ForexPipsCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Forex Pips Calculator - Professional Trading Tool")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Custom.TLabel', background='#2c3e50', foreground='white')
        style.configure('Custom.TEntry', fieldbackground='white')
        style.configure('Custom.TCombobox', fieldbackground='white')

        # Major currency pairs and their specifications
        self.major_pairs = {
            'EURUSD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'GBPUSD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'AUDUSD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'NZDUSD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'USDCAD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'USDCHF': {'pip_location': 4, 'pip_value_base': 0.0001},
            'USDJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'EURJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'GBPJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'AUDJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'CADJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'CHFJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'NZDJPY': {'pip_location': 2, 'pip_value_base': 0.01},
            'EURGBP': {'pip_location': 4, 'pip_value_base': 0.0001},
            'EURAUD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'EURCHF': {'pip_location': 4, 'pip_value_base': 0.0001},
            'GBPAUD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'GBPCAD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'GBPCHF': {'pip_location': 4, 'pip_value_base': 0.0001},
            'AUDCAD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'AUDCHF': {'pip_location': 4, 'pip_value_base': 0.0001},
            'CADCHF': {'pip_location': 4, 'pip_value_base': 0.0001},
            'NZDCAD': {'pip_location': 4, 'pip_value_base': 0.0001},
            'NZDCHF': {'pip_location': 4, 'pip_value_base': 0.0001}
        }

        # Sample exchange rates (in real application, these would be live rates)
        self.sample_rates = {
            'EURUSD': 1.0900, 'GBPUSD': 1.2650, 'USDJPY': 147.50,
            'USDCAD': 1.3680, 'USDCHF': 0.8920, 'AUDUSD': 0.6720,
            'NZDUSD': 0.6150, 'EURJPY': 160.85, 'GBPJPY': 186.69,
            'AUDJPY': 99.13, 'EURGBP': 0.8617, 'EURAUD': 1.6220,
            'EURCHF': 0.9723, 'GBPAUD': 1.8820, 'GBPCAD': 1.7300,
            'GBPCHF': 1.1280, 'AUDCAD': 0.9200, 'AUDCHF': 0.6000,
            'CADCHF': 0.6520, 'CADJPY': 107.80, 'CHFJPY': 165.30,
            'NZDCAD': 0.8420, 'NZDCHF': 0.5490, 'NZDJPY': 90.80
        }

        self.setup_ui()

    def setup_ui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=15)

        title_label = ttk.Label(title_frame, text="Forex Pips Calculator Pro", style='Title.TLabel')
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="Professional Trading Tool", 
                                  font=('Arial', 10), background='#2c3e50', foreground='#bdc3c7')
        subtitle_label.pack()

        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=15, pady=10)

        # Tab 1: Pip Value Calculator
        self.pip_value_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(self.pip_value_frame, text='📊 Pip Value')
        self.setup_pip_value_tab()

        # Tab 2: Profit/Loss Calculator
        self.profit_loss_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(self.profit_loss_frame, text='💰 Profit/Loss')
        self.setup_profit_loss_tab()

        # Tab 3: Position Size Calculator
        self.position_size_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(self.position_size_frame, text='⚖️ Position Size')
        self.setup_position_size_tab()

        # Tab 4: Reference
        self.reference_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(self.reference_frame, text='📖 Reference')
        self.setup_reference_tab()

        # Footer
        footer_frame = tk.Frame(self.root, bg='#2c3e50')
        footer_frame.pack(side='bottom', fill='x', pady=5)

        footer_label = tk.Label(footer_frame, text="© 2025 Forex Pips Calculator - Always trade responsibly", 
                               bg='#2c3e50', fg='#95a5a6', font=('Arial', 8))
        footer_label.pack()

    def setup_pip_value_tab(self):
        # Input section
        input_frame = tk.LabelFrame(self.pip_value_frame, text="Calculate Pip Value", 
                                   bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        input_frame.pack(pady=20, padx=20, fill='x')

        # Currency pair selection
        ttk.Label(input_frame, text="Currency Pair:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.pip_pair_var = tk.StringVar(value='EURUSD')
        pip_pair_combo = ttk.Combobox(input_frame, textvariable=self.pip_pair_var, 
                                     values=list(self.major_pairs.keys()), style='Custom.TCombobox', width=15)
        pip_pair_combo.grid(row=0, column=1, padx=10, pady=8)

        # Lot size
        ttk.Label(input_frame, text="Lot Size:", style='Custom.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.pip_lot_var = tk.StringVar(value='1.0')
        pip_lot_entry = ttk.Entry(input_frame, textvariable=self.pip_lot_var, style='Custom.TEntry', width=15)
        pip_lot_entry.grid(row=1, column=1, padx=10, pady=8)

        # Quick lot size buttons
        lot_frame = tk.Frame(input_frame, bg='#34495e')
        lot_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(lot_frame, text="Micro (0.01)", command=lambda: self.pip_lot_var.set('0.01'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(lot_frame, text="Mini (0.1)", command=lambda: self.pip_lot_var.set('0.1'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(lot_frame, text="Standard (1.0)", command=lambda: self.pip_lot_var.set('1.0'),
                 bg='#95a5a6', fg='black', font=('Arial', 8)).pack(side='left', padx=2)

        # Calculate button
        calculate_pip_btn = tk.Button(input_frame, text="Calculate Pip Value", 
                                     command=self.calculate_pip_value,
                                     bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                                     relief='raised', bd=3)
        calculate_pip_btn.grid(row=3, column=0, columnspan=2, pady=15)

        # Results section
        self.pip_result_frame = tk.LabelFrame(self.pip_value_frame, text="Results", 
                                            bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
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
                                   bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        input_frame.pack(pady=20, padx=20, fill='x')

        # Currency pair
        ttk.Label(input_frame, text="Currency Pair:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.pl_pair_var = tk.StringVar(value='EURUSD')
        pl_pair_combo = ttk.Combobox(input_frame, textvariable=self.pl_pair_var,
                                    values=list(self.major_pairs.keys()), style='Custom.TCombobox', width=15)
        pl_pair_combo.grid(row=0, column=1, padx=10, pady=8)

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

        # Lot size
        ttk.Label(input_frame, text="Lot Size:", style='Custom.TLabel').grid(row=3, column=0, sticky='w', padx=10, pady=8)
        self.pl_lot_var = tk.StringVar(value='1.0')
        pl_lot_entry = ttk.Entry(input_frame, textvariable=self.pl_lot_var, style='Custom.TEntry', width=15)
        pl_lot_entry.grid(row=3, column=1, padx=10, pady=8)

        # Trade direction
        ttk.Label(input_frame, text="Trade Direction:", style='Custom.TLabel').grid(row=4, column=0, sticky='w', padx=10, pady=8)
        self.pl_direction_var = tk.StringVar(value='Buy')
        pl_direction_combo = ttk.Combobox(input_frame, textvariable=self.pl_direction_var,
                                         values=['Buy', 'Sell'], style='Custom.TCombobox', width=15)
        pl_direction_combo.grid(row=4, column=1, padx=10, pady=8)

        # Calculate button
        calculate_pl_btn = tk.Button(input_frame, text="Calculate Profit/Loss",
                                    command=self.calculate_profit_loss,
                                    bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                                    relief='raised', bd=3)
        calculate_pl_btn.grid(row=5, column=0, columnspan=2, pady=15)

        # Results section
        self.pl_result_frame = tk.LabelFrame(self.profit_loss_frame, text="Results",
                                           bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
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
                                   bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        input_frame.pack(pady=20, padx=20, fill='x')

        # Currency pair
        ttk.Label(input_frame, text="Currency Pair:", style='Custom.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.ps_pair_var = tk.StringVar(value='EURUSD')
        ps_pair_combo = ttk.Combobox(input_frame, textvariable=self.ps_pair_var,
                                    values=list(self.major_pairs.keys()), style='Custom.TCombobox', width=15)
        ps_pair_combo.grid(row=0, column=1, padx=10, pady=8)

        # Account balance
        ttk.Label(input_frame, text="Account Balance ($):", style='Custom.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.ps_balance_var = tk.StringVar(value='10000')
        ps_balance_entry = ttk.Entry(input_frame, textvariable=self.ps_balance_var, style='Custom.TEntry', width=15)
        ps_balance_entry.grid(row=1, column=1, padx=10, pady=8)

        # Risk percentage
        ttk.Label(input_frame, text="Risk Percentage (%):", style='Custom.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=8)
        self.ps_risk_pct_var = tk.StringVar(value='2')
        ps_risk_pct_entry = ttk.Entry(input_frame, textvariable=self.ps_risk_pct_var, style='Custom.TEntry', width=15)
        ps_risk_pct_entry.grid(row=2, column=1, padx=10, pady=8)

        # Stop loss pips
        ttk.Label(input_frame, text="Stop Loss (pips):", style='Custom.TLabel').grid(row=3, column=0, sticky='w', padx=10, pady=8)
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
                                           bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        self.ps_result_frame.pack(pady=10, padx=20, fill='both', expand=True)

        self.ps_result_text = tk.Text(self.ps_result_frame, height=12, bg='white',
                                     font=('Consolas', 10), wrap='word')
        scrollbar_ps = tk.Scrollbar(self.ps_result_frame, orient='vertical', command=self.ps_result_text.yview)
        self.ps_result_text.configure(yscrollcommand=scrollbar_ps.set)

        self.ps_result_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_ps.pack(side='right', fill='y')

    def setup_reference_tab(self):
        # Reference information
        ref_text = tk.Text(self.reference_frame, bg='white', font=('Consolas', 9), wrap='word')
        scrollbar_ref = tk.Scrollbar(self.reference_frame, orient='vertical', command=ref_text.yview)
        ref_text.configure(yscrollcommand=scrollbar_ref.set)

        ref_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_ref.pack(side='right', fill='y')

        reference_content = """FOREX PIPS CALCULATOR - PROFESSIONAL REFERENCE GUIDE

═══════════════════════════════════════════════════════════════════════════════

📊 PIP DEFINITIONS
═══════════════════════════════════════════════════════════════════════════════
• Standard Pairs (4th decimal): EUR/USD, GBP/USD, AUD/USD, etc. - 1 pip = 0.0001
• JPY Pairs (2nd decimal): USD/JPY, EUR/JPY, GBP/JPY, etc. - 1 pip = 0.01
• Pipettes (fractional pips): 0.00001 for standard pairs, 0.001 for JPY pairs

📏 LOT SIZES
═══════════════════════════════════════════════════════════════════════════════
• Standard Lot = 100,000 units of base currency
• Mini Lot = 10,000 units (0.1 standard lot)
• Micro Lot = 1,000 units (0.01 standard lot)
• Nano Lot = 100 units (0.001 standard lot)

🧮 CALCULATION FORMULAS
═══════════════════════════════════════════════════════════════════════════════

Pip Value Calculation:
• For XXX/USD pairs: (Pip Size × Lot Size × 100,000)
• For USD/XXX pairs: (Pip Size × Lot Size × 100,000) ÷ Exchange Rate
• For Cross pairs: (Pip Size × Lot Size × 100,000) × XXX/USD Rate

Profit/Loss Calculation:
• Pips = (Exit Price - Entry Price) × 10^(decimal places)
• For SELL trades: Pips = (Entry Price - Exit Price) × 10^(decimal places)
• P&L = Pips × Pip Value × Lot Size

Position Size Calculation:
• Risk Amount = Account Balance × Risk Percentage
• Position Size (lots) = Risk Amount ÷ (Stop Loss Pips × Pip Value per Lot)

💰 SAMPLE PIP VALUES (USD Account)
═══════════════════════════════════════════════════════════════════════════════
Currency Pair    Standard Lot    Mini Lot    Micro Lot    Nano Lot
EUR/USD         $10.00          $1.00       $0.10        $0.01
GBP/USD         $10.00          $1.00       $0.10        $0.01
USD/JPY         $6.78           $0.68       $0.07        $0.007
USD/CAD         $13.68          $1.37       $0.14        $0.014
USD/CHF         $8.92           $0.89       $0.09        $0.009
AUD/USD         $10.00          $1.00       $0.10        $0.01

⚖️ RISK MANAGEMENT GUIDELINES
═══════════════════════════════════════════════════════════════════════════════
Conservative Trading: Risk 1-2% of account per trade
Moderate Trading: Risk 2-3% of account per trade
Aggressive Trading: Risk 3-5% of account per trade

⚠️  NEVER risk more than 10% of your account on a single trade!

🎯 STOP LOSS RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════════════════
Scalping: 5-15 pips (very short-term, minutes to hours)
Day Trading: 15-30 pips (intraday, closed by end of day)
Swing Trading: 30-100 pips (few days to weeks)
Position Trading: 100+ pips (weeks to months)

🌍 SUPPORTED CURRENCY PAIRS
═══════════════════════════════════════════════════════════════════════════════
Major Pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, USD/CAD, AUD/USD, NZD/USD
JPY Crosses: EUR/JPY, GBP/JPY, AUD/JPY, CAD/JPY, CHF/JPY, NZD/JPY
Major Crosses: EUR/GBP, EUR/AUD, EUR/CHF, GBP/AUD, GBP/CAD, GBP/CHF
Other Crosses: AUD/CAD, AUD/CHF, CAD/CHF, NZD/CAD, NZD/CHF

💡 TRADING TIPS
═══════════════════════════════════════════════════════════════════════════════
1. Always use stop losses to protect your capital
2. Never risk more than you can afford to lose
3. Keep a trading journal to track performance
4. Use proper position sizing based on account balance
5. Consider market volatility when setting stop losses
6. Practice with demo accounts before live trading
7. Stay informed about economic news and events
8. Diversify your trades across different currency pairs
9. Use take profit levels to secure gains
10. Review and adjust your risk management regularly

📈 MARKET SESSIONS
═══════════════════════════════════════════════════════════════════════════════
Sydney Session: 22:00 - 07:00 GMT
Tokyo Session: 00:00 - 09:00 GMT
London Session: 08:00 - 17:00 GMT
New York Session: 13:00 - 22:00 GMT

Best Trading Times:
• London-New York Overlap: 13:00 - 17:00 GMT (Highest volatility)
• Tokyo-London Overlap: 08:00 - 09:00 GMT (Good for JPY pairs)

⚠️  DISCLAIMER
═══════════════════════════════════════════════════════════════════════════════
This calculator uses sample exchange rates for demonstration purposes.
For live trading, always use real-time rates from your broker.

Trading forex involves substantial risk of loss and may not be suitable
for all investors. Past performance is not indicative of future results.
Always practice proper risk management and never trade with money you
cannot afford to lose.

© 2025 Forex Pips Calculator Pro - Trade Responsibly
        """

        ref_text.insert('1.0', reference_content)
        ref_text.config(state='disabled')

    def calculate_pip_value(self):
        try:
            pair = self.pip_pair_var.get()
            lot_size = float(self.pip_lot_var.get())

            if pair not in self.major_pairs:
                messagebox.showerror("Error", f"Currency pair {pair} not supported")
                return

            pair_info = self.major_pairs[pair]
            base_currency = pair[:3]
            quote_currency = pair[3:]

            # Standard lot size is 100,000 units
            position_size = 100000 * lot_size
            pip_value_base = pair_info['pip_value_base']

            # Calculate pip value in quote currency
            pip_value_quote = position_size * pip_value_base

            # Calculate pip value in USD
            if quote_currency == 'USD':
                pip_value_usd = pip_value_quote
            elif pair in self.sample_rates:
                if quote_currency == 'JPY':
                    pip_value_usd = pip_value_quote / self.sample_rates[pair]
                else:
                    pip_value_usd = pip_value_quote * self.sample_rates[pair]
            else:
                pip_value_usd = pip_value_quote

            # Display results
            self.pip_result_text.delete('1.0', tk.END)
            result = f"""
PIP VALUE CALCULATION RESULTS
════════════════════════════════════════════════════════════════

Currency Pair: {pair}
Base Currency: {base_currency}
Quote Currency: {quote_currency}
Lot Size: {lot_size}
Position Size: {position_size:,} units

Pip Specifications:
• Pip Location: {pair_info['pip_location']}{'th' if pair_info['pip_location'] == 4 else 'nd'} decimal place
• Pip Size: {pair_info['pip_value_base']}
• Exchange Rate Used: {self.sample_rates.get(pair, 'N/A')}

Pip Value Results:
• Pip Value (Quote Currency): {pip_value_quote} {quote_currency}
• Pip Value (USD): ${pip_value_usd:.2f}

QUICK REFERENCE FOR {pair}:
════════════════════════════════════════════════════════════════
Standard Lot (1.0): ${pip_value_usd:.2f} per pip
Mini Lot (0.1): ${pip_value_usd/10:.2f} per pip  
Micro Lot (0.01): ${pip_value_usd/100:.2f} per pip
Nano Lot (0.001): ${pip_value_usd/1000:.3f} per pip

EXAMPLE CALCULATIONS:
════════════════════════════════════════════════════════════════
• 10 pips profit = ${pip_value_usd*10:.2f}
• 25 pips profit = ${pip_value_usd*25:.2f}
• 50 pips profit = ${pip_value_usd*50:.2f}
• 100 pips profit = ${pip_value_usd*100:.2f}

⚠️  Note: Values calculated using sample exchange rates.
For live trading, use real-time rates from your broker.
            """
            self.pip_result_text.insert('1.0', result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def calculate_profit_loss(self):
        try:
            pair = self.pl_pair_var.get()
            entry_price = float(self.pl_entry_var.get())
            exit_price = float(self.pl_exit_var.get())
            lot_size = float(self.pl_lot_var.get())
            direction = self.pl_direction_var.get().lower()

            if pair not in self.major_pairs:
                messagebox.showerror("Error", f"Currency pair {pair} not supported")
                return

            pair_info = self.major_pairs[pair]
            pip_decimal_places = pair_info['pip_location']

            # Calculate price difference
            price_diff = exit_price - entry_price

            if direction == 'sell':
                price_diff = -price_diff

            # Convert price difference to pips
            pips = price_diff * (10 ** pip_decimal_places)

            # Calculate pip value
            position_size = 100000 * lot_size
            pip_value_base = pair_info['pip_value_base']
            pip_value_quote = position_size * pip_value_base

            quote_currency = pair[3:]
            if quote_currency == 'USD':
                pip_value_usd = pip_value_quote
            elif pair in self.sample_rates:
                if quote_currency == 'JPY':
                    pip_value_usd = pip_value_quote / self.sample_rates[pair]
                else:
                    pip_value_usd = pip_value_quote * self.sample_rates[pair]
            else:
                pip_value_usd = pip_value_quote

            # Calculate profit/loss
            profit_loss = pips * pip_value_usd

            # Calculate return percentage (assuming $10,000 account)
            return_pct = (profit_loss / 10000) * 100

            # Display results
            self.pl_result_text.delete('1.0', tk.END)
            trade_status = "PROFITABLE" if profit_loss > 0 else "LOSS-MAKING" if profit_loss < 0 else "BREAKEVEN"
            result_color = "GREEN" if profit_loss > 0 else "RED" if profit_loss < 0 else "YELLOW"

            result = f"""
PROFIT/LOSS CALCULATION RESULTS
════════════════════════════════════════════════════════════════

TRADE DETAILS:
Currency Pair: {pair}
Trade Direction: {direction.upper()}
Entry Price: {entry_price}
Exit Price: {exit_price}
Lot Size: {lot_size}
Position Size: {100000 * lot_size:,} units

PRICE MOVEMENT:
Price Difference: {price_diff:.5f}
Pips Gained/Lost: {pips:.1f} pips
Pip Value: ${pip_value_usd:.2f} per pip

FINANCIAL RESULT:
════════════════════════════════════════════════════════════════
PROFIT/LOSS: ${profit_loss:.2f}

TRADE SUMMARY: {trade_status} TRADE
Result: {'Gain' if profit_loss > 0 else 'Loss' if profit_loss < 0 else 'No change'} of ${abs(profit_loss):.2f}
Return %: {return_pct:.2f}% (based on $10,000 account)

RISK/REWARD ANALYSIS:
════════════════════════════════════════════════════════════════
• Per pip value: ${pip_value_usd:.2f}
• Total pips: {abs(pips):.1f}
• Direction: {'Profitable' if profit_loss > 0 else 'Loss' if profit_loss < 0 else 'Breakeven'}

WHAT IF SCENARIOS:
════════════════════════════════════════════════════════════════
If 10 more pips in same direction: ${profit_loss + (10 * pip_value_usd):.2f}
If 20 more pips in same direction: ${profit_loss + (20 * pip_value_usd):.2f}
If 50 more pips in same direction: ${profit_loss + (50 * pip_value_usd):.2f}

⚠️  Note: Calculation uses sample exchange rates.
Actual results may vary based on real-time rates, spreads, and commissions.
            """
            self.pl_result_text.insert('1.0', result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def calculate_position_size(self):
        try:
            pair = self.ps_pair_var.get()
            account_balance = float(self.ps_balance_var.get())
            risk_percentage = float(self.ps_risk_pct_var.get())
            stop_loss_pips = float(self.ps_sl_var.get())

            if pair not in self.major_pairs:
                messagebox.showerror("Error", f"Currency pair {pair} not supported")
                return

            # Calculate risk amount
            risk_amount = account_balance * (risk_percentage / 100)

            # Calculate pip value for 1 standard lot
            pair_info = self.major_pairs[pair]
            position_size = 100000  # 1 standard lot
            pip_value_base = pair_info['pip_value_base']
            pip_value_quote = position_size * pip_value_base

            quote_currency = pair[3:]
            if quote_currency == 'USD':
                pip_value_usd = pip_value_quote
            elif pair in self.sample_rates:
                if quote_currency == 'JPY':
                    pip_value_usd = pip_value_quote / self.sample_rates[pair]
                else:
                    pip_value_usd = pip_value_quote * self.sample_rates[pair]
            else:
                pip_value_usd = pip_value_quote

            # Calculate position size
            position_size_lots = risk_amount / (stop_loss_pips * pip_value_usd)
            position_size_units = position_size_lots * 100000

            # Calculate potential scenarios
            potential_loss = stop_loss_pips * pip_value_usd * position_size_lots

            # Calculate take profit scenarios
            tp_1_to_1 = stop_loss_pips * pip_value_usd * position_size_lots  # 1:1 RR
            tp_2_to_1 = stop_loss_pips * 2 * pip_value_usd * position_size_lots  # 2:1 RR
            tp_3_to_1 = stop_loss_pips * 3 * pip_value_usd * position_size_lots  # 3:1 RR

            # Display results
            self.ps_result_text.delete('1.0', tk.END)
            result = f"""
POSITION SIZE CALCULATION RESULTS
════════════════════════════════════════════════════════════════

ACCOUNT INFORMATION:
Currency Pair: {pair}
Account Balance: ${account_balance:,.2f}
Risk Percentage: {risk_percentage}%
Risk Amount: ${risk_amount:.2f}
Stop Loss Distance: {stop_loss_pips} pips

PIP VALUE INFORMATION:
Pip Value (1 lot): ${pip_value_usd:.2f}
Exchange Rate Used: {self.sample_rates.get(pair, 'N/A')}

RECOMMENDED POSITION SIZE:
════════════════════════════════════════════════════════════════
Optimal Lot Size: {position_size_lots:.2f} lots
Position in Units: {position_size_units:,.0f} units

RISK ANALYSIS:
════════════════════════════════════════════════════════════════
Maximum Loss (if SL hit): ${potential_loss:.2f}
Risk as % of Account: {risk_percentage}%
Remaining Balance (worst case): ${account_balance - potential_loss:,.2f}

POSITION SIZE ALTERNATIVES:
════════════════════════════════════════════════════════════════
Conservative (50%): {position_size_lots*0.5:.2f} lots
Recommended (100%): {position_size_lots:.2f} lots
Aggressive (150%): {position_size_lots*1.5:.2f} lots

LOT SIZE BREAKDOWN:
════════════════════════════════════════════════════════════════
Standard lots: {int(position_size_lots)}
Mini lots: {int((position_size_lots % 1) * 10)}
Micro lots: {int(((position_size_lots % 1) * 10 % 1) * 10)}
Remaining: {((position_size_lots % 0.01) * 1000):.0f} nano lots

PROFIT POTENTIAL (Risk:Reward Scenarios):
════════════════════════════════════════════════════════════════
1:1 Risk/Reward ({stop_loss_pips} pips TP): +${tp_1_to_1:.2f}
2:1 Risk/Reward ({stop_loss_pips*2} pips TP): +${tp_2_to_1:.2f}
3:1 Risk/Reward ({stop_loss_pips*3} pips TP): +${tp_3_to_1:.2f}

MARGIN REQUIREMENT (1:100 leverage):
════════════════════════════════════════════════════════════════
Estimated Margin: ${position_size_units / 100:,.2f}
Free Margin: ${account_balance - (position_size_units / 100):,.2f}

RISK MANAGEMENT REMINDERS:
════════════════════════════════════════════════════════════════
• Never risk more than 2-3% per trade
• Use proper stop losses on every trade
• Consider market volatility and news events
• Review position size before entering trade
• Keep a trading journal for performance tracking

⚠️  Always verify calculations with your broker's platform
before placing trades. Consider spreads and commissions.
            """
            self.ps_result_text.insert('1.0', result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except ZeroDivisionError:
            messagebox.showerror("Error", "Stop loss cannot be zero")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ForexPipsCalculatorGUI(root)
    root.mainloop()
