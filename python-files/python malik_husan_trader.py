import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

class StoreManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Malik Husan Trader - Store Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f8ff')
        
        # Company information
        self.company_name = "Malik Husan Trader"
        self.proprietor = "Hafiz Muhammad Ahmad"
        self.address = "Muneer Chowk Hasilpur"
        self.phone = "03017926883"
        
        # Create database and tables
        self.create_database()
        
        # Create UI
        self.create_main_frame()
        
    def create_database(self):
        """Create database and necessary tables"""
        self.conn = sqlite3.connect('malik_husan_trader.db')
        self.cursor = self.conn.cursor()
        
        # Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                min_stock_level INTEGER DEFAULT 0,
                supplier TEXT,
                date_added TEXT
            )
        ''')
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                date_added TEXT
            )
        ''')
        
        # Transactions table (for ledger)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                total_amount REAL,
                date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_main_frame(self):
        """Create the main application interface"""
        # Header frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=self.company_name, 
                              font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        info_label = tk.Label(header_frame, 
                             text=f"Proprietor: {self.proprietor} | Address: {self.address} | Phone: {self.phone}",
                             font=('Arial', 10), fg='white', bg='#2c3e50')
        info_label.pack()
        
        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.inventory_tab = ttk.Frame(self.tab_control)
        self.customers_tab = ttk.Frame(self.tab_control)
        self.ledger_tab = ttk.Frame(self.tab_control)
        self.sales_tab = ttk.Frame(self.tab_control)
        self.reports_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.dashboard_tab, text='Dashboard')
        self.tab_control.add(self.inventory_tab, text='Inventory Management')
        self.tab_control.add(self.customers_tab, text='Customer Management')
        self.tab_control.add(self.ledger_tab, text='Customer Ledger')
        self.tab_control.add(self.sales_tab, text='Sales')
        self.tab_control.add(self.reports_tab, text='Reports')
        
        self.tab_control.pack(expand=1, fill='both')
        
        # Create content for each tab
        self.create_dashboard_tab()
        self.create_inventory_tab()
        self.create_customers_tab()
        self.create_ledger_tab()
        self.create_sales_tab()
        self.create_reports_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with overview information"""
        # Dashboard content
        dashboard_frame = tk.Frame(self.dashboard_tab, bg='#f0f8ff')
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Summary cards
        cards_frame = tk.Frame(dashboard_frame, bg='#f0f8ff')
        cards_frame.pack(fill=tk.X, pady=10)
        
        # Total items card
        total_items = self.get_total_items()
        item_card = self.create_summary_card(cards_frame, "Total Items", total_items, "#3498db")
        item_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Total customers card
        total_customers = self.get_total_customers()
        customer_card = self.create_summary_card(cards_frame, "Total Customers", total_customers, "#2ecc71")
        customer_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Low stock items card
        low_stock = self.get_low_stock_count()
        stock_card = self.create_summary_card(cards_frame, "Low Stock Items", low_stock, "#e74c3c")
        stock_card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Recent activity frame
        activity_frame = tk.LabelFrame(dashboard_frame, text="Recent Activity", font=('Arial', 12, 'bold'))
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add some sample activity text
        activity_text = tk.Text(activity_frame, height=10, font=('Arial', 10))
        activity_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        activity_text.insert(tk.END, "Welcome to Malik Husan Trader Management System!\n\n")
        activity_text.insert(tk.END, f"Today's Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        activity_text.insert(tk.END, f"Proprietor: {self.proprietor}\n")
        activity_text.insert(tk.END, f"Address: {self.address}\n")
        activity_text.insert(tk.END, f"Phone: {self.phone}\n\n")
        activity_text.insert(tk.END, "Use the tabs above to manage inventory, customers, and sales.")
        activity_text.config(state=tk.DISABLED)
    
    def create_summary_card(self, parent, title, value, color):
        """Create a summary card for the dashboard"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        
        title_label = tk.Label(card, text=title, font=('Arial', 14, 'bold'), 
                              bg=color, fg='white')
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(card, text=str(value), font=('Arial', 24, 'bold'), 
                              bg=color, fg='white')
        value_label.pack(pady=(5, 10))
        
        return card
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        # Inventory management content
        inv_frame = tk.Frame(self.inventory_tab)
        inv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(inv_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        add_btn = tk.Button(btn_frame, text="Add New Item", command=self.add_item, 
                           bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(btn_frame, text="Edit Item", command=self.edit_item,
                            bg='#3498db', fg='white', font=('Arial', 10, 'bold'))
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(btn_frame, text="Delete Item", command=self.delete_item,
                              bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh", command=self.refresh_inventory,
                               bg='#f39c12', fg='white', font=('Arial', 10, 'bold'))
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Treeview for items
        columns = ("ID", "Name", "Category", "Price", "Quantity", "Min Stock", "Supplier")
        self.inventory_tree = ttk.Treeview(inv_frame, columns=columns, show='headings')
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(inv_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load inventory data
        self.load_inventory_data()
    
    def create_customers_tab(self):
        """Create customer management tab"""
        # Customer management content
        cust_frame = tk.Frame(self.customers_tab)
        cust_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(cust_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        add_btn = tk.Button(btn_frame, text="Add New Customer", command=self.add_customer,
                           bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(btn_frame, text="Edit Customer", command=self.edit_customer,
                            bg='#3498db', fg='white', font=('Arial', 10, 'bold'))
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(btn_frame, text="Delete Customer", command=self.delete_customer,
                              bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh", command=self.refresh_customers,
                               bg='#f39c12', fg='white', font=('Arial', 10, 'bold'))
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Treeview for customers
        columns = ("ID", "Name", "Phone", "Address", "Date Added")
        self.customers_tree = ttk.Treeview(cust_frame, columns=columns, show='headings')
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(cust_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load customers data
        self.load_customers_data()
    
    def create_ledger_tab(self):
        """Create customer ledger tab"""
        ledger_frame = tk.Frame(self.ledger_tab)
        ledger_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Customer selection
        selection_frame = tk.Frame(ledger_frame)
        selection_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(selection_frame, text="Select Customer:", font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.customer_var = tk.StringVar()
        self.customer_dropdown = ttk.Combobox(selection_frame, textvariable=self.customer_var)
        self.customer_dropdown.pack(side=tk.LEFT, padx=5)
        self.customer_dropdown.bind('<<ComboboxSelected>>', self.load_ledger_data)
        
        # Buttons
        add_trans_btn = tk.Button(selection_frame, text="Add Transaction", command=self.add_transaction,
                                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'))
        add_trans_btn.pack(side=tk.RIGHT, padx=5)
        
        # Treeview for ledger
        columns = ("ID", "Date", "Type", "Amount", "Description")
        self.ledger_tree = ttk.Treeview(ledger_frame, columns=columns, show='headings')
        
        for col in columns:
            self.ledger_tree.heading(col, text=col)
            self.ledger_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(ledger_frame, orient=tk.VERTICAL, command=self.ledger_tree.yview)
        self.ledger_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ledger_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load customer names for dropdown
        self.load_customer_names()
    
    def create_sales_tab(self):
        """Create sales tab"""
        sales_frame = tk.Frame(self.sales_tab)
        sales_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sales form
        form_frame = tk.LabelFrame(sales_frame, text="New Sale", font=('Arial', 12, 'bold'))
        form_frame.pack(fill=tk.X, pady=5)
        
        # Customer selection
        tk.Label(form_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.sale_customer_var = tk.StringVar()
        sale_customer_dropdown = ttk.Combobox(form_frame, textvariable=self.sale_customer_var)
        sale_customer_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Item selection
        tk.Label(form_frame, text="Item:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.sale_item_var = tk.StringVar()
        sale_item_dropdown = ttk.Combobox(form_frame, textvariable=self.sale_item_var)
        sale_item_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Quantity
        tk.Label(form_frame, text="Quantity:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.sale_quantity_var = tk.StringVar()
        sale_quantity_entry = tk.Entry(form_frame, textvariable=self.sale_quantity_var)
        sale_quantity_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Add to cart button
        add_to_cart_btn = tk.Button(form_frame, text="Add to Cart", command=self.add_to_cart,
                                   bg='#3498db', fg='white', font=('Arial', 10, 'bold'))
        add_to_cart_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Cart treeview
        cart_frame = tk.LabelFrame(sales_frame, text="Cart", font=('Arial', 12, 'bold'))
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("Item", "Quantity", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings')
        
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Checkout button
        checkout_btn = tk.Button(sales_frame, text="Process Sale", command=self.process_sale,
                               bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'))
        checkout_btn.pack(pady=10)
        
        # Load customer and item names for dropdowns
        self.load_customer_names()
        self.load_item_names()
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = tk.Frame(self.reports_tab, bg='#f0f8ff')
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Report selection
        selection_frame = tk.Frame(reports_frame, bg='#f0f8ff')
        selection_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(selection_frame, text="Select Report:", font=('Arial', 12), bg='#f0f8ff').pack(side=tk.LEFT)
        
        self.report_var = tk.StringVar()
        report_dropdown = ttk.Combobox(selection_frame, textvariable=self.report_var, 
                                      values=["Sales Report", "Inventory Report", "Customer Report"])
        report_dropdown.pack(side=tk.LEFT, padx=10)
        report_dropdown.bind('<<ComboboxSelected>>', self.generate_report)
        
        # Report display
        report_display_frame = tk.Frame(reports_frame)
        report_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.report_text = tk.Text(report_display_frame, font=('Arial', 10))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial report
        self.report_text.insert(tk.END, "Welcome to Reports Section\n\n")
        self.report_text.insert(tk.END, "Select a report type from the dropdown above to generate reports.")
        self.report_text.config(state=tk.DISABLED)
    
    # Database operations
    def get_total_items(self):
        """Get total number of items in inventory"""
        self.cursor.execute("SELECT COUNT(*) FROM items")
        return self.cursor.fetchone()[0]
    
    def get_total_customers(self):
        """Get total number of customers"""
        self.cursor.execute("SELECT COUNT(*) FROM customers")
        return self.cursor.fetchone()[0]
    
    def get_low_stock_count(self):
        """Get count of items with low stock"""
        self.cursor.execute("SELECT COUNT(*) FROM items WHERE quantity <= min_stock_level")
        return self.cursor.fetchone()[0]
    
    def load_inventory_data(self):
        """Load inventory data into treeview"""
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Fetch data from database
        self.cursor.execute("SELECT * FROM items")
        rows = self.cursor.fetchall()
        
        # Insert data into treeview
        for row in rows:
            self.inventory_tree.insert("", tk.END, values=row)
    
    def load_customers_data(self):
        """Load customers data into treeview"""
        # Clear existing data
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Fetch data from database
        self.cursor.execute("SELECT * FROM customers")
        rows = self.cursor.fetchall()
        
        # Insert data into treeview
        for row in rows:
            self.customers_tree.insert("", tk.END, values=row)
    
    def load_customer_names(self):
        """Load customer names for dropdowns"""
        self.cursor.execute("SELECT id, name FROM customers")
        customers = self.cursor.fetchall()
        customer_list = [f"{cid}: {name}" for cid, name in customers]
        
        self.customer_dropdown['values'] = customer_list
        self.sale_customer_var.set('')
        
        if customer_list:
            self.sale_customer_var.set(customer_list[0])
    
    def load_item_names(self):
        """Load item names for dropdowns"""
        self.cursor.execute("SELECT id, name FROM items")
        items = self.cursor.fetchall()
        item_list = [f"{iid}: {name}" for iid, name in items]
        
        self.sale_item_var.set('')
        
        if item_list:
            self.sale_item_var.set(item_list[0])
    
    def load_ledger_data(self, event=None):
        """Load ledger data for selected customer"""
        # Clear existing data
        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)
        
        # Get selected customer ID
        selected = self.customer_var.get()
        if not selected:
            return
        
        customer_id = selected.split(":")[0]
        
        # Fetch transactions for this customer
        self.cursor.execute("""
            SELECT id, date, type, amount, description 
            FROM transactions 
            WHERE customer_id = ? 
            ORDER BY date DESC
        """, (customer_id,))
        
        transactions = self.cursor.fetchall()
        
        # Insert into treeview
        for trans in transactions:
            self.ledger_tree.insert("", tk.END, values=trans)
    
    def add_item(self):
        """Open dialog to add new item"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Item")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        tk.Label(dialog, text="Item Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Category:").pack(pady=5)
        category_entry = tk.Entry(dialog, width=40)
        category_entry.pack(pady=5)
        
        tk.Label(dialog, text="Price:").pack(pady=5)
        price_entry = tk.Entry(dialog, width=40)
        price_entry.pack(pady=5)
        
        tk.Label(dialog, text="Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(dialog, width=40)
        quantity_entry.pack(pady=5)
        
        tk.Label(dialog, text="Min Stock Level:").pack(pady=5)
        min_stock_entry = tk.Entry(dialog, width=40)
        min_stock_entry.pack(pady=5)
        
        tk.Label(dialog, text="Supplier:").pack(pady=5)
        supplier_entry = tk.Entry(dialog, width=40)
        supplier_entry.pack(pady=5)
        
        def save_item():
            name = name_entry.get()
            category = category_entry.get()
            price = price_entry.get()
            quantity = quantity_entry.get()
            min_stock = min_stock_entry.get()
            supplier = supplier_entry.get()
            
            if not name or not price or not quantity:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            try:
                self.cursor.execute("""
                    INSERT INTO items (name, category, price, quantity, min_stock_level, supplier, date_added)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, category, float(price), int(quantity), int(min_stock), supplier, datetime.now().strftime("%Y-%m-%d")))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Item added successfully")
                self.load_inventory_data()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {str(e)}")
        
        tk.Button(dialog, text="Save", command=save_item, bg='#2ecc71', fg='white').pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy, bg='#e74c3c', fg='white').pack(pady=5)
    
    def edit_item(self):
        """Edit selected item"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_id = self.inventory_tree.item(selected[0])['values'][0]
        
        # Fetch item details
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = self.cursor.fetchone()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields with current values
        tk.Label(dialog, text="Item Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.insert(0, item[1])
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Category:").pack(pady=5)
        category_entry = tk.Entry(dialog, width=40)
        category_entry.insert(0, item[2] if item[2] else "")
        category_entry.pack(pady=5)
        
        tk.Label(dialog, text="Price:").pack(pady=5)
        price_entry = tk.Entry(dialog, width=40)
        price_entry.insert(0, str(item[3]))
        price_entry.pack(pady=5)
        
        tk.Label(dialog, text="Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(dialog, width=40)
        quantity_entry.insert(0, str(item[4]))
        quantity_entry.pack(pady=5)
        
        tk.Label(dialog, text="Min Stock Level:").pack(pady=5)
        min_stock_entry = tk.Entry(dialog, width=40)
        min_stock_entry.insert(0, str(item[5]))
        min_stock_entry.pack(pady=5)
        
        tk.Label(dialog, text="Supplier:").pack(pady=5)
        supplier_entry = tk.Entry(dialog, width=40)
        supplier_entry.insert(0, item[6] if item[6] else "")
        supplier_entry.pack(pady=5)
        
        def update_item():
            name = name_entry.get()
            category = category_entry.get()
            price = price_entry.get()
            quantity = quantity_entry.get()
            min_stock = min_stock_entry.get()
            supplier = supplier_entry.get()
            
            if not name or not price or not quantity:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            try:
                self.cursor.execute("""
                    UPDATE items 
                    SET name=?, category=?, price=?, quantity=?, min_stock_level=?, supplier=?
                    WHERE id=?
                """, (name, category, float(price), int(quantity), int(min_stock), supplier, item_id))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Item updated successfully")
                self.load_inventory_data()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update item: {str(e)}")
        
        tk.Button(dialog, text="Update", command=update_item, bg='#2ecc71', fg='white').pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy, bg='#e74c3c', fg='white').pack(pady=5)
    
    def delete_item(self):
        """Delete selected item"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_id = self.inventory_tree.item(selected[0])['values'][0]
        item_name = self.inventory_tree.item(selected[0])['values'][1]
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {item_name}?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Item deleted successfully")
                self.load_inventory_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    def refresh_inventory(self):
        """Refresh inventory data"""
        self.load_inventory_data()
    
    def add_customer(self):
        """Open dialog to add new customer"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Customer")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        tk.Label(dialog, text="Customer Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Phone:").pack(pady=5)
        phone_entry = tk.Entry(dialog, width=40)
        phone_entry.pack(pady=5)
        
        tk.Label(dialog, text="Address:").pack(pady=5)
        address_entry = tk.Entry(dialog, width=40)
        address_entry.pack(pady=5)
        
        def save_customer():
            name = name_entry.get()
            phone = phone_entry.get()
            address = address_entry.get()
            
            if not name:
                messagebox.showerror("Error", "Customer name is required")
                return
            
            try:
                self.cursor.execute("""
                    INSERT INTO customers (name, phone, address, date_added)
                    VALUES (?, ?, ?, ?)
                """, (name, phone, address, datetime.now().strftime("%Y-%m-%d")))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Customer added successfully")
                self.load_customers_data()
                self.load_customer_names()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
        
        tk.Button(dialog, text="Save", command=save_customer, bg='#2ecc71', fg='white').pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy, bg='#e74c3c', fg='white').pack(pady=5)
    
    def edit_customer(self):
        """Edit selected customer"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
        
        customer_id = self.customers_tree.item(selected[0])['values'][0]
        
        # Fetch customer details
        self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = self.cursor.fetchone()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Customer")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields with current values
        tk.Label(dialog, text="Customer Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.insert(0, customer[1])
        name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Phone:").pack(pady=5)
        phone_entry = tk.Entry(dialog, width=40)
        phone_entry.insert(0, customer[2] if customer[2] else "")
        phone_entry.pack(pady=5)
        
        tk.Label(dialog, text="Address:").pack(pady=5)
        address_entry = tk.Entry(dialog, width=40)
        address_entry.insert(0, customer[3] if customer[3] else "")
        address_entry.pack(pady=5)
        
        def update_customer():
            name = name_entry.get()
            phone = phone_entry.get()
            address = address_entry.get()
            
            if not name:
                messagebox.showerror("Error", "Customer name is required")
                return
            
            try:
                self.cursor.execute("""
                    UPDATE customers 
                    SET name=?, phone=?, address=?
                    WHERE id=?
                """, (name, phone, address, customer_id))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Customer updated successfully")
                self.load_customers_data()
                self.load_customer_names()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {str(e)}")
        
        tk.Button(dialog, text="Update", command=update_customer, bg='#2ecc71', fg='white').pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy, bg='#e74c3c', fg='white').pack(pady=5)
    
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        customer_id = self.customers_tree.item(selected[0])['values'][0]
        customer_name = self.customers_tree.item(selected[0])['values'][1]
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {customer_name}?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Customer deleted successfully")
                self.load_customers_data()
                self.load_customer_names()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")
    
    def refresh_customers(self):
        """Refresh customers data"""
        self.load_customers_data()
    
    def add_transaction(self):
        """Add a new transaction for selected customer"""
        selected_customer = self.customer_var.get()
        if not selected_customer:
            messagebox.showwarning("Warning", "Please select a customer first")
            return
        
        customer_id = selected_customer.split(":")[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Transaction")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        tk.Label(dialog, text="Transaction Type:").pack(pady=5)
        type_var = tk.StringVar(value="Credit")
        type_dropdown = ttk.Combobox(dialog, textvariable=type_var, values=["Credit", "Debit"])
        type_dropdown.pack(pady=5)
        
        tk.Label(dialog, text="Amount:").pack(pady=5)
        amount_entry = tk.Entry(dialog, width=40)
        amount_entry.pack(pady=5)
        
        tk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = tk.Entry(dialog, width=40)
        desc_entry.pack(pady=5)
        
        def save_transaction():
            trans_type = type_var.get()
            amount = amount_entry.get()
            description = desc_entry.get()
            
            if not amount:
                messagebox.showerror("Error", "Amount is required")
                return
            
            try:
                self.cursor.execute("""
                    INSERT INTO transactions (customer_id, type, amount, description, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (customer_id, trans_type, float(amount), description, datetime.now().strftime("%Y-%m-%d")))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Transaction added successfully")
                self.load_ledger_data()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
        
        tk.Button(dialog, text="Save", command=save_transaction, bg='#2ecc71', fg='white').pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy, bg='#e74c3c', fg='white').pack(pady=5)
    
    def add_to_cart(self):
        """Add selected item to cart"""
        selected_item = self.sale_item_var.get()
        quantity = self.sale_quantity_var.get()
        
        if not selected_item or not quantity:
            messagebox.showwarning("Warning", "Please select an item and enter quantity")
            return
        
        try:
            item_id = selected_item.split(":")[0]
            quantity = int(quantity)
            
            # Get item details
            self.cursor.execute("SELECT name, price FROM items WHERE id = ?", (item_id,))
            item = self.cursor.fetchone()
            
            if not item:
                messagebox.showerror("Error", "Selected item not found")
                return
            
            item_name, price = item
            total = price * quantity
            
            # Add to cart treeview
            self.cart_tree.insert("", tk.END, values=(item_name, quantity, price, total))
            
            # Clear quantity field
            self.sale_quantity_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
    
    def process_sale(self):
        """Process the sale and update inventory"""
        # Get all items in cart
        cart_items = []
        for item in self.cart_tree.get_children():
            values = self.cart_tree.item(item)['values']
            cart_items.append(values)
        
        if not cart_items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        # Get customer ID
        selected_customer = self.sale_customer_var.get()
        if not selected_customer:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        customer_id = selected_customer.split(":")[0]
        
        # Process each item in cart
        total_sale = 0
        for item_name, quantity, price, total in cart_items:
            total_sale += total
            
            # Get item ID
            self.cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
            item_result = self.cursor.fetchone()
            
            if not item_result:
                messagebox.showerror("Error", f"Item {item_name} not found in database")
                return
            
            item_id = item_result[0]
            
            # Update inventory
            self.cursor.execute("UPDATE items SET quantity = quantity - ? WHERE id = ?", (quantity, item_id))
            
            # Record sale
            self.cursor.execute("""
                INSERT INTO sales (customer_id, item_id, quantity, total_amount, date)
                VALUES (?, ?, ?, ?, ?)
            """, (customer_id, item_id, quantity, total, datetime.now().strftime("%Y-%m-%d")))
        
        # Add transaction to ledger
        self.cursor.execute("""
            INSERT INTO transactions (customer_id, type, amount, description, date)
            VALUES (?, 'Debit', ?, 'Sale', ?)
        """, (customer_id, total_sale, datetime.now().strftime("%Y-%m-%d")))
        
        self.conn.commit()
        
        # Clear cart
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        messagebox.showinfo("Success", f"Sale processed successfully. Total: ${total_sale:.2f}")
        self.load_inventory_data()
    
    def generate_report(self, event=None):
        """Generate selected report"""
        report_type = self.report_var.get()
        
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)
        
        if report_type == "Sales Report":
            self.generate_sales_report()
        elif report_type == "Inventory Report":
            self.generate_inventory_report()
        elif report_type == "Customer Report":
            self.generate_customer_report()
        
        self.report_text.config(state=tk.DISABLED)
    
    def generate_sales_report(self):
        """Generate sales report"""
        self.cursor.execute("""
            SELECT s.date, c.name, i.name, s.quantity, s.total_amount 
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            JOIN items i ON s.item_id = i.id
            ORDER BY s.date DESC
        """)
        
        sales = self.cursor.fetchall()
        
        self.report_text.insert(tk.END, "SALES REPORT\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        total_sales = 0
        for date, customer, item, quantity, amount in sales:
            self.report_text.insert(tk.END, f"Date: {date}\n")
            self.report_text.insert(tk.END, f"Customer: {customer}\n")
            self.report_text.insert(tk.END, f"Item: {item} x {quantity}\n")
            self.report_text.insert(tk.END, f"Amount: ${amount:.2f}\n")
            self.report_text.insert(tk.END, "-"*30 + "\n")
            total_sales += amount
        
        self.report_text.insert(tk.END, f"\nTotal Sales: ${total_sales:.2f}\n")
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        self.cursor.execute("SELECT * FROM items ORDER BY name")
        items = self.cursor.fetchall()
        
        self.report_text.insert(tk.END, "INVENTORY REPORT\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        for item in items:
            id, name, category, price, quantity, min_stock, supplier, date_added = item
            status = "LOW STOCK" if quantity <= min_stock else "OK"
            
            self.report_text.insert(tk.END, f"Name: {name}\n")
            self.report_text.insert(tk.END, f"Category: {category}\n")
            self.report_text.insert(tk.END, f"Price: ${price:.2f}\n")
            self.report_text.insert(tk.END, f"Quantity: {quantity} (Min: {min_stock}) - {status}\n")
            self.report_text.insert(tk.END, f"Supplier: {supplier}\n")
            self.report_text.insert(tk.END, f"Date Added: {date_added}\n")
            self.report_text.insert(tk.END, "-"*30 + "\n")
    
    def generate_customer_report(self):
        """Generate customer report"""
        self.cursor.execute("SELECT * FROM customers ORDER BY name")
        customers = self.cursor.fetchall()
        
        self.report_text.insert(tk.END, "CUSTOMER REPORT\n")
        self.report_text.insert(tk.END, "="*50 + "\n\n")
        
        for customer in customers:
            id, name, phone, address, date_added = customer
            
            self.report_text.insert(tk.END, f"Name: {name}\n")
            self.report_text.insert(tk.END, f"Phone: {phone}\n")
            self.report_text.insert(tk.END, f"Address: {address}\n")
            self.report_text.insert(tk.END, f"Date Added: {date_added}\n")
            
            # Get balance
            self.cursor.execute("""
                SELECT SUM(CASE WHEN type='Credit' THEN amount ELSE -amount END) 
                FROM transactions 
                WHERE customer_id = ?
            """, (id,))
            
            balance = self.cursor.fetchone()[0] or 0
            
            self.report_text.insert(tk.END, f"Balance: ${balance:.2f}\n")
            self.report_text.insert(tk.END, "-"*30 + "\n")

def main():
    root = tk.Tk()
    app = StoreManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()