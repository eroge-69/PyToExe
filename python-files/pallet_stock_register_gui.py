
import tkinter as tk
from tkinter import ttk, messagebox
import random

# Sample pallet data
pallet_data = [
    {"PalletID": "P001", "Product": "Widget A", "Quantity": 100, "MinStock": 50, "ReorderLevel": 150},
    {"PalletID": "P002", "Product": "Widget B", "Quantity": 40, "MinStock": 60, "ReorderLevel": 120},
    {"PalletID": "P003", "Product": "Widget C", "Quantity": 75, "MinStock": 70, "ReorderLevel": 100},
    {"PalletID": "P004", "Product": "Widget D", "Quantity": 20, "MinStock": 30, "ReorderLevel": 80},
]

def calculate_order_qty(quantity, min_stock, reorder_level):
    if quantity < min_stock:
        return reorder_level - quantity
    return "OK"

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    for item in pallet_data:
        order_qty = calculate_order_qty(item["Quantity"], item["MinStock"], item["ReorderLevel"])
        values = (item["PalletID"], item["Product"], item["Quantity"], item["MinStock"], item["ReorderLevel"], order_qty)
        tag = "low_stock" if isinstance(order_qty, int) else ""
        tree.insert("", "end", values=values, tags=(tag,))

def simulate_stock_update():
    for item in pallet_data:
        change = random.randint(-20, 20)
        item["Quantity"] = max(0, item["Quantity"] + change)
    refresh_table()
    messagebox.showinfo("Stock Update", "Stock quantities have been updated.")

# GUI setup
root = tk.Tk()
root.title("Pallet Stock Register and Order Management")

columns = ("PalletID", "Product", "Quantity", "MinStock", "ReorderLevel", "OrderQty")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.tag_configure("low_stock", background="lightcoral")
tree.pack(padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

tk.Button(button_frame, text="Refresh Data", command=refresh_table).pack(side="left", padx=5)
tk.Button(button_frame, text="Simulate Stock Update", command=simulate_stock_update).pack(side="left", padx=5)

refresh_table()
root.mainloop()
