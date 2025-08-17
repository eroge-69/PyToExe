import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ===================== CONFIG =====================
# You asked to "overwrite existing data".
# Set RESET_DB=True for the first run to wipe and rebuild tables.
# After the first successful run, change this to False to keep your data.
RESET_DB = True
DB_PATH = "inventory.db"

AUTO_REFRESH_MS = 4000  # Current Stock auto-refresh interval (milliseconds)
APP_BG = "#f7f9ff"      # light background
HEADER_BG = "#e6f0ff"   # header bar
HEADER_FG = "#0b5ed7"   # bright blue text
ACCENT_BG = "#fff3cd"   # light amber
ACCENT_FG = "#664d03"   # amber text

# ===================== DB INIT =====================
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db(reset=False):
    conn = get_conn()
    c = conn.cursor()

    if reset:
        c.executescript("""
            DROP TABLE IF EXISTS sales;
            DROP TABLE IF EXISTS purchase;
            DROP TABLE IF EXISTS item_master;
        """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS item_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE,
            product_name TEXT,
            units TEXT,
            category TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            cost REAL,
            vendor_name TEXT,
            vendor_address TEXT,
            purchase_invoice_no TEXT,
            vendor_contact_no TEXT,
            quantity INTEGER,
            date TEXT,
            FOREIGN KEY(item_id) REFERENCES item_master(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            price REAL,
            customer_invoice_no TEXT,
            quantity INTEGER,
            date TEXT,
            FOREIGN KEY(item_id) REFERENCES item_master(id)
        )
    """)
    conn.commit()
    conn.close()

# ===================== HELPERS =====================
def fetch_item_maps():
    """Return two dicts: code->(id,name,units,category) and name->(id,code,units,category)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, product_code, product_name, units, category FROM item_master ORDER BY product_code")
    rows = c.fetchall()
    conn.close()
    code_map = {code: (iid, name, units, cat) for (iid, code, name, units, cat) in rows}
    name_map = {name: (iid, code, units, cat) for (iid, code, name, units, cat) in rows}
    return code_map, name_map

def striped_treeview(tree):
    """Apply alternating row tags for readability."""
    for i, iid in enumerate(tree.get_children()):
        tree.item(iid, tags=("evenrow" if i % 2 == 0 else "oddrow",))


# ===================== APP =====================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management")
        self.root.configure(bg=APP_BG)

        # ttk styling (brighter headings)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview.Heading", background=HEADER_BG, foreground=HEADER_FG, font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=APP_BG)
        style.configure("Bold.TLabel", background=APP_BG, foreground=HEADER_FG, font=("Segoe UI", 11, "bold"))
        style.configure("Accent.TFrame", background=ACCENT_BG)
        style.configure("Accent.TLabel", background=ACCENT_BG, foreground=ACCENT_FG)
        style.map("Treeview", background=[("selected", "#d0ebff")])

        # Header bar
        header = tk.Frame(root, bg=HEADER_BG)
        header.pack(fill="x")
        tk.Label(header, text="Standalone Inventory (Offline)", bg=HEADER_BG, fg=HEADER_FG,
                 font=("Segoe UI", 14, "bold"), padx=12, pady=6).pack(side="left")

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Tabs
        self.tab_items = ttk.Frame(self.nb)
        self.tab_purchase = ttk.Frame(self.nb)
        self.tab_sales = ttk.Frame(self.nb)
        self.tab_stock = ttk.Frame(self.nb)
        self.tab_ledger = ttk.Frame(self.nb)

        self.nb.add(self.tab_items, text="Item Master")
        self.nb.add(self.tab_purchase, text="Purchase (IN)")
        self.nb.add(self.tab_sales, text="Sales (OUT)")
        self.nb.add(self.tab_stock, text="Current Stock")
        self.nb.add(self.tab_ledger, text="Ledger")

        # Build UIs
        self.build_item_master()
        self.build_purchase()
        self.build_sales()
        self.build_stock()
        self.build_ledger()

        # Populate comboboxes initially
        self.refresh_item_caches()

        # Start auto-refresh for stock
        self.schedule_stock_refresh()

    # ---------- Item Master ----------
    def build_item_master(self):
        form = ttk.Frame(self.tab_items)
        form.pack(fill="x", padx=6, pady=6)

        ttk.Label(form, text="Item Master", style="Bold.TLabel").grid(row=0, column=0, columnspan=6, sticky="w", pady=(0,6))

        # 3-per-row aligned inputs
        self.im_code = ttk.Entry(form, width=28)
        self.im_name = ttk.Entry(form, width=28)
        self.im_units = ttk.Entry(form, width=28)
        self.im_cat = ttk.Entry(form, width=28)

        self._place_labeled(form, 1, 0, "Product Code", self.im_code)
        self._place_labeled(form, 1, 2, "Product Name", self.im_name)
        self._place_labeled(form, 1, 4, "Units", self.im_units)
        self._place_labeled(form, 2, 0, "Category", self.im_cat)

        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=6, sticky="w", pady=(6,4))
        ttk.Button(btns, text="Add / Save Item", command=self.add_item).pack(side="left", padx=(0,6))
        ttk.Button(btns, text="Delete Selected", command=self.delete_item).pack(side="left")

        # Table
        table_frame = ttk.Frame(self.tab_items)
        table_frame.pack(fill="both", expand=True, padx=6, pady=(0,6))
        cols = ("code", "name", "units", "category")
        self.items_tv = ttk.Treeview(table_frame, columns=cols, show="headings")
        for c in cols:
            self.items_tv.heading(c, text=c.capitalize())
            self.items_tv.column(c, width=150, anchor="w")
        yb = ttk.Scrollbar(table_frame, orient="vertical", command=self.items_tv.yview)
        self.items_tv.configure(yscrollcommand=yb.set)
        self.items_tv.grid(row=0, column=0, sticky="nsew")
        yb.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.load_items()

    def _place_labeled(self, parent, row, col_group, label, widget):
        """Place a label + widget with 3 groups per row: col_group 0..2 (each group is 2 columns)."""
        base_col = col_group * 2
        ttk.Label(parent, text=label).grid(row=row, column=base_col, sticky="w", padx=(0,6), pady=3)
        widget.grid(row=row, column=base_col+1, sticky="w", padx=(0,16), pady=3)

    def add_item(self):
        code = self.im_code.get().strip()
        name = self.im_name.get().strip()
        units = self.im_units.get().strip()
        cat = self.im_cat.get().strip()
        if not code or not name:
            messagebox.showerror("Error", "Product Code and Product Name are required.")
            return
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO item_master (id, product_code, product_name, units, category) VALUES (COALESCE((SELECT id FROM item_master WHERE product_code=?), NULL),?,?,?,?)",
                      (code, code, name, units, cat))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product Code must be unique.")
        finally:
            conn.close()
        self.load_items()
        self.refresh_item_caches()
        self.im_code.delete(0, tk.END)
        self.im_name.delete(0, tk.END)
        self.im_units.delete(0, tk.END)
        self.im_cat.delete(0, tk.END)

    def delete_item(self):
        sel = self.items_tv.selection()
        if not sel:
            return
        code = self.items_tv.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirm", f"Delete item '{code}'? Purchases/Sales referencing it will remain but code will be missing."):
            return
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM item_master WHERE product_code=?", (code,))
        conn.commit()
        conn.close()
        self.load_items()
        self.refresh_item_caches()

    def load_items(self):
        self.items_tv.delete(*self.items_tv.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT product_code, product_name, units, category FROM item_master ORDER BY product_code")
        for row in c.fetchall():
            self.items_tv.insert("", "end", values=row)
        conn.close()
        striped_treeview(self.items_tv)

    def refresh_item_caches(self):
        self.code_map, self.name_map = fetch_item_maps()
        code_list = list(self.code_map.keys())
        name_list = list(self.name_map.keys())

        # Update comboboxes everywhere
        self.p_code_cb["values"] = code_list
        self.s_code_cb["values"] = code_list
        self.ledger_code_cb["values"] = code_list
        self.ledger_name_cb["values"] = name_list

    # ---------- Purchase (IN) ----------
    def build_purchase(self):
        wrap = ttk.Frame(self.tab_purchase)
        wrap.pack(fill="both", expand=True, padx=6, pady=6)

        ttk.Label(wrap, text="Purchase (IN)", style="Bold.TLabel").pack(anchor="w", pady=(0,6))

        form = ttk.Frame(wrap)
        form.pack(fill="x", pady=(0,6))

        # Inputs (3 per row)
        self.p_code_cb = ttk.Combobox(form, state="readonly", width=26)
        self.p_code_cb.bind("<<ComboboxSelected>>", self._fill_purchase_name)
        self.p_name_var = tk.StringVar()
        p_name_entry = ttk.Entry(form, textvariable=self.p_name_var, state="readonly", width=26)
        self.p_cost = ttk.Entry(form, width=26)
        self.p_vendor = ttk.Entry(form, width=26)
        self.p_vaddr = ttk.Entry(form, width=26)
        self.p_inv = ttk.Entry(form, width=26)
        self.p_vcontact = ttk.Entry(form, width=26)
        self.p_qty = ttk.Entry(form, width=26)

        self._place_labeled(form, 0, 0, "Product Code", self.p_code_cb)
        self._place_labeled(form, 0, 1, "Product Name", p_name_entry)
        self._place_labeled(form, 0, 2, "Cost", self.p_cost)

        self._place_labeled(form, 1, 0, "Vendor Name", self.p_vendor)
        self._place_labeled(form, 1, 1, "Vendor Address", self.p_vaddr)
        self._place_labeled(form, 1, 2, "Purchase Invoice No.", self.p_inv)

        self._place_labeled(form, 2, 0, "Vendor Contact No.", self.p_vcontact)
        self._place_labeled(form, 2, 1, "Total Qty.", self.p_qty)

        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=6, sticky="w", pady=(6, 2))
        ttk.Button(btns, text="Add Purchase", command=self.add_purchase).pack(side="left", padx=(0,6))

        # Table
        table = ttk.Frame(wrap)
        table.pack(fill="both", expand=True)
        cols = ("code","name","cost","vendor","invoice","qty","date")
        self.p_tv = ttk.Treeview(table, columns=cols, show="headings")
        for c in cols:
            self.p_tv.heading(c, text=c.capitalize())
            self.p_tv.column(c, width=120, anchor="w")
        yb = ttk.Scrollbar(table, orient="vertical", command=self.p_tv.yview)
        self.p_tv.configure(yscrollcommand=yb.set)
        self.p_tv.grid(row=0, column=0, sticky="nsew")
        yb.grid(row=0, column=1, sticky="ns")
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)

        self.load_purchases()

    def _fill_purchase_name(self, _evt=None):
        code = self.p_code_cb.get()
        if code in self.code_map:
            self.p_name_var.set(self.code_map[code][1])
        else:
            self.p_name_var.set("")

    def add_purchase(self):
        code = self.p_code_cb.get().strip()
        if code not in self.code_map:
            messagebox.showerror("Error", "Please choose a Product Code from Item Master.")
            return
        try:
            qty = int(self.p_qty.get().strip())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.")
            return
        try:
            cost = float(self.p_cost.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Cost must be a number.")
            return

        item_id = self.code_map[code][0]
        vendor = self.p_vendor.get().strip()
        vaddr = self.p_vaddr.get().strip()
        inv = self.p_inv.get().strip()
        vcontact = self.p_vcontact.get().strip()
        date = datetime.now().strftime("%Y-%m-%d")

        conn = get_conn()
        c = conn.cursor()
        c.execute("""INSERT INTO purchase
            (item_id, cost, vendor_name, vendor_address, purchase_invoice_no, vendor_contact_no, quantity, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, cost, vendor, vaddr, inv, vcontact, qty, date))
        conn.commit()
        conn.close()

        self.load_purchases()
        self.load_stock()  # immediate stock refresh

        # Clear qty only (you can adjust)
        self.p_qty.delete(0, tk.END)

    def load_purchases(self):
        self.p_tv.delete(*self.p_tv.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT im.product_code, im.product_name, p.cost, p.vendor_name,
                            p.purchase_invoice_no, p.quantity, p.date
                     FROM purchase p
                     JOIN item_master im ON im.id = p.item_id
                     ORDER BY p.id DESC""")
        for row in c.fetchall():
            self.p_tv.insert("", "end", values=row)
        conn.close()
        striped_treeview(self.p_tv)

    # ---------- Sales (OUT) ----------
    def build_sales(self):
        wrap = ttk.Frame(self.tab_sales)
        wrap.pack(fill="both", expand=True, padx=6, pady=6)

        ttk.Label(wrap, text="Sales (OUT)", style="Bold.TLabel").pack(anchor="w", pady=(0,6))

        form = ttk.Frame(wrap)
        form.pack(fill="x", pady=(0,6))

        self.s_code_cb = ttk.Combobox(form, state="readonly", width=26)
        self.s_code_cb.bind("<<ComboboxSelected>>", self._fill_sales_name)
        self.s_name_var = tk.StringVar()
        s_name_entry = ttk.Entry(form, textvariable=self.s_name_var, state="readonly", width=26)
        self.s_price = ttk.Entry(form, width=26)
        self.s_invoice = ttk.Entry(form, width=26)
        self.s_qty = ttk.Entry(form, width=26)

        self._place_labeled(form, 0, 0, "Product Code", self.s_code_cb)
        self._place_labeled(form, 0, 1, "Product Name", s_name_entry)
        self._place_labeled(form, 0, 2, "Price", self.s_price)

        self._place_labeled(form, 1, 0, "Customer Invoice No.", self.s_invoice)
        self._place_labeled(form, 1, 1, "Total Qty.", self.s_qty)

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=6, sticky="w", pady=(6, 2))
        ttk.Button(btns, text="Add Sale", command=self.add_sale).pack(side="left", padx=(0,6))

        # Table
        table = ttk.Frame(wrap)
        table.pack(fill="both", expand=True)
        cols = ("code","name","price","invoice","qty","date")
        self.s_tv = ttk.Treeview(table, columns=cols, show="headings")
        for c in cols:
            self.s_tv.heading(c, text=c.capitalize())
            self.s_tv.column(c, width=120, anchor="w")
        yb = ttk.Scrollbar(table, orient="vertical", command=self.s_tv.yview)
        self.s_tv.configure(yscrollcommand=yb.set)
        self.s_tv.grid(row=0, column=0, sticky="nsew")
        yb.grid(row=0, column=1, sticky="ns")
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)

        self.load_sales()

    def _fill_sales_name(self, _evt=None):
        code = self.s_code_cb.get()
        if code in self.code_map:
            self.s_name_var.set(self.code_map[code][1])
        else:
            self.s_name_var.set("")

    def add_sale(self):
        code = self.s_code_cb.get().strip()
        if code not in self.code_map:
            messagebox.showerror("Error", "Please choose a Product Code from Item Master.")
            return
        try:
            qty = int(self.s_qty.get().strip())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.")
            return
        try:
            price = float(self.s_price.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return

        # Check available stock
        item_id = self.code_map[code][0]
        if qty > self._current_stock_for(item_id):
            messagebox.showerror("Error", "Not enough stock for this item.")
            return

        inv = self.s_invoice.get().strip()
        date = datetime.now().strftime("%Y-%m-%d")

        conn = get_conn()
        c = conn.cursor()
        c.execute("""INSERT INTO sales (item_id, price, customer_invoice_no, quantity, date)
                     VALUES (?, ?, ?, ?, ?)""",
                  (item_id, price, inv, qty, date))
        conn.commit()
        conn.close()

        self.load_sales()
        self.load_stock()  # immediate stock refresh

        self.s_qty.delete(0, tk.END)

    def load_sales(self):
        self.s_tv.delete(*self.s_tv.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT im.product_code, im.product_name, s.price, s.customer_invoice_no, s.quantity, s.date
                     FROM sales s
                     JOIN item_master im ON im.id = s.item_id
                     ORDER BY s.id DESC""")
        for row in c.fetchall():
            self.s_tv.insert("", "end", values=row)
        conn.close()
        striped_treeview(self.s_tv)

    def _current_stock_for(self, item_id):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT IFNULL((SELECT SUM(quantity) FROM purchase WHERE item_id=?),0) - IFNULL((SELECT SUM(quantity) FROM sales WHERE item_id=?),0)",
                  (item_id, item_id))
        stock = c.fetchone()[0]
        conn.close()
        return stock

    # ---------- Current Stock (auto-refresh) ----------
    def build_stock(self):
        # Button row
        top = ttk.Frame(self.tab_stock, style="Accent.TFrame")
        top.pack(fill="x", padx=6, pady=(6,0))
        ttk.Label(top, text="Current Stock (auto-refreshing)", style="Accent.TLabel").pack(side="left", padx=8, pady=6)
        ttk.Button(top, text="Refresh Now", command=self.load_stock).pack(side="right", padx=8, pady=6)

        table = ttk.Frame(self.tab_stock)
        table.pack(fill="both", expand=True, padx=6, pady=6)
        cols = ("code","name","units","category","stock")
        self.stock_tv = ttk.Treeview(table, columns=cols, show="headings")
        for c in cols:
            self.stock_tv.heading(c, text=c.capitalize())
            self.stock_tv.column(c, width=140, anchor="w")
        yb = ttk.Scrollbar(table, orient="vertical", command=self.stock_tv.yview)
        self.stock_tv.configure(yscrollcommand=yb.set)
        self.stock_tv.grid(row=0, column=0, sticky="nsew")
        yb.grid(row=0, column=1, sticky="ns")
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)

        self.load_stock()

    def load_stock(self):
        self.stock_tv.delete(*self.stock_tv.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT im.product_code, im.product_name, im.units, im.category,
                   IFNULL((SELECT SUM(quantity) FROM purchase WHERE item_id=im.id),0) -
                   IFNULL((SELECT SUM(quantity) FROM sales WHERE item_id=im.id),0) AS current_stock
            FROM item_master im
            ORDER BY im.product_code
        """)
        for row in c.fetchall():
            self.stock_tv.insert("", "end", values=row)
        conn.close()
        striped_treeview(self.stock_tv)

    def schedule_stock_refresh(self):
        # Auto refresh
        self.load_stock()
        self.root.after(AUTO_REFRESH_MS, self.schedule_stock_refresh)

    # ---------- Ledger ----------
    def build_ledger(self):
        wrap = ttk.Frame(self.tab_ledger)
        wrap.pack(fill="both", expand=True, padx=6, pady=6)

        ttk.Label(wrap, text="Ledger", style="Bold.TLabel").pack(anchor="w", pady=(0,6))

        filters = ttk.Frame(wrap)
        filters.pack(fill="x", pady=(0,6))

        self.ledger_code_cb = ttk.Combobox(filters, state="readonly", width=26)
        self.ledger_name_cb = ttk.Combobox(filters, state="readonly", width=26)

        self._place_labeled(filters, 0, 0, "Search by Product Code", self.ledger_code_cb)
        self._place_labeled(filters, 0, 1, "Search by Product Name", self.ledger_name_cb)

        btns = ttk.Frame(filters)
        btns.grid(row=1, column=0, columnspan=6, sticky="w", pady=(6,2))
        ttk.Button(btns, text="Search", command=self.load_ledger).pack(side="left", padx=(0,6))
        ttk.Button(btns, text="Clear", command=self.clear_ledger_filters).pack(side="left")

        # Table
        table = ttk.Frame(wrap)
        table.pack(fill="both", expand=True)
        cols = ("type","invoice","amount","in_qty","out_qty","balance_qty","date")
        self.ledger_tv = ttk.Treeview(table, columns=cols, show="headings")
        headings = {
            "type": "Type of Transaction",
            "invoice": "Invoice No.",
            "amount": "Amount",
            "in_qty": "IN Qty",
            "out_qty": "OUT Qty",
            "balance_qty": "Balance Qty",
            "date": "Date"
        }
        for c in cols:
            self.ledger_tv.heading(c, text=headings[c])
            self.ledger_tv.column(c, width=130 if c!="invoice" else 160, anchor="w")
        yb = ttk.Scrollbar(table, orient="vertical", command=self.ledger_tv.yview)
        self.ledger_tv.configure(yscrollcommand=yb.set)
        self.ledger_tv.grid(row=0, column=0, sticky="nsew")
        yb.grid(row=0, column=1, sticky="ns")
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)

        # Summary row (labels below)
        self.ledger_summary = tk.StringVar(value="Totals: IN 0 | OUT 0 | Balance 0")
        sum_frame = ttk.Frame(wrap, style="Accent.TFrame")
        sum_frame.pack(fill="x", pady=(6,0))
        ttk.Label(sum_frame, textvariable=self.ledger_summary, style="Accent.TLabel").pack(side="left", padx=8, pady=6)

    def clear_ledger_filters(self):
        self.ledger_code_cb.set("")
        self.ledger_name_cb.set("")
        self.load_ledger()

    def load_ledger(self):
        self.ledger_tv.delete(*self.ledger_tv.get_children())

        # Determine selected item by code OR name (independent)
        selected_item_id = None
        code = self.ledger_code_cb.get().strip()
        name = self.ledger_name_cb.get().strip()

        if code and code in self.code_map:
            selected_item_id = self.code_map[code][0]
        elif name and name in self.name_map:
            selected_item_id = self.name_map[name][0]

        conn = get_conn()
        c = conn.cursor()

        rows = []

        if selected_item_id is None:
            # If nothing selected, show nothing (or show all?)
            # We'll show all transactions combined for all items.
            # Comment next two big queries and implement union for all items:
            c.execute("""
                SELECT 'IN' AS ttype, p.purchase_invoice_no AS inv, p.cost AS amount,
                       p.quantity AS inq, 0 AS outq, p.date AS dt
                FROM purchase p
                ORDER BY p.date, p.id
            """)
            rows += c.fetchall()
            c.execute("""
                SELECT 'OUT' AS ttype, s.customer_invoice_no AS inv, s.price AS amount,
                       0 AS inq, s.quantity AS outq, s.date AS dt
                FROM sales s
                ORDER BY s.date, s.id
            """)
            rows += c.fetchall()
        else:
            # Filter by the chosen item
            c.execute("""
                SELECT 'IN' AS ttype, p.purchase_invoice_no AS inv, p.cost AS amount,
                       p.quantity AS inq, 0 AS outq, p.date AS dt
                FROM purchase p
                WHERE p.item_id=?
                ORDER BY p.date, p.id
            """, (selected_item_id,))
            rows += c.fetchall()

            c.execute("""
                SELECT 'OUT' AS ttype, s.customer_invoice_no AS inv, s.price AS amount,
                       0 AS inq, s.quantity AS outq, s.date AS dt
                FROM sales s
                WHERE s.item_id=?
                ORDER BY s.date, s.id
            """, (selected_item_id,))
            rows += c.fetchall()

        conn.close()

        # Sort combined by date (and type secondarily)
        rows.sort(key=lambda r: (r[5], r[0]))

        # Running balance + totals
        total_in = 0
        total_out = 0
        balance = 0

        for r in rows:
            ttype, inv, amount, inq, outq, dt = r
            total_in += inq
            total_out += outq
            balance = total_in - total_out
            self.ledger_tv.insert("", "end", values=(
                "Stock IN" if ttype == "IN" else "Stock OUT",
                inv or "",
                amount if amount is not None else "",
                inq if inq else "",
                outq if outq else "",
                balance,
                dt
            ))

        striped_treeview(self.ledger_tv)
        self.ledger_summary.set(f"Totals: IN {total_in} | OUT {total_out} | Balance {balance}")

# ===================== MAIN =====================
if __name__ == "__main__":
    # Initialize / reset DB as requested
    init_db(reset=RESET_DB)

    root = tk.Tk()
    app = App(root)
    root.minsize(920, 560)
    root.mainloop()
