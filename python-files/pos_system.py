
\"\"\"
Simple PC POS System (single-file)
Features:
- SQLite DB with categories, subcategories, products, sales, sale_items
- Manage (Add/Edit/Delete) Categories and Subcategories
- Manage Products (add/edit/delete) linked to subcategories
- Sales screen: select category -> subcategory -> product, add to cart, checkout
- Generates a simple text receipt saved under receipts/
Run: python pos_system.py
Requirements: Python 3 (no external packages required)
\"\"\"
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime

DB_PATH = "pos_db.sqlite"
RECEIPTS_DIR = "receipts"

# Ensure receipts directory exists
os.makedirs(RECEIPTS_DIR, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS subcategories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        UNIQUE(category_id, name),
        FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subcategory_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        price REAL NOT NULL DEFAULT 0,
        stock INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        total REAL NOT NULL
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    conn.commit()
    conn.close()

# ---------- Data access helpers ----------
def fetch_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_subcategories(category_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subcategories WHERE category_id=? ORDER BY name", (category_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_products_by_subcategory(subcat_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE subcategory_id=? ORDER BY name", (subcat_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_category(name):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO categories(name) VALUES(?)", (name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not add category: {e}")
        return False

def edit_category(cat_id, new_name):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE categories SET name=? WHERE id=?", (new_name, cat_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not edit category: {e}")
        return False

def delete_category(cat_id):
    if not messagebox.askyesno("Confirm", "Delete category and all its subcategories/products?"):
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete category: {e}")
        return False

def add_subcategory(category_id, name):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO subcategories(category_id, name) VALUES(?,?)", (category_id, name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not add subcategory: {e}")
        return False

def edit_subcategory(sub_id, new_name):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE subcategories SET name=? WHERE id=?", (new_name, sub_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not edit subcategory: {e}")
        return False

def delete_subcategory(sub_id):
    if not messagebox.askyesno("Confirm", "Delete subcategory and all its products?"):
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM subcategories WHERE id=?", (sub_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete subcategory: {e}")
        return False

def add_product(subcategory_id, name, price, stock):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO products(subcategory_id, name, price, stock) VALUES(?,?,?,?)", (subcategory_id, name, price, stock))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not add product: {e}")
        return False

def edit_product(prod_id, name, price, stock, subcategory_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE products SET name=?, price=?, stock=?, subcategory_id=? WHERE id=?", (name, price, stock, subcategory_id, prod_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not edit product: {e}")
        return False

def delete_product(prod_id):
    if not messagebox.askyesno("Confirm", "Delete this product?"):
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=?", (prod_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not delete product: {e}")
        return False

# ---------- GUI ----------
class POSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple POS - PC Version")
        self.geometry("1000x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()

    def create_widgets(self):
        # Left: Management (categories/subcategories/products)
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        notebook = ttk.Notebook(left)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- Categories Tab ---
        cat_frame = ttk.Frame(notebook)
        notebook.add(cat_frame, text="Categories")

        self.cat_list = tk.Listbox(cat_frame, height=10)
        self.cat_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.cat_list.bind("<<ListboxSelect>>", self.on_category_select)

        cat_btn_frame = ttk.Frame(cat_frame)
        cat_btn_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(cat_btn_frame, text="Add Category", command=self.add_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text="Edit Selected", command=self.edit_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text="Delete Selected", command=self.delete_category).pack(fill=tk.X, pady=2)

        # --- Subcategories Tab ---
        sub_frame = ttk.Frame(notebook)
        notebook.add(sub_frame, text="Subcategories")

        self.sub_list = tk.Listbox(sub_frame, height=10)
        self.sub_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.sub_list.bind("<<ListboxSelect>>", self.on_subcategory_select)

        sub_btn_frame = ttk.Frame(sub_frame)
        sub_btn_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(sub_btn_frame, text="Add Subcategory", command=self.add_subcategory).pack(fill=tk.X, pady=2)
        ttk.Button(sub_btn_frame, text="Edit Selected", command=self.edit_subcategory).pack(fill=tk.X, pady=2)
        ttk.Button(sub_btn_frame, text="Delete Selected", command=self.delete_subcategory).pack(fill=tk.X, pady=2)

        # --- Products Tab ---
        prod_frame = ttk.Frame(notebook)
        notebook.add(prod_frame, text="Products")

        self.prod_tree = ttk.Treeview(prod_frame, columns=("id","name","price","stock","subcategory"), show="headings")
        self.prod_tree.heading("id", text="ID")
        self.prod_tree.heading("name", text="Name")
        self.prod_tree.heading("price", text="Price")
        self.prod_tree.heading("stock", text="Stock")
        self.prod_tree.heading("subcategory", text="Subcategory")
        self.prod_tree.column("id", width=40)
        self.prod_tree.pack(fill=tk.BOTH, expand=True)
        self.prod_tree.bind("<Double-1>", self.on_product_double)

        prod_btn_frame = ttk.Frame(prod_frame)
        prod_btn_frame.pack(fill=tk.X)
        ttk.Button(prod_btn_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=2, pady=4)
        ttk.Button(prod_btn_frame, text="Edit Selected", command=self.edit_product).pack(side=tk.LEFT, padx=2, pady=4)
        ttk.Button(prod_btn_frame, text="Delete Selected", command=self.delete_product).pack(side=tk.LEFT, padx=2, pady=4)
        ttk.Button(prod_btn_frame, text="Refresh", command=self.refresh_products).pack(side=tk.LEFT, padx=2, pady=4)

        # Right: Sales area
        right = ttk.Frame(self)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        sales_top = ttk.Frame(right)
        sales_top.pack(fill=tk.X)

        ttk.Label(sales_top, text="Category:").pack(side=tk.LEFT, padx=2)
        self.sales_cat_cb = ttk.Combobox(sales_top, state="readonly")
        self.sales_cat_cb.pack(side=tk.LEFT, padx=2)
        self.sales_cat_cb.bind("<<ComboboxSelected>>", self.on_sales_category_change)

        ttk.Label(sales_top, text="Subcategory:").pack(side=tk.LEFT, padx=2)
        self.sales_sub_cb = ttk.Combobox(sales_top, state="readonly")
        self.sales_sub_cb.pack(side=tk.LEFT, padx=2)
        self.sales_sub_cb.bind("<<ComboboxSelected>>", self.on_sales_subcategory_change)

        ttk.Label(sales_top, text="Product:").pack(side=tk.LEFT, padx=2)
        self.sales_prod_cb = ttk.Combobox(sales_top, state="readonly", width=30)
        self.sales_prod_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(sales_top, text="Add to Cart", command=self.add_to_cart).pack(side=tk.LEFT, padx=4)

        # Cart
        cart_frame = ttk.Frame(right)
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("name","qty","price","total"), show="headings")
        self.cart_tree.heading("name", text="Name")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("total", text="Total")
        self.cart_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        cart_controls = ttk.Frame(cart_frame)
        cart_controls.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(cart_controls, text="Remove Selected", command=self.remove_selected_cart).pack(fill=tk.X, pady=2)
        ttk.Button(cart_controls, text="Clear Cart", command=self.clear_cart).pack(fill=tk.X, pady=2)

        checkout_frame = ttk.Frame(right)
        checkout_frame.pack(fill=tk.X)
        self.total_var = tk.StringVar(value="0.00")
        ttk.Label(checkout_frame, text="Total:").pack(side=tk.LEFT, padx=8)
        ttk.Label(checkout_frame, textvariable=self.total_var, font=("Helvetica", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(checkout_frame, text="Checkout", command=self.checkout).pack(side=tk.RIGHT, padx=8)

        # Load initial data
        self.selected_category_id = None
        self.selected_subcategory_id = None
        self.cart = []  # list of dicts: {product_id, name, qty, price}
        self.refresh_all()

    # ---- Management handlers ----
    def refresh_all(self):
        self.refresh_categories()
        self.refresh_products()
        self.refresh_sales_comboboxes()

    def refresh_categories(self):
        self.cat_list.delete(0, tk.END)
        cats = fetch_categories()
        for c in cats:
            self.cat_list.insert(tk.END, f"{c['id']}: {c['name']}")
        # update sales category combobox
        self.sales_cat_cb['values'] = [f"{c['id']}:{c['name']}" for c in cats]
        if cats:
            self.sales_cat_cb.current(0)
            self.on_sales_category_change()

    def on_category_select(self, event):
        sel = self.cat_list.curselection()
        if not sel:
            return
        text = self.cat_list.get(sel[0])
        cid = int(text.split(":",1)[0])
        self.selected_category_id = cid
        self.refresh_subcategories(cid)

    def add_category(self):
        name = simpledialog.askstring("Add Category", "Category name:")
        if name:
            if add_category(name.strip()):
                self.refresh_categories()

    def edit_category(self):
        sel = self.cat_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a category first")
            return
        text = self.cat_list.get(sel[0])
        cid = int(text.split(":",1)[0])
        old = text.split(":",1)[1].strip()
        name = simpledialog.askstring("Edit Category", "New name:", initialvalue=old)
        if name:
            if edit_category(cid, name.strip()):
                self.refresh_categories()

    def delete_category(self):
        sel = self.cat_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a category first")
            return
        text = self.cat_list.get(sel[0])
        cid = int(text.split(":",1)[0])
        if delete_category(cid):
            self.refresh_all()

    def refresh_subcategories(self, category_id):
        self.sub_list.delete(0, tk.END)
        subs = fetch_subcategories(category_id)
        for s in subs:
            self.sub_list.insert(tk.END, f"{s['id']}: {s['name']}")

    def on_subcategory_select(self, event):
        sel = self.sub_list.curselection()
        if not sel:
            return
        text = self.sub_list.get(sel[0])
        sid = int(text.split(":",1)[0])
        self.selected_subcategory_id = sid
        # optionally refresh products listing
        self.refresh_products()

    def add_subcategory(self):
        if not self.selected_category_id:
            messagebox.showinfo("Info", "Select a category first (left panel)")
            return
        name = simpledialog.askstring("Add Subcategory", "Subcategory name:")
        if name:
            if add_subcategory(self.selected_category_id, name.strip()):
                self.refresh_subcategories(self.selected_category_id)

    def edit_subcategory(self):
        sel = self.sub_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a subcategory first")
            return
        text = self.sub_list.get(sel[0])
        sid = int(text.split(":",1)[0])
        old = text.split(":",1)[1].strip()
        name = simpledialog.askstring("Edit Subcategory", "New name:", initialvalue=old)
        if name:
            if edit_subcategory(sid, name.strip()):
                self.refresh_subcategories(self.selected_category_id)

    def delete_subcategory(self):
        sel = self.sub_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a subcategory first")
            return
        text = self.sub_list.get(sel[0])
        sid = int(text.split(":",1)[0])
        if delete_subcategory(sid):
            self.refresh_subcategories(self.selected_category_id)
            self.refresh_products()

    def refresh_products(self):
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('''
        SELECT p.id, p.name, p.price, p.stock, s.name as subname
        FROM products p JOIN subcategories s ON p.subcategory_id=s.id
        ORDER BY s.name, p.name
        ''')
        rows = cur.fetchall()
        for r in rows:
            self.prod_tree.insert("", tk.END, values=(r['id'], r['name'], f"{r['price']:.2f}", r['stock'], r['subname']))
        conn.close()

    def on_product_double(self, event):
        self.edit_product()

    def add_product(self):
        # choose subcategory
        cats = fetch_categories()
        if not cats:
            messagebox.showinfo("Info", "Create a category first")
            return
        # select category dialog
        cat_map = {f"{c['id']}:{c['name']}": c['id'] for c in cats}
        sel = simpledialog.askstring("Select Category", "Enter category (format id:name)\n" + "\n".join(cat_map.keys()))
        if not sel or sel not in cat_map:
            messagebox.showinfo("Info", "Cancelled or invalid selection")
            return
        cid = cat_map[sel]
        subs = fetch_subcategories(cid)
        if not subs:
            messagebox.showinfo("Info", "Create a subcategory under the chosen category first")
            return
        sub_map = {f"{s['id']}:{s['name']}": s['id'] for s in subs}
        sel2 = simpledialog.askstring("Select Subcategory", "Enter subcategory (format id:name)\n" + "\n".join(sub_map.keys()))
        if not sel2 or sel2 not in sub_map:
            messagebox.showinfo("Info", "Cancelled or invalid selection")
            return
        sid = sub_map[sel2]
        name = simpledialog.askstring("Product Name", "Name:")
        if not name:
            return
        try:
            price = float(simpledialog.askstring("Price", "Price:"))
            stock = int(simpledialog.askstring("Stock", "Stock:"))
        except:
            messagebox.showerror("Error", "Invalid price or stock")
            return
        if add_product(sid, name.strip(), price, stock):
            self.refresh_products()

    def edit_product(self):
        sel = self.prod_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a product")
            return
        item = self.prod_tree.item(sel[0])['values']
        prod_id = item[0]
        # fetch current details
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id=?", (prod_id,))
        p = cur.fetchone()
        conn.close()
        if not p:
            return
        name = simpledialog.askstring("Product Name", "Name:", initialvalue=p['name'])
        if not name:
            return
        try:
            price = float(simpledialog.askstring("Price", "Price:", initialvalue=str(p['price'])))
            stock = int(simpledialog.askstring("Stock", "Stock:", initialvalue=str(p['stock'])))
        except:
            messagebox.showerror("Error", "Invalid price or stock")
            return
        # choose subcategory maybe
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT s.id, s.name, c.name as cname FROM subcategories s JOIN categories c ON s.category_id=c.id ORDER BY c.name, s.name")
        rows = cur.fetchall()
        conn.close()
        sel_map = {}
        for r in rows:
            key = f"{r['id']}:{r['cname']} -> {r['name']}"
            sel_map[key] = r['id']
        selkey = simpledialog.askstring("Select Subcategory", "Choose (exact):\n" + "\n".join(sel_map.keys()), initialvalue=next((k for k,v in sel_map.items() if v==p['subcategory_id']), None))
        if not selkey or selkey not in sel_map:
            messagebox.showinfo("Info", "Cancelled or invalid selection")
            return
        new_sub = sel_map[selkey]
        if edit_product(prod_id, name.strip(), price, stock, new_sub):
            self.refresh_products()

    def delete_product(self):
        sel = self.prod_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a product")
            return
        item = self.prod_tree.item(sel[0])['values']
        prod_id = item[0]
        if delete_product(prod_id):
            self.refresh_products()

    # ---- Sales handlers ----
    def refresh_sales_comboboxes(self):
        cats = fetch_categories()
        cat_vals = [f"{c['id']}:{c['name']}" for c in cats]
        self.sales_cat_cb['values'] = cat_vals
        if cat_vals:
            self.sales_cat_cb.current(0)
            self.on_sales_category_change()

    def on_sales_category_change(self, event=None):
        val = self.sales_cat_cb.get()
        if not val:
            return
        cid = int(val.split(":",1)[0])
        subs = fetch_subcategories(cid)
        sub_vals = [f"{s['id']}:{s['name']}" for s in subs]
        self.sales_sub_cb['values'] = sub_vals
        if sub_vals:
            self.sales_sub_cb.current(0)
            self.on_sales_subcategory_change()
        else:
            self.sales_sub_cb.set('')
            self.sales_prod_cb['values'] = []
            self.sales_prod_cb.set('')

    def on_sales_subcategory_change(self, event=None):
        val = self.sales_sub_cb.get()
        if not val:
            return
        sid = int(val.split(":",1)[0])
        products = fetch_products_by_subcategory(sid)
        prod_vals = [f"{p['id']}:{p['name']} ({p['stock']}) - {p['price']:.2f}" for p in products]
        self.sales_prod_cb['values'] = prod_vals
        if prod_vals:
            self.sales_prod_cb.current(0)

    def add_to_cart(self):
        prod_text = self.sales_prod_cb.get()
        if not prod_text:
            messagebox.showinfo("Info", "Select a product")
            return
        pid = int(prod_text.split(":",1)[0])
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id=?", (pid,))
        p = cur.fetchone()
        conn.close()
        if not p:
            messagebox.showerror("Error", "Product not found")
            return
        qty = simpledialog.askinteger("Quantity", "Enter quantity:", initialvalue=1, minvalue=1)
        if not qty:
            return
        if qty > p['stock']:
            if not messagebox.askyesno("Low stock", f"Only {p['stock']} in stock. Add anyway?"):
                return
        # check if already in cart
        for it in self.cart:
            if it['product_id'] == pid:
                it['qty'] += qty
                break
        else:
            self.cart.append({'product_id': pid, 'name': p['name'], 'qty': qty, 'price': p['price']})
        self.refresh_cart()

    def refresh_cart(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        total = 0.0
        for it in self.cart:
            t = it['qty'] * it['price']
            total += t
            self.cart_tree.insert("", tk.END, values=(it['name'], it['qty'], f"{it['price']:.2f}", f"{t:.2f}"))
        self.total_var.set(f"{total:.2f}")

    def remove_selected_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        del self.cart[idx]
        self.refresh_cart()

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()

    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Info", "Cart is empty")
            return
        total = sum(it['qty']*it['price'] for it in self.cart)
        confirm = messagebox.askyesno("Checkout", f"Total: {total:.2f}\nProceed to checkout?")
        if not confirm:
            return
        # save sale
        conn = get_conn()
        cur = conn.cursor()
        now = datetime.now().isoformat()
        cur.execute("INSERT INTO sales(created_at, total) VALUES(?,?)", (now, total))
        sale_id = cur.lastrowid
        for it in self.cart:
            cur.execute("INSERT INTO sale_items(sale_id, product_id, qty, price) VALUES(?,?,?,?)", (sale_id, it['product_id'], it['qty'], it['price']))
            # subtract stock
            cur.execute("UPDATE products SET stock = stock - ? WHERE id=?", (it['qty'], it['product_id']))
        conn.commit()
        conn.close()
        # generate receipt text file
        receipt_path = os.path.join(RECEIPTS_DIR, f"receipt_{sale_id}.txt")
        with open(receipt_path, "w", encoding="utf-8") as f:
            f.write("Simple POS Receipt\\n")
            f.write(f"Sale ID: {sale_id}\\n")
            f.write(f"Date: {now}\\n")
            f.write("-"*30 + "\\n")
            for it in self.cart:
                f.write(f"{it['name']} x{it['qty']} @ {it['price']:.2f} = {it['qty']*it['price']:.2f}\\n")
            f.write("-"*30 + "\\n")
            f.write(f"Total: {total:.2f}\\n")
            f.write("Thank you!\\n")
        messagebox.showinfo("Success", f"Sale recorded. Receipt saved to:\\n{receipt_path}")
        self.clear_cart()
        self.refresh_products()
        self.refresh_sales_comboboxes()

    def on_close(self):
        if messagebox.askokcancel("Quit", "Exit POS?"):
            self.destroy()

# ---------- Run ----------
if __name__ == "__main__":
    init_db()
    app = POSApp()
    app.mainloop()
