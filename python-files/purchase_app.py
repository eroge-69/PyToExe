import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd

# ------------------ Database Setup ------------------
def init_db():
    conn = sqlite3.connect("purchases.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_cost REAL,
            supplier TEXT,
            bill_no TEXT,
            purchase_date TEXT,
            department TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call it once at the start
init_db()

# ------------------ Functions ------------------
def add_record():
    if not (item_name.get() and category.get() and quantity.get() and unit_price.get()):
        messagebox.showerror("Error", "Please fill all required fields")
        return
    
    try:
        q = int(quantity.get())
        u = float(unit_price.get())
        total = q * u
    except:
        messagebox.showerror("Error", "Quantity & Unit Price must be numbers")
        return

    conn = sqlite3.connect("purchases.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO purchases (item_name, category, quantity, unit_price, total_cost,
                               supplier, bill_no, purchase_date, department)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (item_name.get(), category.get(), q, u, total,
          supplier.get(), bill_no.get(), purchase_date.get(), department.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Record added successfully")
    clear_fields()
    load_records()

def load_records():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("purchases.db")
    c = conn.cursor()
    c.execute("SELECT * FROM purchases")
    rows = c.fetchall()
    for r in rows:
        tree.insert("", tk.END, values=r)
    conn.close()

def delete_record():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Please select a record to delete")
        return
    values = tree.item(selected, "values")
    record_id = values[0]
    conn = sqlite3.connect("purchases.db")
    c = conn.cursor()
    c.execute("DELETE FROM purchases WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Deleted", "Record deleted successfully")
    load_records()

def export_excel():
    conn = sqlite3.connect("purchases.db")
    df = pd.read_sql_query("SELECT * FROM purchases", conn)
    conn.close()
    file = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                        filetypes=[("Excel Files", "*.xlsx")])
    if file:
        df.to_excel(file, index=False)
        messagebox.showinfo("Exported", f"Data exported to {file}")

def clear_fields():
    item_name.set("")
    category.set("")
    quantity.set("")
    unit_price.set("")
    supplier.set("")
    bill_no.set("")
    purchase_date.set("")
    department.set("")

# ------------------ UI Setup ------------------
root = tk.Tk()
root.title("School/College Purchase Manager")
root.geometry("950x600")

# Variables
item_name = tk.StringVar()
category = tk.StringVar()
quantity = tk.StringVar()
unit_price = tk.StringVar()
supplier = tk.StringVar()
bill_no = tk.StringVar()
purchase_date = tk.StringVar()
department = tk.StringVar()

# Form Frame
form = tk.Frame(root, pady=10)
form.pack(fill="x")

fields = [
    ("Item Name", item_name), ("Category", category),
    ("Quantity", quantity), ("Unit Price", unit_price),
    ("Supplier", supplier), ("Bill No", bill_no),
    ("Purchase Date", purchase_date), ("Department", department)
]

for i, (label, var) in enumerate(fields):
    tk.Label(form, text=label).grid(row=i//4, column=(i%4)*2, padx=5, pady=5, sticky="e")
    tk.Entry(form, textvariable=var).grid(row=i//4, column=(i%4)*2+1, padx=5, pady=5)

# Buttons
btn_frame = tk.Frame(root, pady=10)
btn_frame.pack(fill="x")

tk.Button(btn_frame, text="Add Record", command=add_record, bg="lightgreen").pack(side="left", padx=5)
tk.Button(btn_frame, text="Delete Record", command=delete_record, bg="tomato").pack(side="left", padx=5)
tk.Button(btn_frame, text="Export to Excel", command=export_excel, bg="lightblue").pack(side="left", padx=5)
tk.Button(btn_frame, text="Refresh", command=load_records).pack(side="left", padx=5)

# Data Table
tree = ttk.Treeview(root, columns=("ID", "Item", "Category", "Qty", "Unit Price", "Total", "Supplier", "Bill No", "Date", "Department"), show="headings")
tree.pack(fill="both", expand=True)

for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100)

load_records()

root.mainloop()
