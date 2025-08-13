"""
INDIRA'S POS - Modern Flat UI (Upgraded)
Features in this version:
 - Modern flat-style ttk UI
 - Admin & staff login
 - Staff management
 - Inventory management
 - Purchase entry
 - Sales entry with Customer selection/creation
 - Customer records table
 - Barcode generator (Code128 -> PNG)
 - Financials & pie chart (matplotlib)
 - Settings (daily target, printer config, shop info stored in shop_info.json)
 - Logo loaded from file `logo.png` in program folder and shown on dashboard
 - Printable 58mm thermal receipts with centered logo (ESC/POS) via python-escpos
 - Print Receipt button (manual) — creates PDF backup and sends to printer
 - Exports to Excel (pandas/openpyxl)

Dependencies (install):
 pip install pillow python-barcode matplotlib pandas openpyxl python-escpos reportlab

Notes:
 - If python-escpos is not available / printer not connected, the system will still generate a PDF backup and warn the user.
 - Logo file: place `logo.png` in the program folder; Settings allow changing it.
 - To create .exe: use PyInstaller:
     pyinstaller --onefile INDIRA_POS_system.py

"""

import os
import sys
import json
import sqlite3
import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import barcode
from barcode.writer import ImageWriter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas

# Try to import escpos for thermal printing
try:
    from escpos.printer import Usb, Serial, Network, Dummy
    ESC_POS_AVAILABLE = True
except Exception:
    ESC_POS_AVAILABLE = False

DB_FILE = 'indira_pos.db'
BARCODE_DIR = 'barcodes'
REPORTS_DIR = 'reports'
CHARTS_DIR = 'charts'
LOGO_FILE = 'logo.png'  # file-based logo
SHOP_INFO_FILE = 'shop_info.json'

for d in (BARCODE_DIR, REPORTS_DIR, CHARTS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------- DB Setup ----------------------------
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS customers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS inventory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    name TEXT,
    qty INTEGER,
    cost_price REAL,
    sell_price REAL,
    last_updated TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS purchases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT,
    qty INTEGER,
    cost_price REAL,
    total_cost REAL,
    date TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT,
    qty INTEGER,
    sell_price REAL,
    total_sale REAL,
    date TEXT,
    staff TEXT,
    customer_id INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS settings(
    key TEXT PRIMARY KEY,
    value TEXT
)
''')
conn.commit()

# default admin
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", ('admin','11JJsca@052','admin'))
    conn.commit()

# default shop_info
if not os.path.exists(SHOP_INFO_FILE):
    shop_info = {
        'shop_name': "INDIRA",
        'address': '28/1, Mahendrabanarjee Road,Behala, kol-60',
        'phone': '+91-8584030641',
        'gst': ''
    }
    with open(SHOP_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(shop_info, f, ensure_ascii=False, indent=2)
else:
    with open(SHOP_INFO_FILE, 'r', encoding='utf-8') as f:
        try:
            shop_info = json.load(f)
        except Exception:
            shop_info = {
                'shop_name': "INDIRA",
                'address': '28/1, Mahendrabanarjee Road,Behala, kol-60',
                'phone': '+91-8584030641',
                'gst': ''
            }

# helper for settings storage
def set_setting(key, value):
    c.execute('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)', (key,str(value)))
    conn.commit()

def get_setting(key, default=None):
    c.execute('SELECT value FROM settings WHERE key=?', (key,))
    r = c.fetchone()
    return r[0] if r else default

# ---------------------------- Utilities ----------------------------

def generate_barcode(sku):
    filename = os.path.join(BARCODE_DIR, f"{sku}.png")
    code128 = barcode.get('code128', sku, writer=ImageWriter())
    code128.save(filename[:-4])
    return filename


def calculate_financials():
    c.execute('SELECT SUM(cost_price * qty) FROM inventory')
    investment = c.fetchone()[0] or 0.0
    c.execute('SELECT SUM(sell_price * qty) FROM inventory')
    sale_val = c.fetchone()[0] or 0.0
    c.execute('SELECT SUM(total_sale) FROM sales')
    total_sales = c.fetchone()[0] or 0.0
    c.execute('SELECT SUM(total_cost) FROM purchases')
    total_purchases = c.fetchone()[0] or 0.0
    profit = total_sales - total_purchases
    return investment, sale_val, total_sales, total_purchases, profit


def save_pie_chart():
    investment, sale_val, total_sales, total_purchases, profit = calculate_financials()
    labels = ['Investment','Stock Sale Value','Profit']
    values = [investment, sale_val, max(profit,0)]
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    fname = os.path.join(CHARTS_DIR, f'finance_pie_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    fig.savefig(fname, transparent=True)
    plt.close(fig)
    return fname

# PDF receipt backup
def save_pdf_receipt(sale_id, receipt_lines, logo_path=None):
    fname = os.path.join(REPORTS_DIR, f'receipt_{sale_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    cpdf = pdfcanvas.Canvas(fname, pagesize=(200,400))  # small page, arbitrary
    y = 380
    if logo_path and os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            w, h = img.size
            maxw = 180
            ratio = maxw / float(w)
            img = img.resize((int(w*ratio), int(h*ratio)), Image.ANTIALIAS)
            img.save('tmp_logo_print.png')
            cpdf.drawImage('tmp_logo_print.png', (200 - img.size[0]) / 2, y - img.size[1])
            y -= img.size[1] + 8
            os.remove('tmp_logo_print.png')
        except Exception:
            pass
    for line in receipt_lines:
        cpdf.setFont('Helvetica', 8)
        cpdf.drawCentredString(100, y, line)
        y -= 12
    cpdf.save()
    return fname

# Thermal printing helper
class ThermalPrinter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.printer = None
        self.connected = False
        self._connect()

    def _connect(self):
        if not ESC_POS_AVAILABLE:
            self.printer = Dummy()
            self.connected = False
            return
        try:
            typ = self.cfg.get('type','usb')
            if typ == 'usb':
                vid = int(self.cfg.get('usb_vendor',0))
                pid = int(self.cfg.get('usb_product',0))
                self.printer = Usb(vid, pid, timeout=0.5)
            elif typ == 'network':
                ip = self.cfg.get('ip','')
                port = int(self.cfg.get('port',9100))
                self.printer = Network(ip, port=port)
            elif typ == 'serial':
                dev = self.cfg.get('device','')
                baud = int(self.cfg.get('baudrate',9600))
                self.printer = Serial(dev, baudrate=baud)
            else:
                self.printer = Dummy()
            self.connected = True
        except Exception as e:
            print('Printer connect error:', e)
            self.printer = Dummy()
            self.connected = False

    def print_receipt(self, receipt_lines, logo_path=None):
        if not ESC_POS_AVAILABLE or not self.connected:
            raise RuntimeError('Printer not connected or escpos not available')
        p = self.printer
        try:
            # center
            p.set(align='center')
            if logo_path and os.path.exists(logo_path):
                p.image(logo_path)
                p.text(
)
            # shop name & details are expected in receipt_lines first items
            for ln in receipt_lines:
                p.text('ln +')
            p.cut( )
        except Exception as e:
            raise

# ---------------------------- GUI ----------------------------
class IndiraPOS(Tk):
    def __init__(self):
        super().__init__()
        self.title("INDIRA'S POS - Modern")
        self.geometry('1100x700')
        self.minsize(1000,650)
        self.style = ttk.Style(self)
        # apply a modern theme if available
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.style.configure('TFrame', background='#f6f6f6')
        self.style.configure('Card.TFrame', background='white', relief='flat')
        self.style.configure('TLabel', background='#f6f6f6')
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        self.current_user = None
        self.printer = None
        self.load_printer_cfg()
        self.create_login_frame()

    def load_printer_cfg(self):
        cfg = get_setting('printer_cfg')
        if cfg:
            try:
                self.printer_cfg = json.loads(cfg)
            except Exception:
                self.printer_cfg = {}
        else:
            self.printer_cfg = {}
        # init printer object
        try:
            self.printer = ThermalPrinter(self.printer_cfg)
        except Exception:
            self.printer = None

    def save_printer_cfg(self):
        set_setting('printer_cfg', json.dumps(self.printer_cfg))
        try:
            self.printer = ThermalPrinter(self.printer_cfg)
        except Exception:
            self.printer = None

    def create_login_frame(self):
        for w in self.winfo_children(): w.destroy()
        frame = ttk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        ttk.Label(frame, text="INDIRA'S POS", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=8)
        ttk.Label(frame, text='Username').grid(row=1, column=0, sticky=E)
        ttk.Label(frame, text='Password').grid(row=2, column=0, sticky=E)
        self.username_var = StringVar()
        self.password_var = StringVar()
        ttk.Entry(frame, textvariable=self.username_var).grid(row=1, column=1)
        ttk.Entry(frame, show='*', textvariable=self.password_var).grid(row=2, column=1)
        ttk.Button(frame, text='Login', command=self.handle_login).grid(row=3, column=0, columnspan=2, pady=8)

    def handle_login(self):
        u = self.username_var.get().strip()
        pss = self.password_var.get().strip()
        c.execute('SELECT username,role FROM users WHERE username=? AND password=?', (u,pss))
        row = c.fetchone()
        if row:
            self.current_user = row[0]
            role = row[1]
            messagebox.showinfo('Login', f'Welcome {self.current_user} ({role})')
            self.create_main_frame(role)
        else:
            messagebox.showerror('Login failed', 'Invalid credentials')

    def create_main_frame(self, role):
        for w in self.winfo_children(): w.destroy()
        main = ttk.Frame(self)
        main.pack(fill=BOTH, expand=True)
        sidebar = ttk.Frame(main, width=260, style='Card.TFrame')
        sidebar.pack(side=LEFT, fill=Y)
        content = ttk.Frame(main)
        content.pack(side=LEFT, fill=BOTH, expand=True)
        # sidebar buttons
        ttk.Label(sidebar, text=f'User: {self.current_user}').pack(pady=8)
        btns = [
            ('Dashboard', self.show_dashboard),
            ('New Sale', self.show_sales_entry),
            ('Add Stock Purchase', self.show_purchase_entry),
            ('Inventory', self.show_inventory),
            ('Customers', self.show_customers),
            ('Barcode Generator', self.show_barcode_gen),
            ('Export Reports', self.export_reports),
            ('Settings', self.show_settings)
        ]
        for t, cmd in btns:
            b = ttk.Button(sidebar, text=t, command=cmd)
            b.pack(fill=X, padx=10, pady=4)
        if role == 'admin':
            ttk.Button(sidebar, text='Staff Management', command=self.show_staff_mgmt).pack(fill=X, padx=10, pady=4)
        ttk.Button(sidebar, text='Logout', command=self.logout).pack(side=BOTTOM, fill=X, padx=10, pady=10)
        self.content = content
        self.show_dashboard()

    def logout(self):
        self.current_user = None
        self.create_login_frame()

    # ---------------- Dashboard ----------------
    def show_dashboard(self):
        for w in self.content.winfo_children(): w.destroy()
        frame = ttk.Frame(self.content)
        frame.pack(fill=BOTH, expand=True, padx=12, pady=12)
        # header with logo
        top = ttk.Frame(frame)
        top.pack(fill=X)
        logo_img = None
        if os.path.exists(LOGO_FILE):
            try:
                img = Image.open(LOGO_FILE).convert('RGBA')
                img.thumbnail((100,100), Image.ANTIALIAS)
                logo_img = ImageTk.PhotoImage(img)
                lbl = Label(top, image=logo_img, bg='#f6f6f6')
                lbl.image = logo_img
                lbl.pack(side=LEFT, padx=6)
            except Exception:
                pass
        shopname = shop_info.get('shop_name','INDIRA\'S POS')
        ttk.Label(top, text=shopname, style='Header.TLabel').pack(side=LEFT, padx=6)

        # stats cards
        stats = ttk.Frame(frame)
        stats.pack(fill=X, pady=8)
        inv, sale_val, total_sales, total_purchases, profit = calculate_financials()
        cards = [
            ("Investment", f"₹ {inv:.2f}"),
            ("Stock Sale Value", f"₹ {sale_val:.2f}"),
            ("Profit/Loss", f"₹ {profit:.2f}")
        ]
        for t, v in cards:
            card = ttk.Frame(stats, style='Card.TFrame')
            card.pack(side=LEFT, padx=6, ipadx=10, ipady=10)
            ttk.Label(card, text=t).pack()
            ttk.Label(card, text=v, font=('Segoe UI', 12, 'bold')).pack()

        # pie chart
        chart_file = save_pie_chart()
        try:
            img = Image.open(chart_file).resize((260,260))
            self._chart_img = ImageTk.PhotoImage(img)
            Label(frame, image=self._chart_img, bg='#f6f6f6').pack(side=RIGHT, padx=10)
        except Exception:
            pass

    # ---------------- Sales Entry ----------------
    def show_sales_entry(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text='New Sale', style='Header.TLabel').pack(pady=6)
        f = ttk.Frame(self.content)
        f.pack(padx=10, pady=6, anchor=W)
        ttk.Label(f, text='SKU').grid(row=0, column=0, sticky=E)
        ttk.Label(f, text='Quantity').grid(row=1, column=0, sticky=E)
        ttk.Label(f, text='Sell Price').grid(row=2, column=0, sticky=E)
        ttk.Label(f, text='Customer').grid(row=3, column=0, sticky=E)
        self.sale_sku = StringVar()
        self.sale_qty = IntVar(value=1)
        self.sale_price = DoubleVar(value=0.0)
        self.sale_customer = StringVar()
        ttk.Entry(f, textvariable=self.sale_sku).grid(row=0, column=1)
        ttk.Entry(f, textvariable=self.sale_qty).grid(row=1, column=1)
        ttk.Entry(f, textvariable=self.sale_price).grid(row=2, column=1)
        # customer combobox
        customers = self.load_customers_list()
        self.customer_cb = ttk.Combobox(f, textvariable=self.sale_customer, values=customers)
        self.customer_cb.grid(row=3, column=1)
        ttk.Button(f, text='Add Customer', command=self.quick_add_customer).grid(row=3, column=2, padx=6)
        ttk.Button(f, text='Record Sale', command=self.record_sale).grid(row=4, column=0, pady=8)
        self.print_btn = ttk.Button(f, text='Print Receipt', command=self.print_last_sale, state=DISABLED)
        self.print_btn.grid(row=4, column=1)
        # recent sales
        cols = ('id','sku','qty','price','total','date','staff','customer')
        self.sales_tree = ttk.Treeview(self.content, columns=cols, show='headings')
        for col in cols:
            self.sales_tree.heading(col, text=col.title())
        self.sales_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.refresh_sales()

    def load_customers_list(self):
        c.execute('SELECT name FROM customers')
        return [r[0] for r in c.fetchall()]

    def quick_add_customer(self):
        def save():
            name = name_var.get().strip()
            phone = phone_var.get().strip()
            if not name:
                messagebox.showerror('Error','Name required')
                return
            c.execute('INSERT INTO customers(name,phone) VALUES(?,?)', (name,phone))
            conn.commit()
            top.destroy()
            self.customer_cb['values'] = self.load_customers_list()
        top = Toplevel(self)
        top.title('Add Customer')
        name_var = StringVar()
        phone_var = StringVar()
        ttk.Label(top, text='Name').grid(row=0, column=0)
        ttk.Entry(top, textvariable=name_var).grid(row=0, column=1)
        ttk.Label(top, text='Phone').grid(row=1, column=0)
        ttk.Entry(top, textvariable=phone_var).grid(row=1, column=1)
        ttk.Button(top, text='Save', command=save).grid(row=2, column=0, columnspan=2, pady=6)

    def record_sale(self):
        sku = self.sale_sku.get().strip()
        try:
            qty = int(self.sale_qty.get())
        except Exception:
            messagebox.showerror('Error','Invalid quantity')
            return
        try:
            price = float(self.sale_price.get())
        except Exception:
            messagebox.showerror('Error','Invalid price')
            return
        customer_name = self.sale_customer.get().strip()
        customer_id = None
        if customer_name:
            c.execute('SELECT id FROM customers WHERE name=?', (customer_name,))
            r = c.fetchone()
            if r:
                customer_id = r[0]
        if not sku or qty<=0:
            messagebox.showerror('Error','Invalid SKU/qty')
            return
        # check inventory
        c.execute('SELECT qty FROM inventory WHERE sku=?', (sku,))
        row = c.fetchone()
        if not row or row[0] < qty:
            messagebox.showerror('Error','Insufficient stock or SKU not found')
            return
        total = qty * price
        date = datetime.date.today().isoformat()
        c.execute('INSERT INTO sales(sku,qty,sell_price,total_sale,date,staff,customer_id) VALUES(?,?,?,?,?,?,?)', (sku,qty,price,total,date,self.current_user,customer_id))
        # update qty
        newqty = row[0] - qty
        c.execute('UPDATE inventory SET qty=?, last_updated=? WHERE sku=?', (newqty, date, sku))
        conn.commit()
        messagebox.showinfo('Sale', f'Sale recorded. Total ₹ {total:.2f}')
        self.refresh_sales()
        # enable print button and remember last sale id
        c.execute('SELECT last_insert_rowid()')
        self.last_sale_id = c.fetchone()[0]
        self.print_btn['state'] = NORMAL

    def refresh_sales(self):
        for i in self.sales_tree.get_children():
            self.sales_tree.delete(i)
        c.execute('SELECT s.id,s.sku,s.qty,s.sell_price,s.total_sale,s.date,s.staff,coalesce(cus.name,"") FROM sales s LEFT JOIN customers cus ON s.customer_id=cus.id ORDER BY s.date DESC LIMIT 200')
        for r in c.fetchall():
            self.sales_tree.insert('', END, values=r)

    def print_last_sale(self):
        try:
            sid = self.last_sale_id
        except Exception:
            messagebox.showerror('Error','No sale to print')
            return
        # build receipt lines
        c.execute('SELECT sku,qty,sell_price,total_sale,date,staff,customer_id FROM sales WHERE id=?', (sid,))
        row = c.fetchone()
        if not row:
            messagebox.showerror('Error','Sale not found')
            return
        sku, qty, price, total, date, staff, cust_id = row
        customer_name = ''
        customer_phone = ''
        if cust_id:
            c.execute('SELECT name,phone FROM customers WHERE id=?', (cust_id,))
            cr = c.fetchone()
            if cr:
                customer_name, customer_phone = cr
        # build header from shop_info
        header = [shop_info.get('shop_name','INDIRA\'S POS'), shop_info.get('address',''), shop_info.get('phone','')]
        receipt_lines = []
        # add header centered
        for h in header:
            if h:
                receipt_lines.append(h)
        receipt_lines.append('--------------------------------')
        dt = datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')
        receipt_lines.append(f'Date: {dt}')
        receipt_lines.append(f'Invoice No: {sid:06d}')
        if customer_name:
            receipt_lines.append(f'Customer: {customer_name}')
        if customer_phone:
            receipt_lines.append(f'Phone: {customer_phone}')
        receipt_lines.append('--------------------------------')
        receipt_lines.append('{:<12}{:>3}{:>7}{:>8}'.format('Item','Qty','Price','Total'))
        # get product name
        c.execute('SELECT name FROM inventory WHERE sku=?', (sku,))
        prod = c.fetchone()
        prod_name = prod[0] if prod else sku
        receipt_lines.append('{:<12}{:>3}{:>7.2f}{:>8.2f}'.format(prod_name[:12], qty, price, total))
        receipt_lines.append('--------------------------------')
        receipt_lines.append(f'TOTAL: {total:.2f}')
        receipt_lines.append('Paid: CASH')
        receipt_lines.append('--------------------------------')
        receipt_lines.append('Thank you for shopping!')

        # save pdf backup
        pdf_path = save_pdf_receipt(sid, receipt_lines, logo_path=LOGO_FILE if os.path.exists(LOGO_FILE) else None)
        messagebox.showinfo('Receipt Saved', f'Receipt saved to {pdf_path}')

        # attempt thermal print via configured printer when user clicks print
        def do_print():
            if not ESC_POS_AVAILABLE:
                messagebox.showwarning('Printer','python-escpos not installed or unavailable. Only PDF saved.')
                return
            if not self.printer or not self.printer.connected:
                messagebox.showwarning('Printer','Printer not connected. Check settings.')
                return
            try:
                # build printable lines with center alignment for header
                printable = []
                printable.extend(header)
                printable.append('')
                printable.append(f'Date: {dt}')
                printable.append(f'Invoice No: {sid:06d}')
                if customer_name:
                    printable.append(f'Customer: {customer_name}')
                printable.append('')
                printable.append('{:<12}{:>3}{:>7}{:>8}'.format('Item','Qty','Price','Total'))
                printable.append('{:<12}{:>3}{:>7.2f}{:>8.2f}'.format(prod_name[:12], qty, price, total))
                printable.append('')
                printable.append(f'TOTAL: {total:.2f}')
                printable.append('Paid: CASH')
                printable.append('')
                printable.append('Thank you for shopping!')
                self.printer.print_receipt(printable, logo_path=LOGO_FILE if os.path.exists(LOGO_FILE) else None)
                messagebox.showinfo('Printed','Receipt sent to thermal printer')
            except Exception as e:
                messagebox.showerror('Print Error', str(e))
        # ask user whether to print
        if messagebox.askyesno('Print','Do you want to print this receipt to thermal printer now?'):
            do_print()

    # ---------------- Purchases ----------------
    def show_purchase_entry(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text='Add Stock Purchase', style='Header.TLabel').pack(pady=6)
        f = ttk.Frame(self.content)
        f.pack(padx=10, pady=6, anchor=W)
        ttk.Label(f, text='SKU').grid(row=0, column=0, sticky=E)
        ttk.Label(f, text='Name').grid(row=1, column=0, sticky=E)
        ttk.Label(f, text='Quantity').grid(row=2, column=0, sticky=E)
        ttk.Label(f, text='Cost Price').grid(row=3, column=0, sticky=E)
        ttk.Label(f, text='Sell Price').grid(row=4, column=0, sticky=E)
        self.p_sku = StringVar()
        self.p_name = StringVar()
        self.p_qty = IntVar(value=1)
        self.p_cost = DoubleVar(value=0.0)
        self.p_sell = DoubleVar(value=0.0)
        ttk.Entry(f, textvariable=self.p_sku).grid(row=0, column=1)
        ttk.Entry(f, textvariable=self.p_name).grid(row=1, column=1)
        ttk.Entry(f, textvariable=self.p_qty).grid(row=2, column=1)
        ttk.Entry(f, textvariable=self.p_cost).grid(row=3, column=1)
        ttk.Entry(f, textvariable=self.p_sell).grid(row=4, column=1)
        ttk.Button(f, text='Record Purchase', command=self.record_purchase).grid(row=5, column=0, columnspan=2, pady=8)
        # recent purchases
        cols = ('sku','qty','cost','total','date')
        self.pur_tree = ttk.Treeview(self.content, columns=cols, show='headings')
        for col in cols:
            self.pur_tree.heading(col, text=col.title())
        self.pur_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.refresh_purchases()

    def record_purchase(self):
        sku = self.p_sku.get().strip()
        name = self.p_name.get().strip()
        try:
            qty = int(self.p_qty.get())
            cost = float(self.p_cost.get())
            sell = float(self.p_sell.get())
        except Exception:
            messagebox.showerror('Error','Invalid numbers')
            return
        if not sku or qty<=0:
            messagebox.showerror('Error','Invalid SKU or qty')
            return
        total_cost = qty * cost
        date = datetime.date.today().isoformat()
        c.execute('INSERT INTO purchases(sku,qty,cost_price,total_cost,date) VALUES(?,?,?,?,?)', (sku,qty,cost,total_cost,date))
        c.execute('SELECT qty FROM inventory WHERE sku=?', (sku,))
        row = c.fetchone()
        if row:
            newqty = row[0] + qty
            c.execute('UPDATE inventory SET qty=?, cost_price=?, sell_price=?, last_updated=?, name=? WHERE sku=?', (newqty, cost, sell, date, name, sku))
        else:
            c.execute('INSERT INTO inventory(sku,name,qty,cost_price,sell_price,last_updated) VALUES(?,?,?,?,?,?)', (sku,name,qty,cost,sell,date))
        conn.commit()
        messagebox.showinfo('Purchase', f'Purchase recorded. Total cost ₹ {total_cost:.2f}')
        self.refresh_purchases()

    def refresh_purchases(self):
        for i in self.pur_tree.get_children():
            self.pur_tree.delete(i)
        c.execute('SELECT sku,qty,cost_price,total_cost,date FROM purchases ORDER BY date DESC LIMIT 200')
        for r in c.fetchall():
            self.pur_tree.insert('', END, values=r)

    # ---------------- Inventory ----------------
    def show_inventory(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text='Inventory', style='Header.TLabel').pack(pady=6)
        cols = ('sku','name','qty','cost_price','sell_price','last_updated')
        self.inv_tree = ttk.Treeview(self.content, columns=cols, show='headings')
        for col in cols:
            self.inv_tree.heading(col, text=col.title())
        self.inv_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.refresh_inventory()
        btnf = ttk.Frame(self.content)
        btnf.pack(pady=6)
        ttk.Button(btnf, text='Generate Barcode for Selected', command=self.barcode_selected).pack(side=LEFT, padx=4)
        ttk.Button(btnf, text='Export Inventory to Excel', command=self.export_inventory_excel).pack(side=LEFT, padx=4)

    def refresh_inventory(self):
        for i in self.inv_tree.get_children():
            self.inv_tree.delete(i)
        c.execute('SELECT sku,name,qty,cost_price,sell_price,last_updated FROM inventory')
        for r in c.fetchall():
            self.inv_tree.insert('', END, values=r)

    def barcode_selected(self):
        try:
            sel = self.inv_tree.selection()[0]
        except Exception:
            messagebox.showerror('Error','Select an item first')
            return
        sku = self.inv_tree.item(sel)['values'][0]
        fname = generate_barcode(sku)
        messagebox.showinfo('Barcode', f'Barcode saved to {fname}')

    def export_inventory_excel(self):
        c.execute('SELECT sku,name,qty,cost_price,sell_price,last_updated FROM inventory')
        rows = c.fetchall()
        df = pd.DataFrame(rows, columns=['SKU','Name','Qty','Cost Price','Sell Price','Last Updated'])
        fname = os.path.join(REPORTS_DIR, f'inventory_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        df.to_excel(fname, index=False)
        messagebox.showinfo('Export', f'Inventory exported to {fname}')

    # ---------------- Customers ----------------
    def show_customers(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text='Customers', style='Header.TLabel').pack(pady=6)
        f = ttk.Frame(self.content)
        f.pack(padx=10, pady=6, anchor=W)
        ttk.Label(f, text='Name').grid(row=0, column=0)
        ttk.Label(f, text='Phone').grid(row=1, column=0)
        ttk.Label(f, text='Email').grid(row=2, column=0)
        ttk.Label(f, text='Address').grid(row=3, column=0)
        self.c_name = StringVar()
        self.c_phone = StringVar()
        self.c_email = StringVar()
        self.c_address = StringVar()
        ttk.Entry(f, textvariable=self.c_name).grid(row=0, column=1)
        ttk.Entry(f, textvariable=self.c_phone).grid(row=1, column=1)
        ttk.Entry(f, textvariable=self.c_email).grid(row=2, column=1)
        ttk.Entry(f, textvariable=self.c_address).grid(row=3, column=1)
        ttk.Button(f, text='Add Customer', command=self.add_customer).grid(row=4, column=0, columnspan=2, pady=6)
        cols = ('id','name','phone','email','address')
        self.cust_tree = ttk.Treeview(self.content, columns=cols, show='headings')
        for col in cols:
            self.cust_tree.heading(col, text=col.title())
        self.cust_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.refresh_customers()

    def add_customer(self):
        name = self.c_name.get().strip()
        phone = self.c_phone.get().strip()
        email = self.c_email.get().strip()
        addr = self.c_address.get().strip()
        if not name:
            messagebox.showerror('Error','Name required')
            return
        c.execute('INSERT INTO customers(name,phone,email,address) VALUES(?,?,?,?)', (name,phone,email,addr))
        conn.commit()
        messagebox.showinfo('Customer','Customer added')
        self.refresh_customers()

    def refresh_customers(self):
        for i in self.cust_tree.get_children():
            self.cust_tree.delete(i)
        c.execute('SELECT id,name,phone,email,address FROM customers ORDER BY id DESC LIMIT 500')
        for r in c.fetchall():
            self.cust_tree.insert('', END, values=r)

    # ---------------- Barcode Generator ----------------
    def show_barcode_gen(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text='Barcode Generator', style='Header.TLabel').pack(pady=6)
        f = ttk.Frame(self.content)
        f.pack(padx=10, pady=10)
        ttk.Label(f, text='SKU/Text').grid(row=0, column=0)
        self.bc_text = StringVar()
        ttk.Entry(f, textvariable=self.bc_text).grid(row=0, column=1)
        ttk.Button(f, text='Generate', command=self.do_generate_barcode).grid(row=1, column=0, columnspan=2, pady=6)

    def do_generate_barcode(self):
        text = self.bc_text.get().strip()
        if not text:
            messagebox.showerror('Error','Enter text for barcode')
            return
        fname = generate_barcode(text)
        messagebox.showinfo('Barcode', f'Barcode saved to {fname}')

    # ---------------- Staff Management ----------------
    def show_staff_mgmt(self):
        top = Toplevel(self)
        top.title('Staff Management')
        cols = ('username','role')
        tree = ttk.Treeview(top, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col.title())
        tree.pack(fill=BOTH, expand=True)
        c.execute('SELECT username,role FROM users')
        for r in c.fetchall():
            tree.insert('', END, values=r)
        ttk.Label(top, text='Username').pack()
        uvar = StringVar(); pvar = StringVar(); rvar = StringVar(value='staff')
        ttk.Entry(top, textvariable=uvar).pack()
        ttk.Entry(top, textvariable=pvar).pack()
        ttk.Combobox(top, textvariable=rvar, values=['admin','staff']).pack()
        def add():
            try:
                c.execute('INSERT INTO users(username,password,role) VALUES(?,?,?)', (uvar.get(),pvar.get(),rvar.get()))
                conn.commit()
                messagebox.showinfo('Staff','Added')
            except sqlite3.IntegrityError:
                messagebox.showerror('Error','Username exists')
        ttk.Button(top, text='Add', command=add).pack(pady=6)

    # ---------------- Reports & Exports ----------------
    def export_reports(self):
        top = Toplevel(self)
        top.title('Export Reports')
        ttk.Button(top, text='Export Sales to Excel', command=self.export_sales_excel).pack(padx=8, pady=6)
        ttk.Button(top, text='Export Purchases to Excel', command=self.export_purchases_excel).pack(padx=8, pady=6)
        ttk.Button(top, text='Export Inventory to Excel', command=self.export_inventory_excel).pack(padx=8, pady=6)
        ttk.Button(top, text='Export Financials (Excel)', command=self.export_financials_excel).pack(padx=8, pady=6)

    def export_sales_excel(self):
        c.execute('SELECT sku,qty,sell_price,total_sale,date,staff,customer_id FROM sales')
        rows = c.fetchall()
        df = pd.DataFrame(rows, columns=['SKU','Qty','Sell Price','Total Sale','Date','Staff','Customer ID'])
        fname = os.path.join(REPORTS_DIR, f'sales_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        df.to_excel(fname, index=False)
        messagebox.showinfo('Export', f'Sales exported to {fname}')

    def export_purchases_excel(self):
        c.execute('SELECT sku,qty,cost_price,total_cost,date FROM purchases')
        rows = c.fetchall()
        df = pd.DataFrame(rows, columns=['SKU','Qty','Cost Price','Total Cost','Date'])
        fname = os.path.join(REPORTS_DIR, f'purchases_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        df.to_excel(fname, index=False)
        messagebox.showinfo('Export', f'Purchases exported to {fname}')

    def export_financials_excel(self):
        inv, sale_val, total_sales, total_purchases, profit = calculate_financials()
        df = pd.DataFrame([{ 'investment':inv, 'stock_sale_value':sale_val, 'total_sales':total_sales, 'total_purchases':total_purchases, 'profit':profit }])
        fname = os.path.join(REPORTS_DIR, f'financials_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        df.to_excel(fname, index=False)
        messagebox.showinfo('Export', f'Financial summary exported to {fname}')

    # ---------------- Settings ----------------
    def show_settings(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text='Settings', style='Header.TLabel').pack(pady=6)
        f = ttk.Frame(self.content)
        f.pack(padx=10, pady=6, anchor=W)
        # shop info
        ttk.Label(f, text='Shop Name').grid(row=0, column=0)
        ttk.Label(f, text='Address').grid(row=1, column=0)
        ttk.Label(f, text='Phone').grid(row=2, column=0)
        ttk.Label(f, text='GST').grid(row=3, column=0)
        s_name = StringVar(value=shop_info.get('shop_name',''))
        s_addr = StringVar(value=shop_info.get('address',''))
        s_phone = StringVar(value=shop_info.get('phone',''))
        s_gst = StringVar(value=shop_info.get('gst',''))
        ttk.Entry(f, textvariable=s_name, width=60).grid(row=0, column=1)
        ttk.Entry(f, textvariable=s_addr, width=60).grid(row=1, column=1)
        ttk.Entry(f, textvariable=s_phone, width=60).grid(row=2, column=1)
        ttk.Entry(f, textvariable=s_gst, width=60).grid(row=3, column=1)
        def save_shop():
            shop_info['shop_name'] = s_name.get(); shop_info['address'] = s_addr.get(); shop_info['phone'] = s_phone.get(); shop_info['gst'] = s_gst.get()
            with open(SHOP_INFO_FILE, 'w', encoding='utf-8') as f2:
                json.dump(shop_info, f2, ensure_ascii=False, indent=2)
            messagebox.showinfo('Saved','Shop info saved')
        ttk.Button(f, text='Save Shop Info', command=save_shop).grid(row=4, column=0, columnspan=2, pady=6)
        # logo change
        def change_logo():
            p = filedialog.askopenfilename(filetypes=[('PNG/JPG','*.png;*.jpg;*.jpeg')])
            if p:
                try:
                    img = Image.open(p)
                    img = img.convert('RGBA')
                    img.save(LOGO_FILE)
                    messagebox.showinfo('Logo','Logo saved to program folder')
                except Exception as e:
                    messagebox.showerror('Error', str(e))
        ttk.Button(f, text='Change Logo', command=change_logo).grid(row=5, column=0, pady=6)
        # printer settings
        ttk.Label(f, text='Printer Type (usb/network/serial)').grid(row=6, column=0)
        ptype = StringVar(value=self.printer_cfg.get('type','usb'))
        ttk.Entry(f, textvariable=ptype).grid(row=6, column=1)
        ttk.Label(f, text='USB Vendor ID').grid(row=7, column=0)
        pv = StringVar(value=str(self.printer_cfg.get('usb_vendor','0')))
        ttk.Entry(f, textvariable=pv).grid(row=7, column=1)
        ttk.Label(f, text='USB Product ID').grid(row=8, column=0)
        pp = StringVar(value=str(self.printer_cfg.get('usb_product','0')))
        ttk.Entry(f, textvariable=pp).grid(row=8, column=1)
        ttk.Label(f, text='Network IP').grid(row=9, column=0)
        nip = StringVar(value=self.printer_cfg.get('ip',''))
        ttk.Entry(f, textvariable=nip).grid(row=9, column=1)
        ttk.Label(f, text='Network Port').grid(row=10, column=0)
        nport = StringVar(value=str(self.printer_cfg.get('port','9100')))
        ttk.Entry(f, textvariable=nport).grid(row=10, column=1)
        def save_printer():
            self.printer_cfg['type'] = ptype.get()
            self.printer_cfg['usb_vendor'] = pv.get()
            self.printer_cfg['usb_product'] = pp.get()
            self.printer_cfg['ip'] = nip.get()
            self.printer_cfg['port'] = nport.get()
            self.save_printer_cfg()
            messagebox.showinfo('Printer','Printer settings saved')
        ttk.Button(f, text='Save Printer Settings', command=save_printer).grid(row=11, column=0, columnspan=2, pady=6)

    # ---------------- Run ----------------

if __name__ == '__main__':
    app = IndiraPOS()
    app.mainloop()
