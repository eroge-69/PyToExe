
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv

PASSWORD = "akramtechks2025"

# Global storage
products = []
sales = []
repairs = []

# Helpers
def calculate_earnings(period):
    now = datetime.datetime.now()
    total = 0
    for sale in sales:
        date = sale['date']
        if (period == 'day' and date.date() == now.date()) or            (period == 'week' and date.isocalendar()[1] == now.isocalendar()[1]) or            (period == 'month' and date.month == now.month and date.year == now.year):
            total += sale['price']
    return total

def refresh_products():
    product_list.delete(*product_list.get_children())
    for product in products:
        product_list.insert('', 'end', values=(product['name'], product['price'], product['qty']))

def refresh_repairs():
    repair_list.delete(*repair_list.get_children())
    for repair in repairs:
        repair_list.insert('', 'end', values=(repair['desc'], repair['price'], repair['date'].strftime('%Y-%m-%d')))

def add_product():
    name = entry_name.get()
    price = float(entry_price.get())
    qty = int(entry_qty.get())
    products.append({'name': name, 'price': price, 'qty': qty})
    refresh_products()

def remove_selected_product():
    selected = product_list.selection()
    if selected:
        index = product_list.index(selected[0])
        products.pop(index)
        refresh_products()

def sell_product():
    selected = product_list.selection()
    if selected:
        index = product_list.index(selected[0])
        if products[index]['qty'] > 0:
            products[index]['qty'] -= 1
            sales.append({'name': products[index]['name'], 'price': products[index]['price'], 'date': datetime.datetime.now()})
            refresh_products()
        else:
            messagebox.showerror("Error", "Product out of stock")

def add_repair():
    desc = entry_repair_desc.get()
    price = float(entry_repair_price.get())
    repairs.append({'desc': desc, 'price': price, 'date': datetime.datetime.now()})
    sales.append({'name': desc, 'price': price, 'date': datetime.datetime.now()})
    refresh_repairs()

def update_earnings():
    daily.set(f"{calculate_earnings('day')} DA")
    weekly.set(f"{calculate_earnings('week')} DA")
    monthly.set(f"{calculate_earnings('month')} DA")

def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["--- Sales ---"])
        writer.writerow(["Name", "Price", "Date"])
        for s in sales:
            writer.writerow([s['name'], s['price'], s['date'].strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        writer.writerow(["--- Repairs ---"])
        writer.writerow(["Description", "Price", "Date"])
        for r in repairs:
            writer.writerow([r['desc'], r['price'], r['date'].strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        writer.writerow(["--- Products ---"])
        writer.writerow(["Name", "Price", "Quantity"])
        for p in products:
            writer.writerow([p['name'], p['price'], p['qty']])
    messagebox.showinfo("Export Complete", f"Data exported to {file_path}")

# Login screen
def login():
    entered = entry_password.get()
    if entered == PASSWORD:
        login_window.destroy()
        start_main_app()
    else:
        messagebox.showerror("Access Denied", "Wrong password")

def start_main_app():
    global product_list, entry_name, entry_price, entry_qty
    global repair_list, entry_repair_desc, entry_repair_price
    global daily, weekly, monthly

    root = tk.Tk()
    root.title("Stock & Repair Management")
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Product Tab
    frame_products = ttk.Frame(notebook)
    notebook.add(frame_products, text='Products')

    entry_name = ttk.Entry(frame_products)
    entry_name.insert(0, "Product Name")
    entry_price = ttk.Entry(frame_products)
    entry_price.insert(0, "Price")
    entry_qty = ttk.Entry(frame_products)
    entry_qty.insert(0, "Quantity")

    btn_add = ttk.Button(frame_products, text="Add Product", command=add_product)
    btn_remove = ttk.Button(frame_products, text="Remove Selected", command=remove_selected_product)
    btn_sell = ttk.Button(frame_products, text="Sell Selected", command=sell_product)

    entry_name.pack(padx=5, pady=5)
    entry_price.pack(padx=5, pady=5)
    entry_qty.pack(padx=5, pady=5)
    btn_add.pack(padx=5, pady=5)
    btn_remove.pack(padx=5, pady=5)
    btn_sell.pack(padx=5, pady=5)

    product_list = ttk.Treeview(frame_products, columns=('Name', 'Price', 'Qty'), show='headings')
    for col in ('Name', 'Price', 'Qty'):
        product_list.heading(col, text=col)
    product_list.pack(expand=True, fill='both')

    # Repair Tab
    frame_repairs = ttk.Frame(notebook)
    notebook.add(frame_repairs, text='Repairs')

    entry_repair_desc = ttk.Entry(frame_repairs)
    entry_repair_desc.insert(0, "Repair Description")
    entry_repair_price = ttk.Entry(frame_repairs)
    entry_repair_price.insert(0, "Repair Price")
    btn_add_repair = ttk.Button(frame_repairs, text="Add Repair", command=add_repair)

    entry_repair_desc.pack(padx=5, pady=5)
    entry_repair_price.pack(padx=5, pady=5)
    btn_add_repair.pack(padx=5, pady=5)

    repair_list = ttk.Treeview(frame_repairs, columns=('Description', 'Price', 'Date'), show='headings')
    for col in ('Description', 'Price', 'Date'):
        repair_list.heading(col, text=col)
    repair_list.pack(expand=True, fill='both')

    # Earnings & Export
    frame_earnings = ttk.Frame(root)
    frame_earnings.pack(pady=10)

    daily = tk.StringVar(value='0 DA')
    weekly = tk.StringVar(value='0 DA')
    monthly = tk.StringVar(value='0 DA')

    update_btn = ttk.Button(frame_earnings, text="Update Earnings", command=update_earnings)
    export_btn = ttk.Button(frame_earnings, text="Export Data to CSV", command=export_to_csv)

    update_btn.grid(row=0, column=0, padx=10)
    export_btn.grid(row=0, column=1, padx=10)

    ttk.Label(frame_earnings, text="Today:").grid(row=0, column=2)
    ttk.Label(frame_earnings, textvariable=daily).grid(row=0, column=3, padx=10)
    ttk.Label(frame_earnings, text="Week:").grid(row=0, column=4)
    ttk.Label(frame_earnings, textvariable=weekly).grid(row=0, column=5, padx=10)
    ttk.Label(frame_earnings, text="Month:").grid(row=0, column=6)
    ttk.Label(frame_earnings, textvariable=monthly).grid(row=0, column=7, padx=10)

    root.mainloop()

# Initial password prompt
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x150")

ttk.Label(login_window, text="Enter Password:").pack(pady=10)
entry_password = ttk.Entry(login_window, show="*")
entry_password.pack(pady=5)
btn_login = ttk.Button(login_window, text="Login", command=login)
btn_login.pack(pady=10)

login_window.mainloop()
