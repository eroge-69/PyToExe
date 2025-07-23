import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Create main window
root = tk.Tk()
root.title("📚 Book Inventory & Expense Tracker")
root.geometry("1100x650")
root.resizable(False, False)

# Connect to SQLite
conn = sqlite3.connect('book_inventory.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_name TEXT,
        semester TEXT,
        quantity INTEGER,
        price REAL,
        sample_qty INTEGER,
        delivery REAL,
        paid REAL,
        date TEXT,
        remarks TEXT
    )
''')
conn.commit()

# Global variables
fields = {
    "Book Name": tk.StringVar(),
    "Semester": tk.StringVar(),
    "Quantity": tk.IntVar(),
    "Price per Unit": tk.DoubleVar(),
    "Sample Quantity": tk.IntVar(),
    "Delivery Charges": tk.DoubleVar(),
    "Paid Amount": tk.DoubleVar(),
    "Remarks": tk.StringVar()
}
selected_item = None
analytics_text = tk.StringVar()
search_book_var = tk.StringVar()
search_semester_var = tk.StringVar()

# Functions
def calculate_balance():
    qty = fields["Quantity"].get()
    price = fields["Price per Unit"].get()
    samples = fields["Sample Quantity"].get()
    delivery = fields["Delivery Charges"].get()
    paid = fields["Paid Amount"].get()
    total_cost = (qty - samples) * price + delivery
    remaining = total_cost - paid
    return total_cost, remaining

def add_entry():
    total_cost, remaining = calculate_balance()
    data = (
        fields["Book Name"].get(),
        fields["Semester"].get(),
        fields["Quantity"].get(),
        fields["Price per Unit"].get(),
        fields["Sample Quantity"].get(),
        fields["Delivery Charges"].get(),
        fields["Paid Amount"].get(),
        date_entry.get_date().strftime('%Y-%m-%d'),
        fields["Remarks"].get()
    )
    cursor.execute('''
        INSERT INTO books (book_name, semester, quantity, price, sample_qty,
                           delivery, paid, date, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    messagebox.showinfo("Success", f"Entry added!\nTotal Cost: {total_cost}\nRemaining Balance: {remaining}")
    clear_form()
    load_data()

def update_entry():
    global selected_item
    if not selected_item:
        messagebox.showwarning("No selection", "Please select a row to update.")
        return
    data = (
        fields["Book Name"].get(),
        fields["Semester"].get(),
        fields["Quantity"].get(),
        fields["Price per Unit"].get(),
        fields["Sample Quantity"].get(),
        fields["Delivery Charges"].get(),
        fields["Paid Amount"].get(),
        date_entry.get_date().strftime('%Y-%m-%d'),
        fields["Remarks"].get(),
        selected_item[0]
    )
    cursor.execute('''
        UPDATE books SET book_name=?, semester=?, quantity=?, price=?, sample_qty=?,
                        delivery=?, paid=?, date=?, remarks=? WHERE book_name=?
    ''', data)
    conn.commit()
    messagebox.showinfo("Updated", "Entry updated successfully!")
    clear_form()
    load_data()

def delete_entry():
    global selected_item
    if not selected_item:
        messagebox.showwarning("No selection", "Please select a row to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
    if confirm:
        cursor.execute("DELETE FROM books WHERE book_name=?", (selected_item[0],))
        conn.commit()
        messagebox.showinfo("Deleted", "Entry deleted successfully!")
        clear_form()
        load_data()

def clear_form():
    global selected_item
    selected_item = None
    for var in fields.values():
        var.set("")
    date_entry.set_date("2025-07-23")

def load_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT book_name, semester, quantity, price, sample_qty, delivery, paid, date, remarks FROM books")
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
def apply_filters():
    book_filter = search_book_var.get().lower()
    semester_filter = search_semester_var.get().lower()
    tree.delete(*tree.get_children())
    cursor.execute("SELECT book_name, semester, quantity, price, sample_qty, delivery, paid, date, remarks FROM books")
    for row in cursor.fetchall():
        if book_filter in row[0].lower() and semester_filter in row[1].lower():
            tree.insert('', 'end', values=row)

def on_row_select(event):
    global selected_item
    selected = tree.focus()
    if selected:
        values = tree.item(selected, 'values')
        selected_item = values
        fields["Book Name"].set(values[0])
        fields["Semester"].set(values[1])
        fields["Quantity"].set(values[2])
        fields["Price per Unit"].set(values[3])
        fields["Sample Quantity"].set(values[4])
        fields["Delivery Charges"].set(values[5])
        fields["Paid Amount"].set(values[6])
        date_entry.set_date(values[7])
        fields["Remarks"].set(values[8])

def export_to_excel():
    cursor.execute("SELECT * FROM books")
    df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
    df.to_excel("Book_Inventory.xlsx", index=False)
    messagebox.showinfo("Exported", "Data exported to Book_Inventory.xlsx")

def show_analytics():
    cursor.execute("SELECT quantity, sample_qty, delivery, paid, price FROM books")
    rows = cursor.fetchall()

    total_books = sum(r[0] for r in rows)
    total_samples = sum(r[1] for r in rows)
    total_delivery = sum(r[2] for r in rows)
    total_paid = sum(r[3] for r in rows)
    total_cost = sum((r[0] - r[1]) * r[4] + r[2] for r in rows)
    remaining = total_cost - total_paid

    analytics_text.set(f"""
📊 Total Books: {total_books}
📦 Total Samples: {total_samples}
🚚 Delivery Charges: {total_delivery}
💰 Total Paid: {total_paid}
🧾 Total Cost: {total_cost}
🧮 Remaining Balance: {remaining}
""")

    # Optional chart
    plt.figure(figsize=(6, 4))
    plt.bar(["Total Cost", "Paid", "Remaining"], [total_cost, total_paid, remaining], color=["skyblue", "green", "orange"])
    plt.title("Financial Overview")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.show()
# ------------------ Tabs ------------------ #
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

entry_tab = ttk.Frame(notebook)
table_tab = ttk.Frame(notebook)
analytics_tab = ttk.Frame(notebook)

notebook.add(entry_tab, text="📘 Book Entry")
notebook.add(table_tab, text="📋 Table View")
notebook.add(analytics_tab, text="📊 Analytics")

# ------------------ Book Entry Form ------------------ #
form_frame = ttk.LabelFrame(entry_tab, text="Enter Book Details")
form_frame.pack(padx=20, pady=20, fill='x')

row = 0
for label, var in fields.items():
    ttk.Label(form_frame, text=label + ":").grid(row=row, column=0, sticky='w', padx=10, pady=5)
    ttk.Entry(form_frame, textvariable=var, width=30).grid(row=row, column=1, padx=10, pady=5)
    row += 1

ttk.Label(form_frame, text="Purchase Date:").grid(row=row, column=0, sticky='w', padx=10, pady=5)
date_entry = DateEntry(form_frame, width=28, background='darkblue', foreground='white', borderwidth=2)
date_entry.grid(row=row, column=1, padx=10, pady=5)

button_frame = ttk.Frame(entry_tab)
button_frame.pack(pady=10)
ttk.Button(button_frame, text="➕ Add Entry", command=add_entry).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="✏️ Update Entry", command=update_entry).grid(row=0, column=1, padx=10)
ttk.Button(button_frame, text="🗑️ Delete Entry", command=delete_entry).grid(row=0, column=2, padx=10)

# ------------------ Filter Panel ------------------ #
filter_frame = ttk.LabelFrame(table_tab, text="🔍 Filter Records")
filter_frame.pack(padx=20, pady=10, fill='x')

ttk.Label(filter_frame, text="Search Book Name:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
ttk.Entry(filter_frame, textvariable=search_book_var, width=30).grid(row=0, column=1, padx=10, pady=5)
ttk.Label(filter_frame, text="Search Semester:").grid(row=0, column=2, padx=10, pady=5, sticky='w')
ttk.Entry(filter_frame, textvariable=search_semester_var, width=30).grid(row=0, column=3, padx=10, pady=5)

ttk.Button(filter_frame, text="Apply Filter", command=apply_filters).grid(row=0, column=4, padx=10)
ttk.Button(filter_frame, text="Clear Filter", command=lambda: [search_book_var.set(""), search_semester_var.set(""), load_data()]).grid(row=0, column=5, padx=10)

# ------------------ Table View ------------------ #
table_frame = ttk.Frame(table_tab)
table_frame.pack(padx=20, pady=10, fill='both', expand=True)

columns = ("Book Name", "Semester", "Quantity", "Price", "Sample Qty", "Delivery", "Paid", "Date", "Remarks")
tree = ttk.Treeview(table_frame, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(side='left', fill='both', expand=True)
tree.bind("<<TreeviewSelect>>", on_row_select)

scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side='right', fill='y')

# ------------------ Analytics Tab ------------------ #
analytics_frame = ttk.Frame(analytics_tab)
analytics_frame.pack(padx=20, pady=20, fill='both', expand=True)

ttk.Button(analytics_frame, text="📊 Show Analytics", command=show_analytics).pack(pady=10)
ttk.Button(analytics_frame, text="📁 Export to Excel", command=export_to_excel).pack(pady=10)
ttk.Label(analytics_frame, textvariable=analytics_text, justify='left', font=('Segoe UI', 11)).pack(pady=10)

# ------------------ Launch App ------------------ #
load_data()
root.mainloop()
