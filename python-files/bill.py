"""
Simple Billing Management App using Tkinter + SQLite3
Features:
- Customer management (add, update, delete, list)
- Product management (add, update, delete, list)
- Billing: create invoice with multiple products, GST calculations (18% total; SGST 9% + CGST 9%), save invoices

Run:
- Requires Python 3 (no external libraries)
- Save as billing_app.py and run: python billing_app.py
- Database file created: billing.db

This is a concise but functional example. You can extend/beautify as needed.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB = "billing.db"

# ---------- Database helpers ----------

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            addr1 TEXT,
            addr2 TEXT,
            city TEXT,
            district TEXT,
            pin TEXT,
            gst_no TEXT,
            gst_code TEXT,
            state TEXT,
            country TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            qty REAL DEFAULT 0,
            rate REAL DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT UNIQUE,
            invoice_date TEXT,
            customer_id INTEGER,
            total REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            qty REAL,
            rate REAL,
            basic REAL,
            gst REAL,
            sgst REAL,
            cgst REAL,
            total REAL,
            FOREIGN KEY(bill_id) REFERENCES bills(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()


# ---------- App ----------
class BillingApp:
    def __init__(self, root):
        self.root = root
        root.title("Billing Management App")
        root.geometry("1000x650")

        self.conn = sqlite3.connect(DB)
        self.cursor = self.conn.cursor()

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.customer_frame = ttk.Frame(self.notebook)
        self.product_frame = ttk.Frame(self.notebook)
        self.billing_frame = ttk.Frame(self.notebook)

        
        self.notebook.add(self.customer_frame, text='Customers')
        self.notebook.add(self.product_frame, text='Products')
        self.notebook.add(self.billing_frame, text='Billing')

        self.setup_customers()
        self.setup_products()
        self.setup_billing()

        self.load_customers()
        self.load_products()
        self.load_bills()

    # ---------- Customers ----------
    def setup_customers(self):
        frm = self.customer_frame
        left = ttk.Frame(frm, padding=10)
        left.pack(side='left', fill='y')
        right = ttk.Frame(frm, padding=10)
        right.pack(side='right', fill='both', expand=True)

        labels = ['Name','Address-1','Address-2','City','District','PIN','GST No','GST Code','State','Country']
        self.cust_vars = {}
        for i,lab in enumerate(labels):
            ttk.Label(left, text=lab).grid(row=i, column=0, sticky='w')
            var = tk.StringVar()
            ent = ttk.Entry(left, textvariable=var, width=30)
            ent.grid(row=i, column=1, pady=3, sticky='w')
            self.cust_vars[lab] = var

        btns = ttk.Frame(left)
        btns.grid(row=len(labels), column=0, columnspan=2, pady=10)
        ttk.Button(btns, text='Save', command=self.save_customer).grid(row=0,column=0,padx=5)
        ttk.Button(btns, text='Update', command=self.update_customer).grid(row=0,column=1,padx=5)
        ttk.Button(btns, text='Clear', command=self.clear_customer_form).grid(row=0,column=2,padx=5)
        ttk.Button(btns, text='Delete', command=self.delete_customer).grid(row=0,column=3,padx=5)

        # Treeview
        cols = ('id','name','city','district','pin','gst_no','state','country')
        self.cust_tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.cust_tree.heading(c, text=c.title())
            self.cust_tree.column(c, width=100)
        self.cust_tree.pack(fill='both', expand=True)
        self.cust_tree.bind('<<TreeviewSelect>>', self.on_customer_select)

    def save_customer(self):
        vals = [self.cust_vars[k].get().strip() for k in self.cust_vars]
        if not vals[0]:
            messagebox.showwarning('Validation','Customer name required')
            return
        self.cursor.execute('''INSERT INTO customers (name,addr1,addr2,city,district,pin,gst_no,gst_code,state,country)
                               VALUES (?,?,?,?,?,?,?,?,?,?)''', vals)
        self.conn.commit()
        self.load_customers()
        self.clear_customer_form()
        self.refresh_customer_combobox()

    def load_customers(self):
        for r in self.cust_tree.get_children():
            self.cust_tree.delete(r)
        self.cursor.execute('SELECT id,name,city,district,pin,gst_no,state,country FROM customers')
        for row in self.cursor.fetchall():
            self.cust_tree.insert('', 'end', values=row)

    def on_customer_select(self, event):
        sel = self.cust_tree.selection()
        if not sel: return
        vals = self.cust_tree.item(sel[0])['values']
        cid = vals[0]
        self.cursor.execute('SELECT * FROM customers WHERE id=?', (cid,))
        row = self.cursor.fetchone()
        if row:
            keys = list(self.cust_vars.keys())
            # row: (id,name,addr1,...country)
            for i, key in enumerate(keys, start=1):
                self.cust_vars[key].set(row[i] if row[i] is not None else '')

    def update_customer(self):
        sel = self.cust_tree.selection()
        if not sel:
            messagebox.showinfo('Info','Select a customer to update')
            return
        cid = self.cust_tree.item(sel[0])['values'][0]
        vals = [self.cust_vars[k].get().strip() for k in self.cust_vars]
        vals.append(cid)
        self.cursor.execute('''UPDATE customers SET name=?,addr1=?,addr2=?,city=?,district=?,pin=?,gst_no=?,gst_code=?,state=?,country=? WHERE id=?''', vals)
        self.conn.commit()
        self.load_customers()
        self.refresh_customer_combobox()

    def delete_customer(self):
        sel = self.cust_tree.selection()
        if not sel:
            messagebox.showinfo('Info','Select a customer to delete')
            return
        cid = self.cust_tree.item(sel[0])['values'][0]
        if messagebox.askyesno('Confirm','Delete selected customer?'):
            self.cursor.execute('DELETE FROM customers WHERE id=?', (cid,))
            self.conn.commit()
            self.load_customers()
            self.clear_customer_form()
            self.refresh_customer_combobox()

    def clear_customer_form(self):
        for v in self.cust_vars.values():
            v.set('')

    # ---------- Products ----------
    def setup_products(self):
        frm = self.product_frame
        left = ttk.Frame(frm, padding=10)
        left.pack(side='left', fill='y')
        right = ttk.Frame(frm, padding=10)
        right.pack(side='right', fill='both', expand=True)

        labels = ['Name','Qty','Rate']
        self.prod_vars = {}
        for i,lab in enumerate(labels):
            ttk.Label(left, text=lab).grid(row=i, column=0, sticky='w')
            var = tk.StringVar()
            ent = ttk.Entry(left, textvariable=var, width=25)
            ent.grid(row=i, column=1, pady=3, sticky='w')
            self.prod_vars[lab] = var

        # Calculated fields shown as labels
        self.prod_basic_var = tk.StringVar(value='0')
        self.prod_gst_var = tk.StringVar(value='0')
        self.prod_sgst_var = tk.StringVar(value='0')
        self.prod_cgst_var = tk.StringVar(value='0')
        ttk.Label(left, text='Basic Total').grid(row=3,column=0,sticky='w')
        ttk.Label(left, textvariable=self.prod_basic_var).grid(row=3,column=1,sticky='w')
        ttk.Label(left, text='GST 18%').grid(row=4,column=0,sticky='w')
        ttk.Label(left, textvariable=self.prod_gst_var).grid(row=4,column=1,sticky='w')
        ttk.Label(left, text='SGST 9%').grid(row=5,column=0,sticky='w')
        ttk.Label(left, textvariable=self.prod_sgst_var).grid(row=5,column=1,sticky='w')
        ttk.Label(left, text='CGST 9%').grid(row=6,column=0,sticky='w')
        ttk.Label(left, textvariable=self.prod_cgst_var).grid(row=6,column=1,sticky='w')

        btns = ttk.Frame(left)
        btns.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text='Calculate', command=self.calculate_product).grid(row=0,column=0,padx=5)
        ttk.Button(btns, text='Save', command=self.save_product).grid(row=0,column=1,padx=5)
        ttk.Button(btns, text='Update', command=self.update_product).grid(row=0,column=2,padx=5)
        ttk.Button(btns, text='Clear', command=self.clear_product_form).grid(row=0,column=3,padx=5)
        ttk.Button(btns, text='Delete', command=self.delete_product).grid(row=0,column=4,padx=5)

        cols = ('id','name','qty','rate')
        self.prod_tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.prod_tree.heading(c, text=c.title())
            self.prod_tree.column(c, width=120)
        self.prod_tree.pack(fill='both', expand=True)
        self.prod_tree.bind('<<TreeviewSelect>>', self.on_product_select)

    def calculate_product(self):
        try:
            qty = float(self.prod_vars['Qty'].get() or 0)
            rate = float(self.prod_vars['Rate'].get() or 0)
        except ValueError:
            messagebox.showwarning('Validation','Qty and Rate must be numbers')
            return
        basic = qty * rate
        gst = basic * 0.18
        sgst = gst/2
        cgst = gst/2
        self.prod_basic_var.set(f"{basic:.2f}")
        self.prod_gst_var.set(f"{gst:.2f}")
        self.prod_sgst_var.set(f"{sgst:.2f}")
        self.prod_cgst_var.set(f"{cgst:.2f}")

    def save_product(self):
        name = self.prod_vars['Name'].get().strip()
        if not name:
            messagebox.showwarning('Validation','Product name required')
            return
        try:
            qty = float(self.prod_vars['Qty'].get() or 0)
            rate = float(self.prod_vars['Rate'].get() or 0)
        except ValueError:
            messagebox.showwarning('Validation','Qty and Rate must be numbers')
            return
        self.cursor.execute('INSERT INTO products (name,qty,rate) VALUES (?,?,?)', (name,qty,rate))
        self.conn.commit()
        self.load_products()
        self.clear_product_form()
        self.refresh_product_combobox()

    def load_products(self):
        for r in self.prod_tree.get_children():
            self.prod_tree.delete(r)
        self.cursor.execute('SELECT id,name,qty,rate FROM products')
        for row in self.cursor.fetchall():
            self.prod_tree.insert('', 'end', values=row)

    def on_product_select(self, event):
        sel = self.prod_tree.selection()
        if not sel: return
        vals = self.prod_tree.item(sel[0])['values']
        pid = vals[0]
        self.cursor.execute('SELECT * FROM products WHERE id=?', (pid,))
        row = self.cursor.fetchone()
        if row:
            self.prod_vars['Name'].set(row[1])
            self.prod_vars['Qty'].set(str(row[2]))
            self.prod_vars['Rate'].set(str(row[3]))
            self.calculate_product()

    def update_product(self):
        sel = self.prod_tree.selection()
        if not sel:
            messagebox.showinfo('Info','Select a product to update')
            return
        pid = self.prod_tree.item(sel[0])['values'][0]
        try:
            qty = float(self.prod_vars['Qty'].get() or 0)
            rate = float(self.prod_vars['Rate'].get() or 0)
        except ValueError:
            messagebox.showwarning('Validation','Qty and Rate must be numbers')
            return
        name = self.prod_vars['Name'].get().strip()
        self.cursor.execute('UPDATE products SET name=?,qty=?,rate=? WHERE id=?', (name,qty,rate,pid))
        self.conn.commit()
        self.load_products()
        self.refresh_product_combobox()

    def delete_product(self):
        sel = self.prod_tree.selection()
        if not sel:
            messagebox.showinfo('Info','Select a product to delete')
            return
        pid = self.prod_tree.item(sel[0])['values'][0]
        if messagebox.askyesno('Confirm','Delete selected product?'):
            self.cursor.execute('DELETE FROM products WHERE id=?', (pid,))
            self.conn.commit()
            self.load_products()
            self.clear_product_form()
            self.refresh_product_combobox()

    def clear_product_form(self):
        for v in self.prod_vars.values():
            v.set('')
        self.prod_basic_var.set('0')
        self.prod_gst_var.set('0')
        self.prod_sgst_var.set('0')
        self.prod_cgst_var.set('0')

    # ---------- Billing ----------
    def setup_billing(self):
        frm = self.billing_frame
        top = ttk.Frame(frm, padding=10)
        top.pack(side='top', fill='x')
        mid = ttk.Frame(frm, padding=10)
        mid.pack(side='top', fill='x')
        bottom = ttk.Frame(frm, padding=10)
        bottom.pack(side='top', fill='both', expand=True)

        ttk.Label(top, text='Invoice No').grid(row=0,column=0,sticky='w')
        self.invoice_var = tk.StringVar(value=self.generate_invoice_no())
        ttk.Entry(top, textvariable=self.invoice_var, width=20).grid(row=0,column=1,sticky='w')
        ttk.Label(top, text='Invoice Date').grid(row=0,column=2,sticky='w')
        self.invoice_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(top, textvariable=self.invoice_date_var, width=20).grid(row=0,column=3,sticky='w')

        ttk.Label(mid, text='Customer').grid(row=0,column=0,sticky='w')
        self.cust_cb_var = tk.StringVar()
        self.customer_cb = ttk.Combobox(mid, textvariable=self.cust_cb_var, state='readonly')
        self.customer_cb.grid(row=0,column=1,sticky='w')

        # Product selection
        ttk.Label(mid, text='Product').grid(row=1,column=0,sticky='w')
        self.prod_cb_var = tk.StringVar()
        self.product_cb = ttk.Combobox(mid, textvariable=self.prod_cb_var, state='readonly')
        self.product_cb.grid(row=1,column=1,sticky='w')
        ttk.Label(mid, text='Qty').grid(row=1,column=2,sticky='w')
        self.bill_qty_var = tk.StringVar(value='1')
        ttk.Entry(mid, textvariable=self.bill_qty_var, width=10).grid(row=1,column=3,sticky='w')
        ttk.Button(mid, text='Add more Item', command=self.add_bill_item).grid(row=1,column=4, padx=5)

        # Bill items tree
        cols = ('product_id','product_name','qty','rate','basic','gst','sgst','cgst','total')
        self.bill_items_tree = ttk.Treeview(bottom, columns=cols, show='headings', selectmode='browse')
        headings = ['Product ID','Product','Qty','Rate','Basic','GST','SGST','CGST','Total']
        for c,h in zip(cols,headings):
            self.bill_items_tree.heading(c, text=h)
            self.bill_items_tree.column(c, width=100)
        self.bill_items_tree.pack(fill='both', expand=True)

        totals_frame = ttk.Frame(frm, padding=10)
        totals_frame.pack(side='top', fill='x')
        self.total_basic_var = tk.StringVar(value='0.00')
        self.total_gst_var = tk.StringVar(value='0.00')
        self.total_amount_var = tk.StringVar(value='0.00')
        ttk.Label(totals_frame, text='Basic Total:').grid(row=0,column=0,sticky='e')
        ttk.Label(totals_frame, textvariable=self.total_basic_var).grid(row=0,column=1,sticky='w')
        ttk.Label(totals_frame, text='GST Total:').grid(row=0,column=2,sticky='e')
        ttk.Label(totals_frame, textvariable=self.total_gst_var).grid(row=0,column=3,sticky='w')
        ttk.Label(totals_frame, text='Bill Amount:').grid(row=0,column=4,sticky='e')
        ttk.Label(totals_frame, textvariable=self.total_amount_var).grid(row=0,column=5,sticky='w')

        btns = ttk.Frame(frm)
        btns.pack(side='top', pady=6)
        ttk.Button(btns, text='Save Bill', command=self.save_bill).grid(row=0,column=0,padx=5)
        ttk.Button(btns, text='Clear Items', command=self.clear_bill_items).grid(row=0,column=1,padx=5)

        # Saved bills list
        saved_frame = ttk.LabelFrame(frm, text='Saved Bills', padding=10)
        saved_frame.pack(side='bottom', fill='both', expand=True)
        scols = ('id','invoice_no','date','customer','total')
        self.saved_tree = ttk.Treeview(saved_frame, columns=scols, show='headings', selectmode='browse')
        for c in scols:
            self.saved_tree.heading(c, text=c.title())
            self.saved_tree.column(c, width=120)
        self.saved_tree.pack(fill='both', expand=True)
        self.saved_tree.bind('<<TreeviewSelect>>', self.on_bill_select)

        # internal list of items for current bill
        self.current_bill_items = []
        self.refresh_customer_combobox()
        self.refresh_product_combobox()

    def generate_invoice_no(self):
        # Basic invoice no generator: INV-YYYYMMDD-XXXX
        dt = datetime.now().strftime('%Y%m%d')
        self.cursor.execute('SELECT COUNT(*) FROM bills WHERE invoice_date=?', (datetime.now().strftime('%Y-%m-%d'),))
        count = self.cursor.fetchone()[0]
        return f'INV-{dt}-{count+1:04d}'

    def refresh_customer_combobox(self):
        self.cursor.execute('SELECT id,name FROM customers')
        rows = self.cursor.fetchall()
        display = [f"{r[0]} - {r[1]}" for r in rows]
        self.customer_cb['values'] = display

    def refresh_product_combobox(self):
        self.cursor.execute('SELECT id,name,rate FROM products')
        rows = self.cursor.fetchall()
        display = [f"{r[0]} - {r[1]} | {r[2]}" for r in rows]
        self.product_cb['values'] = display

    def add_bill_item(self):
        prod = self.prod_cb_var.get()
        if not prod:
            messagebox.showwarning('Validation','Select a product')
            return
        try:
            qty = float(self.bill_qty_var.get() or 0)
        except ValueError:
            messagebox.showwarning('Validation','Qty must be numeric')
            return
        pid = int(prod.split('-')[0].strip())
        # get product details
        self.cursor.execute('SELECT name,rate FROM products WHERE id=?', (pid,))
        row = self.cursor.fetchone()
        if not row:
            messagebox.showerror('Error','Product not found')
            return
        pname, rate = row
        basic = qty * rate
        gst = basic * 0.18
        sgst = gst/2
        cgst = gst/2
        total = basic + gst
        item = {'product_id':pid, 'product_name':pname, 'qty':qty, 'rate':rate, 'basic':basic, 'gst':gst, 'sgst':sgst, 'cgst':cgst, 'total':total}
        self.current_bill_items.append(item)
        self.refresh_bill_items_tree()

    def refresh_bill_items_tree(self):
        for r in self.bill_items_tree.get_children():
            self.bill_items_tree.delete(r)
        total_basic = total_gst = total_amount = 0.0
        for it in self.current_bill_items:
            vals = (it['product_id'], it['product_name'], f"{it['qty']}", f"{it['rate']:.2f}", f"{it['basic']:.2f}", f"{it['gst']:.2f}", f"{it['sgst']:.2f}", f"{it['cgst']:.2f}", f"{it['total']:.2f}")
            self.bill_items_tree.insert('', 'end', values=vals)
            total_basic += it['basic']
            total_gst += it['gst']
            total_amount += it['total']
        self.total_basic_var.set(f"{total_basic:.2f}")
        self.total_gst_var.set(f"{total_gst:.2f}")
        self.total_amount_var.set(f"{total_amount:.2f}")

    def clear_bill_items(self):
        self.current_bill_items = []
        self.refresh_bill_items_tree()

    def save_bill(self):
        inv = self.invoice_var.get().strip()
        date = self.invoice_date_var.get().strip()
        cust = self.cust_cb_var.get().strip()
        if not inv or not date or not cust:
            messagebox.showwarning('Validation','Invoice no, date and customer required')
            return
        if not self.current_bill_items:
            messagebox.showwarning('Validation','Add at least one item to bill')
            return
        cid = int(cust.split('-')[0].strip())
        total_amount = float(self.total_amount_var.get())
        try:
            self.cursor.execute('INSERT INTO bills (invoice_no,invoice_date,customer_id,total) VALUES (?,?,?,?)', (inv,date,cid,total_amount))
        except sqlite3.IntegrityError:
            messagebox.showerror('Error','Invoice number already exists')
            return
        bill_id = self.cursor.lastrowid
        for it in self.current_bill_items:
            self.cursor.execute('''INSERT INTO bill_items (bill_id,product_id,product_name,qty,rate,basic,gst,sgst,cgst,total)
                                   VALUES (?,?,?,?,?,?,?,?,?,?)''', (
                bill_id, it['product_id'], it['product_name'], it['qty'], it['rate'], it['basic'], it['gst'], it['sgst'], it['cgst'], it['total']
            ))
        self.conn.commit()
        messagebox.showinfo('Saved','Bill saved successfully')
        self.clear_bill_items()
        self.invoice_var.set(self.generate_invoice_no())
        self.load_bills()

    def load_bills(self):
        for r in self.saved_tree.get_children():
            self.saved_tree.delete(r)
        self.cursor.execute('SELECT b.id,b.invoice_no,b.invoice_date,c.name,b.total FROM bills b LEFT JOIN customers c ON b.customer_id=c.id ORDER BY b.id DESC')
        for row in self.cursor.fetchall():
            self.saved_tree.insert('', 'end', values=row)

    def on_bill_select(self, event):
        sel = self.saved_tree.selection()
        if not sel: return
        bid = self.saved_tree.item(sel[0])['values'][0]
        self.cursor.execute('SELECT invoice_no,invoice_date,customer_id,total FROM bills WHERE id=?', (bid,))
        b = self.cursor.fetchone()
        if not b: return
        inv, date, cid, total = b
        self.invoice_var.set(inv)
        self.invoice_date_var.set(date)
        # set customer combobox
        self.cursor.execute('SELECT id,name FROM customers WHERE id=?', (cid,))
        row = self.cursor.fetchone()
        if row:
            self.cust_cb_var.set(f"{row[0]} - {row[1]}")
        # load items
        self.cursor.execute('SELECT product_id,product_name,qty,rate,basic,gst,sgst,cgst,total FROM bill_items WHERE bill_id=?', (bid,))
        rows = self.cursor.fetchall()
        self.current_bill_items = []
        for r in rows:
            it = {'product_id':r[0],'product_name':r[1],'qty':r[2],'rate':r[3],'basic':r[4],'gst':r[5],'sgst':r[6],'cgst':r[7],'total':r[8]}
            self.current_bill_items.append(it)
        self.refresh_bill_items_tree()


if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()



