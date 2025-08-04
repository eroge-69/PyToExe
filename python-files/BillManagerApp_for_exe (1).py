
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry, Calendar
import sqlite3, shutil, datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# === Database Setup ===
conn = sqlite3.connect("bills.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT, date_of_issue TEXT, due_date TEXT,
    amount REAL, status TEXT, money_received_date TEXT, notes TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, password TEXT, role TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, phone TEXT, email TEXT, notes TEXT
)""")
conn.commit()

# === Globals ===
CURRENT_ROLE = "Admin"
OWNER_PASSWORD = "1234"
current_edit_id = None
sort_column = "id"
sort_ascending = False

# === App Setup ===
root = tk.Tk()
root.title("Bill Manager")
root.geometry("1300x800")
root.configure(bg="#ede7f6")

# === Sidebar ===
def show_frame(frame):
    for ch in content_frame.winfo_children():
        ch.pack_forget()
    frame.pack(fill="both", expand=True)

sidebar = tk.Frame(root, bg="#8e24aa", width=180)
sidebar.pack(side="left", fill="y")

def create_sidebar_button(name, frame):
    btn = tk.Button(sidebar, text=name, fg="white", bg="#8e24aa", relief="flat",
                    command=lambda: show_frame(frame))
    btn.pack(fill="x", pady=2)

# === Utility Functions ===
def backup_database():
    fn = f"bills_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy("bills.db", fn)

def clear_entries():
    for e in [bill_number_entry, issue_entry, due_entry, amount_entry, received_entry, notes_entry]:
        e.delete(0, tk.END)
    status_var.set("Unpaid")
    global current_edit_id
    current_edit_id = None

def due_date_reminder():
    today = datetime.date.today()
    warn = []
    for bn, d in c.execute("SELECT bill_number, due_date FROM bills"):
        try:
            due = datetime.datetime.strptime(d, "%Y-%m-%d").date()
            if due <= today:
                warn.append(bn)
        except:
            pass
    if warn:
        messagebox.showwarning("Overdue Bills", "Due or overdue:
" + "\n".join(warn))

def load_bills(status=None):
    for r in bill_table.get_children(): bill_table.delete(r)
    query = f"SELECT * FROM bills"
    params = ()
    if status and status != "All":
        query += " WHERE status=?"
        params = (status,)
    query += f" ORDER BY {sort_column} {'ASC' if sort_ascending else 'DESC'}"
    for r in c.execute(query, params):
        bill_table.insert("", tk.END, values=r)

def apply_filter():
    load_bills(filter_var.get())

def sort_by_column(col):
    global sort_column, sort_ascending
    sort_column = col
    sort_ascending = not sort_ascending
    apply_filter()

# === Main Frame ===
content_frame = tk.Frame(root, bg="#ede7f6")
content_frame.pack(side="left", fill="both", expand=True)

main_frame = tk.Frame(content_frame, bg="#ede7f6")
create_sidebar_button("Main", main_frame)

filter_var = tk.StringVar(value="All")
filter_frame = tk.Frame(main_frame, bg="#ede7f6")
filter_frame.pack(pady=5)
tk.Label(filter_frame, text="Filter:", bg="#ede7f6").pack(side="left")
ttk.Combobox(filter_frame, textvariable=filter_var, values=["All", "Paid", "Unpaid", "Refund", "Cancel"], width=10).pack(side="left", padx=5)
ttk.Button(filter_frame, text="Apply", command=apply_filter).pack(side="left")

form = tk.Frame(main_frame, bg="#ede7f6"); form.pack(pady=10)
labels = ["Bill Number", "Issue Date", "Due Date", "Amount", "Status", "Received Date", "Notes"]
entries = []
for i, lbl in enumerate(labels):
    tk.Label(form, text=lbl+":", bg="#ede7f6").grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=5)
    if "Date" in lbl:
        entry = DateEntry(form, date_pattern="yyyy-mm-dd", width=28)
    elif lbl == "Status":
        status_var = tk.StringVar(value="Unpaid")
        entry = ttk.Combobox(form, textvariable=status_var, values=["Paid", "Unpaid", "Refund", "Cancel"], width=18)
    else:
        entry = tk.Entry(form, width=30)
    entry.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5)
    entries.append(entry)

(bill_number_entry, issue_entry, due_entry, amount_entry, status_box, received_entry, notes_entry) = entries

bill_table = ttk.Treeview(main_frame, columns=("ID", "Bill #", "Issue", "Due", "Amt", "Status", "Received", "Notes"), show="headings")
for col in bill_table["columns"]:
    bill_table.heading(col, text=col, command=lambda c=col: sort_by_column(c.lower().replace(" #","_").replace(" ","_")))
bill_table.pack(fill="both", expand=True)

def add_bill():
    data = (
        bill_number_entry.get(), issue_entry.get(), due_entry.get(),
        amount_entry.get(), status_var.get(), received_entry.get(), notes_entry.get()
    )
    if not data[0] or not data[1] or not data[3]:
        return messagebox.showerror("Error", "Bill Number, Issue Date, Amount required")
    c.execute("INSERT INTO bills (bill_number, date_of_issue, due_date, amount, status, money_received_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit(); backup_database(); clear_entries(); apply_filter()

def edit_bill():
    sel = bill_table.selection()
    if not sel: return
    vals = bill_table.item(sel[0], "values")
    bill_number_entry.delete(0, tk.END); bill_number_entry.insert(0, vals[1])
    issue_entry.delete(0, tk.END); issue_entry.insert(0, vals[2])
    due_entry.delete(0, tk.END); due_entry.insert(0, vals[3])
    amount_entry.delete(0, tk.END); amount_entry.insert(0, vals[4])
    status_var.set(vals[5])
    received_entry.delete(0, tk.END); received_entry.insert(0, vals[6])
    notes_entry.delete(0, tk.END); notes_entry.insert(0, vals[7])
    global current_edit_id; current_edit_id = vals[0]

def update_bill():
    global current_edit_id
    if not current_edit_id:
        return messagebox.showwarning("None", "Select an edit first")
    data = (
        bill_number_entry.get(), issue_entry.get(), due_entry.get(),
        amount_entry.get(), status_var.get(), received_entry.get(), notes_entry.get(), current_edit_id
    )
    c.execute("UPDATE bills SET bill_number=?, date_of_issue=?, due_date=?, amount=?, status=?, money_received_date=?, notes=? WHERE id=?", data)
    conn.commit(); backup_database(); clear_entries(); apply_filter()

def delete_bill():
    sel = bill_table.selection()
    if not sel: return
    if not messagebox.askyesno("Confirm", "Sure?"): return
    bid = bill_table.item(sel[0], "values")[0]
    c.execute("DELETE FROM bills WHERE id=?", (bid,))
    conn.commit(); backup_database(); apply_filter()

btns = tk.Frame(main_frame, bg="#ede7f6")
btns.pack(pady=5)
for name, cmd in [("Add", add_bill), ("Edit", edit_bill), ("Update", update_bill), ("Delete", delete_bill)]:
    ttk.Button(btns, text=name, command=cmd).pack(side="left", padx=5)

# === Final Frames and Launch ===
show_frame(main_frame)
due_date_reminder()
apply_filter()
root.mainloop()
