import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
import win32print
import win32ui
import win32con
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import random

DB_NAME = "restaurant.db"

# ---------------- Helpers ----------------
def app_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def fmt_birr(amount):
    try:
        return f"{float(amount):,.2f} ብር"
    except:
        return f"{amount} ብር"

# ---------------- Printer Helper ----------------
def print_receipt(receipt_text):
    try:
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc('Receipt')
        hdc.StartPage()
        font = win32ui.CreateFont({
            "name": "Arial",
            "height": 60,
            "weight": win32con.FW_NORMAL
        })
        hdc.SelectObject(font)
        y = 100
        for line in receipt_text.split('\n'):
            hdc.TextOut(100, y, line)
            y += 100
        hdc.EndPage()
        hdc.EndDoc()
        win32print.ClosePrinter(hprinter)
        return True
    except Exception as e:
        messagebox.showerror("ስህተት", f"ፕሪንት አልተሳካም: {str(e)}")
        return False

# ---------------- Database Initialization ----------------
def init_database():
    db_path = app_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin','staff','cashier','waiter')) NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            category TEXT,
            stock INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER,
            status TEXT CHECK(status IN ('pending','preparing','completed','cancelled')) DEFAULT 'pending',
            total_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            waiter_id INTEGER,
            FOREIGN KEY (waiter_id) REFERENCES users (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            notes TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            amount REAL,
            payment_method TEXT CHECK(payment_method IN ('cash','credit','debit','bank')),
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_amount REAL DEFAULT 0,
            status TEXT CHECK(status IN ('pending','partial','paid')) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS credit_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_id INTEGER,
            amount REAL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (credit_id) REFERENCES credits (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            unit TEXT,
            cost REAL,
            received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS capital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waiter_id INTEGER,
            order_id INTEGER,
            amount REAL,
            tip_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (waiter_id) REFERENCES users (id),
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    """)
    conn.commit()

    # Check if tables need to be altered for new columns
    cur.execute("PRAGMA table_info(expenses)")
    expense_cols = [row[1] for row in cur.fetchall()]
    if "category" not in expense_cols:
        cur.execute("ALTER TABLE expenses ADD COLUMN category TEXT")
    
    cur.execute("PRAGMA table_info(orders)")
    order_cols = [row[1] for row in cur.fetchall()]
    if "waiter_id" not in order_cols:
        cur.execute("ALTER TABLE orders ADD COLUMN waiter_id INTEGER REFERENCES users(id)")
    
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        sample_users = [
            ("admin", sha256("admin"), "admin"),
            ("cashier", sha256("cashier"), "cashier"),
            ("waiter1", sha256("waiter1"), "waiter"),
            ("staff", sha256("staff"), "staff")
        ]
        cur.executemany(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            sample_users
        )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        sample_products = [
            ("ዶሮ ማሳ", 120.0, "ምግብ", 50),
            ("ቲፒዎ", 80.0, "ምግብ", 30),
            ("ኮላ", 25.0, "መጠጥ", 100),
            ("ስፐሻል ቡና", 35.0, "መጠጥ", 60),
            ("ኬክ", 50.0, "ምግብ", 20)
        ]
        cur.executemany(
            "INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)",
            sample_products
        )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM capital")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO capital (amount, note) VALUES (?, ?)", (0.0, "መነሻ ካፒታል"))
        conn.commit()

    conn.close()

# ---------------- Login Window ----------------
class LoginWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=10)
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))
        self.title("መግቢያ (Login)")
        self.geometry("500x400")
        self.resizable(False, False)
        self.configure(bg="#f8f9fa")
        self.on_success = on_success

        # Main container
        container = ttk.Frame(self, padding=20, style="light.TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ttk.Label(container, text="የሬስቶራንት ሲስተም", 
                          font=("Arial", 18, "bold"), 
                          style="primary.Inverse.TLabel")
        header.pack(pady=(10, 30), fill="x")

        # Form container
        form_frame = ttk.Frame(container, style="light.TFrame")
        form_frame.pack(fill="x", pady=10)

        # Username
        ttk.Label(form_frame, text="የተጠቃሚ ስም:", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(10,5), sticky="w")
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, 
                                  font=("Arial", 12), width=25)
        username_entry.grid(row=0, column=1, pady=(10,5), padx=(10,0), sticky="ew")

        # Password
        ttk.Label(form_frame, text="የይለፍ ቃል:", 
                 font=("Arial", 12, "bold")).grid(row=1, column=0, pady=(10,5), sticky="w")
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", 
                                  font=("Arial", 12), width=25)
        password_entry.grid(row=1, column=1, pady=(10,5), padx=(10,0), sticky="ew")

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="ግባ", command=self.try_login, 
                  style="success.TButton", width=10).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ዝጋ", command=self.destroy, 
                  style="secondary.TButton", width=10).pack(side="left", padx=5)

        form_frame.columnconfigure(1, weight=1)
        
        self.bind("<Return>", lambda e: self.try_login())
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # Focus on username field
        username_entry.focus()

    def try_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showerror("ስህተት", "እባክዎ የተጠቃሚ ስም �እና የይለፍ ቃል ያስገቡ")
            return
        conn = sqlite3.connect(app_db_path())
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash, role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        if not row or row[2] != sha256(password):
            messagebox.showerror("ስህተት", "የመግቢያ መረጃ ትክክል አይደለም")
            return
        user = {"id": row[0], "username": row[1], "role": row[3]}
        self.on_success(user)
        self.destroy()

# ---------------- Main App ----------------
class RestaurantSystem:
    def __init__(self, root, current_user):
        self.root = root
        self.user = current_user
        self.root.title("ሬስቶራንት ሲስተም - ሽያጭ፣ ወጪ፣ ክምችት እና ሪፖርቶች")
        self.root.geometry("1280x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("flatly")
        
        # Custom styles
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        self.style.configure("Subheader.TLabel", font=("Arial", 14, "bold"))
        self.style.configure("Metric.TLabel", font=("Arial", 14))
        self.style.configure("MetricValue.TLabel", font=("Arial", 18, "bold"))
        self.style.configure("Treeview", font=("Arial", 11), rowheight=30)
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        self.style.configure("TButton", font=("Arial", 11), padding=6)
        self.style.configure("TNotebook.Tab", font=("Arial", 12, "bold"))

        # DB connection
        db_path = app_db_path()
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

        # Cart for bulk sales
        self.cart_items = []
        self.current_order_items = []
        self.current_order_id = None

        # Create header frame
        self.header_frame = ttk.Frame(self.root, style="primary.TFrame", height=60)
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.header_frame.pack_propagate(False)
        
        # Header content
        ttk.Label(self.header_frame, text="ሬስቶራንት ሲስተም", 
                 style="primary.Inverse.TLabel", 
                 font=("Arial", 18, "bold")).pack(side="left", padx=20)
        
        user_info = ttk.Label(self.header_frame, 
                             text=f"ተጠቃሚ: {self.user['username']} ({self.user['role']})", 
                             style="primary.Inverse.TLabel",
                             font=("Arial", 12))
        user_info.pack(side="right", padx=20)

        # Notebook tabs
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dashboard_frame = ttk.Frame(self.notebook, padding=10)
        self.orders_frame = ttk.Frame(self.notebook, padding=10)
        self.sales_frame = ttk.Frame(self.notebook, padding=10)
        self.expense_frame = ttk.Frame(self.notebook, padding=10)
        self.credit_frame = ttk.Frame(self.notebook, padding=10)
        self.staff_frame = ttk.Frame(self.notebook, padding=10)
        self.inventory_frame = ttk.Frame(self.notebook, padding=10)
        self.products_frame = ttk.Frame(self.notebook, padding=10)
        self.reports_frame = ttk.Frame(self.notebook, padding=10)
        self.users_frame = ttk.Frame(self.notebook, padding=10)
        self.capital_frame = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.dashboard_frame, text="ዳሽቦርድ")
        self.notebook.add(self.orders_frame, text="ኦርደሮች")
        self.notebook.add(self.sales_frame, text="ሽያጭ")
        self.notebook.add(self.expense_frame, text="ወጪዎች")
        self.notebook.add(self.credit_frame, text="ክሬዲት/ዴቢት")
        if self.user["role"] in ["admin", "waiter"]:
            self.notebook.add(self.staff_frame, text="አገልጋዮች")
        self.notebook.add(self.inventory_frame, text="የገቢ እቃዎች")
        self.notebook.add(self.products_frame, text="ምርቶች")
        self.notebook.add(self.reports_frame, text="ሪፖርቶች")
        if self.user["role"] == "admin":
            self.notebook.add(self.users_frame, text="ተጠቃሚዎች")
            self.notebook.add(self.capital_frame, text="ካፒታል")

        # Build UI
        self.build_dashboard_tab()
        self.build_orders_tab()
        self.build_sales_tab()
        self.build_expense_tab()
        self.build_credit_tab()
        if self.user["role"] in ["admin", "waiter"]:
            self.build_staff_tab()
        self.build_inventory_tab()
        self.build_products_tab()
        self.build_reports_tab()
        if self.user["role"] == "admin":
            self.build_users_tab()
            self.build_capital_tab()

        # Load initial data
        self.refresh_all()

    # ---------------- Dashboard ----------------
    def build_dashboard_tab(self):
        # Metrics section
        metrics_frame = ttk.LabelFrame(self.dashboard_frame, text="የሥራ አፈጻጸም መለኪያዎች", style="info.TLabelframe")
        metrics_frame.pack(fill="x", pady=(0, 10), padx=10)

        metrics_container = ttk.Frame(metrics_frame)
        metrics_container.pack(fill="x", padx=10, pady=10)

        self.total_sales_var = tk.StringVar(value="0 ብር")
        self.total_expenses_var = tk.StringVar(value="0 ብር")
        self.net_profit_var = tk.StringVar(value="0 ብር")
        self.current_capital_var = tk.StringVar(value="0 ብር")
        self.today_orders_var = tk.StringVar(value="0")
        self.today_income_var = tk.StringVar(value="0 ብር")

        def metric_box(label, var, style):
            frame = ttk.Frame(metrics_container, style="light.TFrame")
            frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            
            lbl = ttk.Label(frame, text=label, style="Metric.TLabel")
            lbl.pack(pady=(5, 2))
            
            val = ttk.Label(frame, textvariable=var, style="MetricValue.TLabel")
            val.pack(pady=(2, 5))
            
            # Add some color based on the metric type
            if style == "sales":
                frame.configure(style="success.TFrame")
                lbl.configure(style="success.Inverse.TLabel")
                val.configure(style="success.Inverse.TLabel")
            elif style == "expenses":
                frame.configure(style="danger.TFrame")
                lbl.configure(style="danger.Inverse.TLabel")
                val.configure(style="danger.Inverse.TLabel")
            elif style == "profit":
                frame.configure(style="info.TFrame")
                lbl.configure(style="info.Inverse.TLabel")
                val.configure(style="info.Inverse.TLabel")
            elif style == "capital":
                frame.configure(style="warning.TFrame")
                lbl.configure(style="warning.Inverse.TLabel")
                val.configure(style="warning.Inverse.TLabel")
            elif style == "orders":
                frame.configure(style="primary.TFrame")
                lbl.configure(style="primary.Inverse.TLabel")
                val.configure(style="primary.Inverse.TLabel")
            elif style == "income":
                frame.configure(style="secondary.TFrame")
                lbl.configure(style="secondary.Inverse.TLabel")
                val.configure(style="secondary.Inverse.TLabel")
                
            return frame

        metric_box("ጠቅላላ ሽያጭ", self.total_sales_var, "sales")
        metric_box("ጠቅላላ ወጪ", self.total_expenses_var, "expenses")
        metric_box("የትርፍ ገንዘብ", self.net_profit_var, "profit")
        metric_box("የአሁኑ ካፒታል", self.current_capital_var, "capital")
        metric_box("የቀኑ ኦርደሮች", self.today_orders_var, "orders")
        metric_box("የቀኑ ገቢ", self.today_income_var, "income")

        # Recent activity section
        mid = ttk.Frame(self.dashboard_frame)
        mid.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(mid, text="የቅርብ ሽያጮች", style="info.TLabelframe")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.recent_sales_tree = ttk.Treeview(left, columns=("date", "product", "qty", "total"), 
                                             show="headings", height=8, style="Treeview")
        for c, t, w in [("date","ቀን",140), ("product","ምርት",180), ("qty","ብዛት",80), ("total","ጠቅላላ",120)]:
            self.recent_sales_tree.heading(c, text=t)
            self.recent_sales_tree.column(c, width=w, anchor="w")
        
        scrollbar_sales = ttk.Scrollbar(left, orient="vertical", command=self.recent_sales_tree.yview)
        self.recent_sales_tree.configure(yscrollcommand=scrollbar_sales.set)
        
        self.recent_sales_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_sales.pack(side="right", fill="y", pady=5)

        right = ttk.LabelFrame(mid, text="የቅርብ ወጪዎች", style="info.TLabelframe")
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.recent_exp_tree = ttk.Treeview(right, columns=("date", "desc", "amount"), 
                                           show="headings", height=8, style="Treeview")
        for c, t, w in [("date","ቀን",140), ("desc","መግለጫ",220), ("amount","መጠን",120)]:
            self.recent_exp_tree.heading(c, text=t)
            self.recent_exp_tree.column(c, width=w, anchor="w")
            
        scrollbar_exp = ttk.Scrollbar(right, orient="vertical", command=self.recent_exp_tree.yview)
        self.recent_exp_tree.configure(yscrollcommand=scrollbar_exp.set)
        
        self.recent_exp_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_exp.pack(side="right", fill="y", pady=5)

        # Low stock and chart section
        bottom = ttk.Frame(self.dashboard_frame)
        bottom.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        low_stock_frame = ttk.LabelFrame(bottom, text="ዝቅተኛ ክምችት ማስጠንቀቂያ", style="warning.TLabelframe")
        low_stock_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.low_stock_tree = ttk.Treeview(low_stock_frame, columns=("product", "stock"), 
                                          show="headings", height=4, style="Treeview")
        for c, t, w in [("product","ምርት",300), ("stock","ክምችት",100)]:
            self.low_stock_tree.heading(c, text=t)
            self.low_stock_tree.column(c, width=w, anchor="w")
            
        scrollbar_low = ttk.Scrollbar(low_stock_frame, orient="vertical", command=self.low_stock_tree.yview)
        self.low_stock_tree.configure(yscrollcommand=scrollbar_low.set)
        
        self.low_stock_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_low.pack(side="right", fill="y", pady=5)

        chart_frame = ttk.LabelFrame(bottom, text="የሽያጭ እና ወጪ ዝርዝር (30 ቀን)", style="info.TLabelframe")
        chart_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.fig_dash = Figure(figsize=(6, 2.8), dpi=100)
        self.ax_dash = self.fig_dash.add_subplot(111)
        self.canvas_dash = FigureCanvasTkAgg(self.fig_dash, master=chart_frame)
        self.canvas_dash.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_dashboard(self):
        # Get today's date
        today = datetime.now().date().isoformat()
        
        self.cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status='completed'")
        total_sales = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM expenses")
        total_exp = self.cursor.fetchone()[0] or 0.0
        net = total_sales - total_exp

        # Get today's orders count
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = ?", (today,))
        today_orders = self.cursor.fetchone()[0] or 0
        
        # Get today's income
        self.cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE DATE(created_at) = ? AND status = 'completed'", (today,))
        today_income = self.cursor.fetchone()[0] or 0.0

        self.total_sales_var.set(fmt_birr(total_sales))
        self.total_expenses_var.set(fmt_birr(total_exp))
        self.net_profit_var.set(fmt_birr(net))
        self.today_orders_var.set(str(today_orders))
        self.today_income_var.set(fmt_birr(today_income))

        self.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM capital")
        current_capital = self.cursor.fetchone()[0] or 0.0
        self.current_capital_var.set(fmt_birr(current_capital))

        self.recent_sales_tree.delete(*self.recent_sales_tree.get_children())
        self.cursor.execute('''
            SELECT o.created_at, p.name, oi.quantity, oi.price * oi.quantity as total
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status = 'completed'
            ORDER BY o.created_at DESC LIMIT 15
        ''')
        for row in self.cursor.fetchall():
            d = str(row[0]).split('.')[0] if row[0] else ""
            self.recent_sales_tree.insert("", "end", values=(d, row[1], row[2], fmt_birr(row[3])))

        self.recent_exp_tree.delete(*self.recent_exp_tree.get_children())
        self.cursor.execute('''SELECT expense_date, description, amount FROM expenses ORDER BY expense_date DESC LIMIT 15''')
        for row in self.cursor.fetchall():
            d = str(row[0]).split('.')[0] if row[0] else ""
            self.recent_exp_tree.insert("", "end", values=(d, row[1], fmt_birr(row[2])))

        self.low_stock_tree.delete(*self.low_stock_tree.get_children())
        self.cursor.execute("SELECT name, stock FROM products WHERE stock <= 5 ORDER BY stock")
        for name, stock in self.cursor.fetchall():
            self.low_stock_tree.insert("", "end", values=(name, stock))

        start = (datetime.now() - timedelta(days=29)).date()
        self.cursor.execute('''
            SELECT DATE(o.created_at), SUM(oi.price * oi.quantity)
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'completed' AND DATE(o.created_at) >= DATE(?)
            GROUP BY DATE(o.created_at) ORDER BY DATE(o.created_at)
        ''', (start.isoformat(),))
        sales_series = {row[0]: row[1] for row in self.cursor.fetchall()}
        self.cursor.execute('''
            SELECT DATE(expense_date), SUM(amount) FROM expenses
            WHERE DATE(expense_date) >= DATE(?)
            GROUP BY DATE(expense_date) ORDER BY DATE(expense_date)
        ''', (start.isoformat(),))
        exp_series = {row[0]: row[1] for row in self.cursor.fetchall()}

        dates = [start + timedelta(days=i) for i in range(30)]
        sales_vals = [sales_series.get(d.isoformat(), 0) for d in dates]
        exp_vals = [exp_series.get(d.isoformat(), 0) for d in dates]

        self.ax_dash.clear()
        self.ax_dash.plot(dates, sales_vals, label="ሽያጭ", color="#007bff", marker='o', markersize=3)
        self.ax_dash.plot(dates, exp_vals, label="ወጪ", color="#dc3545", marker='s', markersize=3)
        self.ax_dash.set_xlabel("ቀን")
        self.ax_dash.set_ylabel("መጠን")
        self.ax_dash.legend()
        self.ax_dash.grid(True, alpha=0.3)
        self.fig_dash.tight_layout()
        self.canvas_dash.draw()

    # ---------------- Orders Management ----------------
    def build_orders_tab(self):
        frm = self.orders_frame
        
        # Order creation section
        order_frame = ttk.LabelFrame(frm, text="አዲስ ኦርደር", style="info.TLabelframe")
        order_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Table number
        ttk.Label(order_frame, text="ሰንጠረዥ ቁጥር:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.table_var = tk.StringVar()
        ttk.Entry(order_frame, textvariable=self.table_var, width=10, style="primary.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Product selection
        ttk.Label(order_frame, text="ምርት ምረጥ:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.order_product_var = tk.StringVar()
        self.order_product_combo = ttk.Combobox(order_frame, textvariable=self.order_product_var, state="readonly", width=20, style="primary.TCombobox")
        self.order_product_combo.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.order_product_combo.bind("<<ComboboxSelected>>", self.update_order_product_price)
        
        # Quantity
        ttk.Label(order_frame, text="ብዛት:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.order_qty_var = tk.StringVar(value="1")
        ttk.Entry(order_frame, textvariable=self.order_qty_var, width=5, style="primary.TEntry").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        
        # Price
        ttk.Label(order_frame, text="ዋጋ:", style="TLabel").grid(row=0, column=6, padx=10, pady=10, sticky="w")
        self.order_price_var = tk.StringVar(value="0.00")
        ttk.Label(order_frame, textvariable=self.order_price_var, style="TLabel").grid(row=0, column=7, padx=10, pady=10, sticky="w")
        
        # Add to order button
        ttk.Button(order_frame, text="ወደ ኦርደር ጨምር", command=self.add_to_order, style="primary.TButton").grid(row=0, column=8, padx=10, pady=10)
        
        # Create order button
        ttk.Button(order_frame, text="አዲስ ኦርደር ፍጠር", command=self.create_new_order, style="success.TButton").grid(row=0, column=9, padx=10, pady=10)
        
        order_frame.columnconfigure(3, weight=1)
        
        # Current order items
        items_frame = ttk.LabelFrame(frm, text="የኦርደር ዝርዝር", style="info.TLabelframe")
        items_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        self.order_tree = ttk.Treeview(items_frame, columns=("product", "qty", "price", "total"), show="headings", height=5, style="Treeview")
        for c, t, w in [("product","ምርት",200), ("qty","ብዛት",80), ("price","ዋጋ",100), ("total","ጠቅላላ",100)]:
            self.order_tree.heading(c, text=t)
            self.order_tree.column(c, width=w, anchor="w")
            
        scrollbar_order = ttk.Scrollbar(items_frame, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar_order.set)
        
        self.order_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_order.pack(side="right", fill="y", pady=5)
        
        # Order total
        total_frame = ttk.Frame(items_frame)
        total_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Label(total_frame, text="ጠቅላላ ዋጋ:", style="TLabel").pack(anchor="e")
        self.order_total_var = tk.StringVar(value="0.00 ብር")
        ttk.Label(total_frame, textvariable=self.order_total_var, style="MetricValue.TLabel").pack(anchor="e")
        
        # Order actions
        action_frame = ttk.Frame(items_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="ኦርደር አስቀምጥ", command=self.save_order, style="success.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ኦርደር አቋርጥ", command=self.cancel_order, style="danger.TButton").pack(pady=5)
        
        # Active orders section
        active_frame = ttk.LabelFrame(frm, text="ንቁ ኦርደሮች", style="info.TLabelframe")
        active_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.active_orders_tree = ttk.Treeview(active_frame, columns=("id", "table", "status", "total", "created"), show="headings", height=10, style="Treeview")
        for c, t, w in [("id","ID",50), ("table","ሰንጠረዥ",80), ("status","ሁኔታ",100), ("total","ጠቅላላ",100), ("created","የተፈጠረበት",140)]:
            self.active_orders_tree.heading(c, text=t)
            self.active_orders_tree.column(c, width=w, anchor="w")
            
        scrollbar_active = ttk.Scrollbar(active_frame, orient="vertical", command=self.active_orders_tree.yview)
        self.active_orders_tree.configure(yscrollcommand=scrollbar_active.set)
        
        self.active_orders_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_active.pack(side="right", fill="y", pady=5)
        
        # Order actions
        order_action_frame = ttk.Frame(active_frame)
        order_action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(order_action_frame, text="ኦርደር አሳይ", command=self.show_order_details, style="primary.TButton").pack(pady=5)
        ttk.Button(order_action_frame, text="ሁኔታ ቀይር", command=self.change_order_status, style="warning.TButton").pack(pady=5)
        ttk.Button(order_action_frame, text="ኦርደር ሰርዝ", command=self.delete_order, style="danger.TButton").pack(pady=5)
        ttk.Button(order_action_frame, text="ክፍያ አስገባ", command=self.process_payment, style="success.TButton").pack(pady=5)
        
        # Bind selection event
        self.active_orders_tree.bind("<<TreeviewSelect>>", self.on_order_select)
        
    def update_order_product_price(self, event):
        product_name = self.order_product_var.get()
        if product_name:
            self.cursor.execute("SELECT price FROM products WHERE name=?", (product_name,))
            result = self.cursor.fetchone()
            if result:
                self.order_price_var.set(f"{result[0]:.2f}")
                
    def add_to_order(self):
        product_name = self.order_product_var.get()
        qty = self.order_qty_var.get()
        
        if not product_name or not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ምርት እና ብዛት ያስገቡ")
            return
            
        qty = int(qty)
        self.cursor.execute("SELECT id, price FROM products WHERE name=?", (product_name,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("ስህተት", "ምርት አልተገኘም")
            return
            
        product_id, price = result
        total = qty * price
        
        # Add to current order items
        self.current_order_items.append({
            "product_id": product_id,
            "product_name": product_name,
            "quantity": qty,
            "price": price,
            "total": total
        })
        
        # Update the order tree
        self.order_tree.insert("", "end", values=(product_name, qty, f"{price:.2f}", f"{total:.2f}"))
        
        # Update total
        order_total = sum(item["total"] for item in self.current_order_items)
        self.order_total_var.set(f"{order_total:.2f} ብር")
        
        # Reset input fields
        self.order_qty_var.set("1")
        self.order_product_var.set("")
        self.order_price_var.set("0.00")
        
    def create_new_order(self):
        # Clear current order
        self.current_order_items = []
        self.order_tree.delete(*self.order_tree.get_children())
        self.order_total_var.set("0.00 ብር")
        self.table_var.set("")
        self.current_order_id = None
        
    def save_order(self):
        table_num = self.table_var.get()
        if not table_num.isdigit() or not self.current_order_items:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ሰንጠረዥ ቁጥር ያስገቡ እና ምርቶችን ያክሉ")
            return
            
        table_num = int(table_num)
        total_amount = sum(item["total"] for item in self.current_order_items)
        
        try:
            if self.current_order_id:
                # Update existing order
                self.cursor.execute("UPDATE orders SET table_number=?, total_amount=? WHERE id=?", 
                                  (table_num, total_amount, self.current_order_id))
                # Delete existing items
                self.cursor.execute("DELETE FROM order_items WHERE order_id=?", (self.current_order_id,))
                order_id = self.current_order_id
            else:
                # Create new order
                self.cursor.execute("INSERT INTO orders (table_number, total_amount, waiter_id) VALUES (?, ?, ?)",
                                  (table_num, total_amount, self.user["id"]))
                order_id = self.cursor.lastrowid
                
            # Add order items
            for item in self.current_order_items:
                self.cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                                  (order_id, item["product_id"], item["quantity"], item["price"]))
                
            self.conn.commit()
            messagebox.showinfo("ተሳክቷል", f"ኦርደር በትክክል ተመዝግቧል (ID: {order_id})")
            self.create_new_order()
            self.refresh_orders()
        except Exception as e:
            messagebox.showerror("ስህተት", f"ኦርደር ማስቀመጥ አልተሳካም: {str(e)}")
            
    def cancel_order(self):
        self.create_new_order()
        
    def refresh_orders(self):
        self.active_orders_tree.delete(*self.active_orders_tree.get_children())
        
        self.cursor.execute('''
            SELECT o.id, o.table_number, o.status, o.total_amount, o.created_at
            FROM orders o
            WHERE o.status != 'completed'
            ORDER BY o.created_at DESC
        ''')
        
        for row in self.cursor.fetchall():
            created = str(row[4]).split('.')[0] if row[4] else ""
            self.active_orders_tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:.2f}", created))
            
        # Update product combo
        self.order_product_combo['values'] = self.get_product_names()
        
    def on_order_select(self, event):
        selection = self.active_orders_tree.selection()
        if not selection:
            return
            
        item = self.active_orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        self.current_order_id = order_id
        self.current_order_items = []
        self.order_tree.delete(*self.order_tree.get_children())
        
        # Load order details
        self.cursor.execute("SELECT table_number FROM orders WHERE id=?", (order_id,))
        result = self.cursor.fetchone()
        if result:
            self.table_var.set(str(result[0]))
            
        self.cursor.execute('''
            SELECT p.name, oi.quantity, oi.price, (oi.quantity * oi.price) as total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        
        total_amount = 0
        for row in self.cursor.fetchall():
            self.order_tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f}", f"{row[3]:.2f}"))
            self.current_order_items.append({
                "product_name": row[0],
                "quantity": row[1],
                "price": row[2],
                "total": row[3]
            })
            total_amount += row[3]
            
        self.order_total_var.set(f"{total_amount:.2f} ብር")
        
    def show_order_details(self):
        selection = self.active_orders_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ኦርደር ይምረጡ")
            return
            
        item = self.active_orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        # Show order details in a new window
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"የኦርደር ዝርዝር - ID: {order_id}")
        detail_win.geometry("500x400")
        
        ttk.Label(detail_win, text=f"የኦርደር ዝርዝር - ID: {order_id}", style="Header.TLabel").pack(pady=10)
        
        tree = ttk.Treeview(detail_win, columns=("product", "qty", "price", "total"), show="headings", height=15)
        for c, t, w in [("product","ምርት",200), ("qty","ብዛት",80), ("price","ዋጋ",100), ("total","ጠቅላላ",100)]:
            tree.heading(c, text=t)
            tree.column(c, width=w, anchor="w")
            
        scrollbar = ttk.Scrollbar(detail_win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        self.cursor.execute('''
            SELECT p.name, oi.quantity, oi.price, (oi.quantity * oi.price) as total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        
        total = 0
        for row in self.cursor.fetchall():
            tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f}", f"{row[3]:.2f}"))
            total += row[3]
            
        ttk.Label(detail_win, text=f"ጠቅላላ: {total:.2f} ብር", style="MetricValue.TLabel").pack(pady=10)
        
    def change_order_status(self):
        selection = self.active_orders_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ኦርደር ይምረጡ")
            return
            
        item = self.active_orders_tree.item(selection[0])
        order_id = item['values'][0]
        current_status = item['values'][2]
        
        statuses = ["pending", "preparing", "completed", "cancelled"]
        current_idx = statuses.index(current_status) if current_status in statuses else 0
        
        # Create status selection dialog
        status_win = tk.Toplevel(self.root)
        status_win.title("ሁኔታ ቀይር")
        status_win.geometry("300x200")
        
        ttk.Label(status_win, text="አዲስ ሁኔታ ምረጥ:", style="TLabel").pack(pady=10)
        
        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(status_win, textvariable=status_var, values=statuses, state="readonly")
        status_combo.pack(pady=10)
        
        def update_status():
            new_status = status_var.get()
            try:
                self.cursor.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
                if new_status == "completed":
                    self.cursor.execute("UPDATE orders SET completed_at=CURRENT_TIMESTAMP WHERE id=?", (order_id,))
                self.conn.commit()
                messagebox.showinfo("ተሳክቷል", "ሁኔታ በትክክል ተቀይሯል")
                status_win.destroy()
                self.refresh_orders()
            except Exception as e:
                messagebox.showerror("ስህተት", f"ሁኔታ ማዘመን አልተሳካም: {str(e)}")
                
        ttk.Button(status_win, text="አዘምን", command=update_status, style="primary.TButton").pack(pady=10)
        
    def delete_order(self):
        selection = self.active_orders_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ኦርደር ይምረጡ")
            return
            
        item = self.active_orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        if messagebox.askyesno("አረጋግጥ", "እርግጠኛ ነዎት ይህን ኦርደር ለማስወገድ?"):
            try:
                self.cursor.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
                self.cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
                self.conn.commit()
                messagebox.showinfo("ተሳክቷል", "ኦርደር በትክክል ተሰርዟል")
                self.refresh_orders()
                self.create_new_order()
            except Exception as e:
                messagebox.showerror("ስህተት", f"ኦርደር ማስወገድ አልተሳካም: {str(e)}")
                
    def process_payment(self):
        selection = self.active_orders_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ኦርደር ይምረጡ")
            return
            
        item = self.active_orders_tree.item(selection[0])
        order_id = item['values'][0]
        total_amount = float(item['values'][3])
        
        # Check if order is completed
        self.cursor.execute("SELECT status FROM orders WHERE id=?", (order_id,))
        result = self.cursor.fetchone()
        if result and result[0] != "completed":
            messagebox.showwarning("ማስጠንቀቂያ", "ክፍያ ለመስራት ኦርደሩ መጠናቀቅ አለበት")
            return
            
        # Create payment window
        pay_win = tk.Toplevel(self.root)
        pay_win.title("ክፍያ አስገባ")
        pay_win.geometry("400x300")
        
        ttk.Label(pay_win, text=f"ክፍያ ለኦርደር ID: {order_id}", style="Header.TLabel").pack(pady=10)
        ttk.Label(pay_win, text=f"ጠቅላላ ዋጋ: {total_amount:.2f} ብር", style="MetricValue.TLabel").pack(pady=5)
        
        # Payment method
        ttk.Label(pay_win, text="የክፍያ ዘዴ:", style="TLabel").pack(pady=5)
        method_var = tk.StringVar(value="cash")
        methods = [("እጅ ገንዘብ", "cash"), ("ክሬዲት", "credit"), ("ዴቢት", "debit"), ("ባንክ", "bank")]
        
        method_frame = ttk.Frame(pay_win)
        method_frame.pack(pady=5)
        
        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, value=value, variable=method_var).pack(side="left", padx=5)
            
        # Amount paid
        ttk.Label(pay_win, text="የተከፈለ መጠን:", style="TLabel").pack(pady=5)
        amount_var = tk.StringVar(value=f"{total_amount:.2f}")
        ttk.Entry(pay_win, textvariable=amount_var, style="primary.TEntry").pack(pady=5)
        
        def process_payment():
            try:
                paid_amount = float(amount_var.get())
                method = method_var.get()
                
                if paid_amount < total_amount:
                    messagebox.showwarning("ማስጠንቀቂያ", "የተከፈለው መጠን ከጠቅላላ ዋጋ ያንሳል")
                    return
                    
                # Record payment
                self.cursor.execute("INSERT INTO payments (order_id, amount, payment_method) VALUES (?, ?, ?)",
                                  (order_id, paid_amount, method))
                
                # Update order status if needed
                self.cursor.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
                
                self.conn.commit()
                
                # Print receipt
                if messagebox.askyesno("ሪሲት", "ሪሲት ልታተም?"):
                    receipt_text = f"""
                    ሬስቶራንት ሲስተም
                    --------------------
                    ኦርደር ID: {order_id}
                    ቀን: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    --------------------
                    ጠቅላላ: {total_amount:.2f} ብር
                    የተከፈለ: {paid_amount:.2f} ብር
                    ለውጥ: {paid_amount - total_amount:.2f} ብር
                    የክፍያ ዘዴ: {method}
                    --------------------
                    እናመሰግናለን!
                    """
                    print_receipt(receipt_text)
                
                messagebox.showinfo("ተሳክቷል", "ክፍያ በትክክል ተመዝግቧል")
                pay_win.destroy()
                self.refresh_orders()
                
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥር ያስገቡ")
            except Exception as e:
                messagebox.showerror("ስህተት", f"ክፍያ ማስገባት አልተሳካም: {str(e)}")
                
        ttk.Button(pay_win, text="ክፍያ አስገባ", command=process_payment, style="success.TButton").pack(pady=20)

    # ---------------- Sales/Cashier ----------------
    def build_sales_tab(self):
        frm = self.sales_frame
        
        # Sales entry section
        sales_frame = ttk.LabelFrame(frm, text="አዲስ ሽያጭ", style="info.TLabelframe")
        sales_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Product selection
        ttk.Label(sales_frame, text="ምርት:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.sale_product_var = tk.StringVar()
        self.sale_product_combo = ttk.Combobox(sales_frame, textvariable=self.sale_product_var, state="readonly", width=20, style="primary.TCombobox")
        self.sale_product_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.sale_product_combo.bind("<<ComboboxSelected>>", self.update_sale_product_price)
        
        # Load products into combobox
        self.refresh_sales_products()  # ይህንን መስመር ይጨምሩ
        
        # Quantity
        ttk.Label(sales_frame, text="ብዛት:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.sale_qty_var = tk.StringVar(value="1")
        ttk.Entry(sales_frame, textvariable=self.sale_qty_var, width=5, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Price
        ttk.Label(sales_frame, text="ዋጋ:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.sale_price_var = tk.StringVar(value="0.00")
        ttk.Label(sales_frame, textvariable=self.sale_price_var, style="TLabel").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        
        # Add to cart button
        ttk.Button(sales_frame, text="ወደ ዘንቢል ጨምር", command=self.add_to_cart, style="primary.TButton").grid(row=0, column=6, padx=10, pady=10)
        
        # Clear cart button
        ttk.Button(sales_frame, text="ዘንቢል አጽዳ", command=self.clear_cart, style="danger.TButton").grid(row=0, column=7, padx=10, pady=10)
        
        sales_frame.columnconfigure(1, weight=1)
        
        # Cart items
        cart_frame = ttk.LabelFrame(frm, text="የሽያጭ ዘንቢል", style="info.TLabelframe")
        cart_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        self.cart_tree = ttk.Treeview(cart_frame, columns=("product", "qty", "price", "total"), show="headings", height=5, style="Treeview")
        for c, t, w in [("product","ምርት",200), ("qty","ብዛት",80), ("price","ዋጋ",100), ("total","ጠቅላላ",100)]:
            self.cart_tree.heading(c, text=t)
            self.cart_tree.column(c, width=w, anchor="w")
            
        scrollbar_cart = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar_cart.set)
        
        self.cart_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_cart.pack(side="right", fill="y", pady=5)
        
        # Cart total
        total_frame = ttk.Frame(cart_frame)
        total_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Label(total_frame, text="ጠቅላላ ዋጋ:", style="TLabel").pack(anchor="e")
        self.cart_total_var = tk.StringVar(value="0.00 ብር")
        ttk.Label(total_frame, textvariable=self.cart_total_var, style="MetricValue.TLabel").pack(anchor="e")
        
        # Payment section
        payment_frame = ttk.LabelFrame(frm, text="ክፍያ", style="info.TLabelframe")
        payment_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Payment method
        ttk.Label(payment_frame, text="የክፍያ ዘዴ:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.payment_method_var = tk.StringVar(value="cash")
        methods = [("እጅ ገንዘብ", "cash"), ("ክሬዲት", "credit"), ("ዴቢት", "debit"), ("ባንክ", "bank")]
        
        method_frame = ttk.Frame(payment_frame)
        method_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, value=value, variable=self.payment_method_var).pack(side="left", padx=5)
            
        # Process payment button
        ttk.Button(payment_frame, text="ክፍያ አስገባ", command=self.process_sale_payment, style="success.TButton").grid(row=0, column=2, padx=10, pady=10)
        
        # Recent sales section
        recent_frame = ttk.LabelFrame(frm, text="የቅርብ ሽያጮች", style="info.TLabelframe")
        recent_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.sales_tree = ttk.Treeview(recent_frame, columns=("id", "date", "product", "qty", "price", "total", "method"), show="headings", height=10, style="Treeview")
        for c, t, w in [("id","ID",50), ("date","ቀን",140), ("product","ምርት",150), ("qty","ብዛት",80), ("price","ዋጋ",80), ("total","ጠቅላላ",100), ("method","ዘዴ",80)]:
            self.sales_tree.heading(c, text=t)
            self.sales_tree.column(c, width=w, anchor="w")
            
        scrollbar_sales = ttk.Scrollbar(recent_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar_sales.set)
        
        self.sales_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_sales.pack(side="right", fill="y", pady=5)
        
        # Sales actions
        sales_action_frame = ttk.Frame(recent_frame)
        sales_action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(sales_action_frame, text="ዝርዝር አሳይ", command=self.show_sale_details, style="primary.TButton").pack(pady=5)
        ttk.Button(sales_action_frame, text="ሪሲት አተም", command=self.print_sale_receipt, style="info.TButton").pack(pady=5)
        ttk.Button(sales_action_frame, text="ሽያጭ ሰርዝ", command=self.delete_sale, style="danger.TButton").pack(pady=5)
        
    def refresh_sales_products(self):
        """የሽያጭ ምርት ማውጫውን በምርት ስሞች ይሙላው"""
        self.sale_product_combo['values'] = self.get_product_names()
        
    def update_sale_product_price(self, event):
        product_name = self.sale_product_var.get()
        if product_name:
            self.cursor.execute("SELECT price FROM products WHERE name=?", (product_name,))
            result = self.cursor.fetchone()
            if result:
                self.sale_price_var.set(f"{result[0]:.2f}")
                
    def add_to_cart(self):
        product_name = self.sale_product_var.get()
        qty = self.sale_qty_var.get()
        
        if not product_name or not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ምርት እና ብዛት ያስገቡ")
            return
            
        qty = int(qty)
        self.cursor.execute("SELECT id, price, stock FROM products WHERE name=?", (product_name,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("ስህተት", "ምርት አልተገኘም")
            return
            
        product_id, price, stock = result
        
        if stock < qty:
            messagebox.showerror("ስህተት", f"በቂ ክምችት የለም። የሚገኘው: {stock}")
            return
            
        total = qty * price
        
        # Add to cart
        self.cart_items.append({
            "product_id": product_id,
            "product_name": product_name,
            "quantity": qty,
            "price": price,
            "total": total
        })
        
        # Update the cart tree
        self.cart_tree.insert("", "end", values=(product_name, qty, f"{price:.2f}", f"{total:.2f}"))
        
        # Update total
        cart_total = sum(item["total"] for item in self.cart_items)
        self.cart_total_var.set(f"{cart_total:.2f} ብር")
        
        # Reset input fields
        self.sale_qty_var.set("1")
        self.sale_product_var.set("")
        self.sale_price_var.set("0.00")
        
    def clear_cart(self):
        self.cart_items = []
        self.cart_tree.delete(*self.cart_tree.get_children())
        self.cart_total_var.set("0.00 ብር")
        
    def process_sale_payment(self):
        if not self.cart_items:
            messagebox.showerror("ስህተት", "ዘንቢሉ ባዶ ነው")
            return
            
        total_amount = sum(item["total"] for item in self.cart_items)
        method = self.payment_method_var.get()
        
        try:
            # Record each sale item
            for item in self.cart_items:
                self.cursor.execute("INSERT INTO sales (product_id, quantity, unit_price, total_price, payment_method) VALUES (?, ?, ?, ?, ?)",
                                  (item["product_id"], item["quantity"], item["price"], item["total"], method))
                
                # Update product stock
                self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", 
                                  (item["quantity"], item["product_id"]))
                
            self.conn.commit()
            
            # Print receipt
            if messagebox.askyesno("ሪሲት", "ሪሲት ልታተም?"):
                receipt_text = f"""
                ሬስቶራንት ሲስተም
                --------------------
                ቀን: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                --------------------
                """
                for item in self.cart_items:
                    receipt_text += f"{item['product_name']} x{item['quantity']}: {item['total']:.2f} ብር\n"
                
                receipt_text += f"""
                --------------------
                ጠቅላላ: {total_amount:.2f} ብር
                የክፍያ ዘዴ: {method}
                --------------------
                እናመሰግናለን!
                """
                print_receipt(receipt_text)
                
            messagebox.showinfo("ተሳክቷል", "ሽያጭ በትክክል �ተመዝግቧል")
            self.clear_cart()
            self.refresh_sales()
            
        except Exception as e:
            messagebox.showerror("ስህተት", f"ሽያጭ ማስቀመጥ አልተሳካም: {str(e)}")
            
    def refresh_sales(self):
        self.sales_tree.delete(*self.sales_tree.get_children())
        
        self.cursor.execute('''
            SELECT s.id, s.sale_date, p.name, s.quantity, s.unit_price, s.total_price, s.payment_method
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC LIMIT 50
        ''')
        
        for row in self.cursor.fetchall():
            date = str(row[1]).split('.')[0] if row[1] else ""
            self.sales_tree.insert("", "end", values=(row[0], date, row[2], row[3], f"{row[4]:.2f}", f"{row[5]:.2f}", row[6]))
            
        # Update product combo
        self.refresh_sales_products()  # ይህንን መስመር ይጨምሩ
        
    def show_sale_details(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ሽያጭ ይምረጡ")
            return
            
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        
        # Show sale details in a messagebox
        self.cursor.execute('''
            SELECT s.sale_date, p.name, s.quantity, s.unit_price, s.total_price, s.payment_method
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.id = ?
        ''', (sale_id,))
        
        result = self.cursor.fetchone()
        if result:
            date, product, qty, price, total, method = result
            date_str = str(date).split('.')[0] if date else ""
            
            details = f"""
            የሽያጭ ዝርዝር - ID: {sale_id}
            --------------------
            ቀን: {date_str}
            ምርት: {product}
            ብዛት: {qty}
            የአንድ ዋጋ: {price:.2f} ብር
            ጠቅላላ: {total:.2f} ብር
            የክፍያ ዘዴ: {method}
            """
            
            messagebox.showinfo("የሽያጭ ዝርዝር", details)
            
    def print_sale_receipt(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ሽያጭ ይምረጡ")
            return
            
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        
        self.cursor.execute('''
            SELECT s.sale_date, p.name, s.quantity, s.unit_price, s.total_price, s.payment_method
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.id = ?
        ''', (sale_id,))
        
        result = self.cursor.fetchone()
        if result:
            date, product, qty, price, total, method = result
            date_str = str(date).split('.')[0] if date else ""
            
            receipt_text = f"""
            ሬስቶራንት ሲስተም
            --------------------
            ሽያጭ ID: {sale_id}
            ቀን: {date_str}
            --------------------
            {product} x{qty}
            የአንድ ዋጋ: {price:.2f} ብር
            ጠቅላላ: {total:.2f} ብር
            የክፍያ ዘዴ: {method}
            --------------------
            እናመሰግናለን!
            """
            
            if print_receipt(receipt_text):
                messagebox.showinfo("ተሳክቷል", "ሪሲት ተታትሟል")
                
    def delete_sale(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ሽያጭ ይምረጡ")
            return
            
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        
        if messagebox.askyesno("አረጋግጥ", "እርግጠኛ �ነዎት ይህን ሽያጭ ለማስወገድ?"):
            try:
                # Get sale details to restore stock
                self.cursor.execute("SELECT product_id, quantity FROM sales WHERE id=?", (sale_id,))
                result = self.cursor.fetchone()
                
                if result:
                    product_id, quantity = result
                    # Restore stock
                    self.cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
                
                # Delete the sale
                self.cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ሽያጭ በትክክል ተሰርዟል")
                self.refresh_sales()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ሽያጭ ማስወገድ አልተሳካም: {str(e)}")


    # ---------------- Expenses Management ----------------
    def build_expense_tab(self):
        frm = self.expense_frame
        
        # Expense entry section
        entry_frame = ttk.LabelFrame(frm, text="አዲስ ወጪ", style="info.TLabelframe")
        entry_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Description
        ttk.Label(entry_frame, text="መግለጫ:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.exp_desc_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.exp_desc_var, width=30, style="primary.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Amount
        ttk.Label(entry_frame, text="መጠን:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.exp_amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.exp_amount_var, width=15, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Category
        ttk.Label(entry_frame, text="ምድብ:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.exp_category_var = tk.StringVar()
        categories = ["ምግብ እቃ", "ነዳጅ", "የሰራተኛ ክፍያ", "ጽዳት", "ሌሎች"]
        ttk.Combobox(entry_frame, textvariable=self.exp_category_var, values=categories, state="readonly", width=15, style="primary.TCombobox").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        
        # Add expense button
        ttk.Button(entry_frame, text="ወጪ ጨምር", command=self.add_expense, style="primary.TButton").grid(row=0, column=6, padx=10, pady=10)
        
        entry_frame.columnconfigure(1, weight=1)
        
        # Expenses list
        list_frame = ttk.LabelFrame(frm, text="ወጪዎች ዝርዝር", style="info.TLabelframe")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.expenses_tree = ttk.Treeview(list_frame, columns=("id", "date", "desc", "amount", "category"), show="headings", height=15, style="Treeview")
        for c, t, w in [("id","ID",50), ("date","ቀን",140), ("desc","መግለጫ",250), ("amount","መጠን",100), ("category","ምድብ",100)]:
            self.expenses_tree.heading(c, text=t)
            self.expenses_tree.column(c, width=w, anchor="w")
            
        scrollbar_exp = ttk.Scrollbar(list_frame, orient="vertical", command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar_exp.set)
        
        self.expenses_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_exp.pack(side="right", fill="y", pady=5)
        
        # Expense actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="ዝርዝር አሳይ", command=self.show_expense_details, style="primary.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ወጪ አስተካክል", command=self.edit_expense, style="warning.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ወጪ ሰርዝ", command=self.delete_expense, style="danger.TButton").pack(pady=5)
        
    def add_expense(self):
        description = self.exp_desc_var.get().strip()
        amount_str = self.exp_amount_var.get().strip()
        category = self.exp_category_var.get()
        
        if not description or not amount_str or not category:
            messagebox.showerror("ስህተት", "እባክዎ ሁሉንም መረጃዎች ያስገቡ")
            return
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("ስህተት", "የወጪ መጠን ከዜሮ በላይ መሆን አለበት")
                return
                
            self.cursor.execute("INSERT INTO expenses (description, amount, category, user_id) VALUES (?, ?, ?, ?)",
                              (description, amount, category, self.user["id"]))
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ወጪ በትክክል ተመዝግቧል")
            self.refresh_expenses()
            
            # Clear input fields
            self.exp_desc_var.set("")
            self.exp_amount_var.set("")
            self.exp_category_var.set("")
            
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ የወጪ መጠን ያስገቡ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ወጪ ማስገባት አልተሳካም: {str(e)}")
            
    def refresh_expenses(self):
        self.expenses_tree.delete(*self.expenses_tree.get_children())
        
        self.cursor.execute('''
            SELECT id, expense_date, description, amount, category
            FROM expenses
            ORDER BY expense_date DESC
        ''')
        
        for row in self.cursor.fetchall():
            date = str(row[1]).split('.')[0] if row[1] else ""
            self.expenses_tree.insert("", "end", values=(row[0], date, row[2], f"{row[3]:.2f}", row[4]))
            
    def show_expense_details(self):
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ወጪ ይምረጡ")
            return
            
        item = self.expenses_tree.item(selection[0])
        exp_id = item['values'][0]
        
        self.cursor.execute('''
            SELECT e.expense_date, e.description, e.amount, e.category, u.username
            FROM expenses e
            JOIN users u ON e.user_id = u.id
            WHERE e.id = ?
        ''', (exp_id,))
        
        result = self.cursor.fetchone()
        if result:
            date, desc, amount, category, user = result
            date_str = str(date).split('.')[0] if date else ""
            
            details = f"""
            የወጪ ዝርዝር - ID: {exp_id}
            --------------------
            ቀን: {date_str}
            መግለጫ: {desc}
            መጠን: {amount:.2f} ብር
            ምድብ: {category}
            ያስገባው: {user}
            """
            
            messagebox.showinfo("የወጪ ዝርዝር", details)
            
    def edit_expense(self):
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ወጪ ይምረጡ")
            return
            
        item = self.expenses_tree.item(selection[0])
        exp_id = item['values'][0]
        
        # Get current expense details
        self.cursor.execute("SELECT description, amount, category FROM expenses WHERE id=?", (exp_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("ስህተት", "ወጪ አልተገኘም")
            return
            
        desc, amount, category = result
        
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title("ወጪ አስተካክል")
        edit_win.geometry("400x300")
        
        ttk.Label(edit_win, text="ወጪ አስተካክል", style="Header.TLabel").pack(pady=10)
        
        # Description
        ttk.Label(edit_win, text="መግለጫ:", style="TLabel").pack(pady=5)
        desc_var = tk.StringVar(value=desc)
        ttk.Entry(edit_win, textvariable=desc_var, width=40, style="primary.TEntry").pack(pady=5)
        
        # Amount
        ttk.Label(edit_win, text="መጠን:", style="TLabel").pack(pady=5)
        amount_var = tk.StringVar(value=str(amount))
        ttk.Entry(edit_win, textvariable=amount_var, width=20, style="primary.TEntry").pack(pady=5)
        
        # Category
        ttk.Label(edit_win, text="ምድብ:", style="TLabel").pack(pady=5)
        category_var = tk.StringVar(value=category)
        categories = ["ምግብ እቃ", "ነዳጅ", "የሰራተኛ ክፍያ", "ጽዳት", "ሌሎች"]
        ttk.Combobox(edit_win, textvariable=category_var, values=categories, state="readonly", width=20, style="primary.TCombobox").pack(pady=5)
        
        def update_expense():
            new_desc = desc_var.get().strip()
            new_amount_str = amount_var.get().strip()
            new_category = category_var.get()
            
            if not new_desc or not new_amount_str or not new_category:
                messagebox.showerror("ስህተት", "እባክዎ ሁሉንም መረጃዎች ያስገቡ")
                return
                
            try:
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    messagebox.showerror("ስህተት", "የወጪ መጠን ከዜሮ በላይ መሆን አለበት")
                    return
                    
                self.cursor.execute("UPDATE expenses SET description=?, amount=?, category=? WHERE id=?",
                                  (new_desc, new_amount, new_category, exp_id))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ወጪ በትክክል ተስተካክሏል")
                edit_win.destroy()
                self.refresh_expenses()
                
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ የወጪ መጠን ያስገቡ")
            except Exception as e:
                messagebox.showerror("ስህተት", f"ወጪ ማሻሻል አልተሳካም: {str(e)}")
                
        ttk.Button(edit_win, text="አዘምን", command=update_expense, style="primary.TButton").pack(pady=20)
        
    def delete_expense(self):
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ወጪ ይምረጡ")
            return
            
        item = self.expenses_tree.item(selection[0])
        exp_id = item['values'][0]
        
        if messagebox.askyesno("አረጋግጥ", "እርግጠኛ ነዎት ይህን ወጪ ለማስወገድ?"):
            try:
                self.cursor.execute("DELETE FROM expenses WHERE id=?", (exp_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ወጪ በትክክል ተሰርዟል")
                self.refresh_expenses()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ወጪ ማስወገድ አልተሳካም: {str(e)}")

    # ---------------- Credit/Debit Management ----------------
    def build_credit_tab(self):
        frm = self.credit_frame
        
        # Credit entry section
        entry_frame = ttk.LabelFrame(frm, text="አዲስ ክሬዲት/ዴቢት", style="info.TLabelframe")
        entry_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Customer name
        ttk.Label(entry_frame, text="የደንበኛ ስም:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.credit_customer_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.credit_customer_var, width=30, style="primary.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Amount
        ttk.Label(entry_frame, text="መጠን:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.credit_amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.credit_amount_var, width=15, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Due date
        ttk.Label(entry_frame, text="የመጨረሻ ቀን:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.credit_due_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.credit_due_var, width=15, style="primary.TEntry").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        ttk.Label(entry_frame, text="(YYYY-MM-DD)", style="TLabel").grid(row=0, column=6, padx=5, pady=10, sticky="w")
        
        # Add credit button
        ttk.Button(entry_frame, text="ክሬዲት ጨምር", command=self.add_credit, style="primary.TButton").grid(row=0, column=7, padx=10, pady=10)
        
        entry_frame.columnconfigure(1, weight=1)
        
        # Credits list
        list_frame = ttk.LabelFrame(frm, text="ክሬዲት/ዴቢት ዝርዝር", style="info.TLabelframe")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.credits_tree = ttk.Treeview(list_frame, columns=("id", "customer", "amount", "paid", "balance", "status", "due"), show="headings", height=15, style="Treeview")
        for c, t, w in [("id","ID",50), ("customer","ደንበኛ",150), ("amount","መጠን",100), ("paid","የተከፈለ",100), ("balance","ቀሪ",100), ("status","ሁኔታ",100), ("due","የመጨረሻ ቀን",100)]:
            self.credits_tree.heading(c, text=t)
            self.credits_tree.column(c, width=w, anchor="w")
            
        scrollbar_cred = ttk.Scrollbar(list_frame, orient="vertical", command=self.credits_tree.yview)
        self.credits_tree.configure(yscrollcommand=scrollbar_cred.set)
        
        self.credits_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_cred.pack(side="right", fill="y", pady=5)
        
        # Credit actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="ዝርዝር አሳይ", command=self.show_credit_details, style="primary.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ክፍያ አስገባ", command=self.add_credit_payment, style="success.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ክሬዲት አስተካክል", command=self.edit_credit, style="warning.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ክሬዲት ሰርዝ", command=self.delete_credit, style="danger.TButton").pack(pady=5)
        
    def add_credit(self):
        customer = self.credit_customer_var.get().strip()
        amount_str = self.credit_amount_var.get().strip()
        due_date = self.credit_due_var.get().strip()
        
        if not customer or not amount_str:
            messagebox.showerror("ስህተት", "እባክዎ የደንበኛ ስም እና መጠን ያስገቡ")
            return
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("ስህተት", "የክሬዲት መጠን ከዜሮ በላይ መሆን አለበት")
                return
                
            # Validate due date if provided
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("ስህተት", "የቀን ቅርጸት YYYY-MM-DD መሆን አለበት")
                    return
                    
            self.cursor.execute("INSERT INTO credits (customer_name, amount, due_date) VALUES (?, ?, ?)",
                              (customer, amount, due_date or None))
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ክሬዲት በትክክል ተመዝግቧል")
            self.refresh_credits()
            
            # Clear input fields
            self.credit_customer_var.set("")
            self.credit_amount_var.set("")
            self.credit_due_var.set("")
            
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ የክሬዲት መጠን ያስገቡ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ክሬዲት ማስገባት አልተሳካም: {str(e)}")
            
    def refresh_credits(self):
        self.credits_tree.delete(*self.credits_tree.get_children())
        
        self.cursor.execute('''
            SELECT id, customer_name, amount, paid_amount, 
                   (amount - paid_amount) as balance,
                   status, due_date
            FROM credits
            ORDER BY created_at DESC
        ''')
        
        for row in self.cursor.fetchall():
            due_date = row[6] or "የለም"
            self.credits_tree.insert("", "end", values=(
                row[0], row[1], f"{row[2]:.2f}", f"{row[3]:.2f}", 
                f"{row[4]:.2f}", row[5], due_date
            ))
            
    def show_credit_details(self):
        selection = self.credits_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክሬዲት ይምረጡ")
            return
            
        item = self.credits_tree.item(selection[0])
        credit_id = item['values'][0]
        
        self.cursor.execute('''
            SELECT c.customer_name, c.amount, c.paid_amount, 
                   (c.amount - c.paid_amount) as balance,
                   c.status, c.due_date, c.created_at
            FROM credits c
            WHERE c.id = ?
        ''', (credit_id,))
        
        result = self.cursor.fetchone()
        if result:
            customer, amount, paid, balance, status, due_date, created = result
            due_date = due_date or "የለም"
            created = str(created).split('.')[0] if created else ""
            
            details = f"""
            የክሬዲት ዝርዝር - ID: {credit_id}
            --------------------
            ደንበኛ: {customer}
            መጠን: {amount:.2f} ብር
            የተከፈለ: {paid:.2f} ብር
            ቀሪ: {balance:.2f} ብር
            ሁኔታ: {status}
            የመጨረሻ ቀን: {due_date}
            የተፈጠረበት: {created}
            """
            
            messagebox.showinfo("የክሬዲት ዝርዝር", details)
            
    def add_credit_payment(self):
        selection = self.credits_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክሬዲት ይምረጡ")
            return
            
        item = self.credits_tree.item(selection[0])
        credit_id = item['values'][0]
        customer = item['values'][1]
        balance = float(item['values'][4])
        
        if balance <= 0:
            messagebox.showinfo("መረጃ", "ይህ ክሬዲት ቀድሞውኑ ተከፍሏል")
            return
            
        # Create payment window
        pay_win = tk.Toplevel(self.root)
        pay_win.title("ክፍያ አስገባ")
        pay_win.geometry("300x200")
        
        ttk.Label(pay_win, text=f"ክፍያ ለ {customer}", style="Header.TLabel").pack(pady=10)
        ttk.Label(pay_win, text=f"ቀሪ መጠን: {balance:.2f} ብር", style="TLabel").pack(pady=5)
        
        ttk.Label(pay_win, text="የክፍያ መጠን:", style="TLabel").pack(pady=5)
        amount_var = tk.StringVar(value=f"{balance:.2f}")
        ttk.Entry(pay_win, textvariable=amount_var, width=15, style="primary.TEntry").pack(pady=5)
        
        def process_payment():
            try:
                payment_amount = float(amount_var.get())
                if payment_amount <= 0:
                    messagebox.showerror("ስህተት", "የክፍያ መጠን ከዜሮ በላይ መሆን አለበት")
                    return
                    
                if payment_amount > balance:
                    messagebox.showerror("ስህተት", "የክፍያ መጠን ከቀሪ መጠን መብለጥ አይችልም")
                    return
                    
                # Record payment
                self.cursor.execute("INSERT INTO credit_payments (credit_id, amount) VALUES (?, ?)",
                                  (credit_id, payment_amount))
                
                # Update credit record
                self.cursor.execute("UPDATE credits SET paid_amount = paid_amount + ? WHERE id = ?",
                                  (payment_amount, credit_id))
                
                # Update status
                self.cursor.execute('''
                    UPDATE credits SET status = 
                    CASE 
                        WHEN paid_amount >= amount THEN 'paid'
                        WHEN paid_amount > 0 THEN 'partial'
                        ELSE 'pending'
                    END
                    WHERE id = ?
                ''', (credit_id,))
                
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ክፍያ በትክክል ተመዝግቧል")
                pay_win.destroy()
                self.refresh_credits()
                
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥር ያስገቡ")
            except Exception as e:
                messagebox.showerror("ስህተት", f"ክፍያ ማስገባት አልተሳካም: {str(e)}")
                
        ttk.Button(pay_win, text="ክፍያ አስገባ", command=process_payment, style="success.TButton").pack(pady=20)
        
    def edit_credit(self):
        selection = self.credits_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክሬዲት ይምረጡ")
            return
            
        item = self.credits_tree.item(selection[0])
        credit_id = item['values'][0]
        
        # Get current credit details
        self.cursor.execute("SELECT customer_name, amount, due_date FROM credits WHERE id=?", (credit_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("ስህተት", "ክሬዲት አልተገኘም")
            return
            
        customer, amount, due_date = result
        
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title("ክሬዲት አስተካክል")
        edit_win.geometry("400x300")
        
        ttk.Label(edit_win, text="ክሬዲት አስተካክል", style="Header.TLabel").pack(pady=10)
        
        # Customer name
        ttk.Label(edit_win, text="የደንበኛ ስም:", style="TLabel").pack(pady=5)
        customer_var = tk.StringVar(value=customer)
        ttk.Entry(edit_win, textvariable=customer_var, width=30, style="primary.TEntry").pack(pady=5)
        
        # Amount
        ttk.Label(edit_win, text="መጠን:", style="TLabel").pack(pady=5)
        amount_var = tk.StringVar(value=str(amount))
        ttk.Entry(edit_win, textvariable=amount_var, width=15, style="primary.TEntry").pack(pady=5)
        
        # Due date
        ttk.Label(edit_win, text="የመጨረሻ ቀን:", style="TLabel").pack(pady=5)
        due_var = tk.StringVar(value=due_date or "")
        ttk.Entry(edit_win, textvariable=due_var, width=15, style="primary.TEntry").pack(pady=5)
        ttk.Label(edit_win, text="(YYYY-MM-DD)", style="TLabel").pack()
        
        def update_credit():
            new_customer = customer_var.get().strip()
            new_amount_str = amount_var.get().strip()
            new_due_date = due_var.get().strip()
            
            if not new_customer or not new_amount_str:
                messagebox.showerror("ስህተት", "እባክዎ የደንበኛ ስም እና መጠን ያስገቡ")
                return
                
            try:
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    messagebox.showerror("ስህተት", "የክሬዲት መጠን ከዜሮ በላይ መሆን አለበት")
                    return
                    
                # Validate due date if provided
                if new_due_date:
                    try:
                        datetime.strptime(new_due_date, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("ስህተት", "የቀን ቅርጸት YYYY-MM-DD መሆን አለበት")
                        return
                        
                self.cursor.execute("UPDATE credits SET customer_name=?, amount=?, due_date=? WHERE id=?",
                                  (new_customer, new_amount, new_due_date or None, credit_id))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ክሬዲት በትክክል ተስተካክሏል")
                edit_win.destroy()
                self.refresh_credits()
                
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ የክሬዲት መጠን ያስገቡ")
            except Exception as e:
                messagebox.showerror("ስህተት", f"ክሬዲት ማሻሻል አልተሳካም: {str(e)}")
                
        ttk.Button(edit_win, text="አዘምን", command=update_credit, style="primary.TButton").pack(pady=20)
        
    def delete_credit(self):
        selection = self.credits_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክሬዲት ይምረጡ")
            return
            
        item = self.credits_tree.item(selection[0])
        credit_id = item['values'][0]
        
        if messagebox.askyesno("አረጋግጥ", "እርግጠኛ ነዎት ይህን ክሬዲት ለማስወገድ?"):
            try:
                # Check if there are payments
                self.cursor.execute("SELECT COUNT(*) FROM credit_payments WHERE credit_id=?", (credit_id,))
                payment_count = self.cursor.fetchone()[0]
                
                if payment_count > 0:
                    if not messagebox.askyesno("ማስጠንቀቂያ", "ይህ ክሬዲት ክፍያዎች አሉት። ሁሉንም የክፍያ ዝርዝሮች ይሰርዛሉ?"):
                        return
                        
                    # Delete payments first
                    self.cursor.execute("DELETE FROM credit_payments WHERE credit_id=?", (credit_id,))
                
                # Delete the credit
                self.cursor.execute("DELETE FROM credits WHERE id=?", (credit_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ክሬዲት በትክክል ተሰርዟል")
                self.refresh_credits()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ክሬዲት ማስወገድ አልተሳካም: {str(e)}")

    # ---------------- Staff/Waiter Management ----------------
    def build_staff_tab(self):
        frm = self.staff_frame
        
        # Staff performance section
        perf_frame = ttk.LabelFrame(frm, text="የአገልጋይ አፈጻጸም", style="info.TLabelframe")
        perf_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Date range selection
        date_frame = ttk.Frame(perf_frame)
        date_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(date_frame, text="ከ:", style="TLabel").pack(side="left", padx=5)
        self.staff_start_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.staff_start_var, width=12, style="primary.TEntry").pack(side="left", padx=5)
        
        ttk.Label(date_frame, text="እስከ:", style="TLabel").pack(side="left", padx=5)
        self.staff_end_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.staff_end_var, width=12, style="primary.TEntry").pack(side="left", padx=5)
        
        ttk.Button(date_frame, text="አሳይ", command=self.refresh_staff_performance, style="primary.TButton").pack(side="left", padx=10)
        
        # Staff performance tree
        self.staff_tree = ttk.Treeview(perf_frame, columns=("staff", "orders", "sales", "tips"), show="headings", height=8, style="Treeview")
        for c, t, w in [("staff","አገልጋይ",150), ("orders","ኦርደሮች",100), ("sales","ሽያጭ",100), ("tips","ቲፖች",100)]:
            self.staff_tree.heading(c, text=t)
            self.staff_tree.column(c, width=w, anchor="w")
            
        scrollbar_staff = ttk.Scrollbar(perf_frame, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=scrollbar_staff.set)
        
        self.staff_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_staff.pack(side="right", fill="y", pady=5)
        
        # Staff details section
        detail_frame = ttk.LabelFrame(frm, text="የአገልጋይ ዝርዝር", style="info.TLabelframe")
        detail_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Orders by selected staff
        self.staff_orders_tree = ttk.Treeview(detail_frame, columns=("id", "date", "table", "status", "total"), show="headings", height=10, style="Treeview")
        for c, t, w in [("id","ID",50), ("date","ቀን",140), ("table","ሰንጠረዥ",80), ("status","ሁኔታ",100), ("total","ጠቅላላ",100)]:
            self.staff_orders_tree.heading(c, text=t)
            self.staff_orders_tree.column(c, width=w, anchor="w")
            
        scrollbar_orders = ttk.Scrollbar(detail_frame, orient="vertical", command=self.staff_orders_tree.yview)
        self.staff_orders_tree.configure(yscrollcommand=scrollbar_orders.set)
        
        self.staff_orders_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_orders.pack(side="right", fill="y", pady=5)
        
        # Tip management
        tip_frame = ttk.Frame(detail_frame)
        tip_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Label(tip_frame, text="ቲፕ አስገባ", style="TLabel").pack(pady=5)
        
        ttk.Label(tip_frame, text="ኦርደር ID:", style="TLabel").pack(pady=2)
        self.tip_order_var = tk.StringVar()
        ttk.Entry(tip_frame, textvariable=self.tip_order_var, width=10, style="primary.TEntry").pack(pady=2)
        
        ttk.Label(tip_frame, text="ቲፕ መጠን:", style="TLabel").pack(pady=2)
        self.tip_amount_var = tk.StringVar()
        ttk.Entry(tip_frame, textvariable=self.tip_amount_var, width=10, style="primary.TEntry").pack(pady=2)
        
        ttk.Button(tip_frame, text="ቲፕ ጨምር", command=self.add_tip, style="success.TButton").pack(pady=10)
        
        # Bind selection event
        self.staff_tree.bind("<<TreeviewSelect>>", self.on_staff_select)
        
    def refresh_staff_performance(self):
        start_date = self.staff_start_var.get()
        end_date = self.staff_end_var.get()
        
        # Validate dates
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቀን ያስገቡ (YYYY-MM-DD)")
            return
            
        self.staff_tree.delete(*self.staff_tree.get_children())
        
        # Get staff performance data
        self.cursor.execute('''
            SELECT u.id, u.username, 
                   COUNT(o.id) as order_count,
                   COALESCE(SUM(o.total_amount), 0) as total_sales,
                   COALESCE(SUM(t.amount), 0) as total_tips
            FROM users u
            LEFT JOIN orders o ON u.id = o.waiter_id AND DATE(o.created_at) BETWEEN ? AND ?
            LEFT JOIN tips t ON u.id = t.waiter_id AND DATE(t.tip_date) BETWEEN ? AND ?
            WHERE u.role = 'waiter'
            GROUP BY u.id, u.username
            ORDER BY total_sales DESC
        ''', (start_date, end_date, start_date, end_date))
        
        for row in self.cursor.fetchall():
            self.staff_tree.insert("", "end", values=(row[1], row[2], f"{row[3]:.2f}", f"{row[4]:.2f}"), tags=(row[0],))
            
    def on_staff_select(self, event):
        selection = self.staff_tree.selection()
        if not selection:
            return
            
        item = self.staff_tree.item(selection[0])
        staff_id = item['tags'][0] if item['tags'] else None
        
        if not staff_id:
            return
            
        # Get orders for this staff member
        self.staff_orders_tree.delete(*self.staff_orders_tree.get_children())
        
        start_date = self.staff_start_var.get()
        end_date = self.staff_end_var.get()
        
        self.cursor.execute('''
            SELECT id, created_at, table_number, status, total_amount
            FROM orders
            WHERE waiter_id = ? AND DATE(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
        ''', (staff_id, start_date, end_date))
        
        for row in self.cursor.fetchall():
            date = str(row[1]).split('.')[0] if row[1] else ""
            self.staff_orders_tree.insert("", "end", values=(row[0], date, row[2], row[3], f"{row[4]:.2f}"))
            
    def add_tip(self):
        order_id_str = self.tip_order_var.get().strip()
        amount_str = self.tip_amount_var.get().strip()
        
        if not order_id_str or not amount_str:
            messagebox.showerror("ስህተት", "እባክዎ ኦርደር ID እና ቲፕ መጠን ያስገቡ")
            return
            
        try:
            order_id = int(order_id_str)
            amount = float(amount_str)
            
            if amount <= 0:
                messagebox.showerror("ስህተት", "ቲፕ መጠን ከዜሮ በላይ መሆን አለበት")
                return
                
            # Get waiter ID from the order
            self.cursor.execute("SELECT waiter_id FROM orders WHERE id=?", (order_id,))
            result = self.cursor.fetchone()
            
            if not result:
                messagebox.showerror("ስህተት", "ኦርደር አልተገኘም")
                return
                
            waiter_id = result[0]
            
            # Add tip
            self.cursor.execute("INSERT INTO tips (waiter_id, order_id, amount) VALUES (?, ?, ?)",
                              (waiter_id, order_id, amount))
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ቲፕ በትክክል ተመዝግቧል")
            self.tip_order_var.set("")
            self.tip_amount_var.set("")
            self.refresh_staff_performance()
            
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥሮች ያስገቡ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ቲፕ ማስገባት አልተሳካም: {str(e)}")

    # ---------------- Inventory Management ----------------
    def build_inventory_tab(self):
        frm = self.inventory_frame
        
        # Inventory entry section
        entry_frame = ttk.LabelFrame(frm, text="አዲስ የገቢ እቃ", style="info.TLabelframe")
        entry_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Product selection
        ttk.Label(entry_frame, text="ምርት:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.inv_product_var = tk.StringVar()
        self.inv_product_combo = ttk.Combobox(entry_frame, textvariable=self.inv_product_var, state="readonly", width=20, style="primary.TCombobox")
        self.inv_product_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Quantity
        ttk.Label(entry_frame, text="ብዛት:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.inv_qty_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.inv_qty_var, width=10, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Unit
        ttk.Label(entry_frame, text="አሃድ:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.inv_unit_var = tk.StringVar(value="pcs")
        units = ["pcs", "kg", "g", "l", "ml", "box"]
        ttk.Combobox(entry_frame, textvariable=self.inv_unit_var, values=units, state="readonly", width=10, style="primary.TCombobox").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        
        # Cost
        ttk.Label(entry_frame, text="ዋጋ:", style="TLabel").grid(row=0, column=6, padx=10, pady=10, sticky="w")
        self.inv_cost_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.inv_cost_var, width=10, style="primary.TEntry").grid(row=0, column=7, padx=10, pady=10, sticky="w")
        
        # Add inventory button
        ttk.Button(entry_frame, text="ክምችት ጨምር", command=self.add_inventory, style="primary.TButton").grid(row=0, column=8, padx=10, pady=10)
        
        entry_frame.columnconfigure(1, weight=1)
        
        # Inventory list
        list_frame = ttk.LabelFrame(frm, text="የክምችት ዝርዝር", style="info.TLabelframe")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.inventory_tree = ttk.Treeview(list_frame, columns=("id", "product", "qty", "unit", "cost", "date"), show="headings", height=15, style="Treeview")
        for c, t, w in [("id","ID",50), ("product","ምርት",200), ("qty","ብዛት",80), ("unit","አሃድ",80), ("cost","ዋጋ",100), ("date","ቀን",120)]:
            self.inventory_tree.heading(c, text=t)
            self.inventory_tree.column(c, width=w, anchor="w")
            
        scrollbar_inv = ttk.Scrollbar(list_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar_inv.set)
        
        self.inventory_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_inv.pack(side="right", fill="y", pady=5)
        
        # Inventory actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="ዝርዝር አሳይ", command=self.show_inventory_details, style="primary.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ክምችት አስተካክል", command=self.edit_inventory, style="warning.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ክምችት ሰርዝ", command=self.delete_inventory, style="danger.TButton").pack(pady=5)
        
    def add_inventory(self):
        product_name = self.inv_product_var.get()
        qty_str = self.inv_qty_var.get().strip()
        unit = self.inv_unit_var.get()
        cost_str = self.inv_cost_var.get().strip()
        
        if not product_name or not qty_str or not cost_str:
            messagebox.showerror("ስህተት", "እባክዎ ሁሉንም መረጃዎች ያስገቡ")
            return
            
        try:
            qty = float(qty_str)
            cost = float(cost_str)
            
            if qty <= 0 or cost <= 0:
                messagebox.showerror("ስህተት", "ብዛት እና ዋጋ ከዜሮ በላይ መሆን አለበት")
                return
                
            # Get product ID
            self.cursor.execute("SELECT id FROM products WHERE name=?", (product_name,))
            result = self.cursor.fetchone()
            
            if not result:
                messagebox.showerror("ስህተት", "ምርት አልተገኘም")
                return
                
            product_id = result[0]
            
            # Add inventory
            self.cursor.execute("INSERT INTO inventory (product_id, quantity, unit, cost) VALUES (?, ?, ?, ?)",
                              (product_id, qty, unit, cost))
            
            # Update product stock
            self.cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, product_id))
            
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ክምችት በትክክል ተመዝግቧል")
            self.refresh_inventory()
            
            # Clear input fields
            self.inv_product_var.set("")
            self.inv_qty_var.set("")
            self.inv_cost_var.set("")
            
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥሮች ያስገቡ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ክምችት ማስገባት አልተሳካም: {str(e)}")
            
    def refresh_inventory(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        
        self.cursor.execute('''
            SELECT i.id, p.name, i.quantity, i.unit, i.cost, i.received_date
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY i.received_date DESC
        ''')
        
        for row in self.cursor.fetchall():
            date = str(row[5]).split('.')[0] if row[5] else ""
            self.inventory_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], f"{row[4]:.2f}", date))
            
        # Update product combo
        self.inv_product_combo['values'] = self.get_product_names()
        
    def show_inventory_details(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክምችት ይምረጡ")
            return
            
        item = self.inventory_tree.item(selection[0])
        inv_id = item['values'][0]
        
        self.cursor.execute('''
            SELECT p.name, i.quantity, i.unit, i.cost, i.received_date
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.id = ?
        ''', (inv_id,))
        
        result = self.cursor.fetchone()
        if result:
            product, qty, unit, cost, date = result
            date_str = str(date).split('.')[0] if date else ""
            
            details = f"""
            የክምችት ዝርዝር - ID: {inv_id}
            --------------------
            ምርት: {product}
            ብዛት: {qty} {unit}
            ዋጋ: {cost:.2f} ብር
            የተቀበለው: {date_str}
            አጠቃላይ ዋጋ: {qty * cost:.2f} ብር
            """
            
            messagebox.showinfo("የክምችት ዝርዝር", details)
            
    def edit_inventory(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክምችት ይምረጡ")
            return
            
        item = self.inventory_tree.item(selection[0])
        inv_id = item['values'][0]
        current_qty = float(item['values'][2])
        
        # Get current inventory details
        self.cursor.execute('''
            SELECT i.product_id, i.quantity, i.unit, i.cost, p.name
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.id = ?
        ''', (inv_id,))
        
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("ስህተት", "ክምችት አልተገኘም")
            return
            
        product_id, qty, unit, cost, product_name = result
        
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title("ክምችት አስተካክል")
        edit_win.geometry("400x300")
        
        ttk.Label(edit_win, text="ክምችት አስተካክል", style="Header.TLabel").pack(pady=10)
        
        # Product (read-only)
        ttk.Label(edit_win, text="ምርት:", style="TLabel").pack(pady=5)
        ttk.Label(edit_win, text=product_name, style="TLabel").pack(pady=5)
        
        # Quantity
        ttk.Label(edit_win, text="ብዛት:", style="TLabel").pack(pady=5)
        qty_var = tk.StringVar(value=str(qty))
        ttk.Entry(edit_win, textvariable=qty_var, width=10, style="primary.TEntry").pack(pady=5)
        
        # Unit
        ttk.Label(edit_win, text="አሃድ:", style="TLabel").pack(pady=5)
        unit_var = tk.StringVar(value=unit)
        units = ["pcs", "kg", "g", "l", "ml", "box"]
        ttk.Combobox(edit_win, textvariable=unit_var, values=units, state="readonly", width=10, style="primary.TCombobox").pack(pady=5)
        
        # Cost
        ttk.Label(edit_win, text="ዋጋ:", style="TLabel").pack(pady=5)
        cost_var = tk.StringVar(value=str(cost))
        ttk.Entry(edit_win, textvariable=cost_var, width=10, style="primary.TEntry").pack(pady=5)
        
        def update_inventory():
            new_qty_str = qty_var.get().strip()
            new_unit = unit_var.get()
            new_cost_str = cost_var.get().strip()
            
            if not new_qty_str or not new_cost_str:
                messagebox.showerror("ስህተት", "እባክዎ ሁሉንም መረጃዎች ያስገቡ")
                return
                
            try:
                new_qty = float(new_qty_str)
                new_cost = float(new_cost_str)
                
                if new_qty <= 0 or new_cost <= 0:
                    messagebox.showerror("ስህተት", "ብዛት እና ዋጋ ከዜሮ በላይ መሆን አለበት")
                    return
                    
                # Calculate stock difference
                qty_diff = new_qty - current_qty
                
                # Update inventory
                self.cursor.execute("UPDATE inventory SET quantity=?, unit=?, cost=? WHERE id=?",
                                  (new_qty, new_unit, new_cost, inv_id))
                
                # Update product stock
                self.cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty_diff, product_id))
                
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ክምችት በትክክል ተስተካክሏል")
                edit_win.destroy()
                self.refresh_inventory()
                
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥሮች ያስገቡ")
            except Exception as e:
                messagebox.showerror("ስህተት", f"ክምችት ማሻሻል አልተሳካም: {str(e)}")
                
        ttk.Button(edit_win, text="አዘምን", command=update_inventory, style="primary.TButton").pack(pady=20)
        
    def delete_inventory(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ክምችት ይምረጡ")
            return
            
        item = self.inventory_tree.item(selection[0])
        inv_id = item['values'][0]
        current_qty = float(item['values'][2])
        product_name = item['values'][1]
        
        if messagebox.askyesno("አረጋግጥ", f"እርግጠኛ ነዎት ይህን ክምችት ለማስወገድ? ({product_name})"):
            try:
                # Get product ID
                self.cursor.execute("SELECT product_id FROM inventory WHERE id=?", (inv_id,))
                result = self.cursor.fetchone()
                
                if result:
                    product_id = result[0]
                    # Update product stock
                    self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (current_qty, product_id))
                
                # Delete the inventory
                self.cursor.execute("DELETE FROM inventory WHERE id=?", (inv_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ክምችት በትክክል ተሰርዟል")
                self.refresh_inventory()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ክምችት ማስወገድ አልተሳካም: {str(e)}")

    # ---------------- Products Management ----------------
    def build_products_tab(self):
        frm = self.products_frame
        
        # Product entry section
        entry_frame = ttk.LabelFrame(frm, text="አዲስ ምርት", style="info.TLabelframe")
        entry_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Name
        ttk.Label(entry_frame, text="ስም:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.prod_name_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.prod_name_var, width=20, style="primary.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Price
        ttk.Label(entry_frame, text="ዋጋ:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.prod_price_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.prod_price_var, width=10, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Category
        ttk.Label(entry_frame, text="ምድብ:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.prod_category_var = tk.StringVar()
        categories = ["ምግብ", "መጠጥ", "ሌላ"]
        ttk.Combobox(entry_frame, textvariable=self.prod_category_var, values=categories, state="readonly", width=10, style="primary.TCombobox").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        
        # Stock
        ttk.Label(entry_frame, text="ክምችት:", style="TLabel").grid(row=0, column=6, padx=10, pady=10, sticky="w")
        self.prod_stock_var = tk.StringVar(value="0")
        ttk.Entry(entry_frame, textvariable=self.prod_stock_var, width=10, style="primary.TEntry").grid(row=0, column=7, padx=10, pady=10, sticky="w")
        
        # Add product button
        ttk.Button(entry_frame, text="ምርት ጨምር", command=self.add_product, style="primary.TButton").grid(row=0, column=8, padx=10, pady=10)
        
        entry_frame.columnconfigure(1, weight=1)
        
        # Products list
        list_frame = ttk.LabelFrame(frm, text="ምርቶች ዝርዝር", style="info.TLabelframe")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.products_tree = ttk.Treeview(list_frame, columns=("id", "name", "price", "category", "stock"), show="headings", height=15, style="Treeview")
        for c, t, w in [("id","ID",50), ("name","ስም",200), ("price","ዋጋ",100), ("category","ምድብ",100), ("stock","ክምችት",80)]:
            self.products_tree.heading(c, text=t)
            self.products_tree.column(c, width=w, anchor="w")
            
        scrollbar_prod = ttk.Scrollbar(list_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar_prod.set)
        
        self.products_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_prod.pack(side="right", fill="y", pady=5)
        
        # Product actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="ዝርዝር አሳይ", command=self.show_product_details, style="primary.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ምርት አስተካክል", command=self.edit_product, style="warning.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ምርት ሰርዝ", command=self.delete_product, style="danger.TButton").pack(pady=5)
        
    def add_product(self):
        name = self.prod_name_var.get().strip()
        price_str = self.prod_price_var.get().strip()
        category = self.prod_category_var.get()
        stock_str = self.prod_stock_var.get().strip()
        
        if not name or not price_str or not category:
            messagebox.showerror("ስህተት", "እባክዎ ስም፣ ዋጋ እና ምድብ ያስገቡ")
            return
            
        try:
            price = float(price_str)
            stock = int(stock_str) if stock_str else 0
            
            if price <= 0:
                messagebox.showerror("ስህተት", "ዋጋ ከዜሮ በላይ መሆን አለበት")
                return
                
            if stock < 0:
                messagebox.showerror("ስህተት", "ክምችት ከዜሮ በታች መሆን አይችልም")
                return
                
            self.cursor.execute("INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)",
                              (name, price, category, stock))
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ምርት በትክክል ተመዝግቧል")
            self.refresh_products()
            
            # Clear input fields
            self.prod_name_var.set("")
            self.prod_price_var.set("")
            self.prod_category_var.set("")
            self.prod_stock_var.set("0")
            
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥሮች ያስገቡ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ምርት ማስገባት አልተሳካም: {str(e)}")
            
    def refresh_products(self):
        self.products_tree.delete(*self.products_tree.get_children())
        
        self.cursor.execute('SELECT id, name, price, category, stock FROM products ORDER BY name')
        
        for row in self.cursor.fetchall():
            self.products_tree.insert("", "end", values=(row[0], row[1], f"{row[2]:.2f}", row[3], row[4]))
            
    def show_product_details(self):
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ምርት ይምረጡ")
            return
            
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        
        self.cursor.execute('SELECT name, price, category, stock FROM products WHERE id=?', (product_id,))
        
        result = self.cursor.fetchone()
        if result:
            name, price, category, stock = result
            
            details = f"""
            የምርት ዝርዝር - ID: {product_id}
            --------------------
            ስም: {name}
            ዋጋ: {price:.2f} ብር
            ምድብ: {category}
            ክምችት: {stock}
            """
            
            messagebox.showinfo("የምርት ዝርዝር", details)
            
    def edit_product(self):
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ምርት ይምረጡ")
            return
            
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Get current product details
        self.cursor.execute("SELECT name, price, category, stock FROM products WHERE id=?", (product_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("ስህተት", "ምርት አልተገኘም")
            return
            
        name, price, category, stock = result
        
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title("ምርት አስተካክል")
        edit_win.geometry("400x300")
        
        ttk.Label(edit_win, text="ምርት አስተካክል", style="Header.TLabel").pack(pady=10)
        
        # Name
        ttk.Label(edit_win, text="ስም:", style="TLabel").pack(pady=5)
        name_var = tk.StringVar(value=name)
        ttk.Entry(edit_win, textvariable=name_var, width=30, style="primary.TEntry").pack(pady=5)
        
        # Price
        ttk.Label(edit_win, text="ዋጋ:", style="TLabel").pack(pady=5)
        price_var = tk.StringVar(value=str(price))
        ttk.Entry(edit_win, textvariable=price_var, width=15, style="primary.TEntry").pack(pady=5)
        
        # Category
        ttk.Label(edit_win, text="ምድብ:", style="TLabel").pack(pady=5)
        category_var = tk.StringVar(value=category)
        categories = ["ምግብ", "መጠጥ", "ሌላ"]
        ttk.Combobox(edit_win, textvariable=category_var, values=categories, state="readonly", width=15, style="primary.TCombobox").pack(pady=5)
        
        # Stock
        ttk.Label(edit_win, text="ክምችት:", style="TLabel").pack(pady=5)
        stock_var = tk.StringVar(value=str(stock))
        ttk.Entry(edit_win, textvariable=stock_var, width=10, style="primary.TEntry").pack(pady=5)
        
        def update_product():
            new_name = name_var.get().strip()
            new_price_str = price_var.get().strip()
            new_category = category_var.get()
            new_stock_str = stock_var.get().strip()
            
            if not new_name or not new_price_str or not new_category:
                messagebox.showerror("ስህተት", "እባክዎ ስም፣ ዋጋ እና ምድብ ያስገቡ")
                return
                
            try:
                new_price = float(new_price_str)
                new_stock = int(new_stock_str) if new_stock_str else 0
                
                if new_price <= 0:
                    messagebox.showerror("ስህተት", "ዋጋ ከዜሮ በላይ መሆን አለበት")
                    return
                    
                if new_stock < 0:
                    messagebox.showerror("ስህተት", "ክምችት ከዜሮ በታች መሆን አይችልም")
                    return
                    
                self.cursor.execute("UPDATE products SET name=?, price=?, category=?, stock=? WHERE id=?",
                                  (new_name, new_price, new_category, new_stock, product_id))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ምርት በትክክል ተስተካክሏል")
                edit_win.destroy()
                self.refresh_products()
                
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥሮች ያስገቡ")
            except Exception as e:
                messagebox.showerror("ስህተት", f"ምርት ማሻሻል አልተሳካም: {str(e)}")
                
        ttk.Button(edit_win, text="አዘምን", command=update_product, style="primary.TButton").pack(pady=20)
        
    def delete_product(self):
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ምርት ይምረጡ")
            return
            
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("አረጋግጥ", f"እርግጠኛ ነዎት ይህን ምርት ለማስወገድ? ({product_name})"):
            try:
                # Check if product has sales or orders
                self.cursor.execute("SELECT COUNT(*) FROM sales WHERE product_id=?", (product_id,))
                sales_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM order_items WHERE product_id=?", (product_id,))
                orders_count = self.cursor.fetchone()[0]
                
                if sales_count > 0 or orders_count > 0:
                    messagebox.showerror("ስህተት", "ይህ ምርት በሽያጭ ወይም በኦርደር ውስጥ አለ። ሊሰረዝ አይችልም።")
                    return
                    
                # Delete the product
                self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ምርት በትክክል ተሰርዟል")
                self.refresh_products()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ምርት ማስወገድ አልተሳካም: {str(e)}")

    # ---------------- Reports ----------------
    def build_reports_tab(self):
        frm = self.reports_frame
        
        # Report controls
        control_frame = ttk.LabelFrame(frm, text="ሪፖርት ማውጫ", style="info.TLabelframe")
        control_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Report type
        ttk.Label(control_frame, text="ሪፖርት አይነት:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.report_type_var = tk.StringVar(value="sales")
        report_types = [("ሽያጭ", "sales"), ("ወጪ", "expenses"), ("ክሬዲት", "credits"), ("ክምችት", "inventory")]
        
        type_frame = ttk.Frame(control_frame)
        type_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        for text, value in report_types:
            ttk.Radiobutton(type_frame, text=text, value=value, variable=self.report_type_var).pack(side="left", padx=5)
        
        # Date range
        ttk.Label(control_frame, text="ቀን:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.report_date_var = tk.StringVar(value="today")
        date_options = [("ዛሬ", "today"), ("ትላልቅን", "yesterday"), ("ይህ ሳምንት", "this_week"), ("ይህ ወር", "this_month"), ("ብጁ", "custom")]
        
        date_frame = ttk.Frame(control_frame)
        date_frame.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        for text, value in date_options:
            ttk.Radiobutton(date_frame, text=text, value=value, variable=self.report_date_var).pack(side="left", padx=5)
        
        # Custom date inputs (initially hidden)
        self.custom_date_frame = ttk.Frame(control_frame)
        self.custom_date_frame.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        self.custom_date_frame.grid_remove()
        
        ttk.Label(self.custom_date_frame, text="ከ:", style="TLabel").pack(side="left")
        self.report_start_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_date_frame, textvariable=self.report_start_var, width=12, style="primary.TEntry").pack(side="left", padx=5)
        
        ttk.Label(self.custom_date_frame, text="እስከ:", style="TLabel").pack(side="left", padx=(10,0))
        self.report_end_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_date_frame, textvariable=self.report_end_var, width=12, style="primary.TEntry").pack(side="left", padx=5)
        
        # Generate button
        ttk.Button(control_frame, text="ሪፖርት አሳይ", command=self.generate_report, style="primary.TButton").grid(row=0, column=4, padx=10, pady=10)
        
        # Export button
        ttk.Button(control_frame, text="ሪፖርት አትም", command=self.export_report, style="success.TButton").grid(row=0, column=5, padx=10, pady=10)
        
        control_frame.columnconfigure(3, weight=1)
        
        # Report display
        report_frame = ttk.LabelFrame(frm, text="ሪፖርት", style="info.TLabelframe")
        report_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.report_tree = ttk.Treeview(report_frame, columns=("col1", "col2", "col3", "col4", "col5"), show="headings", height=15, style="Treeview")
        
        scrollbar_report = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar_report.set)
        
        self.report_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_report.pack(side="right", fill="y", pady=5)
        
        # Summary frame
        summary_frame = ttk.Frame(report_frame)
        summary_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Label(summary_frame, text="ጠቅላላ:", style="TLabel").pack(pady=5)
        self.report_total_var = tk.StringVar(value="0.00 ብር")
        ttk.Label(summary_frame, textvariable=self.report_total_var, style="MetricValue.TLabel").pack(pady=5)
        
        # Bind date option change
        self.report_date_var.trace('w', self.on_report_date_change)
        
    def on_report_date_change(self, *args):
        if self.report_date_var.get() == "custom":
            self.custom_date_frame.grid()
        else:
            self.custom_date_frame.grid_remove()
            
    def generate_report(self):
        report_type = self.report_type_var.get()
        date_option = self.report_date_var.get()
        
        # Get date range
        if date_option == "today":
            start_date = datetime.now().date().isoformat()
            end_date = start_date
        elif date_option == "yesterday":
            start_date = (datetime.now() - timedelta(days=1)).date().isoformat()
            end_date = start_date
        elif date_option == "this_week":
            today = datetime.now().date()
            start_date = (today - timedelta(days=today.weekday())).isoformat()
            end_date = today.isoformat()
        elif date_option == "this_month":
            today = datetime.now().date()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        else:  # custom
            start_date = self.report_start_var.get()
            end_date = self.report_end_var.get()
            
            # Validate dates
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቀን ያስገቡ (YYYY-MM-DD)")
                return
        
        # Clear previous report
        self.report_tree.delete(*self.report_tree.get_children())
        
        # Configure columns based on report type
        if report_type == "sales":
            self.report_tree.configure(columns=("id", "date", "product", "qty", "price", "total", "method"))
            for c, t, w in [("id","ID",50), ("date","ቀን",120), ("product","ምርት",150), ("qty","ብዛት",80), ("price","ዋጋ",80), ("total","ጠቅላላ",100), ("method","ዘዴ",80)]:
                self.report_tree.heading(c, text=t)
                self.report_tree.column(c, width=w, anchor="w")
                
            # Get sales data
            self.cursor.execute('''
                SELECT s.id, s.sale_date, p.name, s.quantity, s.unit_price, s.total_price, s.payment_method
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE DATE(s.sale_date) BETWEEN ? AND ?
                ORDER BY s.sale_date
            ''', (start_date, end_date))
            
            total = 0
            for row in self.cursor.fetchall():
                date = str(row[1]).split('.')[0] if row[1] else ""
                self.report_tree.insert("", "end", values=(row[0], date, row[2], row[3], f"{row[4]:.2f}", f"{row[5]:.2f}", row[6]))
                total += row[5]
                
            self.report_total_var.set(f"{total:.2f} ብር")
            
        elif report_type == "expenses":
            self.report_tree.configure(columns=("id", "date", "description", "amount", "category", "user"))
            for c, t, w in [("id","ID",50), ("date","ቀን",120), ("description","መግለጫ",200), ("amount","መጠን",100), ("category","ምድብ",100), ("user","ተጠቃሚ",100)]:
                self.report_tree.heading(c, text=t)
                self.report_tree.column(c, width=w, anchor="w")
                
            # Get expenses data
            self.cursor.execute('''
                SELECT e.id, e.expense_date, e.description, e.amount, e.category, u.username
                FROM expenses e
                JOIN users u ON e.user_id = u.id
                WHERE DATE(e.expense_date) BETWEEN ? AND ?
                ORDER BY e.expense_date
            ''', (start_date, end_date))
            
            total = 0
            for row in self.cursor.fetchall():
                date = str(row[1]).split('.')[0] if row[1] else ""
                self.report_tree.insert("", "end", values=(row[0], date, row[2], f"{row[3]:.2f}", row[4], row[5]))
                total += row[3]
                
            self.report_total_var.set(f"{total:.2f} ብር")
            
        elif report_type == "credits":
            self.report_tree.configure(columns=("id", "customer", "amount", "paid", "balance", "status", "due"))
            for c, t, w in [("id","ID",50), ("customer","ደንበኛ",150), ("amount","መጠን",100), ("paid","የተከፈለ",100), ("balance","ቀሪ",100), ("status","ሁኔታ",100), ("due","የመጨረሻ ቀን",100)]:
                self.report_tree.heading(c, text=t)
                self.report_tree.column(c, width=w, anchor="w")
                
            # Get credits data
            self.cursor.execute('''
                SELECT id, customer_name, amount, paid_amount, 
                       (amount - paid_amount) as balance,
                       status, due_date
                FROM credits
                WHERE DATE(created_at) BETWEEN ? AND ?
                ORDER BY created_at
            ''', (start_date, end_date))
            
            total = 0
            for row in self.cursor.fetchall():
                due_date = row[6] or "የለም"
                self.report_tree.insert("", "end", values=(
                    row[0], row[1], f"{row[2]:.2f}", f"{row[3]:.2f}", 
                    f"{row[4]:.2f}", row[5], due_date
                ))
                total += row[2]  # Total credit amount
                
            self.report_total_var.set(f"{total:.2f} ብር")
            
        elif report_type == "inventory":
            self.report_tree.configure(columns=("id", "product", "qty", "unit", "cost", "total", "date"))
            for c, t, w in [("id","ID",50), ("product","ምርት",150), ("qty","ብዛት",80), ("unit","አሃድ",80), ("cost","ዋጋ",100), ("total","ጠቅላላ",100), ("date","ቀን",120)]:
                self.report_tree.heading(c, text=t)
                self.report_tree.column(c, width=w, anchor="w")
                
            # Get inventory data
            self.cursor.execute('''
                SELECT i.id, p.name, i.quantity, i.unit, i.cost, (i.quantity * i.cost), i.received_date
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                WHERE DATE(i.received_date) BETWEEN ? AND ?
                ORDER BY i.received_date
            ''', (start_date, end_date))
            
            total = 0
            for row in self.cursor.fetchall():
                date = str(row[6]).split('.')[0] if row[6] else ""
                self.report_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], f"{row[4]:.2f}", f"{row[5]:.2f}", date))
                total += row[5]
                
            self.report_total_var.set(f"{total:.2f} ብር")
            
    def export_report(self):
        # Get all items from the report tree
        items = self.report_tree.get_children()
        if not items:
            messagebox.showwarning("ማስጠንቀቂያ", "ምንም ሪፖርት የለም ለማተም")
            return
            
        # Prepare report text
        report_type = self.report_type_var.get()
        report_title = {
            "sales": "የሽያጭ ሪፖርት",
            "expenses": "የወጪ ሪፖርት",
            "credits": "የክሬዲት ሪፖርት",
            "inventory": "የክምችት ሪፖርት"
        }.get(report_type, "ሪፖርት")
        
        date_option = self.report_date_var.get()
        if date_option == "custom":
            date_range = f"ከ {self.report_start_var.get()} እስከ {self.report_end_var.get()}"
        else:
            date_range = {
                "today": "ዛሬ",
                "yesterday": "ትላልቅን",
                "this_week": "ይህ ሳምንት",
                "this_month": "ይህ ወር"
            }.get(date_option, "")
        
        report_text = f"""
        ሬስቶራንት ሲስተም
        {report_title}
        {date_range}
        ቀን: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        --------------------
        """
        
        # Add column headers
        columns = [self.report_tree.heading(col)["text"] for col in self.report_tree["columns"]]
        report_text += " | ".join(columns) + "\n"
        report_text += "-" * 50 + "\n"
        
        # Add data rows
        for item in items:
            values = self.report_tree.item(item)["values"]
            report_text += " | ".join(str(v) for v in values) + "\n"
        
        # Add total
        report_text += f"""
        --------------------
        ጠቅላላ: {self.report_total_var.get()}
        """
        
        # Print the report
        if print_receipt(report_text):
            messagebox.showinfo("ተሳክቷል", "ሪፖርት ተታትሟል")

    # ---------------- User Management ----------------
    def build_users_tab(self):
        if self.user["role"] != "admin":
            ttk.Label(self.users_frame, text="ይህንን ክፍል ለማየት ፈቃድ የለዎትም", style="Header.TLabel").pack(pady=50)
            return
            
        frm = self.users_frame
        
        # User entry section
        entry_frame = ttk.LabelFrame(frm, text="አዲስ ተጠቃሚ", style="info.TLabelframe")
        entry_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Username
        ttk.Label(entry_frame, text="የተጠቃሚ ስም:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.user_username_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.user_username_var, width=20, style="primary.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Password
        ttk.Label(entry_frame, text="የይለፍ ቃል:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.user_password_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.user_password_var, show="*", width=20, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Role
        ttk.Label(entry_frame, text="ሚና:", style="TLabel").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.user_role_var = tk.StringVar(value="staff")
        roles = ["admin", "staff", "cashier", "waiter"]
        ttk.Combobox(entry_frame, textvariable=self.user_role_var, values=roles, state="readonly", width=15, style="primary.TCombobox").grid(row=0, column=5, padx=10, pady=10, sticky="w")
        
        # Add user button
        ttk.Button(entry_frame, text="ተጠቃሚ ጨምር", command=self.add_user, style="primary.TButton").grid(row=0, column=6, padx=10, pady=10)
        
        entry_frame.columnconfigure(1, weight=1)
        
        # Users list
        list_frame = ttk.LabelFrame(frm, text="ተጠቃሚዎች ዝርዝር", style="info.TLabelframe")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.users_tree = ttk.Treeview(list_frame, columns=("id", "username", "role"), show="headings", height=15, style="Treeview")
        for c, t, w in [("id","ID",50), ("username","የተጠቃሚ ስም",150), ("role","ሚና",100)]:
            self.users_tree.heading(c, text=t)
            self.users_tree.column(c, width=w, anchor="w")
            
        scrollbar_user = ttk.Scrollbar(list_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar_user.set)
        
        self.users_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_user.pack(side="right", fill="y", pady=5)
        
        # User actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="የይለፍ ቃል ቀይር", command=self.change_user_password, style="primary.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ሚና ቀይር", command=self.change_user_role, style="warning.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ተጠቃሚ ሰርዝ", command=self.delete_user, style="danger.TButton").pack(pady=5)
        
        self.refresh_users()
        
    def add_user(self):
        username = self.user_username_var.get().strip()
        password = self.user_password_var.get().strip()
        role = self.user_role_var.get()
        
        if not username or not password:
            messagebox.showerror("ስህተት", "እባክዎ የተጠቃሚ ስም እና የይለፍ ቃል ያስገቡ")
            return
            
        try:
            password_hash = sha256(password)
            
            self.cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                              (username, password_hash, role))
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ተጠቃሚ በትክክል ተመዝግቧል")
            self.refresh_users()
            
            # Clear input fields
            self.user_username_var.set("")
            self.user_password_var.set("")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("ስህተት", "የተጠቃሚ ስም አስቀድሞ አለ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ተጠቃሚ ማስገባት አልተሳካም: {str(e)}")
            
    def refresh_users(self):
        self.users_tree.delete(*self.users_tree.get_children())
        
        self.cursor.execute('SELECT id, username, role FROM users ORDER BY username')
        
        for row in self.cursor.fetchall():
            self.users_tree.insert("", "end", values=row)
            
    def change_user_password(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ተጠቃሚ ይምረጡ")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        # Create password change window
        pass_win = tk.Toplevel(self.root)
        pass_win.title("የይለፍ ቃል ቀይር")
        pass_win.geometry("300x200")
        
        ttk.Label(pass_win, text=f"የይለፍ ቃል ለ {username}", style="Header.TLabel").pack(pady=10)
        
        ttk.Label(pass_win, text="አዲስ የይለፍ ቃል:", style="TLabel").pack(pady=5)
        new_pass_var = tk.StringVar()
        ttk.Entry(pass_win, textvariable=new_pass_var, show="*", width=20, style="primary.TEntry").pack(pady=5)
        
        ttk.Label(pass_win, text="የይለፍ ቃል አረጋግጥ:", style="TLabel").pack(pady=5)
        confirm_pass_var = tk.StringVar()
        ttk.Entry(pass_win, textvariable=confirm_pass_var, show="*", width=20, style="primary.TEntry").pack(pady=5)
        
        def update_password():
            new_pass = new_pass_var.get().strip()
            confirm_pass = confirm_pass_var.get().strip()
            
            if not new_pass:
                messagebox.showerror("ስህተት", "እባክዎ የይለፍ ቃል ያስገቡ")
                return
                
            if new_pass != confirm_pass:
                messagebox.showerror("ስህተት", "የይለፍ ቃሎች አይጣጣሙም")
                return
                
            try:
                password_hash = sha256(new_pass)
                
                self.cursor.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "የይለፍ ቃል በትክክል ተቀይሯል")
                pass_win.destroy()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"የይለፍ ቃል ማዘመን አልተሳካም: {str(e)}")
                
        ttk.Button(pass_win, text="አዘምን", command=update_password, style="primary.TButton").pack(pady=20)
        
    def change_user_role(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ተጠቃሚ ይምረጡ")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        current_role = item['values'][2]
        
        # Create role change window
        role_win = tk.Toplevel(self.root)
        role_win.title("ሚና ቀይር")
        role_win.geometry("300x150")
        
        ttk.Label(role_win, text=f"ሚና ለ {username}", style="Header.TLabel").pack(pady=10)
        
        ttk.Label(role_win, text="አዲስ ሚና:", style="TLabel").pack(pady=5)
        new_role_var = tk.StringVar(value=current_role)
        roles = ["admin", "staff", "cashier", "waiter"]
        ttk.Combobox(role_win, textvariable=new_role_var, values=roles, state="readonly", width=15, style="primary.TCombobox").pack(pady=5)
        
        def update_role():
            new_role = new_role_var.get()
            
            try:
                self.cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ሚና በትክክል ተቀይሯል")
                role_win.destroy()
                self.refresh_users()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ሚና ማዘመን አልተሳካም: {str(e)}")
                
        ttk.Button(role_win, text="አዘምን", command=update_role, style="primary.TButton").pack(pady=20)
        
    def delete_user(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ተጠቃሚ ይምረጡ")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        if user_id == self.user["id"]:
            messagebox.showerror("ስህተት", "ራስዎን ማስወገድ አይችሉም")
            return
            
        if messagebox.askyesno("አረጋግጥ", f"እርግጠኛ ነዎት ይህን ተጠቃሚ ለማስወገድ? ({username})"):
            try:
                self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ተጠቃሚ በትክክል ተሰርዟል")
                self.refresh_users()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ተጠቃሚ ማስወገድ አልተሳካም: {str(e)}")

    # ---------------- Capital Management ----------------
    def build_capital_tab(self):
        if self.user["role"] != "admin":
            ttk.Label(self.capital_frame, text="ይህንን ክፍል ለማየት ፈቃድ የለዎትም", style="Header.TLabel").pack(pady=50)
            return
            
        frm = self.capital_frame
        
        # Capital entry section
        entry_frame = ttk.LabelFrame(frm, text="ካፒታል አስገባ", style="info.TLabelframe")
        entry_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Amount
        ttk.Label(entry_frame, text="መጠን:", style="TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.capital_amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.capital_amount_var, width=15, style="primary.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Note
        ttk.Label(entry_frame, text="ማስታወሻ:", style="TLabel").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.capital_note_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.capital_note_var, width=30, style="primary.TEntry").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Add capital button
        ttk.Button(entry_frame, text="ካፒታል ጨምር", command=self.add_capital, style="primary.TButton").grid(row=0, column=4, padx=10, pady=10)
        
        entry_frame.columnconfigure(3, weight=1)
        
        # Capital list
        list_frame = ttk.LabelFrame(frm, text="ካፒታል ዝርዝር", style="info.TLabelframe")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.capital_tree = ttk.Treeview(list_frame, columns=("id", "date", "amount", "note"), show="headings", height=15, style="Treeview")
        for c, t, w in [("id","ID",50), ("date","ቀን",120), ("amount","መጠን",100), ("note","ማስታወሻ",250)]:
            self.capital_tree.heading(c, text=t)
            self.capital_tree.column(c, width=w, anchor="w")
            
        scrollbar_cap = ttk.Scrollbar(list_frame, orient="vertical", command=self.capital_tree.yview)
        self.capital_tree.configure(yscrollcommand=scrollbar_cap.set)
        
        self.capital_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_cap.pack(side="right", fill="y", pady=5)
        
        # Capital summary
        summary_frame = ttk.Frame(list_frame)
        summary_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Label(summary_frame, text="ጠቅላላ ካፒታል:", style="TLabel").pack(pady=5)
        self.capital_total_var = tk.StringVar(value="0.00 ብር")
        ttk.Label(summary_frame, textvariable=self.capital_total_var, style="MetricValue.TLabel").pack(pady=5)
        
        # Capital actions
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ttk.Button(action_frame, text="ዝርዝር አሳይ", command=self.show_capital_details, style="primary.TButton").pack(pady=5)
        ttk.Button(action_frame, text="ካፒታል ሰርዝ", command=self.delete_capital, style="danger.TButton").pack(pady=5)
        
        self.refresh_capital()
        
    def add_capital(self):
        amount_str = self.capital_amount_var.get().strip()
        note = self.capital_note_var.get().strip()
        
        if not amount_str:
            messagebox.showerror("ስህተት", "እባክዎ መጠን ያስገቡ")
            return
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("ስህተት", "መጠን ከዜሮ በላይ መሆን አለበት")
                return
                
            self.cursor.execute("INSERT INTO capital (amount, note) VALUES (?, ?)", (amount, note))
            self.conn.commit()
            
            messagebox.showinfo("ተሳክቷል", "ካፒታል በትክክል ተመዝግቧል")
            self.refresh_capital()
            
            # Clear input fields
            self.capital_amount_var.set("")
            self.capital_note_var.set("")
            
        except ValueError:
            messagebox.showerror("ስህተት", "እባክዎ ትክክለኛ ቁጥር ያስገቡ")
        except Exception as e:
            messagebox.showerror("ስህተት", f"ካፒታል ማስገባት አልተሳካም: {str(e)}")
            
    def refresh_capital(self):
        self.capital_tree.delete(*self.capital_tree.get_children())
        
        self.cursor.execute('SELECT id, created_at, amount, note FROM capital ORDER BY created_at DESC')
        
        total = 0
        for row in self.cursor.fetchall():
            date = str(row[1]).split('.')[0] if row[1] else ""
            self.capital_tree.insert("", "end", values=(row[0], date, f"{row[2]:.2f}", row[3]))
            total += row[2]
            
        self.capital_total_var.set(f"{total:.2f} ብር")
        
    def show_capital_details(self):
        selection = self.capital_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ካፒታል ይምረጡ")
            return
            
        item = self.capital_tree.item(selection[0])
        cap_id = item['values'][0]
        
        self.cursor.execute('SELECT created_at, amount, note FROM capital WHERE id=?', (cap_id,))
        
        result = self.cursor.fetchone()
        if result:
            date, amount, note = result
            date_str = str(date).split('.')[0] if date else ""
            
            details = f"""
            የካፒታል ዝርዝር - ID: {cap_id}
            --------------------
            ቀን: {date_str}
            መጠን: {amount:.2f} ብር
            ማስታወሻ: {note}
            """
            
            messagebox.showinfo("የካፒታል ዝርዝር", details)
            
    def delete_capital(self):
        selection = self.capital_tree.selection()
        if not selection:
            messagebox.showwarning("ማስጠንቀቂያ", "እባክዎ ካፒታል ይምረጡ")
            return
            
        item = self.capital_tree.item(selection[0])
        cap_id = item['values'][0]
        amount = item['values'][2]
        
        if messagebox.askyesno("አረጋግጥ", f"እርግጠኛ ነዎት ይህን ካፒታል ለማስወገድ? ({amount})"):
            try:
                self.cursor.execute("DELETE FROM capital WHERE id=?", (cap_id,))
                self.conn.commit()
                
                messagebox.showinfo("ተሳክቷል", "ካፒታል በትክክል ተሰርዟል")
                self.refresh_capital()
                
            except Exception as e:
                messagebox.showerror("ስህተት", f"ካፒታል ማስወገድ አልተሳካም: {str(e)}")

    # ---------------- Helper Methods ----------------
    def get_product_names(self):
        self.cursor.execute("SELECT name FROM products ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]
        
    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_orders()
        self.refresh_sales()
        self.refresh_expenses()
        self.refresh_credits()
        self.refresh_inventory()
        self.refresh_products()
        if self.user["role"] == "admin":
            self.refresh_users()
            self.refresh_capital()
        if self.user["role"] in ["admin", "waiter"]:
            self.refresh_staff_performance()
            
    def close_app(self):
        self.conn.close()
        self.root.destroy()

# ---------------- Main Application ----------------
def main():
    # Initialize database
    init_database()
    
    # Create main window
    root = ttk.Window(themename="flatly")
    root.title("ሬስቶራንት ሲስተም - መግቢያ")
    root.geometry("600x400")
    root.resizable(False, False)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (600 // 2)
    y = (root.winfo_screenheight() // 2) - (400 // 2)
    root.geometry(f"600x400+{x}+{y}")
    
    # Welcome screen
    welcome_frame = ttk.Frame(root, padding=30, style="light.TFrame")
    welcome_frame.pack(fill="both", expand=True)
    
    ttk.Label(welcome_frame, text="ሬስቶራንት ሲስተም", 
              font=("Arial", 24, "bold"), 
              style="primary.Inverse.TLabel").pack(pady=(40, 20))
    
    ttk.Label(welcome_frame, text="ሽያጭ፣ ወጪ፣ ክምችት እና ሪፖርቶች", 
              font=("Arial", 14), 
              style="TLabel").pack(pady=(0, 40))
    
    def start_login():
        def on_login_success(user):
            welcome_frame.destroy()
            app = RestaurantSystem(root, user)
            root.protocol("WM_DELETE_WINDOW", app.close_app)
            
        LoginWindow(root, on_login_success)
    
    ttk.Button(welcome_frame, text="መግቢያ", command=start_login, 
               style="success.TButton", width=15).pack(pady=10)
    
    ttk.Button(welcome_frame, text="ውጣ", command=root.destroy, 
               style="secondary.TButton", width=15).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()