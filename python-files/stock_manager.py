
"""
Simple E‑Commerce Stock Management (FIFO) - single-file Python app
Features:
- Items + Purchase Batches (supports FIFO)
- Sales (reduces stock using FIFO, calculates COGS)
- Expenses
- Alerts for batches older than 30 days with remaining stock
- Profit & Loss statement (Revenue - COGS - Expenses)
- Lightweight SQLite DB (file: stock_manager.db)
- Export CSV reports
Instructions:
1. Install Python 3.8+ from https://www.python.org
2. (Optional) Create standalone executable: pip install pyinstaller
   pyinstaller --onefile stock_manager.py
3. Run: python stock_manager.py
"""
import sqlite3, os, csv, sys
from datetime import datetime, timedelta
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
except Exception as e:
    print("tkinter is required. On Windows it's included. Error:", e)
    sys.exit(1)

DB = os.path.join(os.path.dirname(__file__), "stock_manager.db")

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        sku TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS batches(
        id INTEGER PRIMARY KEY,
        item_id INTEGER,
        qty INTEGER,
        cost_per_unit REAL,
        purchase_date TEXT,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY,
        item_id INTEGER,
        qty INTEGER,
        unit_price REAL,
        date TEXT,
        cogs REAL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY,
        description TEXT,
        amount REAL,
        date TEXT
    )""")
    conn.commit()
    conn.close()

# DB helpers
def add_item(name, sku=None):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO items(name, sku) VALUES(?,?)", (name, sku))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_items():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT id,name,sku FROM items ORDER BY name")
    rows = cur.fetchall(); conn.close()
    return rows

def add_batch(item_id, qty, cost_per_unit, purchase_date):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("INSERT INTO batches(item_id,qty,cost_per_unit,purchase_date) VALUES(?,?,?,?)",
                (item_id, qty, cost_per_unit, purchase_date))
    conn.commit(); conn.close()

def get_batches_for_item(item_id):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT id,qty,cost_per_unit,purchase_date FROM batches WHERE item_id=? AND qty>0 ORDER BY date(purchase_date) ASC", (item_id,))
    rows = cur.fetchall(); conn.close()
    return rows

def total_stock_for_item(item_id):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT SUM(qty) FROM batches WHERE item_id=?", (item_id,))
    r = cur.fetchone()[0] or 0
    conn.close(); return r

def add_sale(item_id, sale_qty, unit_price, date_str):
    """
    Apply FIFO across batches; returns cogs
    """
    conn = sqlite3.connect(DB); cur = conn.cursor()
    remaining = sale_qty
    cogs_total = 0.0
    # fetch batches oldest first
    cur.execute("SELECT id,qty,cost_per_unit FROM batches WHERE item_id=? AND qty>0 ORDER BY date(purchase_date) ASC", (item_id,))
    batches = cur.fetchall()
    for b_id, b_qty, cost in batches:
        if remaining<=0: break
        take = min(b_qty, remaining)
        # reduce batch qty
        cur.execute("UPDATE batches SET qty = qty - ? WHERE id=?", (take, b_id))
        cogs_total += take * cost
        remaining -= take
    if remaining>0:
        conn.rollback()
        conn.close()
        raise ValueError("Not enough stock to complete sale.")
    # record sale
    cur.execute("INSERT INTO sales(item_id,qty,unit_price,date,cogs) VALUES(?,?,?,?,?)",
                (item_id, sale_qty, unit_price, date_str, cogs_total))
    conn.commit(); conn.close()
    return cogs_total

def add_expense(description, amount, date_str):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("INSERT INTO expenses(description,amount,date) VALUES(?,?,?)", (description, amount, date_str))
    conn.commit(); conn.close()

def get_revenue_and_cogs(date_from=None, date_to=None):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    q = "SELECT SUM(qty*unit_price), SUM(cogs) FROM sales WHERE 1=1"
    params=[]
    if date_from:
        q += " AND date>=?"
        params.append(date_from)
    if date_to:
        q += " AND date<=?"
        params.append(date_to)
    cur.execute(q, params)
    r = cur.fetchone(); conn.close()
    revenue = r[0] or 0.0; cogs = r[1] or 0.0
    return revenue, cogs

def get_total_expenses(date_from=None, date_to=None):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    q = "SELECT SUM(amount) FROM expenses WHERE 1=1"
    params=[]
    if date_from:
        q += " AND date>=?"
        params.append(date_from)
    if date_to:
        q += " AND date<=?"
        params.append(date_to)
    cur.execute(q, params)
    r = cur.fetchone(); conn.close()
    return r[0] or 0.0

def batches_older_than(days=30):
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("""SELECT items.name, SUM(batches.qty) as qty, MIN(batches.purchase_date)
                   FROM batches JOIN items ON items.id=batches.item_id
                   WHERE date(batches.purchase_date) <= date(?) AND batches.qty>0
                   GROUP BY items.name HAVING qty>0""", (cutoff,))
    rows = cur.fetchall(); conn.close()
    return rows

def export_csv(query, params, filename):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    headers = [d[0] for d in cur.description]
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    conn.close()

# GUI
class App:
    def __init__(self, root):
        self.root = root
        root.title("Simple Stock Manager (FIFO)")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        self.create_inventory_tab()
        self.create_purchase_tab()
        self.create_sales_tab()
        self.create_expense_tab()
        self.create_reports_tab()
        self.refresh_items()
        self.check_alerts_on_startup()

    def create_inventory_tab(self):
        frame = ttk.Frame(self.notebook); self.notebook.add(frame, text="Inventory")
        left = ttk.Frame(frame); left.pack(side='left', fill='y', padx=8, pady=8)
        ttk.Label(left, text="Items").pack(anchor='w')
        self.items_list = tk.Listbox(left, width=30)
        self.items_list.pack(fill='y', expand=True)
        self.items_list.bind("<<ListboxSelect>>", self.on_item_select)
        btn_frame = ttk.Frame(left); btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Add Item", command=self.ui_add_item).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export Items CSV", command=self.export_items).pack(side='left', padx=2)

        right = ttk.Frame(frame); right.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        ttk.Label(right, text="Batches (FIFO order)").pack(anchor='w')
        cols = ("id","qty","cost_per_unit","purchase_date")
        self.batches_tree = ttk.Treeview(right, columns=cols, show='headings')
        for c in cols:
            self.batches_tree.heading(c, text=c)
        self.batches_tree.pack(fill='both', expand=True)

    def create_purchase_tab(self):
        frame = ttk.Frame(self.notebook); self.notebook.add(frame, text="Purchase (Add Stock)")
        ttk.Label(frame, text="Item").grid(row=0,column=0,sticky='w', pady=4, padx=4)
        self.purchase_item_cb = ttk.Combobox(frame, state='readonly')
        self.purchase_item_cb.grid(row=0,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Quantity").grid(row=1,column=0,sticky='w', pady=4, padx=4)
        self.purchase_qty = tk.IntVar(value=1)
        ttk.Entry(frame, textvariable=self.purchase_qty).grid(row=1,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Cost per unit").grid(row=2,column=0,sticky='w', pady=4, padx=4)
        self.purchase_cost = tk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=self.purchase_cost).grid(row=2,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Purchase Date (YYYY-MM-DD)").grid(row=3,column=0,sticky='w', pady=4, padx=4)
        self.purchase_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frame, textvariable=self.purchase_date).grid(row=3,column=1,sticky='ew', padx=4)
        ttk.Button(frame, text="Add Batch", command=self.ui_add_batch).grid(row=4,column=0,columnspan=2,pady=8)

    def create_sales_tab(self):
        frame = ttk.Frame(self.notebook); self.notebook.add(frame, text="Sales")
        ttk.Label(frame, text="Item").grid(row=0,column=0,sticky='w', pady=4, padx=4)
        self.sale_item_cb = ttk.Combobox(frame, state='readonly')
        self.sale_item_cb.grid(row=0,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Quantity").grid(row=1,column=0,sticky='w', pady=4, padx=4)
        self.sale_qty = tk.IntVar(value=1)
        ttk.Entry(frame, textvariable=self.sale_qty).grid(row=1,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Unit Price (sale)").grid(row=2,column=0,sticky='w', pady=4, padx=4)
        self.sale_price = tk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=self.sale_price).grid(row=2,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=3,column=0,sticky='w', pady=4, padx=4)
        self.sale_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frame, textvariable=self.sale_date).grid(row=3,column=1,sticky='ew', padx=4)
        ttk.Button(frame, text="Record Sale", command=self.ui_record_sale).grid(row=4,column=0,columnspan=2,pady=8)

    def create_expense_tab(self):
        frame = ttk.Frame(self.notebook); self.notebook.add(frame, text="Expenses")
        ttk.Label(frame, text="Description").grid(row=0,column=0,sticky='w', padx=4, pady=4)
        self.exp_desc = tk.StringVar()
        ttk.Entry(frame, textvariable=self.exp_desc).grid(row=0,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Amount").grid(row=1,column=0,sticky='w', padx=4, pady=4)
        self.exp_amount = tk.DoubleVar(value=0.0)
        ttk.Entry(frame, textvariable=self.exp_amount).grid(row=1,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=2,column=0,sticky='w', padx=4, pady=4)
        self.exp_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frame, textvariable=self.exp_date).grid(row=2,column=1,sticky='ew', padx=4)
        ttk.Button(frame, text="Add Expense", command=self.ui_add_expense).grid(row=3,column=0,columnspan=2,pady=8)
        ttk.Button(frame, text="Export Expenses CSV", command=self.export_expenses).grid(row=4,column=0,columnspan=2,pady=8)

    def create_reports_tab(self):
        frame = ttk.Frame(self.notebook); self.notebook.add(frame, text="Reports / P&L")
        ttk.Label(frame, text="From (YYYY-MM-DD)").grid(row=0,column=0,sticky='w', padx=4, pady=4)
        self.r_from = tk.StringVar()
        ttk.Entry(frame, textvariable=self.r_from).grid(row=0,column=1,sticky='ew', padx=4)
        ttk.Label(frame, text="To (YYYY-MM-DD)").grid(row=1,column=0,sticky='w', padx=4, pady=4)
        self.r_to = tk.StringVar()
        ttk.Entry(frame, textvariable=self.r_to).grid(row=1,column=1,sticky='ew', padx=4)
        ttk.Button(frame, text="Show P&L", command=self.ui_show_pl).grid(row=2,column=0,columnspan=2,pady=8)
        ttk.Button(frame, text="Export Sales CSV", command=self.export_sales).grid(row=3,column=0,columnspan=2,pady=4)
        ttk.Button(frame, text="Export P&L CSV", command=self.export_pl).grid(row=4,column=0,columnspan=2,pady=4)

        self.pl_text = tk.Text(frame, height=10)
        self.pl_text.grid(row=5,column=0,columnspan=2,sticky='nsew', padx=4, pady=4)
        frame.rowconfigure(5, weight=1)
        frame.columnconfigure(1, weight=1)

    # UI actions
    def refresh_items(self):
        items = get_items()
        self.items_list.delete(0, tk.END)
        names=[]
        for i in items:
            self.items_list.insert(tk.END, f"{i[1]} (id:{i[0]})")
            names.append(i[1])
        self.purchase_item_cb['values'] = names
        self.sale_item_cb['values'] = names

    def on_item_select(self, event):
        sel = self.items_list.curselection()
        if not sel: return
        text = self.items_list.get(sel[0])
        # extract id from text
        try:
            id_part = text.split("id:")[1].strip(")")
            item_id = int(id_part)
        except:
            return
        # populate batches
        for i in self.batches_tree.get_children():
            self.batches_tree.delete(i)
        for b in get_batches_for_item(item_id):
            self.batches_tree.insert("", "end", values=b)

    def ui_add_item(self):
        name = simpledialog.askstring("New item", "Item name:")
        if not name: return
        sku = simpledialog.askstring("SKU (optional)","SKU:")
        add_item(name, sku)
        self.refresh_items()
        messagebox.showinfo("Item", "Item added/updated.")

    def ui_add_batch(self):
        name = self.purchase_item_cb.get()
        if not name:
            messagebox.showwarning("Select item","Please select an item.")
            return
        # lookup id
        items = get_items()
        item_id = None
        for i in items:
            if i[1]==name:
                item_id = i[0]; break
        try:
            qty = int(self.purchase_qty.get())
            cost = float(self.purchase_cost.get())
            date = self.purchase_date.get()
            datetime.strptime(date, "%Y-%m-%d")
        except Exception as e:
            messagebox.showerror("Invalid", "Check quantity, cost, or date format (YYYY-MM-DD).")
            return
        add_batch(item_id, qty, cost, date)
        messagebox.showinfo("Batch", "Batch added.")
        self.refresh_items()

    def ui_record_sale(self):
        name = self.sale_item_cb.get()
        if not name:
            messagebox.showwarning("Select item","Please select an item.")
            return
        items = get_items()
        item_id = None
        for i in items:
            if i[1]==name:
                item_id = i[0]; break
        try:
            qty = int(self.sale_qty.get())
            price = float(self.sale_price.get())
            date = self.sale_date.get()
            datetime.strptime(date, "%Y-%m-%d")
        except Exception as e:
            messagebox.showerror("Invalid", "Check quantity, price, or date format (YYYY-MM-DD).")
            return
        try:
            cogs = add_sale(item_id, qty, price, date)
            messagebox.showinfo("Sale", f"Sale recorded. COGS = {cogs:.2f}")
            self.refresh_items()
        except ValueError as e:
            messagebox.showerror("Stock error", str(e))

    def ui_add_expense(self):
        desc = self.exp_desc.get()
        try:
            amt = float(self.exp_amount.get())
            date = self.exp_date.get()
            datetime.strptime(date, "%Y-%m-%d")
        except:
            messagebox.showerror("Invalid", "Check amount or date.")
            return
        add_expense(desc, amt, date)
        messagebox.showinfo("Expense", "Expense recorded.")

    def ui_show_pl(self):
        d1 = self.r_from.get() or None
        d2 = self.r_to.get() or None
        revenue, cogs = get_revenue_and_cogs(d1,d2)
        expenses = get_total_expenses(d1,d2)
        profit = revenue - cogs - expenses
        self.pl_text.delete("1.0", tk.END)
        self.pl_text.insert(tk.END, f"Revenue: {revenue:.2f}\nCOGS: {cogs:.2f}\nExpenses: {expenses:.2f}\n\nProfit: {profit:.2f}\n")

    # exports
    def export_items(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fn: return
        export_csv("SELECT id,name,sku FROM items", (), fn)
        messagebox.showinfo("Export", "Exported items CSV.")

    def export_sales(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fn: return
        export_csv("SELECT id,item_id,qty,unit_price,date,cogs FROM sales", (), fn)
        messagebox.showinfo("Export", "Exported sales CSV.")

    def export_expenses(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fn: return
        export_csv("SELECT id,description,amount,date FROM expenses", (), fn)
        messagebox.showinfo("Export", "Exported expenses CSV.")

    def export_pl(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fn: return
        d1 = self.r_from.get() or None; d2 = self.r_to.get() or None
        revenue, cogs = get_revenue_and_cogs(d1,d2)
        expenses = get_total_expenses(d1,d2)
        with open(fn, "w", newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["Revenue","COGS","Expenses","Profit"])
            w.writerow([revenue, cogs, expenses, revenue-cogs-expenses])
        messagebox.showinfo("Export", "Exported P&L CSV.")

    def check_alerts_on_startup(self):
        rows = batches_older_than(30)
        if rows:
            text = "Batches older than 30 days with remaining stock:\n\n"
            for name, qty, pd in rows:
                text += f"{name}: qty {qty}, oldest purchase {pd}\n"
            messagebox.showwarning("Stock Alert (30+ days)", text)

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.geometry("800x600")
    app = App(root)
    root.mainloop()
