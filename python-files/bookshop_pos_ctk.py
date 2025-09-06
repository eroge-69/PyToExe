#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookshop POS — Modern UI with CustomTkinter (single-file)
Author: ChatGPT (GPT-5 Thinking)
License: MIT
Requires: Python 3.8+, customtkinter
Install: pip install customtkinter
Run: python bookshop_pos_ctk.py

Features (kept from original):
- Product catalog (ISBN, Title, Author, Price, Stock) (SQLite)
- Add/Edit/Delete products
- Quick ISBN/barcode entry (scan into field + Enter)
- Cart with qty edit, remove line
- Checkout (Cash/Card/Other) with cash tendered & change
- Auto stock update after sale
- Sales history + simple daily report + CSV export
- Receipts as text files saved to receipts/
- Modern UI using customtkinter: sidebar, pages, toggles, icons-like buttons
"""

import os
import sqlite3
import csv
from datetime import datetime, date
from dataclasses import dataclass
import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog

APP_NAME = "Bookshop POS (Modern)"
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "bookshop.db")
RECEIPT_DIR = os.path.join(BASE_DIR, "receipts")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECEIPT_DIR, exist_ok=True)

# ---------- Database helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        author TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        total REAL NOT NULL,
        payment_method TEXT NOT NULL,
        cash_tendered REAL,
        change_due REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        unit_price REAL NOT NULL
    )
    """)
    cur.execute("SELECT COUNT(*) as c FROM products")
    if cur.fetchone()["c"] == 0:
        seed = [
            ("9789556653450", "English Grade 6 Workbook", "MSK Publishers", 950.0, 20),
            ("9789552101234", "Mathematics Grade 7", "Lake House", 1200.0, 15),
            ("9789552119871", "Sinhala Story Collection", "Sarasavi", 850.0, 30),
            ("9780199535569", "Pride and Prejudice", "Jane Austen", 1800.0, 10),
            ("9780132350884", "Clean Code", "Robert C. Martin", 5500.0, 5),
        ]
        cur.executemany("INSERT INTO products (isbn,title,author,price,stock) VALUES (?,?,?,?,?)", seed)
    conn.commit()
    conn.close()

# ---------- Data classes ----------
@dataclass
class CartItem:
    product_id: int
    isbn: str
    title: str
    unit_price: float
    qty: int

# ---------- App ----------
class BookshopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1200x740")
        ctk.set_appearance_mode("dark")  # "dark" or "light"
        ctk.set_default_color_theme("blue")

        self.cart = []
        self._build_ui()
        self.refresh_products()
        self.refresh_report()

        # keyboard bindings
        self.bind("<F2>", lambda e: self.open_checkout())
        self.bind("<F9>", lambda e: self.new_sale())
        self.bind("<Control-f>", lambda e: self.focus_scan())

    def _build_ui(self):
        # sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo = ctk.CTkLabel(self.sidebar, text="📚 Bookshop POS", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo.pack(pady=(18,10))

        self.btn_inventory = ctk.CTkButton(self.sidebar, text="Inventory", command=self.show_inventory, anchor="w")
        self.btn_sales = ctk.CTkButton(self.sidebar, text="Sales", command=self.show_sales, anchor="w")
        self.btn_reports = ctk.CTkButton(self.sidebar, text="Reports", command=self.show_reports, anchor="w")
        self.btn_settings = ctk.CTkButton(self.sidebar, text="Settings", command=self.show_settings, anchor="w")

        for btn in (self.btn_inventory, self.btn_sales, self.btn_reports, self.btn_settings):
            btn.pack(fill="x", padx=12, pady=6)

        self.theme_toggle = ctk.CTkSwitch(self.sidebar, text="Light Mode", command=self.toggle_theme)
        self.theme_toggle.pack(padx=12, pady=(10,0))

        # main area
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # Pages
        self.page_inventory = ctk.CTkFrame(self.container)
        self.page_sales = ctk.CTkFrame(self.container)
        self.page_reports = ctk.CTkFrame(self.container)
        self.page_settings = ctk.CTkFrame(self.container)

        for p in (self.page_inventory, self.page_sales, self.page_reports, self.page_settings):
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_inventory_page()
        self._build_sales_page()
        self._build_reports_page()
        self._build_settings_page()

        self.show_sales()  # default

    # ---------- pages ----------
    def show_inventory(self):
        self.page_inventory.lift()

    def show_sales(self):
        self.page_sales.lift()
        self.focus_scan()

    def show_reports(self):
        self.page_reports.lift()
        self.refresh_report()

    def show_settings(self):
        self.page_settings.lift()

    def toggle_theme(self, *_):
        mode = "light" if self.theme_toggle.get() else "dark"
        ctk.set_appearance_mode(mode)

    # ---------- Inventory Page ----------
    def _build_inventory_page(self):
        top = ctk.CTkFrame(self.page_inventory)
        top.pack(side="top", fill="x", pady=8, padx=8)

        self.inv_search_var = ctk.StringVar()
        inv_search = ctk.CTkEntry(top, placeholder_text="Search ISBN, title, or author...", textvariable=self.inv_search_var)
        inv_search.pack(side="left", fill="x", expand=True, padx=(6,8))
        inv_search.bind("<KeyRelease>", lambda e: self.refresh_products())

        ctk.CTkButton(top, text="Add", command=self.add_product_dialog).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Edit", command=self.edit_selected_product).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Delete", command=self.delete_selected_product).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Export CSV", command=self.export_products_csv).pack(side="left", padx=6)

        # product list
        self.inv_listbox = ctk.CTkTextbox(self.page_inventory, width=800, height=520, corner_radius=8)
        self.inv_listbox.pack(fill="both", expand=True, padx=12, pady=12)
        self.inv_listbox.configure(state="disabled")

    # ---------- Sales Page ----------
    def _build_sales_page(self):
        top = ctk.CTkFrame(self.page_sales)
        top.pack(side="top", fill="x", pady=6, padx=8)

        self.scan_var = ctk.StringVar()
        self.qty_var = ctk.StringVar(value="1")
        scan_entry = ctk.CTkEntry(top, placeholder_text="Scan or type ISBN then press Enter", textvariable=self.scan_var, width=320)
        scan_entry.pack(side="left", padx=(8,6))
        scan_entry.bind("<Return>", lambda e: self.add_isbn_to_cart())

        qty_entry = ctk.CTkEntry(top, width=80, textvariable=self.qty_var)
        qty_entry.pack(side="left", padx=(0,6))

        ctk.CTkButton(top, text="Add", command=self.add_isbn_to_cart).pack(side="left", padx=6)
        ctk.CTkButton(top, text="New Sale (F9)", fg_color="#1f6aa5", command=self.new_sale).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Checkout (F2)", fg_color="#2f8f4a", command=self.open_checkout).pack(side="left", padx=6)

        # middle: products on left, cart on right
        mid = ctk.CTkFrame(self.page_sales)
        mid.pack(fill="both", expand=True, padx=12, pady=12)

        left = ctk.CTkFrame(mid)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        ctk.CTkLabel(left, text="Products (search to filter)", anchor="w").pack(fill="x", padx=6, pady=(6,0))
        self.prod_list = ctk.CTkScrollableFrame(left, width=520, height=520, corner_radius=8)
        self.prod_list.pack(fill="both", expand=True, padx=6, pady=6)

        right = ctk.CTkFrame(mid, width=380)
        right.pack(side="left", fill="y")

        ctk.CTkLabel(right, text="Cart", anchor="w").pack(fill="x", padx=6, pady=(6,0))
        self.cart_box = ctk.CTkTextbox(right, width=360, height=360, corner_radius=8)
        self.cart_box.pack(padx=6, pady=6)
        self.cart_box.configure(state="disabled")

        btns = ctk.CTkFrame(right)
        btns.pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(btns, text="Remove Line", command=self.remove_cart_line).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Set Qty", command=self.set_cart_qty).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=6)

        totals = ctk.CTkFrame(right)
        totals.pack(fill="x", padx=6, pady=(8,0))
        self.items_var = ctk.StringVar(value="0")
        self.subtotal_var = ctk.StringVar(value="0.00")
        ctk.CTkLabel(totals, text="Items:").pack(side="left")
        ctk.CTkLabel(totals, textvariable=self.items_var, width=6).pack(side="left", padx=(6,12))
        ctk.CTkLabel(totals, text="Subtotal (LKR):").pack(side="left")
        ctk.CTkLabel(totals, textvariable=self.subtotal_var, width=12).pack(side="left", padx=6)

    # ---------- Reports Page ----------
    def _build_reports_page(self):
        top = ctk.CTkFrame(self.page_reports)
        top.pack(side="top", fill="x", pady=8, padx=8)
        ctk.CTkButton(top, text="Refresh Report", command=self.refresh_report).pack(side="left", padx=8)
        ctk.CTkButton(top, text="Export Today's Sales CSV", command=self.export_todays_sales_csv).pack(side="left", padx=8)

        self.report_box = ctk.CTkTextbox(self.page_reports, width=900, height=600, corner_radius=8)
        self.report_box.pack(fill="both", expand=True, padx=12, pady=12)
        self.report_box.configure(state="disabled")

    # ---------- Settings Page ----------
    def _build_settings_page(self):
        f = ctk.CTkFrame(self.page_settings, padx=12, pady=12)
        f.pack(fill="both", expand=True)
        ctk.CTkLabel(f, text="Settings & Tools", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0,8))
        ctk.CTkButton(f, text="Export Products CSV", command=self.export_products_csv).pack(anchor="w", pady=6)
        ctk.CTkButton(f, text="Open Data Folder", command=lambda: os.startfile(DATA_DIR)).pack(anchor="w", pady=6)
        ctk.CTkButton(f, text="Open Receipts Folder", command=lambda: os.startfile(RECEIPT_DIR)).pack(anchor="w", pady=6)

    # ---------- Product operations ----------
    def refresh_products(self, *_):
        q = getattr(self, "inv_search_var", ctk.StringVar()).get().strip() if hasattr(self, "inv_search_var") else ""
        q2 = getattr(self, "prod_list", None)
        conn = get_conn()
        cur = conn.cursor()
        if q:
            like = f"%{q}%"
            cur.execute("SELECT * FROM products WHERE isbn LIKE ? OR title LIKE ? OR author LIKE ? ORDER BY title ASC", (like, like, like))
        else:
            cur.execute("SELECT * FROM products ORDER BY title ASC")
        rows = cur.fetchall()
        conn.close()

        # populate product scroll area
        self.prod_list.destroy()
        parent = self.page_sales.winfo_children()[1].winfo_children()[0]  # mid -> left
        self.prod_list = ctk.CTkScrollableFrame(parent, width=520, height=520, corner_radius=8)
        self.prod_list.pack(fill="both", expand=True, padx=6, pady=6)
        for r in rows:
            b = ctk.CTkButton(self.prod_list, text=f"{r['title']} — LKR {r['price']:.2f}\n{r['isbn']}", anchor="w", width=520, command=lambda row=r: self.add_product_to_cart(row, 1))
            b.pack(fill="x", pady=4, padx=6)

        # inventory text
        self.inv_listbox.configure(state="normal")
        self.inv_listbox.delete("0.0", "end")
        for r in rows:
            self.inv_listbox.insert("end", f"{r['isbn']}\t{r['title']}\t{r['author'] or ''}\tLKR {r['price']:.2f}\tStock:{r['stock']}\n")
        self.inv_listbox.configure(state="disabled")

    def add_product_to_cart(self, row, qty=1):
        if row["stock"] < qty:
            messagebox.showwarning("Stock", f"Only {row['stock']} in stock.")
            return
        for it in self.cart:
            if it.product_id == row["id"]:
                it.qty += qty
                break
        else:
            self.cart.append(CartItem(row["id"], row["isbn"], row["title"], float(row["price"]), qty))
        self.refresh_cart()

    def add_isbn_to_cart(self):
        isbn = self.scan_var.get().strip()
        try:
            qty = int(self.qty_var.get().strip() or "1")
        except ValueError:
            messagebox.showerror("Qty", "Invalid quantity.")
            return
        if not isbn:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE isbn=?", (isbn,))
        r = cur.fetchone()
        conn.close()
        if not r:
            messagebox.showerror("Not found", f"ISBN {isbn} not found.")
            return
        if r["stock"] < qty:
            messagebox.showwarning("Stock", f"Only {r['stock']} in stock.")
            return
        self.add_product_to_cart(r, qty)
        self.scan_var.set("")
        self.qty_var.set("1")
        self.focus_scan()

    def focus_scan(self):
        # focus the scan entry in sales page; find it by traversing widgets
        for child in self.page_sales.winfo_children():
            for w in child.winfo_children():
                if isinstance(w, ctk.CTkEntry) and w.placeholder_text and "ISBN" in (w.placeholder_text or ""):
                    w.focus_set()
                    return
        # fallback: focus first entry
        self.focus_set()

    def refresh_cart(self):
        self.cart_box.configure(state="normal")
        self.cart_box.delete("0.0", "end")
        subtotal = 0.0
        items = 0
        for it in self.cart:
            line = f"{it.title[:36]:36s} x{it.qty:>2}  {it.unit_price:>8.2f}  {it.unit_price * it.qty:>8.2f}\n"
            self.cart_box.insert("end", line)
            subtotal += it.unit_price * it.qty
            items += it.qty
        self.cart_box.configure(state="disabled")
        self.subtotal_var.set(f"{subtotal:.2f}")
        self.items_var.set(str(items))

    def remove_cart_line(self):
        # ask which ISBN to remove (simple approach)
        if not self.cart:
            return
        titles = [f"{i+1}. {c.title} x{c.qty}" for i,c in enumerate(self.cart)]
        choice = simpledialog.askinteger("Remove Line", "Enter line number to remove:\n" + "\n".join(titles), minvalue=1, maxvalue=len(self.cart))
        if choice:
            idx = choice-1
            del self.cart[idx]
            self.refresh_cart()

    def set_cart_qty(self):
        if not self.cart:
            return
        titles = [f"{i+1}. {c.title} x{c.qty}" for i,c in enumerate(self.cart)]
        choice = simpledialog.askinteger("Set Qty", "Enter line number to change:\n" + "\n".join(titles), minvalue=1, maxvalue=len(self.cart))
        if not choice:
            return
        idx = choice-1
        new_qty = simpledialog.askinteger("Qty", f"New qty for {self.cart[idx].title}:", initialvalue=self.cart[idx].qty, minvalue=1)
        if new_qty is None:
            return
        # check stock
        conn = get_conn(); cur = conn.cursor(); cur.execute("SELECT stock FROM products WHERE id=?", (self.cart[idx].product_id,)); s = cur.fetchone()["stock"]; conn.close()
        if new_qty > s:
            messagebox.showwarning("Stock", f"Only {s} in stock.")
            return
        self.cart[idx].qty = new_qty
        self.refresh_cart()

    def clear_cart(self):
        if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            self.cart = []
            self.refresh_cart()

    def new_sale(self):
        if self.cart and not messagebox.askyesno("New Sale", "Clear current cart and start a new sale?"):
            return
        self.cart = []
        self.refresh_cart()
        self.status("New sale started.")
        self.show_sales()

    def status(self, msg):
        # temporary message in title
        self.title(f"{APP_NAME} — {msg}")

    # ---------- Checkout ----------
    def open_checkout(self):
        if not self.cart:
            messagebox.showinfo("Checkout", "Cart is empty.")
            return
        subtotal = float(self.subtotal_var.get())
        dlg = CheckoutDialog(self, subtotal)
        self.wait_window(dlg)
        if not getattr(dlg, "result", None):
            return
        payment_method, cash_tendered = dlg.result
        change = 0.0
        if payment_method == "Cash":
            change = max(0.0, (cash_tendered or 0.0) - subtotal)
        # commit sale
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("BEGIN")
            # check stock
            for it in self.cart:
                cur.execute("SELECT stock FROM products WHERE id=?", (it.product_id,))
                s = cur.fetchone()["stock"]
                if s < it.qty:
                    raise RuntimeError(f"Insufficient stock for {it.title}")
            cur.execute("INSERT INTO sales (ts,total,payment_method,cash_tendered,change_due) VALUES (?,?,?,?,?)",
                        (datetime.now().isoformat(timespec="seconds"), subtotal, payment_method, cash_tendered, change))
            sale_id = cur.lastrowid
            for it in self.cart:
                cur.execute("INSERT INTO sale_items (sale_id,product_id,qty,unit_price) VALUES (?,?,?,?)",
                            (sale_id, it.product_id, it.qty, it.unit_price))
                cur.execute("UPDATE products SET stock = stock - ? WHERE id=?", (it.qty, it.product_id))
            conn.commit()
            self.save_receipt(sale_id)
            self.cart = []
            self.refresh_cart()
            self.refresh_products()
            self.refresh_report()
            self.status(f"Sale #{sale_id} completed")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Checkout Error", str(e))
        finally:
            conn.close()

    def save_receipt(self, sale_id:int):
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT * FROM sales WHERE id=?", (sale_id,)); sale = cur.fetchone()
        cur.execute("SELECT p.isbn, p.title, si.qty, si.unit_price FROM sale_items si JOIN products p ON p.id=si.product_id WHERE si.sale_id=?", (sale_id,))
        items = cur.fetchall(); conn.close()
        ts = datetime.fromisoformat(sale["ts"])
        fname = f"{ts.strftime('%Y%m%d-%H%M%S')}-sale{sale_id}.txt"
        path = os.path.join(RECEIPT_DIR, fname)
        lines = []
        lines.append("MSK Online Bookshop")
        lines.append("Kadawatha, Sri Lanka")
        lines.append("-"*40)
        lines.append(f"Sale ID: {sale_id}    {ts.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("-"*40)
        for r in items:
            total = r["qty"] * r["unit_price"]
            lines.append(f"{r['title'][:28]:28s} x{r['qty']:>2}  {r['unit_price']:>8.2f}  {total:>8.2f}")
        lines.append("-"*40)
        lines.append(f"TOTAL: LKR {sale['total']:.2f}")
        lines.append(f"Pay: {sale['payment_method']}")
        if sale["payment_method"] == "Cash":
            lines.append(f"Cash: LKR {sale['cash_tendered'] or 0:.2f}")
            lines.append(f"Change: LKR {sale['change_due'] or 0:.2f}")
        lines.append("Thank you!")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # ---------- Reports ----------
    def refresh_report(self):
        conn = get_conn(); cur = conn.cursor()
        today = date.today().isoformat()
        cur.execute("SELECT id, ts, total, payment_method FROM sales WHERE substr(ts,1,10)=? ORDER BY ts DESC", (today,))
        sales = cur.fetchall()
        total_sales = sum(r["total"] for r in sales)
        count_sales = len(sales)
        cur.execute("""SELECT p.title, SUM(si.qty) as qty FROM sale_items si JOIN products p ON p.id=si.product_id JOIN sales s ON s.id=si.sale_id WHERE substr(s.ts,1,10)=? GROUP BY p.title ORDER BY qty DESC LIMIT 5""", (today,))
        top = cur.fetchall(); conn.close()
        txt = []
        txt.append(f"Date: {today}")
        txt.append(f"Sales Count: {count_sales}")
        txt.append(f"Total Revenue (LKR): {total_sales:.2f}")
        if count_sales:
            txt.append(f"Avg Sale: {total_sales/count_sales:.2f}")
        txt.append("Top Items:")
        for r in top:
            txt.append(f" - {r['title']} (x{r['qty']})")
        self.report_box.configure(state="normal"); self.report_box.delete("0.0","end"); self.report_box.insert("0.0","\n".join(txt)); self.report_box.configure(state="disabled")

    def export_products_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="products.csv")
        if not path: return
        conn = get_conn(); cur = conn.cursor(); cur.execute("SELECT isbn,title,author,price,stock FROM products ORDER BY title ASC"); rows = cur.fetchall(); conn.close()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["ISBN","Title","Author","Price","Stock"]); 
            for r in rows: w.writerow([r["isbn"], r["title"], r["author"] or "", f"{r['price']:.2f}", r["stock"]])
        messagebox.showinfo("Export", f"Exported {len(rows)} products.")

    def export_todays_sales_csv(self):
        today = date.today().isoformat()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile=f"sales_{today}.csv")
        if not path: return
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT s.id, s.ts, s.total, s.payment_method FROM sales s WHERE substr(s.ts,1,10)=? ORDER BY s.ts", (today,))
        sales = cur.fetchall()
        data = []
        for s in sales:
            cur.execute("SELECT p.isbn, p.title, si.qty, si.unit_price FROM sale_items si JOIN products p ON p.id=si.product_id WHERE si.sale_id=?", (s["id"],))
            items = cur.fetchall()
            for it in items:
                data.append([s["id"], s["ts"], s["total"], s["payment_method"], it["isbn"], it["title"], it["qty"], it["unit_price"]])
        conn.close()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["SaleID","TS","Total","Payment","ISBN","Title","Qty","UnitPrice"]); w.writerows(data)
        messagebox.showinfo("Export", f"Exported {len(data)} rows.")

    # ---------- Inventory dialogs ----------
    def add_product_dialog(self):
        dlg = ProductDialog(self, "Add Product")
        self.wait_window(dlg)
        if getattr(dlg, "result", None):
            isbn, title, author, price, stock = dlg.result
            try:
                conn = get_conn(); cur = conn.cursor(); cur.execute("INSERT INTO products (isbn,title,author,price,stock) VALUES (?,?,?,?,?)", (isbn,title,author,float(price),int(stock))); conn.commit(); conn.close()
                messagebox.showinfo("Added", "Product added."); self.refresh_products()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_selected_product(self):
        # ask for ISBN to edit
        isbn = simpledialog.askstring("Edit", "Enter ISBN of product to edit:")
        if not isbn: return
        conn = get_conn(); cur = conn.cursor(); cur.execute("SELECT * FROM products WHERE isbn=?", (isbn,)); r = cur.fetchone(); conn.close()
        if not r: messagebox.showinfo("Not found", "Product not found."); return
        dlg = ProductDialog(self, "Edit Product", initial=(r["isbn"], r["title"], r["author"], r["price"], r["stock"]))
        self.wait_window(dlg)
        if getattr(dlg, "result", None):
            isbn2, title2, author2, price2, stock2 = dlg.result
            try:
                conn = get_conn(); cur = conn.cursor(); cur.execute("UPDATE products SET isbn=?, title=?, author=?, price=?, stock=? WHERE id=?", (isbn2, title2, author2, float(price2), int(stock2), r["id"])); conn.commit(); conn.close()
                messagebox.showinfo("Updated", "Product updated."); self.refresh_products()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_selected_product(self):
        isbn = simpledialog.askstring("Delete", "Enter ISBN to delete:")
        if not isbn: return
        if not messagebox.askyesno("Confirm", f"Delete product {isbn}?"): return
        conn = get_conn(); cur = conn.cursor(); cur.execute("DELETE FROM products WHERE isbn=?", (isbn,)); conn.commit(); conn.close(); messagebox.showinfo("Deleted", "Product deleted."); self.refresh_products()

# ---------- Dialogs ----------
class ProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, initial=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("520x300")
        self.result = None
        self.transient(parent)
        self.grab_set()

        frm = ctk.CTkFrame(self, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        self.v_isbn = ctk.StringVar(value=initial[0] if initial else "")
        self.v_title = ctk.StringVar(value=initial[1] if initial else "")
        self.v_author = ctk.StringVar(value=initial[2] if initial else "")
        self.v_price = ctk.StringVar(value=str(initial[3]) if initial else "0.00")
        self.v_stock = ctk.StringVar(value=str(initial[4]) if initial else "0")

        ctk.CTkLabel(frm, text="ISBN *").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ctk.CTkEntry(frm, textvariable=self.v_isbn).grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ctk.CTkLabel(frm, text="Title *").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        ctk.CTkEntry(frm, textvariable=self.v_title, width=340).grid(row=1, column=1, sticky="w", padx=6, pady=6)
        ctk.CTkLabel(frm, text="Author").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        ctk.CTkEntry(frm, textvariable=self.v_author).grid(row=2, column=1, sticky="w", padx=6, pady=6)
        ctk.CTkLabel(frm, text="Price *").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        ctk.CTkEntry(frm, textvariable=self.v_price, width=120).grid(row=3, column=1, sticky="w", padx=6, pady=6)
        ctk.CTkLabel(frm, text="Stock *").grid(row=4, column=0, sticky="e", padx=6, pady=6)
        ctk.CTkEntry(frm, textvariable=self.v_stock, width=120).grid(row=4, column=1, sticky="w", padx=6, pady=6)

        btns = ctk.CTkFrame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=12)
        ctk.CTkButton(btns, text="Save", command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Cancel", command=self.destroy).pack(side="left", padx=6)

    def on_save(self):
        try:
            isbn = self.v_isbn.get().strip()
            title = self.v_title.get().strip()
            author = self.v_author.get().strip()
            price = float(self.v_price.get().strip())
            stock = int(self.v_stock.get().strip())
            if not isbn or not title:
                raise ValueError("ISBN and Title required.")
            if price < 0 or stock < 0:
                raise ValueError("Negative values not allowed.")
            self.result = (isbn, title, author, price, stock)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class CheckoutDialog(ctk.CTkToplevel):
    def __init__(self, parent, total):
        super().__init__(parent)
        self.title("Checkout")
        self.geometry("420x220")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.total = total

        frm = ctk.CTkFrame(self, padx=12, pady=12)
        frm.pack(fill="both", expand=True)
        ctk.CTkLabel(frm, text=f"Total: LKR {total:.2f}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0,8))

        self.pay_var = ctk.StringVar(value="Cash")
        ctk.CTkComboBox(frm, values=["Cash","Card","Other"], variable=self.pay_var).pack(fill="x", pady=6)
        self.cash_var = ctk.StringVar(value=f"{total:.2f}")
        ctk.CTkLabel(frm, text="Cash Tendered:").pack(anchor="w", pady=(6,0))
        e = ctk.CTkEntry(frm, textvariable=self.cash_var)
        e.pack(fill="x", pady=6)
        self.change_lbl = ctk.CTkLabel(frm, text="Change: LKR 0.00")
        self.change_lbl.pack(pady=6)

        e.bind("<KeyRelease>", self.compute_change)
        btns = ctk.CTkFrame(frm)
        btns.pack(pady=6)
        ctk.CTkButton(btns, text="Confirm", fg_color="#2f8f4a", command=self.on_ok).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Cancel", command=self.destroy).pack(side="left", padx=6)
        self.compute_change()

    def compute_change(self, *_):
        pm = self.pay_var.get()
        try:
            cash = float(self.cash_var.get() or "0")
        except ValueError:
            cash = 0.0
        change = 0.0
        if pm == "Cash":
            change = max(0.0, cash - self.total)
        self.change_lbl.configure(text=f"Change: LKR {change:.2f}")

    def on_ok(self):
        pm = self.pay_var.get()
        cash = None
        if pm == "Cash":
            try:
                cash = float(self.cash_var.get())
            except ValueError:
                messagebox.showerror("Cash", "Invalid cash amount."); return
            if cash + 1e-6 < self.total:
                if not messagebox.askyesno("Confirm", "Cash is less than total. Continue?"):
                    return
        self.result = (pm, cash)
        self.destroy()

# ---------- Main run ----------
if __name__ == "__main__":
    init_db()
    app = BookshopApp()
    app.mainloop()
