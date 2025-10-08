# inventory_billing_windows.py
# Windows-ready Inventory & Billing MVP
# Standard library only (tkinter, sqlite3, csv, hashlib, etc.)
# Tested conceptually across Windows; if you see an exception paste trace and I'll help.

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import os
import csv
import hashlib
from datetime import datetime, timedelta
import tempfile
import webbrowser
import shutil
import logging
import json

APP_NAME = "InventoryBillingWin"
DB_FILE = "inventory_win.db"
LOG_FILE = "inventory_win.log"
CONFIG_FILE = "inventory_win_config.json"

# ------------- Logging --------------
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
def log_info(msg):
    logging.info(msg)
def log_err(msg):
    logging.exception(msg)

# ------------- Utilities --------------
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def parse_money(s):
    s = str(s).strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except Exception:
        raise ValueError("Invalid money value")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# ------------- Config --------------
DEFAULT_CONFIG = {"tax_rate_percent": 18.0, "currency_symbol": "₹"}
def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

CONFIG = load_config()

# ------------- Database --------------
def init_db():
    new_db = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    # items
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            qty INTEGER NOT NULL,
            reorder_level INTEGER DEFAULT 0
        )
    ''')
    # invoices
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            total REAL NOT NULL,
            tax REAL,
            discount REAL,
            user TEXT
        )
    ''')
    # invoice lines
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoice_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_id INTEGER,
            sku TEXT,
            name TEXT,
            unit_price REAL,
            quantity INTEGER,
            discount REAL,
            line_total REAL
        )
    ''')
    # users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
    ''')
    conn.commit()
    if new_db:
        log_info("Created new DB")
    return conn

# ------------- App main class --------------
class InventoryBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Windows Edition")
        self.conn = init_db()
        self.user = None
        self.cart = []  # list of dicts
        self.undo_stack = []
        self.build_ui()
        self.refresh_items()
        self.load_shortcuts()

    # ---------------- UI ----------------
    def build_ui(self):
        self.root.geometry("1050x640")
        main = ttk.Frame(self.root, padding=6)
        main.pack(fill=tk.BOTH, expand=True)

        # Top: toolbar with login, search, settings
        top = ttk.Frame(main)
        top.pack(fill=tk.X)
        self.login_btn = ttk.Button(top, text="Login", command=self.login_dialog)
        self.login_btn.pack(side=tk.LEFT)
        ttk.Button(top, text="Create Admin", command=self.create_admin_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Backup DB", command=self.backup_db).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Restore DB", command=self.restore_db).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Export Inventory CSV", command=self.export_inventory_csv).pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Search:").pack(side=tk.LEFT, padx=(12,4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_items())
        self.search_entry = ttk.Entry(top, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT)

        ttk.Button(top, text="Low stock report", command=self.low_stock_report).pack(side=tk.RIGHT)

        # Middle split: left inventory, right billing
        middle = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
        middle.pack(fill=tk.BOTH, expand=True, pady=6)

        # Left inventory
        left_frame = ttk.Frame(middle, padding=6)
        middle.add(left_frame, weight=2)
        ttk.Label(left_frame, text="Inventory", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        columns = ("id","sku","name","category","price","qty","reorder")
        self.item_tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        for col, text in zip(columns, ("ID","SKU","Name","Category","Price","Qty","Reorder")):
            self.item_tree.heading(col, text=text)
            self.item_tree.column(col, width=80 if col in ("id","sku","price","qty","reorder") else 200)
        self.item_tree.pack(fill=tk.BOTH, expand=True)
        self.item_tree.bind("<Double-1>", lambda e: self.edit_selected_item())

        inv_ctrl = ttk.Frame(left_frame)
        inv_ctrl.pack(fill=tk.X, pady=6)
        ttk.Button(inv_ctrl, text="Add Item (Ctrl+N)", command=self.add_item_dialog).pack(side=tk.LEFT)
        ttk.Button(inv_ctrl, text="Edit Selected", command=self.edit_selected_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(inv_ctrl, text="Delete Selected", command=self.delete_selected_item).pack(side=tk.LEFT, padx=4)
        ttk.Button(inv_ctrl, text="Refresh", command=self.refresh_items).pack(side=tk.RIGHT)

        # Right billing
        right_frame = ttk.Frame(middle, padding=6)
        middle.add(right_frame, weight=3)
        ttk.Label(right_frame, text="Billing / Cart", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        # Selector
        sel_frame = ttk.Frame(right_frame)
        sel_frame.pack(fill=tk.X, pady=(4,8))
        ttk.Label(sel_frame, text="Item:").pack(side=tk.LEFT)
        self.item_combo = ttk.Combobox(sel_frame, width=40, state="readonly")
        self.item_combo.pack(side=tk.LEFT, padx=4)
        ttk.Label(sel_frame, text="Qty:").pack(side=tk.LEFT, padx=(8,0))
        self.qty_entry = ttk.Entry(sel_frame, width=6)
        self.qty_entry.pack(side=tk.LEFT, padx=4)
        ttk.Label(sel_frame, text="Line Discount (%):").pack(side=tk.LEFT, padx=(8,0))
        self.line_discount_entry = ttk.Entry(sel_frame, width=6)
        self.line_discount_entry.insert(0,"0")
        self.line_discount_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(sel_frame, text="Add to Cart (Enter)", command=self.add_to_cart).pack(side=tk.LEFT, padx=6)

        # Cart tree
        cart_cols = ("sku","name","unit","qty","ldisc","ltotal")
        self.cart_tree = ttk.Treeview(right_frame, columns=cart_cols, show="headings", height=12)
        for col, txt in zip(cart_cols, ("SKU","Name","Unit","Qty","LineDisc%","LineTotal")):
            self.cart_tree.heading(col, text=txt)
            self.cart_tree.column(col, width=100 if col in ("sku","unit","qty","ldisc","ltotal") else 220)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        cart_ctrl = ttk.Frame(right_frame)
        cart_ctrl.pack(fill=tk.X, pady=6)
        ttk.Button(cart_ctrl, text="Remove Selected", command=self.remove_from_cart).pack(side=tk.LEFT)
        ttk.Button(cart_ctrl, text="Undo Last Action", command=self.undo_action).pack(side=tk.LEFT, padx=6)
        ttk.Button(cart_ctrl, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, padx=6)

        # Totals & actions
        tot_frame = ttk.Frame(right_frame)
        tot_frame.pack(fill=tk.X, pady=6)
        ttk.Label(tot_frame, text="Discount overall (% or fixed):").pack(side=tk.LEFT)
        self.overall_discount_entry = ttk.Entry(tot_frame, width=10)
        self.overall_discount_entry.insert(0,"0")
        self.overall_discount_entry.pack(side=tk.LEFT, padx=4)
        self.discount_mode_var = tk.StringVar(value="percent")
        ttk.Radiobutton(tot_frame, text="%", variable=self.discount_mode_var, value="percent").pack(side=tk.LEFT)
        ttk.Radiobutton(tot_frame, text="Fixed", variable=self.discount_mode_var, value="fixed").pack(side=tk.LEFT)

        ttk.Label(tot_frame, text="Tax %:").pack(side=tk.LEFT, padx=(12,0))
        self.tax_var = tk.StringVar(value=str(CONFIG.get("tax_rate_percent",18.0)))
        self.tax_entry = ttk.Entry(tot_frame, width=6, textvariable=self.tax_var)
        self.tax_entry.pack(side=tk.LEFT, padx=4)

        ttk.Label(tot_frame, text="Total:").pack(side=tk.LEFT, padx=(12,0))
        self.total_var = tk.StringVar(value=f"{CONFIG.get('currency_symbol','₹')}0.00")
        ttk.Label(tot_frame, textvariable=self.total_var, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(4,0))

        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X)
        ttk.Button(action_frame, text="Save Invoice (Ctrl+S)", command=self.save_invoice).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Preview/Print Invoice", command=self.preview_invoice).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="Export Invoice CSV", command=self.export_cart_csv).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="Sales Report", command=self.sales_report_dialog).pack(side=tk.RIGHT)

        # Status bar
        status = ttk.Frame(self.root)
        status.pack(fill=tk.X)
        self.status_var = tk.StringVar(value="Welcome")
        ttk.Label(status, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)

    # ---------------- Shortcuts ----------------
    def load_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.add_item_dialog())
        self.root.bind("<Control-s>", lambda e: self.save_invoice())
        self.root.bind("<Control-b>", lambda e: self.backup_db())
        self.root.bind("<Return>", lambda e: self.add_to_cart())

    # ---------------- DB / Inventory ops ----------------
    def refresh_items(self):
        q = self.search_var.get().strip().lower()
        c = self.conn.cursor()
        if q:
            like = f"%{q}%"
            c.execute("SELECT id, sku, name, category, price, qty, reorder_level FROM items WHERE sku LIKE ? OR name LIKE ? OR category LIKE ? ORDER BY name",
                      (like, like, like))
        else:
            c.execute("SELECT id, sku, name, category, price, qty, reorder_level FROM items ORDER BY name")
        rows = c.fetchall()
        for r in self.item_tree.get_children():
            self.item_tree.delete(r)
        combo_vals=[]
        self._combomap={}
        for row in rows:
            self.item_tree.insert("", tk.END, values=row)
            display = f"{row[2]} [{row[1]}] ({row[4]:.2f}, {row[5]}pcs)"
            combo_vals.append(display)
            self._combomap[display]=row[0]
        self.item_combo['values']=combo_vals
        self.status_var.set(f"Loaded {len(rows)} items")
        self.check_low_stock_visual(rows)

    def check_low_stock_visual(self, rows):
        # simple change of background of tree rows when low stock
        # tkinter treeview doesn't support per-row background easily cross-platform; skip heavy styling.
        low = [r for r in rows if r[5] <= (r[6] or 0)]
        if low:
            self.status_var.set(f"Low stock for {len(low)} items. Click 'Low stock report'.")
        else:
            self.status_var.set("Inventory OK")

    def add_item_dialog(self):
        dlg = ItemEditDialog(self.root, title="Add Item")
        if dlg.result:
            sku, name, category, price, qty, reorder = dlg.result
            try:
                self.add_item(sku, name, category, price, qty, reorder)
                self.refresh_items()
                messagebox.showinfo("Added", f"Item '{name}' added")
            except Exception as e:
                log_err("Add item failed")
                messagebox.showerror("Error", str(e))

    def add_item(self, sku, name, category, price, qty, reorder):
        c = self.conn.cursor()
        c.execute("INSERT INTO items (sku,name,category,price,qty,reorder_level) VALUES (?, ?, ?, ?, ?, ?)",
                  (sku.strip() or None, name.strip(), category.strip(), float(price), int(qty), int(reorder)))
        self.conn.commit()
        log_info(f"Item added: {name} ({sku})")

    def edit_selected_item(self):
        sel = self.item_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item to edit.")
            return
        vals = self.item_tree.item(sel[0], 'values')
        item = {"id":vals[0], "sku":vals[1], "name":vals[2], "category":vals[3], "price":vals[4], "qty":vals[5], "reorder":vals[6]}
        dlg = ItemEditDialog(self.root, title="Edit Item", prefill=item)
        if dlg.result:
            sku, name, category, price, qty, reorder = dlg.result
            try:
                c = self.conn.cursor()
                c.execute("UPDATE items SET sku=?, name=?, category=?, price=?, qty=?, reorder_level=? WHERE id=?",
                          (sku.strip() or None, name.strip(), category.strip(), float(price), int(qty), int(reorder), item["id"]))
                self.conn.commit()
                self.refresh_items()
                log_info(f"Item updated: {name}")
            except Exception as e:
                log_err("Edit item failed")
                messagebox.showerror("Error", str(e))

    def delete_selected_item(self):
        sel = self.item_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an item to delete.")
            return
        vals = self.item_tree.item(sel[0], 'values')
        if messagebox.askyesno("Confirm", f"Delete '{vals[2]}'?"):
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM items WHERE id=?", (vals[0],))
                self.conn.commit()
                self.refresh_items()
                log_info(f"Item deleted: {vals[2]}")
            except Exception as e:
                log_err("Delete item failed")
                messagebox.showerror("Error", str(e))

    # ---------------- CSV import/export ----------------
    def import_csv(self):
        fn = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not fn:
            return
        try:
            with open(fn, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                c = self.conn.cursor()
                count=0
                for row in reader:
                    # expect sku,name,category,price,qty,reorder_level (some may be missing)
                    sku = row.get("sku") or row.get("SKU") or ""
                    name = row.get("name") or row.get("Name")
                    if not name:
                        continue
                    price = float(row.get("price") or row.get("unit_price") or 0)
                    qty = int(float(row.get("qty") or row.get("quantity") or 0))
                    reorder = int(float(row.get("reorder_level") or row.get("reorder") or 0))
                    category = row.get("category") or ""
                    try:
                        c.execute("INSERT INTO items (sku,name,category,price,qty,reorder_level) VALUES (?,?,?,?,?,?)",
                                  (sku.strip() or None, name.strip(), category.strip(), price, qty, reorder))
                        count+=1
                    except sqlite3.IntegrityError:
                        # SKU unique constraint — update existing by SKU or name
                        try:
                            if sku:
                                c.execute("UPDATE items SET name=?,category=?,price=?,qty=?,reorder_level=? WHERE sku=?",
                                          (name.strip(), category.strip(), price, qty, reorder, sku))
                                count+=1
                            else:
                                c.execute("UPDATE items SET category=?,price=?,qty=?,reorder_level=? WHERE name=?",
                                          (category.strip(), price, qty, reorder, name))
                                count+=1
                        except Exception:
                            pass
                self.conn.commit()
                messagebox.showinfo("Imported", f"Imported/updated {count} items")
                log_info(f"Imported CSV: {fn}, count={count}")
                self.refresh_items()
        except Exception as e:
            log_err("Import CSV failed")
            messagebox.showerror("Import failed", str(e))

    def export_inventory_csv(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not fn:
            return
        try:
            c = self.conn.cursor()
            c.execute("SELECT sku,name,category,price,qty,reorder_level FROM items ORDER BY name")
            rows = c.fetchall()
            with open(fn, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["sku","name","category","price","qty","reorder_level"])
                for r in rows:
                    w.writerow(r)
            messagebox.showinfo("Exported", f"Inventory exported to {fn}")
            log_info(f"Exported inventory CSV to {fn}")
        except Exception as e:
            log_err("Export inventory failed")
            messagebox.showerror("Error", str(e))

    # ---------------- Cart ops ----------------
    def add_to_cart(self):
        sel = self.item_combo.get()
        if not sel:
            messagebox.showinfo("Info","Select an item")
            return
        try:
            item_id = self._combomap[sel]
        except Exception:
            messagebox.showerror("Error","Selection mismatch")
            return
        try:
            qty = int(self.qty_entry.get().strip() or "1")
            if qty <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Error","Invalid quantity")
            return
        try:
            line_disc = float(self.line_discount_entry.get().strip() or "0")
        except Exception:
            messagebox.showerror("Error","Invalid line discount")
            return

        c = self.conn.cursor()
        c.execute("SELECT sku,name,price,qty FROM items WHERE id=?", (item_id,))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error","Item not found")
            return
        sku, name, price, stock = row
        if qty > stock:
            if not messagebox.askyesno("Confirm", f"Only {stock} in stock. Add anyway?"):
                return
        line_total = round(price * qty * (1 - line_disc/100.0),2)
        entry = {"item_id": item_id, "sku": sku or "", "name": name, "unit": price, "qty": qty, "ldisc": line_disc, "ltotal": line_total}
        self.cart.append(entry)
        self.undo_stack.append(("add", entry))
        self.refresh_cart()
        self.qty_entry.delete(0,tk.END)
        self.line_discount_entry.delete(0,tk.END)
        self.line_discount_entry.insert(0,"0")
        self.status_var.set(f"Added {qty} x {name}")
        log_info(f"Cart add: {name} x{qty}")

    def refresh_cart(self):
        for r in self.cart_tree.get_children():
            self.cart_tree.delete(r)
        for it in self.cart:
            self.cart_tree.insert("", tk.END, values=(it['sku'], it['name'], f"{it['unit']:.2f}", it['qty'], f"{it['ldisc']:.2f}", f"{it['ltotal']:.2f}"))
        self.recalculate_totals()

    def remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showinfo("Info","Select a cart line to remove")
            return
        idx = self.cart_tree.index(sel[0])
        removed = self.cart.pop(idx)
        self.undo_stack.append(("remove", removed, idx))
        self.refresh_cart()
        self.status_var.set(f"Removed {removed['name']}")
        log_info(f"Cart remove: {removed['name']}")

    def clear_cart(self):
        if messagebox.askyesno("Confirm","Clear cart?"):
            self.undo_stack.append(("clear", list(self.cart)))
            self.cart.clear()
            self.refresh_cart()
            self.status_var.set("Cart cleared")

    def undo_action(self):
        if not self.undo_stack:
            messagebox.showinfo("Info","Nothing to undo")
            return
        action = self.undo_stack.pop()
        if action[0]=="add":
            entry = action[1]
            # remove last matching entry
            for i in range(len(self.cart)-1, -1, -1):
                if self.cart[i] is entry:
                    self.cart.pop(i)
                    break
        elif action[0]=="remove":
            entry = action[1]; idx = action[2]
            self.cart.insert(idx, entry)
        elif action[0]=="clear":
            self.cart = list(action[1])
        self.refresh_cart()
        self.status_var.set("Undid last action")
        log_info("Undid action")

    def recalculate_totals(self):
        subtotal = sum(it['ltotal'] for it in self.cart)
        # overall discount
        disc_val = 0.0
        ovd = self.overall_discount_entry.get().strip()
        try:
            ov = float(ovd) if ovd else 0.0
        except Exception:
            ov = 0.0
        if self.discount_mode_var.get()=="percent":
            disc_val = subtotal * (ov/100.0)
        else:
            disc_val = ov
        subtotal_after = max(0.0, subtotal - disc_val)
        try:
            tax_percent = float(self.tax_var.get().strip() or CONFIG.get("tax_rate_percent",18.0))
        except Exception:
            tax_percent = CONFIG.get("tax_rate_percent",18.0)
        tax = subtotal_after * (tax_percent/100.0)
        total = round(subtotal_after + tax,2)
        self.total_var.set(f"{CONFIG.get('currency_symbol','₹')}{total:.2f}")

    # ---------------- Invoice ops ----------------
    def save_invoice(self):
        if not self.cart:
            messagebox.showinfo("Info","Cart is empty")
            return
        if not self.user:
            if not messagebox.askyesno("Confirm","You are not logged in. Save invoice anyway?"):
                return
        # commit: reduce stock, save invoice and lines
        try:
            c = self.conn.cursor()
            subtotal = sum(it['ltotal'] for it in self.cart)
            ovd = float(self.overall_discount_entry.get().strip() or 0)
            if self.discount_mode_var.get()=="percent":
                discount = subtotal * (ovd/100.0)
            else:
                discount = ovd
            subtotal_after = max(0.0, subtotal - discount)
            tax_percent = float(self.tax_var.get().strip() or CONFIG.get("tax_rate_percent",18.0))
            tax = subtotal_after * (tax_percent/100.0)
            total = round(subtotal_after + tax, 2)
            now = datetime.now().isoformat(timespec='seconds')
            c.execute("INSERT INTO invoices (created_at,total,tax,discount,user) VALUES (?,?,?,?,?)",
                      (now, total, tax, discount, (self.user or "unknown")))
            invoice_id = c.lastrowid
            for it in self.cart:
                c.execute("INSERT INTO invoice_lines (invoice_id,item_id,sku,name,unit_price,quantity,discount,line_total) VALUES (?,?,?,?,?,?,?,?)",
                          (invoice_id, it['item_id'], it['sku'], it['name'], it['unit'], it['qty'], it['ldisc'], it['ltotal']))
                # decrease stock
                c.execute("SELECT qty FROM items WHERE id=?", (it['item_id'],))
                r = c.fetchone()
                if r:
                    new_qty = r[0] - it['qty']
                    c.execute("UPDATE items SET qty=? WHERE id=?", (new_qty, it['item_id']))
            self.conn.commit()
            log_info(f"Saved invoice {invoice_id} by {self.user or 'unknown'} total={total}")
            messagebox.showinfo("Saved", f"Invoice #{invoice_id} saved (Total: {CONFIG.get('currency_symbol')} {total:.2f})")
            self.cart.clear()
            self.refresh_cart()
            self.refresh_items()
            # optionally preview
            if messagebox.askyesno("Print", "Open printable invoice now?"):
                self.open_invoice_html(invoice_id)
        except Exception as e:
            log_err("Save invoice failed")
            messagebox.showerror("Error", str(e))

    def preview_invoice(self):
        # create temp preview html from current cart (not saved)
        if not self.cart:
            messagebox.showinfo("Info","Cart empty")
            return
        html = self.generate_invoice_html_preview()
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
        tmp.write(html)
        tmp.close()
        webbrowser.open(f"file://{tmp.name}")

    def generate_invoice_html_preview(self):
        subtotal = sum(it['ltotal'] for it in self.cart)
        ovd = float(self.overall_discount_entry.get().strip() or 0)
        if self.discount_mode_var.get()=="percent":
            discount = subtotal * (ovd/100.0)
        else:
            discount = ovd
        subtotal_after = max(0.0, subtotal - discount)
        tax_percent = float(self.tax_var.get().strip() or CONFIG.get("tax_rate_percent",18.0))
        tax = subtotal_after * (tax_percent/100.0)
        total = round(subtotal_after + tax,2)
        rows_html = ""
        for it in self.cart:
            rows_html += f"<tr><td>{it['sku']}</td><td>{it['name']}</td><td align='right'>{it['unit']:.2f}</td><td align='center'>{it['qty']}</td><td align='right'>{it['ldisc']:.2f}%</td><td align='right'>{it['ltotal']:.2f}</td></tr>"
        html = f"""
        <html><head><meta charset="utf-8"><title>Invoice Preview</title></head>
        <body>
        <h2>{APP_NAME} - Invoice Preview</h2>
        <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>SKU</th><th>Name</th><th>Unit</th><th>Qty</th><th>LineDisc%</th><th>LineTotal</th></tr>
        {rows_html}
        </table>
        <p>Subtotal: {CONFIG.get('currency_symbol')} {subtotal:.2f}</p>
        <p>Discount: {CONFIG.get('currency_symbol')} {discount:.2f}</p>
        <p>Tax ({tax_percent}%): {CONFIG.get('currency_symbol')} {tax:.2f}</p>
        <h3>Total: {CONFIG.get('currency_symbol')} {total:.2f}</h3>
        </body></html>
        """
        return html

    def open_invoice_html(self, invoice_id):
        c = self.conn.cursor()
        c.execute("SELECT id,created_at,total,tax,discount,user FROM invoices WHERE id=?", (invoice_id,))
        inv = c.fetchone()
        if not inv:
            messagebox.showerror("Error","Invoice not found")
            return
        lines = []
        c.execute("SELECT sku,name,unit_price,quantity,discount,line_total FROM invoice_lines WHERE invoice_id=?", (invoice_id,))
        for r in c.fetchall():
            lines.append(r)
        rows_html=""
        subtotal = 0.0
        for r in lines:
            sku,name,unit,qty,ldisc,ltotal = r
            rows_html += f"<tr><td>{sku}</td><td>{name}</td><td align='right'>{unit:.2f}</td><td align='center'>{qty}</td><td align='right'>{ldisc:.2f}%</td><td align='right'>{ltotal:.2f}</td></tr>"
            subtotal += ltotal
        created_at = inv[1]
        total = inv[2]
        tax = inv[3] or 0.0
        discount = inv[4] or 0.0
        user = inv[5] or "unknown"
        html = f"""
        <html><head><meta charset="utf-8"><title>Invoice #{invoice_id}</title></head>
        <body>
        <h2>{APP_NAME} - Invoice #{invoice_id}</h2>
        <p>Date: {created_at}</p>
        <p>Cashier: {user}</p>
        <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>SKU</th><th>Name</th><th>Unit</th><th>Qty</th><th>LineDisc%</th><th>LineTotal</th></tr>
        {rows_html}
        </table>
        <p>Subtotal: {CONFIG.get('currency_symbol')} {subtotal:.2f}</p>
        <p>Discount: {CONFIG.get('currency_symbol')} {discount:.2f}</p>
        <p>Tax: {CONFIG.get('currency_symbol')} {tax:.2f}</p>
        <h3>Total: {CONFIG.get('currency_symbol')} {total:.2f}</h3>
        </body></html>
        """
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
        tmp.write(html)
        tmp.close()
        webbrowser.open(f"file://{tmp.name}")

    def export_cart_csv(self):
        if not self.cart:
            messagebox.showinfo("Info","Cart empty")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not fn:
            return
        try:
            with open(fn, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["sku","name","unit_price","qty","line_discount_percent","line_total"])
                for it in self.cart:
                    w.writerow([it['sku'], it['name'], f"{it['unit']:.2f}", it['qty'], f"{it['ldisc']:.2f}", f"{it['ltotal']:.2f}"])
            messagebox.showinfo("Exported", f"Cart exported to {fn}")
            log_info(f"Exported cart CSV to {fn}")
        except Exception as e:
            log_err("Export cart failed")
            messagebox.showerror("Error", str(e))

    # ---------------- Reports & low stock ----------------
    def low_stock_report(self):
        c = self.conn.cursor()
        c.execute("SELECT sku,name,qty,reorder_level FROM items WHERE qty <= reorder_level ORDER BY qty")
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Low stock report", "No low-stock items")
            return
        txt = "Low stock items:\n\n"
        for r in rows:
            txt += f"{r[1]} [{r[0]}] - Qty {r[2]} (Reorder at {r[3]})\n"
        ReportDialog(self.root, "Low Stock Report", txt)

    def sales_report_dialog(self):
        dlg = DateRangeDialog(self.root, title="Sales Report")
        if dlg.result:
            start, end = dlg.result
            # include end day full day
            start_iso = start.isoformat()
            end_iso = (end + timedelta(days=1)).isoformat()
            c = self.conn.cursor()
            c.execute("SELECT id,created_at,total,user FROM invoices WHERE created_at >= ? AND created_at < ? ORDER BY created_at",
                      (start_iso, end_iso))
            invs = c.fetchall()
            if not invs:
                messagebox.showinfo("Sales", "No invoices in range")
                return
            rows_txt = "Invoices:\n\n"
            rows_csv = [["id","created_at","total","user"]]
            for inv in invs:
                rows_txt += f"#{inv[0]} {inv[1]}  {CONFIG.get('currency_symbol')} {inv[2]:.2f} by {inv[3]}\n"
                rows_csv.append([inv[0],inv[1],f"{inv[2]:.2f}",inv[3]])
            dlg2 = ReportDialog(self.root, "Sales Report", rows_txt, csv_rows=rows_csv)

    # ---------------- Backup / Restore ----------------
    def backup_db(self):
        fn = filedialog.asksaveasfilename(defaultextension=".db", title="Save DB Backup As", filetypes=[("DB file","*.db"),("All files","*.*")])
        if not fn:
            return
        try:
            shutil.copy2(DB_FILE, fn)
            messagebox.showinfo("Backup", f"Database backed up to {fn}")
            log_info(f"DB backup to {fn}")
        except Exception as e:
            log_err("DB backup failed")
            messagebox.showerror("Backup failed", str(e))

    def restore_db(self):
        fn = filedialog.askopenfilename(title="Select DB to restore", filetypes=[("DB file","*.db"),("All files","*.*")])
        if not fn:
            return
        if not messagebox.askyesno("Confirm", "Restore will overwrite the current DB. Continue?"):
            return
        try:
            self.conn.close()
            shutil.copy2(fn, DB_FILE)
            self.conn = init_db()
            self.refresh_items()
            messagebox.showinfo("Restored", "Database restored successfully.")
            log_info(f"DB restored from {fn}")
        except Exception as e:
            log_err("DB restore failed")
            messagebox.showerror("Restore failed", str(e))

    # ---------------- User login ----------------
    def create_admin_dialog(self):
        dlg = CreateUserDialog(self.root, title="Create Admin", require_role="admin")
        if dlg.result:
            username, password = dlg.result
            try:
                c = self.conn.cursor()
                c.execute("INSERT INTO users (username,password_hash,role) VALUES (?,?,?)",
                          (username, hash_password(password), "admin"))
                self.conn.commit()
                messagebox.showinfo("Created", "Admin user created")
                log_info(f"Admin created: {username}")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "User already exists")
            except Exception as e:
                log_err("Create admin failed")
                messagebox.showerror("Error", str(e))

    def login_dialog(self):
        dlg = LoginDialog(self.root, title="Login")
        if not dlg.result:
            return
        username, password = dlg.result
        c = self.conn.cursor()
        c.execute("SELECT password_hash,role FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error", "Unknown user")
            return
        phash, role = row
        if hash_password(password) == phash:
            self.user = username
            self.login_btn.config(text=f"User: {username} ({role})")
            self.status_var.set(f"Logged in as {username}")
            log_info(f"User logged in: {username}")
        else:
            messagebox.showerror("Error", "Wrong password")

# ---------------- Dialogs & small helpers ----------------
class ItemEditDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prefill=None):
        self.prefill = prefill
        super().__init__(parent, title=title)

    def body(self, master):
        ttk.Label(master, text="SKU:").grid(row=0,column=0,sticky=tk.W)
        self.sku = ttk.Entry(master); self.sku.grid(row=0,column=1)
        ttk.Label(master, text="Name:").grid(row=1,column=0,sticky=tk.W)
        self.name = ttk.Entry(master); self.name.grid(row=1,column=1)
        ttk.Label(master, text="Category:").grid(row=2,column=0,sticky=tk.W)
        self.category = ttk.Entry(master); self.category.grid(row=2,column=1)
        ttk.Label(master, text="Unit Price:").grid(row=3,column=0,sticky=tk.W)
        self.price = ttk.Entry(master); self.price.grid(row=3,column=1)
        ttk.Label(master, text="Qty:").grid(row=4,column=0,sticky=tk.W)
        self.qty = ttk.Entry(master); self.qty.grid(row=4,column=1)
        ttk.Label(master, text="Reorder level:").grid(row=5,column=0,sticky=tk.W)
        self.reorder = ttk.Entry(master); self.reorder.grid(row=5,column=1)
        if self.prefill:
            self.sku.insert(0, self.prefill.get("sku") or "")
            self.name.insert(0, self.prefill.get("name") or "")
            self.category.insert(0, self.prefill.get("category") or "")
            self.price.insert(0, str(self.prefill.get("price") or "0"))
            self.qty.insert(0, str(self.prefill.get("qty") or "0"))
            self.reorder.insert(0, str(self.prefill.get("reorder") or "0"))
        return self.name

    def validate(self):
        if not self.name.get().strip():
            messagebox.showerror("Validation","Name required"); return False
        try:
            float(self.price.get()); int(self.qty.get()); int(self.reorder.get())
        except Exception:
            messagebox.showerror("Validation","Invalid numeric value"); return False
        return True

    def apply(self):
        self.result = (self.sku.get().strip(), self.name.get().strip(), self.category.get().strip(),
                       float(self.price.get()), int(self.qty.get()), int(self.reorder.get()))

class ReportDialog(simpledialog.Dialog):
    def __init__(self, parent, title, text, csv_rows=None):
        self.text = text
        self.csv_rows = csv_rows
        super().__init__(parent, title=title)

    def body(self, master):
        txt = tk.Text(master, width=80, height=20)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", self.text)
        txt.config(state=tk.DISABLED)
        self.txt = txt
        return txt

    def buttonbox(self):
        box = ttk.Frame(self)
        ttk.Button(box, text="Close", command=self.ok).pack(side=tk.RIGHT, padx=5, pady=5)
        if self.csv_rows:
            ttk.Button(box, text="Export CSV", command=self._export_csv).pack(side=tk.RIGHT, padx=5, pady=5)
        box.pack()

    def _export_csv(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv")
        if not fn:
            return
        try:
            with open(fn, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                for r in self.csv_rows:
                    w.writerow(r)
            messagebox.showinfo("Exported", f"Exported to {fn}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class DateRangeDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="Start date (YYYY-MM-DD):").grid(row=0,column=0)
        self.s = ttk.Entry(master); self.s.grid(row=0,column=1)
        ttk.Label(master, text="End date (YYYY-MM-DD):").grid(row=1,column=0)
        self.e = ttk.Entry(master); self.e.grid(row=1,column=1)
        return self.s
    def validate(self):
        try:
            s = datetime.fromisoformat(self.s.get().strip())
            e = datetime.fromisoformat(self.e.get().strip())
            if s>e:
                messagebox.showerror("Validation","Start must be <= End"); return False
            self.result = (s.date(), e.date())
            return True
        except Exception:
            messagebox.showerror("Validation","Invalid dates"); return False

class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="Username:").grid(row=0,column=0)
        self.u = ttk.Entry(master); self.u.grid(row=0,column=1)
        ttk.Label(master, text="Password:").grid(row=1,column=0)
        self.p = ttk.Entry(master, show="*"); self.p.grid(row=1,column=1)
        return self.u
    def apply(self):
        self.result = (self.u.get().strip(), self.p.get())

class CreateUserDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, require_role=None):
        self.require_role = require_role
        super().__init__(parent, title=title)
    def body(self, master):
        ttk.Label(master, text="Username:").grid(row=0,column=0)
        self.u = ttk.Entry(master); self.u.grid(row=0,column=1)
        ttk.Label(master, text="Password:").grid(row=1,column=0)
        self.p = ttk.Entry(master, show="*"); self.p.grid(row=1,column=1)
        return self.u
    def validate(self):
        if not self.u.get().strip() or not self.p.get():
            messagebox.showerror("Validation","Provide username and password"); return False
        return True
    def apply(self):
        self.result = (self.u.get().strip(), self.p.get())

# ------------- Entry point --------------
def main():
    root = tk.Tk()
    app = InventoryBillingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
