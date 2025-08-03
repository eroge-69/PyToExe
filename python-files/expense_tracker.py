import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# --- Database Setup ---
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT
    )
""")
conn.commit()

# --- Functions ---
def add_expense():
    try:
        amt = float(amount_entry.get())
        cat = category_entry.get()
        date_val = date_entry.get()
        desc = desc_entry.get()

        if not cat or not date_val:
            raise ValueError("Category and Date are required.")

        cursor.execute("INSERT INTO expenses (amount, category, date, description) VALUES (?, ?, ?, ?)",
                       (amt, cat, date_val, desc))
        conn.commit()
        messagebox.showinfo("Success", "Expense added!")
        clear_fields()
        load_expenses()
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))

def load_expenses():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT id, amount, category, date, description FROM expenses")
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

def delete_expense():
    selected = tree.selection()
    if not selected:
        return messagebox.showwarning("No selection", "Please select a record to delete.")

    expense_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    tree.delete(selected[0])

def clear_fields():
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

# --- GUI Setup ---
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("700x500")
root.resizable(False, False)

# Input Frame
input_frame = tk.LabelFrame(root, text="Add Expense", padx=10, pady=10)
input_frame.pack(fill="x", padx=10, pady=5)

tk.Label(input_frame, text="Amount").grid(row=0, column=0)
amount_entry = tk.Entry(input_frame)
amount_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Category").grid(row=0, column=2)
category_entry = tk.Entry(input_frame)
category_entry.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=1, column=0)
date_entry = tk.Entry(input_frame)
date_entry.grid(row=1, column=1, padx=5)
date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

tk.Label(input_frame, text="Description").grid(row=1, column=2)
desc_entry = tk.Entry(input_frame)
desc_entry.grid(row=1, column=3, padx=5)

add_btn = tk.Button(input_frame, text="Add Expense", command=add_expense)
add_btn.grid(row=2, column=0, columnspan=4, pady=10)

# Table Frame
table_frame = tk.LabelFrame(root, text="Expense History", padx=10, pady=10)
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("ID", "Amount", "Category", "Date", "Description")
tree = ttk.Treeview(table_frame, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100 if col != "Description" else 200)
tree.pack(fill="both", expand=True)

# Delete Button
delete_btn = tk.Button(root, text="Delete Selected Expense", command=delete_expense)
delete_btn.pack(pady=5)

# Load data
load_expenses()

# Run app
root.mainloop()
