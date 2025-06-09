import json
import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
from pyzbar import pyzbar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CashierSoftware:
    def __init__(self):
        self.products = {}
        self.current_transaction = []
        self.users = {}
        self.discounts = {}
        self.db_conn = None
        self.current_user = None
        self.setup_database()
        self.load_data()
        
    def setup_database(self):
        """Set up SQLite database"""
        self.db_conn = sqlite3.connect('cashier_system.db')
        cursor = self.db_conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                barcode TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discounts (
                code TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                discount_type TEXT NOT NULL,
                value REAL NOT NULL,
                valid_until TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                total REAL NOT NULL,
                payment REAL NOT NULL,
                discount_code TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (discount_code) REFERENCES discounts(code)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS returns (
                return_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                total_refund REAL NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS return_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (return_id) REFERENCES returns(return_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        self.db_conn.commit()
        
        # Add admin user if none exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                ('admin', 'Administrator', 'admin123', 'admin')
            )
            self.db_conn.commit()
    
    def load_data(self):
        """Load data from database"""
        cursor = self.db_conn.cursor()
        
        # Load products
        cursor.execute("SELECT * FROM products")
        self.products = {
            row[0]: {
                'name': row[1],
                'price': row[2],
                'stock': row[3],
                'barcode': row[4]
            } for row in cursor.fetchall()
        }
        
        # Load users
        cursor.execute("SELECT * FROM users")
        self.users = {
            row[0]: {
                'name': row[1],
                'password': row[2],
                'role': row[3]
            } for row in cursor.fetchall()
        }
        
        # Load discounts
        cursor.execute("SELECT * FROM discounts")
        self.discounts = {
            row[0]: {
                'description': row[1],
                'discount_type': row[2],
                'value': row[3],
                'valid_until': row[4]
            } for row in cursor.fetchall()
        }
    
    def authenticate_user(self, user_id, password):
        """Authenticate user login"""
        if user_id in self.users and self.users[user_id]['password'] == password:
            self.current_user = user_id
            return True
        return False
    
    def add_product(self, product_id, name, price, stock, barcode=None):
        """Add a new product to inventory"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
                (product_id, name, price, stock, barcode)
            )
            self.db_conn.commit()
            self.products[product_id] = {
                'name': name,
                'price': price,
                'stock': stock,
                'barcode': barcode
            }
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_product(self, product_id, name=None, price=None, stock=None, barcode=None):
        """Update product information"""
        cursor = self.db_conn.cursor()
        product = self.products.get(product_id)
        if not product:
            return False
        
        # Only update fields that are provided
        if name is None: name = product['name']
        if price is None: price = product['price']
        if stock is None: stock = product['stock']
        if barcode is None: barcode = product['barcode']
        
        cursor.execute(
            "UPDATE products SET name=?, price=?, stock=?, barcode=? WHERE product_id=?",
            (name, price, stock, barcode, product_id)
        )
        self.db_conn.commit()
        
        # Update in-memory data
        self.products[product_id] = {
            'name': name,
            'price': price,
            'stock': stock,
            'barcode': barcode
        }
        return True
    
    def add_to_transaction(self, product_id, quantity):
        """Add an item to the current transaction"""
        if product_id not in self.products:
            return False, "Product not found!"
        
        if self.products[product_id]['stock'] < quantity:
            return False, f"Not enough stock! Only {self.products[product_id]['stock']} available."
        
        # Add to transaction
        self.current_transaction.append({
            'product_id': product_id,
            'name': self.products[product_id]['name'],
            'price': self.products[product_id]['price'],
            'quantity': quantity,
            'subtotal': self.products[product_id]['price'] * quantity
        })
        
        return True, "Item added to transaction"
    
    def apply_discount(self, discount_code):
        """Apply discount to current transaction"""
        if discount_code not in self.discounts:
            return False, "Invalid discount code"
        
        discount = self.discounts[discount_code]
        valid_until = datetime.strptime(discount['valid_until'], '%Y-%m-%d') if discount['valid_until'] else None
        
        if valid_until and valid_until < datetime.now():
            return False, "Discount code has expired"
        
        return True, discount
    
    def calculate_total(self):
        """Calculate total for current transaction"""
        subtotal = sum(item['subtotal'] for item in self.current_transaction)
        return subtotal
    
    def process_payment(self, payment_amount, discount_code=None):
        """Process payment and complete transaction"""
        if not self.current_transaction:
            return False, "No items in transaction"
        
        total = self.calculate_total()
        discount = None
        
        # Apply discount if provided
        if discount_code:
            valid, discount_info = self.apply_discount(discount_code)
            if valid:
                discount = discount_info
                if discount['discount_type'] == 'percentage':
                    total *= (1 - discount['value'] / 100)
                else:  # fixed amount
                    total -= discount['value']
                total = max(0, total)  # Ensure total doesn't go negative
        
        if payment_amount < total:
            return False, "Insufficient payment"
        
        # Record transaction in database
        cursor = self.db_conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert transaction
        cursor.execute(
            "INSERT INTO transactions (user_id, timestamp, total, payment, discount_code) VALUES (?, ?, ?, ?, ?)",
            (self.current_user, timestamp, total, payment_amount, discount_code if discount else None)
        )
        transaction_id = cursor.lastrowid
        
        # Insert transaction items
        for item in self.current_transaction:
            cursor.execute(
                "INSERT INTO transaction_items (transaction_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (transaction_id, item['product_id'], item['quantity'], item['price'])
            )
            
            # Update product stock
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                (item['quantity'], item['product_id'])
            )
        
        self.db_conn.commit()
        
        # Update in-memory data
        for item in self.current_transaction:
            self.products[item['product_id']]['stock'] -= item['quantity']
        
        # Generate receipt
        receipt = self.generate_receipt(transaction_id, total, payment_amount, discount)
        
        # Clear current transaction
        self.current_transaction = []
        
        return True, receipt
    
    def generate_receipt(self, transaction_id, total, payment_amount, discount=None):
        """Generate receipt text"""
        receipt_lines = [
            "=== RECEIPT ===",
            f"Transaction ID: {transaction_id}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Cashier: {self.users[self.current_user]['name']}",
            "-" * 40
        ]
        
        for item in self.current_transaction:
            receipt_lines.append(
                f"{item['name']} x{item['quantity']} @ ${item['price']:.2f}: ${item['subtotal']:.2f}"
            )
        
        receipt_lines.append("-" * 40)
        
        if discount:
            if discount['discount_type'] == 'percentage':
                discount_text = f"{discount['value']}% off"
            else:
                discount_text = f"${discount['value']:.2f} off"
            receipt_lines.append(f"Discount Applied ({discount['description']}): {discount_text}")
        
        receipt_lines.extend([
            f"TOTAL: ${total:.2f}",
            f"PAID: ${payment_amount:.2f}",
            f"CHANGE: ${(payment_amount - total):.2f}",
            "Thank you for shopping with us!",
            "=" * 40
        ])
        
        # Save receipt to file
        receipt_filename = f"receipt_{transaction_id}.txt"
        with open(receipt_filename, 'w') as f:
            f.write("\n".join(receipt_lines))
        
        return "\n".join(receipt_lines)
    
    def process_return(self, transaction_id, items_to_return):
        """Process a return for items from a transaction"""
        cursor = self.db_conn.cursor()
        
        # Verify transaction exists
        cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
        transaction = cursor.fetchone()
        if not transaction:
            return False, "Transaction not found"
        
        # Get original transaction items
        cursor.execute(
            "SELECT product_id, quantity, price FROM transaction_items WHERE transaction_id = ?",
            (transaction_id,)
        )
        original_items = {row[0]: {'quantity': row[1], 'price': row[2]} for row in cursor.fetchall()}
        
        # Validate items to return
        return_items = []
        total_refund = 0
        
        for product_id, quantity in items_to_return.items():
            if product_id not in original_items:
                return False, f"Product {product_id} not in original transaction"
            
            if quantity > original_items[product_id]['quantity']:
                return False, f"Cannot return more than purchased for product {product_id}"
            
            return_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': original_items[product_id]['price'],
                'subtotal': quantity * original_items[product_id]['price']
            })
            total_refund += quantity * original_items[product_id]['price']
        
        # Record return in database
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert return record
        cursor.execute(
            "INSERT INTO returns (transaction_id, user_id, timestamp, total_refund) VALUES (?, ?, ?, ?)",
            (transaction_id, self.current_user, timestamp, total_refund)
        )
        return_id = cursor.lastrowid
        
        # Insert return items
        for item in return_items:
            cursor.execute(
                "INSERT INTO return_items (return_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (return_id, item['product_id'], item['quantity'], item['price'])
            )
            
            # Update product stock
            cursor.execute(
                "UPDATE products SET stock = stock + ? WHERE product_id = ?",
                (item['quantity'], item['product_id'])
            )
        
        self.db_conn.commit()
        
        # Update in-memory data
        for item in return_items:
            self.products[item['product_id']]['stock'] += item['quantity']
        
        return True, {
            'return_id': return_id,
            'total_refund': total_refund,
            'items': return_items
        }
    
    def generate_sales_report(self, start_date=None, end_date=None):
        """Generate sales report for a date range"""
        cursor = self.db_conn.cursor()
        
        query = """
            SELECT t.timestamp, t.transaction_id, u.name as cashier, 
                   SUM(ti.quantity * ti.price) as subtotal, t.discount_code,
                   t.total, t.payment
            FROM transactions t
            JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
            JOIN users u ON t.user_id = u.user_id
        """
        params = []
        
        if start_date and end_date:
            query += " WHERE t.timestamp BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif start_date:
            query += " WHERE t.timestamp >= ?"
            params.append(start_date)
        elif end_date:
            query += " WHERE t.timestamp <= ?"
            params.append(end_date)
        
        query += " GROUP BY t.transaction_id ORDER BY t.timestamp"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        # Get top selling products
        product_query = """
            SELECT p.name, SUM(ti.quantity) as total_quantity, 
                   SUM(ti.quantity * ti.price) as total_sales
            FROM transaction_items ti
            JOIN products p ON ti.product_id = p.product_id
            JOIN transactions t ON ti.transaction_id = t.transaction_id
        """
        product_params = []
        
        if start_date and end_date:
            product_query += " WHERE t.timestamp BETWEEN ? AND ?"
            product_params.extend([start_date, end_date])
        elif start_date:
            product_query += " WHERE t.timestamp >= ?"
            product_params.append(start_date)
        elif end_date:
            product_query += " WHERE t.timestamp <= ?"
            product_params.append(end_date)
        
        product_query += " GROUP BY ti.product_id ORDER BY total_quantity DESC LIMIT 10"
        
        cursor.execute(product_query, product_params)
        top_products = cursor.fetchall()
        
        # Calculate totals
        total_sales = sum(t[5] for t in transactions)
        total_transactions = len(transactions)
        avg_sale = total_sales / total_transactions if total_transactions else 0
        
        report = {
            'start_date': start_date,
            'end_date': end_date,
            'transactions': transactions,
            'top_products': top_products,
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'avg_sale': avg_sale
        }
        
        return report

class CashierApp:
    def __init__(self, root, cashier_system):
        self.root = root
        self.cashier_system = cashier_system
        self.root.title("Cashier System")
        self.root.geometry("1200x800")
        
        # Login frame
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(pady=100)
        
        ttk.Label(self.login_frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        self.user_id_entry = ttk.Entry(self.login_frame)
        self.user_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.handle_login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Main application frame (initially hidden)
        self.main_frame = ttk.Frame(self.root)
        
        # Set up main interface after successful login
        self.setup_main_interface()
        
        # Barcode scanner setup
        self.barcode_scanner_active = False
        self.cap = None
        
        # Start with login frame
        self.show_login()
    
    def show_login(self):
        """Show login frame and hide main frame"""
        self.main_frame.pack_forget()
        self.login_frame.pack(pady=100)
        self.user_id_entry.focus()
    
    def show_main(self):
        """Show main frame and hide login frame"""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def handle_login(self):
        """Handle user login"""
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()
        
        if self.cashier_system.authenticate_user(user_id, password):
            self.show_main()
            self.update_status(f"Logged in as {self.cashier_system.users[user_id]['name']}")
        else:
            messagebox.showerror("Login Failed", "Invalid user ID or password")
    
    def setup_main_interface(self):
        """Set up the main application interface"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Point of Sale tab
        self.pos_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pos_tab, text="Point of Sale")
        self.setup_pos_tab()
        
        # Inventory tab
        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.setup_inventory_tab()
        
        # Reports tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        self.setup_reports_tab()
        
        # Admin tab (only for admin users)
        self.admin_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_tab, text="Admin", state='hidden')
        self.setup_admin_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Logout button
        self.logout_button = ttk.Button(self.main_frame, text="Logout", command=self.show_login)
        self.logout_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def setup_pos_tab(self):
        """Set up Point of Sale tab"""
        # Left frame for product selection
        left_frame = ttk.Frame(self.pos_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Product search
        ttk.Label(left_frame, text="Search Products:").pack(pady=5)
        self.product_search_entry = ttk.Entry(left_frame)
        self.product_search_entry.pack(fill=tk.X, pady=5)
        self.product_search_entry.bind('<KeyRelease>', self.search_products)
        
        # Product list
        self.product_tree = ttk.Treeview(left_frame, columns=('id', 'name', 'price', 'stock'), show='headings')
        self.product_tree.heading('id', text='ID')
        self.product_tree.heading('name', text='Name')
        self.product_tree.heading('price', text='Price')
        self.product_tree.heading('stock', text='Stock')
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        self.product_tree.bind('<Double-1>', self.add_selected_product)
        
        # Barcode scanner button
        self.barcode_button = ttk.Button(left_frame, text="Scan Barcode", command=self.toggle_barcode_scanner)
        self.barcode_button.pack(pady=5)
        
        # Right frame for transaction
        right_frame = ttk.Frame(self.pos_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Current transaction
        ttk.Label(right_frame, text="Current Transaction:").pack(pady=5)
        self.transaction_tree = ttk.Treeview(right_frame, columns=('name', 'price', 'quantity', 'subtotal'), show='headings')
        self.transaction_tree.heading('name', text='Name')
        self.transaction_tree.heading('price', text='Price')
        self.transaction_tree.heading('quantity', text='Qty')
        self.transaction_tree.heading('subtotal', text='Subtotal')
        self.transaction_tree.pack(fill=tk.BOTH, expand=True)
        
        # Remove item button
        self.remove_item_button = ttk.Button(right_frame, text="Remove Selected", command=self.remove_selected_item)
        self.remove_item_button.pack(pady=5)
        
        # Transaction summary
        summary_frame = ttk.Frame(right_frame)
        summary_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(summary_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.E)
        self.subtotal_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, textvariable=self.subtotal_var).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Discount:").grid(row=1, column=0, sticky=tk.E)
        self.discount_entry = ttk.Entry(summary_frame, width=15)
        self.discount_entry.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Total:").grid(row=2, column=0, sticky=tk.E)
        self.total_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, textvariable=self.total_var).grid(row=2, column=1, sticky=tk.W)
        
        # Payment buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.cash_button = ttk.Button(button_frame, text="Cash Payment", command=lambda: self.process_payment('cash'))
        self.cash_button.pack(side=tk.LEFT, padx=5)
        
        self.card_button = ttk.Button(button_frame, text="Card Payment", command=lambda: self.process_payment('card'))
        self.card_button.pack(side=tk.LEFT, padx=5)
        
        # Load products
        self.refresh_product_list()
    
    def toggle_barcode_scanner(self):
        """Toggle barcode scanner on/off"""
        if not self.barcode_scanner_active:
            # Start scanner
            self.barcode_scanner_active = True
            self.barcode_button.config(text="Stop Scanner")
            self.cap = cv2.VideoCapture(0)
            self.scan_barcode()
        else:
            # Stop scanner
            self.barcode_scanner_active = False
            self.barcode_button.config(text="Scan Barcode")
            if self.cap:
                self.cap.release()
                self.cap = None
    
    def scan_barcode(self):
        """Scan for barcodes in video feed"""
        if not self.barcode_scanner_active:
            return
        
        ret, frame = self.cap.read()
        if ret:
            # Find and decode barcodes
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                self.handle_barcode_scan(barcode_data)
                break  # Only process first barcode
            
            # Show the frame (optional)
            cv2.imshow('Barcode Scanner', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.toggle_barcode_scanner()
                cv2.destroyAllWindows()
                return
        
        # Continue scanning
        self.root.after(100, self.scan_barcode)
    
    def handle_barcode_scan(self, barcode_data):
        """Handle scanned barcode"""
        # Look for product with this barcode
        product_id = None
        for pid, product in self.cashier_system.products.items():
            if product['barcode'] == barcode_data:
                product_id = pid
                break
        
        if product_id:
            # Add to transaction
            self.add_product_to_transaction(product_id, 1)
        else:
            messagebox.showwarning("Barcode Not Found", f"No product found with barcode: {barcode_data}")
    
    def setup_inventory_tab(self):
        """Set up Inventory Management tab"""
        # Product list
        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=('id', 'name', 'price', 'stock', 'barcode'), show='headings')
        self.inventory_tree.heading('id', text='ID')
        self.inventory_tree.heading('name', text='Name')
        self.inventory_tree.heading('price', text='Price')
        self.inventory_tree.heading('stock', text='Stock')
        self.inventory_tree.heading('barcode', text='Barcode')
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.inventory_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_product_button = ttk.Button(button_frame, text="Add Product", command=self.show_add_product_dialog)
        self.add_product_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_product_button = ttk.Button(button_frame, text="Edit Product", command=self.show_edit_product_dialog)
        self.edit_product_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_inventory_button = ttk.Button(button_frame, text="Refresh", command=self.refresh_inventory)
        self.refresh_inventory_button.pack(side=tk.RIGHT, padx=5)
        
        # Load inventory
        self.refresh_inventory()
    
    def setup_reports_tab(self):
        """Set up Reports tab"""
        # Date range selection
        date_frame = ttk.Frame(self.reports_tab)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.start_date_entry = ttk.Entry(date_frame, width=10)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.end_date_entry = ttk.Entry(date_frame, width=10)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        
        self.generate_report_button = ttk.Button(date_frame, text="Generate Report", command=self.generate_report)
        self.generate_report_button.pack(side=tk.LEFT, padx=10)
        
        # Report display
        self.report_text = tk.Text(self.reports_tab, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.reports_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_admin_tab(self):
        """Set up Admin tab"""
        # Notebook for admin sections
        admin_notebook = ttk.Notebook(self.admin_tab)
        admin_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Users section
        users_tab = ttk.Frame(admin_notebook)
        admin_notebook.add(users_tab, text="Users")
        
        self.users_tree = ttk.Treeview(users_tab, columns=('id', 'name', 'role'), show='headings')
        self.users_tree.heading('id', text='User ID')
        self.users_tree.heading('name', text='Name')
        self.users_tree.heading('role', text='Role')
        self.users_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(users_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_user_button = ttk.Button(button_frame, text="Add User", command=self.show_add_user_dialog)
        self.add_user_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_user_button = ttk.Button(button_frame, text="Edit User", command=self.show_edit_user_dialog)
        self.edit_user_button.pack(side=tk.LEFT, padx=5)
        
        # Discounts section
        discounts_tab = ttk.Frame(admin_notebook)
        admin_notebook.add(discounts_tab, text="Discounts")
        
        self.discounts_tree = ttk.Treeview(discounts_tab, columns=('code', 'description', 'type', 'value', 'valid_until'), show='headings')
        self.discounts_tree.heading('code', text='Code')
        self.discounts_tree.heading('description', text='Description')
        self.discounts_tree.heading('type', text='Type')
        self.discounts_tree.heading('value', text='Value')
        self.discounts_tree.heading('valid_until', text='Valid Until')
        self.discounts_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(discounts_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_discount_button = ttk.Button(button_frame, text="Add Discount", command=self.show_add_discount_dialog)
        self.add_discount_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_discount_button = ttk.Button(button_frame, text="Edit Discount", command=self.show_edit_discount_dialog)
        self.edit_discount_button.pack(side=tk.LEFT, padx=5)
        
        # Returns section
        returns_tab = ttk.Frame(admin_notebook)
        admin_notebook.add(returns_tab, text="Returns")
        
        self.returns_tree = ttk.Treeview(returns_tab, columns=('id', 'transaction_id', 'date', 'amount'), show='headings')
        self.returns_tree.heading('id', text='Return ID')
        self.returns_tree.heading('transaction_id', text='Original Transaction')
        self.returns_tree.heading('date', text='Date')
        self.returns_tree.heading('amount', text='Amount')
        self.returns_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.process_return_button = ttk.Button(returns_tab, text="Process Return", command=self.show_process_return_dialog)
        self.process_return_button.pack(pady=5)
        
        # Load admin data
        self.refresh_admin_data()
    
    def refresh_admin_data(self):
        """Refresh all admin data"""
        self.refresh_users_list()
        self.refresh_discounts_list()
        self.refresh_returns_list()
    
    def refresh_users_list(self):
        """Refresh the users list in admin tab"""
        self.users_tree.delete(*self.users_tree.get_children())
        for user_id, user in self.cashier_system.users.items():
            self.users_tree.insert('', 'end', values=(user_id, user['name'], user['role']))
    
    def refresh_discounts_list(self):
        """Refresh the discounts list in admin tab"""
        self.discounts_tree.delete(*self.discounts_tree.get_children())
        for code, discount in self.cashier_system.discounts.items():
            self.discounts_tree.insert('', 'end', values=(
                code, 
                discount['description'], 
                discount['discount_type'], 
                discount['value'], 
                discount['valid_until'] or 'N/A'
            ))
    
    def refresh_returns_list(self):
        """Refresh the returns list in admin tab"""
        self.returns_tree.delete(*self.returns_tree.get_children())
        cursor = self.cashier_system.db_conn.cursor()
        cursor.execute("""
            SELECT r.return_id, r.transaction_id, r.timestamp, r.total_refund
            FROM returns r
            ORDER BY r.timestamp DESC
        """)
        for row in cursor.fetchall():
            self.returns_tree.insert('', 'end', values=row)
    
    def show_add_user_dialog(self):
        """Show dialog to add a new user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        
        ttk.Label(dialog, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        user_id_entry = ttk.Entry(dialog)
        user_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Password:").grid(row=2, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Role:").grid(row=3, column=0, padx=5, pady=5)
        role_var = tk.StringVar(value="cashier")
        ttk.Radiobutton(dialog, text="Cashier", variable=role_var, value="cashier").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="Admin", variable=role_var, value="admin").grid(row=4, column=1, sticky=tk.W)
        
        def add_user():
            user_id = user_id_entry.get()
            name = name_entry.get()
            password = password_entry.get()
            role = role_var.get()
            
            if not user_id or not name or not password:
                messagebox.showerror("Error", "All fields are required")
                return
            
            cursor = self.cashier_system.db_conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?)",
                    (user_id, name, password, role)
                )
                self.cashier_system.db_conn.commit()
                self.cashier_system.users[user_id] = {
                    'name': name,
                    'password': password,
                    'role': role
                }
                self.refresh_users_list()
                dialog.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "User ID already exists")
        
        ttk.Button(dialog, text="Add", command=add_user).grid(row=5, column=0, columnspan=2, pady=10)
    
    def show_edit_user_dialog(self):
        """Show dialog to edit an existing user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a user to edit")
            return
        
        user_id = self.users_tree.item(selected[0], 'values')[0]
        user = self.cashier_system.users[user_id]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit User")
        
        ttk.Label(dialog, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(dialog, text=user_id).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, user['name'])
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="New Password:").grid(row=2, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Role:").grid(row=3, column=0, padx=5, pady=5)
        role_var = tk.StringVar(value=user['role'])
        ttk.Radiobutton(dialog, text="Cashier", variable=role_var, value="cashier").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="Admin", variable=role_var, value="admin").grid(row=4, column=1, sticky=tk.W)
        
        def update_user():
            name = name_entry.get()
            password = password_entry.get()
            role = role_var.get()
            
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            
            cursor = self.cashier_system.db_conn.cursor()
            if password:
                # Update with new password
                cursor.execute(
                    "UPDATE users SET name=?, password=?, role=? WHERE user_id=?",
                    (name, password, role, user_id)
                )
                user['password'] = password
            else:
                # Update without changing password
                cursor.execute(
                    "UPDATE users SET name=?, role=? WHERE user_id=?",
                    (name, role, user_id)
                )
            
            self.cashier_system.db_conn.commit()
            user['name'] = name
            user['role'] = role
            self.refresh_users_list()
            dialog.destroy()
        
        ttk.Button(dialog, text="Update", command=update_user).grid(row=5, column=0, columnspan=2, pady=10)
    
    def show_add_discount_dialog(self):
        """Show dialog to add a new discount"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Discount")
        
        ttk.Label(dialog, text="Discount Code:").grid(row=0, column=0, padx=5, pady=5)
        code_entry = ttk.Entry(dialog)
        code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(dialog)
        desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Discount Type:").grid(row=2, column=0, padx=5, pady=5)
        type_var = tk.StringVar(value="percentage")
        ttk.Radiobutton(dialog, text="Percentage", variable=type_var, value="percentage").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="Fixed Amount", variable=type_var, value="fixed").grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(dialog, text="Value:").grid(row=4, column=0, padx=5, pady=5)
        value_entry = ttk.Entry(dialog)
        value_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Valid Until (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5)
        valid_entry = ttk.Entry(dialog)
        valid_entry.grid(row=5, column=1, padx=5, pady=5)
        
        def add_discount():
            code = code_entry.get()
            description = desc_entry.get()
            discount_type = type_var.get()
            value = value_entry.get()
            valid_until = valid_entry.get() or None
            
            if not code or not description or not value:
                messagebox.showerror("Error", "Code, description and value are required")
                return
            
            try:
                value = float(value)
                if discount_type == "percentage" and (value <= 0 or value > 100):
                    raise ValueError("Percentage must be between 0 and 100")
                if discount_type == "fixed" and value <= 0:
                    raise ValueError("Fixed amount must be positive")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            cursor = self.cashier_system.db_conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO discounts VALUES (?, ?, ?, ?, ?)",
                    (code, description, discount_type, value, valid_until)
                )
                self.cashier_system.db_conn.commit()
                self.cashier_system.discounts[code] = {
                    'description': description,
                    'discount_type': discount_type,
                    'value': value,
                    'valid_until': valid_until
                }
                self.refresh_discounts_list()
                dialog.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Discount code already exists")
        
        ttk.Button(dialog, text="Add", command=add_discount).grid(row=6, column=0, columnspan=2, pady=10)
    
    def show_edit_discount_dialog(self):
        """Show dialog to edit an existing discount"""
        selected = self.discounts_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a discount to edit")
            return
        
        code = self.discounts_tree.item(selected[0], 'values')[0]
        discount = self.cashier_system.discounts[code]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Discount")
        
        ttk.Label(dialog, text="Discount Code:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(dialog, text=code).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(dialog)
        desc_entry.insert(0, discount['description'])
        desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Discount Type:").grid(row=2, column=0, padx=5, pady=5)
        type_var = tk.StringVar(value=discount['discount_type'])
        ttk.Radiobutton(dialog, text="Percentage", variable=type_var, value="percentage").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="Fixed Amount", variable=type_var, value="fixed").grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(dialog, text="Value:").grid(row=4, column=0, padx=5, pady=5)
        value_entry = ttk.Entry(dialog)
        value_entry.insert(0, str(discount['value']))
        value_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Valid Until (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5)
        valid_entry = ttk.Entry(dialog)
        if discount['valid_until']:
            valid_entry.insert(0, discount['valid_until'])
        valid_entry.grid(row=5, column=1, padx=5, pady=5)
        
        def update_discount():
            description = desc_entry.get()
            discount_type = type_var.get()
            value = value_entry.get()
            valid_until = valid_entry.get() or None
            
            if not description or not value:
                messagebox.showerror("Error", "Description and value are required")
                return
            
            try:
                value = float(value)
                if discount_type == "percentage" and (value <= 0 or value > 100):
                    raise ValueError("Percentage must be between 0 and 100")
                if discount_type == "fixed" and value <= 0:
                    raise ValueError("Fixed amount must be positive")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            cursor = self.cashier_system.db_conn.cursor()
            cursor.execute(
                "UPDATE discounts SET description=?, discount_type=?, value=?, valid_until=? WHERE code=?",
                (description, discount_type, value, valid_until, code)
            )
            self.cashier_system.db_conn.commit()
            discount['description'] = description
            discount['discount_type'] = discount_type
            discount['value'] = value
            discount['valid_until'] = valid_until
            self.refresh_discounts_list()
            dialog.destroy()
        
        ttk.Button(dialog, text="Update", command=update_discount).grid(row=6, column=0, columnspan=2, pady=10)
    
    def show_process_return_dialog(self):
        """Show dialog to process a return"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Process Return")
        dialog.geometry("600x400")
        
        # Transaction selection
        ttk.Label(dialog, text="Transaction ID:").pack(pady=5)
        self.return_transaction_entry = ttk.Entry(dialog)
        self.return_transaction_entry.pack(pady=5)
        
        ttk.Button(dialog, text="Lookup Transaction", command=self.lookup_transaction_for_return).pack(pady=5)
        
        # Items frame
        items_frame = ttk.Frame(dialog)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.return_items_tree = ttk.Treeview(items_frame, columns=('id', 'name', 'price', 'purchased', 'return'), show='headings')
        self.return_items_tree.heading('id', text='Product ID')
        self.return_items_tree.heading('name', text='Name')
        self.return_items_tree.heading('price', text='Price')
        self.return_items_tree.heading('purchased', text='Purchased Qty')
        self.return_items_tree.heading('return', text='Return Qty')
        self.return_items_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add spinboxes for return quantities
        self.return_qty_vars = {}
        
        def create_spinbox(tree, item, column):
            if column == 'return':
                product_id = tree.item(item, 'values')[0]
                purchased_qty = int(tree.item(item, 'values')[3])
                
                frame = ttk.Frame(tree)
                spinbox = ttk.Spinbox(frame, from_=0, to=purchased_qty, width=5)
                spinbox.set(0)
                self.return_qty_vars[product_id] = spinbox
                frame.pack()
                spinbox.pack()
                return frame
        
        self.return_items_tree.bind('<Map>', lambda e: self.return_items_tree.update())
        self.return_items_tree.bind('<Configure>', lambda e: self.return_items_tree.update())
        self.return_items_tree['displaycolumns'] = ('id', 'name', 'price', 'purchased', 'return')
        self.return_items_tree.column('return', stretch=False, width=100)
        self.return_items_tree['show'] = 'headings'
        
        # Process button
        ttk.Button(dialog, text="Process Return", command=self.process_return).pack(pady=10)
    
    def lookup_transaction_for_return(self):
        """Lookup transaction items for return"""
        transaction_id = self.return_transaction_entry.get()
        if not transaction_id:
            messagebox.showwarning("Error", "Please enter a transaction ID")
            return
        
        cursor = self.cashier_system.db_conn.cursor()
        
        # Verify transaction exists
        cursor.execute("SELECT timestamp, total FROM transactions WHERE transaction_id = ?", (transaction_id,))
        transaction = cursor.fetchone()
        if not transaction:
            messagebox.showerror("Error", "Transaction not found")
            return
        
        # Get transaction items
        cursor.execute("""
            SELECT ti.product_id, p.name, ti.price, ti.quantity
            FROM transaction_items ti
            JOIN products p ON ti.product_id = p.product_id
            WHERE ti.transaction_id = ?
        """, (transaction_id,))
        
        self.return_items_tree.delete(*self.return_items_tree.get_children())
        self.return_qty_vars = {}
        
        for row in cursor.fetchall():
            product_id, name, price, quantity = row
            self.return_items_tree.insert('', 'end', values=(product_id, name, price, quantity, 0))
    
    def process_return(self):
        """Process the return of items"""
        transaction_id = self.return_transaction_entry.get()
        if not transaction_id:
            messagebox.showwarning("Error", "Please enter a transaction ID")
            return
        
        # Get quantities to return
        items_to_return = {}
        for item in self.return_items_tree.get_children():
            product_id = self.return_items_tree.item(item, 'values')[0]
            return_qty = int(self.return_qty_vars[product_id].get())
            if return_qty > 0:
                items_to_return[product_id] = return_qty
        
        if not items_to_return:
            messagebox.showwarning("Error", "No items selected for return")
            return
        
        # Process return
        success, result = self.cashier_system.process_return(transaction_id, items_to_return)
        if success:
            messagebox.showinfo("Success", f"Return processed successfully\nRefund amount: ${result['total_refund']:.2f}")
            self.refresh_returns_list()
        else:
            messagebox.showerror("Error", result)
    
    def show_add_product_dialog(self):
        """Show dialog to add a new product"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Product")
        
        ttk.Label(dialog, text="Product ID:").grid(row=0, column=0, padx=5, pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Price:").grid(row=2, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Stock:").grid(row=3, column=0, padx=5, pady=5)
        stock_entry = ttk.Entry(dialog)
        stock_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Barcode:").grid(row=4, column=0, padx=5, pady=5)
        barcode_entry = ttk.Entry(dialog)
        barcode_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def add_product():
            product_id = id_entry.get()
            name = name_entry.get()
            price = price_entry.get()
            stock = stock_entry.get()
            barcode = barcode_entry.get() or None
            
            if not product_id or not name or not price or not stock:
                messagebox.showerror("Error", "Product ID, name, price and stock are required")
                return
            
            try:
                price = float(
		price = float(price)
                stock = int(stock)
                if price <= 0 or stock < 0:
                    raise ValueError("Price must be positive and stock must be non-negative")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            success = self.cashier_system.add_product(product_id, name, price, stock, barcode)
            if success:
                messagebox.showinfo("Success", "Product added successfully")
                self.refresh_inventory()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Product ID already exists")
        
        ttk.Button(dialog, text="Add", command=add_product).grid(row=5, column=0, columnspan=2, pady=10)
    
    def show_edit_product_dialog(self):
        """Show dialog to edit an existing product"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to edit")
            return
        
        product_id = self.inventory_tree.item(selected[0], 'values')[0]
        product = self.cashier_system.products[product_id]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Product")
        
        ttk.Label(dialog, text="Product ID:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(dialog, text=product_id).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, product['name'])
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Price:").grid(row=2, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(dialog)
        price_entry.insert(0, str(product['price']))
        price_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Stock:").grid(row=3, column=0, padx=5, pady=5)
        stock_entry = ttk.Entry(dialog)
        stock_entry.insert(0, str(product['stock']))
        stock_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Barcode:").grid(row=4, column=0, padx=5, pady=5)
        barcode_entry = ttk.Entry(dialog)
        if product['barcode']:
            barcode_entry.insert(0, product['barcode'])
        barcode_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def update_product():
            name = name_entry.get()
            price = price_entry.get()
            stock = stock_entry.get()
            barcode = barcode_entry.get() or None
            
            if not name or not price or not stock:
                messagebox.showerror("Error", "Name, price and stock are required")
                return
            
            try:
                price = float(price)
                stock = int(stock)
                if price <= 0 or stock < 0:
                    raise ValueError("Price must be positive and stock must be non-negative")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            success = self.cashier_system.update_product(product_id, name, price, stock, barcode)
            if success:
                messagebox.showinfo("Success", "Product updated successfully")
                self.refresh_inventory()
                self.refresh_product_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update product")
        
        ttk.Button(dialog, text="Update", command=update_product).grid(row=5, column=0, columnspan=2, pady=10)
    
    def refresh_inventory(self):
        """Refresh the inventory list"""
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        for product_id, product in self.cashier_system.products.items():
            self.inventory_tree.insert('', 'end', values=(
                product_id,
                product['name'],
                f"${product['price']:.2f}",
                product['stock'],
                product['barcode'] or ''
            ))
    
    def refresh_product_list(self):
        """Refresh the product list in POS tab"""
        self.product_tree.delete(*self.product_tree.get_children())
        for product_id, product in self.cashier_system.products.items():
            if product['stock'] > 0:  # Only show products with available stock
                self.product_tree.insert('', 'end', values=(
                    product_id,
                    product['name'],
                    f"${product['price']:.2f}",
                    product['stock']
                ))
    
    def search_products(self, event=None):
        """Search products based on search term"""
        search_term = self.product_search_entry.get().lower()
        self.product_tree.delete(*self.product_tree.get_children())
        
        for product_id, product in self.cashier_system.products.items():
            if (search_term in product_id.lower() or 
                search_term in product['name'].lower()) and product['stock'] > 0:
                self.product_tree.insert('', 'end', values=(
                    product_id,
                    product['name'],
                    f"${product['price']:.2f}",
                    product['stock']
                ))
    
    def add_selected_product(self, event):
        """Add selected product to transaction"""
        selected = self.product_tree.selection()
        if not selected:
            return
        
        product_id = self.product_tree.item(selected[0], 'values')[0]
        self.add_product_to_transaction(product_id, 1)
    
    def add_product_to_transaction(self, product_id, quantity):
        """Add product to current transaction"""
        success, message = self.cashier_system.add_to_transaction(product_id, quantity)
        if success:
            self.update_transaction_display()
        else:
            messagebox.showerror("Error", message)
    
    def remove_selected_item(self):
        """Remove selected item from transaction"""
        selected = self.transaction_tree.selection()
        if not selected:
            return
        
        # Remove from transaction
        item_index = int(self.transaction_tree.index(selected[0]))
        self.cashier_system.current_transaction.pop(item_index)
        self.update_transaction_display()
    
    def update_transaction_display(self):
        """Update the transaction display"""
        self.transaction_tree.delete(*self.transaction_tree.get_children())
        for item in self.cashier_system.current_transaction:
            self.transaction_tree.insert('', 'end', values=(
                item['name'],
                f"${item['price']:.2f}",
                item['quantity'],
                f"${item['subtotal']:.2f}"
            ))
        
        # Update totals
        subtotal = self.cashier_system.calculate_total()
        self.subtotal_var.set(f"${subtotal:.2f}")
        
        # Check if discount should be applied
        discount_code = self.discount_entry.get()
        total = subtotal
        if discount_code:
            valid, discount = self.cashier_system.apply_discount(discount_code)
            if valid:
                if discount['discount_type'] == 'percentage':
                    total *= (1 - discount['value'] / 100)
                else:  # fixed amount
                    total -= discount['value']
                total = max(0, total)
            else:
                messagebox.showerror("Invalid Discount", discount)
                self.discount_entry.delete(0, tk.END)
        
        self.total_var.set(f"${total:.2f}")
    
    def process_payment(self, payment_type):
        """Process payment for current transaction"""
        if not self.cashier_system.current_transaction:
            messagebox.showerror("Error", "No items in transaction")
            return
        
        total = float(self.total_var.get()[1:])  # Remove $ and convert to float
        
        if payment_type == 'cash':
            # Get payment amount
            payment_amount = simpledialog.askfloat(
                "Cash Payment",
                f"Total: ${total:.2f}\nEnter amount received:",
                minvalue=total
            )
            
            if payment_amount is None:  # User canceled
                return
        else:  # card
            payment_amount = total
        
        discount_code = self.discount_entry.get() or None
        success, receipt = self.cashier_system.process_payment(payment_amount, discount_code)
        
        if success:
            # Show receipt
            receipt_window = tk.Toplevel(self.root)
            receipt_window.title("Receipt")
            
            text = tk.Text(receipt_window, wrap=tk.WORD)
            text.insert(tk.END, receipt)
            text.pack(fill=tk.BOTH, expand=True)
            
            # Print button
            ttk.Button(
                receipt_window,
                text="Print Receipt",
                command=lambda: self.print_receipt(receipt)
            ).pack(pady=5)
            
            # Clear transaction
            self.transaction_tree.delete(*self.transaction_tree.get_children())
            self.subtotal_var.set("$0.00")
            self.total_var.set("$0.00")
            self.discount_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", receipt)
    
    def print_receipt(self, receipt_text):
        """Print the receipt (simulated)"""
        # In a real application, this would send to a printer
        # For now, we'll just show a message
        messagebox.showinfo("Print Receipt", "Receipt sent to printer")
    
    def generate_report(self):
        """Generate sales report"""
        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        
        report = self.cashier_system.generate_sales_report(start_date, end_date)
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Display report in text
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, f"Sales Report from {start_date or 'beginning'} to {end_date or 'now'}\n")
        self.report_text.insert(tk.END, "="*50 + "\n")
        self.report_text.insert(tk.END, f"Total Sales: ${report['total_sales']:.2f}\n")
        self.report_text.insert(tk.END, f"Total Transactions: {report['total_transactions']}\n")
        self.report_text.insert(tk.END, f"Average Sale: ${report['avg_sale']:.2f}\n\n")
        
        self.report_text.insert(tk.END, "Top Selling Products:\n")
        for product in report['top_products']:
            self.report_text.insert(tk.END, f"- {product[0]}: {product[1]} units (${product[2]:.2f})\n")
        
        # Create chart
        if report['top_products']:
            fig, ax = plt.subplots(figsize=(8, 4))
            product_names = [p[0] for p in report['top_products']]
            sales = [p[2] for p in report['top_products']]
            
            ax.bar(product_names, sales)
            ax.set_title("Top Selling Products by Revenue")
            ax.set_ylabel("Sales ($)")
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
    
    def check_admin_access(self):
        """Check if current user has admin access"""
        if (self.cashier_system.current_user and 
            self.cashier_system.users[self.cashier_system.current_user]['role'] == 'admin'):
            self.notebook.tab(self.admin_tab, state='normal')
        else:
            self.notebook.tab(self.admin_tab, state='hidden')

def main():
    root = tk.Tk()
    cashier_system = CashierSoftware()
    app = CashierApp(root, cashier_system)
    root.mainloop()

if __name__ == "__main__":
    main()


