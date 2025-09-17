import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class OrderTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Order Tracker")
        self.root.geometry("800x600")
        
        # Initialize database
        self.init_database()
        
        # Create main interface
        self.create_widgets()
        
        # Load customers into combobox
        self.refresh_customer_list()
        self.refresh_customer_filter()
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect('orders.db')
        self.cursor = self.conn.cursor()
        
        # Create customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        
        # Create orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                account_number TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                date_added TEXT NOT NULL,
                printed INTEGER DEFAULT 0,
                FOREIGN KEY (account_number) REFERENCES customers (account_number)
            )
        ''')
        
        self.conn.commit()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Orders tab
        orders_frame = ttk.Frame(notebook)
        notebook.add(orders_frame, text='Orders')
        self.create_orders_tab(orders_frame)
        
        # Customers tab
        customers_frame = ttk.Frame(notebook)
        notebook.add(customers_frame, text='Customers')
        self.create_customers_tab(customers_frame)
        
    def create_orders_tab(self, parent):
        """Create the orders tracking tab"""
        # Input frame
        input_frame = ttk.LabelFrame(parent, text="Add New Order", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Order number
        ttk.Label(input_frame, text="Order Number:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.order_entry = ttk.Entry(input_frame, width=30)
        self.order_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        
        # Account number with autocomplete
        ttk.Label(input_frame, text="Account Number:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.account_entry = ttk.Entry(input_frame, width=30)
        self.account_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.account_entry.bind('<KeyRelease>', self.on_account_change)
        
        # Customer name (auto-filled)
        ttk.Label(input_frame, text="Customer Name:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.customer_name_var = tk.StringVar()
        self.customer_label = ttk.Label(input_frame, textvariable=self.customer_name_var, 
                                       background='lightgray', relief='sunken', padding=5)
        self.customer_label.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        
        # Date (auto-filled)
        ttk.Label(input_frame, text="Date:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_label = ttk.Label(input_frame, textvariable=self.date_var, 
                                   background='lightgray', relief='sunken', padding=5)
        self.date_label.grid(row=3, column=1, padx=5, pady=2, sticky='ew')
        
        # Printed checkbox
        self.printed_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Already Printed", variable=self.printed_var).grid(row=4, column=0, columnspan=2, pady=2)
        
        # Add button
        ttk.Button(input_frame, text="Add Order", command=self.add_order).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Configure column weights
        input_frame.columnconfigure(1, weight=1)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(parent, text="Filters", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        # Date filters
        ttk.Label(filter_frame, text="From Date:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.from_date_var = tk.StringVar()
        self.from_date_entry = ttk.Entry(filter_frame, textvariable=self.from_date_var, width=15)
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="To Date:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.to_date_var = tk.StringVar()
        self.to_date_entry = ttk.Entry(filter_frame, textvariable=self.to_date_var, width=15)
        self.to_date_entry.grid(row=0, column=3, padx=5, pady=2)
        
        # Customer filter
        ttk.Label(filter_frame, text="Customer:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.customer_filter_var = tk.StringVar()
        self.customer_filter = ttk.Combobox(filter_frame, textvariable=self.customer_filter_var, width=25)
        self.customer_filter.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        # Printed status filter
        ttk.Label(filter_frame, text="Show:").grid(row=1, column=3, sticky='w', padx=5, pady=2)
        self.status_filter_var = tk.StringVar(value="All")
        self.status_filter = ttk.Combobox(filter_frame, textvariable=self.status_filter_var, 
                                         values=["All", "Printed", "Not Printed"], width=15)
        self.status_filter.grid(row=1, column=4, padx=5, pady=2)
        
        # Filter buttons
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.grid(row=2, column=0, columnspan=5, pady=10)
        
        ttk.Button(filter_buttons_frame, text="Apply Filters", command=self.apply_filters).pack(side='left', padx=5)
        ttk.Button(filter_buttons_frame, text="Clear Filters", command=self.clear_filters).pack(side='left', padx=5)
        ttk.Button(filter_buttons_frame, text="Today's Orders", command=self.show_today_orders).pack(side='left', padx=5)
        
        # Configure filter frame column weights
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(2, weight=1)
        
        # Orders list frame
        list_frame = ttk.LabelFrame(parent, text="Orders", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for orders
        columns = ('Order#', 'Account#', 'Customer', 'Date', 'Printed')
        self.orders_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.orders_tree.heading(col, text=col)
            if col == 'Order#':
                self.orders_tree.column(col, width=120)
            elif col == 'Account#':
                self.orders_tree.column(col, width=120)
            elif col == 'Customer':
                self.orders_tree.column(col, width=200)
            elif col == 'Date':
                self.orders_tree.column(col, width=100)
            elif col == 'Printed':
                self.orders_tree.column(col, width=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click to toggle printed status
        self.orders_tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Toggle Printed", command=self.toggle_printed).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete Order", command=self.delete_order).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_orders).pack(side='left', padx=5)
        
        # Load orders
        self.refresh_orders()
        
    def create_customers_tab(self, parent):
        """Create the customers management tab"""
        # Input frame
        input_frame = ttk.LabelFrame(parent, text="Add New Customer", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="Account Number:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.cust_account_entry = ttk.Entry(input_frame, width=30)
        self.cust_account_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(input_frame, text="Customer Name:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.cust_name_entry = ttk.Entry(input_frame, width=30)
        self.cust_name_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Button(input_frame, text="Add Customer", command=self.add_customer).grid(row=2, column=0, columnspan=2, pady=10)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Customers list frame
        list_frame = ttk.LabelFrame(parent, text="Customers", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for customers
        columns = ('Account#', 'Customer Name')
        self.customers_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=200)
        
        # Scrollbar
        cust_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=cust_scrollbar.set)
        
        self.customers_tree.pack(side='left', fill='both', expand=True)
        cust_scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        cust_buttons_frame = ttk.Frame(parent)
        cust_buttons_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(cust_buttons_frame, text="Delete Customer", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(cust_buttons_frame, text="Refresh", command=self.refresh_customers).pack(side='left', padx=5)
        
        # Load customers
        self.refresh_customers()
        
    def on_account_change(self, event=None):
        """Handle account number input to auto-fill customer name"""
        account_num = self.account_entry.get().strip()
        if account_num:
            self.cursor.execute("SELECT name FROM customers WHERE account_number = ?", (account_num,))
            result = self.cursor.fetchone()
            if result:
                self.customer_name_var.set(result[0])
            else:
                self.customer_name_var.set("Customer not found")
        else:
            self.customer_name_var.set("")
            
    def add_order(self):
        """Add a new order to the database"""
        order_num = self.order_entry.get().strip()
        account_num = self.account_entry.get().strip()
        customer_name = self.customer_name_var.get().strip()
        printed_status = 1 if self.printed_var.get() else 0
        
        if not order_num or not account_num:
            messagebox.showerror("Error", "Please enter both Order Number and Account Number")
            return
            
        if customer_name == "Customer not found" or not customer_name:
            messagebox.showerror("Error", "Please select a valid customer account")
            return
            
        try:
            self.cursor.execute("""
                INSERT INTO orders (order_number, account_number, customer_name, date_added, printed)
                VALUES (?, ?, ?, ?, ?)
            """, (order_num, account_num, customer_name, self.date_var.get(), printed_status))
            
            self.conn.commit()
            
            # Clear inputs
            self.order_entry.delete(0, tk.END)
            self.account_entry.delete(0, tk.END)
            self.customer_name_var.set("")
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
            self.printed_var.set(False)
            
            self.refresh_orders()
            messagebox.showinfo("Success", "Order added successfully!")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Order number already exists!")
            
    def add_customer(self):
        """Add a new customer to the database"""
        account_num = self.cust_account_entry.get().strip()
        name = self.cust_name_entry.get().strip()
        
        if not account_num or not name:
            messagebox.showerror("Error", "Please enter both Account Number and Customer Name")
            return
            
        try:
            self.cursor.execute("INSERT INTO customers (account_number, name) VALUES (?, ?)", 
                              (account_num, name))
            self.conn.commit()
            
            # Clear inputs
            self.cust_account_entry.delete(0, tk.END)
            self.cust_name_entry.delete(0, tk.END)
            
            self.refresh_customers()
            self.refresh_customer_list()
            self.refresh_customer_filter()
            messagebox.showinfo("Success", "Customer added successfully!")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Account number already exists!")
            
    def toggle_printed(self):
        """Toggle the printed status of selected order"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order")
            return
            
        item = self.orders_tree.item(selected[0])
        order_num = item['values'][0]
        
        # Get current printed status
        self.cursor.execute("SELECT printed FROM orders WHERE order_number = ?", (order_num,))
        current_status = self.cursor.fetchone()[0]
        new_status = 1 - current_status  # Toggle between 0 and 1
        
        self.cursor.execute("UPDATE orders SET printed = ? WHERE order_number = ?", 
                          (new_status, order_num))
        self.conn.commit()
        self.refresh_orders()
        
    def on_double_click(self, event):
        """Handle double-click on treeview items"""
        item = self.orders_tree.identify_row(event.y)
        if item:
            column = self.orders_tree.identify_column(event.x)
            if column == '#5':  # Printed column (1-indexed)
                # Select the item and toggle printed status
                self.orders_tree.selection_set(item)
                self.toggle_printed()
            
    def on_checkbox_change(self, order_number, var):
        """Handle checkbox state change"""
        new_status = 1 if var.get() else 0
        self.cursor.execute("UPDATE orders SET printed = ? WHERE order_number = ?", 
                          (new_status, order_number))
        self.conn.commit()
        
    def scroll_both(self, *args):
        """Scroll both treeview and checkboxes together"""
        self.orders_tree.yview(*args)
        # Update checkbox positions when scrolling
        self.update_checkbox_positions()
        
    def update_scrollbar(self, *args):
        """Update scrollbar and checkbox positions"""
        # Update checkbox positions when scrollbar changes
        self.root.after_idle(self.update_checkbox_positions)
        
    def update_checkbox_positions(self):
        """Update checkbox positions to align with treeview rows"""
        # Clear existing checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        self.printed_checkboxes.clear()
        
        # Get visible items
        visible_items = []
        for item_id in self.orders_tree.get_children():
            bbox = self.orders_tree.bbox(item_id)
            if bbox:  # Item is visible
                visible_items.append(item_id)
        
        # Create checkboxes for visible items
        for i, item_id in enumerate(visible_items):
            item_data = self.orders_tree.item(item_id)
            order_number = item_data['values'][0]
            
            # Get current printed status from database
            self.cursor.execute("SELECT printed FROM orders WHERE order_number = ?", (order_number,))
            result = self.cursor.fetchone()
            is_printed = bool(result[0]) if result else False
            
            # Create checkbox variable
            var = tk.BooleanVar(value=is_printed)
            self.checkbox_vars[order_number] = var
            
            # Create checkbox
            checkbox = ttk.Checkbutton(self.checkbox_frame, variable=var,
                                     command=lambda on=order_number, v=var: self.on_checkbox_change(on, v))
            checkbox.pack(pady=(2, 0), anchor='w')
            self.printed_checkboxes[order_number] = checkbox
            
    def on_tree_click(self, event):
        """Handle tree click events"""
        # Update checkbox positions after any tree interaction
        self.root.after_idle(self.update_checkbox_positions)
        
    def delete_order(self):
        """Delete selected order"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this order?"):
            item = self.orders_tree.item(selected[0])
            order_num = item['values'][0]
            
            self.cursor.execute("DELETE FROM orders WHERE order_number = ?", (order_num,))
            self.conn.commit()
            self.refresh_orders()
            
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
            item = self.customers_tree.item(selected[0])
            account_num = item['values'][0]
            
            # Check if customer has orders
            self.cursor.execute("SELECT COUNT(*) FROM orders WHERE account_number = ?", (account_num,))
            order_count = self.cursor.fetchone()[0]
            
            if order_count > 0:
                messagebox.showerror("Error", f"Cannot delete customer. They have {order_count} orders.")
                return
                
            self.cursor.execute("DELETE FROM customers WHERE account_number = ?", (account_num,))
            self.conn.commit()
            self.refresh_customers()
            self.refresh_customer_list()
            self.refresh_customer_filter()
            
    def refresh_orders(self):
        """Refresh the orders list"""
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
            
        # Load orders from database
        self.cursor.execute("""
            SELECT order_number, account_number, customer_name, date_added, printed 
            FROM orders ORDER BY date_added DESC
        """)
        
        for row in self.cursor.fetchall():
            printed_status = "☑" if row[4] else "☐"
            self.orders_tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], printed_status))
            
    def refresh_customers(self):
        """Refresh the customers list"""
        # Clear existing items
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
            
        # Load customers from database
        self.cursor.execute("SELECT account_number, name FROM customers ORDER BY name")
        
        for row in self.cursor.fetchall():
            self.customers_tree.insert('', 'end', values=row)
            
    def refresh_customer_list(self):
        """Refresh customer data for autocomplete"""
        pass  # This could be used for more advanced autocomplete features
        
    def refresh_customer_filter(self):
        """Refresh customer filter dropdown"""
        self.cursor.execute("SELECT DISTINCT name FROM customers ORDER BY name")
        customers = ['All'] + [row[0] for row in self.cursor.fetchall()]
        self.customer_filter['values'] = customers
        
    def apply_filters(self):
        """Apply filters to the orders display"""
        # Build query based on filters
        query = """
            SELECT order_number, account_number, customer_name, date_added, printed 
            FROM orders WHERE 1=1
        """
        params = []
        
        # Date filters
        from_date = self.from_date_var.get().strip()
        to_date = self.to_date_var.get().strip()
        
        if from_date:
            query += " AND date_added >= ?"
            params.append(from_date)
            
        if to_date:
            query += " AND date_added <= ?"
            params.append(to_date)
            
        # Customer filter
        customer_filter = self.customer_filter_var.get().strip()
        if customer_filter and customer_filter != "All":
            query += " AND customer_name = ?"
            params.append(customer_filter)
            
        # Status filter
        status_filter = self.status_filter_var.get().strip()
        if status_filter == "Printed":
            query += " AND printed = 1"
        elif status_filter == "Not Printed":
            query += " AND printed = 0"
            
        query += " ORDER BY date_added DESC"
        
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
            
        # Load filtered orders
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            printed_status = "☑" if row[4] else "☐"
            self.orders_tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], printed_status))
            
    def clear_filters(self):
        """Clear all filters and show all orders"""
        self.from_date_var.set("")
        self.to_date_var.set("")
        self.customer_filter_var.set("All")
        self.status_filter_var.set("All")
        self.refresh_orders()
        
    def show_today_orders(self):
        """Show only today's orders"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.from_date_var.set(today)
        self.to_date_var.set(today)
        self.customer_filter_var.set("All")
        self.status_filter_var.set("All")
        self.apply_filters()
        
    def on_closing(self):
        """Handle application closing"""
        self.conn.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = OrderTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()