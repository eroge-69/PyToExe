import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
import webbrowser
from datetime import datetime, timedelta
import random
import json
import time

# ====================== CONSTANTS ======================
APP_NAME = "IMCO Trading Suite DEMO"
VERSION = "1.0"
COMPANY = "IMCO Trading Solutions"
TERMS_URL = "https://www.imcotradingsolutions.com/terms"
PRIVACY_URL = "https://www.imcotradingsolutions.com/privacy"
SUPPORT_URL = "https://www.imcotradingsolutions.com"

# Color scheme
PRIMARY_COLOR = "#2A5CFF"  # Darker blue for professional look
SECONDARY_COLOR = "#161622"  # Darker background
ACCENT_COLOR = "#FF6B35"
TEXT_COLOR = "#FFFFFF"
DARK_BG = "#0E0E14"  # Even darker for contrast
LIGHT_TEXT = "#E0E0E0"
SUCCESS_GREEN = "#4BB543"
ERROR_RED = "#FF3B30"
WARNING_YELLOW = "#FFCC00"
PANEL_BG = "#1E1E2E"  # More contrast with secondary
BORDER_COLOR = "#2D2D3D"  # Subtler border
HOVER_COLOR = "#2D2D3D"
ACTIVE_COLOR = "#3A7BFF"
TABLE_HEADER_BG = "#252538"
TABLE_ROW_BG = "#1A1A24"
TABLE_ALT_ROW_BG = "#1E1E2A"

# Fonts
TITLE_FONT = ("Segoe UI Semibold", 24, "bold")
HEADER_FONT = ("Segoe UI Semibold", 16, "bold")
BODY_FONT = ("Segoe UI", 12)
SMALL_FONT = ("Segoe UI", 10)
BUTTON_FONT = ("Segoe UI Semibold", 12)
DISCLAIMER_FONT = ("Segoe UI", 9)
TABLE_FONT = ("Segoe UI", 11)
TABLE_HEADER_FONT = ("Segoe UI Semibold", 11)

# Mock API endpoints - Only IBKR now
BROKER_API_ENDPOINTS = {
    "Interactive Brokers": "https://api.ibkr.com"
}

# ====================== MAIN APPLICATION ======================
class ImcoTradingDemo(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self._setup_window((1400, 850))  # Slightly larger for better layout
        self._configure_appearance("Dark")
        self.connected_accounts = []  # Track connected accounts
        self.order_history = []  # Store order history
        self._generate_mock_history()  # Generate some initial history
        self.show_main_app()

    def _setup_window(self, size):
        """Configure main window settings"""
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(1200, 800)
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def _configure_appearance(self, mode):
        """Configure the application's visual appearance"""
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")

    def _generate_mock_history(self):
        """Generate realistic mock order history data with more detailed information"""
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
        sides = ["Buy", "Sell"]
        
        for i in range(50):
            symbol = random.choice(symbols)
            price = round(random.uniform(100, 500), 2)
            qty = random.randint(1, 100)
            value = round(price * qty, 2)
            slippage = round(random.uniform(0.1, 1.5), 2)
            filled_pct = random.choice([100, 100, 100, 100, 75, 50])  # Mostly filled, some partial
            
            order_time = datetime.now() - timedelta(days=random.randint(0, 30),
                                                 hours=random.randint(0, 23),
                                                 minutes=random.randint(0, 59))
            
            execution_time = random.randint(100, 5000)  # milliseconds
            
            self.order_history.append({
                "order_id": f"ORD{random.randint(100000, 999999)}",
                "symbol": symbol,
                "status": "Filled" if filled_pct == 100 else "Partially Filled",
                "side": random.choice(sides),
                "order_type": random.choice(["Market", "Limit", "Stop"]),
                "quantity": qty,
                "filled_quantity": round(qty * (filled_pct / 100)),
                "filled_pct": filled_pct,
                "price": price,
                "avg_price": round(price * (1 + (slippage/100 if random.random() > 0.5 else -slippage/100)), 2),
                "slippage_pct": slippage,
                "value": value,
                "time": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                "execution_time_ms": execution_time,
                "account": "IBKR DEMO"
            })

    # ====================== SCREEN MANAGEMENT ======================
    def show_main_app(self):
        """Show the main application interface"""
        self.clear_window()
        
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
        """Create the professional sidebar navigation"""
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

        # Logo with professional styling
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 25))
        
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
        
        # Divider
        ctk.CTkFrame(
            sidebar,
            height=1,
            fg_color=BORDER_COLOR
        ).pack(fill="x", padx=10, pady=(0, 15))

        # Navigation buttons with professional icons
        nav_buttons = [
            ("Order Management", "📊", self.show_order_management),
            ("Order History", "📜", self.show_order_history),
            ("Link Account", "🔌", self.show_link_account)
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
                height=42,
                corner_radius=4,
                border_spacing=10
            )
            btn.pack(fill="x", padx=8, pady=2)

        # Divider
        ctk.CTkFrame(
            sidebar,
            height=1,
            fg_color=BORDER_COLOR
        ).pack(fill="x", padx=10, pady=15)

        # Support button
        ctk.CTkButton(
            sidebar,
            text="  💬  Support",
            command=lambda: webbrowser.open(SUPPORT_URL),
            fg_color="transparent",
            anchor="w",
            hover_color=HOVER_COLOR,
            font=BODY_FONT,
            height=42,
            corner_radius=4,
            border_spacing=10
        ).pack(fill="x", padx=8, pady=2)

    def _create_status_bar(self, parent):
        """Create the status bar with professional styling"""
        self.status_bar = ctk.CTkFrame(
            parent,
            height=35,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Status indicators
        status_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        status_frame.pack(side="left", padx=15)
        
        # Connection status
        self.connection_status = ctk.CTkLabel(
            status_frame,
            text="● DEMO MODE",
            font=DISCLAIMER_FONT,
            text_color=WARNING_YELLOW
        )
        self.connection_status.pack(side="left", padx=5)
        
        # Last update time
        self.last_update = ctk.CTkLabel(
            status_frame,
            text=f"Last update: {datetime.now().strftime('%H:%M:%S')}",
            font=DISCLAIMER_FONT,
            text_color=LIGHT_TEXT
        )
        self.last_update.pack(side="left", padx=15)
        
        # Links
        links = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        links.pack(side="right", padx=15)
        
        ctk.CTkButton(
            links,
            text="Terms",
            command=lambda: webbrowser.open(TERMS_URL),
            width=60,
            height=20,
            font=SMALL_FONT,
            fg_color="transparent",
            hover_color=HOVER_COLOR,
            text_color=LIGHT_TEXT
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
            text_color=LIGHT_TEXT
        ).pack(side="left")

    def _create_content_area(self, parent):
        """Create the main content area with professional styling"""
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
        """Display the professional order management interface"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Header frame with breadcrumb
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="Trading > Order Management",
            font=SMALL_FONT,
            text_color=LIGHT_TEXT
        ).pack(side="left", anchor="w")
        
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.content_area,
            fg_color=PANEL_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Title with icon
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="📊  Order Management",
            font=HEADER_FONT,
            text_color=TEXT_COLOR
        ).pack(side="left")
        
        # Form frame
        form_frame = ctk.CTkFrame(
            content_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        form_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        form_frame.grid_columnconfigure(1, weight=1)

        # Define form fields configuration with professional options
        form_fields = [
            ("Account", "account_var", "dropdown", ["IBKR DEMO (DEMO456)"], True),
            ("Ticker", "ticker_entry", "entry", None, True),
            ("Action", "action_var", "radio", ["Buy", "Sell"], True),
            ("Quantity", "quantity_entry", "entry", None, True),
            ("Average Price ($)", "avg_price_entry", "entry", None, False),
            ("Slippage Threshold (%)", "slippage_entry", "entry", None, False),
            ("Aggressiveness", "aggressiveness_var", "dropdown", ["Low", "Medium", "High"], True)
        ]

        # Create form fields with professional styling
        for i, (label, attr, field_type, *args) in enumerate(form_fields):
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, sticky="ew", padx=15, pady=10)

            # Create label
            label_text = f"{label}{'*' if args[-1] else ''}"
            ctk.CTkLabel(
                row_frame,
                text=label_text,
                font=BODY_FONT,
                text_color=LIGHT_TEXT,
                width=120,
                anchor="w"
            ).pack(side="left", padx=(0, 15))

            # Create input widget based on type
            if field_type == "entry":
                entry = ctk.CTkEntry(
                    row_frame,
                    height=35,
                    font=BODY_FONT,
                    border_color=BORDER_COLOR,
                    fg_color=DARK_BG,
                    corner_radius=4
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
                    height=35,
                    font=BODY_FONT,
                    dropdown_fg_color=DARK_BG,
                    dropdown_hover_color=HOVER_COLOR
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
                        value=option.lower(),
                        font=BODY_FONT,
                        fg_color=PRIMARY_COLOR,
                        hover_color=ACTIVE_COLOR
                    )
                    radio.pack(side="left", padx=(0, 15))

                setattr(self, attr, var)

        # Action buttons with professional spacing
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=len(form_fields)+1, column=0, sticky="e", padx=15, pady=15)

        ctk.CTkButton(
            button_frame,
            text="Preview Order",
            command=self.preview_order,
            width=120,
            height=35,
            font=BUTTON_FONT,
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR,
            corner_radius=4
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Submit Order",
            command=self.confirm_order,
            width=120,
            height=35,
            font=BUTTON_FONT,
            fg_color=SUCCESS_GREEN,
            hover_color="#3AA543",
            corner_radius=4
        ).pack(side="left")

    def preview_order(self):
        """Show professional order preview"""
        # Get values from form
        account = self.account_var.get() if hasattr(self, 'account_var') else "IBKR DEMO (DEMO456)"
        action = self.action_var.get() if hasattr(self, 'action_var') else "buy"
        ticker = self.ticker_entry.get() if hasattr(self, 'ticker_entry') and self.ticker_entry.get() else "AAPL"
        quantity = self.quantity_entry.get() if hasattr(self, 'quantity_entry') and self.quantity_entry.get() else "100"
        avg_price = round(random.uniform(150, 200), 2)
        slippage = round(random.uniform(0.1, 1.5), 2)
        aggressiveness = self.aggressiveness_var.get() if hasattr(self, 'aggressiveness_var') else "Medium"
        
        # Map aggressiveness to numerical value for calculations
        agg_map = {"Low": 3, "Medium": 6, "High": 9}
        agg_value = agg_map.get(aggressiveness, 5)
        
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Order Preview")
        preview_window.geometry("500x450")
        preview_window.resizable(False, False)
        preview_window.transient(self)
        preview_window.grab_set()
        
        # Center the window
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 225
        preview_window.geometry(f"+{x}+{y}")
        
        # Preview content
        preview_frame = ctk.CTkFrame(preview_window, fg_color=PANEL_BG)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            preview_frame,
            text="Order Preview",
            font=HEADER_FONT,
            text_color=TEXT_COLOR
        ).pack(pady=(10, 20))
        
        # Order details
        details = [
            ("Account:", account),
            ("Action:", action.capitalize()),
            ("Ticker:", ticker),
            ("Quantity:", quantity),
            ("Average Price:", f"${avg_price:.2f}"),
            ("Slippage Threshold:", f"{slippage:.2f}%"),
            ("Estimated Slippage:", f"{slippage * (10 - agg_value)/10:.2f}%"),
            ("Aggressiveness:", aggressiveness),
            ("Estimated Cost:", f"${float(quantity) * avg_price:,.2f}")
        ]
        
        for label, value in details:
            detail_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                detail_frame,
                text=label,
                font=BODY_FONT,
                text_color=LIGHT_TEXT,
                width=150,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                detail_frame,
                text=value,
                font=BODY_FONT,
                text_color=TEXT_COLOR,
                anchor="w"
            ).pack(side="left")
        
        # Buttons
        button_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        button_frame.pack(side="bottom", pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Edit Order",
            command=preview_window.destroy,
            width=100,
            height=35,
            font=BUTTON_FONT,
            fg_color=SECONDARY_COLOR,
            hover_color=HOVER_COLOR
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Confirm & Submit",
            command=lambda: self._submit_preview_order(preview_window, ticker),
            width=150,
            height=35,
            font=BUTTON_FONT,
            fg_color=SUCCESS_GREEN,
            hover_color="#3AA543"
        ).pack(side="left")

    def _submit_preview_order(self, window, ticker):
        """Handle order submission from preview"""
        window.destroy()
        self.confirm_order(ticker)

    def confirm_order(self, ticker="AAPL"):
        """Show professional order confirmation"""
        # Generate realistic order details
        quantity = int(self.quantity_entry.get()) if hasattr(self, 'quantity_entry') and self.quantity_entry.get() else 100
        price = round(random.uniform(150, 200), 2)
        slippage = round(random.uniform(0.1, 1.5), 2)
        execution_time = random.randint(100, 5000)  # milliseconds
        filled_pct = random.choice([100, 100, 100, 100, 75, 50])  # Mostly filled, some partial
        
        # Add to history
        self.order_history.insert(0, {
            "order_id": f"ORD{random.randint(100000, 999999)}",
            "symbol": ticker,
            "status": "Filled" if filled_pct == 100 else "Partially Filled",
            "side": self.action_var.get().capitalize() if hasattr(self, 'action_var') else "Buy",
            "order_type": "Market",
            "quantity": quantity,
            "filled_quantity": round(quantity * (filled_pct / 100)),
            "filled_pct": filled_pct,
            "price": price,
            "avg_price": round(price * (1 + (slippage/100 if random.random() > 0.5 else -slippage/100)), 2),
            "slippage_pct": slippage,
            "value": round(quantity * price, 2),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time_ms": execution_time,
            "account": "IBKR DEMO"
        })
        
        # Show confirmation
        messagebox.showinfo(
            "Order Confirmation",
            f"Order for {ticker} has been submitted successfully!\n\n"
            f"Status: {'Filled' if filled_pct == 100 else 'Partially Filled'}\n"
            f"Order ID: {self.order_history[0]['order_id']}\n"
            f"Execution Time: {execution_time}ms\n"
            f"Average Price: ${self.order_history[0]['avg_price']:.2f}"
        )

    # ====================== ORDER HISTORY ======================
    def show_order_history(self):
        """Display professional order history with detailed information"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Header frame with breadcrumb
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="Trading > Order History",
            font=SMALL_FONT,
            text_color=LIGHT_TEXT
        ).pack(side="left", anchor="w")
        
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.content_area,
            fg_color=PANEL_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Title with icon and filter controls
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        ctk.CTkLabel(
            title_frame,
            text="📜  Order History",
            font=HEADER_FONT,
            text_color=TEXT_COLOR
        ).pack(side="left")
        
        # Filter controls
        filter_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        # Time filter
        time_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Last 24 hours", "Last 7 days", "Last 30 days", "All"],
            state="readonly",
            width=120,
            height=30,
            dropdown_fg_color=DARK_BG,
            dropdown_hover_color=HOVER_COLOR,
            command=self._filter_order_history
        )
        time_filter.set("Last 7 days")
        time_filter.pack(side="left", padx=5)
        
        # Status filter
        status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All Statuses", "Filled", "Partially Filled", "Cancelled", "Rejected"],
            state="readonly",
            width=120,
            height=30,
            dropdown_fg_color=DARK_BG,
            dropdown_hover_color=HOVER_COLOR,
            command=self._filter_order_history
        )
        status_filter.set("All Statuses")
        status_filter.pack(side="left", padx=5)
        
        # Search box
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search orders...",
            width=180,
            height=30
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self._filter_order_history)
        
        # Table frame
        table_frame = ctk.CTkFrame(
            content_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create a Treeview widget for the table
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                      background=TABLE_ROW_BG,
                      foreground=TEXT_COLOR,
                      rowheight=30,
                      fieldbackground=TABLE_ROW_BG,
                      borderwidth=0,
                      font=TABLE_FONT)
        style.configure("Treeview.Heading",
                      background=TABLE_HEADER_BG,
                      foreground=TEXT_COLOR,
                      font=TABLE_HEADER_FONT,
                      padding=5)
        style.map("Treeview",
                background=[('selected', PRIMARY_COLOR)],
                foreground=[('selected', TEXT_COLOR)])
        
        # Create the treeview
        self.history_tree = ttk.Treeview(
            table_frame,
            columns=("order_id", "time", "symbol", "side", "quantity", "filled", "avg_price", "slippage", "cost", "exec_time", "status"),
            show="headings",
            selectmode="extended",
            style="Treeview"
        )
        
        # Configure columns
        self.history_tree.column("order_id", width=100, anchor="w")
        self.history_tree.column("time", width=140, anchor="w")
        self.history_tree.column("symbol", width=80, anchor="center")
        self.history_tree.column("side", width=60, anchor="center")
        self.history_tree.column("quantity", width=80, anchor="center")
        self.history_tree.column("filled", width=80, anchor="center")
        self.history_tree.column("avg_price", width=100, anchor="center")
        self.history_tree.column("slippage", width=80, anchor="center")
        self.history_tree.column("cost", width=100, anchor="center")
        self.history_tree.column("exec_time", width=100, anchor="center")
        self.history_tree.column("status", width=100, anchor="center")
        
        # Add headings
        self.history_tree.heading("order_id", text="Order ID")
        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("symbol", text="Symbol")
        self.history_tree.heading("side", text="Side")
        self.history_tree.heading("quantity", text="Qty")
        self.history_tree.heading("filled", text="Filled %")
        self.history_tree.heading("avg_price", text="Avg Price")
        self.history_tree.heading("slippage", text="Slippage %")
        self.history_tree.heading("cost", text="Cost")
        self.history_tree.heading("exec_time", text="Exec Time")
        self.history_tree.heading("status", text="Status")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid the tree and scrollbars
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Populate with data
        self._populate_order_history()

    def _populate_order_history(self, orders=None):
        """Populate the order history table with data"""
        if orders is None:
            orders = self.order_history
            
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add data to the treeview
        for order in sorted(orders, key=lambda x: x["time"], reverse=True):
            status_color = ""
            if order["status"] == "Filled":
                status_color = SUCCESS_GREEN
            elif order["status"] == "Partially Filled":
                status_color = WARNING_YELLOW
            elif order["status"] in ["Cancelled", "Rejected"]:
                status_color = ERROR_RED
            
            self.history_tree.insert("", "end", values=(
                order["order_id"],
                order["time"],
                order["symbol"],
                order["side"],
                order["quantity"],
                f"{order['filled_pct']}%",
                f"${order['avg_price']:.2f}",
                f"{order['slippage_pct']:.2f}%",
                f"${order['value']:,.2f}",
                f"{order['execution_time_ms']}ms",
                order["status"]
            ))

    def _filter_order_history(self, event=None):
        """Filter order history based on selected filters"""
        time_filter = "Last 7 days"  # Default if we can't get the actual value
        status_filter = "All Statuses"  # Default
        
        # Try to get the actual filter values from the UI
        for widget in self.content_area.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkComboBox):
                        if "hours" in child.get() or "days" in child.get():
                            time_filter = child.get()
                        else:
                            status_filter = child.get()
        
        search_term = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        
        # Calculate date cutoff
        if time_filter == "Last 24 hours":
            cutoff = datetime.now() - timedelta(hours=24)
        elif time_filter == "Last 7 days":
            cutoff = datetime.now() - timedelta(days=7)
        elif time_filter == "Last 30 days":
            cutoff = datetime.now() - timedelta(days=30)
        else:  # "All"
            cutoff = datetime.min
        
        filtered_orders = []
        for order in self.order_history:
            order_time = datetime.strptime(order["time"], "%Y-%m-%d %H:%M:%S")
            
            # Apply time filter
            if order_time < cutoff:
                continue
                
            # Apply status filter
            if status_filter != "All Statuses" and order["status"] != status_filter:
                continue
                
            # Apply search filter
            if search_term:
                search_fields = [
                    order["order_id"],
                    order["symbol"],
                    order["side"],
                    str(order["quantity"]),
                    str(order["filled_pct"]),
                    str(order["avg_price"]),
                    str(order["slippage_pct"]),
                    str(order["value"]),
                    str(order["execution_time_ms"]),
                    order["status"]
                ]
                if not any(search_term in str(field).lower() for field in search_fields):
                    continue
            
            filtered_orders.append(order)
        
        self._populate_order_history(filtered_orders)

    # ====================== ACCOUNT MANAGEMENT ======================
    def show_link_account(self):
        """Display professional account linking interface with mock API"""
        self.clear_content_area()
        
        # Configure grid layout
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        # Header frame with breadcrumb
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="Account > Link Broker Account",
            font=SMALL_FONT,
            text_color=LIGHT_TEXT
        ).pack(side="left", anchor="w")
        
        # Main content frame
        content_frame = ctk.CTkFrame(
            self.content_area,
            fg_color=PANEL_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Title with icon
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        ctk.CTkLabel(
            title_frame,
            text="🔌  Link Broker Account",
            font=HEADER_FONT,
            text_color=TEXT_COLOR
        ).pack(side="left")
        
        # Two-column layout
        columns_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        columns_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1, minsize=300)
        columns_frame.grid_rowconfigure(0, weight=1)
        
        # Left column - Connected accounts
        connected_frame = ctk.CTkFrame(
            columns_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        connected_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        ctk.CTkLabel(
            connected_frame,
            text="Connected Accounts",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).pack(pady=(10, 15))
        
        # Connected accounts list
        self.connected_accounts_frame = ctk.CTkScrollableFrame(
            connected_frame,
            fg_color="transparent",
            height=200
        )
        self.connected_accounts_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add mock connected accounts
        self._update_connected_accounts()
        
        # Right column - Link new account
        link_frame = ctk.CTkFrame(
            columns_frame,
            fg_color=DARK_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=5
        )
        link_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        
        ctk.CTkLabel(
            link_frame,
            text="Link New Account",
            font=BODY_FONT,
            text_color=TEXT_COLOR
        ).pack(pady=(10, 15))
        
        # Form to link new account
        form_frame = ctk.CTkFrame(link_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=5)
        
        # Broker selection (only IBKR now)
        ctk.CTkLabel(
            form_frame,
            text="Broker*",
            font=BODY_FONT,
            text_color=LIGHT_TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        self.broker_var = ctk.StringVar(value="Interactive Brokers")
        broker_dropdown = ctk.CTkComboBox(
            form_frame,
            variable=self.broker_var,
            values=["Interactive Brokers"],
            state="readonly",
            height=35,
            font=BODY_FONT,
            dropdown_fg_color=DARK_BG,
            dropdown_hover_color=HOVER_COLOR
        )
        broker_dropdown.pack(fill="x", pady=(0, 15))
        
        # API Key
        ctk.CTkLabel(
            form_frame,
            text="API Key*",
            font=BODY_FONT,
            text_color=LIGHT_TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        self.api_key_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your API key",
            height=35,
            font=BODY_FONT
        )
        self.api_key_entry.pack(fill="x", pady=(0, 15))
        
        # API Secret
        ctk.CTkLabel(
            form_frame,
            text="API Secret*",
            font=BODY_FONT,
            text_color=LIGHT_TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        self.api_secret_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your API secret",
            height=35,
            font=BODY_FONT,
            show="•"
        )
        self.api_secret_entry.pack(fill="x", pady=(0, 15))
        
        # Nickname (optional)
        ctk.CTkLabel(
            form_frame,
            text="Account Nickname (optional)",
            font=BODY_FONT,
            text_color=LIGHT_TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        self.nickname_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="e.g. 'Main Trading Account'",
            height=35,
            font=BODY_FONT
        )
        self.nickname_entry.pack(fill="x", pady=(0, 20))
        
        # Link button
        ctk.CTkButton(
            form_frame,
            text="Link Account",
            command=self._link_account,
            height=40,
            font=BUTTON_FONT,
            fg_color=PRIMARY_COLOR,
            hover_color=ACTIVE_COLOR
        ).pack(fill="x")

    def _update_connected_accounts(self):
        """Update the connected accounts list"""
        for widget in self.connected_accounts_frame.winfo_children():
            widget.destroy()
        
        if not self.connected_accounts:
            ctk.CTkLabel(
                self.connected_accounts_frame,
                text="No accounts connected",
                font=SMALL_FONT,
                text_color=LIGHT_TEXT
            ).pack(pady=20)
            return
        
        for account in self.connected_accounts:
            account_frame = ctk.CTkFrame(
                self.connected_accounts_frame,
                fg_color=TABLE_ROW_BG,
                corner_radius=4
            )
            account_frame.pack(fill="x", pady=5, padx=5)
            
            # Account info
            info_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=account["nickname"] if account["nickname"] else account["broker"],
                font=BODY_FONT,
                text_color=TEXT_COLOR,
                anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                info_frame,
                text=f"{account['broker']} •••••{account['api_key'][-4:]}",
                font=SMALL_FONT,
                text_color=LIGHT_TEXT,
                anchor="w"
            ).pack(fill="x")
            
            # Disconnect button
            ctk.CTkButton(
                account_frame,
                text="Disconnect",
                width=80,
                height=30,
                font=SMALL_FONT,
                fg_color=ERROR_RED,
                hover_color="#D0352B",
                command=lambda a=account: self._disconnect_account(a)
            ).pack(side="right", padx=10)

    def _link_account(self):
        """Mock account linking functionality"""
        broker = self.broker_var.get()
        api_key = self.api_key_entry.get()
        api_secret = self.api_secret_entry.get()
        nickname = self.nickname_entry.get()
        
        if not api_key or not api_secret:
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        # Mock API connection
        self.connected_accounts.append({
            "broker": broker,
            "api_key": api_key,
            "api_secret": api_secret,
            "nickname": nickname,
            "status": "Connected",
            "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Update UI
        self._update_connected_accounts()
        
        # Clear form
        self.api_key_entry.delete(0, tk.END)
        self.api_secret_entry.delete(0, tk.END)
        self.nickname_entry.delete(0, tk.END)
        
        # Show success
        messagebox.showinfo(
            "Success",
            f"Account connected to {broker} successfully!\n\n"
            "Note: This is a demo. In the full version, we would verify the API keys "
            "and sync account data."
        )

    def _disconnect_account(self, account):
        """Disconnect an account"""
        if messagebox.askyesno(
            "Confirm Disconnect",
            f"Are you sure you want to disconnect {account['nickname'] if account['nickname'] else account['broker']}?"
        ):
            self.connected_accounts.remove(account)
            self._update_connected_accounts()
            messagebox.showinfo("Disconnected", "Account has been disconnected")

    # ====================== WINDOW MANAGEMENT ======================
    def clear_content_area(self):
        """Clear the content area while preserving sidebar and status bar"""
        if hasattr(self, 'content_area'):
            for widget in self.content_area.winfo_children():
                widget.destroy()

    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.winfo_children():
            widget.destroy()

    def _on_app_close(self):
        """Handle application close event"""
        if messagebox.askokcancel("Quit", "Do you want to close the demo application?"):
            self.destroy()

# ====================== APPLICATION ENTRY POINT ======================
if __name__ == "__main__":
    app = ImcoTradingDemo()
    app.mainloop()