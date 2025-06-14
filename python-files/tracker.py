
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
# Stationary Tracker System using Tkinter and SQLite

# Database setup
def init_db():
    conn = sqlite3.connect("stationary.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER,
        category TEXT
    )
    """)
    conn.commit()
    conn.close()

# Functions for buttons
def add_item():
    name = entry_name.get()
    quantity = entry_quantity.get()
    category = entry_category.get()

    if name == "" or quantity == "" or category == "":
        messagebox.showwarning("Input Error", "Please fill all fields")
        return

    conn = sqlite3.connect("stationary.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, quantity, category) VALUES (?, ?, ?)", (name, quantity, category))
    conn.commit()
    conn.close()
    display_items()
    clear_entries()
    messagebox.showinfo("Success", "Item added successfully!")

def display_items():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("stationary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)

    conn.close()

def delete_item():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Select Item", "No item selected")
        return

    values = tree.item(selected, 'values')
    item_id = values[0]

    conn = sqlite3.connect("stationary.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    display_items()
    messagebox.showinfo("Deleted", "Item deleted successfully")

def update_item():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Select Item", "No item selected")
        return

    values = tree.item(selected, 'values')
    item_id = values[0]

    name = entry_name.get()
    quantity = entry_quantity.get()
    category = entry_category.get()

    conn = sqlite3.connect("stationary.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name=?, quantity=?, category=? WHERE id=?",
                   (name, quantity, category, item_id))
    conn.commit()
    conn.close()
    display_items()
    clear_entries()
    messagebox.showinfo("Updated", "Item updated successfully")

def clear_entries():
    entry_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_category.delete(0, tk.END)

def on_tree_select(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected, 'values')
        entry_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_category.delete(0, tk.END)
        entry_name.insert(0, values[1])
        entry_quantity.insert(0, values[2])
        entry_category.insert(0, values[3])

# GUI setup
root = tk.Tk()
root.title("Stationary Tracker System")
root.geometry("700x450")

# Labels and Entries
tk.Label(root, text="Item Name").grid(row=0, column=0, padx=10, pady=5)
tk.Label(root, text="Quantity").grid(row=0, column=1, padx=10, pady=5)
tk.Label(root, text="Category").grid(row=0, column=2, padx=10, pady=5)

entry_name = tk.Entry(root)
entry_quantity = tk.Entry(root)
entry_category = tk.Entry(root)

entry_name.grid(row=1, column=0, padx=10, pady=5)
entry_quantity.grid(row=1, column=1, padx=10, pady=5)
entry_category.grid(row=1, column=2, padx=10, pady=5)

# Buttons
tk.Button(root, text="Add", command=add_item, width=10).grid(row=2, column=0, pady=10)
tk.Button(root, text="Update", command=update_item, width=10).grid(row=2, column=1)
tk.Button(root, text="Delete", command=delete_item, width=10).grid(row=2, column=2)
tk.Button(root, text="Show All", command=display_items, width=10).grid(row=2, column=3)

# Treeview
columns = ("ID", "Name", "Quantity", "Category")
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.bind("<<TreeviewSelect>>", on_tree_select)
tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

# Initialize
init_db()
display_items()
root.mainloop()
