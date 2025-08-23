import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# ------------------ File paths ------------------
INVENTORY_FILE = "inventory.csv"
IN_HISTORY_FILE = "inward_history.csv"
OUT_HISTORY_FILE = "outward_history.csv"
LOW_QTY_FILE = "low_quantity.csv"
INVENTORY_HISTORY_FILE = "inventory_history.csv"

# ------------------ Columns ------------------
columns_inv = ["ID", "Name", "Quantity", "Vendor", "PartCode"]
columns_low = ["ID", "Name", "Quantity", "DateTime"]
columns_in = ["ID", "Name", "QuantityIn", "Vendor", "PartCode", "DateTime"]
columns_out = ["ID", "Name", "QuantityOut", "Customer", "DateTime"]
columns_inventory_history = ["ID", "Name", "ChangeType", "QuantityChange",
                             "ResultingQuantity", "Vendor/Customer", "PartCode", "DateTime"]

LOW_QTY_THRESHOLD = 5

# ------------------ Helper Functions ------------------
def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_csv(file_path, columns):
    data = []
    if not os.path.exists(file_path):
        save_csv(file_path, [], columns)
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if any(row.values()):
                    item = {col: row.get(col, "") for col in columns}
                    data.append(item)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load {file_path}: {e}")
    return data

def save_csv(file_path, data, columns):
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save {file_path}: {e}")

def check_low_quantity():
    low_items = []
    for item in inventory:
        try:
            qty = int(item.get("Quantity", 0))
        except:
            qty = 0
        if qty <= LOW_QTY_THRESHOLD:
            low_items.append({
                "ID": item.get("ID", ""),
                "Name": item.get("Name", ""),
                "Quantity": qty,
                "DateTime": get_current_datetime()
            })
    if low_items:
        save_csv(LOW_QTY_FILE, low_items, columns_low)
    return low_items

# ------------------ Load Data ------------------
inventory = load_csv(INVENTORY_FILE, columns_inv)
inward_history = load_csv(IN_HISTORY_FILE, columns_in)
outward_history = load_csv(OUT_HISTORY_FILE, columns_out)
inventory_history = load_csv(INVENTORY_HISTORY_FILE, columns_inventory_history)

# ------------------ GUI ------------------
root = tk.Tk()
root.title("Inventory Management")
root.geometry("1500x900")

# --- Scrollable Frame ---
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ------------------ Treeview Styling ------------------
def style_treeview(tree, columns):
    tree["columns"] = columns
    tree["show"] = "headings"
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    return tree

def populate_tree(tree, data, columns, latest_on_top=False):
    tree.delete(*tree.get_children())
    if latest_on_top:
        data = data[::-1]
    for row in data:
        values = [row.get(col, "") for col in columns]
        tree.insert("", "end", values=values)

# ------------------ Update Functions ------------------
def update_inventory_table():
    populate_tree(tree_inventory, inventory, columns_inv)
    populate_tree(tree_low, check_low_quantity(), columns_low)

def update_history_tables():
    populate_tree(tree_in, inward_history, columns_in, latest_on_top=True)
    populate_tree(tree_out, outward_history, columns_out, latest_on_top=True)
    populate_tree(tree_hist, inventory_history, columns_inventory_history, latest_on_top=True)

# ------------------ Functional Buttons ------------------
def add_item_dialog():
    top = tk.Toplevel(root)
    top.title("Add Item")
    labels = ["ID","Name","Quantity","Vendor","PartCode"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(top, text=label).grid(row=i, column=0)
        entries[label] = tk.Entry(top)
        entries[label].grid(row=i, column=1)

    def save_new_item():
        new_item = {label: entries[label].get() for label in labels}
        if not new_item["ID"] or not new_item["Quantity"]:
            messagebox.showerror("Error","ID and Quantity required")
            return
        found = False
        for item in inventory:
            if item["ID"] == new_item["ID"]:
                item["Quantity"] = str(int(item["Quantity"])+int(new_item["Quantity"]))
                found = True
                break
        if not found:
            inventory.append(new_item)
        save_csv(INVENTORY_FILE, inventory, columns_inv)

        # Add inward history
        inward_history.append({
            "ID": new_item["ID"],
            "Name": new_item["Name"],
            "QuantityIn": new_item["Quantity"],
            "Vendor": new_item["Vendor"],
            "PartCode": new_item["PartCode"],
            "DateTime": get_current_datetime()
        })
        save_csv(IN_HISTORY_FILE, inward_history, columns_in)

        # Inventory history
        resulting_qty = next(item["Quantity"] for item in inventory if item["ID"]==new_item["ID"])
        inventory_history.append({
            "ID": new_item["ID"],
            "Name": new_item["Name"],
            "ChangeType": "IN",
            "QuantityChange": new_item["Quantity"],
            "ResultingQuantity": resulting_qty,
            "Vendor/Customer": new_item["Vendor"],
            "PartCode": new_item["PartCode"],
            "DateTime": get_current_datetime()
        })
        save_csv(INVENTORY_HISTORY_FILE, inventory_history, columns_inventory_history)
        update_inventory_table()
        update_history_tables()
        top.destroy()

    tk.Button(top, text="Save", command=save_new_item).grid(row=len(labels), column=0, columnspan=2, pady=5)

def item_out_dialog():
    top = tk.Toplevel(root)
    top.title("Item Out")
    labels = ["ID","Name","Quantity","Customer"]
    entries = {}
    for i,label in enumerate(labels):
        tk.Label(top,text=label).grid(row=i,column=0)
        entries[label]=tk.Entry(top)
        entries[label].grid(row=i,column=1)

    def save_out_item():
        try:
            qty_out = int(entries["Quantity"].get())
        except:
            messagebox.showerror("Error","Quantity must be number")
            return
        found = False
        for item in inventory:
            if item["ID"]==entries["ID"].get() or item["Name"]==entries["Name"].get():
                if qty_out>int(item["Quantity"]):
                    messagebox.showerror("Error","Not enough stock")
                    return
                item["Quantity"]=str(int(item["Quantity"])-qty_out)
                found=True
                # Outward history
                outward_history.append({
                    "ID": item["ID"],
                    "Name": item["Name"],
                    "QuantityOut": qty_out,
                    "Customer": entries["Customer"].get(),
                    "DateTime": get_current_datetime()
                })
                save_csv(OUT_HISTORY_FILE, outward_history, columns_out)
                # Inventory history
                inventory_history.append({
                    "ID": item["ID"],
                    "Name": item["Name"],
                    "ChangeType": "OUT",
                    "QuantityChange": qty_out,
                    "ResultingQuantity": item["Quantity"],
                    "Vendor/Customer": entries["Customer"].get(),
                    "PartCode": item["PartCode"],
                    "DateTime": get_current_datetime()
                })
                save_csv(INVENTORY_HISTORY_FILE, inventory_history, columns_inventory_history)
                save_csv(INVENTORY_FILE, inventory, columns_inv)
                update_inventory_table()
                update_history_tables()
                top.destroy()
                return
        if not found:
            messagebox.showerror("Error","Item not found")
    tk.Button(top,text="Save Out",command=save_out_item).grid(row=len(labels),column=0,columnspan=2,pady=5)

def edit_item_dialog():
    messagebox.showinfo("Info","Double-click Low Stock Quantity to edit, inventory updates automatically.")

def search_item_dialog():
    top=tk.Toplevel(root)
    top.title("Search Item")
    tk.Label(top,text="Search by ID/Name").grid(row=0,column=0)
    e=tk.Entry(top)
    e.grid(row=0,column=1)
    def search():
        q=e.get().lower()
        tree_inventory.delete(*tree_inventory.get_children())
        for item in inventory:
            if q in item["ID"].lower() or q in item["Name"].lower():
                tree_inventory.insert("", "end", values=[item[col] for col in columns_inv])
    tk.Button(top,text="Search",command=search).grid(row=1,column=0,columnspan=2,pady=5)

def export_low_items():
    save_csv("low_quantity_export.csv", check_low_quantity(), columns_low)
    messagebox.showinfo("Exported","Low quantity items exported to low_quantity_export.csv")

# ------------------ Main Buttons ------------------
frame_buttons = tk.Frame(scrollable_frame,pady=10)
frame_buttons.grid(row=0,column=0,columnspan=2,sticky="w")

tk.Button(frame_buttons,text="➕ Add Item",width=15,bg="#4CAF50",fg="white",command=add_item_dialog).pack(side="left",padx=5)
tk.Button(frame_buttons,text="✏️ Edit Item",width=15,bg="#FFC107",fg="white",command=edit_item_dialog).pack(side="left",padx=5)
tk.Button(frame_buttons,text="📤 Item Out",width=15,bg="#F44336",fg="white",command=item_out_dialog).pack(side="left",padx=5)
tk.Button(frame_buttons,text="🔍 Search",width=15,bg="#2196F3",fg="white",command=search_item_dialog).pack(side="left",padx=5)
tk.Button(frame_buttons,text="🔄 Refresh",width=15,bg="#9E9E9E",fg="white",
          command=lambda:[update_inventory_table(),update_history_tables()]).pack(side="left",padx=5)
tk.Button(frame_buttons,text="💾 Export Low Items",width=20,bg="#FF5722",fg="white",command=export_low_items).pack(side="left",padx=5)

# ------------------ 2x2 Table Layout ------------------
frame_top=tk.Frame(scrollable_frame)
frame_top.grid(row=1,column=0,columnspan=4,sticky="nsew")
frame_bottom=tk.Frame(scrollable_frame)
frame_bottom.grid(row=2,column=0,columnspan=4,sticky="nsew")

def create_table(frame,title,columns):
    tk.Label(frame,text=title,font=("Segoe UI Emoji",12,"bold")).pack()
    tree=ttk.Treeview(frame)
    tree["columns"]=columns
    tree["show"]="headings"
    for col in columns:
        tree.heading(col,text=col)
        tree.column(col,anchor="center",width=150)
    tree.pack(fill="both",expand=True)
    scrollbar=ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right",fill="y")
    return tree

frame_inventory=tk.Frame(frame_top)
frame_inventory.grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
tree_inventory=create_table(frame_inventory,"📦 Inventory",columns_inv)

frame_low=tk.Frame(frame_top)
frame_low.grid(row=0,column=1,padx=5,pady=5,sticky="nsew")
tree_low=create_table(frame_low,"⚠️ Low Quantity",columns_low)

frame_in=tk.Frame(frame_bottom)
frame_in.grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
tree_in=create_table(frame_in,"⬅️ Inward History",columns_in)

frame_out=tk.Frame(frame_bottom)
frame_out.grid(row=0,column=1,padx=5,pady=5,sticky="nsew")
tree_out=create_table(frame_out,"➡️ Outward History",columns_out)

frame_hist=tk.Frame(scrollable_frame)
frame_hist.grid(row=3,column=0,columnspan=2,padx=5,pady=5,sticky="nsew")
tree_hist=create_table(frame_hist,"📜 Inventory History",columns_inventory_history)

# ------------------ Editable Low Stock ------------------
def edit_low_stock(event):
    selected=tree_low.focus()
    if not selected:
        return
    col=tree_low.identify_column(event.x)
    if col!="#3":
        return
    x,y,width,height=tree_low.bbox(selected,col)
    entry_edit=tk.Entry(tree_low)
    entry_edit.place(x=x,y=y,width=width,height=height)
    entry_edit.focus()

    def save_edit(event):
        try:
            new_qty=int(entry_edit.get())
        except:
            messagebox.showerror("Error","Quantity must be a number")
            entry_edit.destroy()
            return
        tree_low.set(selected,column="Quantity",value=new_qty)
        low_item_id=tree_low.item(selected,"values")[0]
        for item in inventory:
            if item["ID"]==low_item_id:
                item["Quantity"]=str(new_qty)
                save_csv(INVENTORY_FILE,inventory,columns_inv)
                break
        entry_edit.destroy()
        update_inventory_table()
        update_history_tables()
    entry_edit.bind("<Return>",save_edit)
    entry_edit.bind("<FocusOut>",lambda e: entry_edit.destroy())

tree_low.bind("<Double-1>",edit_low_stock)

# ------------------ Initialize ------------------
update_inventory_table()
update_history_tables()
root.mainloop()
