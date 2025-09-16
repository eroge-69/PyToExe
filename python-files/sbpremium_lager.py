
#!/usr/bin/env python3
"""
Warehouse Manager (desktop)
Python 3, Tkinter GUI + SQLite3

Features:
- Add / edit products (stored as grams internally; display in kg+g)
- Add / edit customers
- Make sales (zaduženje): select customer, product, enter qty (kg+g) -> subtracts from stock and records transaction
- View products and current stock, low-stock warnings
- View transactions by product or customer
- Export CSV reports (products, transactions)

How to run:
    python warehouse_app.py

Dependencies: uses only Python stdlib (tkinter, sqlite3, csv, datetime)
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import os
from datetime import datetime
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse.db")

# ---------- Utilities ----------
def grams_from_input(kg_str, g_str):
    try:
        kg = int(kg_str) if kg_str else 0
        g = int(g_str) if g_str else 0
        if kg < 0 or g < 0:
            return None
        return kg * 1000 + g
    except ValueError:
        return None

def kg_g_from_grams(total_g):
    kg = total_g // 1000
    g = total_g % 1000
    return kg, g

def fmt_qty(total_g):
    kg, g = kg_g_from_grams(total_g)
    return f"{kg} kg {g} g"

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        qty_g INTEGER NOT NULL DEFAULT 0,
        min_qty_g INTEGER NOT NULL DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty_g INTEGER NOT NULL,
        date TEXT NOT NULL,
        remark TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    conn.commit()
    conn.close()

def db_execute(query, params=(), fetch=False, many=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if many:
        cur.executemany(query, params)
        conn.commit()
        conn.close()
        return None
    cur.execute(query, params)
    if fetch:
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    conn.commit()
    conn.close()
    return None

# ---------- App ----------
class WarehouseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Layali - Evidencija proizvoda")
        self.geometry("900x600")
        self.create_widgets()
        self.refresh_all()

    def create_widgets(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=8)

        # Products tab
        self.products_frame = ttk.Frame(nb)
        nb.add(self.products_frame, text="Proizvodi")
        self.create_products_tab(self.products_frame)

        # Customers tab
        self.customers_frame = ttk.Frame(nb)
        nb.add(self.customers_frame, text="Kupci")
        self.create_customers_tab(self.customers_frame)

        # Sales / Transactions tab
        self.sales_frame = ttk.Frame(nb)
        nb.add(self.sales_frame, text="Prodaja (Zaduživanje)")
        self.create_sales_tab(self.sales_frame)

        # Reports tab
        self.reports_frame = ttk.Frame(nb)
        nb.add(self.reports_frame, text="Izvještaj")
        self.create_reports_tab(self.reports_frame)

    # ---- Products Tab ----
    def create_products_tab(self, parent):
        left = ttk.Frame(parent)
        left.pack(side='left', fill='y', padx=6, pady=6)

        self.products_list = tk.Listbox(left, width=40)
        self.products_list.pack(fill='y', expand=True)
        self.products_list.bind("<<ListboxSelect>>", self.on_product_select)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill='x', pady=4)
        ttk.Button(btn_frame, text="Dodaj proizvod", command=self.add_product).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Uredi označeno", command=self.edit_product).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Obriši označeno", command=self.delete_product).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_products_csv).pack(side='left', padx=2)

        right = ttk.Frame(parent)
        right.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        self.prod_detail = tk.Text(right, state='disabled', width=60, height=20)
        self.prod_detail.pack(fill='both', expand=True)

    def refresh_products(self):
        self.products_list.delete(0,tk.END)
        rows = db_execute("SELECT id, name, qty_g, min_qty_g FROM products ORDER BY name", fetch=True)
        self.products = rows or []
        for r in self.products:
            pid, name, qty_g, min_qty = r
            display = f"{name} — {fmt_qty(qty_g)}"
            if qty_g <= min_qty:
                display += "  [LOW]"
            self.products_list.insert(tk.END, display)

    def on_product_select(self, event=None):
        sel = self.products_list.curselection()
        if not sel:
            self.prod_detail.config(state='normal')
            self.prod_detail.delete('1.0', tk.END)
            self.prod_detail.config(state='disabled')
            return
        idx = sel[0]
        pid, name, qty_g, min_qty = self.products[idx]
        txt = f"Product: {name}\nCurrent stock: {fmt_qty(qty_g)}\nMinimum stock: {fmt_qty(min_qty)}\n\nTransactions:\n"
        txs = db_execute("SELECT t.date, c.name, t.qty_g, t.remark FROM transactions t JOIN customers c ON t.customer_id=c.id WHERE t.product_id=? ORDER BY t.date DESC LIMIT 50", (pid,), fetch=True)
        if txs:
            for d, cname, qg, remark in txs:
                txt += f"{d} — {cname} — {fmt_qty(qg)}"
                if remark:
                    txt += f" — {remark}"
                txt += "\n"
        else:
            txt += "Nema transakcija"
        self.prod_detail.config(state='normal')
        self.prod_detail.delete('1.0', tk.END)
        self.prod_detail.insert(tk.END, txt)
        self.prod_detail.config(state='disabled')

    def add_product(self):
        d = ProductDialog(self, title="Dodaj proizvod")
        self.wait_window(d.top)
        if d.result:
            name, qty_g, min_g = d.result
            try:
                db_execute("INSERT INTO products (name, qty_g, min_qty_g) VALUES (?,?,?)", (name, qty_g, min_g))
                self.refresh_products()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Proizvod sa istim imenom već postoji")

    def edit_product(self):
        sel = self.products_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Prvo izaberi proizvod")
            return
        idx = sel[0]
        pid, name, qty_g, min_g = self.products[idx]
        d = ProductDialog(self, title="Uredi proizvod", name=name, qty_g=qty_g, min_g=min_g)
        self.wait_window(d.top)
        if d.result:
            name_new, qty_new, min_new = d.result
            db_execute("UPDATE products SET name=?, qty_g=?, min_qty_g=? WHERE id=?", (name_new, qty_new, min_new, pid))
            self.refresh_products()

    def delete_product(self):
        sel = self.products_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Prvo izaberi proizvod")
            return
        idx = sel[0]
        pid, name, qty_g, min_g = self.products[idx]
        if messagebox.askyesno("Potvrdi", f"Delete product '{name}'? This will NOT delete transactions."):
            db_execute("DELETE FROM products WHERE id=?", (pid,))
            self.refresh_products()
            self.prod_detail.config(state='normal')
            self.prod_detail.delete('1.0', tk.END)
            self.prod_detail.config(state='disabled')

    def export_products_csv(self):
        rows = db_execute("SELECT id, name, qty_g, min_qty_g FROM products ORDER BY name", fetch=True)
        if not rows:
            messagebox.showinfo("Info", "Nema proizvoda za export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV datoteka","*.csv")])
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["id","name","qty_g","qty_display","min_qty_g"])
            for pid, name, qty_g, min_g in rows:
                w.writerow([pid, name, qty_g, fmt_qty(qty_g), min_g])
        messagebox.showinfo("Exportovano", f"Products exported to {path}")

    # ---- Customers Tab ----
    def create_customers_tab(self, parent):
        left = ttk.Frame(parent)
        left.pack(side='left', fill='y', padx=6, pady=6)

        self.customers_list = tk.Listbox(left, width=40)
        self.customers_list.pack(fill='y', expand=True)
        self.customers_list.bind("<<ListboxSelect>>", self.on_customer_select)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill='x', pady=4)
        ttk.Button(btn_frame, text="Dodaj kupca", command=self.add_customer).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Uredi označeno", command=self.edit_customer).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Izbriši označeno", command=self.delete_customer).pack(side='left', padx=2)

        right = ttk.Frame(parent)
        right.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        self.cust_detail = tk.Text(right, state='disabled', width=60, height=20)
        self.cust_detail.pack(fill='both', expand=True)

    def refresh_customers(self):
        self.customers_list.delete(0,tk.END)
        rows = db_execute("SELECT id, name, contact FROM customers ORDER BY name", fetch=True)
        self.customers = rows or []
        for r in self.customers:
            cid, name, contact = r
            display = f"{name} — {contact if contact else ''}"
            self.customers_list.insert(tk.END, display)

    def on_customer_select(self, event=None):
        sel = self.customers_list.curselection()
        if not sel:
            self.cust_detail.config(state='normal')
            self.cust_detail.delete('1.0', tk.END)
            self.cust_detail.config(state='disabled')
            return
        idx = sel[0]
        cid, name, contact = self.customers[idx]
        txt = f"Customer: {name}\nContact: {contact}\n\nPurchases:\n"
        txs = db_execute("SELECT t.date, p.name, t.qty_g, t.remark FROM transactions t JOIN products p ON t.product_id=p.id WHERE t.customer_id=? ORDER BY t.date DESC LIMIT 50", (cid,), fetch=True)
        if txs:
            for d, pname, qg, remark in txs:
                txt += f"{d} — {pname} — {fmt_qty(qg)}"
                if remark:
                    txt += f" — {remark}"
                txt += "\n"
        else:
            txt += "No purchases."
        self.cust_detail.config(state='normal')
        self.cust_detail.delete('1.0', tk.END)
        self.cust_detail.insert(tk.END, txt)
        self.cust_detail.config(state='disabled')

    def add_customer(self):
        name = simpledialog.askstring("Ime kupca", "Unesi ime kupca:")
        if not name:
            return
        contact = simpledialog.askstring("Kontakt", "Unesi kontakt podatke ")
        db_execute("INSERT INTO customers (name, contact) VALUES (?,?)", (name.strip(), contact))
        self.refresh_customers()

    def edit_customer(self):
        sel = self.customers_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Prvo izberi kupca")
            return
        idx = sel[0]
        cid, name, contact = self.customers[idx]
        name_new = simpledialog.askstring("Ime kupca", "Uredi ime kupca:", initialvalue=name)
        if not name_new:
            return
        contact_new = simpledialog.askstring("Kontakt", "Uredi kontakt podatke", initialvalue=contact)
        db_execute("UPDATE customers SET name=?, contact=? WHERE id=?", (name_new.strip(), contact_new, cid))
        self.refresh_customers()

    def delete_customer(self):
        sel = self.customers_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Prvo izaberi kupca")
            return
        idx = sel[0]
        cid, name, contact = self.customers[idx]
        if messagebox.askyesno("Potrvdi", f"Delete customer '{name}'? This will NOT delete transactions."):
            db_execute("DELETE FROM customers WHERE id=?", (cid,))
            self.refresh_customers()
            self.cust_detail.config(state='normal')
            self.cust_detail.delete('1.0', tk.END)
            self.cust_detail.config(state='disabled')

    # ---- Sales tab ----
    def create_sales_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        top = ttk.Frame(frm)
        top.pack(fill='x')

        ttk.Label(top, text="Kupac:").grid(row=0,column=0,sticky='w')
        self.sale_customer_cb = ttk.Combobox(top, state='readonly', width=40)
        self.sale_customer_cb.grid(row=0,column=1,sticky='w', padx=4, pady=2)

        ttk.Label(top, text="Proizvod:").grid(row=1,column=0,sticky='w')
        self.sale_product_cb = ttk.Combobox(top, state='readonly', width=40)
        self.sale_product_cb.grid(row=1,column=1,sticky='w', padx=4, pady=2)

        qtyfrm = ttk.Frame(top)
        qtyfrm.grid(row=2,column=0,columnspan=2,sticky='w', pady=6)
        ttk.Label(qtyfrm, text="Quantity:").pack(side='left')
        self.sale_kg = tk.Entry(qtyfrm, width=6)
        self.sale_kg.pack(side='left', padx=4)
        ttk.Label(qtyfrm, text="kg").pack(side='left')
        self.sale_g = tk.Entry(qtyfrm, width=6)
        self.sale_g.pack(side='left', padx=4)
        ttk.Label(qtyfrm, text="g").pack(side='left')

        ttk.Label(top, text="Remark (optional):").grid(row=3,column=0,sticky='w')
        self.sale_remark = tk.Entry(top, width=60)
        self.sale_remark.grid(row=3,column=1,sticky='w', padx=4, pady=2)

        ttk.Button(top, text="Izvrši kupovinu (Zaduži)", command=self.make_sale).grid(row=4,column=0,columnspan=2,pady=8)

        # Bottom: recent transactions
        bottom = ttk.Frame(frm)
        bottom.pack(fill='both', expand=True)
        self.tx_list = tk.Listbox(bottom)
        self.tx_list.pack(fill='both', expand=True)

    def refresh_sales_comboboxes(self):
        rows = db_execute("SELECT id, name, qty_g FROM products ORDER BY name", fetch=True) or []
        self.products_for_cb = rows
        prod_names = [f"{r[1]} — {fmt_qty(r[2])}" for r in rows]
        self.sale_product_cb['values'] = prod_names

        rows2 = db_execute("SELECT id, name FROM customers ORDER BY name", fetch=True) or []
        self.customers_for_cb = rows2
        cust_names = [r[1] for r in rows2]
        self.sale_customer_cb['values'] = cust_names

    def refresh_transactions(self):
        self.tx_list.delete(0, tk.END)
        rows = db_execute("SELECT t.date, c.name, p.name, t.qty_g, t.remark FROM transactions t JOIN customers c ON t.customer_id=c.id JOIN products p ON t.product_id=p.id ORDER BY t.date DESC LIMIT 200", fetch=True)
        if rows:
            for d, cname, pname, qg, remark in rows:
                line = f"{d} — {cname} — {pname} — {fmt_qty(qg)}"
                if remark:
                    line += f" — {remark}"
                self.tx_list.insert(tk.END, line)

    def make_sale(self):
        ci = self.sale_customer_cb.current()
        pi = self.sale_product_cb.current()
        if ci < 0 or pi < 0:
            messagebox.showinfo("Info", "Izbaberi kupca i proizvod")
            return
        cust_id = self.customers_for_cb[ci][0]
        prod_id = self.products_for_cb[pi][0]
        qty = grams_from_input(self.sale_kg.get(), self.sale_g.get())
        if qty is None or qty <= 0:
            messagebox.showerror("Error", "Unesi količinu ( kg, g) ")
            return
        # Check stock
        cur = db_execute("SELECT qty_g, name FROM products WHERE id=?", (prod_id,), fetch=True)
        if not cur:
            messagebox.showerror("Error", "Proizvod nije pronađen")
            return
        cur_qty, prod_name = cur[0]
        if qty > cur_qty:
            if not messagebox.askyesno("Potvrdi", f"Not enough stock for {prod_name} (available {fmt_qty(cur_qty)}). Da li želiš potvriditi količinu u minusu"):
                return
        # record transaction and update product
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        remark = self.sale_remark.get().strip()
        db_execute("INSERT INTO transactions (customer_id, product_id, qty_g, date, remark) VALUES (?,?,?,?,?)", (cust_id, prod_id, qty, date, remark))
        new_qty = cur_qty - qty
        db_execute("UPDATE products SET qty_g=? WHERE id=?", (new_qty, prod_id))
        messagebox.showinfo("Done", f"Sold {fmt_qty(qty)} of {prod_name} to {self.customers_for_cb[ci][1] if len(self.customers_for_cb[ci])>1 else self.sale_customer_cb.get()}")
        # clear inputs
        self.sale_kg.delete(0, tk.END)
        self.sale_g.delete(0, tk.END)
        self.sale_remark.delete(0, tk.END)
        self.refresh_all()

    # ---- Reports tab ----
    def create_reports_tab(self, parent):
        top = ttk.Frame(parent)
        top.pack(fill='x', padx=6, pady=6)
        ttk.Button(top, text="Exportuj transakcije u CSV format", command=self.export_transactions_csv).pack(side='left', padx=4)
        ttk.Button(top, text="Osvježi", command=self.refresh_all).pack(side='left', padx=4)

        mid = ttk.Frame(parent)
        mid.pack(fill='both', expand=True, padx=6, pady=6)
        self.reports_tv = ttk.Treeview(mid, columns=("col1","col2","col3","col4"), show='headings')
        self.reports_tv.heading("col1", text="Datum")
        self.reports_tv.heading("col2", text="Kupac")
        self.reports_tv.heading("col3", text="Proizvod")
        self.reports_tv.heading("col4", text="Količina")
        self.reports_tv.pack(fill='both', expand=True)

    def export_transactions_csv(self):
        rows = db_execute("SELECT t.id, t.date, c.name, p.name, t.qty_g, t.remark FROM transactions t JOIN customers c ON t.customer_id=c.id JOIN products p ON t.product_id=p.id ORDER BY t.date DESC", fetch=True)
        if not rows:
            messagebox.showinfo("Info", "Nema transakcija za export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["id","date","customer","product","qty_g","qty_display","remark"])
            for tid, date, cname, pname, qg, remark in rows:
                w.writerow([tid, date, cname, pname, qg, fmt_qty(qg), remark])
        messagebox.showinfo("Exportovano", f"Transactions exported to {path}")

    def refresh_reports(self):
        for r in self.reports_tv.get_children():
            self.reports_tv.delete(r)
        rows = db_execute("SELECT t.date, c.name, p.name, t.qty_g FROM transactions t JOIN customers c ON t.customer_id=c.id JOIN products p ON t.product_id=p.id ORDER BY t.date DESC LIMIT 200", fetch=True) or []
        for date, cname, pname, qg in rows:
            self.reports_tv.insert('', tk.END, values=(date, cname, pname, fmt_qty(qg)))

    # ---- Misc ----
    def refresh_all(self):
        self.refresh_products()
        self.refresh_customers()
        self.refresh_sales_comboboxes()
        self.refresh_transactions()
        self.refresh_reports()

# ---------- Dialogs ----------
class ProductDialog:
    def __init__(self, parent, title="Proizvod", name="", qty_g=0, min_g=0):
        top = self.top = tk.Toplevel(parent)
        top.title(title)
        self.result = None

        ttk.Label(top, text="Ime:").grid(row=0,column=0,sticky='w')
        self.entry_name = ttk.Entry(top, width=40)
        self.entry_name.grid(row=0,column=1,padx=4,pady=4)
        self.entry_name.insert(0, name)

        ttk.Label(top, text="Količina (kg):").grid(row=1,column=0,sticky='w')
        self.entry_kg = ttk.Entry(top, width=8)
        self.entry_kg.grid(row=1,column=1,sticky='w', padx=4)
        ttk.Label(top, text="g:").grid(row=1,column=1,sticky='e')
        self.entry_g = ttk.Entry(top, width=8)
        self.entry_g.grid(row=1,column=1,sticky='e', padx=50)

        kg, g = kg_g_from_grams(qty_g)
        self.entry_kg.delete(0, tk.END); self.entry_kg.insert(0, str(kg))
        self.entry_g.delete(0, tk.END); self.entry_g.insert(0, str(g))

        ttk.Label(top, text="Minimum (kg):").grid(row=2,column=0,sticky='w')
        self.min_kg = ttk.Entry(top, width=8)
        self.min_kg.grid(row=2,column=1,sticky='w', padx=4)
        ttk.Label(top, text="g:").grid(row=2,column=1,sticky='e')
        self.min_g = ttk.Entry(top, width=8)
        self.min_g.grid(row=2,column=1,sticky='e', padx=50)
        minkg, ming = kg_g_from_grams(min_g)
        self.min_kg.delete(0, tk.END); self.min_kg.insert(0, str(minkg))
        self.min_g.delete(0, tk.END); self.min_g.insert(0, str(ming))

        btn_frame = ttk.Frame(top)
        btn_frame.grid(row=3,column=0,columnspan=2,pady=8)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side='left', padx=6)
        ttk.Button(btn_frame, text="Odustani", command=top.destroy).pack(side='left', padx=6)

    def on_ok(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Ime obavezno")
            return
        qty = grams_from_input(self.entry_kg.get(), self.entry_g.get())
        minq = grams_from_input(self.min_kg.get(), self.min_g.get())
        if qty is None or minq is None:
            messagebox.showerror("Error", "Neispravan unos količine")
            return
        self.result = (name, qty, minq)
        self.top.destroy()

# ---------- Main ----------
def ensure_sample_data():
    # create a few sample products/customers if DB empty
    prods = db_execute("SELECT COUNT(*) FROM products", fetch=True)[0][0]
    custs = db_execute("SELECT COUNT(*) FROM customers", fetch=True)[0][0]
    if prods == 0:
        sample = [
            ("Limun", 50000, 10000), # 50 kg, min 10 kg
            ("Peach", 12000, 2000),    # 12 kg
            ("Ice", 3000, 500),      # 3 kg
        ]
        db_execute("INSERT INTO products (name, qty_g, min_qty_g) VALUES (?,?,?)", sample[0], many=False)
        # insert rest
        if len(sample) > 1:
            db_execute("INSERT INTO products (name, qty_g, min_qty_g) VALUES (?,?,?)", sample[1], many=False)
            db_execute("INSERT INTO products (name, qty_g, min_qty_g) VALUES (?,?,?)", sample[2], many=False)
    if custs == 0:
        samplec = [("Firma Primjer","061-123-456"), ("Marko Markovic","061-654-321")]
        db_execute("INSERT INTO customers (name, contact) VALUES (?,?)", samplec[0], many=False)
        db_execute("INSERT INTO customers (name, contact) VALUES (?,?)", samplec[1], many=False)

def main():
    init_db()
    ensure_sample_data()
    app = WarehouseApp()
    app.mainloop()

if __name__ == "__main__":
    main()
