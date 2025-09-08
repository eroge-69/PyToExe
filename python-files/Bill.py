import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime
import os

# ---------- Save Sale ----------
def save_sale():
    customer = entry_customer.get()
    item = entry_item.get()
    qty = entry_qty.get()
    price = entry_price.get()

    if not (customer and item and qty and price):
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        qty = int(qty)
        price = float(price)
    except ValueError:
        messagebox.showerror("Error", "Quantity must be integer and Price must be number")
        return

    total = qty * price
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    with open("sales_data.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date_time, customer, item, qty, price, total])

    # Create bill file
    bill_name = f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(bill_name, "w") as bill:
        bill.write("===== SALES BILL =====\n")
        bill.write(f"Date: {date_time}\n")
        bill.write(f"Customer: {customer}\n")
        bill.write(f"Item: {item}\n")
        bill.write(f"Quantity: {qty}\n")
        bill.write(f"Price per unit: {price}\n")
        bill.write(f"Total: {total}\n")
        bill.write("======================\n")

    messagebox.showinfo("Success", f"Sale saved and bill generated: {bill_name}")
    entry_customer.delete(0, tk.END)
    entry_item.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)

# ---------- Search Sales ----------
def search_sales():
    query = entry_search.get().strip().lower()
    if not query:
        messagebox.showerror("Error", "Enter a search term")
        return

    if not os.path.exists("sales_data.csv"):
        messagebox.showerror("Error", "No sales data found")
        return

    for row in tree.get_children():
        tree.delete(row)

    with open("sales_data.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if any(query in str(cell).lower() for cell in row):
                tree.insert("", tk.END, values=row)

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Sales Entry Form with Search")

# Entry Form
tk.Label(root, text="Customer Name").grid(row=0, column=0)
entry_customer = tk.Entry(root)
entry_customer.grid(row=0, column=1)

tk.Label(root, text="Item Name").grid(row=1, column=0)
entry_item = tk.Entry(root)
entry_item.grid(row=1, column=1)

tk.Label(root, text="Quantity").grid(row=2, column=0)
entry_qty = tk.Entry(root)
entry_qty.grid(row=2, column=1)

tk.Label(root, text="Price per Unit").grid(row=3, column=0)
entry_price = tk.Entry(root)
entry_price.grid(row=3, column=1)

tk.Button(root, text="Save Sale", command=save_sale).grid(row=4, column=0, columnspan=2, pady=5)

# Search Section
tk.Label(root, text="Search Sales").grid(row=5, column=0)
entry_search = tk.Entry(root)
entry_search.grid(row=5, column=1)
tk.Button(root, text="Search", command=search_sales).grid(row=5, column=2)

# Results Table
columns = ("Date", "Customer", "Item", "Quantity", "Price", "Total")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=6, column=0, columnspan=3, pady=10)

root.mainloop()
