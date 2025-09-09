import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import sqlite3
import pandas as pd
import uuid
import os
import shutil
import datetime
import qrcode
from PIL import Image, ImageTk, ImageDraw
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import io
import requests
import svglib.svglib
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.graphics.barcode import code128
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Fungsi Pustaka Tambahan (Placeholder, perlu diinstal) ---
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    pass

# --- URL Ikon dari Icons8 (SVG untuk kualitas tinggi) ---
ICONS = {
    "login": "https://img.icons8.com/wired/64/user--v1.png",
    "dashboard": "https://img.icons8.com/wired/64/dashboard.png",
    "products": "https://img.icons8.com/wired/64/shopping-cart-loaded.png",
    "categories": "https://img.icons8.com/wired/64/tags--v1.png",
    "sales": "https://img.icons8.com/wired/64/sales-performance.png",
    "stock": "https://img.icons8.com/wired/64/in-transit.png",
    "cashier": "https://img.icons8.com/wired/64/cashier-machine.png",
    "logout": "https://img.icons8.com/wired/64/exit.png",
    "users": "https://img.icons8.com/wired/64/admin-settings-male.png",
    "add_user": "https://img.icons8.com/wired/64/add-user-male.png",
    "edit_user": "https://img.icons8.com/wired/64/edit-user-male.png",
    "delete_user": "https://img.icons8.com/wired/64/delete-user-male.png",
    "end_shift": "https://img.icons8.com/wired/64/clock.png",
    "search": "https://img.icons8.com/wired/64/search.png",
    "export": "https://img.icons8.com/wired/64/export.png",
    "reports": "https://img.icons8.com/wired/64/bar-chart.png"
}

# --- Kelas Manajemen Database ---
class DatabaseManager:
    """Mengelola koneksi dan operasi database SQLite."""
    def __init__(self, db_path='database/billing_db.sqlite'):
        self.db_path = db_path
        self._ensure_db_path()
        self.conn = None

    def _ensure_db_path(self):
        """Memastikan direktori database dan folder aset ada."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        if not os.path.exists('images'):
            os.makedirs('images')

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def _create_tables(self):
        """Membuat tabel jika belum ada."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'cashier'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon_url TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                hpp REAL NOT NULL,
                stock INTEGER NOT NULL,
                category_id INTEGER,
                image_path TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                product_sku TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                hpp REAL NOT NULL,
                payment_method TEXT NOT NULL,
                sale_timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_start_time TEXT NOT NULL,
                shift_end_time TEXT NOT NULL,
                cashier_id INTEGER NOT NULL,
                blind_deposit_amount REAL NOT NULL,
                actual_sales_total REAL NOT NULL,
                discrepancy REAL NOT NULL
            )
        """)
        self.conn.commit()
        self._seed_data()
        
    def _seed_data(self):
        """Memasukkan data contoh untuk pengujian."""
        cursor = self.conn.cursor()
        users = [('admin', 'admin123', 'admin'), ('kasir1', 'kasir123', 'cashier')]
        cursor.executemany("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", users)

        categories = [
            ("Laptop", ICONS['products']),
            ("Komputer", ICONS['products']),
            ("CCTV", ICONS['products']),
            ("Aksesoris Komputer", ICONS['products'])
        ]
        cursor.executemany("INSERT OR IGNORE INTO categories (name, icon_url) VALUES (?, ?)", categories)
        self.conn.commit()
        
        # Ambil category_id setelah seeding
        laptop_id = cursor.execute("SELECT id FROM categories WHERE name='Laptop'").fetchone()['id']
        komputer_id = cursor.execute("SELECT id FROM categories WHERE name='Komputer'").fetchone()['id']
        aksesoris_id = cursor.execute("SELECT id FROM categories WHERE name='Aksesoris Komputer'").fetchone()['id']
        cctv_id = cursor.execute("SELECT id FROM categories WHERE name='CCTV'").fetchone()['id']

        products = [
            ('LPT001', 'Laptop Gaming ROG', 'Laptop gaming berperforma tinggi dengan RTX 4080.', 35000000.00, 30000000.00, 5, laptop_id, None),
            ('LPT002', 'Laptop Bisnis Ultrabook', 'Laptop tipis dan ringan untuk produktivitas.', 18000000.00, 15000000.00, 10, laptop_id, None),
            ('PC001', 'PC Desktop Rakitan Core i7', 'PC serbaguna untuk pekerjaan sehari-hari.', 12500000.00, 10000000.00, 8, komputer_id, None),
            ('CCTV001', 'CCTV 360 Derajat', 'Kamera pengawas pintar dengan rotasi 360 derajat.', 750000.00, 500000.00, 20, cctv_id, None),
            ('ACC001', 'Keyboard Mekanikal RGB', 'Keyboard gaming dengan lampu RGB dan switch biru.', 1500000.00, 1200000.00, 50, aksesoris_id, None)
        ]
        cursor.executemany("INSERT OR IGNORE INTO products (sku, name, description, price, hpp, stock, category_id, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", products)
        self.conn.commit()

    def get_users(self):
        """Mengambil semua pengguna dari database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users")
        return cursor.fetchall()
        
    def add_user(self, username, password, role):
        """Menambahkan pengguna baru ke database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_user(self, user_id, username, password, role):
        """Memperbarui data pengguna."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET username=?, password=?, role=? WHERE id=?", (username, password, role, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        """Menghapus pengguna dari database."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()
        
    def add_deposit(self, cashier_id, start_time, end_time, blind_amount, actual_sales_total, discrepancy):
        """Menambahkan catatan setoran kasir."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO deposits (cashier_id, shift_start_time, shift_end_time, blind_deposit_amount, actual_sales_total, discrepancy) VALUES (?, ?, ?, ?, ?, ?)",
                       (cashier_id, start_time, end_time, blind_amount, actual_sales_total, discrepancy))
        self.conn.commit()

    def get_user_by_id(self, user_id):
        """Mencari pengguna berdasarkan ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return cursor.fetchone()

    def get_product_by_sku(self, sku):
        """Mencari produk berdasarkan SKU."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE sku=?", (sku,))
        return cursor.fetchone()

    def update_product_stock(self, sku, quantity):
        """Memperbarui stok produk."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE sku=?", (quantity, sku))
        self.conn.commit()
        
    def add_product(self, sku, name, desc, price, hpp, stock, cat_id, img_path):
        """Menambahkan produk baru ke database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO products (sku, name, description, price, hpp, stock, category_id, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (sku, name, desc, price, hpp, stock, cat_id, img_path))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def update_product(self, sku, name, desc, price, hpp, stock, cat_id, img_path):
        """Memperbarui data produk yang ada."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET name=?, description=?, price=?, hpp=?, stock=?, category_id=?, image_path=? WHERE sku=?",
                       (name, desc, price, hpp, stock, cat_id, img_path, sku))
        self.conn.commit()

    def delete_product(self, sku):
        """Menghapus produk dari database."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM products WHERE sku=?", (sku,))
        self.conn.commit()

    def get_products(self, query=""):
        """Mengambil semua produk dari database, dengan filter pencarian."""
        cursor = self.conn.cursor()
        if query:
            cursor.execute("SELECT p.sku, p.name, p.price, p.hpp, p.stock, c.name as category, p.description, p.image_path FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.sku LIKE ? OR p.name LIKE ? OR c.name LIKE ? ORDER BY p.name ASC", (f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("SELECT p.sku, p.name, p.price, p.hpp, p.stock, c.name as category, p.description, p.image_path FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.name ASC")
        return cursor.fetchall()
        
    def add_sale(self, transaction_id, product_sku, product_name, quantity, price, hpp, payment_method, timestamp):
        """Menambahkan entri penjualan."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sales (transaction_id, product_sku, product_name, quantity, price, hpp, payment_method, sale_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (transaction_id, product_sku, product_name, quantity, price, hpp, payment_method, timestamp))
        self.conn.commit()

    def get_sales_report(self, start_date=None, end_date=None):
        """Mengambil laporan penjualan."""
        cursor = self.conn.cursor()
        if start_date and end_date:
            cursor.execute("SELECT * FROM sales WHERE sale_timestamp BETWEEN ? AND ?", (start_date, end_date))
        else:
            cursor.execute("SELECT * FROM sales")
        return cursor.fetchall()
    
    def get_sales_by_payment_method(self):
        """Mengambil rekap penjualan per metode pembayaran."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT payment_method, SUM(quantity * price) as total_sales, SUM(quantity * (price - hpp)) as total_profit FROM sales GROUP BY payment_method")
        return cursor.fetchall()

    def get_categories(self):
        """Mengambil semua kategori."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        return cursor.fetchall()

    def get_categories_with_urls(self):
        """Mengambil semua kategori dengan URL ikon."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, icon_url FROM categories")
        return cursor.fetchall()

    def add_category(self, name, icon_url):
        """Menambahkan kategori baru."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name, icon_url) VALUES (?, ?)", (name, icon_url))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_category(self, name):
        """Menghapus kategori dan produk terkait."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM categories WHERE name=?", (name,))
        self.conn.commit()

    def get_top_selling_products(self, limit=10):
        """Mengambil produk terlaris."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT product_name, SUM(quantity) as total_quantity FROM sales GROUP BY product_name ORDER BY total_quantity DESC LIMIT ?", (limit,))
        return cursor.fetchall()

# --- Kelas Utama Aplikasi UI ---
class BillingApp(ttk.Window):
    def __init__(self, db_manager):
        super().__init__(themename="darkly")
        self.title("Aplikasi Billing Profesional")
        self.geometry("1400x900")
        self.db = db_manager
        self.db.connect()
        self.current_user = None
        self.shift_start_time = None
        
        self.style.configure("TNotebook", tabposition="n", background="#1A1A1A")
        self.style.configure("TNotebook.Tab", font=("Inter", 10, "bold"), padding=[15, 5])
        self.style.configure("TButton", font=("Inter", 10, "bold"), borderwidth=2, relief="solid")
        self.style.configure("TLabel", font=("Inter", 10), background="#1A1A1A", foreground="#E0E0E0")
        self.style.configure("TFrame", background="#1A1A1A")
        self.style.configure("Gold.TLabel", foreground="#FFD700", font=("Inter", 12, "bold"), background="#1A1A1A")
        self.style.configure("Neon.TLabel", foreground="#39FF14", background="#1A1A1A", font=("Inter", 10, "bold"))
        self.style.configure("Neon.TButton", background="#333333", foreground="#39FF14", bordercolor="#39FF14")
        self.style.map("Neon.TButton", background=[("active", "#444444")])
        self.style.configure("Gold.TButton", background="#333333", foreground="#FFD700", bordercolor="#FFD700")
        self.style.map("Gold.TButton", background=[("active", "#444444")])
        self.style.configure("Treeview", background="#1A1A1A", foreground="#E0E0E0", fieldbackground="#1A1A1A", borderwidth=1, relief="solid")
        self.style.configure("Treeview.Heading", background="#333333", foreground="#FFD700")
        
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        self.login_frame()

    def show_toast(self, message, style="info"):
        """Menampilkan notifikasi melayang (toast)."""
        toast = ttk.Toplevel(self)
        toast.wm_attributes("-alpha", 0.9)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        toast_width = 300
        toast_height = 50
        x = screen_width - toast_width - 20
        y = screen_height - toast_height - 60
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        toast.overrideredirect(True)
        toast_label = ttk.Label(toast, text=message, padding=10, bootstyle=f"{style}-inverse", anchor="center", font=("Inter", 10, "bold"))
        toast_label.pack(fill=BOTH, expand=True)
        self.after(3000, toast.destroy)

    def load_icon(self, url, size=(24, 24)):
        """Memuat ikon dari URL dan mengubah ukurannya."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(io.BytesIO(img_data)).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def login_frame(self):
        """Halaman login multi-user."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        login_container = ttk.Frame(self.main_frame, padding=40, style="TFrame")
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        logo_img = self.load_icon("https://img.icons8.com/wired/64/shopping-bag--v1.png", size=(80, 80))
        logo_label = ttk.Label(login_container, image=logo_img, style="TFrame")
        logo_label.image = logo_img
        logo_label.pack(pady=(0, 10))

        ttk.Label(login_container, text="APP BILLING PRO", font=("Inter", 24, "bold"), foreground="#39FF14").pack(pady=(0, 20))
        ttk.Label(login_container, text="Selamat Datang", font=("Inter", 18, "bold"), foreground="#FFD700").pack(pady=10)
        
        ttk.Label(login_container, text="Username:", foreground="#E0E0E0").pack(pady=(10, 0))
        self.username_entry = ttk.Entry(login_container, width=30)
        self.username_entry.insert(0, "admin")
        self.username_entry.pack(pady=5)
        
        ttk.Label(login_container, text="Password:", foreground="#E0E0E0").pack(pady=(10, 0))
        self.password_entry = ttk.Entry(login_container, show="*", width=30)
        self.password_entry.insert(0, "admin123")
        self.password_entry.pack(pady=5)
        
        ttk.Button(login_container, text="Login", command=self.login, bootstyle="warning").pack(pady=20, ipadx=10, ipady=5)
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        users = self.db.get_users()
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        
        if user:
            self.current_user = user
            self.shift_start_time = datetime.datetime.now()
            self.show_toast(f"Selamat datang, {user['username']}", style="success")
            self.main_ui()
        else:
            self.show_toast("Login Gagal: Username atau password salah.", style="danger")

    def main_ui(self):
        """Tampilan utama aplikasi setelah login."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Sidebar
        sidebar_frame = ttk.Frame(self.main_frame, width=200, style="primary.TFrame")
        sidebar_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        logo_img = self.load_icon("https://img.icons8.com/wired/64/shopping-bag--v1.png", size=(48, 48))
        logo_label = ttk.Label(sidebar_frame, image=logo_img, text="MENU", compound="left", font=("Inter", 14, "bold"), bootstyle="inverse")
        logo_label.image = logo_img
        logo_label.pack(pady=10)
        
        self.content_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        btn_style = "info-outline"

        dashboard_icon = self.load_icon(ICONS['dashboard'])
        btn_dashboard = ttk.Button(sidebar_frame, text="Dashboard", command=self.show_dashboard, image=dashboard_icon, compound="left", bootstyle=btn_style)
        btn_dashboard.image = dashboard_icon
        btn_dashboard.pack(fill=X, padx=10, pady=5)
        
        if self.current_user['role'] == 'admin':
            ttk.Label(sidebar_frame, text="ADMIN", font=("Inter", 12, "bold"), bootstyle="inverse").pack(pady=(10, 5))
            
            users_icon = self.load_icon(ICONS['users'])
            btn_users = ttk.Button(sidebar_frame, text="Manajemen Pengguna", command=self.show_user_management, image=users_icon, compound="left", bootstyle=btn_style)
            btn_users.image = users_icon
            btn_users.pack(fill=X, padx=10, pady=5)
            
            products_icon = self.load_icon(ICONS['products'])
            btn_products = ttk.Button(sidebar_frame, text="Manajemen Produk", command=self.show_product_management, image=products_icon, compound="left", bootstyle=btn_style)
            btn_products.image = products_icon
            btn_products.pack(fill=X, padx=10, pady=5)
            
            categories_icon = self.load_icon(ICONS['categories'])
            btn_categories = ttk.Button(sidebar_frame, text="Manajemen Kategori", command=self.show_category_management, image=categories_icon, compound="left", bootstyle=btn_style)
            btn_categories.image = categories_icon
            btn_categories.pack(fill=X, padx=10, pady=5)

        ttk.Label(sidebar_frame, text="KASIR & LAPORAN", font=("Inter", 12, "bold"), bootstyle="inverse").pack(pady=(10, 5))
        
        cashier_icon = self.load_icon(ICONS['cashier'])
        btn_cashier = ttk.Button(sidebar_frame, text="Kasir", command=self.show_cashier, image=cashier_icon, compound="left", bootstyle=btn_style)
        btn_cashier.image = cashier_icon
        btn_cashier.pack(fill=X, padx=10, pady=5)

        sales_icon = self.load_icon(ICONS['sales'])
        btn_sales = ttk.Button(sidebar_frame, text="Laporan Penjualan", command=self.show_sales_report, image=sales_icon, compound="left", bootstyle=btn_style)
        btn_sales.image = sales_icon
        btn_sales.pack(fill=X, padx=10, pady=5)

        stock_icon = self.load_icon(ICONS['stock'])
        btn_stock = ttk.Button(sidebar_frame, text="Laporan Stok", command=self.show_stock_report, image=stock_icon, compound="left", bootstyle=btn_style)
        btn_stock.image = stock_icon
        btn_stock.pack(fill=X, padx=10, pady=5)

        if self.current_user['role'] == 'cashier':
            end_shift_icon = self.load_icon(ICONS['end_shift'])
            btn_end_shift = ttk.Button(sidebar_frame, text="Akhiri Shift", command=self.end_shift_dialog, image=end_shift_icon, compound="left", bootstyle="warning-outline")
            btn_end_shift.image = end_shift_icon
            btn_end_shift.pack(fill=X, padx=10, pady=5)
            
        logout_icon = self.load_icon(ICONS['logout'])
        btn_logout = ttk.Button(sidebar_frame, text="Logout", command=self.login_frame, image=logout_icon, compound="left", bootstyle="danger-outline")
        btn_logout.image = logout_icon
        btn_logout.pack(fill=X, padx=10, pady=(20, 5), side=BOTTOM)
        
        self.show_dashboard()
        
    def clear_content_frame(self):
        """Mengosongkan frame konten."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content_frame()
        
        header_frame = ttk.Frame(self.content_frame, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Dashboard", font=("Inter", 24, "bold"), foreground="#39FF14").pack(side=LEFT)

        main_dashboard_frame = ttk.Frame(self.content_frame, padding=10)
        main_dashboard_frame.pack(fill=BOTH, expand=True)

        # Kotak info total
        info_frame = ttk.Frame(main_dashboard_frame)
        info_frame.pack(fill=X, pady=10)

        sales_data = self.db.get_sales_report()
        total_sales_value = sum(s['quantity'] * s['price'] for s in sales_data)
        total_profit_value = sum(s['quantity'] * (s['price'] - s['hpp']) for s in sales_data)
        total_products_value = len(self.db.get_products())
        
        self.create_info_card(info_frame, "Total Penjualan", f"Rp{total_sales_value:,.0f}", "success")
        self.create_info_card(info_frame, "Total Keuntungan", f"Rp{total_profit_value:,.0f}", "warning")
        self.create_info_card(info_frame, "Jumlah Produk", f"{total_products_value}", "info")
        
        # Grafik
        charts_frame = ttk.Frame(main_dashboard_frame)
        charts_frame.pack(fill=BOTH, expand=True)
        
        self.create_monthly_sales_chart(charts_frame)
        self.create_payment_method_chart(charts_frame)
        self.create_top_selling_chart(charts_frame)

    def create_info_card(self, parent, title, value, bootstyle):
        card = ttk.Frame(parent, bootstyle=bootstyle)
        card.pack(side=LEFT, fill=BOTH, expand=True, padx=5, ipadx=10, ipady=10)
        ttk.Label(card, text=title, font=("Inter", 12, "bold"), bootstyle=f"{bootstyle}-inverse").pack(pady=(0, 5))
        ttk.Label(card, text=value, font=("Inter", 20, "bold"), bootstyle=f"{bootstyle}-inverse").pack()
        
    def create_monthly_sales_chart(self, parent):
        sales = self.db.get_sales_report()
        sales_by_month = {}
        for sale in sales:
            month = datetime.datetime.fromisoformat(sale['sale_timestamp']).strftime('%Y-%m')
            sales_by_month[month] = sales_by_month.get(month, 0) + (sale['price'] * sale['quantity'])

        months = list(sales_by_month.keys())
        values = list(sales_by_month.values())

        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#1A1A1A')
        ax.bar(months, values, color='#39FF14')
        ax.set_title('Penjualan Bulanan', color='white')
        ax.set_ylabel('Rupiah', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor('#1A1A1A')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
    def create_payment_method_chart(self, parent):
        sales = self.db.get_sales_by_payment_method()
        labels = [s['payment_method'] for s in sales]
        sizes = [s['total_sales'] for s in sales]
        colors = ['#FFD700', '#39FF14', '#1E90FF']

        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#1A1A1A')
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        ax.set_title('Penjualan per Metode Pembayaran', color='white')
        ax.set_facecolor('#1A1A1A')
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

    def create_top_selling_chart(self, parent):
        top_products = self.db.get_top_selling_products(limit=5)
        names = [p['product_name'] for p in top_products]
        quantities = [p['total_quantity'] for p in top_products]

        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#1A1A1A')
        ax.barh(names, quantities, color='#FF4500')
        ax.set_title('Top 5 Produk Terlaris', color='white')
        ax.set_xlabel('Jumlah Terjual', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor('#1A1A1A')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

    # --- Halaman Manajemen Pengguna (khusus Admin) ---
    def show_user_management(self):
        self.clear_content_frame()
        
        header_frame = ttk.Frame(self.content_frame, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Manajemen Pengguna", font=("Inter", 24, "bold"), foreground="#39FF14").pack(side=LEFT)
        
        form_frame = ttk.Frame(self.content_frame, padding=10)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Username:", style="Gold.TLabel").grid(row=0, column=0, padx=5, pady=2, sticky="W")
        self.user_username_entry = ttk.Entry(form_frame, width=30)
        self.user_username_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Password:", style="Gold.TLabel").grid(row=1, column=0, padx=5, pady=2, sticky="W")
        self.user_password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.user_password_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Role:", style="Gold.TLabel").grid(row=2, column=0, padx=5, pady=2, sticky="W")
        self.user_role_combobox = ttk.Combobox(form_frame, values=["admin", "cashier"], state="readonly")
        self.user_role_combobox.grid(row=2, column=1, padx=5, pady=2)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        add_icon = self.load_icon(ICONS['add_user'])
        btn_add = ttk.Button(button_frame, text="Tambah Pengguna", command=self.add_user, image=add_icon, compound="left", bootstyle="success")
        btn_add.image = add_icon
        btn_add.pack(side=LEFT, padx=5)

        edit_icon = self.load_icon(ICONS['edit_user'])
        btn_edit = ttk.Button(button_frame, text="Perbarui", command=self.update_user, image=edit_icon, compound="left", bootstyle="warning")
        btn_edit.image = edit_icon
        btn_edit.pack(side=LEFT, padx=5)
        
        delete_icon = self.load_icon(ICONS['delete_user'])
        btn_delete = ttk.Button(button_frame, text="Hapus", command=self.delete_user, image=delete_icon, compound="left", bootstyle="danger")
        btn_delete.image = delete_icon
        btn_delete.pack(side=LEFT, padx=5)
        
        self.user_treeview = ttk.Treeview(self.content_frame, columns=("ID", "Username", "Role"), show='headings')
        self.user_treeview.heading("ID", text="ID")
        self.user_treeview.heading("Username", text="Username")
        self.user_treeview.heading("Role", text="Role")
        
        self.user_treeview.column("ID", width=50, anchor=CENTER)
        self.user_treeview.column("Username", width=250, anchor=W)
        self.user_treeview.column("Role", width=150, anchor=W)
        
        self.user_treeview.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.user_treeview.bind("<<TreeviewSelect>>", self.on_user_select)
        self.load_users_to_treeview()
        
    def load_users_to_treeview(self):
        for item in self.user_treeview.get_children():
            self.user_treeview.delete(item)
        users = self.db.get_users()
        for user in users:
            self.user_treeview.insert('', 'end', values=(user['id'], user['username'], user['role']))

    def add_user(self):
        username = self.user_username_entry.get()
        password = self.user_password_entry.get()
        role = self.user_role_combobox.get()
        
        if not all([username, password, role]):
            self.show_toast("Semua bidang harus diisi.", "danger")
            return
            
        if self.db.add_user(username, password, role):
            self.show_toast("Pengguna berhasil ditambahkan!", "success")
            self.load_users_to_treeview()
            self.clear_user_form()
        else:
            self.show_toast("Username sudah ada.", "danger")

    def update_user(self):
        selected_item = self.user_treeview.focus()
        if not selected_item:
            self.show_toast("Pilih pengguna yang ingin diperbarui.", "info")
            return
            
        user_id = self.user_treeview.item(selected_item)['values'][0]
        username = self.user_username_entry.get()
        password = self.user_password_entry.get()
        role = self.user_role_combobox.get()
        
        if not all([username, password, role]):
            self.show_toast("Semua bidang harus diisi.", "danger")
            return
            
        self.db.update_user(user_id, username, password, role)
        self.show_toast("Pengguna berhasil diperbarui!", "success")
        self.load_users_to_treeview()
        self.clear_user_form()

    def delete_user(self):
        selected_item = self.user_treeview.focus()
        if not selected_item:
            self.show_toast("Pilih pengguna yang ingin dihapus.", "info")
            return
        
        user_id = self.user_treeview.item(selected_item)['values'][0]
        if user_id == self.current_user['id']:
            self.show_toast("Anda tidak bisa menghapus akun Anda sendiri.", "danger")
            return
            
        if messagebox.askyesno("Konfirmasi Hapus", "Yakin ingin menghapus pengguna ini?"):
            self.db.delete_user(user_id)
            self.show_toast("Pengguna berhasil dihapus!", "success")
            self.load_users_to_treeview()
            self.clear_user_form()

    def on_user_select(self, event):
        selected_item = self.user_treeview.focus()
        if selected_item:
            item_data = self.user_treeview.item(selected_item)['values']
            user_id = item_data[0]
            user = self.db.get_user_by_id(user_id)
            if user:
                self.clear_user_form()
                self.user_username_entry.insert(0, user['username'])
                self.user_password_entry.insert(0, user['password'])
                self.user_role_combobox.set(user['role'])
                
    def clear_user_form(self):
        self.user_username_entry.delete(0, tk.END)
        self.user_password_entry.delete(0, tk.END)
        self.user_role_combobox.set('')
        
    # --- Halaman Kasir ---
    def show_cashier(self):
        self.clear_content_frame()
        
        main_frame = ttk.Frame(self.content_frame, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        products_frame = ttk.Frame(main_frame, style="TFrame")
        products_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        search_frame = ttk.Frame(products_frame, style="TFrame")
        search_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Smart Search:", font=("Inter", 12), style="Neon.TLabel").pack(side=LEFT, padx=(0, 5))
        self.cashier_search_entry = ttk.Entry(search_frame, width=40)
        self.cashier_search_entry.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)
        self.cashier_search_entry.bind("<KeyRelease>", self.filter_cashier_products)
        self.cashier_search_entry.bind("<F1>", lambda e: self.cashier_search_entry.focus())

        self.products_canvas = tk.Canvas(products_frame, bg="#1A1A1A", highlightbackground="#FFD700", highlightthickness=1)
        self.products_scrollbar = ttk.Scrollbar(products_frame, orient=VERTICAL, command=self.products_canvas.yview)
        self.scrollable_products_frame = ttk.Frame(self.products_canvas, style="TFrame")
        
        self.products_canvas.configure(yscrollcommand=self.products_scrollbar.set)
        
        self.products_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.products_scrollbar.pack(side=RIGHT, fill=Y)
        
        self.products_canvas.create_window((0, 0), window=self.scrollable_products_frame, anchor="nw")
        self.scrollable_products_frame.bind("<Configure>", lambda e: self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all")))
        
        cart_frame = ttk.Frame(main_frame, width=400, style="primary.TFrame", padding=10)
        cart_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        ttk.Label(cart_frame, text="Keranjang Belanja", font=("Inter", 16, "bold"), bootstyle="inverse").pack(pady=10)
        
        cart_columns = ("Nama", "Qty", "Subtotal")
        self.cart_treeview = ttk.Treeview(cart_frame, columns=cart_columns, show='headings')
        self.cart_treeview.column("Nama", width=150, anchor=W)
        self.cart_treeview.column("Qty", width=50, anchor=CENTER)
        self.cart_treeview.column("Subtotal", width=120, anchor=E)
        for col in cart_columns:
            self.cart_treeview.heading(col, text=col)
        self.cart_treeview.pack(fill=BOTH, expand=True, pady=(0, 10))
        self.cart_treeview.bind("<Double-1>", self.adjust_cart_item)
        
        ttk.Separator(cart_frame, orient=HORIZONTAL, bootstyle="warning").pack(fill=X, pady=10)
        
        total_frame = ttk.Frame(cart_frame, style="info.TFrame", padding=10)
        total_frame.pack(fill=X)
        ttk.Label(total_frame, text="TOTAL BELANJA", font=("Inter", 14, "bold"), bootstyle="inverse").pack()
        self.total_label = ttk.Label(total_frame, text="Rp0", font=("Inter", 24, "bold"), bootstyle="inverse")
        self.total_label.pack(pady=5)
        
        payment_frame = ttk.Frame(cart_frame)
        payment_frame.pack(pady=10)
        ttk.Label(payment_frame, text="Metode Pembayaran:").pack(side=LEFT)
        self.payment_method = ttk.Combobox(payment_frame, values=["Tunai", "Debit", "Transfer Bank"], state="readonly")
        self.payment_method.set("Tunai")
        self.payment_method.pack(side=LEFT)

        ttk.Button(cart_frame, text="Bayar & Cetak Struk", bootstyle="success", command=self.pay_and_print).pack(pady=(20, 5), fill=X)
        ttk.Button(cart_frame, text="Batalkan Transaksi", bootstyle="danger", command=self.clear_cart).pack(pady=5, fill=X)
        
        self.cart_items = {}
        self.cashier_products = self.db.get_products()
        self.load_cashier_products()
        self.update_cart_display()

        # Keyboard shortcuts
        self.bind("<F1>", lambda e: self.cashier_search_entry.focus())
        self.bind("<F2>", lambda e: self.pay_and_print())

    def filter_cashier_products(self, event=None):
        """Memfilter produk di halaman kasir berdasarkan pencarian."""
        query = self.cashier_search_entry.get()
        self.cashier_products = self.db.get_products(query)
        self.load_cashier_products()

    def load_cashier_products(self):
        """Memuat produk ke dalam tampilan kartu di halaman kasir."""
        for widget in self.scrollable_products_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        max_cols = 4
        for product in self.cashier_products:
            self.create_product_card(self.scrollable_products_frame, product, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_product_card(self, parent_frame, product, row, col):
        """Membuat widget kartu untuk produk dengan tata letak grid."""
        card = ttk.Frame(parent_frame, style="info.TFrame", padding=10, relief="solid", borderwidth=1, cursor="hand2")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent_frame.columnconfigure(col, weight=1)
        
        ttk.Label(card, text=product['name'], font=("Inter", 12, "bold"), style="info.TLabel").pack(pady=(0, 5))
        ttk.Label(card, text=f"Rp{product['price']:,.0f}", font=("Inter", 10, "bold"), style="info.TLabel").pack()
        ttk.Label(card, text=f"Stok: {product['stock']}", font=("Inter", 8, "italic"), style="info.TLabel").pack()
        
        card.bind("<Button-1>", lambda e, p=product: self.add_to_cart_by_click(p))
        for widget in card.winfo_children():
            widget.bind("<Button-1>", lambda e, p=product: self.add_to_cart_by_click(p))

    def add_to_cart_by_click(self, product):
        """Menambahkan produk ke keranjang belanja saat kartu diklik."""
        if product['stock'] > 0:
            sku = product['sku']
            if sku in self.cart_items:
                self.cart_items[sku]['qty'] += 1
            else:
                self.cart_items[sku] = {
                    'name': product['name'],
                    'price': product['price'],
                    'hpp': product['hpp'],
                    'qty': 1,
                    'sku': product['sku']
                }
            self.update_cart_display()
            self.show_toast(f"Ditambahkan: {product['name']}", "success")
        else:
            self.show_toast("Stok habis!", "danger")
        
    def adjust_cart_item(self, event):
        """Mengubah kuantitas item di keranjang belanja."""
        selected_item = self.cart_treeview.focus()
        if not selected_item:
            return

        item_data = self.cart_treeview.item(selected_item)['values']
        item_name = item_data[0]
        
        sku_to_adjust = next((s for s, item in self.cart_items.items() if item['name'] == item_name), None)
        if not sku_to_adjust:
            return

        current_qty = self.cart_items[sku_to_adjust]['qty']
        
        new_qty = simpledialog.askinteger("Ubah Kuantitas", f"Ubah kuantitas untuk {item_name}:", initialvalue=current_qty)
        
        if new_qty is not None:
            if new_qty <= 0:
                del self.cart_items[sku_to_adjust]
                self.show_toast("Item dihapus dari keranjang.", "info")
            else:
                self.cart_items[sku_to_adjust]['qty'] = new_qty
                self.show_toast("Kuantitas diperbarui.", "success")
            self.update_cart_display()

    def update_cart_display(self):
        """Memperbarui tampilan keranjang belanja."""
        for item in self.cart_treeview.get_children():
            self.cart_treeview.delete(item)
        
        total = 0
        for sku, item in self.cart_items.items():
            subtotal = item['price'] * item['qty']
            total += subtotal
            self.cart_treeview.insert('', 'end', values=(item['name'], item['qty'], f"Rp{subtotal:,.0f}"))
        
        self.total_label.config(text=f"Rp{total:,.0f}")

    def clear_cart(self):
        """Mengosongkan keranjang belanja."""
        if messagebox.askyesno("Konfirmasi", "Yakin ingin membatalkan transaksi ini?"):
            self.cart_items = {}
            self.update_cart_display()
            self.show_toast("Transaksi dibatalkan. Keranjang kosong.", "info")

    def pay_and_print(self):
        """Memproses pembayaran, mencatat penjualan, dan mencetak struk."""
        if not self.cart_items:
            self.show_toast("Keranjang kosong, tidak bisa memproses pembayaran.", "danger")
            return

        total_amount = sum(item['price'] * item['qty'] for item in self.cart_items.values())
        payment_method = self.payment_method.get()
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        for sku, item in self.cart_items.items():
            self.db.add_sale(
                transaction_id,
                item['sku'],
                item['name'],
                item['qty'],
                item['price'],
                item['hpp'],
                payment_method,
                timestamp
            )
            self.db.update_product_stock(item['sku'], -item['qty'])
        
        self.print_receipt(self.cart_items, total_amount, payment_method, transaction_id)
        self.clear_cart()
        self.show_toast("Pembayaran berhasil dan struk dicetak!", "success")

    def print_receipt(self, items, total, payment_method, transaction_id):
        """Mencetak struk penjualan (PDF fallback)."""
        filename = f"struk_{transaction_id}.pdf"
        try:
            c = pdf_canvas.Canvas(filename, pagesize=(58*mm, 210*mm))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(10*mm, 195*mm, "TOKO MAJU JAYA")
            c.setFont("Helvetica", 8)
            c.drawString(10*mm, 190*mm, "Jl. Contoh No. 123, Kota")
            c.drawString(10*mm, 185*mm, "------------------------------------")

            y_pos = 180*mm
            for item in items.values():
                c.drawString(10*mm, y_pos, f"{item['name']}")
                c.drawString(10*mm, y_pos - 4, f"{item['qty']} x Rp{item['price']:,.0f}")
                subtotal = item['price'] * item['qty']
                c.drawString(45*mm, y_pos - 4, f"Rp{subtotal:,.0f}")
                y_pos -= 10
            
            c.drawString(10*mm, y_pos, "------------------------------------")
            y_pos -= 5
            c.setFont("Helvetica-Bold", 10)
            c.drawString(10*mm, y_pos, "TOTAL:")
            c.drawString(45*mm, y_pos, f"Rp{total:,.0f}")
            
            c.drawString(10*mm, y_pos - 10, f"Pembayaran: {payment_method}")

            c.showPage()
            c.save()
            self.show_toast(f"Struk berhasil dicetak sebagai {filename}", "success")
        except Exception as e:
            self.show_toast(f"Gagal mencetak struk: {e}", "danger")

    # --- Fitur Manajemen Shift ---
    def end_shift_dialog(self):
        """Menampilkan dialog untuk setoran akhir shift."""
        dialog = ttk.Toplevel(self)
        dialog.title("Akhiri Shift")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        dialog_frame = ttk.Frame(dialog, padding=20)
        dialog_frame.pack(fill=BOTH, expand=True)

        ttk.Label(dialog_frame, text="Setoran Akhir Shift", font=("Inter", 14, "bold"), bootstyle="inverse").pack(pady=10)
        ttk.Label(dialog_frame, text="Masukkan jumlah uang setoran tanpa melihat laporan.", bootstyle="inverse").pack()
        
        ttk.Label(dialog_frame, text="Jumlah Setoran Tunai:", bootstyle="inverse").pack(pady=(10, 0))
        self.blind_deposit_entry = ttk.Entry(dialog_frame, width=30)
        self.blind_deposit_entry.pack(pady=5)
        
        ttk.Button(dialog_frame, text="Simpan Setoran", bootstyle="success", command=lambda: self.save_blind_deposit(dialog)).pack(pady=10)
        
    def save_blind_deposit(self, dialog):
        """Menyimpan setoran buta dan membandingkannya dengan penjualan aktual."""
        try:
            blind_amount = float(self.blind_deposit_entry.get())
            
            total_cash_sales = 0
            sales = self.db.get_sales_report()
            for sale in sales:
                if sale['payment_method'] == 'Tunai':
                    total_cash_sales += sale['price'] * sale['quantity']
            
            discrepancy = blind_amount - total_cash_sales
            
            self.db.add_deposit(
                self.current_user['id'],
                self.shift_start_time.isoformat(),
                datetime.datetime.now().isoformat(),
                blind_amount,
                total_cash_sales,
                discrepancy
            )

            dialog.destroy()
            self.show_toast(f"Setoran berhasil disimpan. Selisih: Rp{discrepancy:,.0f}", "success")
            self.shift_start_time = datetime.datetime.now() # Reset shift
        except ValueError:
            self.show_toast("Jumlah setoran tidak valid.", "danger")
            
    # --- Halaman Laporan Penjualan ---
    def show_sales_report(self):
        self.clear_content_frame()
        
        header_frame = ttk.Frame(self.content_frame, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Laporan Penjualan", font=("Inter", 24, "bold"), foreground="#39FF14").pack(side=LEFT)
        
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=RIGHT)
        export_icon = self.load_icon(ICONS['export'])
        ttk.Button(button_frame, text="Ekspor ke Excel/CSV", command=self.export_sales_report, image=export_icon, compound="left", bootstyle="warning").pack(side=LEFT, padx=5)

        recap_frame = ttk.Frame(self.content_frame, padding=10)
        recap_frame.pack(fill=X)
        
        ttk.Label(recap_frame, text="Rekap Penjualan per Metode Pembayaran", font=("Inter", 14, "bold")).pack()
        
        recap_tree = ttk.Treeview(recap_frame, columns=("Metode", "Total Penjualan", "Total Keuntungan"), show='headings')
        recap_tree.heading("Metode", text="Metode Pembayaran")
        recap_tree.heading("Total Penjualan", text="Total Penjualan")
        recap_tree.heading("Total Keuntungan", text="Total Keuntungan")
        
        recap_tree.column("Metode", width=200, anchor=W)
        recap_tree.column("Total Penjualan", width=200, anchor=E)
        recap_tree.column("Total Keuntungan", width=200, anchor=E)
        
        recap_tree.pack(fill=X, pady=10)
        
        sales_recap = self.db.get_sales_by_payment_method()
        for row in sales_recap:
            recap_tree.insert('', 'end', values=(
                row['payment_method'],
                f"Rp{row['total_sales']:,.0f}",
                f"Rp{row['total_profit']:,.0f}"
            ))

        ttk.Separator(self.content_frame, orient=HORIZONTAL, bootstyle="warning").pack(fill=X, pady=10)
        
        ttk.Label(self.content_frame, text="Detail Penjualan", font=("Inter", 14, "bold")).pack(pady=(10, 0))
        
        sales_columns = ("ID Transaksi", "SKU", "Nama Produk", "Qty", "Harga", "Tanggal")
        sales_tree = ttk.Treeview(self.content_frame, columns=sales_columns, show='headings')
        
        sales_tree.heading("ID Transaksi", text="ID Transaksi")
        sales_tree.heading("SKU", text="SKU")
        sales_tree.heading("Nama Produk", text="Nama Produk")
        sales_tree.heading("Qty", text="Qty")
        sales_tree.heading("Harga", text="Harga")
        sales_tree.heading("Tanggal", text="Tanggal")
        
        sales_tree.column("ID Transaksi", width=150, anchor=W)
        sales_tree.column("SKU", width=100, anchor=W)
        sales_tree.column("Nama Produk", width=200, anchor=W)
        sales_tree.column("Qty", width=50, anchor=CENTER)
        sales_tree.column("Harga", width=100, anchor=E)
        sales_tree.column("Tanggal", width=150, anchor=W)
        
        sales_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        sales_data = self.db.get_sales_report()
        for row in sales_data:
            sales_tree.insert('', 'end', values=(
                row['transaction_id'][:8] + '...',
                row['product_sku'],
                row['product_name'],
                row['quantity'],
                f"Rp{row['price']:,.0f}",
                datetime.datetime.fromisoformat(row['sale_timestamp']).strftime('%Y-%m-%d %H:%M')
            ))
            
    def export_sales_report(self):
        sales_data = self.db.get_sales_report()
        if not sales_data:
            self.show_toast("Tidak ada data penjualan untuk diekspor.", "info")
            return
            
        df = pd.DataFrame(sales_data)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            initialfile=f"laporan_penjualan_{datetime.datetime.now().strftime('%Y-%m-%d')}"
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False)
                self.show_toast("Laporan berhasil diekspor!", "success")
            except Exception as e:
                self.show_toast(f"Gagal mengekspor laporan: {e}", "danger")

    # --- Halaman Laporan Stok ---
    def show_stock_report(self):
        self.clear_content_frame()
        
        header_frame = ttk.Frame(self.content_frame, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Laporan Stok", font=("Inter", 24, "bold"), foreground="#39FF14").pack(side=LEFT)
        
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=RIGHT)
        export_icon = self.load_icon(ICONS['export'])
        ttk.Button(button_frame, text="Ekspor ke Excel/CSV", command=self.export_stock_report, image=export_icon, compound="left", bootstyle="warning").pack(side=LEFT, padx=5)

        stock_columns = ("SKU", "Nama Produk", "Stok Tersedia", "Kategori")
        stock_tree = ttk.Treeview(self.content_frame, columns=stock_columns, show='headings')
        
        stock_tree.heading("SKU", text="SKU")
        stock_tree.heading("Nama Produk", text="Nama Produk")
        stock_tree.heading("Stok Tersedia", text="Stok Tersedia")
        stock_tree.heading("Kategori", text="Kategori")
        
        stock_tree.column("SKU", width=100, anchor=W)
        stock_tree.column("Nama Produk", width=300, anchor=W)
        stock_tree.column("Stok Tersedia", width=150, anchor=CENTER)
        stock_tree.column("Kategori", width=200, anchor=W)
        
        stock_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        products = self.db.get_products()
        for product in products:
            stock_tree.insert('', 'end', values=(
                product['sku'],
                product['name'],
                product['stock'],
                product['category'] or 'Tidak ada'
            ))

    def export_stock_report(self):
        stock_data = self.db.get_products()
        if not stock_data:
            self.show_toast("Tidak ada data stok untuk diekspor.", "info")
            return
            
        df = pd.DataFrame(stock_data)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            initialfile=f"laporan_stok_{datetime.datetime.now().strftime('%Y-%m-%d')}"
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False)
                self.show_toast("Laporan berhasil diekspor!", "success")
            except Exception as e:
                self.show_toast(f"Gagal mengekspor laporan: {e}", "danger")

    # --- Halaman Manajemen Produk (seperti sebelumnya, hanya UI diubah) ---
    def show_product_management(self):
        self.clear_content_frame()
        
        header_frame = ttk.Frame(self.content_frame, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Manajemen Produk", font=("Inter", 24, "bold"), foreground="#39FF14").pack(side=LEFT)

        form_frame = ttk.Frame(self.content_frame, padding=10)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="SKU", style="Gold.TLabel").grid(row=0, column=0, sticky=W, padx=5, pady=2)
        self.sku_entry = ttk.Entry(form_frame, width=30)
        self.sku_entry.grid(row=0, column=1, sticky=W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Nama Produk", style="Gold.TLabel").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=1, column=1, sticky=W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Harga Jual", style="Gold.TLabel").grid(row=0, column=2, sticky=W, padx=5, pady=2)
        self.price_entry = ttk.Entry(form_frame, width=30)
        self.price_entry.grid(row=0, column=3, sticky=W, padx=5, pady=2)

        ttk.Label(form_frame, text="Harga Pokok (HPP)", style="Gold.TLabel").grid(row=1, column=2, sticky=W, padx=5, pady=2)
        self.hpp_entry = ttk.Entry(form_frame, width=30)
        self.hpp_entry.grid(row=1, column=3, sticky=W, padx=5, pady=2)

        ttk.Label(form_frame, text="Stok", style="Gold.TLabel").grid(row=0, column=4, sticky=W, padx=5, pady=2)
        self.stock_entry = ttk.Entry(form_frame, width=30)
        self.stock_entry.grid(row=0, column=5, sticky=W, padx=5, pady=2)

        ttk.Label(form_frame, text="Deskripsi", style="Gold.TLabel").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.desc_entry = ttk.Entry(form_frame, width=75)
        self.desc_entry.grid(row=2, column=1, columnspan=3, sticky=W, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Kategori", style="Gold.TLabel").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        categories = self.db.get_categories()
        cat_names = [c['name'] for c in categories]
        self.cat_combobox = ttk.Combobox(form_frame, values=cat_names)
        self.cat_combobox.grid(row=3, column=1, sticky=W, padx=5, pady=2)
        
        button_frame = ttk.Frame(self.content_frame, padding=10)
        button_frame.pack(fill=X, padx=10)
        ttk.Button(button_frame, text="Tambah Produk", command=self.add_product, bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Perbarui Produk", command=self.update_product, bootstyle="warning").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Produk", command=self.delete_product, bootstyle="danger").pack(side=LEFT, padx=5)
        
        search_frame = ttk.Frame(self.content_frame, padding=10)
        search_frame.pack(fill=X, padx=10)
        ttk.Label(search_frame, text="Cari Produk:", style="Neon.TLabel").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_products)

        columns = ("SKU", "Nama Produk", "Harga Jual", "Harga Pokok", "Stok", "Kategori")
        self.product_treeview = ttk.Treeview(self.content_frame, columns=columns, show='headings', selectmode="browse")
        
        self.product_treeview.heading("SKU", text="SKU")
        self.product_treeview.heading("Nama Produk", text="Nama Produk")
        self.product_treeview.heading("Harga Jual", text="Harga Jual")
        self.product_treeview.heading("Harga Pokok", text="Harga Pokok")
        self.product_treeview.heading("Stok", text="Stok")
        self.product_treeview.heading("Kategori", text="Kategori")
        
        self.product_treeview.column("SKU", width=100, anchor=W)
        self.product_treeview.column("Nama Produk", width=300, anchor=W)
        self.product_treeview.column("Harga Jual", width=120, anchor=E)
        self.product_treeview.column("Harga Pokok", width=120, anchor=E)
        self.product_treeview.column("Stok", width=80, anchor=CENTER)
        self.product_treeview.column("Kategori", width=150, anchor=W)
        
        self.product_treeview.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.product_treeview.bind("<<TreeviewSelect>>", self.on_product_select)
        self.load_products_to_treeview()

    def filter_products(self, event=None):
        query = self.search_entry.get()
        self.load_products_to_treeview(query)

    def add_product(self):
        sku = self.sku_entry.get()
        name = self.name_entry.get()
        price = self.price_entry.get()
        hpp = self.hpp_entry.get()
        stock = self.stock_entry.get()
        desc = self.desc_entry.get()
        cat_name = self.cat_combobox.get()
        
        if not all([sku, name, price, hpp, stock, cat_name]):
            self.show_toast("Semua bidang harus diisi!", "danger")
            return

        try:
            price = float(price)
            hpp = float(hpp)
            stock = int(stock)
            cat_id = next(c['id'] for c in self.db.get_categories() if c['name'] == cat_name)
            
            if self.db.add_product(sku, name, desc, price, hpp, stock, cat_id, None):
                self.show_toast("Produk berhasil ditambahkan!", "success")
                self.load_products_to_treeview()
            else:
                self.show_toast("SKU sudah ada!", "danger")
        except (ValueError, StopIteration):
            self.show_toast("Input tidak valid. Periksa Harga, Stok, dan Kategori.", "danger")
        self.clear_product_form()

    def update_product(self):
        selected_item = self.product_treeview.focus()
        if not selected_item:
            self.show_toast("Pilih produk yang ingin diperbarui.", "info")
            return
            
        sku_to_update = self.product_treeview.item(selected_item)['values'][0]
        name = self.name_entry.get()
        price = self.price_entry.get()
        hpp = self.hpp_entry.get()
        stock = self.stock_entry.get()
        desc = self.desc_entry.get()
        cat_name = self.cat_combobox.get()
        
        if not all([name, price, hpp, stock, cat_name]):
            self.show_toast("Semua bidang harus diisi!", "danger")
            return
            
        try:
            price = float(price)
            hpp = float(hpp)
            stock = int(stock)
            cat_id = next(c['id'] for c in self.db.get_categories() if c['name'] == cat_name)
            self.db.update_product(sku_to_update, name, desc, price, hpp, stock, cat_id, None)
            self.show_toast("Produk berhasil diperbarui!", "success")
            self.load_products_to_treeview()
        except (ValueError, StopIteration):
            self.show_toast("Input tidak valid. Periksa Harga, HPP, Stok, dan Kategori.", "danger")
        self.clear_product_form()

    def delete_product(self):
        selected_item = self.product_treeview.focus()
        if not selected_item:
            self.show_toast("Pilih produk yang ingin dihapus.", "info")
            return
        
        sku_to_delete = self.product_treeview.item(selected_item)['values'][0]
        if messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus produk dengan SKU {sku_to_delete}?"):
            self.db.delete_product(sku_to_delete)
            self.show_toast("Produk berhasil dihapus!", "success")
            self.load_products_to_treeview()
            self.clear_product_form()

    def on_product_select(self, event):
        selected_item = self.product_treeview.focus()
        if selected_item:
            item_data = self.product_treeview.item(selected_item)['values']
            sku = item_data[0]
            product = self.db.get_product_by_sku(sku)
            if product:
                self.clear_product_form()
                self.sku_entry.insert(0, product['sku'])
                self.name_entry.insert(0, product['name'])
                self.price_entry.insert(0, str(product['price']))
                self.hpp_entry.insert(0, str(product['hpp']))
                self.stock_entry.insert(0, str(product['stock']))
                self.desc_entry.insert(0, product['description'])
                cat_name = next((c['name'] for c in self.db.get_categories() if c['id'] == product['category_id']), '')
                self.cat_combobox.set(cat_name)

    def clear_product_form(self):
        self.sku_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.hpp_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.cat_combobox.set('')

    def load_products_to_treeview(self, query=""):
        for item in self.product_treeview.get_children():
            self.product_treeview.delete(item)
        products = self.db.get_products(query)
        for product in products:
            self.product_treeview.insert('', 'end', values=(
                product['sku'],
                product['name'],
                f"Rp{product['price']:,.0f}",
                f"Rp{product['hpp']:,.0f}",
                product['stock'],
                product['category'] or 'Tidak ada'
            ))

    def show_category_management(self):
        self.clear_content_frame()
        
        header_frame = ttk.Frame(self.content_frame, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Manajemen Kategori", font=("Inter", 24, "bold"), foreground="#39FF14").pack(side=LEFT)
        
        form_frame = ttk.Frame(self.content_frame, padding=10)
        form_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nama Kategori", style="Gold.TLabel").grid(row=0, column=0, padx=5, pady=2)
        self.cat_name_entry = ttk.Entry(form_frame, width=30)
        self.cat_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="URL Ikon", style="Gold.TLabel").grid(row=1, column=0, padx=5, pady=2)
        self.cat_icon_url_entry = ttk.Entry(form_frame, width=30)
        self.cat_icon_url_entry.grid(row=1, column=1, padx=5, pady=2)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Tambah Kategori", command=self.add_category, bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Kategori", command=self.delete_category, bootstyle="danger").pack(side=LEFT, padx=5)
        
        cat_columns = ("Nama", "URL Ikon")
        self.cat_treeview = ttk.Treeview(self.content_frame, columns=cat_columns, show='headings')
        
        self.cat_treeview.heading("Nama", text="Nama")
        self.cat_treeview.heading("URL Ikon", text="URL Ikon")
        
        self.cat_treeview.column("Nama", width=200, anchor=W)
        self.cat_treeview.column("URL Ikon", width=400, anchor=W)
        
        self.cat_treeview.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.load_categories_to_treeview()

    def add_category(self):
        name = self.cat_name_entry.get()
        url = self.cat_icon_url_entry.get()
        
        if not name:
            self.show_toast("Nama kategori harus diisi!", "danger")
            return
            
        if self.db.add_category(name, url):
            self.show_toast("Kategori berhasil ditambahkan!", "success")
            self.cat_name_entry.delete(0, tk.END)
            self.cat_icon_url_entry.delete(0, tk.END)
            self.load_categories_to_treeview()
        else:
            self.show_toast("Nama kategori sudah ada!", "danger")
            
    def delete_category(self):
        selected_item = self.cat_treeview.focus()
        if not selected_item:
            self.show_toast("Pilih kategori yang ingin dihapus.", "info")
            return
        
        cat_name_to_delete = self.cat_treeview.item(selected_item)['values'][0]
        if messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus kategori '{cat_name_to_delete}'? Produk terkait tidak akan memiliki kategori lagi."):
            self.db.delete_category(cat_name_to_delete)
            self.show_toast("Kategori berhasil dihapus!", "success")
            self.load_categories_to_treeview()

    def load_categories_to_treeview(self):
        for item in self.cat_treeview.get_children():
            self.cat_treeview.delete(item)
        categories = self.db.get_categories_with_urls()
        for cat in categories:
            self.cat_treeview.insert('', 'end', values=(cat['name'], cat['icon_url']))

def main():
    db_manager = DatabaseManager()
    app = BillingApp(db_manager)
    app.mainloop()

if __name__ == "__main__":
    main()
