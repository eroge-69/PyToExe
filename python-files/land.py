CREATE TABLE plots (
    plot_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    size REAL NOT NULL,
    location TEXT NOT NULL,
    price REAL NOT NULL,
    status TEXT DEFAULT 'available' CHECK(status IN ('available', 'reserved', 'sold', 'allocated'))
);

CREATE TABLE buyers (
    buyer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    national_id TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    email TEXT
);

CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    plot_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    sale_price REAL NOT NULL,
    deposit REAL NOT NULL,
    balance REAL NOT NULL,
    FOREIGN KEY (plot_id) REFERENCES plots(plot_id),
    FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_date DATE NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('Cash', 'Bank Transfer', 'M-Pesa', 'Cheque')),
    receipt_number TEXT UNIQUE,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
);
pip install tkcalendar sqlite3 pandas reportlab
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

class LandSaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kenyan Land Sale Tracker")
        self.conn = sqlite3.connect('land_sales.db')
        self.create_tables()
        self.create_ui()
    
    def create_tables(self):
        # Create database tables if they don't exist
        cursor = self.conn.cursor()
        # Execute table creation SQL here
        self.conn.commit()
    
    def create_ui(self):
        # Create main UI components
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_plot_tab()
        self.create_buyer_tab()
        self.create_sales_tab()
        self.create_payment_tab()
        self.create_report_tab()
    
    # Additional methods for each tab...