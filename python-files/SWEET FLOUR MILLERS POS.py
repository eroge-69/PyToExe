import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import calendar

# ==============================================================================
# Database Class
# Handles all interactions with the SQLite database.
# ==============================================================================
class Database:
    """Manages all database operations for the POS system."""
    def __init__(self, db_file="pos_database.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_settings_table()

    def create_tables(self):
        """
        Creates the products, sales, and milling_records tables.
        Includes a 'barcode' column for products.
        """
        self.cursor.execute("PRAGMA foreign_keys = OFF")

        # Drop the old tables to ensure a clean slate and apply the new schema
        self.cursor.execute("DROP TABLE IF EXISTS products")
        self.cursor.execute("DROP TABLE IF EXISTS sales")
        self.cursor.execute("DROP TABLE IF EXISTS milling_records")

        # Create the new 'products' table with the 'unit' and 'barcode' columns
        self.cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                cost_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                stock REAL NOT NULL,
                unit TEXT NOT NULL,
                barcode TEXT UNIQUE
            )
        ''')

        # Create the 'sales' table with a foreign key to 'products'
        self.cursor.execute('''
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                sale_datetime TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Create the 'milling_records' table for the new section
        # Added a column for labour_percentage
        self.cursor.execute('''
            CREATE TABLE milling_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT NOT NULL,
                current_reading REAL NOT NULL,
                previous_reading REAL NOT NULL,
                unit_cost REAL NOT NULL,
                units_used REAL NOT NULL,
                power_bill REAL NOT NULL,
                labour_cost REAL NOT NULL,
                money_generated REAL NOT NULL,
                labour_percentage REAL
            )
        ''')

        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()

    def create_settings_table(self):
        """Creates a table to store application settings, like last used values."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def set_setting(self, key, value):
        """Saves or updates a setting in the database."""
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_setting(self, key, default=None):
        """Retrieves a setting from the database, or returns a default value."""
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default

    def add_product(self, name, cost_price, selling_price, stock, unit, barcode=None):
        """Adds a new product to the database with cost, selling prices, unit, and an optional barcode."""
        try:
            self.cursor.execute("INSERT INTO products (name, cost_price, selling_price, stock, unit, barcode) VALUES (?, ?, ?, ?, ?, ?)", (name, cost_price, selling_price, stock, unit, barcode))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "name" in str(e):
                messagebox.showerror("Error", f"Product '{name}' already exists.")
            elif "barcode" in str(e):
                messagebox.showerror("Error", f"Barcode '{barcode}' already exists for another product.")
            return False

    def update_product(self, product_id, name, cost_price, selling_price, stock, unit, barcode=None):
        """Updates an existing product's details in the database."""
        try:
            self.cursor.execute("UPDATE products SET name=?, cost_price=?, selling_price=?, stock=?, unit=?, barcode=? WHERE id=?", (name, cost_price, selling_price, stock, unit, barcode, product_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            if "name" in str(e):
                messagebox.showerror("Error", "Product with that name already exists.")
            elif "barcode" in str(e):
                messagebox.showerror("Error", f"Barcode '{barcode}' is already assigned to another product.")
            return False

    def delete_product(self, product_id):
        """Deletes a product from the database by its ID."""
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    def get_all_products(self):
        """Fetches all products from the database, including the unit and barcode."""
        self.cursor.execute("SELECT id, name, cost_price, selling_price, stock, unit, barcode FROM products")
        return self.cursor.fetchall()

    def get_product_by_name(self, name):
        """Fetches a single product by its name."""
        self.cursor.execute("SELECT id, name, cost_price, selling_price, stock, unit, barcode FROM products WHERE name=?", (name,))
        return self.cursor.fetchone()

    def get_product_by_id(self, product_id):
        """Fetches a single product by its ID."""
        self.cursor.execute("SELECT id, name, cost_price, selling_price, stock, unit, barcode FROM products WHERE id=?", (product_id,))
        return self.cursor.fetchone()

    def get_product_by_barcode(self, barcode):
        """Fetches a single product by its barcode."""
        self.cursor.execute("SELECT id, name, cost_price, selling_price, stock, unit, barcode FROM products WHERE barcode=?", (barcode,))
        return self.cursor.fetchone()

    def update_stock(self, product_id, new_stock):
        """Updates the stock level of a product."""
        self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        self.conn.commit()

    def add_sale(self, product_id, quantity, unit_price):
        """Records a new sale in the database."""
        sale_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO sales (product_id, quantity, unit_price, sale_datetime) VALUES (?, ?, ?, ?)",
                            (product_id, quantity, unit_price, sale_datetime))
        self.conn.commit()

    def get_sales_report(self, start_date, end_date):
        """Generates a sales report between two dates, including cost price for profit calculation."""
        self.cursor.execute("""
            SELECT p.name, p.cost_price, s.quantity, s.unit_price, s.sale_datetime, p.unit
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.sale_datetime BETWEEN ? AND ?
            ORDER BY s.sale_datetime DESC
        """, (start_date, end_date))
        return self.cursor.fetchall()

    def add_milling_record(self, current_reading, previous_reading, unit_cost, units_used, power_bill, labour_cost, money_generated, labour_percentage):
        """Records a new milling operation in the database."""
        start_datetime = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S") # Placeholder
        end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO milling_records (start_datetime, end_datetime, current_reading, previous_reading, unit_cost, units_used, power_bill, labour_cost, money_generated, labour_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (start_datetime, end_datetime, current_reading, previous_reading, unit_cost, units_used, power_bill, labour_cost, money_generated, labour_percentage))
        self.conn.commit()

    def get_milling_report(self, start_date, end_date):
        """Fetches milling records for a specific date range."""
        self.cursor.execute("""
            SELECT start_datetime, end_datetime, current_reading, previous_reading, units_used, power_bill, labour_cost, money_generated, labour_percentage
            FROM milling_records
            WHERE start_datetime BETWEEN ? AND ?
            ORDER BY start_datetime DESC
        """, (start_date, end_date))
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        self.conn.close()


# ==============================================================================
# GUI Class
# Builds and manages the graphical user interface.
# ==============================================================================
class POSApp(tk.Tk):
    """Main application class for the POS system GUI."""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("SWEET FLOUR MILLERS POINT OF SALE")
        self.geometry("1000x750")

        # --- GUI Styling ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # A modern, flat-looking theme
        self.style.configure("TFrame", background="#F5F5F5")
        self.style.configure("TLabel", background="#F5F5F5", font=("Segoe UI", 10))
        self.style.configure("TEntry", fieldbackground="#FFFFFF", foreground="#333333", borderwidth=1, relief="solid")
        self.style.configure("TButton", background="#007BFF", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat", padding=8)
        self.style.map("TButton", background=[('active', '#0056b3')])
        self.style.configure("TLabelframe", background="#E8E8E8", borderwidth=1, relief="solid")
        self.style.configure("TNotebook", background="#F5F5F5", borderwidth=0, tabposition="n")
        self.style.configure("TNotebook.Tab", background="#C0C0C0", foreground="black", padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[('selected', '#F5F5F5')])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Create frames for each tab
        self.add_product_frame = ttk.Frame(self.notebook, padding="20")
        self.make_sale_frame = ttk.Frame(self.notebook, padding="20")
        self.inventory_frame = ttk.Frame(self.notebook, padding="20")
        self.reports_frame = ttk.Frame(self.notebook, padding="20")
        self.milling_frame = ttk.Frame(self.notebook, padding="20")

        self.notebook.add(self.add_product_frame, text="Add/Edit Product")
        self.notebook.add(self.make_sale_frame, text="Make Sale")
        self.notebook.add(self.inventory_frame, text="Inventory")
        self.notebook.add(self.reports_frame, text="Sales Report")
        self.notebook.add(self.milling_frame, text="Milling Section")

        # Build each section
        self.create_add_product_section()
        self.create_make_sale_section()
        self.create_inventory_section()
        self.create_reports_section()
        self.create_milling_section()

        # Update inventory display when the notebook tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Instance variables to store calculated values for saving
        self.calculated_labour_cost = 0.0
        self.calculated_profit_generated = 0.0
        
        # Default report types
        self.sales_report_type = "daily"
        self.milling_report_type = "daily"

    def on_tab_changed(self, event):
        """Handles tab changes to refresh data displays."""
        selected_tab_id = self.notebook.select()
        selected_tab_text = self.notebook.tab(selected_tab_id, "text")
        if selected_tab_text == "Inventory":
            self.display_inventory()
        elif selected_tab_text == "Make Sale":
            self.refresh_product_list()
            self.make_sale_barcode_entry.focus_set()
        elif selected_tab_text == "Add/Edit Product":
            self.add_product_barcode_entry.focus_set()
        elif selected_tab_text == "Milling Section":
            self.load_milling_settings()
            self.set_milling_report_view('daily')
        elif selected_tab_text == "Sales Report":
            self.set_sales_report_view('daily')

    # ==========================================================================
    # Add Product Section
    # ==========================================================================
    def create_add_product_section(self):
        """Sets up the 'Add Product' tab with a barcode entry."""
        container = ttk.Frame(self.add_product_frame)
        container.pack(expand=True, fill="both")

        ttk.Label(container, text="Manage Products", font=("Segoe UI", 18, "bold")).pack(pady=(0, 20))

        # Barcode Scanner Section
        barcode_frame = ttk.LabelFrame(container, text="Scan Barcode to Add or Edit", padding="15")
        barcode_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        inner_barcode_frame = ttk.Frame(barcode_frame)
        inner_barcode_frame.pack(fill="x")
        
        ttk.Label(inner_barcode_frame, text="Scan product barcode:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))
        self.add_product_barcode_entry = ttk.Entry(inner_barcode_frame, width=40, font=("Segoe UI", 11))
        self.add_product_barcode_entry.pack(side="left", expand=True, fill="x")
        self.add_product_barcode_entry.bind("<Return>", self.on_barcode_scan_add_product)

        # Form for product details
        form_frame = ttk.Frame(container)
        form_frame.pack(pady=10, padx=20, fill="x")

        fields = [
            ("Product Name:", "add_product_name_entry"),
            ("Barcode (Manual):", "add_product_manual_barcode_entry"),
            ("Cost Price (Ksh):", "add_cost_price_entry"),
            ("Selling Price (Ksh):", "add_selling_price_entry"),
            ("Stock:", "add_stock_entry"),
        ]

        # Use a grid layout for better alignment
        for i, (label_text, entry_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(form_frame, width=35, font=("Segoe UI", 10))
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            setattr(self, entry_name, entry)

        # Special case for the unit combobox
        ttk.Label(form_frame, text="Unit:").grid(row=4, column=2, sticky="w", pady=5, padx=5)
        self.add_unit_combo = ttk.Combobox(form_frame, values=["packets", "kgs", "liters"], width=15, state="readonly", font=("Segoe UI", 10))
        self.add_unit_combo.current(0)
        self.add_unit_combo.grid(row=4, column=3, pady=5, padx=5, sticky="w")
        
        form_frame.columnconfigure(1, weight=1)

        self.add_product_button = ttk.Button(container, text="Add Product", command=self.add_product, style="TButton")
        self.add_product_button.pack(pady=20, ipadx=20)

        # Internal state to manage edit vs. add mode
        self.product_to_edit_id = None

    def on_barcode_scan_add_product(self, event=None):
        """Handles barcode scan in the Add Product section."""
        barcode = self.add_product_barcode_entry.get().strip()
        self.add_product_barcode_entry.delete(0, tk.END)

        if not barcode:
            return

        product = self.db.get_product_by_barcode(barcode)

        if product:
            # Product found, populate fields for editing
            self.product_to_edit_id = product[0]
            self.add_product_name_entry.delete(0, tk.END)
            self.add_product_name_entry.insert(0, product[1])
            self.add_cost_price_entry.delete(0, tk.END)
            self.add_cost_price_entry.insert(0, product[2])
            self.add_selling_price_entry.delete(0, tk.END)
            self.add_selling_price_entry.insert(0, product[3])
            self.add_stock_entry.delete(0, tk.END)
            self.add_stock_entry.insert(0, product[4])
            self.add_unit_combo.set(product[5])
            self.add_product_manual_barcode_entry.delete(0, tk.END)
            self.add_product_manual_barcode_entry.insert(0, product[6])

            self.add_product_button.config(text="Update Product")
            messagebox.showinfo("Product Found", f"Product '{product[1]}' loaded for editing.")
        else:
            # New product, prepare fields for adding
            self.product_to_edit_id = None
            self.add_product_name_entry.delete(0, tk.END)
            self.add_cost_price_entry.delete(0, tk.END)
            self.add_selling_price_entry.delete(0, tk.END)
            self.add_stock_entry.delete(0, tk.END)
            self.add_unit_combo.set("packets")
            self.add_product_manual_barcode_entry.delete(0, tk.END)
            self.add_product_manual_barcode_entry.insert(0, barcode)

            self.add_product_button.config(text="Add Product")
            messagebox.showinfo("New Product", f"Barcode '{barcode}' not found. Please enter details for a new product.")

    def add_product(self):
        """Adds or updates a product in the database based on form input."""
        name = self.add_product_name_entry.get().strip()
        cost_price_str = self.add_cost_price_entry.get().strip()
        selling_price_str = self.add_selling_price_entry.get().strip()
        stock_str = self.add_stock_entry.get().strip()
        unit = self.add_unit_combo.get()
        barcode = self.add_product_manual_barcode_entry.get().strip() or None

        if not all([name, cost_price_str, selling_price_str, stock_str]):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        try:
            cost_price = float(cost_price_str)
            selling_price = float(selling_price_str)
            stock = float(stock_str)
            if cost_price < 0 or selling_price < 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Prices and Stock must be positive numbers.")
            return

        if self.product_to_edit_id:
            # Update existing product
            if self.db.update_product(self.product_to_edit_id, name, cost_price, selling_price, stock, unit, barcode):
                messagebox.showinfo("Success", f"Product '{name}' updated successfully.")
                self.reset_add_product_form()
        else:
            # Add new product
            if self.db.add_product(name, cost_price, selling_price, stock, unit, barcode):
                messagebox.showinfo("Success", f"Product '{name}' added successfully.")
                self.reset_add_product_form()

        self.display_inventory() # Refresh inventory display
        self.add_product_barcode_entry.focus_set()

    def reset_add_product_form(self):
        """Clears the Add/Update Product form."""
        self.add_product_name_entry.delete(0, tk.END)
        self.add_cost_price_entry.delete(0, tk.END)
        self.add_selling_price_entry.delete(0, tk.END)
        self.add_stock_entry.delete(0, tk.END)
        self.add_unit_combo.set("packets")
        self.add_product_manual_barcode_entry.delete(0, tk.END)
        self.add_product_button.config(text="Add Product")
        self.product_to_edit_id = None

    # ==========================================================================
    # Make Sale Section
    # ==========================================================================
    def create_make_sale_section(self):
        """Sets up the 'Make Sale' tab with barcode scanner input."""
        self.cart = []

        main_frame = ttk.Frame(self.make_sale_frame)
        main_frame.pack(expand=True, fill="both")

        # Top section for barcode scanner and product list
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side="top", fill="x", pady=(0, 10))

        # Barcode scanner
        barcode_frame = ttk.LabelFrame(top_frame, text="Scan Barcode", padding="15")
        barcode_frame.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Label(barcode_frame, text="Scan product barcode:").pack(side="left", padx=5)
        self.make_sale_barcode_entry = ttk.Entry(barcode_frame, width=30)
        self.make_sale_barcode_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.make_sale_barcode_entry.bind("<Return>", self.on_barcode_scan_make_sale)

        # Product list
        products_frame = ttk.LabelFrame(main_frame, text="Available Products", padding="15")
        products_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.product_listbox = tk.Listbox(products_frame, selectmode=tk.SINGLE, font=("Segoe UI", 10), height=10)
        self.product_listbox.pack(expand=True, fill="both")

        # Action frame with radio buttons and entry
        action_frame = ttk.Frame(products_frame)
        action_frame.pack(pady=10)
        self.sale_mode = tk.StringVar(value="quantity")
        ttk.Radiobutton(action_frame, text="Sell by Quantity", variable=self.sale_mode, value="quantity", command=self.update_sale_mode_inputs).pack(side="left", padx=5)
        self.quantity_entry = ttk.Entry(action_frame, width=8, font=("Segoe UI", 10))
        self.quantity_entry.pack(side="left")
        self.quantity_entry.insert(0, "1")

        ttk.Radiobutton(action_frame, text="Sell by Amount", variable=self.sale_mode, value="amount", command=self.update_sale_mode_inputs).pack(side="left", padx=5)
        self.amount_entry = ttk.Entry(action_frame, width=8, font=("Segoe UI", 10))
        self.amount_entry.pack(side="left")
        self.amount_entry.insert(0, "0")
        self.amount_entry.config(state="disabled")

        ttk.Button(action_frame, text="Add to Cart", command=self.add_to_cart).pack(side="left", padx=10, ipadx=10, ipady=5)

        # Cart section
        cart_frame = ttk.LabelFrame(main_frame, text="Current Cart", padding="15")
        cart_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.cart_listbox = tk.Listbox(cart_frame, font=("Segoe UI", 10), height=10)
        self.cart_listbox.pack(expand=True, fill="both")
        self.cart_listbox.bind("<Double-Button-1>", self.remove_from_cart)

        # Buttons and total
        buttons_total_frame = ttk.Frame(main_frame)
        buttons_total_frame.pack(side="bottom", fill="x", pady=10)

        ttk.Button(buttons_total_frame, text="Remove Selected Item", command=self.remove_from_cart).pack(side="right", padx=5)
        
        total_frame = ttk.Frame(buttons_total_frame)
        total_frame.pack(side="left", padx=5)
        ttk.Label(total_frame, text="Total:", font=("Segoe UI", 14, "bold")).pack(side="left")
        self.total_label = ttk.Label(total_frame, text="Ksh 0.00", font=("Segoe UI", 14, "bold"), foreground="#007BFF")
        self.total_label.pack(side="left", padx=10)
        
        ttk.Button(buttons_total_frame, text="Complete Sale", command=self.complete_sale).pack(side="right", ipadx=20)

        self.refresh_product_list()

    def on_barcode_scan_make_sale(self, event=None):
        """Handles barcode scan in the Make Sale section."""
        barcode = self.make_sale_barcode_entry.get().strip()
        self.make_sale_barcode_entry.delete(0, tk.END)
        self.make_sale_barcode_entry.focus_set() # Keep focus on the barcode entry

        if not barcode:
            return

        product = self.db.get_product_by_barcode(barcode)

        if product:
            quantity = 1 # Assume 1 unit per scan
            product_id = product[0]

            # Check if item is already in cart, if so, update quantity
            for item in self.cart:
                if item['id'] == product_id:
                    item['quantity'] += quantity
                    self.update_cart_display()
                    return

            # If not in cart, add a new item
            self.cart.append({
                'id': product_id,
                'name': product[1],
                'price': product[3],
                'quantity': quantity,
                'unit': product[5]
            })
            self.update_cart_display()
        else:
            messagebox.showwarning("Product Not Found", f"No product found with barcode '{barcode}'.")


    def update_sale_mode_inputs(self):
        """Toggles the state of the quantity and amount entry fields."""
        mode = self.sale_mode.get()
        if mode == "quantity":
            self.quantity_entry.config(state="normal")
            self.amount_entry.config(state="disabled")
        else: # mode == "amount"
            self.quantity_entry.config(state="disabled")
            self.amount_entry.config(state="normal")

    def refresh_product_list(self):
        """Refreshes the list of available products, showing their units."""
        self.product_listbox.delete(0, tk.END)
        self.products = self.db.get_all_products()
        if not self.products:
            self.product_listbox.insert(tk.END, "No products available.")
        else:
            for product in self.products:
                item_text = f"ID:{product[0]} - {product[1]} | Price: Ksh {product[3]:.2f} | Stock: {product[4]} {product[5]}"
                self.product_listbox.insert(tk.END, item_text)


    def add_to_cart(self):
        """Adds a selected product to the cart with the specified quantity or amount."""
        selected_index = self.product_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a product to add.")
            return

        product = self.products[selected_index[0]]
        product_id = product[0]
        product_name = product[1]
        product_price = product[3]
        product_stock = product[4]
        product_unit = product[5]

        try:
            if self.sale_mode.get() == "quantity":
                quantity_str = self.quantity_entry.get().strip()
                if not quantity_str:
                    messagebox.showwarning("Warning", "Quantity cannot be empty.")
                    return
                quantity = float(quantity_str)
                if quantity <= 0:
                    messagebox.showwarning("Warning", "Quantity must be a positive number.")
                    return
                if quantity > product_stock:
                    messagebox.showwarning("Warning", f"Insufficient stock. Available: {product_stock} {product_unit}.")
                    return
                unit_price = product_price
            else: # sell by amount
                amount_str = self.amount_entry.get().strip()
                if not amount_str:
                    messagebox.showwarning("Warning", "Amount cannot be empty.")
                    return
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showwarning("Warning", "Amount must be a positive number.")
                    return
            
                unit_price = product_price
                quantity = amount / unit_price
                if quantity > product_stock:
                    # Re-calculate amount to be sold to match available stock
                    amount = product_stock * unit_price
                    quantity = product_stock
                    messagebox.showinfo("Note", f"Adjusting sale to available stock. Selling {quantity:.2f} {product_unit} for Ksh {amount:.2f}.")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for quantity or amount.")
            return

        # Check if product is already in the cart, if so, update quantity
        for item in self.cart:
            if item['id'] == product_id:
                if self.sale_mode.get() == "quantity":
                    if item['quantity'] + quantity > product_stock:
                        messagebox.showwarning("Warning", f"Adding this quantity exceeds available stock. Available: {product_stock} {product_unit}.")
                        return
                    item['quantity'] += quantity
                else: # sell by amount, overwrite quantity
                    if quantity > product_stock:
                        messagebox.showwarning("Warning", f"The amount you entered would exceed available stock. Available: {product_stock} {product_unit}.")
                        return
                    item['quantity'] = quantity
                self.update_cart_display()
                return

        # Add new item to cart
        self.cart.append({'id': product_id, 'name': product_name, 'price': unit_price, 'quantity': quantity, 'unit': product_unit})
        self.update_cart_display()

    def update_cart_display(self):
        """Refreshes the cart listbox and updates the total."""
        self.cart_listbox.delete(0, tk.END)
        total = 0.0
        for item in self.cart:
            item_total = item['price'] * item['quantity']
            total += item_total
            display_text = f"{item['name']} - {item['quantity']:.2f} {item['unit']} @ Ksh {item['price']:.2f} each | Total: Ksh {item_total:.2f}"
            self.cart_listbox.insert(tk.END, display_text)
        self.total_label.config(text=f"Ksh {total:.2f}")

    def remove_from_cart(self, event=None):
        """Removes the selected item from the cart."""
        selected_index = self.cart_listbox.curselection()
        if not selected_index:
            return
        self.cart.pop(selected_index[0])
        self.update_cart_display()

    def complete_sale(self):
        """Processes the sale, updates stock, and clears the cart."""
        if not self.cart:
            messagebox.showwarning("Warning", "The cart is empty.")
            return

        for item in self.cart:
            product = self.db.get_product_by_id(item['id'])
            if product:
                current_stock = product[4]
                new_stock = current_stock - item['quantity']
                self.db.update_stock(item['id'], new_stock)
                self.db.add_sale(item['id'], item['quantity'], item['price'])
            else:
                messagebox.showerror("Error", f"Product '{item['name']}' not found in database. Sale aborted for this item.")

        messagebox.showinfo("Success", "Sale completed successfully.")
        self.cart = []
        self.update_cart_display()
        self.refresh_product_list()

    # ==========================================================================
    # Inventory Section
    # ==========================================================================
    def create_inventory_section(self):
        """Sets up the 'Inventory' tab."""
        container = ttk.Frame(self.inventory_frame)
        container.pack(expand=True, fill="both")

        ttk.Label(container, text="Current Inventory", font=("Segoe UI", 18, "bold")).pack(pady=(0, 20))

        # Treeview to display inventory
        self.inventory_tree = ttk.Treeview(container, columns=("ID", "Name", "Cost Price", "Selling Price", "Stock", "Unit", "Barcode"), show="headings")
        self.inventory_tree.pack(expand=True, fill="both", padx=10)

        # Define column headings
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Cost Price", text="Cost Price")
        self.inventory_tree.heading("Selling Price", text="Selling Price")
        self.inventory_tree.heading("Stock", text="Stock")
        self.inventory_tree.heading("Unit", text="Unit")
        self.inventory_tree.heading("Barcode", text="Barcode")

        # Set column widths
        self.inventory_tree.column("ID", width=40, stretch=tk.NO)
        self.inventory_tree.column("Name", width=150)
        self.inventory_tree.column("Cost Price", width=80)
        self.inventory_tree.column("Selling Price", width=80)
        self.inventory_tree.column("Stock", width=60)
        self.inventory_tree.column("Unit", width=60)
        self.inventory_tree.column("Barcode", width=120)

        # Context menu for editing/deleting
        self.inventory_tree.bind("<Button-3>", self.show_inventory_context_menu)
        self.inventory_tree.bind("<Double-Button-1>", self.on_inventory_item_double_click)

        # Buttons below the treeview
        button_frame = ttk.Frame(container)
        button_frame.pack(fill="x", pady=10)
        ttk.Button(button_frame, text="Refresh", command=self.display_inventory).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Selected", command=self.on_edit_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.on_delete_product).pack(side="left", padx=5)
        
    def display_inventory(self):
        """Fetches and displays all products in the inventory treeview."""
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        products = self.db.get_all_products()
        if products:
            for product in products:
                # Format the prices for display
                formatted_product = (
                    product[0],
                    product[1],
                    f"Ksh {product[2]:.2f}",
                    f"Ksh {product[3]:.2f}",
                    product[4],
                    product[5],
                    product[6]
                )
                self.inventory_tree.insert("", "end", values=formatted_product)

    def show_inventory_context_menu(self, event):
        """Displays a context menu for the inventory treeview."""
        item = self.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_tree.selection_set(item)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Edit", command=self.on_edit_product)
            menu.add_command(label="Delete", command=self.on_delete_product)
            menu.tk_popup(event.x_root, event.y_root)

    def on_inventory_item_double_click(self, event):
        """Switches to the 'Add Product' tab and pre-fills the form for editing."""
        selected_item = self.inventory_tree.selection()
        if selected_item:
            item_data = self.inventory_tree.item(selected_item, "values")
            product_id = item_data[0]
            product = self.db.get_product_by_id(product_id)
            if product:
                self.product_to_edit_id = product[0]
                self.add_product_name_entry.delete(0, tk.END)
                self.add_product_name_entry.insert(0, product[1])
                self.add_cost_price_entry.delete(0, tk.END)
                self.add_cost_price_entry.insert(0, product[2])
                self.add_selling_price_entry.delete(0, tk.END)
                self.add_selling_price_entry.insert(0, product[3])
                self.add_stock_entry.delete(0, tk.END)
                self.add_stock_entry.insert(0, product[4])
                self.add_unit_combo.set(product[5])
                self.add_product_manual_barcode_entry.delete(0, tk.END)
                self.add_product_manual_barcode_entry.insert(0, product[6])
                
                self.add_product_button.config(text="Update Product")
                self.notebook.select(self.add_product_frame)


    def on_edit_product(self):
        """Triggered from a button to edit the selected product."""
        selected_item = self.inventory_tree.selection()
        if selected_item:
            item_data = self.inventory_tree.item(selected_item, "values")
            product_id = item_data[0]
            product = self.db.get_product_by_id(product_id)
            if product:
                self.product_to_edit_id = product[0]
                self.add_product_name_entry.delete(0, tk.END)
                self.add_product_name_entry.insert(0, product[1])
                self.add_cost_price_entry.delete(0, tk.END)
                self.add_cost_price_entry.insert(0, product[2])
                self.add_selling_price_entry.delete(0, tk.END)
                self.add_selling_price_entry.insert(0, product[3])
                self.add_stock_entry.delete(0, tk.END)
                self.add_stock_entry.insert(0, product[4])
                self.add_unit_combo.set(product[5])
                self.add_product_manual_barcode_entry.delete(0, tk.END)
                self.add_product_manual_barcode_entry.insert(0, product[6])
                
                self.add_product_button.config(text="Update Product")
                self.notebook.select(self.add_product_frame)


    def on_delete_product(self):
        """Deletes the selected product from the database."""
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return

        item_data = self.inventory_tree.item(selected_item, "values")
        product_id = item_data[0]
        product_name = item_data[1]

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{product_name}'?"):
            self.db.delete_product(product_id)
            messagebox.showinfo("Success", f"Product '{product_name}' deleted.")
            self.display_inventory()
            
    # ==========================================================================
    # Reports Section
    # ==========================================================================
    def create_reports_section(self):
        """Sets up the 'Sales Report' tab."""
        container = ttk.Frame(self.reports_frame)
        container.pack(expand=True, fill="both")

        ttk.Label(container, text="Sales Report", font=("Segoe UI", 18, "bold")).pack(pady=(0, 20))

        # Date selection frame
        date_frame = ttk.Frame(container)
        date_frame.pack(fill="x", pady=10)
        
        ttk.Label(date_frame, text="Select Report Type:").pack(side="left", padx=5)
        
        report_options = ["Daily", "Weekly", "Monthly", "Yearly"]
        self.sales_report_combo = ttk.Combobox(date_frame, values=report_options, state="readonly")
        self.sales_report_combo.set("Daily")
        self.sales_report_combo.pack(side="left", padx=5)
        self.sales_report_combo.bind("<<ComboboxSelected>>", self.update_sales_report)

        # Treeview for the report
        self.sales_tree = ttk.Treeview(container, columns=("Date", "Item", "Quantity", "Price", "Total Sale", "Profit"), show="headings")
        self.sales_tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.heading("Item", text="Item")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Price", text="Unit Price")
        self.sales_tree.heading("Total Sale", text="Total Sale (Ksh)")
        self.sales_tree.heading("Profit", text="Profit (Ksh)")
        
        self.sales_tree.column("Date", width=150, stretch=tk.NO)
        self.sales_tree.column("Item", width=150)
        self.sales_tree.column("Quantity", width=80, stretch=tk.NO)
        self.sales_tree.column("Price", width=80, stretch=tk.NO)
        self.sales_tree.column("Total Sale", width=100, stretch=tk.NO)
        self.sales_tree.column("Profit", width=100, stretch=tk.NO)

        # Summary labels
        summary_frame = ttk.Frame(container)
        summary_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(summary_frame, text="Summary:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        self.sales_total_label = ttk.Label(summary_frame, text="Total Sales: Ksh 0.00", font=("Segoe UI", 12))
        self.sales_total_label.pack(side="left", padx=10)
        self.sales_profit_label = ttk.Label(summary_frame, text="Total Profit: Ksh 0.00", font=("Segoe UI", 12))
        self.sales_profit_label.pack(side="left", padx=10)

        self.update_sales_report()

    def update_sales_report(self, event=None):
        """Updates the sales report based on the selected time frame."""
        report_type = self.sales_report_combo.get().lower()
        self.sales_report_type = report_type
        self.set_sales_report_view(report_type)
        
    def set_sales_report_view(self, report_type):
        today = datetime.now().date()
        
        if report_type == "daily":
            start_date = today
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif report_type == "weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7) - timedelta(seconds=1)
        elif report_type == "monthly":
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day) + timedelta(days=1) - timedelta(seconds=1)
        elif report_type == "yearly":
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31) + timedelta(days=1) - timedelta(seconds=1)

        start_str = start_date.strftime("%Y-%m-%d 00:00:00")
        end_str = end_date.strftime("%Y-%m-%d 23:59:59")
        
        self.refresh_sales_report(start_str, end_str)

    def refresh_sales_report(self, start_date_str, end_date_str):
        """Fetches and displays sales data within a date range."""
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
            
        sales = self.db.get_sales_report(start_date_str, end_date_str)
        total_sales = 0.0
        total_profit = 0.0
        
        for sale in sales:
            item_name, cost_price, quantity, unit_price, sale_datetime, unit = sale
            total_sale = quantity * unit_price
            profit = (unit_price - cost_price) * quantity
            
            total_sales += total_sale
            total_profit += profit
            
            # Format the date string for display
            formatted_date = datetime.strptime(sale_datetime, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

            self.sales_tree.insert("", "end", values=(
                formatted_date,
                item_name,
                f"{quantity:.2f} {unit}",
                f"{unit_price:.2f}",
                f"{total_sale:.2f}",
                f"{profit:.2f}"
            ))
            
        self.sales_total_label.config(text=f"Total Sales: Ksh {total_sales:.2f}")
        self.sales_profit_label.config(text=f"Total Profit: Ksh {total_profit:.2f}")

    # ==========================================================================
    # Milling Section
    # ==========================================================================
    def create_milling_section(self):
        """Sets up the 'Milling Section' tab."""
        container = ttk.Frame(self.milling_frame)
        container.pack(expand=True, fill="both")
        
        # Input Frame
        input_frame = ttk.LabelFrame(container, text="Milling Operation Input", padding=20)
        input_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        labels_entries = [
            ("Current Meter Reading (Units):", "current_reading_entry"),
            ("Previous Meter Reading (Units):", "previous_reading_entry"),
            ("Unit Cost (Ksh):", "unit_cost_entry"),
            ("Money Generated (Ksh):", "money_generated_entry"),
            ("Labour Percentage (%):", "labour_percentage_entry")
        ]
        
        for i, (label_text, entry_name) in enumerate(labels_entries):
            ttk.Label(input_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(input_frame)
            entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            setattr(self, entry_name, entry)
        
        # Bind events to update calculations
        self.current_reading_entry.bind("<KeyRelease>", self.update_milling_calculations)
        self.previous_reading_entry.bind("<KeyRelease>", self.update_milling_calculations)
        self.unit_cost_entry.bind("<KeyRelease>", self.update_milling_calculations)
        self.money_generated_entry.bind("<KeyRelease>", self.update_milling_calculations)
        self.labour_percentage_entry.bind("<KeyRelease>", self.update_milling_calculations)

        # Calculated values frame
        calc_frame = ttk.LabelFrame(input_frame, text="Calculated Values", padding=10)
        calc_frame.grid(row=len(labels_entries), columnspan=2, sticky="ew", pady=10)

        self.units_used_label = ttk.Label(calc_frame, text="Units Used: 0.0")
        self.units_used_label.pack(anchor="w")
        self.power_bill_label = ttk.Label(calc_frame, text="Power Bill: Ksh 0.00")
        self.power_bill_label.pack(anchor="w")
        self.labour_cost_label = ttk.Label(calc_frame, text="Labour Cost: Ksh 0.00")
        self.labour_cost_label.pack(anchor="w")
        self.profit_generated_label = ttk.Label(calc_frame, text="Profit Generated: Ksh 0.00")
        self.profit_generated_label.pack(anchor="w")
        
        # Save button
        ttk.Button(input_frame, text="Save Record", command=self.save_milling_record).grid(row=len(labels_entries) + 1, columnspan=2, pady=10, sticky="ew")

        # Report Frame
        report_frame = ttk.Frame(container)
        report_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        ttk.Label(report_frame, text="Milling Report", font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))

        # Report View Selection
        report_view_frame = ttk.Frame(report_frame)
        report_view_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(report_view_frame, text="Select Report Type:").pack(side="left", padx=5)
        report_options = ["Daily", "Weekly", "Monthly", "Yearly"]
        self.milling_report_combo = ttk.Combobox(report_view_frame, values=report_options, state="readonly")
        self.milling_report_combo.set("Daily")
        self.milling_report_combo.pack(side="left", padx=5)
        self.milling_report_combo.bind("<<ComboboxSelected>>", self.update_milling_report)

        # Report Treeview
        self.milling_tree = ttk.Treeview(report_frame, columns=("Date", "Units Used", "Power Bill", "Money Generated", "Labour Cost", "Labour %", "Profit"), show="headings")
        self.milling_tree.pack(expand=True, fill="both", padx=5)

        self.milling_tree.heading("Date", text="Date & Time")
        self.milling_tree.heading("Units Used", text="Units Used")
        self.milling_tree.heading("Power Bill", text="Power Bill (Ksh)")
        self.milling_tree.heading("Money Generated", text="Money Generated (Ksh)")
        self.milling_tree.heading("Labour Cost", text="Labour Cost (Ksh)")
        self.milling_tree.heading("Labour %", text="Labour %")
        self.milling_tree.heading("Profit", text="Profit (Ksh)")

        self.milling_tree.column("Date", width=150, stretch=tk.NO)
        self.milling_tree.column("Units Used", width=80, stretch=tk.NO)
        self.milling_tree.column("Power Bill", width=90, stretch=tk.NO)
        self.milling_tree.column("Money Generated", width=110, stretch=tk.NO)
        self.milling_tree.column("Labour Cost", width=90, stretch=tk.NO)
        self.milling_tree.column("Labour %", width=70, stretch=tk.NO)
        self.milling_tree.column("Profit", width=90, stretch=tk.NO)
        
        # Summary labels
        milling_summary_frame = ttk.Frame(report_frame)
        milling_summary_frame.pack(fill="x", pady=10)
        
        ttk.Label(milling_summary_frame, text="Summary:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        self.milling_total_profit_label = ttk.Label(milling_summary_frame, text="Total Profit: Ksh 0.00", font=("Segoe UI", 12))
        self.milling_total_profit_label.pack(side="left", padx=10)
        self.milling_total_units_label = ttk.Label(milling_summary_frame, text="Total Units: 0.0", font=("Segoe UI", 12))
        self.milling_total_units_label.pack(side="left", padx=10)

        self.load_milling_settings()
        self.set_milling_report_view('daily')
        
    def load_milling_settings(self):
        """Loads last-used values from the settings table."""
        try:
            prev_reading = self.db.get_setting("milling_prev_reading")
            unit_cost = self.db.get_setting("milling_unit_cost")
            labour_percentage = self.db.get_setting("milling_labour_percentage")

            if prev_reading:
                self.previous_reading_entry.delete(0, tk.END)
                self.previous_reading_entry.insert(0, prev_reading)
            if unit_cost:
                self.unit_cost_entry.delete(0, tk.END)
                self.unit_cost_entry.insert(0, unit_cost)
            if labour_percentage:
                self.labour_percentage_entry.delete(0, tk.END)
                self.labour_percentage_entry.insert(0, labour_percentage)
        except Exception as e:
            # Handle potential errors if settings table or keys don't exist yet
            print(f"Error loading milling settings: {e}")
            
    def update_milling_calculations(self, event=None):
        """Calculates and updates milling metrics as the user types."""
        try:
            current_reading = float(self.current_reading_entry.get() or 0)
            previous_reading = float(self.previous_reading_entry.get() or 0)
            unit_cost = float(self.unit_cost_entry.get() or 0)
            money_generated = float(self.money_generated_entry.get() or 0)
            labour_percentage = float(self.labour_percentage_entry.get() or 0)

            # Calculations
            units_used = max(0, current_reading - previous_reading)
            power_bill = units_used * unit_cost
            
            # Use the new formula
            self.calculated_labour_cost = (money_generated - power_bill) * (labour_percentage / 100)
            
            self.calculated_profit_generated = money_generated - power_bill - self.calculated_labour_cost

            # Update labels
            self.units_used_label.config(text=f"Units Used: {units_used:.2f}")
            self.power_bill_label.config(text=f"Power Bill: Ksh {power_bill:.2f}")
            self.labour_cost_label.config(text=f"Labour Cost: Ksh {self.calculated_labour_cost:.2f}")
            self.profit_generated_label.config(text=f"Profit Generated: Ksh {self.calculated_profit_generated:.2f}")

        except ValueError:
            # Clear or show error for invalid inputs
            self.units_used_label.config(text="Units Used: Invalid Input")
            self.power_bill_label.config(text="Power Bill: Invalid Input")
            self.labour_cost_label.config(text="Labour Cost: Invalid Input")
            self.profit_generated_label.config(text="Profit Generated: Invalid Input")
            
    def save_milling_record(self):
        """Saves the current milling record to the database."""
        try:
            current_reading = float(self.current_reading_entry.get() or 0)
            previous_reading = float(self.previous_reading_entry.get() or 0)
            unit_cost = float(self.unit_cost_entry.get() or 0)
            money_generated = float(self.money_generated_entry.get() or 0)
            labour_percentage = float(self.labour_percentage_entry.get() or 0)

            units_used = max(0, current_reading - previous_reading)
            power_bill = units_used * unit_cost
            
            # Use the new formula
            labour_cost = (money_generated - power_bill) * (labour_percentage / 100)
            
            if current_reading <= previous_reading:
                messagebox.showerror("Error", "Current reading must be greater than previous reading.")
                return
                
            self.db.add_milling_record(
                current_reading,
                previous_reading,
                unit_cost,
                units_used,
                power_bill,
                labour_cost,
                money_generated,
                labour_percentage
            )
            
            # Save the last used values
            self.db.set_setting("milling_prev_reading", str(current_reading))
            self.db.set_setting("milling_unit_cost", str(unit_cost))
            self.db.set_setting("milling_labour_percentage", str(labour_percentage))

            messagebox.showinfo("Success", "Milling record saved successfully!")
            
            # Refresh the report and clear the current reading input
            self.set_milling_report_view(self.milling_report_type)
            self.current_reading_entry.delete(0, tk.END)
            self.money_generated_entry.delete(0, tk.END)
            self.previous_reading_entry.delete(0, tk.END)
            self.previous_reading_entry.insert(0, str(current_reading))
            self.update_milling_calculations()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields.")
            
    def update_milling_report(self, event=None):
        """Updates the milling report based on the selected time frame."""
        report_type = self.milling_report_combo.get().lower()
        self.milling_report_type = report_type
        self.set_milling_report_view(report_type)

    def set_milling_report_view(self, report_type):
        today = datetime.now().date()
        
        if report_type == "daily":
            start_date = today
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif report_type == "weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7) - timedelta(seconds=1)
        elif report_type == "monthly":
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day) + timedelta(days=1) - timedelta(seconds=1)
        elif report_type == "yearly":
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31) + timedelta(days=1) - timedelta(seconds=1)
            
        start_str = start_date.strftime("%Y-%m-%d 00:00:00")
        end_str = end_date.strftime("%Y-%m-%d 23:59:59")
        
        self.refresh_milling_report(start_str, end_str)

    def refresh_milling_report(self, start_date_str, end_date_str):
        """Fetches and displays milling data within a date range."""
        for item in self.milling_tree.get_children():
            self.milling_tree.delete(item)
        
        records = self.db.get_milling_report(start_date_str, end_date_str)
        total_profit = 0.0
        total_units_used = 0.0
        
        for record in records:
            start_datetime, end_datetime, current_reading, previous_reading, units_used, power_bill, labour_cost, money_generated, labour_percentage = record
            
            # Calculate profit from the stored values
            profit = money_generated - power_bill - labour_cost
            
            total_profit += profit
            total_units_used += units_used
            
            # Format the start date for display
            formatted_date = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

            self.milling_tree.insert("", "end", values=(
                formatted_date,
                f"{units_used:.2f}",
                f"{power_bill:.2f}",
                f"{money_generated:.2f}",
                f"{labour_cost:.2f}",
                f"{labour_percentage:.2f}",
                f"{profit:.2f}"
            ))
            
        self.milling_total_profit_label.config(text=f"Total Profit: Ksh {total_profit:.2f}")
        self.milling_total_units_label.config(text=f"Total Units: {total_units_used:.2f}")


if __name__ == "__main__":
    db = Database()
    app = POSApp(db)
    app.mainloop()
    db.close()
