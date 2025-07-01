
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

def create_table_if_not_exists(table_name):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Bunny@1475",
            database="billing_system"
        )
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                loan_id VARCHAR(50),
                name VARCHAR(100),
                application VARCHAR(50),
                emi DECIMAL(10,2),
                ot_pay DECIMAL(10,2),
                due_date DATE,
                paid_status VARCHAR(10),
                extend_status VARCHAR(10),
                pydate DATE
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_selected_table():
    month = month_var.get().lower()
    year = year_var.get()
    if month and year:
        return f"{month}_{year}"
    else:
        messagebox.showerror("Selection Error", "Please select month and year.")
        return None

def insert_record():
    table = get_selected_table()
    if not table:
        return
    create_table_if_not_exists(table)
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Bunny@1475",
            database="billing_system"
        )
        cursor = conn.cursor()
        query = f"""
        INSERT INTO {table} (
            loan_id, name, application, emi, ot_pay, due_date, paid_status, extend_status, pydate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            entry_loanid.get(),
            entry_name.get(),
            entry_app.get(),
            entry_emi.get(),
            entry_otpay.get(),
            entry_due.get(),
            entry_paid.get(),
            entry_extend.get(),
            entry_pydate.get()
        )
        cursor.execute(query, values)
        conn.commit()
        messagebox.showinfo("Success", f"Record inserted into {table}.")
        clear_fields()
        view_records()
    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def view_records():
    table = get_selected_table()
    if not table:
        return
    for row in tree.get_children():
        tree.delete(row)
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Bunny@1475",
            database="billing_system"
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def clear_fields():
    for e in [entry_loanid, entry_name, entry_app, entry_emi, entry_otpay, entry_due, entry_paid, entry_extend, entry_pydate]:
        e.delete(0, tk.END)

root = tk.Tk()
root.title("Multi-Month Loan Management System")
root.geometry("1100x650")

# Month & Year dropdown
months = [datetime(2000, m, 1).strftime('%B') for m in range(1, 13)]
years = [str(y) for y in range(2024, 2027)]

month_var = tk.StringVar()
year_var = tk.StringVar()

tk.Label(root, text="Select Month").grid(row=0, column=0, padx=10, pady=5, sticky="w")
month_menu = ttk.Combobox(root, textvariable=month_var, values=months, state="readonly")
month_menu.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Select Year").grid(row=0, column=2, padx=10, pady=5, sticky="w")
year_menu = ttk.Combobox(root, textvariable=year_var, values=years, state="readonly")
year_menu.grid(row=0, column=3, padx=10, pady=5)

# Form inputs
labels = ["Loan ID", "Name", "Application", "EMI", "OT Pay", "Due Date (YYYY-MM-DD)", "Paid", "Extend", "Pay Date (YYYY-MM-DD)"]
entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i+1, column=0, padx=10, pady=5, sticky="w")
    entry = tk.Entry(root, width=30)
    entry.grid(row=i+1, column=1, padx=10, pady=5)
    entries.append(entry)

entry_loanid, entry_name, entry_app, entry_emi, entry_otpay, entry_due, entry_paid, entry_extend, entry_pydate = entries

tk.Button(root, text="Submit", command=insert_record, bg="green", fg="white", width=20).grid(row=10, column=0, pady=10)
tk.Button(root, text="View Records", command=view_records, bg="blue", fg="white", width=20).grid(row=10, column=1, pady=10)

columns = ("LoanID", "Name", "Application", "EMI", "OTPay", "DueDate", "Paid", "Extend", "PayDate")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.grid(row=11, column=0, columnspan=4, padx=10, pady=20)

root.mainloop()
