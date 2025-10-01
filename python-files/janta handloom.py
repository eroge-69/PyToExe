import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
import os

# ---------------- Database Setup ----------------
conn = sqlite3.connect('pos.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                price REAL,
                stock INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                discount REAL,
                tax REAL,
                total REAL,
                date TEXT,
                customer TEXT)''')

conn.commit()

# Add default admin if not exists
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users (username,password,role) VALUES ('admin','admin','Admin')")
conn.commit()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Janta Handloom POS")
root.geometry("1000x650")

# ---------- Functions ----------
def login():
    username = username_entry.get()
    password = password_entry.get()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if user:
        messagebox.showinfo("Login", f"Welcome {user[1]} ({user[3]})")
        login_frame.pack_forget()
        dashboard_frame.pack(fill='both', expand=True)
    else:
        messagebox.showerror("Error", "Invalid username or password")

def add_product():
    name = prod_name_entry.get()
    category = prod_cat_entry.get()
    price = float(prod_price_entry.get())
    stock = int(prod_stock_entry.get())
    c.execute("INSERT INTO products (name, category, price, stock) VALUES (?,?,?,?)",
              (name, category, price, stock))
    conn.commit()
    messagebox.showinfo("Success", "Product added successfully")
    prod_name_entry.delete(0,'end')
    prod_cat_entry.delete(0,'end')
    prod_price_entry.delete(0,'end')
    prod_stock_entry.delete(0,'end')
    load_products()

def load_products():
    for row in product_tree.get_children():
        product_tree.delete(row)
    c.execute("SELECT * FROM products")
    for row in c.fetchall():
        product_tree.insert('', 'end', values=row)

def sell_product():
    try:
        selected = product_tree.item(product_tree.selection())['values']
        quantity = int(sell_qty_entry.get())
        discount = float(sell_discount_entry.get())
        tax = float(sell_tax_entry.get())
        if quantity > selected[4]:
            messagebox.showerror("Error", "Not enough stock")
            return
        price = selected[3]
        total_price = (price * quantity) - discount + tax
        customer = sell_cust_entry.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO sales (product_name, quantity, price, discount, tax, total, date, customer) VALUES (?,?,?,?,?,?,?,?)",
                  (selected[1], quantity, price, discount, tax, total_price, date, customer))
        c.execute("UPDATE products SET stock = stock - ? WHERE id=?", (quantity, selected[0]))
        conn.commit()
        messagebox.showinfo("Success", f"Sold {quantity} x {selected[1]} = ₹{total_price}")
        generate_invoice(selected[1], quantity, price, discount, tax, total_price, customer)
        load_products()
        load_sales()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generate_invoice(product, quantity, price, discount, tax, total, customer):
    invoice_name = f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    c_pdf = canvas.Canvas(invoice_name)
    c_pdf.setFont("Helvetica", 14)
    c_pdf.drawString(200, 800, "Janta Handloom Invoice")
    c_pdf.drawString(50, 760, f"Customer: {customer}")
    c_pdf.drawString(50, 740, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c_pdf.drawString(50, 700, f"Product: {product}")
    c_pdf.drawString(50, 680, f"Quantity: {quantity}")
    c_pdf.drawString(50, 660, f"Price per item: ₹{price}")
    c_pdf.drawString(50, 640, f"Discount: ₹{discount}")
    c_pdf.drawString(50, 620, f"Tax: ₹{tax}")
    c_pdf.drawString(50, 600, f"Total: ₹{total}")
    c_pdf.save()
    messagebox.showinfo("Invoice Generated", f"Invoice saved as {invoice_name}")

def load_sales():
    for row in sales_tree.get_children():
        sales_tree.delete(row)
    c.execute("SELECT * FROM sales")
    for row in c.fetchall():
        sales_tree.insert('', 'end', values=row)

def daily_report():
    date = report_date_entry.get()
    c.execute("SELECT SUM(total) FROM sales WHERE date LIKE ?", (f"{date}%",))
    total = c.fetchone()[0]
    messagebox.showinfo("Daily Report", f"Total Sales on {date}: ₹{total if total else 0}")

def monthly_report():
    month = report_month_entry.get()
    c.execute("SELECT SUM(total) FROM sales WHERE date LIKE ?", (f"{month}%",))
    total = c.fetchone()[0]
    messagebox.showinfo("Monthly Report", f"Total Sales in {month}: ₹{total if total else 0}")

# ---------- Login Frame ----------
login_frame = tk.Frame(root)
login_frame.pack(fill='both', expand=True)

tk.Label(login_frame, text="Janta Handloom POS", font=('Arial', 24)).pack(pady=20)
tk.Label(login_frame, text="Username").pack()
username_entry = tk.Entry(login_frame)
username_entry.pack()
tk.Label(login_frame, text="Password").pack()
password_entry = tk.Entry(login_frame, show="*")
password_entry.pack()
tk.Button(login_frame, text="Login", command=login).pack(pady=10)

# ---------- Dashboard Frame ----------
dashboard_frame = tk.Frame(root)

# Tabs
tab_control = ttk.Notebook(dashboard_frame)

# Products Tab
products_tab = ttk.Frame(tab_control)
tab_control.add(products_tab, text='Products')

tk.Label(products_tab, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
prod_name_entry = tk.Entry(products_tab)
prod_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(products_tab, text="Category").grid(row=1, column=0, padx=5, pady=5)
prod_cat_entry = tk.Entry(products_tab)
prod_cat_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(products_tab, text="Price").grid(row=2, column=0, padx=5, pady=5)
prod_price_entry = tk.Entry(products_tab)
prod_price_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(products_tab, text="Stock").grid(row=3, column=0, padx=5, pady=5)
prod_stock_entry = tk.Entry(products_tab)
prod_stock_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Button(products_tab, text="Add Product", command=add_product).grid(row=4, column=0, columnspan=2, pady=10)

# Product List
product_tree = ttk.Treeview(products_tab, columns=('ID','Name','Category','Price','Stock'), show='headings')
for col in ('ID','Name','Category','Price','Stock'):
    product_tree.heading(col, text=col)
product_tree.grid(row=5, column=0, columnspan=2, pady=10)
load_products()

# Sales Tab
sales_tab = ttk.Frame(tab_control)
tab_control.add(sales_tab, text='Sales')

tk.Label(sales_tab, text="Quantity").grid(row=0, column=0, padx=5, pady=5)
sell_qty_entry = tk.Entry(sales_tab)
sell_qty_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(sales_tab, text="Discount").grid(row=1, column=0, padx=5, pady=5)
sell_discount_entry = tk.Entry(sales_tab)
sell_discount_entry.grid(row=1, column=1, padx=5, pady=5)
sell_discount_entry.insert(0, "0")

tk.Label(sales_tab, text="Tax").grid(row=2, column=0, padx=5, pady=5)
sell_tax_entry = tk.Entry(sales_tab)
sell_tax_entry.grid(row=2, column=1, padx=5, pady=5)
sell_tax_entry.insert(0, "0")

tk.Label(sales_tab, text="Customer Name").grid(row=3, column=0, padx=5, pady=5)
sell_cust_entry = tk.Entry(sales_tab)
sell_cust_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Button(sales_tab, text="Sell Product", command=sell_product).grid(row=4, column=0, columnspan=2, pady=10)

# Sales List
sales_tree = ttk.Treeview(sales_tab, columns=('ID','Product','Quantity','Price','Discount','Tax','Total','Date','Customer'), show='headings')
for col in ('ID','Product','Quantity','Price','Discount','Tax','Total','Date','Customer'):
    sales_tree.heading(col, text=col)
sales_tree.grid(row=5, column=0, columnspan=2, pady=10)
load_sales()

# Reports Tab
report_tab = ttk.Frame(tab_control)
tab_control.add(report_tab, text='Reports')

tk.Label(report_tab, text="Daily Report (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
report_date_entry = tk.Entry(report_tab)
report_date_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(report_tab, text="Show Daily Report", command=daily_report).grid(row=0, column=2, padx=5, pady=5)

tk.Label(report_tab, text="Monthly Report (YYYY-MM)").grid(row=1, column=0, padx=5, pady=5)
report_month_entry = tk.Entry(report_tab)
report_month_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(report_tab, text="Show Monthly Report", command=monthly_report).grid(row=1, column=2, padx=5, pady=5)

tab_control.pack(expand=1, fill='both')

root.mainloop()
