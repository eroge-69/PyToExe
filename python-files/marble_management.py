"""
Marble Company Management System (single-file)
Features:
- SQLite backend (marble.db)
- Customers, Suppliers, Products (inventory)
- Purchases (increasing stock), Sales (decreasing stock) with line items
- Payments for customers and suppliers
- Basic reports and CSV export
- Simple Tkinter GUI with ttk

Run: python marble_management.py
Requires: Python 3.8+ (no external packages)
"""

import os
import sqlite3
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_FILE = 'marble.db'

# ---------- Database layer ----------
class DB:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._create()

    def _create(self):
        c = self.conn.cursor()
        # Customers
        c.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            address TEXT,
            email TEXT,
            created_at TEXT
        )''')
        # Suppliers
        c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            address TEXT,
            email TEXT,
            created_at TEXT
        )''')
        # Products (marble types / slabs)
        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            name TEXT,
            description TEXT,
            unit TEXT,
            cost_price REAL,
            sale_price REAL,
            stock REAL DEFAULT 0,
            created_at TEXT
        )''')
        # Purchases
        c.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER,
            invoice_no TEXT,
            date TEXT,
            total REAL,
            created_at TEXT,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER,
            product_id INTEGER,
            qty REAL,
            rate REAL,
            amount REAL,
            FOREIGN KEY(purchase_id) REFERENCES purchases(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )''')
        # Sales
        c.execute('''CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            invoice_no TEXT,
            date TEXT,
            total REAL,
            created_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            qty REAL,
            rate REAL,
            amount REAL,
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )''')
        # Payments
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_type TEXT, -- 'customer' or 'supplier'
            party_id INTEGER,
            amount REAL,
            method TEXT,
            date TEXT,
            remarks TEXT,
            created_at TEXT
        )''')
        self.conn.commit()

    # Customers
    def add_customer(self, name, contact, address, email):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute('INSERT INTO customers (name, contact, address, email, created_at) VALUES (?, ?, ?, ?, ?)', (name, contact, address, email, now))
        self.conn.commit()
        return c.lastrowid

    def update_customer(self, cid, **kwargs):
        c = self.conn.cursor()
        cols = ', '.join(f"{k}=?" for k in kwargs.keys())
        vals = list(kwargs.values()) + [cid]
        c.execute(f'UPDATE customers SET {cols} WHERE id=?', vals)
        self.conn.commit()

    def delete_customer(self, cid):
        c = self.conn.cursor()
        c.execute('DELETE FROM customers WHERE id=?', (cid,))
        self.conn.commit()

    def list_customers(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM customers ORDER BY name')
        return c.fetchall()

    def search_customers(self, term):
        like = f'%{term}%'
        c = self.conn.cursor()
        c.execute('SELECT * FROM customers WHERE name LIKE ? OR contact LIKE ? ORDER BY name', (like, like))
        return c.fetchall()

    # Suppliers
    def add_supplier(self, name, contact, address, email):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute('INSERT INTO suppliers (name, contact, address, email, created_at) VALUES (?, ?, ?, ?, ?)', (name, contact, address, email, now))
        self.conn.commit()
        return c.lastrowid

    def list_suppliers(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM suppliers ORDER BY name')
        return c.fetchall()

    # Products
    def add_product(self, sku, name, description, unit, cost_price, sale_price, stock=0):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute('INSERT INTO products (sku, name, description, unit, cost_price, sale_price, stock, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (sku, name, description, unit, cost_price, sale_price, stock, now))
        self.conn.commit()
        return c.lastrowid

    def update_product(self, pid, **kwargs):
        c = self.conn.cursor()
        cols = ', '.join(f"{k}=?" for k in kwargs.keys())
        vals = list(kwargs.values()) + [pid]
        c.execute(f'UPDATE products SET {cols} WHERE id=?', vals)
        self.conn.commit()

    def list_products(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM products ORDER BY name')
        return c.fetchall()

    def get_product(self, pid):
        c = self.conn.cursor()
        c.execute('SELECT * FROM products WHERE id=?', (pid,))
        return c.fetchone()

    def search_products(self, term):
        like = f'%{term}%'
        c = self.conn.cursor()
        c.execute('SELECT * FROM products WHERE sku LIKE ? OR name LIKE ? ORDER BY name', (like, like))
        return c.fetchall()

    # Purchases (increase stock)
    def add_purchase(self, supplier_id, invoice_no, date, items):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        total = sum(it['qty'] * it['rate'] for it in items)
        c.execute('INSERT INTO purchases (supplier_id, invoice_no, date, total, created_at) VALUES (?, ?, ?, ?, ?)', (supplier_id, invoice_no, date, total, now))
        pid = c.lastrowid
        for it in items:
            amount = it['qty'] * it['rate']
            c.execute('INSERT INTO purchase_items (purchase_id, product_id, qty, rate, amount) VALUES (?, ?, ?, ?, ?)', (pid, it['product_id'], it['qty'], it['rate'], amount))
            # update stock
            c.execute('UPDATE products SET stock = stock + ? WHERE id=?', (it['qty'], it['product_id']))
        self.conn.commit()
        return pid

    # Sales (decrease stock)
    def add_sale(self, customer_id, invoice_no, date, items):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        total = sum(it['qty'] * it['rate'] for it in items)
        # simple stock check
        for it in items:
            c.execute('SELECT stock FROM products WHERE id=?', (it['product_id'],))
            row = c.fetchone()
            if not row or row['stock'] < it['qty']:
                raise ValueError(f"Insufficient stock for product id {it['product_id']}")
        c.execute('INSERT INTO sales (customer_id, invoice_no, date, total, created_at) VALUES (?, ?, ?, ?, ?)', (customer_id, invoice_no, date, total, now))
        sid = c.lastrowid
        for it in items:
            amount = it['qty'] * it['rate']
            c.execute('INSERT INTO sale_items (sale_id, product_id, qty, rate, amount) VALUES (?, ?, ?, ?, ?)', (sid, it['product_id'], it['qty'], it['rate'], amount))
            # update stock
            c.execute('UPDATE products SET stock = stock - ? WHERE id=?', (it['qty'], it['product_id']))
        self.conn.commit()
        return sid

    # Payments
    def add_payment(self, party_type, party_id, amount, method, date, remarks=None):
        c = self.conn.cursor()
        now = datetime.now().isoformat()
        c.execute('INSERT INTO payments (party_type, party_id, amount, method, date, remarks, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', (party_type, party_id, amount, method, date, remarks, now))
        self.conn.commit()
        return c.lastrowid

    # Reporting helpers
    def export_table(self, table, path):
        c = self.conn.cursor()
        c.execute(f'SELECT * FROM {table}')
        rows = c.fetchall()
        if not rows:
            raise ValueError('No data to export')
        cols = rows[0].keys()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            for r in rows:
                writer.writerow([r[c] for c in cols])

# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.title('Marble Company Management')
        self.geometry('1100x700')
        self._build()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)

        self.cust_tab = ttk.Frame(nb); nb.add(self.cust_tab, text='Customers')
        self.prod_tab = ttk.Frame(nb); nb.add(self.prod_tab, text='Products')
        self.purchase_tab = ttk.Frame(nb); nb.add(self.purchase_tab, text='Purchases')
        self.sales_tab = ttk.Frame(nb); nb.add(self.sales_tab, text='Sales')
        self.pay_tab = ttk.Frame(nb); nb.add(self.pay_tab, text='Payments')
        self.report_tab = ttk.Frame(nb); nb.add(self.report_tab, text='Reports')

        self._customers_ui(self.cust_tab)
        self._products_ui(self.prod_tab)
        self._purchases_ui(self.purchase_tab)
        self._sales_ui(self.sales_tab)
        self._payments_ui(self.pay_tab)
        self._reports_ui(self.report_tab)

    # Customers UI
    def _customers_ui(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='New Customer', command=self._open_customer_form).pack(side='right')
        ttk.Label(top, text='Search:').pack(side='left')
        self.cust_search = tk.StringVar()
        ttk.Entry(top, textvariable=self.cust_search).pack(side='left', padx=4)
        ttk.Button(top, text='Go', command=self._search_customers).pack(side='left')

        cols = ('id','name','contact','email','address')
        self.cust_tree = ttk.Treeview(parent, columns=cols, show='headings')
        for c in cols:
            self.cust_tree.heading(c, text=c.title())
            self.cust_tree.column(c, width=150)
        self.cust_tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.cust_tree.bind('<Double-1>', self._edit_customer)
        ttk.Button(parent, text='Export CSV', command=lambda: self._export_table('customers')).pack(side='right', padx=8, pady=6)
        self._load_customers()

    def _load_customers(self):
        for i in self.cust_tree.get_children(): self.cust_tree.delete(i)
        for r in self.db.list_customers():
            self.cust_tree.insert('', 'end', values=(r['id'], r['name'], r['contact'], r['email'], r['address']))

    def _search_customers(self):
        term = self.cust_search.get().strip()
        for i in self.cust_tree.get_children(): self.cust_tree.delete(i)
        if not term:
            self._load_customers(); return
        for r in self.db.search_customers(term):
            self.cust_tree.insert('', 'end', values=(r['id'], r['name'], r['contact'], r['email'], r['address']))

    def _open_customer_form(self):
        CustomerForm(self, self.db)

    def _edit_customer(self, event):
        sel = self.cust_tree.selection();
        if not sel: return
        cid = self.cust_tree.item(sel[0])['values'][0]
        CustomerForm(self, self.db, cid)

    # Products UI
    def _products_ui(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='New Product', command=self._open_product_form).pack(side='right')
        ttk.Label(top, text='Search:').pack(side='left')
        self.prod_search = tk.StringVar()
        ttk.Entry(top, textvariable=self.prod_search).pack(side='left', padx=4)
        ttk.Button(top, text='Go', command=self._search_products).pack(side='left')

        cols = ('id','sku','name','unit','cost_price','sale_price','stock')
        self.prod_tree = ttk.Treeview(parent, columns=cols, show='headings')
        for c in cols:
            self.prod_tree.heading(c, text=c.title())
            self.prod_tree.column(c, width=120)
        self.prod_tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.prod_tree.bind('<Double-1>', self._edit_product)
        ttk.Button(parent, text='Export CSV', command=lambda: self._export_table('products')).pack(side='right', padx=8, pady=6)
        self._load_products()

    def _load_products(self):
        for i in self.prod_tree.get_children(): self.prod_tree.delete(i)
        for r in self.db.list_products():
            self.prod_tree.insert('', 'end', values=(r['id'], r['sku'], r['name'], r['unit'], r['cost_price'], r['sale_price'], r['stock']))

    def _search_products(self):
        term = self.prod_search.get().strip()
        for i in self.prod_tree.get_children(): self.prod_tree.delete(i)
        if not term:
            self._load_products(); return
        for r in self.db.search_products(term):
            self.prod_tree.insert('', 'end', values=(r['id'], r['sku'], r['name'], r['unit'], r['cost_price'], r['sale_price'], r['stock']))

    def _open_product_form(self):
        ProductForm(self, self.db)

    def _edit_product(self, event):
        sel = self.prod_tree.selection();
        if not sel: return
        pid = self.prod_tree.item(sel[0])['values'][0]
        ProductForm(self, self.db, pid)

    # Purchases UI
    def _purchases_ui(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='New Purchase', command=self._open_purchase_form).pack(side='right')
        ttk.Label(top, text='(Purchases increase stock)').pack(side='left')

    def _open_purchase_form(self):
        PurchaseForm(self, self.db)

    # Sales UI
    def _sales_ui(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='New Sale', command=self._open_sale_form).pack(side='right')
        ttk.Label(top, text='(Sales decrease stock)').pack(side='left')

    def _open_sale_form(self):
        SaleForm(self, self.db)

    # Payments UI
    def _payments_ui(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', padx=8, pady=8)
        ttk.Button(top, text='Record Payment', command=self._open_payment_form).pack(side='right')
        ttk.Label(top, text='Payments for customers/suppliers').pack(side='left')

    def _open_payment_form(self):
        PaymentForm(self, self.db)

    # Reports UI
    def _reports_ui(self, parent):
        ttk.Button(parent, text='Export Customers CSV', command=lambda: self._export_table('customers')).pack(pady=6)
        ttk.Button(parent, text='Export Products CSV', command=lambda: self._export_table('products')).pack(pady=6)
        ttk.Button(parent, text='Export Sales CSV', command=lambda: self._export_table('sales')).pack(pady=6)
        ttk.Button(parent, text='Backup DB', command=self._backup_db).pack(pady=6)

    def _export_table(self, table):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path: return
        try:
            self.db.export_table(table, path)
            messagebox.showinfo('Exported', f'{table} exported to {path}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _backup_db(self):
        path = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('DB','*.db')], initialfile=f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        if not path: return
        self.db.conn.close()
        import shutil
        shutil.copy(self.db.path, path)
        messagebox.showinfo('Backup', f'Backup saved to {path}')
        self.db = DB(self.db.path)

# ---------- Forms ----------
class CustomerForm(tk.Toplevel):
    def __init__(self, parent, db, cid=None):
        super().__init__(parent)
        self.db = db
        self.cid = cid
        self.title('Customer')
        self.geometry('450x320')
        self._build()
        if cid: self._load()

    def _build(self):
        f = ttk.Frame(self); f.pack(fill='both', expand=True, padx=12, pady=12)
        labels = ['Name','Contact','Email','Address']
        self.vars = {}
        r=0
        for lab in labels:
            ttk.Label(f, text=lab).grid(row=r, column=0, sticky='w', pady=6)
            v = tk.StringVar()
            ttk.Entry(f, textvariable=v, width=40).grid(row=r, column=1)
            self.vars[lab]=v
            r+=1
        btns = ttk.Frame(f); btns.grid(row=r, column=0, columnspan=2, pady=12)
        ttk.Button(btns, text='Save', command=self._save).pack(side='left', padx=6)
        ttk.Button(btns, text='Cancel', command=self.destroy).pack(side='left', padx=6)

    def _load(self):
        c = self.db.conn.cursor(); c.execute('SELECT * FROM customers WHERE id=?', (self.cid,)); row = c.fetchone()
        if not row: messagebox.showerror('Error','Not found'); self.destroy(); return
        self.vars['Name'].set(row['name']); self.vars['Contact'].set(row['contact']); self.vars['Email'].set(row['email']); self.vars['Address'].set(row['address'])

    def _save(self):
        data = {k:v.get().strip() for k,v in self.vars.items()}
        if not data['Name']: messagebox.showerror('Error','Name required'); return
        if self.cid:
            self.db.update_customer(self.cid, name=data['Name'], contact=data['Contact'], email=data['Email'], address=data['Address'])
            messagebox.showinfo('Saved','Customer updated')
        else:
            self.db.add_customer(data['Name'], data['Contact'], data['Address'], data['Email'])
            messagebox.showinfo('Saved','Customer added')
        self.master._load_customers()
        self.destroy()

class ProductForm(tk.Toplevel):
    def __init__(self, parent, db, pid=None):
        super().__init__(parent)
        self.db = db
        self.pid = pid
        self.title('Product')
        self.geometry('520x380')
        self._build()
        if pid: self._load()

    def _build(self):
        f = ttk.Frame(self); f.pack(fill='both', expand=True, padx=12, pady=12)
        labels = ['SKU','Name','Description','Unit','Cost Price','Sale Price','Stock']
        self.vars = {}
        r=0
        for lab in labels:
            ttk.Label(f, text=lab).grid(row=r, column=0, sticky='w', pady=6)
            v = tk.StringVar()
            ttk.Entry(f, textvariable=v, width=40).grid(row=r, column=1)
            self.vars[lab]=v
            r+=1
        btns = ttk.Frame(f); btns.grid(row=r, column=0, columnspan=2, pady=12)
        ttk.Button(btns, text='Save', command=self._save).pack(side='left', padx=6)
        ttk.Button(btns, text='Cancel', command=self.destroy).pack(side='left', padx=6)

    def _load(self):
        row = self.db.get_product(self.pid)
        if not row: messagebox.showerror('Error','Not found'); self.destroy(); return
        self.vars['SKU'].set(row['sku']); self.vars['Name'].set(row['name']); self.vars['Description'].set(row['description']); self.vars['Unit'].set(row['unit'])
        self.vars['Cost Price'].set(str(row['cost_price'])); self.vars['Sale Price'].set(str(row['sale_price'])); self.vars['Stock'].set(str(row['stock']))

    def _save(self):
        data = {k:v.get().strip() for k,v in self.vars.items()}
        if not data['SKU'] or not data['Name']: messagebox.showerror('Error','SKU and Name required'); return
        try:
            cp = float(data['Cost Price']) if data['Cost Price'] else 0.0
            sp = float(data['Sale Price']) if data['Sale Price'] else 0.0
            stock = float(data['Stock']) if data['Stock'] else 0.0
        except ValueError:
            messagebox.showerror('Error','Numeric fields invalid'); return
        if self.pid:
            self.db.update_product(self.pid, sku=data['SKU'], name=data['Name'], description=data['Description'], unit=data['Unit'], cost_price=cp, sale_price=sp, stock=stock)
            messagebox.showinfo('Saved','Product updated')
        else:
            self.db.add_product(data['SKU'], data['Name'], data['Description'], data['Unit'], cp, sp, stock)
            messagebox.showinfo('Saved','Product added')
        self.master._load_products()
        self.destroy()

class PurchaseForm(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title('New Purchase')
        self.geometry('820x520')
        self.items = []
        self._build()

    def _build(self):
        f = ttk.Frame(self); f.pack(fill='both', expand=True, padx=10, pady=10)
        # Supplier selection
        ttk.Label(f, text='Supplier').grid(row=0, column=0, sticky='w')
        self.supplier_q = tk.StringVar()
        ttk.Entry(f, textvariable=self.supplier_q, width=40).grid(row=0, column=1)
        ttk.Button(f, text='Find', command=self._find_supplier).grid(row=0, column=2, padx=6)
        self.supplier_lbl = ttk.Label(f, text='No supplier selected')
        self.supplier_lbl.grid(row=0, column=3, sticky='w')

        ttk.Label(f, text='Invoice No').grid(row=1, column=0, sticky='w')
        self.invoice_var = tk.StringVar(value=f'P{datetime.now().strftime("%Y%m%d%H%M%S")}')
        ttk.Entry(f, textvariable=self.invoice_var).grid(row=1, column=1, sticky='w')

        # Item entry
        ttk.Separator(f, orient='horizontal').grid(row=2, column=0, columnspan=4, sticky='ew', pady=8)
        ttk.Label(f, text='Product').grid(row=3, column=0, sticky='w')
        self.prod_q = tk.StringVar()
        ttk.Entry(f, textvariable=self.prod_q).grid(row=3, column=1, sticky='w')
        ttk.Button(f, text='Find', command=self._find_product).grid(row=3, column=2, padx=6)
        ttk.Label(f, text='Qty').grid(row=4, column=0, sticky='w')
        self.qty_var = tk.StringVar(value='1')
        ttk.Entry(f, textvariable=self.qty_var, width=10).grid(row=4, column=1, sticky='w')
        ttk.Label(f, text='Rate').grid(row=4, column=2, sticky='w')
        self.rate_var = tk.StringVar(value='0')
        ttk.Entry(f, textvariable=self.rate_var, width=12).grid(row=4, column=3, sticky='w')
        ttk.Button(f, text='Add Item', command=self._add_item).grid(row=5, column=0, pady=8)

        # Items tree
        cols = ('product','qty','rate','amount')
        self.items_tree = ttk.Treeview(f, columns=cols, show='headings', height=10)
        for c in cols: self.items_tree.heading(c, text=c.title())
        self.items_tree.grid(row=6, column=0, columnspan=4, pady=8)

        ttk.Button(f, text='Save Purchase', command=self._save).grid(row=7, column=3, sticky='e', pady=8)

    def _find_supplier(self):
        term = self.supplier_q.get().strip()
        if not term: messagebox.showinfo('Info','Enter supplier name or contact'); return
        rows = self.db.conn.execute('SELECT * FROM suppliers WHERE name LIKE ? OR contact LIKE ?', (f'%{term}%', f'%{term}%')).fetchall()
        if not rows:
            if messagebox.askyesno('Not found', 'Supplier not found. Add new?'):
                sid = self.db.add_supplier(term, '', '', '')
                self.supplier = self.db.conn.execute('SELECT * FROM suppliers WHERE id=?', (sid,)).fetchone()
                self.supplier_lbl.config(text=f"{self.supplier['name']}")
            return
        self.supplier = rows[0]
        self.supplier_lbl.config(text=f"{self.supplier['name']}")

    def _find_product(self):
        term = self.prod_q.get().strip()
        if not term: messagebox.showinfo('Info','Enter SKU or name'); return
        rows = self.db.conn.execute('SELECT * FROM products WHERE sku LIKE ? OR name LIKE ?', (f'%{term}%', f'%{term}%')).fetchall()
        if not rows: messagebox.showinfo('Info','Product not found'); return
        self.selected_product = rows[0]
        messagebox.showinfo('Found', f"Selected: {self.selected_product['name']} (Stock: {self.selected_product['stock']})")

    def _add_item(self):
        if not hasattr(self, 'selected_product'):
            messagebox.showerror('Error','Select a product first'); return
        try:
            qty = float(self.qty_var.get())
            rate = float(self.rate_var.get())
        except ValueError:
            messagebox.showerror('Error','Invalid numeric'); return
        amt = qty * rate
        it = {'product_id': self.selected_product['id'], 'product': self.selected_product['name'], 'qty': qty, 'rate': rate, 'amount': amt}
        self.items.append(it)
        self.items_tree.insert('', 'end', values=(it['product'], it['qty'], it['rate'], it['amount']))

    def _save(self):
        if not hasattr(self, 'supplier'):
            messagebox.showerror('Error','Select supplier'); return
        if not self.items:
            messagebox.showerror('Error','Add items'); return
        try:
            self.db.add_purchase(self.supplier['id'], self.invoice_var.get(), datetime.now().date().isoformat(), self.items)
            messagebox.showinfo('Saved','Purchase recorded')
            self.destroy()
        except Exception as e:
            messagebox.showerror('Error', str(e))

class SaleForm(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title('New Sale')
        self.geometry('820x520')
        self.items = []
        self._build()

    def _build(self):
        f = ttk.Frame(self); f.pack(fill='both', expand=True, padx=10, pady=10)
        ttk.Label(f, text='Customer').grid(row=0, column=0, sticky='w')
        self.cust_q = tk.StringVar()
        ttk.Entry(f, textvariable=self.cust_q, width=40).grid(row=0, column=1)
        ttk.Button(f, text='Find', command=self._find_customer).grid(row=0, column=2, padx=6)
        self.cust_lbl = ttk.Label(f, text='No customer selected')
        self.cust_lbl.grid(row=0, column=3, sticky='w')

        ttk.Label(f, text='Invoice No').grid(row=1, column=0, sticky='w')
        self.invoice_var = tk.StringVar(value=f'S{datetime.now().strftime("%Y%m%d%H%M%S")}')
        ttk.Entry(f, textvariable=self.invoice_var).grid(row=1, column=1, sticky='w')

        ttk.Separator(f, orient='horizontal').grid(row=2, column=0, columnspan=4, sticky='ew', pady=8)
        ttk.Label(f, text='Product').grid(row=3, column=0, sticky='w')
        self.prod_q = tk.StringVar()
        ttk.Entry(f, textvariable=self.prod_q).grid(row=3, column=1, sticky='w')
        ttk.Button(f, text='Find', command=self._find_product).grid(row=3, column=2, padx=6)
        ttk.Label(f, text='Qty').grid(row=4, column=0, sticky='w')
        self.qty_var = tk.StringVar(value='1')
        ttk.Entry(f, textvariable=self.qty_var, width=10).grid(row=4, column=1, sticky='w')
        ttk.Label(f, text='Rate').grid(row=4, column=2, sticky='w')
        self.rate_var = tk.StringVar(value='0')
        ttk.Entry(f, textvariable=self.rate_var, width=12).grid(row=4, column=3, sticky='w')
        ttk.Button(f, text='Add Item', command=self._add_item).grid(row=5, column=0, pady=8)

        cols = ('product','qty','rate','amount')
        self.items_tree = ttk.Treeview(f, columns=cols, show='headings', height=10)
        for c in cols: self.items_tree.heading(c, text=c.title())
        self.items_tree.grid(row=6, column=0, columnspan=4, pady=8)
        ttk.Button(f, text='Save Sale', command=self._save).grid(row=7, column=3, sticky='e', pady=8)

    def _find_customer(self):
        term = self.cust_q.get().strip()
        if not term: messagebox.showinfo('Info','Enter customer name or contact'); return
        rows = self.db.conn.execute('SELECT * FROM customers WHERE name LIKE ? OR contact LIKE ?', (f'%{term}%', f'%{term}%')).fetchall()
        if not rows: messagebox.showinfo('Info','Customer not found'); return
        self.customer = rows[0]
        self.cust_lbl.config(text=self.customer['name'])

    def _find_product(self):
        term = self.prod_q.get().strip()
        if not term: messagebox.showinfo('Info','Enter SKU or name'); return
        rows = self.db.conn.execute('SELECT * FROM products WHERE sku LIKE ? OR name LIKE ?', (f'%{term}%', f'%{term}%')).fetchall()
        if not rows: messagebox.showinfo('Info','Product not found'); return
        self.selected_product = rows[0]
        messagebox.showinfo('Found', f"Selected: {self.selected_product['name']} (Stock: {self.selected_product['stock']})")

    def _add_item(self):
        if not hasattr(self, 'selected_product'):
            messagebox.showerror('Error','Select a product first'); return
        try:
            qty = float(self.qty_var.get())
            rate = float(self.rate_var.get())
        except ValueError:
            messagebox.showerror('Error','Invalid numeric'); return
        if qty > self.selected_product['stock']:
            messagebox.showerror('Error','Insufficient stock'); return
        amt = qty * rate
        it = {'product_id': self.selected_product['id'], 'product': self.selected_product['name'], 'qty': qty, 'rate': rate, 'amount': amt}
        self.items.append(it)
        self.items_tree.insert('', 'end', values=(it['product'], it['qty'], it['rate'], it['amount']))

    def _save(self):
        if not hasattr(self, 'customer'):
            messagebox.showerror('Error','Select customer'); return
        if not self.items: messagebox.showerror('Error','Add items'); return
        try:
            self.db.add_sale(self.customer['id'], self.invoice_var.get(), datetime.now().date().isoformat(), self.items)
            messagebox.showinfo('Saved','Sale recorded')
            self.destroy()
        except Exception as e:
            messagebox.showerror('Error', str(e))

class PaymentForm(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title('Record Payment')
        self.geometry('420x320')
        self._build()

    def _build(self):
        f = ttk.Frame(self); f.pack(fill='both', expand=True, padx=12, pady=12)
        ttk.Label(f, text='Party Type').grid(row=0, column=0, sticky='w')
        self.party_type = tk.StringVar(value='customer')
        ttk.Combobox(f, textvariable=self.party_type, values=['customer','supplier']).grid(row=0, column=1)
        ttk.Label(f, text='Party ID (select via search)').grid(row=1, column=0, sticky='w')
        self.party_q = tk.StringVar()
        ttk.Entry(f, textvariable=self.party_q).grid(row=1, column=1)
        ttk.Button(f, text='Find', command=self._find_party).grid(row=1, column=2)
        self.party_lbl = ttk.Label(f, text='No party selected')
        self.party_lbl.grid(row=2, column=0, columnspan=3, sticky='w')

        ttk.Label(f, text='Amount').grid(row=3, column=0, sticky='w')
        self.amount_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.amount_var).grid(row=3, column=1)
        ttk.Label(f, text='Method').grid(row=4, column=0, sticky='w')
        self.method_var = tk.StringVar(value='Cash')
        ttk.Entry(f, textvariable=self.method_var).grid(row=4, column=1)
        ttk.Label(f, text='Date (YYYY-MM-DD)').grid(row=5, column=0, sticky='w')
        self.date_var = tk.StringVar(value=datetime.now().date().isoformat())
        ttk.Entry(f, textvariable=self.date_var).grid(row=5, column=1)
        ttk.Button(f, text='Save Payment', command=self._save).grid(row=6, column=1, pady=12)

    def _find_party(self):
        term = self.party_q.get().strip()
        ptype = self.party_type.get()
        if not term: messagebox.showinfo('Info','Enter search term'); return
        if ptype=='customer': rows = self.db.conn.execute('SELECT * FROM customers WHERE name LIKE ? OR contact LIKE ?', (f'%{term}%', f'%{term}%')).fetchall()
        else: rows = self.db.conn.execute('SELECT * FROM suppliers WHERE name LIKE ? OR contact LIKE ?', (f'%{term}%', f'%{term}%')).fetchall()
        if not rows: messagebox.showinfo('Info','Not found'); return
        self.party = rows[0]
        self.party_lbl.config(text=self.party['name'])

    def _save(self):
        if not hasattr(self, 'party'): messagebox.showerror('Error','Select party'); return
        try:
            amt = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror('Error','Invalid amount'); return
        self.db.add_payment(self.party_type.get(), self.party['id'], amt, self.method_var.get(), self.date_var.get())
        messagebox.showinfo('Saved','Payment recorded')
        self.destroy()

# ---------- Run ----------
def main():
    db = DB()
    app = App(db)
    app.mainloop()

if __name__ == '__main__':
    main()
