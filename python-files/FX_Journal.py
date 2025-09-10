import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import pandas as pd
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from typing import Dict, List, Optional
import calendar
import math

class ForexTradingJournalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kaluwal FX Journal")
        self.root.geometry("800x717")
        self.root.minsize(600, 500)
        
        # Configure consistent background color
        self.bg_color = '#f0f0f0'
        self.root.configure(bg=self.bg_color)
        
        # Prevent window size changes
        self.root.resizable(True, True)
        
        # Setup custom styles first
        self.setup_styles()
        
        # Initialize flags
        self._closing = False
        
        # Data storage
        self.journal_file = "forex_journal.json"
        self.trades = self.load_journal()
        
        # Create main interface
        self.create_widgets()
        
        # Defer heavy operations
        self.root.after(100, self.delayed_init)
        
        # Add developer credit
        self.add_developer_credit()
        
    def delayed_init(self):
        """Initialize heavy operations after UI is shown"""
        self.refresh_trades_view()
        self.update_statistics()
        
    def load_journal(self) -> List[Dict]:
        """Load existing trades from JSON file with error recovery"""
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r') as f:
                    data = json.load(f)
                    # Validate data structure
                    if isinstance(data, list):
                        return data
                    else:
                        return []
            except (json.JSONDecodeError, FileNotFoundError, MemoryError) as e:
                # Try to load backup if main file is corrupted
                backup_file = f"{self.journal_file}.backup"
                if os.path.exists(backup_file):
                    try:
                        with open(backup_file, 'r') as f:
                            return json.load(f)
                    except:
                        pass
                messagebox.showwarning("Load Warning", f"Journal file corrupted, starting fresh: {str(e)}")
                return []
        return []
    
    def save_journal(self):
        """Save trades to JSON file with error handling"""
        try:
            # Create backup before saving
            if os.path.exists(self.journal_file):
                backup_file = f"{self.journal_file}.backup"
                import shutil
                shutil.copy2(self.journal_file, backup_file)
            
            with open(self.journal_file, 'w') as f:
                json.dump(self.trades, f, indent=2, default=str)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save journal: {str(e)}")
    
    def save_journal_as(self):
        """Save journal to a new file location"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Journal As",
            initialfile="Kaluwal_FX_Journal"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.trades, f, indent=2, default=str)
                self.journal_file = filename
                self.root.title(f"Kaluwal FX Journal - {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Journal saved as: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save journal: {str(e)}")
    
    def setup_styles(self):
        """Setup custom styles for tabs and widgets"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure tab styles with color highlighting
        self.style.configure('TNotebook', background=self.bg_color, tabposition='n')
        self.style.configure('TNotebook.Tab', 
                           padding=[15, 8], 
                           background='#e1e1e1',
                           foreground='#333333',
                           focuscolor='none')
        
        # Active/selected tab style
        self.style.map('TNotebook.Tab',
                      background=[('selected', '#0078d4'),
                                ('active', '#005a9e')],
                      foreground=[('selected', 'white'),
                                ('active', 'white')])
        
        # Configure other styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabelFrame', background=self.bg_color)
    
    def on_tab_changed(self, event):
        """Handle tab change events"""
        # Maintain window size when switching tabs
        current_geometry = self.root.geometry()
        self.root.after_idle(lambda: self.root.geometry(current_geometry))
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive design"""
        if event.widget == self.root:
            # Update background color consistency
            self.root.configure(bg=self.bg_color)
            # Force update of all child widgets
            self.root.update_idletasks()
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create main container with consistent background
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure grid weights for responsive behavior
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create notebook for tabs with consistent styling
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Bind tab selection event for color highlighting
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Create tabs
        self.create_add_trade_tab()
        self.create_view_trades_tab()
        self.create_statistics_tab()
        self.create_charts_tab()
        self.create_analysis_tab()
        self.create_calculator_tab()
        self.create_world_clock_tab()
        
    def create_add_trade_tab(self):
        """Create the add trade tab"""
        add_frame = ttk.Frame(self.notebook)
        self.notebook.add(add_frame, text="Add Trade")
        
        # Configure frame for responsive behavior
        add_frame.grid_rowconfigure(0, weight=1)
        add_frame.grid_columnconfigure(0, weight=1)
        
        # Main container with responsive grid
        container = ttk.Frame(add_frame)
        container.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame with consistent background
        canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure responsive grid for canvas and scrollbar
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Developer credit at bottom
        credit_frame = ttk.Frame(scrollable_frame)
        credit_frame.pack(side='bottom', fill='x', pady=5)
        ttk.Label(credit_frame, text="Developed by WASEEM KALUWAL", 
                 font=('Arial', 8), foreground='#666666').pack(side='right', padx=10)
        
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Configure grid weights for main_frame
        for i in range(5):
            main_frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            main_frame.grid_columnconfigure(i, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add New Trade", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Trade details frame
        details_frame = ttk.LabelFrame(main_frame, text="Trade Details", padding=15)
        details_frame.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        
        # Configure grid weights for details_frame
        for i in range(4):
            details_frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            details_frame.grid_columnconfigure(i, weight=1)
        
        # Entry fields
        ttk.Label(details_frame, text="Currency Pair:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.pair_var = tk.StringVar()
        pair_combo = ttk.Combobox(details_frame, textvariable=self.pair_var, width=15)
        pair_combo['values'] = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        pair_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(details_frame, text="Direction:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.direction_var = tk.StringVar(value='long')
        direction_combo = ttk.Combobox(details_frame, textvariable=self.direction_var, width=10)
        direction_combo['values'] = ['long', 'short']
        direction_combo.grid(row=0, column=3)
        
        ttk.Label(details_frame, text="Entry Price:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.entry_price_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.entry_price_var, width=15).grid(row=1, column=1, pady=(10, 0), padx=(0, 20))
        
        ttk.Label(details_frame, text="Exit Price:").grid(row=1, column=2, sticky='w', padx=(0, 10), pady=(10, 0))
        self.exit_price_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.exit_price_var, width=15).grid(row=1, column=3, pady=(10, 0))
        
        ttk.Label(details_frame, text="Position Size (lots):").grid(row=2, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.position_size_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.position_size_var, width=15).grid(row=2, column=1, pady=(10, 0), padx=(0, 20))
        
        ttk.Label(details_frame, text="Commission:").grid(row=2, column=2, sticky='w', padx=(0, 10), pady=(10, 0))
        self.commission_var = tk.StringVar(value='0')
        ttk.Entry(details_frame, textvariable=self.commission_var, width=15).grid(row=2, column=3, pady=(10, 0))
        
        ttk.Label(details_frame, text="Trade Date:").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.trade_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(details_frame, textvariable=self.trade_date_var, width=15).grid(row=3, column=1, pady=(10, 0), padx=(0, 20))
        ttk.Button(details_frame, text="📅", command=self.open_calendar, width=3).grid(row=3, column=2, pady=(10, 0), sticky='w', padx=(0, 5))
        ttk.Button(details_frame, text="Today", command=self.set_today_date, width=8).grid(row=3, column=3, pady=(10, 0), sticky='w')
        
        # Optional details frame
        optional_frame = ttk.LabelFrame(main_frame, text="Optional Details", padding=15)
        optional_frame.grid(row=2, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        
        # Configure grid weights for optional_frame
        for i in range(6):
            optional_frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            optional_frame.grid_columnconfigure(i, weight=1)
        
        ttk.Label(optional_frame, text="Stop Loss:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.stop_loss_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.stop_loss_var, width=15).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(optional_frame, text="Take Profit:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.take_profit_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.take_profit_var, width=15).grid(row=0, column=3)
        
        ttk.Label(optional_frame, text="Strategy:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.strategy_var = tk.StringVar()
        strategy_combo = ttk.Combobox(optional_frame, textvariable=self.strategy_var, width=15)
        strategy_combo['values'] = ['Silver Bullet', 'ICT 2022', 'Turtle Soup', '9am Setup', '5am Setup', '1am Setup', 'Breakout', 'Trend Following', 'Scalping', 'Support/Resistance', 'News Trading', 'Order Block', 'Fair Value Gap', 'Liquidity Grab', 'Market Structure Shift', 'Optimal Trade Entry', 'Custom...']
        strategy_combo.grid(row=1, column=1, pady=(10, 0), padx=(0, 20))
        strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_select)
        
        ttk.Label(optional_frame, text="Setup Rating (1-5):").grid(row=1, column=2, sticky='w', padx=(0, 10), pady=(10, 0))
        self.setup_rating_var = tk.StringVar()
        rating_combo = ttk.Combobox(optional_frame, textvariable=self.setup_rating_var, width=15)
        rating_combo['values'] = ['1', '2', '3', '4', '5']
        rating_combo.grid(row=1, column=3, pady=(10, 0))
        
        ttk.Label(optional_frame, text="Opening Balance:").grid(row=2, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.opening_balance_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.opening_balance_var, width=15).grid(row=2, column=1, pady=(10, 0), padx=(0, 20))
        
        ttk.Label(optional_frame, text="Closing Balance:").grid(row=2, column=2, sticky='w', padx=(0, 10), pady=(10, 0))
        self.closing_balance_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.closing_balance_var, width=15).grid(row=2, column=3, pady=(10, 0))
        
        ttk.Label(optional_frame, text="Chart Screenshot:").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        chart_frame = ttk.Frame(optional_frame)
        chart_frame.grid(row=3, column=1, columnspan=3, pady=(10, 0), sticky='ew')
        
        self.chart_path_var = tk.StringVar()
        chart_entry = ttk.Entry(chart_frame, textvariable=self.chart_path_var, width=40, state='readonly')
        chart_entry.pack(side='left', padx=(0, 5))
        ttk.Button(chart_frame, text="Browse", command=self.browse_chart, width=8).pack(side='left', padx=(0, 5))
        ttk.Button(chart_frame, text="Clear", command=self.clear_chart, width=6).pack(side='left')
        
        ttk.Label(optional_frame, text="Notes:").grid(row=4, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.notes_text = tk.Text(optional_frame, height=3, width=60)
        self.notes_text.grid(row=5, column=0, columnspan=4, pady=(5, 0), sticky='ew')
        
        # Configure scroll region with responsive behavior
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make canvas content responsive to window width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_frame, width=canvas_width)
        
        def on_canvas_configure(event):
            configure_scroll_region()
        
        scrollable_frame.bind("<Configure>", on_canvas_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="Add Trade", command=self.add_trade, 
                  style='Accent.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side='left')
        
    def create_view_trades_tab(self):
        """Create the view trades tab"""
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text="View Trades")
        
        # Configure responsive grid weights
        view_frame.grid_rowconfigure(0, weight=0)  # Controls
        view_frame.grid_rowconfigure(1, weight=1)  # Tree view
        view_frame.grid_rowconfigure(2, weight=0)  # Notes
        view_frame.grid_columnconfigure(0, weight=1)
        
        # Controls frame
        controls_frame = ttk.Frame(view_frame)
        controls_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Filter by Pair:").pack(side='left', padx=(0, 5))
        self.filter_pair_var = tk.StringVar(value='All')
        filter_combo = ttk.Combobox(controls_frame, textvariable=self.filter_pair_var, width=10)
        filter_combo['values'] = ['All'] + ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        filter_combo.pack(side='left', padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_trades_view())
        
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_trades_view).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Export CSV", command=self.export_csv).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Save As", command=self.save_journal_as).pack(side='left')
        ttk.Button(controls_frame, text="View Chart", command=self.view_chart).pack(side='right', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit Selected", command=self.edit_trade).pack(side='right', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete Selected", command=self.delete_trade).pack(side='right')
        
        # Trades treeview
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        
        # Configure grid weights for tree_frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('Date', 'ID', 'Pair', 'Direction', 'Entry', 'Exit', 'P&L', 'Pips', 'Rating', 'Strategy')
        self.trades_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.trades_tree.heading(col, text=col)
            if col == 'P&L':
                self.trades_tree.column(col, width=80, anchor='center')
            elif col == 'Pips':
                self.trades_tree.column(col, width=60, anchor='center')
            elif col == 'Rating':
                self.trades_tree.column(col, width=50, anchor='center')
            else:
                self.trades_tree.column(col, width=80, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.trades_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.trades_tree.xview)
        self.trades_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.trades_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Bind selection event to show notes
        self.trades_tree.bind('<<TreeviewSelect>>', self.on_trade_select)
        
        # Notes section
        notes_frame = ttk.LabelFrame(view_frame, text="Trade Notes", padding=10)
        notes_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))
        
        # Configure grid weights for notes_frame
        notes_frame.grid_rowconfigure(0, weight=1)
        notes_frame.grid_columnconfigure(0, weight=1)
        
        self.notes_display = tk.Text(notes_frame, height=4, width=80, state='disabled', 
                                    font=('Arial', 10), wrap='word')
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient='vertical', command=self.notes_display.yview)
        self.notes_display.configure(yscrollcommand=notes_scrollbar.set)
        
        self.notes_display.grid(row=0, column=0, sticky='nsew')
        notes_scrollbar.grid(row=0, column=1, sticky='ns')
        
    def create_statistics_tab(self):
        """Create the statistics tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        # Configure responsive grid weights
        stats_frame.grid_rowconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Create responsive scrollable frame
        canvas = tk.Canvas(stats_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Responsive statistics display
        self.stats_text = tk.Text(scrollable_frame, font=('Courier', 11), state='disabled', 
                                 wrap='word', bg='white')
        self.stats_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        canvas.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Responsive scroll region configuration
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_frame, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
    def create_charts_tab(self):
        """Create the charts tab"""
        charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(charts_frame, text="Charts")
        
        # Configure responsive grid weights
        charts_frame.grid_rowconfigure(0, weight=0)  # Controls
        charts_frame.grid_rowconfigure(1, weight=1)  # Chart area
        charts_frame.grid_columnconfigure(0, weight=1)
        
        # Chart controls with responsive layout
        controls_frame = ttk.Frame(charts_frame)
        controls_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Button(controls_frame, text="P&L Curve", command=self.plot_pnl_curve).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="Monthly Performance", command=self.plot_monthly_performance).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="Win/Loss Distribution", command=self.plot_win_loss_distribution).pack(side='left')
        
        # Responsive chart display area
        self.chart_frame = ttk.Frame(charts_frame)
        self.chart_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        
    def create_analysis_tab(self):
        """Create the analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Configure grid weights
        analysis_frame.grid_rowconfigure(1, weight=1)
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        # Analysis controls
        controls_frame = ttk.Frame(analysis_frame)
        controls_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Analyze by Pair", command=self.analyze_by_pair).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Analyze by Strategy", command=self.analyze_by_strategy).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Time Analysis", command=self.analyze_by_time).pack(side='left')
        
        # Analysis display frame
        text_frame = ttk.Frame(analysis_frame)
        text_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Analysis display
        self.analysis_text = tk.Text(text_frame, height=25, width=100, font=('Courier', 10), state='disabled')
        self.analysis_text.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar for analysis text
        analysis_scrollbar = ttk.Scrollbar(text_frame, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        analysis_scrollbar.grid(row=0, column=1, sticky='ns')
    
    def create_calculator_tab(self):
        """Create the advanced calculator tab"""
        calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(calc_frame, text="Calculator")
        
        # Configure responsive grid weights
        calc_frame.grid_rowconfigure(0, weight=1)
        calc_frame.grid_columnconfigure(0, weight=1)
        
        # Responsive main container with scrollable frame
        canvas = tk.Canvas(calc_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(calc_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Title
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(title_frame, text="Advanced Forex Calculator", font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Professional Trading Tools by WASEEM KALUWAL", 
                 font=('Arial', 10), foreground='#666666').pack()
        
        # Create calculator sections
        self.create_position_size_calculator(scrollable_frame)
        self.create_pip_calculator(scrollable_frame)
        self.create_profit_loss_calculator(scrollable_frame)
        self.create_margin_calculator(scrollable_frame)
        self.create_risk_reward_calculator(scrollable_frame)
        
        canvas.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Responsive scroll region configuration
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_frame, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
    
    def create_position_size_calculator(self, parent):
        """Position Size Calculator"""
        frame = ttk.LabelFrame(parent, text="Position Size Calculator", padding=15)
        frame.pack(fill='x', padx=20, pady=10)
        
        # Configure grid weights
        for i in range(4):
            frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        
        # Input fields
        ttk.Label(frame, text="Account Balance ($):").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pos_balance_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pos_balance_var, width=15).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Risk Percentage (%):").grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        self.pos_risk_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pos_risk_var, width=15).grid(row=0, column=3, pady=5)
        
        ttk.Label(frame, text="Entry Price:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pos_entry_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pos_entry_var, width=15).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Stop Loss:").grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        self.pos_sl_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pos_sl_var, width=15).grid(row=1, column=3, pady=5)
        
        ttk.Label(frame, text="Currency Pair:").grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pos_pair_var = tk.StringVar()
        pos_pair_combo = ttk.Combobox(frame, textvariable=self.pos_pair_var, width=12)
        pos_pair_combo['values'] = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        pos_pair_combo.grid(row=2, column=1, pady=5)
        
        ttk.Button(frame, text="Calculate Position Size", command=self.calculate_position_size).grid(row=2, column=2, columnspan=2, pady=10, padx=(20, 0))
        
        # Results
        self.pos_result_var = tk.StringVar()
        ttk.Label(frame, text="Recommended Position Size:").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        result_label = ttk.Label(frame, textvariable=self.pos_result_var, font=('Arial', 12, 'bold'), foreground='blue')
        result_label.grid(row=3, column=1, columnspan=3, sticky='w', pady=5)
    
    def create_pip_calculator(self, parent):
        """Pip Value Calculator"""
        frame = ttk.LabelFrame(parent, text="Pip Value Calculator", padding=15)
        frame.pack(fill='x', padx=20, pady=10)
        
        # Configure grid weights
        for i in range(3):
            frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        
        ttk.Label(frame, text="Currency Pair:").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pip_pair_var = tk.StringVar()
        pip_pair_combo = ttk.Combobox(frame, textvariable=self.pip_pair_var, width=12)
        pip_pair_combo['values'] = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        pip_pair_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Position Size (lots):").grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        self.pip_size_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pip_size_var, width=15).grid(row=0, column=3, pady=5)
        
        ttk.Label(frame, text="Account Currency:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pip_account_var = tk.StringVar(value='USD')
        pip_account_combo = ttk.Combobox(frame, textvariable=self.pip_account_var, width=12)
        pip_account_combo['values'] = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']
        pip_account_combo.grid(row=1, column=1, pady=5)
        
        ttk.Button(frame, text="Calculate Pip Value", command=self.calculate_pip_value).grid(row=1, column=2, columnspan=2, pady=10, padx=(20, 0))
        
        # Results
        self.pip_result_var = tk.StringVar()
        ttk.Label(frame, text="Pip Value:").grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        pip_result_label = ttk.Label(frame, textvariable=self.pip_result_var, font=('Arial', 12, 'bold'), foreground='green')
        pip_result_label.grid(row=2, column=1, columnspan=3, sticky='w', pady=5)
    
    def create_profit_loss_calculator(self, parent):
        """Profit/Loss Calculator"""
        frame = ttk.LabelFrame(parent, text="Profit/Loss Calculator", padding=15)
        frame.pack(fill='x', padx=20, pady=10)
        
        # Configure grid weights
        for i in range(4):
            frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        
        ttk.Label(frame, text="Currency Pair:").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pl_pair_var = tk.StringVar()
        pl_pair_combo = ttk.Combobox(frame, textvariable=self.pl_pair_var, width=12)
        pl_pair_combo['values'] = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        pl_pair_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Direction:").grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        self.pl_direction_var = tk.StringVar(value='long')
        pl_direction_combo = ttk.Combobox(frame, textvariable=self.pl_direction_var, width=12)
        pl_direction_combo['values'] = ['long', 'short']
        pl_direction_combo.grid(row=0, column=3, pady=5)
        
        ttk.Label(frame, text="Entry Price:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pl_entry_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pl_entry_var, width=15).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Exit Price:").grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        self.pl_exit_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pl_exit_var, width=15).grid(row=1, column=3, pady=5)
        
        ttk.Label(frame, text="Position Size (lots):").grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        self.pl_size_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pl_size_var, width=15).grid(row=2, column=1, pady=5)
        
        ttk.Button(frame, text="Calculate P&L", command=self.calculate_profit_loss).grid(row=2, column=2, columnspan=2, pady=10, padx=(20, 0))
        
        # Results
        self.pl_result_var = tk.StringVar()
        self.pl_pips_var = tk.StringVar()
        ttk.Label(frame, text="Profit/Loss:").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        pl_result_label = ttk.Label(frame, textvariable=self.pl_result_var, font=('Arial', 12, 'bold'))
        pl_result_label.grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(frame, text="Pips:").grid(row=3, column=2, sticky='w', padx=(20, 10), pady=5)
        pl_pips_label = ttk.Label(frame, textvariable=self.pl_pips_var, font=('Arial', 12, 'bold'))
        pl_pips_label.grid(row=3, column=3, sticky='w', pady=5)
    
    def create_margin_calculator(self, parent):
        """Margin Calculator"""
        frame = ttk.LabelFrame(parent, text="Margin Calculator", padding=15)
        frame.pack(fill='x', padx=20, pady=10)
        
        # Configure grid weights
        for i in range(4):
            frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        
        ttk.Label(frame, text="Currency Pair:").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.margin_pair_var = tk.StringVar()
        margin_pair_combo = ttk.Combobox(frame, textvariable=self.margin_pair_var, width=12)
        margin_pair_combo['values'] = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        margin_pair_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Position Size (lots):").grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        self.margin_size_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.margin_size_var, width=15).grid(row=0, column=3, pady=5)
        
        ttk.Label(frame, text="Leverage (1:X):").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.margin_leverage_var = tk.StringVar(value='100')
        ttk.Entry(frame, textvariable=self.margin_leverage_var, width=15).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Current Price:").grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        self.margin_price_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.margin_price_var, width=15).grid(row=1, column=3, pady=5)
        
        ttk.Button(frame, text="Calculate Margin", command=self.calculate_margin).grid(row=2, column=1, columnspan=2, pady=10)
        
        # Results
        self.margin_result_var = tk.StringVar()
        ttk.Label(frame, text="Required Margin:").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        margin_result_label = ttk.Label(frame, textvariable=self.margin_result_var, font=('Arial', 12, 'bold'), foreground='purple')
        margin_result_label.grid(row=3, column=1, columnspan=3, sticky='w', pady=5)
    
    def create_risk_reward_calculator(self, parent):
        """Risk/Reward Calculator"""
        frame = ttk.LabelFrame(parent, text="Risk/Reward Calculator", padding=15)
        frame.pack(fill='x', padx=20, pady=10)
        
        # Configure grid weights
        for i in range(5):
            frame.grid_rowconfigure(i, weight=0)
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        
        ttk.Label(frame, text="Entry Price:").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.rr_entry_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.rr_entry_var, width=15).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Stop Loss:").grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        self.rr_sl_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.rr_sl_var, width=15).grid(row=0, column=3, pady=5)
        
        ttk.Label(frame, text="Take Profit:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.rr_tp_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.rr_tp_var, width=15).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Direction:").grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        self.rr_direction_var = tk.StringVar(value='long')
        rr_direction_combo = ttk.Combobox(frame, textvariable=self.rr_direction_var, width=12)
        rr_direction_combo['values'] = ['long', 'short']
        rr_direction_combo.grid(row=1, column=3, pady=5)
        
        ttk.Button(frame, text="Calculate Risk/Reward", command=self.calculate_risk_reward).grid(row=2, column=1, columnspan=2, pady=10)
        
        # Results
        self.rr_ratio_var = tk.StringVar()
        self.rr_risk_var = tk.StringVar()
        self.rr_reward_var = tk.StringVar()
        
        ttk.Label(frame, text="Risk (pips):").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(frame, textvariable=self.rr_risk_var, font=('Arial', 10, 'bold')).grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(frame, text="Reward (pips):").grid(row=3, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(frame, textvariable=self.rr_reward_var, font=('Arial', 10, 'bold')).grid(row=3, column=3, sticky='w', pady=5)
        
        ttk.Label(frame, text="Risk/Reward Ratio:").grid(row=4, column=0, sticky='w', padx=(0, 10), pady=5)
        rr_ratio_label = ttk.Label(frame, textvariable=self.rr_ratio_var, font=('Arial', 12, 'bold'), foreground='red')
        rr_ratio_label.grid(row=4, column=1, columnspan=3, sticky='w', pady=5)
    
    def calculate_position_size(self):
        """Calculate recommended position size"""
        try:
            balance = float(self.pos_balance_var.get())
            risk_pct = float(self.pos_risk_var.get()) / 100
            entry = float(self.pos_entry_var.get())
            stop_loss = float(self.pos_sl_var.get())
            pair = self.pos_pair_var.get()
            
            if not pair:
                self.pos_result_var.set("Please select a currency pair")
                return
            
            # Use the universal calculation method for accurate pip calculation
            # Calculate 1 pip difference to get pip size and value
            test_pips, test_pnl = self.calculate_pnl_and_pips(pair, 'long', entry, entry + (0.01 if "JPY" in pair else 0.0001), 1, 0)
            
            # Calculate actual risk
            risk_pips = abs(entry - stop_loss) / (0.01 if "JPY" in pair else 0.0001 if pair not in ["XAUUSD", "XAGUSD", "US30", "NAS100", "GER30", "UK100", "JPN225", "SPX500", "USOIL", "UKOIL", "NATGAS", "COPPER"] else (0.10 if pair == "XAUUSD" else 0.001 if pair == "XAGUSD" else 1.0 if pair in ["US30", "NAS100", "GER30", "UK100", "JPN225", "SPX500"] else 0.01 if pair in ["USOIL", "UKOIL"] else 0.001 if pair == "NATGAS" else 0.0001))
            risk_amount = balance * risk_pct
            
            # Calculate pip value from test calculation
            pip_value = abs(test_pnl) if test_pips != 0 else 10
            
            position_size = risk_amount / (risk_pips * pip_value)
            
            self.pos_result_var.set(f"{position_size:.2f} lots (Risk: ${risk_amount:.2f}, {risk_pips:.1f} pips)")
            
        except ValueError:
            self.pos_result_var.set("Please enter valid numbers")
        except Exception as e:
            self.pos_result_var.set(f"Error: {str(e)}")
    
    def calculate_pip_value(self):
        """Calculate pip value"""
        try:
            pair = self.pip_pair_var.get()
            position_size = float(self.pip_size_var.get())
            account_currency = self.pip_account_var.get()
            
            if not pair:
                self.pip_result_var.set("Please select a currency pair")
                return
            
            # Use the universal calculation method for accurate pip value
            # Calculate 1 pip difference to get accurate pip value
            if "JPY" in pair:
                test_entry = 100.00
                test_exit = 100.01
            elif pair in ["XAUUSD"]:
                test_entry = 2000.00
                test_exit = 2000.10
            elif pair in ["XAGUSD"]:
                test_entry = 25.000
                test_exit = 25.001
            elif pair in ["US30", "NAS100", "GER30", "UK100", "JPN225", "SPX500"]:
                test_entry = 30000.0
                test_exit = 30001.0
            elif pair in ["USOIL", "UKOIL"]:
                test_entry = 80.00
                test_exit = 80.01
            elif pair == "NATGAS":
                test_entry = 3.000
                test_exit = 3.001
            elif pair == "COPPER":
                test_entry = 4.0000
                test_exit = 4.0001
            else:
                test_entry = 1.1000
                test_exit = 1.1001
            
            test_pips, test_pnl = self.calculate_pnl_and_pips(pair, 'long', test_entry, test_exit, position_size, 0)
            pip_value = abs(test_pnl) if test_pips != 0 else position_size * 10
            
            self.pip_result_var.set(f"{pip_value:.2f} {account_currency} per pip")
            
        except ValueError:
            self.pip_result_var.set("Please enter valid numbers")
        except Exception as e:
            self.pip_result_var.set(f"Error: {str(e)}")
    
    def calculate_profit_loss(self):
        """Calculate profit/loss"""
        try:
            pair = self.pl_pair_var.get()
            direction = self.pl_direction_var.get()
            entry = float(self.pl_entry_var.get())
            exit_price = float(self.pl_exit_var.get())
            position_size = float(self.pl_size_var.get())
            
            if not pair:
                self.pl_result_var.set("Please select a currency pair")
                return
            
            # Use the existing calculation method
            pips, pnl = self.calculate_pnl_and_pips(pair, direction, entry, exit_price, position_size, 0)
            
            # Set color based on profit/loss
            if pnl > 0:
                color = 'green'
                self.pl_result_var.set(f"${pnl:.2f} PROFIT")
            else:
                color = 'red'
                self.pl_result_var.set(f"${pnl:.2f} LOSS")
            
            self.pl_pips_var.set(f"{pips:.1f} pips")
            
        except ValueError:
            self.pl_result_var.set("Please enter valid numbers")
            self.pl_pips_var.set("")
        except Exception as e:
            self.pl_result_var.set(f"Error: {str(e)}")
            self.pl_pips_var.set("")
    
    def calculate_margin(self):
        """Calculate required margin"""
        try:
            pair = self.margin_pair_var.get()
            position_size = float(self.margin_size_var.get())
            leverage = float(self.margin_leverage_var.get())
            price = float(self.margin_price_var.get())
            
            if not pair:
                self.margin_result_var.set("Please select a currency pair")
                return
            
            # Use instrument-specific contract sizes
            if pair in ["XAUUSD"]:
                contract_size = 100  # 1 lot = 100 oz
            elif pair in ["XAGUSD"]:
                contract_size = 5000  # 1 lot = 5000 oz
            elif pair in ["US30", "NAS100", "GER30", "UK100", "JPN225", "SPX500"]:
                contract_size = 1  # 1 lot = 1 index contract
            elif pair in ["USOIL", "UKOIL"]:
                contract_size = 1000  # 1 lot = 1000 barrels
            elif pair in ["NATGAS"]:
                contract_size = 10000  # 1 lot = 10000 MMBtu
            elif pair in ["COPPER"]:
                contract_size = 25000  # 1 lot = 25000 lbs
            else:
                contract_size = 100000  # Forex standard lot
            
            # Calculate notional value
            notional_value = position_size * contract_size * price
            
            # Calculate margin
            margin = notional_value / leverage
            
            self.margin_result_var.set(f"${margin:.2f} (Leverage 1:{int(leverage)})")
            
        except ValueError:
            self.margin_result_var.set("Please enter valid numbers")
        except Exception as e:
            self.margin_result_var.set(f"Error: {str(e)}")
    
    def calculate_risk_reward(self):
        """Calculate risk/reward ratio"""
        try:
            entry = float(self.rr_entry_var.get())
            stop_loss = float(self.rr_sl_var.get())
            take_profit = float(self.rr_tp_var.get())
            direction = self.rr_direction_var.get()
            
            if direction.lower() == 'long':
                risk_pips = (entry - stop_loss) * 10000
                reward_pips = (take_profit - entry) * 10000
            else:  # short
                risk_pips = (stop_loss - entry) * 10000
                reward_pips = (entry - take_profit) * 10000
            
            if risk_pips <= 0:
                self.rr_ratio_var.set("Invalid risk setup")
                return
            
            ratio = reward_pips / risk_pips
            
            self.rr_risk_var.set(f"{abs(risk_pips):.1f}")
            self.rr_reward_var.set(f"{abs(reward_pips):.1f}")
            
            if ratio >= 2:
                color_text = "EXCELLENT"
            elif ratio >= 1.5:
                color_text = "GOOD"
            elif ratio >= 1:
                color_text = "ACCEPTABLE"
            else:
                color_text = "POOR"
            
            self.rr_ratio_var.set(f"1:{ratio:.2f} ({color_text})")
            
        except ValueError:
            self.rr_ratio_var.set("Please enter valid numbers")
            self.rr_risk_var.set("")
            self.rr_reward_var.set("")
        except Exception as e:
            self.rr_ratio_var.set(f"Error: {str(e)}")
            self.rr_risk_var.set("")
            self.rr_reward_var.set("")
    
    def create_world_clock_tab(self):
        """Create the world clock tab with analog clocks"""
        clock_frame = ttk.Frame(self.notebook)
        self.notebook.add(clock_frame, text="World Clock")
        
        # Configure responsive grid
        clock_frame.grid_rowconfigure(0, weight=0)  # Title
        clock_frame.grid_rowconfigure(1, weight=0)  # Controls
        clock_frame.grid_rowconfigure(2, weight=1)  # Clocks
        clock_frame.grid_columnconfigure(0, weight=1)
        
        # Title and controls
        title_frame = ttk.Frame(clock_frame)
        title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        ttk.Label(title_frame, text="Forex Market Hours - World Clock", font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Professional Trading Times by WASEEM KALUWAL", 
                 font=('Arial', 10), foreground='#666666').pack()
        
        # Timezone selection controls
        controls_frame = ttk.Frame(clock_frame)
        controls_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        
        # Available timezones
        self.timezones = {
            'Pakistan (PKT)': 5, 'Tokyo (JST)': 9, 'London (GMT)': 0, 'New York (EST)': -5,
            'Sydney (AEDT)': 11, 'Frankfurt (CET)': 1, 'Hong Kong (HKT)': 8, 'Singapore (SGT)': 8,
            'Dubai (GST)': 4, 'Mumbai (IST)': 5.5, 'Shanghai (CST)': 8, 'Seoul (KST)': 9,
            'Zurich (CET)': 1, 'Toronto (EST)': -5, 'Chicago (CST)': -6, 'Los Angeles (PST)': -8
        }
        
        # Responsive main container for clocks
        self.main_container = ttk.Frame(clock_frame)
        self.main_container.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        
        # Initialize clock data
        self.clock_canvases = {}
        self.time_labels = {}
        self.timezone_vars = {}
        
        # Default clocks
        default_clocks = ['Pakistan (PKT)', 'Tokyo (JST)', 'London (GMT)', 'New York (EST)']
        
        # Create 2x2 grid for clocks
        for i, tz_name in enumerate(default_clocks):
            row, col = i // 2, i % 2
            self.create_single_clock(tz_name, row, col)
        
        # Configure responsive grid weights for clocks
        for i in range(2):
            self.main_container.grid_rowconfigure(i, weight=1)
            self.main_container.grid_columnconfigure(i, weight=1)
        
        # Bind resize event for responsive clock sizing
        self.main_container.bind('<Configure>', self.on_clock_container_resize)
        
        # Start clock updates
        self.update_world_clocks()
    
    def create_single_clock(self, tz_name, row, col):
        """Create a single responsive clock widget"""
        # Create responsive frame for each clock
        clock_container = ttk.LabelFrame(self.main_container, text="", padding=10)
        clock_container.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Configure responsive grid for clock container
        clock_container.grid_rowconfigure(1, weight=1)  # Canvas row
        clock_container.grid_columnconfigure(0, weight=1)
        
        # Timezone selector
        tz_frame = ttk.Frame(clock_container)
        tz_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        ttk.Label(tz_frame, text="Timezone:").pack(side='left')
        tz_var = tk.StringVar(value=tz_name)
        tz_combo = ttk.Combobox(tz_frame, textvariable=tz_var, values=list(self.timezones.keys()), width=12)
        tz_combo.pack(side='right')
        tz_combo.bind('<<ComboboxSelected>>', lambda e, r=row, c=col: self.change_timezone(r, c))
        
        # Create responsive canvas for analog clock
        canvas = tk.Canvas(clock_container, bg='white', highlightthickness=0, 
                          width=200, height=200)  # Default size
        canvas.grid(row=1, column=0, sticky='nsew', pady=5)
        
        # Digital time display
        time_label = ttk.Label(clock_container, text="", font=('Arial', 10, 'bold'))
        time_label.grid(row=2, column=0, pady=2)
        
        # Market status
        status_label = ttk.Label(clock_container, text="", font=('Arial', 8))
        status_label.grid(row=3, column=0, pady=2)
        
        # Store references
        self.timezone_vars[f"{row}_{col}"] = tz_var
        self.clock_canvases[f"{row}_{col}"] = {'canvas': canvas, 'name': tz_name}
        self.time_labels[f"{row}_{col}"] = {'time': time_label, 'status': status_label}
        
        # Bind canvas resize for responsive behavior
        canvas.bind('<Configure>', lambda e, r=row, c=col: self.on_canvas_resize(r, c))
    
    def change_timezone(self, row, col):
        """Change timezone for a specific clock"""
        key = f"{row}_{col}"
        new_tz = self.timezone_vars[key].get()
        self.clock_canvases[key]['name'] = new_tz
    
    def on_canvas_resize(self, row, col):
        """Handle canvas resize for responsive clocks"""
        key = f"{row}_{col}"
        # Debounce resize events to avoid excessive redraws
        if hasattr(self, '_resize_timer'):
            self.root.after_cancel(self._resize_timer)
        self._resize_timer = self.root.after(300, lambda: self.update_single_clock(key))
    
    def on_clock_container_resize(self, event=None):
        """Handle clock container resize for responsive behavior"""
        # Update all clocks when container is resized
        self.root.after_idle(self.update_all_clocks_size)
    
    def update_all_clocks_size(self):
        """Update all clock sizes for responsive behavior"""
        for key in self.clock_canvases.keys():
            self.update_single_clock(key)
    
    def draw_analog_clock(self, canvas, hour, minute, second, is_am=True):
        """Draw responsive analog clock on canvas"""
        try:
            canvas.delete("all")
            
            # Get canvas size for responsive design
            width = canvas.winfo_width()
            height = canvas.winfo_height()
        except:
            return
        
        if width <= 1 or height <= 1:
            return
        
        # Responsive clock parameters
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 15
        
        if radius < 20:
            radius = 20
        
        # Responsive color scheme based on AM/PM
        if is_am:
            bg_color = 'white'
            text_color = 'black'
            hand_color = 'black'
            minute_hand_color = 'blue'
            border_color = '#cccccc'
        else:
            bg_color = '#2c2c2c'
            text_color = 'white'
            hand_color = 'white'
            minute_hand_color = 'lightblue'
            border_color = '#555555'
        
        # Draw responsive clock face
        border_width = max(2, radius // 30)
        canvas.create_oval(center_x - radius, center_y - radius, 
                          center_x + radius, center_y + radius, 
                          outline=border_color, width=border_width, fill=bg_color)
        
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = center_x + (radius - 15) * math.cos(angle)
            y1 = center_y + (radius - 15) * math.sin(angle)
            x2 = center_x + (radius - 5) * math.cos(angle)
            y2 = center_y + (radius - 5) * math.sin(angle)
            canvas.create_line(x1, y1, x2, y2, width=3, fill=text_color)
            
            # Add numbers
            num_x = center_x + (radius - 25) * math.cos(angle)
            num_y = center_y + (radius - 25) * math.sin(angle)
            canvas.create_text(num_x, num_y, text=str(12 if i == 0 else i), 
                             font=('Arial', max(8, radius//8), 'bold'), fill=text_color)
        
        # Draw minute markers
        for i in range(60):
            if i % 5 != 0:
                angle = math.radians(i * 6 - 90)
                x1 = center_x + (radius - 10) * math.cos(angle)
                y1 = center_y + (radius - 10) * math.sin(angle)
                x2 = center_x + (radius - 5) * math.cos(angle)
                y2 = center_y + (radius - 5) * math.sin(angle)
                canvas.create_line(x1, y1, x2, y2, width=1, fill='gray')
        
        # Calculate angles
        hour_angle = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
        minute_angle = math.radians(minute * 6 - 90)
        second_angle = math.radians(second * 6 - 90)
        
        # Draw responsive hands with proper scaling
        hour_length = radius * 0.5
        minute_length = radius * 0.75
        second_length = radius * 0.85
        
        # Responsive hand widths
        hour_width = max(3, radius // 25)
        minute_width = max(2, radius // 30)
        second_width = max(1, radius // 50)
        
        # Hour hand
        hour_x = center_x + hour_length * math.cos(hour_angle)
        hour_y = center_y + hour_length * math.sin(hour_angle)
        canvas.create_line(center_x, center_y, hour_x, hour_y, 
                          width=hour_width, fill=hand_color, capstyle='round')
        
        # Minute hand
        minute_x = center_x + minute_length * math.cos(minute_angle)
        minute_y = center_y + minute_length * math.sin(minute_angle)
        canvas.create_line(center_x, center_y, minute_x, minute_y, 
                          width=minute_width, fill=minute_hand_color, capstyle='round')
        
        # Second hand
        second_x = center_x + second_length * math.cos(second_angle)
        second_y = center_y + second_length * math.sin(second_angle)
        canvas.create_line(center_x, center_y, second_x, second_y, 
                          width=second_width, fill='red', capstyle='round')
        
        # Responsive center dot
        dot_size = max(3, radius // 25)
        canvas.create_oval(center_x - dot_size, center_y - dot_size, 
                          center_x + dot_size, center_y + dot_size, 
                          fill=hand_color, outline=hand_color)
    

    
    def update_world_clocks(self):
        """Update all world clocks"""
        if self._closing or not hasattr(self, 'clock_canvases'):
            return
            
        try:
            for key in self.clock_canvases.keys():
                self.update_single_clock(key)
        except:
            pass
        
        # Schedule next update
        if not self._closing:
            self.root.after(1000, self.update_world_clocks)
    
    def update_single_clock(self, key):
        """Update a single clock"""
        utc_now = datetime.now(timezone.utc)
        tz_name = self.timezone_vars[key].get()
        
        # Get timezone offset
        offset = self.timezones.get(tz_name, 0)
        
        # Adjust for daylight saving time
        if 'New York' in tz_name or 'Toronto' in tz_name or 'Chicago' in tz_name:
            if 3 <= utc_now.month <= 11:
                offset += 1
        elif 'London' in tz_name or 'Frankfurt' in tz_name or 'Zurich' in tz_name:
            if 3 <= utc_now.month <= 10:
                offset += 1
        elif 'Sydney' in tz_name:
            if 10 <= utc_now.month <= 12 or 1 <= utc_now.month <= 4:
                offset = 11
            else:
                offset = 10
        
        local_time = utc_now + timedelta(hours=offset)
        is_am = local_time.hour < 12
        
        # Update analog clock
        canvas = self.clock_canvases[key]['canvas']
        self.draw_analog_clock(canvas, local_time.hour, local_time.minute, local_time.second, is_am)
        
        # Update digital time
        time_str = local_time.strftime("%I:%M:%S %p")
        date_str = local_time.strftime("%Y-%m-%d")
        self.time_labels[key]['time'].config(text=f"{time_str}\n{date_str}")
        
        # Update market status
        status_text, status_color = self.get_market_status(tz_name, local_time.hour)
        self.time_labels[key]['status'].config(text=status_text, foreground=status_color)
    
    def get_market_status(self, city_name, hour):
        """Get market status based on city and hour"""
        if 'Pakistan' in city_name or 'Mumbai' in city_name:
            if 9 <= hour <= 17:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        elif 'Tokyo' in city_name or 'Hong Kong' in city_name or 'Singapore' in city_name or 'Shanghai' in city_name or 'Seoul' in city_name:
            if 9 <= hour <= 15:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        elif 'London' in city_name or 'Frankfurt' in city_name or 'Zurich' in city_name:
            if 8 <= hour <= 16:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        elif 'New York' in city_name or 'Toronto' in city_name or 'Chicago' in city_name:
            if 9 <= hour <= 16:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        elif 'Sydney' in city_name:
            if 10 <= hour <= 16:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        elif 'Dubai' in city_name:
            if 10 <= hour <= 14:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        elif 'Los Angeles' in city_name:
            if 6 <= hour <= 13:
                return "📈 Market Open", 'green'
            else:
                return "🔒 Market Closed", 'red'
        return "🔒 Market Closed", 'red'
        
    def add_trade(self):
        """Add a new trade with enhanced error handling"""
        try:
            # Validate required fields
            if not all([self.pair_var.get(), self.entry_price_var.get(), 
                       self.exit_price_var.get(), self.position_size_var.get()]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            # Check memory usage - limit to 10000 trades
            if len(self.trades) >= 10000:
                if not messagebox.askyesno("Memory Warning", 
                    "You have 10000+ trades. Consider exporting old data. Continue?"):
                    return
            
            pair = self.pair_var.get().upper()
            entry_price = float(self.entry_price_var.get())
            exit_price = float(self.exit_price_var.get())
            position_size = float(self.position_size_var.get())
            direction = self.direction_var.get().lower()
            commission = float(self.commission_var.get() or 0)
            
            stop_loss = float(self.stop_loss_var.get()) if self.stop_loss_var.get() else None
            take_profit = float(self.take_profit_var.get()) if self.take_profit_var.get() else None
            strategy = self.strategy_var.get()
            setup_rating = int(self.setup_rating_var.get()) if self.setup_rating_var.get() else None
            notes = self.notes_text.get('1.0', tk.END).strip()
            chart_path = self.chart_path_var.get()
            opening_balance = float(self.opening_balance_var.get()) if self.opening_balance_var.get() else None
            closing_balance = float(self.closing_balance_var.get()) if self.closing_balance_var.get() else None
            
            pips, pnl = self.calculate_pnl_and_pips(pair, direction, entry_price, exit_price, position_size, commission)
            
            trade_date = self.trade_date_var.get()
            try:
                datetime.strptime(trade_date, "%Y-%m-%d")
                trade_datetime = f"{trade_date} {datetime.now().strftime('%H:%M:%S')}"
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            trade = {
                'id': len(self.trades) + 1,
                'pair': pair,
                'entry_date': trade_datetime,
                'exit_date': trade_datetime,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'direction': direction,
                'pips': round(pips, 1),
                'pnl': round(pnl, 2),
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'commission': commission,
                'strategy': strategy,
                'setup_rating': setup_rating,
                'notes': notes,
                'chart_path': chart_path,
                'win': pnl > 0
            }
            
            self.trades.append(trade)
            self.save_journal()
            self.refresh_trades_view()
            self.update_statistics()
            self.clear_fields()
            
            messagebox.showinfo("Success", f"Trade added successfully!\nP&L: ${pnl:.2f}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        """Add a new trade"""
        try:
            # Validate required fields
            if not all([self.pair_var.get(), self.entry_price_var.get(), 
                       self.exit_price_var.get(), self.position_size_var.get()]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            # Get values
            pair = self.pair_var.get().upper()
            entry_price = float(self.entry_price_var.get())
            exit_price = float(self.exit_price_var.get())
            position_size = float(self.position_size_var.get())
            direction = self.direction_var.get().lower()
            commission = float(self.commission_var.get() or 0)
            
            # Optional values
            stop_loss = float(self.stop_loss_var.get()) if self.stop_loss_var.get() else None
            take_profit = float(self.take_profit_var.get()) if self.take_profit_var.get() else None
            strategy = self.strategy_var.get()
            setup_rating = int(self.setup_rating_var.get()) if self.setup_rating_var.get() else None
            notes = self.notes_text.get('1.0', tk.END).strip()
            chart_path = self.chart_path_var.get()
            
            # Calculate P&L and pips
            pips, pnl = self.calculate_pnl_and_pips(pair, direction, entry_price, exit_price, position_size, commission)
            
            # Get trade date
            trade_date = self.trade_date_var.get()
            try:
                # Validate date format
                datetime.strptime(trade_date, "%Y-%m-%d")
                trade_datetime = f"{trade_date} {datetime.now().strftime('%H:%M:%S')}"
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Create trade record
            trade = {
                'id': len(self.trades) + 1,
                'pair': pair,
                'entry_date': trade_datetime,
                'exit_date': trade_datetime,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position_size': position_size,
                'direction': direction,
                'pips': round(pips, 1),
                'pnl': round(pnl, 2),
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'commission': commission,
                'strategy': strategy,
                'setup_rating': setup_rating,
                'notes': notes,
                'chart_path': chart_path,
                'win': pnl > 0
            }
            
            self.trades.append(trade)
            self.save_journal()
            
            # Refresh displays
            self.refresh_trades_view()
            self.update_statistics()
            self.clear_fields()
            
            messagebox.showinfo("Success", f"Trade added successfully!\nP&L: ${pnl:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


        

    
    def open_calendar(self):
        """Open calendar widget for date selection"""
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal_window.geometry("300x250")
        cal_window.resizable(False, False)
        
        # Get current date
        try:
            current_date = datetime.strptime(self.trade_date_var.get(), "%Y-%m-%d")
        except:
            current_date = datetime.now()
        
        # Month/Year selection frame
        nav_frame = ttk.Frame(cal_window)
        nav_frame.pack(pady=10)
        
        month_var = tk.IntVar(value=current_date.month)
        year_var = tk.IntVar(value=current_date.year)
        
        ttk.Button(nav_frame, text="<", width=3, command=lambda: self.prev_month(month_var, year_var, cal_frame, month_label)).pack(side='left')
        month_label = ttk.Label(nav_frame, text=f"{calendar.month_name[current_date.month]} {current_date.year}", width=15)
        month_label.pack(side='left', padx=10)
        ttk.Button(nav_frame, text=">", width=3, command=lambda: self.next_month(month_var, year_var, cal_frame, month_label)).pack(side='left')
        
        # Calendar frame
        cal_frame = ttk.Frame(cal_window)
        cal_frame.pack(pady=10)
        
        self.update_calendar_display(cal_frame, month_var.get(), year_var.get(), cal_window)
        
    def prev_month(self, month_var, year_var, cal_frame, month_label):
        """Navigate to previous month"""
        month = month_var.get()
        year = year_var.get()
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        month_var.set(month)
        year_var.set(year)
        month_label.config(text=f"{calendar.month_name[month]} {year}")
        self.update_calendar_display(cal_frame, month, year, cal_frame.master)
        
    def next_month(self, month_var, year_var, cal_frame, month_label):
        """Navigate to next month"""
        month = month_var.get()
        year = year_var.get()
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        month_var.set(month)
        year_var.set(year)
        month_label.config(text=f"{calendar.month_name[month]} {year}")
        self.update_calendar_display(cal_frame, month, year, cal_frame.master)
        
    def update_calendar_display(self, frame, month, year, window):
        """Update calendar display"""
        for widget in frame.winfo_children():
            widget.destroy()
            
        # Days header
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(frame, text=day, font=('Arial', 8, 'bold')).grid(row=0, column=i, padx=2, pady=2)
            
        # Calendar days
        cal = calendar.monthcalendar(year, month)
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    ttk.Label(frame, text="").grid(row=week_num, column=day_num, padx=2, pady=2)
                else:
                    btn = ttk.Button(frame, text=str(day), width=3,
                                   command=lambda d=day: self.select_calendar_date(d, month, year, window))
                    btn.grid(row=week_num, column=day_num, padx=2, pady=2)
                    
    def select_calendar_date(self, day, month, year, window):
        """Select date from calendar"""
        selected_date = f"{year:04d}-{month:02d}-{day:02d}"
        self.trade_date_var.set(selected_date)
        window.destroy()

    def set_today_date(self):
        """Set trade date to today"""
        self.trade_date_var.set(datetime.now().strftime("%Y-%m-%d"))
    
    def browse_chart(self):
        """Browse for chart screenshot with size validation"""
        filename = filedialog.askopenfilename(
            title="Select Chart Screenshot",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Check file size (limit to 10MB)
                file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                if file_size > 10:
                    messagebox.showwarning("File Too Large", 
                        f"Image file is {file_size:.1f}MB. Please use files smaller than 10MB.")
                    return
                self.chart_path_var.set(filename)
            except Exception as e:
                messagebox.showerror("File Error", f"Cannot access file: {str(e)}")
    
    def clear_chart(self):
        """Clear chart screenshot path"""
        self.chart_path_var.set('')
    
    def on_strategy_select(self, event=None):
        """Handle strategy selection for custom input"""
        if self.strategy_var.get() == 'Custom...':
            custom_strategy = tk.simpledialog.askstring("Custom Strategy", "Enter custom strategy name:")
            if custom_strategy:
                self.strategy_var.set(custom_strategy)
            else:
                self.strategy_var.set('')
    
    def on_strategy_select_edit(self, event, strategy_var):
        """Handle strategy selection for edit dialog"""
        if strategy_var.get() == 'Custom...':
            custom_strategy = tk.simpledialog.askstring("Custom Strategy", "Enter custom strategy name:")
            if custom_strategy:
                strategy_var.set(custom_strategy)
            else:
                strategy_var.set('')
    
    def view_chart(self):
        """View chart screenshot for selected trade"""
        selected = self.trades_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a trade to view chart")
            return
        
        item = selected[0]
        trade_id = int(self.trades_tree.item(item)['values'][1])
        trade = next((t for t in self.trades if t['id'] == trade_id), None)
        
        if not trade:
            messagebox.showerror("Error", "Trade not found")
            return
        
        chart_path = trade.get('chart_path', '')
        if not chart_path or not os.path.exists(chart_path):
            messagebox.showinfo("Info", "No chart screenshot available for this trade")
            return
        
        self.show_chart_window(chart_path, trade_id)
    
    def show_chart_window(self, chart_path, trade_id):
        """Show chart screenshot in a new window with memory management"""
        try:
            # Check if file exists and is accessible
            if not os.path.exists(chart_path):
                messagebox.showerror("File Not Found", "Chart screenshot file not found.")
                return
                
            from PIL import Image, ImageTk
            
            chart_window = tk.Toplevel(self.root)
            chart_window.title(f"Chart - Trade #{trade_id}")
            chart_window.transient(self.root)
            
            # Load and resize image with memory limits
            image = Image.open(chart_path)
            
            # Check image size and resize if too large
            max_size = (1920, 1080)  # Limit to Full HD
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Resize to fit screen while maintaining aspect ratio
            screen_width = min(self.root.winfo_screenwidth() - 100, 1200)
            screen_height = min(self.root.winfo_screenheight() - 100, 800)
            display_size = (screen_width, screen_height)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            # Create label to display image
            label = tk.Label(chart_window, image=photo)
            label.image = photo  # Keep a reference
            label.pack(padx=10, pady=10)
            
            # Center the window
            chart_window.geometry(f"{image.width + 20}x{image.height + 20}")
            chart_window.update_idletasks()
            x = (chart_window.winfo_screenwidth() - chart_window.winfo_width()) // 2
            y = (chart_window.winfo_screenheight() - chart_window.winfo_height()) // 2
            chart_window.geometry(f"+{x}+{y}")
            
        except ImportError:
            messagebox.showerror("Error", "PIL (Pillow) library is required to view images.\nInstall with: pip install Pillow")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
    
    def on_trade_select(self, event):
        """Display notes when a trade is selected"""
        selected = self.trades_tree.selection()
        if not selected:
            self.notes_display.config(state='normal')
            self.notes_display.delete('1.0', tk.END)
            self.notes_display.config(state='disabled')
            return
        
        item = selected[0]
        trade_id = int(self.trades_tree.item(item)['values'][1])
        trade = next((t for t in self.trades if t['id'] == trade_id), None)
        
        if trade:
            notes = trade.get('notes', 'No notes available for this trade.')
            self.notes_display.config(state='normal')
            self.notes_display.delete('1.0', tk.END)
            self.notes_display.insert('1.0', notes)
            self.notes_display.config(state='disabled')
    

    

    
    def add_developer_credit(self):
        """Add developer credit at the bottom of the window"""
        credit_frame = tk.Frame(self.root, bg=self.bg_color)
        credit_frame.pack(side='bottom', fill='x', pady=(0, 2))
        
        credit_label = tk.Label(credit_frame, text="Developed by WASEEM KALUWAL", 
                               font=('Arial', 8), fg='#666666', bg=self.bg_color)
        credit_label.pack(side='right', padx=5)
    
    def calculate_pnl_and_pips(self, pair, direction, entry_price, exit_price, position_size, commission):
        """Universal P&L and pip calculation based on the provided logic"""
        
        # Step 1: Define pip size based on instrument
        if "JPY" in pair:
            pip_size = 0.01
        elif pair in ["XAUUSD"]:
            pip_size = 0.10
        elif pair in ["XAGUSD"]:
            pip_size = 0.001
        elif pair in ["US30", "NAS100", "GER30", "UK100", "JPN225", "SPX500"]:
            pip_size = 1.0
        elif pair in ["USOIL", "UKOIL"]:
            pip_size = 0.01
        elif pair in ["NATGAS"]:
            pip_size = 0.001
        elif pair in ["COPPER"]:
            pip_size = 0.0001
        else:
            pip_size = 0.0001  # Default for forex majors
        
        # Step 2: Pips moved
        pips = (exit_price - entry_price) / pip_size
        if direction.lower() == "short":
            pips = -pips  # reverse for short trades
        
        # Step 3: Contract size
        if pair in ["XAUUSD"]:
            contract_size = 100  # 1 lot = 100 oz
        elif pair in ["XAGUSD"]:
            contract_size = 5000  # 1 lot = 5000 oz
        elif pair in ["US30", "NAS100", "GER30", "UK100", "JPN225", "SPX500"]:
            contract_size = 1  # 1 lot = 1 index contract
        elif pair in ["USOIL", "UKOIL"]:
            contract_size = 1000  # 1 lot = 1000 barrels
        elif pair in ["NATGAS"]:
            contract_size = 10000  # 1 lot = 10000 MMBtu
        elif pair in ["COPPER"]:
            contract_size = 25000  # 1 lot = 25000 lbs
        else:
            contract_size = 100000  # Forex standard lot
        
        # Step 4: Pip value
        pip_value = contract_size * pip_size
        
        # Step 5: Profit/Loss
        profit_loss = pips * pip_value * position_size - commission
        
        return round(pips, 1), round(profit_loss, 2)
    
    def clear_fields(self):
        """Clear all input fields"""
        self.pair_var.set('')
        self.direction_var.set('long')
        self.entry_price_var.set('')
        self.exit_price_var.set('')
        self.position_size_var.set('')
        self.commission_var.set('0')
        self.trade_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.stop_loss_var.set('')
        self.take_profit_var.set('')
        self.strategy_var.set('')
        self.setup_rating_var.set('')
        self.notes_text.delete('1.0', tk.END)
        self.chart_path_var.set('')
        self.opening_balance_var.set('')
        self.closing_balance_var.set('')
    
    def refresh_trades_view(self):
        """Refresh the trades view with memory optimization"""
        try:
            # Clear existing items
            for item in self.trades_tree.get_children():
                self.trades_tree.delete(item)
            
            # Filter trades
            filter_pair = self.filter_pair_var.get()
            filtered_trades = self.trades
            if filter_pair != 'All':
                filtered_trades = [t for t in self.trades if t.get('pair') == filter_pair]
            
            # Limit display to prevent memory issues (show last 100 trades)
            display_limit = 100
            trades_to_show = filtered_trades[-display_limit:] if len(filtered_trades) > display_limit else filtered_trades
            
            # Add trades to tree with error handling
            for trade in reversed(trades_to_show):
                try:
                    entry_date = str(trade.get('entry_date', ''))[:10]  # Show only date
                    
                    item = self.trades_tree.insert('', 'end', values=(
                        entry_date,
                        trade.get('id', ''),
                        trade.get('pair', ''),
                        str(trade.get('direction', '')).upper(),
                        f"{float(trade.get('entry_price', 0)):.5f}",
                        f"{float(trade.get('exit_price', 0)):.5f}",
                        f"${float(trade.get('pnl', 0)):.2f}",
                        f"{float(trade.get('pips', 0)):.1f}",
                        trade.get('setup_rating', ''),
                        trade.get('strategy', '')
                    ))
                except (ValueError, TypeError) as e:
                    # Skip corrupted trade entries
                    continue
            
            # Show info if trades were limited
            if len(filtered_trades) > display_limit:
                messagebox.showinfo("Display Limited", 
                    f"Showing last {display_limit} trades of {len(filtered_trades)} total.")
                    
        except Exception as e:
            messagebox.showerror("Display Error", f"Error refreshing trades: {str(e)}")
    
    def edit_trade(self):
        """Edit selected trade"""
        selected = self.trades_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a trade to edit")
            return
        
        item = selected[0]
        trade_id = int(self.trades_tree.item(item)['values'][1])
        trade = next((t for t in self.trades if t['id'] == trade_id), None)
        
        if not trade:
            messagebox.showerror("Error", "Trade not found")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Trade #{trade_id}")
        edit_window.geometry("450x700")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"Edit Trade #{trade_id}", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Trade details frame
        details_frame = ttk.LabelFrame(main_frame, text="Trade Details", padding=8)
        details_frame.pack(fill='x', pady=(0, 8))
        
        # Create variables and populate with current values
        edit_pair_var = tk.StringVar(value=trade['pair'])
        edit_direction_var = tk.StringVar(value=trade['direction'])
        edit_entry_price_var = tk.StringVar(value=str(trade['entry_price']))
        edit_exit_price_var = tk.StringVar(value=str(trade['exit_price']))
        edit_position_size_var = tk.StringVar(value=str(trade['position_size']))
        edit_commission_var = tk.StringVar(value=str(trade.get('commission', 0)))
        edit_trade_date_var = tk.StringVar(value=trade['entry_date'][:10])
        edit_stop_loss_var = tk.StringVar(value=str(trade.get('stop_loss', '')) if trade.get('stop_loss') else '')
        edit_take_profit_var = tk.StringVar(value=str(trade.get('take_profit', '')) if trade.get('take_profit') else '')
        edit_strategy_var = tk.StringVar(value=trade.get('strategy', ''))
        edit_setup_rating_var = tk.StringVar(value=str(trade.get('setup_rating', '')) if trade.get('setup_rating') else '')
        edit_opening_balance_var = tk.StringVar(value=str(trade.get('opening_balance', '')) if trade.get('opening_balance') else '')
        edit_closing_balance_var = tk.StringVar(value=str(trade.get('closing_balance', '')) if trade.get('closing_balance') else '')
        
        # Entry fields
        ttk.Label(details_frame, text="Currency Pair:").grid(row=0, column=0, sticky='w', padx=(0, 8), pady=3)
        pair_combo = ttk.Combobox(details_frame, textvariable=edit_pair_var, width=12)
        pair_combo['values'] = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'NATGAS', 'COPPER', 'US30', 'SPX500', 'NAS100', 'GER30', 'UK100', 'JPN225']
        pair_combo.grid(row=0, column=1, pady=3)
        
        ttk.Label(details_frame, text="Direction:").grid(row=1, column=0, sticky='w', padx=(0, 8), pady=3)
        direction_combo = ttk.Combobox(details_frame, textvariable=edit_direction_var, width=12)
        direction_combo['values'] = ['long', 'short']
        direction_combo.grid(row=1, column=1, pady=3)
        
        ttk.Label(details_frame, text="Entry Price:").grid(row=2, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_entry_price_var, width=15).grid(row=2, column=1, pady=3)
        
        ttk.Label(details_frame, text="Exit Price:").grid(row=3, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_exit_price_var, width=15).grid(row=3, column=1, pady=3)
        
        ttk.Label(details_frame, text="Position Size:").grid(row=4, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_position_size_var, width=15).grid(row=4, column=1, pady=3)
        
        ttk.Label(details_frame, text="Commission:").grid(row=5, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_commission_var, width=15).grid(row=5, column=1, pady=3)
        
        ttk.Label(details_frame, text="Trade Date:").grid(row=6, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_trade_date_var, width=15).grid(row=6, column=1, pady=3)
        
        ttk.Label(details_frame, text="Opening Balance:").grid(row=7, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_opening_balance_var, width=15).grid(row=7, column=1, pady=3)
        
        ttk.Label(details_frame, text="Closing Balance:").grid(row=8, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(details_frame, textvariable=edit_closing_balance_var, width=15).grid(row=8, column=1, pady=3)
        
        # Optional details frame
        optional_frame = ttk.LabelFrame(main_frame, text="Optional Details", padding=8)
        optional_frame.pack(fill='x', pady=(0, 8))
        
        ttk.Label(optional_frame, text="Stop Loss:").grid(row=0, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(optional_frame, textvariable=edit_stop_loss_var, width=15).grid(row=0, column=1, pady=3)
        
        ttk.Label(optional_frame, text="Take Profit:").grid(row=1, column=0, sticky='w', padx=(0, 8), pady=3)
        ttk.Entry(optional_frame, textvariable=edit_take_profit_var, width=15).grid(row=1, column=1, pady=3)
        
        ttk.Label(optional_frame, text="Strategy:").grid(row=2, column=0, sticky='w', padx=(0, 8), pady=3)
        strategy_combo = ttk.Combobox(optional_frame, textvariable=edit_strategy_var, width=12)
        strategy_combo['values'] = ['Silver Bullet', 'ICT 2022', 'Turtle Soup', '9am Setup', '5am Setup', '1am Setup', 'Breakout', 'Trend Following', 'Scalping', 'Support/Resistance', 'News Trading', 'Order Block', 'Fair Value Gap', 'Liquidity Grab', 'Market Structure Shift', 'Optimal Trade Entry', 'Custom...']
        strategy_combo.grid(row=2, column=1, pady=3)
        strategy_combo.bind('<<ComboboxSelected>>', lambda e: self.on_strategy_select_edit(e, edit_strategy_var))
        
        ttk.Label(optional_frame, text="Setup Rating:").grid(row=3, column=0, sticky='w', padx=(0, 8), pady=3)
        rating_combo = ttk.Combobox(optional_frame, textvariable=edit_setup_rating_var, width=12)
        rating_combo['values'] = ['1', '2', '3', '4', '5']
        rating_combo.grid(row=3, column=1, pady=3)
        

        
        # Chart Screenshot section
        ttk.Label(optional_frame, text="Chart Screenshot:").grid(row=4, column=0, sticky='w', padx=(0, 8), pady=3)
        chart_frame = ttk.Frame(optional_frame)
        chart_frame.grid(row=4, column=1, pady=3, sticky='ew')
        
        edit_chart_path_var = tk.StringVar(value=trade.get('chart_path', ''))
        chart_entry = ttk.Entry(chart_frame, textvariable=edit_chart_path_var, width=20, state='readonly')
        chart_entry.pack(side='left', padx=(0, 5))
        
        def browse_edit_chart():
            filename = filedialog.askopenfilename(
                title="Select Chart Screenshot",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            if filename:
                try:
                    # Check file size (limit to 10MB)
                    file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                    if file_size > 10:
                        messagebox.showwarning("File Too Large", 
                            f"Image file is {file_size:.1f}MB. Please use files smaller than 10MB.")
                        return
                    edit_chart_path_var.set(filename)
                except Exception as e:
                    messagebox.showerror("File Error", f"Cannot access file: {str(e)}")
        
        def clear_edit_chart():
            edit_chart_path_var.set('')
        
        ttk.Button(chart_frame, text="Browse", command=browse_edit_chart, width=8).pack(side='left', padx=(0, 5))
        ttk.Button(chart_frame, text="Clear", command=clear_edit_chart, width=6).pack(side='left')
        
        ttk.Label(optional_frame, text="Notes:").grid(row=5, column=0, sticky='w', padx=(0, 8), pady=3)
        notes_text = tk.Text(optional_frame, height=2, width=35)
        notes_text.grid(row=6, column=0, columnspan=2, pady=3, sticky='ew')
        notes_text.insert('1.0', trade.get('notes', ''))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=15)
        
        def save_changes():
            try:
                # Get updated values
                pair = edit_pair_var.get().upper()
                entry_price = float(edit_entry_price_var.get())
                exit_price = float(edit_exit_price_var.get())
                position_size = float(edit_position_size_var.get())
                direction = edit_direction_var.get().lower()
                commission = float(edit_commission_var.get() or 0)
                
                # Calculate P&L and pips
                pips, pnl = self.calculate_pnl_and_pips(pair, direction, entry_price, exit_price, position_size, commission)
                
                # Update trade
                trade['pair'] = pair
                trade['entry_price'] = entry_price
                trade['exit_price'] = exit_price
                trade['position_size'] = position_size
                trade['direction'] = direction
                trade['commission'] = commission
                trade['pips'] = round(pips, 1)
                trade['pnl'] = round(pnl, 2)
                trade['win'] = pnl > 0
                trade['stop_loss'] = float(edit_stop_loss_var.get()) if edit_stop_loss_var.get() else None
                trade['take_profit'] = float(edit_take_profit_var.get()) if edit_take_profit_var.get() else None
                trade['strategy'] = edit_strategy_var.get()
                trade['setup_rating'] = int(edit_setup_rating_var.get()) if edit_setup_rating_var.get() else None
                trade['notes'] = notes_text.get('1.0', tk.END).strip()
                trade['chart_path'] = edit_chart_path_var.get()
                trade['opening_balance'] = float(edit_opening_balance_var.get()) if edit_opening_balance_var.get() else None
                trade['closing_balance'] = float(edit_closing_balance_var.get()) if edit_closing_balance_var.get() else None
                
                # Update date if changed
                new_date = edit_trade_date_var.get()
                if new_date != trade['entry_date'][:10]:
                    try:
                        datetime.strptime(new_date, "%Y-%m-%d")
                        trade['entry_date'] = f"{new_date} {trade['entry_date'][11:]}"
                        trade['exit_date'] = f"{new_date} {trade['exit_date'][11:]}"
                    except ValueError:
                        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                        return
                
                self.save_journal()
                self.refresh_trades_view()
                self.update_statistics()
                edit_window.destroy()
                messagebox.showinfo("Success", f"Trade #{trade_id} updated successfully!")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        ttk.Button(button_frame, text="Save Changes", command=save_changes, style='Accent.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='left')
    
    def delete_trade(self):
        """Delete selected trade"""
        selected = self.trades_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a trade to delete")
            return
        
        item = selected[0]
        trade_id = int(self.trades_tree.item(item)['values'][1])
        
        if messagebox.askyesno("Confirm", f"Delete trade #{trade_id}?"):
            self.trades = [t for t in self.trades if t['id'] != trade_id]
            self.save_journal()
            self.refresh_trades_view()
            self.update_statistics()
            messagebox.showinfo("Success", "Trade deleted successfully")
    
    def update_statistics(self):
        """Update the statistics display with memory optimization"""
        try:
            if not self.trades:
                self.stats_text.config(state='normal')
                self.stats_text.delete('1.0', tk.END)
                self.stats_text.insert('1.0', "No trades recorded yet.")
                self.stats_text.config(state='disabled')
                return
            
            # Limit processing to last 5000 trades for performance
            trades_to_analyze = self.trades[-5000:] if len(self.trades) > 5000 else self.trades
            df = pd.DataFrame(trades_to_analyze)
            df['entry_date'] = pd.to_datetime(df['entry_date'])
        
            # Calculate statistics
            total_trades = len(df)
            winning_trades = len(df[df['win'] == True])
            losing_trades = len(df[df['win'] == False])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            total_pnl = df['pnl'].sum()
            avg_win = df[df['win'] == True]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = df[df['win'] == False]['pnl'].mean() if losing_trades > 0 else 0
            
            profit_factor = abs(df[df['win'] == True]['pnl'].sum() / df[df['win'] == False]['pnl'].sum()) if losing_trades > 0 else float('inf')
            risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            
            largest_win = df['pnl'].max()
            largest_loss = df['pnl'].min()
            
            # Calculate drawdown
            df_sorted = df.sort_values('entry_date')
            df_sorted['cumulative_pnl'] = df_sorted['pnl'].cumsum()
            df_sorted['running_max'] = df_sorted['cumulative_pnl'].expanding().max()
            df_sorted['drawdown'] = df_sorted['cumulative_pnl'] - df_sorted['running_max']
            max_drawdown = df_sorted['drawdown'].min()
            
            # Format statistics
            stats_text = f"""
{'='*60}
KALUWAL FX JOURNAL - PERFORMANCE STATISTICS
{'='*60}

TRADE SUMMARY
{'-'*60}
Total Trades:           {total_trades:>10}
Winning Trades:         {winning_trades:>10}
Losing Trades:          {losing_trades:>10}
Win Rate:               {win_rate:>9.1f}%

PROFITABILITY
{'-'*60}
Total P&L:              ${total_pnl:>9.2f}
Average Win:            ${avg_win:>9.2f}
Average Loss:           ${avg_loss:>9.2f}
Profit Factor:          {profit_factor if profit_factor != float('inf') else 'N/A':>10}
Risk/Reward Ratio:      {risk_reward if risk_reward != float('inf') else 'N/A':>10}

EXTREMES
{'-'*60}
Largest Win:            ${largest_win:>9.2f}
Largest Loss:           ${largest_loss:>9.2f}
Maximum Drawdown:       ${max_drawdown:>9.2f}

RECENT ACTIVITY
{'-'*60}
Last Trade Date:        {df['entry_date'].max().strftime('%Y-%m-%d')}
Trades This Month:      {len(df[df['entry_date'].dt.month == datetime.now().month]):>10}
This Month P&L:         ${df[df['entry_date'].dt.month == datetime.now().month]['pnl'].sum():>9.2f}

BALANCE TRACKING
{'-'*60}
Opening Balance:        ${df[df['opening_balance'].notna()]['opening_balance'].iloc[0] if len(df[df['opening_balance'].notna()]) > 0 else 0:>9.2f}
Closing Balance:        ${df[df['closing_balance'].notna()]['closing_balance'].iloc[-1] if len(df[df['closing_balance'].notna()]) > 0 else 0:>9.2f}
Balance Growth:         ${(df[df['closing_balance'].notna()]['closing_balance'].iloc[-1] if len(df[df['closing_balance'].notna()]) > 0 else 0) - (df[df['opening_balance'].notna()]['opening_balance'].iloc[0] if len(df[df['opening_balance'].notna()]) > 0 else 0):>9.2f}

{'='*60}
            """
        
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', stats_text)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', f"Error calculating statistics: {str(e)}")
            self.stats_text.config(state='disabled')
    
    def plot_pnl_curve(self):
        """Plot cumulative P&L curve with memory optimization"""
        try:
            if not self.trades:
                messagebox.showinfo("Info", "No trades to plot")
                return
            
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Limit to last 1000 trades for chart performance
            trades_to_plot = self.trades[-1000:] if len(self.trades) > 1000 else self.trades
            df = pd.DataFrame(trades_to_plot)
            df['entry_date'] = pd.to_datetime(df['entry_date'])
            df = df.sort_values('entry_date')
            df['cumulative_pnl'] = df['pnl'].cumsum()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['entry_date'], df['cumulative_pnl'], linewidth=2, color='blue')
            ax.set_title('Cumulative P&L Over Time', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Cumulative P&L ($)')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.get_tk_widget().pack(fill='both', expand=True)
            canvas.draw()
            
            # Show info if data was limited
            if len(self.trades) > 1000:
                messagebox.showinfo("Chart Info", f"Showing last 1000 trades of {len(self.trades)} total.")
                
        except Exception as e:
            messagebox.showerror("Chart Error", f"Error creating chart: {str(e)}")
    
    def plot_monthly_performance(self):
        """Plot monthly P&L performance"""
        if not self.trades:
            messagebox.showinfo("Info", "No trades to plot")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        df = pd.DataFrame(self.trades)
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        df['month'] = df['entry_date'].dt.to_period('M')
        monthly_pnl = df.groupby('month')['pnl'].sum()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['green' if x > 0 else 'red' for x in monthly_pnl.values]
        bars = ax.bar(range(len(monthly_pnl)), monthly_pnl.values, color=colors, alpha=0.7)
        
        ax.set_title('Monthly P&L Performance', fontsize=14, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('P&L ($)')
        ax.set_xticks(range(len(monthly_pnl)))
        ax.set_xticklabels([str(month) for month in monthly_pnl.index], rotation=45)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'${height:.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3 if height > 0 else -15),
                       textcoords="offset points",
                       ha='center', va='bottom' if height > 0 else 'top',
                       fontsize=9)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()
    
    def plot_win_loss_distribution(self):
        """Plot win/loss distribution"""
        if not self.trades:
            messagebox.showinfo("Info", "No trades to plot")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        df = pd.DataFrame(self.trades)
        wins = df[df['win'] == True]['pnl']
        losses = df[df['win'] == False]['pnl']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Win/Loss pie chart
        labels = ['Wins', 'Losses']
        sizes = [len(wins), len(losses)]
        colors = ['green', 'red']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Win/Loss Distribution')
        
        # P&L histogram
        all_pnl = df['pnl']
        ax2.hist(all_pnl, bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax2.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        ax2.set_title('P&L Distribution')
        ax2.set_xlabel('P&L ($)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()
    
    def analyze_by_pair(self):
        """Analyze performance by currency pair"""
        if not self.trades:
            messagebox.showinfo("Info", "No trades to analyze")
            return
        
        df = pd.DataFrame(self.trades)
        pair_analysis = df.groupby('pair').agg({
            'pnl': ['sum', 'mean', 'count'],
            'win': 'mean',
            'pips': 'mean'
        }).round(2)
        
        pair_analysis.columns = ['Total_PnL', 'Avg_PnL', 'Trade_Count', 'Win_Rate', 'Avg_Pips']
        pair_analysis['Win_Rate'] = (pair_analysis['Win_Rate'] * 100).round(1)
        pair_analysis = pair_analysis.sort_values('Total_PnL', ascending=False)
        
        analysis_text = "PERFORMANCE BY CURRENCY PAIR\n"
        analysis_text += "="*70 + "\n\n"
        analysis_text += f"{'Pair':<8} {'Total P&L':<12} {'Avg P&L':<10} {'Trades':<8} {'Win%':<8} {'Avg Pips':<10}\n"
        analysis_text += "-"*70 + "\n"
        
        for pair, row in pair_analysis.iterrows():
            analysis_text += f"{pair:<8} ${row['Total_PnL']:<11.2f} ${row['Avg_PnL']:<9.2f} "
            analysis_text += f"{int(row['Trade_Count']):<8} {row['Win_Rate']:<7.1f}% {row['Avg_Pips']:<10.1f}\n"
        
        self.analysis_text.config(state='normal')
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert('1.0', analysis_text)
        self.analysis_text.config(state='disabled')
    
    def analyze_by_strategy(self):
        """Analyze performance by strategy"""
        if not self.trades:
            messagebox.showinfo("Info", "No trades to analyze")
            return
        
        df = pd.DataFrame(self.trades)
        df_with_strategy = df[df['strategy'] != '']
        
        if df_with_strategy.empty:
            self.analysis_text.config(state='normal')
            self.analysis_text.delete('1.0', tk.END)
            self.analysis_text.insert('1.0', "No strategies recorded in trades.")
            self.analysis_text.config(state='disabled')
            return
        
        strategy_analysis = df_with_strategy.groupby('strategy').agg({
            'pnl': ['sum', 'mean', 'count'],
            'win': 'mean',
            'pips': 'mean'
        }).round(2)
        
        strategy_analysis.columns = ['Total_PnL', 'Avg_PnL', 'Trade_Count', 'Win_Rate', 'Avg_Pips']
        strategy_analysis['Win_Rate'] = (strategy_analysis['Win_Rate'] * 100).round(1)
        strategy_analysis = strategy_analysis.sort_values('Total_PnL', ascending=False)
        
        analysis_text = "PERFORMANCE BY STRATEGY\n"
        analysis_text += "="*80 + "\n\n"
        analysis_text += f"{'Strategy':<15} {'Total P&L':<12} {'Avg P&L':<10} {'Trades':<8} {'Win%':<8} {'Avg Pips':<10}\n"
        analysis_text += "-"*80 + "\n"
        
        for strategy, row in strategy_analysis.iterrows():
            analysis_text += f"{strategy:<15} ${row['Total_PnL']:<11.2f} ${row['Avg_PnL']:<9.2f} "
            analysis_text += f"{int(row['Trade_Count']):<8} {row['Win_Rate']:<7.1f}% {row['Avg_Pips']:<10.1f}\n"
        
        self.analysis_text.config(state='normal')
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert('1.0', analysis_text)
        self.analysis_text.config(state='disabled')
    
    def analyze_by_time(self):
        """Analyze performance by time periods"""
        if not self.trades:
            messagebox.showinfo("Info", "No trades to analyze")
            return
        
        df = pd.DataFrame(self.trades)
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        df['hour'] = df['entry_date'].dt.hour
        df['day_of_week'] = df['entry_date'].dt.day_name()
        df['month'] = df['entry_date'].dt.month_name()
        
        # Analysis by hour
        hourly_analysis = df.groupby('hour').agg({
            'pnl': ['sum', 'mean', 'count'],
            'win': 'mean'
        }).round(2)
        hourly_analysis.columns = ['Total_PnL', 'Avg_PnL', 'Trade_Count', 'Win_Rate']
        hourly_analysis['Win_Rate'] = (hourly_analysis['Win_Rate'] * 100).round(1)
        
        # Analysis by day of week
        daily_analysis = df.groupby('day_of_week').agg({
            'pnl': ['sum', 'mean', 'count'],
            'win': 'mean'
        }).round(2)
        daily_analysis.columns = ['Total_PnL', 'Avg_PnL', 'Trade_Count', 'Win_Rate']
        daily_analysis['Win_Rate'] = (daily_analysis['Win_Rate'] * 100).round(1)
        
        analysis_text = "TIME-BASED PERFORMANCE ANALYSIS\n"
        analysis_text += "="*60 + "\n\n"
        
        # Best performing hours
        analysis_text += "BEST PERFORMING HOURS (Top 5)\n"
        analysis_text += "-"*40 + "\n"
        best_hours = hourly_analysis.sort_values('Total_PnL', ascending=False).head(5)
        for hour, row in best_hours.iterrows():
            analysis_text += f"Hour {hour:02d}: ${row['Total_PnL']:7.2f} P&L, {row['Win_Rate']:5.1f}% Win Rate ({int(row['Trade_Count'])} trades)\n"
        
        analysis_text += "\n"
        
        # Best performing days
        analysis_text += "PERFORMANCE BY DAY OF WEEK\n"
        analysis_text += "-"*40 + "\n"
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in day_order:
            if day in daily_analysis.index:
                row = daily_analysis.loc[day]
                analysis_text += f"{day:<10}: ${row['Total_PnL']:7.2f} P&L, {row['Win_Rate']:5.1f}% Win Rate ({int(row['Trade_Count'])} trades)\n"
        
        self.analysis_text.config(state='normal')
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert('1.0', analysis_text)
        self.analysis_text.config(state='disabled')
    
    def export_csv(self):
        """Export trades to CSV file with professional formatting"""
        if not self.trades:
            messagebox.showinfo("Info", "No trades to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Trading Journal",
            initialfile="Kaluwal_FX_Journal_Export"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.trades)
                
                # Create professional column mapping
                column_mapping = {
                    'id': 'Trade ID',
                    'pair': 'Currency Pair',
                    'entry_date': 'Entry Date',
                    'exit_date': 'Exit Date', 
                    'entry_price': 'Entry Price',
                    'exit_price': 'Exit Price',
                    'position_size': 'Position Size (Lots)',
                    'direction': 'Direction',
                    'pips': 'Pips',
                    'pnl': 'P&L ($)',
                    'stop_loss': 'Stop Loss',
                    'take_profit': 'Take Profit',
                    'commission': 'Commission ($)',
                    'strategy': 'Strategy',
                    'setup_rating': 'Setup Rating (1-5)',
                    'notes': 'Notes',
                    'win': 'Win/Loss'
                }
                
                # Rename columns
                df = df.rename(columns=column_mapping)
                
                # Format data for better presentation
                if 'Direction' in df.columns:
                    df['Direction'] = df['Direction'].str.upper()
                if 'Win/Loss' in df.columns:
                    df['Win/Loss'] = df['Win/Loss'].map({True: 'WIN', False: 'LOSS'})
                
                # Remove chart_path column if it exists
                if 'Chart Screenshot Path' in df.columns:
                    df = df.drop('Chart Screenshot Path', axis=1)
                
                # Handle missing columns gracefully
                df = df.fillna('')
                
                # Reorder columns for better presentation
                preferred_order = [
                    'Trade ID', 'Entry Date', 'Currency Pair', 'Direction',
                    'Entry Price', 'Exit Price', 'Position Size (Lots)',
                    'Pips', 'P&L ($)', 'Win/Loss', 'Stop Loss', 'Take Profit',
                    'Commission ($)', 'Strategy', 'Setup Rating (1-5)', 'Notes'
                ]
                
                # Reorder columns (only include existing ones)
                existing_cols = [col for col in preferred_order if col in df.columns]
                remaining_cols = [col for col in df.columns if col not in existing_cols]
                df = df[existing_cols + remaining_cols]
                
                if filename.endswith('.xlsx'):
                    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                        workbook = writer.book
                        worksheet = workbook.add_worksheet('Kaluwal FX Journal')
                        
                        # Define formats
                        title_format = workbook.add_format({
                            'bold': True, 'font_size': 16, 'font_color': 'white',
                            'bg_color': '#1f4e79', 'align': 'center', 'valign': 'vcenter'
                        })
                        
                        summary_label_format = workbook.add_format({
                            'bg_color': '#fff2cc', 'border': 1, 'bold': True
                        })
                        
                        summary_value_format = workbook.add_format({
                            'bg_color': '#dae3f0', 'border': 1
                        })
                        
                        header_format = workbook.add_format({
                            'bold': True, 'font_color': 'white', 'bg_color': '#c65911',
                            'align': 'center', 'valign': 'vcenter', 'border': 1
                        })
                        
                        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'border': 1})
                        profit_format = workbook.add_format({'num_format': '$#,##0.00', 'font_color': 'green', 'border': 1})
                        loss_format = workbook.add_format({'num_format': '$#,##0.00', 'font_color': 'red', 'border': 1})
                        
                        # Title Row (B2:K2)
                        worksheet.merge_range('B2:K2', 'KALUWAL FX JOURNAL - TRADING EXPORT', title_format)
                        worksheet.set_row(1, 35)
                        
                        # Account Summary (Rows 4-6)
                        total_pnl = df['P&L ($)'].str.replace('$', '').astype(float).sum()
                        win_trades = len(df[df['Win/Loss'] == 'WIN'])
                        total_trades = len(df)
                        
                        worksheet.write('C4', 'Total P&L:', summary_label_format)
                        worksheet.write('D4', total_pnl, summary_value_format)
                        worksheet.write('C5', 'Win Rate:', summary_label_format)
                        worksheet.write('D5', f'{(win_trades/total_trades*100):.1f}%' if total_trades > 0 else '0%', summary_value_format)
                        worksheet.write('C6', 'Total Trades:', summary_label_format)
                        worksheet.write('D6', total_trades, summary_value_format)
                        
                        # Set column widths
                        worksheet.set_column('B:B', 14)  # Date
                        worksheet.set_column('C:C', 12)  # Symbol
                        worksheet.set_column('D:D', 12)  # Direction
                        worksheet.set_column('E:E', 10)  # Qty
                        worksheet.set_column('F:G', 12)  # Entry/Exit
                        worksheet.set_column('H:K', 14)  # P&L columns
                        
                        # Table Headers (Row 9)
                        headers = ['Date', 'Symbol', 'Long/Short', 'Qty', 'Entry', 'Exit', 'Profit/Loss', 'Commission', 'Net P&L', 'Win/Loss']
                        for col, header in enumerate(headers, 1):
                            worksheet.write(8, col, header, header_format)
                        worksheet.set_row(8, 25)
                        
                        # Table Data (Row 10+)
                        for row, (_, trade) in enumerate(df.iterrows(), 9):
                            worksheet.write(row, 1, trade['Entry Date'][:10])  # Date only
                            worksheet.write(row, 2, trade['Currency Pair'])
                            worksheet.write(row, 3, trade['Direction'])
                            worksheet.write(row, 4, trade['Position Size (Lots)'])
                            worksheet.write(row, 5, trade['Entry Price'], currency_format)
                            worksheet.write(row, 6, trade['Exit Price'], currency_format)
                            
                            pnl_value = float(trade['P&L ($)'].replace('$', ''))
                            pnl_format = profit_format if pnl_value >= 0 else loss_format
                            worksheet.write(row, 7, pnl_value, pnl_format)
                            worksheet.write(row, 8, float(trade['Commission ($)']), currency_format)
                            worksheet.write(row, 9, pnl_value - float(trade['Commission ($)']), pnl_format)
                            worksheet.write(row, 10, trade['Win/Loss'])
                            
                            worksheet.set_row(row, 20)
                    
                    messagebox.showinfo("Success", f"Professional Excel exported successfully!\nFile: {filename}")
                else:
                    # Create professional CSV with proper formatting
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        # Header section
                        f.write('=================================================================\n')
                        f.write('                    KALUWAL FX JOURNAL                          \n')
                        f.write('                   TRADING EXPORT REPORT                        \n')
                        f.write('=================================================================\n')
                        f.write(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                        f.write(f'Total Trades: {len(df)}\n')
                        f.write('Developed by: WASEEM KALUWAL\n')
                        f.write('=================================================================\n\n')
                    
                    # Append data with proper formatting
                    df.to_csv(filename, mode='a', index=False)
                    
                    # Add footer
                    with open(filename, 'a', newline='', encoding='utf-8') as f:
                        f.write('\n=================================================================\n')
                        f.write('                    END OF REPORT                               \n')
                        f.write('=================================================================\n')
                    
                    messagebox.showinfo("Success", f"Professional CSV exported successfully!\nFile: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        # Configure additional button styles
        self.style.configure('Accent.TButton',
                           foreground='white',
                           background='#0078d4',
                           focuscolor='#005a9e')
        
        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window on screen
        self.center_window()
        
        # Maintain initial window size
        initial_geometry = self.root.geometry()
        self.root.after(100, lambda: self.root.geometry(initial_geometry))
        
        # Start the main loop
        self.root.mainloop()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        """Handle application closing with confirmation"""
        self._closing = True
        if messagebox.askyesno("Exit", "Save journal before closing?"):
            self.save_journal()
        self.root.destroy()


# Additional utility functions and enhancements
class TradingJournalEnhanced(ForexTradingJournalGUI):
    """Enhanced version with additional features"""
    
    def __init__(self):
        super().__init__()
        self.add_menu_bar()
        self.add_status_bar()
        
        # Additional window improvements
        self.setup_window_improvements()
    
    def setup_window_improvements(self):
        """Setup additional window improvements"""
        # Make window resizable with better constraints
        self.root.minsize(700, 600)
        self.root.maxsize(1600, 1200)
        
        # Bind additional events for better responsiveness
        self.root.bind('<Control-s>', lambda e: self.save_journal())
        self.root.bind('<Control-o>', lambda e: self.open_journal())
        self.root.bind('<Control-n>', lambda e: self.new_journal())
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        
        # Track fullscreen state
        self.is_fullscreen = False
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        if self.is_fullscreen:
            self.status_var.set("Fullscreen mode - Press Escape to exit")
        else:
            self.status_var.set(f"Ready - {len(self.trades)} trades loaded")
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
            self.status_var.set(f"Ready - {len(self.trades)} trades loaded")
    
    def add_menu_bar(self):
        """Add menu bar to the application"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Journal", command=self.new_journal)
        file_menu.add_command(label="Open Journal", command=self.open_journal)
        file_menu.add_command(label="Save Journal", command=self.save_journal)
        file_menu.add_command(label="Save Journal As...", command=self.save_journal_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calculate Position Size", command=self.calculate_position_size)
        tools_menu.add_command(label="Risk Calculator", command=self.risk_calculator)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def add_status_bar(self):
        """Add enhanced status bar to the application"""
        self.status_frame = tk.Frame(self.root, bg=self.bg_color, relief='sunken', bd=1)
        self.status_frame.pack(side='bottom', fill='x', before=self.root.winfo_children()[0])
        
        self.status_var = tk.StringVar()
        self.status_var.set(f"Ready - {len(self.trades)} trades loaded")
        
        # Status message
        status_label = tk.Label(self.status_frame, textvariable=self.status_var, 
                               bg=self.bg_color, fg='#333333', font=('Arial', 9))
        status_label.pack(side='left', fill='x', expand=True, padx=5, pady=2)
        
        # Window size indicator
        self.size_var = tk.StringVar()
        size_label = tk.Label(self.status_frame, textvariable=self.size_var,
                             bg=self.bg_color, fg='#666666', font=('Arial', 8))
        size_label.pack(side='right', padx=5, pady=2)
        
        # Current time
        self.time_var = tk.StringVar()
        time_label = tk.Label(self.status_frame, textvariable=self.time_var,
                             bg=self.bg_color, fg='#666666', font=('Arial', 8))
        time_label.pack(side='right', padx=5, pady=2)
        
        self.update_time()
        self.update_window_size()
    
    def update_time(self):
        """Update the time display"""
        if self._closing:
            return
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        if not self._closing:
            self.root.after(1000, self.update_time)
    
    def update_window_size(self):
        """Update window size display"""
        if self._closing or not hasattr(self, 'root') or not self.root.winfo_exists():
            return
        try:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.size_var.set(f"{width}x{height}")
        except:
            return
        if not self._closing and hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(2000, self.update_window_size)
    
    def new_journal(self):
        """Create a new journal"""
        if messagebox.askyesno("New Journal", "This will clear all current trades. Continue?"):
            self.trades = []
            self.save_journal()
            self.refresh_trades_view()
            self.update_statistics()
            self.status_var.set("New journal created")
    
    def open_journal(self):
        """Open an existing journal file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open journal file"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.trades = json.load(f)
                self.journal_file = filename
                self.refresh_trades_view()
                self.update_statistics()
                self.status_var.set(f"Journal loaded: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def calculate_position_size(self):
        """Open position size calculator"""
        calc_window = tk.Toplevel(self.root)
        calc_window.title("Position Size Calculator")
        calc_window.geometry("400x300")
        calc_window.transient(self.root)
        calc_window.grab_set()
        
        # Calculator interface
        ttk.Label(calc_window, text="Position Size Calculator", font=('Arial', 14, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(calc_window)
        frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Input fields
        ttk.Label(frame, text="Account Balance ($):").grid(row=0, column=0, sticky='w', pady=5)
        balance_var = tk.StringVar()
        ttk.Entry(frame, textvariable=balance_var, width=15).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Risk Percentage (%):").grid(row=1, column=0, sticky='w', pady=5)
        risk_var = tk.StringVar()
        ttk.Entry(frame, textvariable=risk_var, width=15).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Stop Loss (pips):").grid(row=2, column=0, sticky='w', pady=5)
        sl_var = tk.StringVar()
        ttk.Entry(frame, textvariable=sl_var, width=15).grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Pip Value ($):").grid(row=3, column=0, sticky='w', pady=5)
        pip_var = tk.StringVar(value="10")  # Default for standard lot
        ttk.Entry(frame, textvariable=pip_var, width=15).grid(row=3, column=1, pady=5)
        
        # Result
        result_var = tk.StringVar()
        ttk.Label(frame, text="Position Size (lots):").grid(row=4, column=0, sticky='w', pady=5)
        result_label = ttk.Label(frame, textvariable=result_var, font=('Arial', 10, 'bold'))
        result_label.grid(row=4, column=1, pady=5)
        
        def calculate():
            try:
                balance = float(balance_var.get())
                risk_pct = float(risk_var.get()) / 100
                stop_loss = float(sl_var.get())
                pip_value = float(pip_var.get())
                
                risk_amount = balance * risk_pct
                position_size = risk_amount / (stop_loss * pip_value)
                
                result_var.set(f"{position_size:.2f}")
            except ValueError:
                result_var.set("Invalid input")
        
        ttk.Button(frame, text="Calculate", command=calculate).grid(row=5, column=0, columnspan=2, pady=20)
    
    def risk_calculator(self):
        """Open risk calculator"""
        risk_window = tk.Toplevel(self.root)
        risk_window.title("Risk Calculator")
        risk_window.geometry("400x250")
        risk_window.transient(self.root)
        risk_window.grab_set()
        
        ttk.Label(risk_window, text="Risk Calculator", font=('Arial', 14, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(risk_window)
        frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Input fields
        ttk.Label(frame, text="Entry Price:").grid(row=0, column=0, sticky='w', pady=5)
        entry_var = tk.StringVar()
        ttk.Entry(frame, textvariable=entry_var, width=15).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Stop Loss:").grid(row=1, column=0, sticky='w', pady=5)
        sl_var = tk.StringVar()
        ttk.Entry(frame, textvariable=sl_var, width=15).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Position Size (lots):").grid(row=2, column=0, sticky='w', pady=5)
        size_var = tk.StringVar()
        ttk.Entry(frame, textvariable=size_var, width=15).grid(row=2, column=1, pady=5)
        
        # Results
        pips_var = tk.StringVar()
        risk_var = tk.StringVar()
        
        ttk.Label(frame, text="Risk (pips):").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Label(frame, textvariable=pips_var, font=('Arial', 10, 'bold')).grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Risk Amount ($):").grid(row=4, column=0, sticky='w', pady=5)
        ttk.Label(frame, textvariable=risk_var, font=('Arial', 10, 'bold')).grid(row=4, column=1, pady=5)
        
        def calculate_risk():
            try:
                entry = float(entry_var.get())
                stop_loss = float(sl_var.get())
                position_size = float(size_var.get())
                
                pips = abs(entry - stop_loss) * 10000
                risk_amount = pips * position_size * 1  # $1 per pip for standard lot
                
                pips_var.set(f"{pips:.1f}")
                risk_var.set(f"${risk_amount:.2f}")
            except ValueError:
                pips_var.set("Invalid input")
                risk_var.set("Invalid input")
        
        ttk.Button(frame, text="Calculate", command=calculate_risk).grid(row=5, column=0, columnspan=2, pady=20)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
            "Kaluwal FX Journal v2.0\n\n"
            "A comprehensive tool for tracking and analyzing\n"
            "forex trading performance.\n\n"
            "Features:\n"
            "• Add Trade - Record new trades with detailed information\n"
            "• View Trades - Browse and manage trade history\n"
            "• Statistics - Comprehensive performance analytics\n"
            "• Charts - P&L curves, monthly performance, distributions\n"
            "• Analysis - Performance by pair, strategy, and time\n"
            "• Calculator - Position size, pip value, P&L, margin, risk/reward\n"
            "• World Clock - Forex market hours with analog clocks\n"
            "• Export - Professional CSV/Excel export\n"
            "• Chart Screenshots - Attach and view trade charts\n"
            "• Strategy Tracking - Monitor different trading strategies\n"
            "• Risk Management - Calculate optimal position sizes\n"
            "• Real-time Updates - Live clock and market status\n\n"
            "Developed by WASEEM KALUWAL")


def main():
    """Main function to run the application"""
    try:
        app = TradingJournalEnhanced()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        # Fallback to basic version
        app = ForexTradingJournalGUI()
        app.run()


if __name__ == "__main__":
    main()