# Full FGV Construction Supplies System (Modern + Persistent + Full Tabs)

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import time

INVENTORY_FILE = "inventory.json"
SALES_FILE = "sales.txt"

# === Load & Save ===
def load_inventory():
    if not os.path.exists(INVENTORY_FILE): return {}
    with open(INVENTORY_FILE, "r") as f: return json.load(f)

def save_inventory():
    with open(INVENTORY_FILE, "w") as f: json.dump(inventory, f, indent=4)

def log_sale(item, qty, total):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SALES_FILE, "a") as f:
        f.write(f"[{now}] {item} x{qty} - PHP {total}\n")

# === GUI Setup ===
root = tk.Tk()
root.title("FGV Construction Supplies")
root.geometry("1100x720")
root.configure(bg="#f4f4f4")

style = ttk.Style()
style.theme_use("default")
style.configure("TNotebook.Tab", padding=(12, 8), font=("Segoe UI", 10))
style.configure("TButton", padding=6, font=("Segoe UI", 10))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

clock_label = tk.Label(root, font=("Segoe UI", 10), bg="#f4f4f4", anchor="e")
clock_label.pack(anchor="ne", padx=15, pady=5)

def update_clock():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=now)
    root.after(1000, update_clock)

update_clock()

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

tabs = {}
for tab_name in ["Inventory", "Restock", "Add Item", "Calculator", "Sales Summary", "Cart"]:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)
    tabs[tab_name] = frame

# === Inventory Tab ===
search_var = tk.StringVar()
tk.Label(tabs["Inventory"], text="Search by Keyword").pack(pady=3)
search_entry = tk.Entry(tabs["Inventory"], textvariable=search_var, width=40)
search_entry.pack(pady=3)

columns = ("Item", "Quantity", "Price")
tree_inventory = ttk.Treeview(tabs["Inventory"], columns=columns, show="headings")
for col in columns:
    tree_inventory.heading(col, text=col)
tree_inventory.pack(fill='both', expand=True, padx=10, pady=10)
tree_inventory.tag_configure("low", background="#ffe5e5")

add_cart_frame = ttk.Frame(tabs["Inventory"])
add_cart_frame.pack(pady=5)
tk.Label(add_cart_frame, text="Qty:").grid(row=0, column=0, padx=4)
inventory_cart_qty = tk.Entry(add_cart_frame, width=10)
inventory_cart_qty.grid(row=0, column=1, padx=4)

def update_inventory():
    tree_inventory.delete(*tree_inventory.get_children())
    keyword = search_var.get().lower()
    for item, data in inventory.items():
        if keyword in item.lower():
            qty = data["quantity"]
            price = data["price"]
            tag = "low" if qty == 0 else "normal"
            tree_inventory.insert("", "end", values=(item, qty, f"PHP {price}"), tags=(tag,))
            if qty == 0:
                messagebox.showwarning("Out of Stock", f"{item} is OUT OF STOCK!")

search_entry.bind("<KeyRelease>", lambda e: update_inventory())

def add_inventory_selection_to_cart():
    selected = tree_inventory.focus()
    if not selected:
        messagebox.showerror("Error", "Select an item first.")
        return
    item = tree_inventory.item(selected)['values'][0]
    qty_text = inventory_cart_qty.get()
    try:
        qty = int(qty_text)
        if qty <= 0 or qty > inventory[item]['quantity']:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid quantity.")
        return
    cart.append({"item": item, "qty": qty, "price": inventory[item]['price']})
    cart_list.insert(tk.END, f"{item} x{qty} @ PHP {inventory[item]['price']} = PHP {qty * inventory[item]['price']}")
    update_total()
    inventory_cart_qty.delete(0, tk.END)
    notebook.select(tabs["Cart"])

def delete_inventory_item():
    selected = tree_inventory.focus()
    if not selected:
        messagebox.showerror("Error", "Select an item to delete.")
        return
    item = tree_inventory.item(selected)['values'][0]
    if messagebox.askyesno("Confirm", f"Delete '{item}' from inventory?"):
        inventory.pop(item, None)
        save_inventory()
        update_inventory()
        restock_item_menu['values'] = list(inventory.keys())
        cart_item_menu['values'] = list(inventory.keys())
        messagebox.showinfo("Deleted", f"{item} has been removed.")

tk.Button(add_cart_frame, text="Add to Cart", command=add_inventory_selection_to_cart).grid(row=0, column=2, padx=4)
tk.Button(tabs["Inventory"], text="Delete Selected Item", command=delete_inventory_item).pack(pady=5)

# === Restock Tab ===
restock_item_var = tk.StringVar()
tk.Label(tabs["Restock"], text="Select Item").pack(pady=2)
restock_item_menu = ttk.Combobox(tabs["Restock"], textvariable=restock_item_var)
restock_item_menu.pack()
restock_qty_entry = tk.Entry(tabs["Restock"])
tk.Label(tabs["Restock"], text="Qty to Add").pack(pady=2)
restock_qty_entry.pack()

def restock_item():
    item = restock_item_var.get()
    try:
        qty = int(restock_qty_entry.get())
        if item not in inventory or qty <= 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid input")
        return
    inventory[item]["quantity"] += qty
    with open("restock_log.txt", "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] Restocked {qty} of {item}\n")
    save_inventory()
    update_inventory()
    restock_qty_entry.delete(0, tk.END)
    messagebox.showinfo("Success", f"Restocked {qty} of {item}")

tk.Button(tabs["Restock"], text="Restock", command=restock_item).pack(pady=10)

# === Add Item Tab ===
tk.Label(tabs["Add Item"], text="Item Name").pack()
add_name_entry = tk.Entry(tabs["Add Item"])
add_name_entry.pack()

tk.Label(tabs["Add Item"], text="Price (PHP)").pack()
add_price_entry = tk.Entry(tabs["Add Item"])
add_price_entry.pack()

tk.Label(tabs["Add Item"], text="Initial Quantity").pack()
add_qty_entry = tk.Entry(tabs["Add Item"])
add_qty_entry.pack()

def add_new_item():
    name = add_name_entry.get()
    try:
        price = int(add_price_entry.get())
        qty = int(add_qty_entry.get())
        if name in inventory or price <= 0 or qty < 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid input")
        return
    inventory[name] = {"price": price, "quantity": qty}
    save_inventory()
    update_inventory()
    restock_item_menu['values'] = list(inventory.keys())
    cart_item_menu['values'] = list(inventory.keys())
    add_name_entry.delete(0, tk.END)
    add_price_entry.delete(0, tk.END)
    add_qty_entry.delete(0, tk.END)
    messagebox.showinfo("Item Added", f"{name} added")

tk.Button(tabs["Add Item"], text="Add Item", command=add_new_item).pack(pady=10)

# === Calculator ===
tk.Label(tabs["Calculator"], text="Unit Price (PHP)").pack()
calc_price_entry = tk.Entry(tabs["Calculator"])
calc_price_entry.pack()

tk.Label(tabs["Calculator"], text="Quantity").pack()
calc_qty_entry = tk.Entry(tabs["Calculator"])
calc_qty_entry.pack()

calc_result_var = tk.StringVar()
tk.Label(tabs["Calculator"], textvariable=calc_result_var, font=("Segoe UI", 11)).pack(pady=4)

def calculate_price():
    try:
        total = float(calc_price_entry.get()) * int(calc_qty_entry.get())
        calc_result_var.set(f"Total: PHP {total:.2f}")
    except:
        calc_result_var.set("Invalid input")

tk.Button(tabs["Calculator"], text="Calculate", command=calculate_price).pack(pady=5)

# === Sales Summary ===
summary_list = tk.Listbox(tabs["Sales Summary"], width=100)
summary_list.pack(pady=5)

lbl_tx = tk.Label(tabs["Sales Summary"], text="Transactions: 0")
lbl_tx.pack()
lbl_volume = tk.Label(tabs["Sales Summary"], text="Volume Sold: 0 units")
lbl_volume.pack()
lbl_income = tk.Label(tabs["Sales Summary"], text="Total Income: PHP 0.00")
lbl_income.pack()

def update_summary():
    total_tx = total_volume = total_income = 0
    summary_list.delete(0, tk.END)
    if os.path.exists(SALES_FILE):
        with open(SALES_FILE, "r") as f:
            for line in f:
                summary_list.insert(tk.END, line.strip())
                parts = line.strip().split(" - PHP ")
                if len(parts) == 2:
                    total_tx += 1
                    try:
                        total_income += float(parts[1])
                        qty = int(parts[0].split("x")[-1].strip())
                        total_volume += qty
                    except:
                        pass
    lbl_tx.config(text=f"Transactions: {total_tx}")
    lbl_volume.config(text=f"Volume Sold: {total_volume} units")
    lbl_income.config(text=f"Total Income: PHP {total_income:,.2f}")

def reset_sales():
    if messagebox.askyesno("Confirm", "Clear all sales data?"):
        open(SALES_FILE, "w").close()
        update_summary()

tk.Button(tabs["Sales Summary"], text="Refresh", command=update_summary).pack(pady=2)
tk.Button(tabs["Sales Summary"], text="Reset Sales", command=reset_sales).pack(pady=2)

# === Cart Tab ===
cart = []
cart_item_var = tk.StringVar()
tk.Label(tabs["Cart"], text="Select Item").pack()
cart_item_menu = ttk.Combobox(tabs["Cart"], textvariable=cart_item_var)
cart_item_menu.pack()

cart_qty_entry = tk.Entry(tabs["Cart"])
tk.Label(tabs["Cart"], text="Quantity").pack()
cart_qty_entry.pack()

cart_list = tk.Listbox(tabs["Cart"], height=8)
cart_list.pack(padx=10, pady=5)

total_var = tk.StringVar(value="Total: PHP 0.00")
tk.Label(tabs["Cart"], textvariable=total_var, font=("Segoe UI", 12)).pack(pady=2)

payment_entry = tk.Entry(tabs["Cart"])
tk.Label(tabs["Cart"], text="Customer Payment (PHP)").pack()
payment_entry.pack()

def update_total():
    total = sum(item['qty'] * item['price'] for item in cart)
    total_var.set(f"Total: PHP {total:,.2f}")

def add_to_cart():
    item = cart_item_var.get()
    try:
        qty = int(cart_qty_entry.get())
        if item not in inventory or qty <= 0 or qty > inventory[item]['quantity']:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid input")
        return
    cart.append({"item": item, "qty": qty, "price": inventory[item]['price']})
    cart_list.insert(tk.END, f"{item} x{qty} @ PHP {inventory[item]['price']} = PHP {qty * inventory[item]['price']}")
    update_total()
    cart_qty_entry.delete(0, tk.END)

def delete_cart_item():
    selected = cart_list.curselection()
    if not selected:
        messagebox.showerror("Error", "Select item in cart to delete")
        return
    index = selected[0]
    del cart[index]
    cart_list.delete(index)
    update_total()

def checkout():
    if not cart:
        messagebox.showerror("Error", "Cart is empty.")
        return
    try:
        payment = float(payment_entry.get())
        total = sum(item['qty'] * item['price'] for item in cart)
        if payment < total:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid payment or not enough.")
        return
    for item in cart:
        inventory[item['item']]['quantity'] -= item['qty']
        log_sale(item['item'], item['qty'], item['qty'] * item['price'])
    change = payment - total
    messagebox.showinfo("Success", f"Change: PHP {change:.2f}")
    cart.clear()
    cart_list.delete(0, tk.END)
    total_var.set("Total: PHP 0.00")
    payment_entry.delete(0, tk.END)
    save_inventory()
    update_inventory()
    update_summary()

tk.Button(tabs["Cart"], text="Add to Cart", command=add_to_cart).pack(pady=5)
tk.Button(tabs["Cart"], text="Delete Selected Item", command=delete_cart_item).pack(pady=2)
tk.Button(tabs["Cart"], text="Checkout", command=checkout).pack(pady=5)

# === Load Initial Data ===
inventory = load_inventory()
update_inventory()
restock_item_menu['values'] = list(inventory.keys())
cart_item_menu['values'] = list(inventory.keys())
update_summary()

root.mainloop()