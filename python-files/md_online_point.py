import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ---------------- Database Setup ----------------
conn = sqlite3.connect("md_online_point.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        particulars TEXT,
        remarks TEXT,
        amount REAL
    )
""")
conn.commit()

# ---------------- Functions ----------------
def add_record():
    date = date_entry.get()
    particulars = particulars_entry.get()
    remarks = remarks_entry.get()
    amount = amount_entry.get()

    if not date or not particulars or not amount:
        messagebox.showerror("Error", "Please fill Date, Particulars and Amount")
        return

    try:
        amt = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    cursor.execute("INSERT INTO transactions (date, particulars, remarks, amount) VALUES (?, ?, ?, ?)",
                   (date, particulars, remarks, amt))
    conn.commit()
    messagebox.showinfo("Success", "Record added successfully!")
    clear_entries()
    load_records()


def clear_entries():
    date_entry.delete(0, tk.END)
    particulars_entry.delete(0, tk.END)
    remarks_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)


def load_records():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    income, expense = 0, 0

    for r in rows:
        tree.insert("", tk.END, values=r)
        if r[4] >= 0:
            income += r[4]
        else:
            expense += abs(r[4])

    total_income_label.config(text=f"Total Income: ₹{income:.2f}")
    total_expense_label.config(text=f"Total Expense: ₹{expense:.2f}")
    profit_loss_label.config(text=f"Profit / Loss: ₹{(income - expense):.2f}")


def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a record to delete")
        return

    record_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM transactions WHERE id=?", (record_id,))
    conn.commit()
    messagebox.showinfo("Deleted", "Record deleted successfully!")
    load_records()

# ---------------- UI Setup ----------------
root = tk.Tk()
root.title("MD ONLINE POINT - Income & Expense Tracker")
root.geometry("800x600")

# Form Frame
form_frame = tk.Frame(root)
form_frame.pack(pady=10)

tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
date_entry = tk.Entry(form_frame)
date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
date_entry.grid(row=0, column=1)

tk.Label(form_frame, text="Service / Particulars:").grid(row=1, column=0)
particulars_entry = tk.Entry(form_frame)
particulars_entry.grid(row=1, column=1)

tk.Label(form_frame, text="Remarks:").grid(row=2, column=0)
remarks_entry = tk.Entry(form_frame)
remarks_entry.grid(row=2, column=1)

tk.Label(form_frame, text="Amount (+income / -expense):").grid(row=3, column=0)
amount_entry = tk.Entry(form_frame)
amount_entry.grid(row=3, column=1)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Add Record", command=add_record).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Delete Record", command=delete_record).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Refresh", command=load_records).grid(row=0, column=2, padx=5)

# Table
columns = ("ID", "Date", "Particulars", "Remarks", "Amount")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(pady=10)

# Summary Labels
summary_frame = tk.Frame(root)
summary_frame.pack(pady=10)

total_income_label = tk.Label(summary_frame, text="Total Income: ₹0.00", font=("Arial", 12, "bold"))
total_income_label.grid(row=0, column=0, padx=20)

total_expense_label = tk.Label(summary_frame, text="Total Expense: ₹0.00", font=("Arial", 12, "bold"))
total_expense_label.grid(row=0, column=1, padx=20)

profit_loss_label = tk.Label(summary_frame, text="Profit / Loss: ₹0.00", font=("Arial", 12, "bold"))
profit_loss_label.grid(row=0, column=2, padx=20)

# Load data on start
load_records()

root.mainloop()
