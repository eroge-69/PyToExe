import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import pandas as pd

# Initialize DB
def init_db():
    conn = sqlite3.connect("records.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        engineer_name TEXT,
        unit_id TEXT,
        issue TEXT,
        solution TEXT,
        part_ordered INTEGER,
        repaired INTEGER,
        timestamp TEXT
    )''')
    conn.close()

# Add Record
def add_record(engineer_name, unit_id, issue, solution, part_ordered, repaired):
    conn = sqlite3.connect("records.db")
    conn.execute('''
        INSERT INTO records(engineer_name, unit_id, issue, solution, part_ordered, repaired, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (engineer_name, unit_id, issue, solution, part_ordered, repaired,
          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    refresh_tree()

# Update Record
def update_record(record_id, engineer_name, unit_id, issue, solution, part_ordered, repaired):
    conn = sqlite3.connect("records.db")
    conn.execute('''
        UPDATE records
        SET engineer_name=?, unit_id=?, issue=?, solution=?, part_ordered=?, repaired=?
        WHERE id=?
    ''', (engineer_name, unit_id, issue, solution, part_ordered, repaired, record_id))
    conn.commit()
    conn.close()
    refresh_tree()

# Delete Record
def delete_record():
    if not selected_id.get():
        messagebox.showwarning("Delete", "No record selected.")
        return

    answer = messagebox.askyesno("Delete", "Are you sure you want to delete this record?")
    if answer:
        conn = sqlite3.connect("records.db")
        conn.execute("DELETE FROM records WHERE id=?", (selected_id.get(),))
        conn.commit()
        conn.close()
        refresh_tree()
        clear_inputs()
        selected_id.set("")

# Load records into Treeview
def refresh_tree():
    for item in tree.get_children():
        tree.delete(item)
    conn = sqlite3.connect("records.db")
    cursor = conn.execute("SELECT * FROM records")
    for row in cursor:
        tree.insert('', tk.END, values=row)
    conn.close()

# Submit Button Action
def submit_record():
    engineer = entry_engineer.get()
    unit = entry_unit.get()
    issue = entry_issue.get()
    solution = entry_solution.get()
    part = var_part.get()
    repaired = var_repaired.get()

    if selected_id.get():
        update_record(selected_id.get(), engineer, unit, issue, solution, part, repaired)
        selected_id.set("")
    else:
        add_record(engineer, unit, issue, solution, part, repaired)

    clear_inputs()

# Clear input fields
def clear_inputs():
    entry_engineer.delete(0, tk.END)
    entry_unit.delete(0, tk.END)
    entry_issue.delete(0, tk.END)
    entry_solution.delete(0, tk.END)
    var_part.set(0)
    var_repaired.set(0)

# On Tree row select
def on_tree_select(event):
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, 'values')
    selected_id.set(values[0])
    entry_engineer.delete(0, tk.END)
    entry_engineer.insert(0, values[1])
    entry_unit.delete(0, tk.END)
    entry_unit.insert(0, values[2])
    entry_issue.delete(0, tk.END)
    entry_issue.insert(0, values[3])
    entry_solution.delete(0, tk.END)
    entry_solution.insert(0, values[4])
    var_part.set(int(values[5]))
    var_repaired.set(int(values[6]))

# Export to Excel
def export_excel():
    conn = sqlite3.connect("records.db")
    df = pd.read_sql_query("SELECT * FROM records", conn)
    filename = f"records_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)
    conn.close()
    messagebox.showinfo("Export", f"Records exported to {filename}")

# GUI Setup
root = tk.Tk()
root.title("Engineer Repair Records")

selected_id = tk.StringVar()
var_part = tk.IntVar()
var_repaired = tk.IntVar()

tk.Label(root, text="Engineer Name").grid(row=0, column=0)
entry_engineer = tk.Entry(root)
entry_engineer.grid(row=0, column=1)

tk.Label(root, text="Unit ID").grid(row=1, column=0)
entry_unit = tk.Entry(root)
entry_unit.grid(row=1, column=1)

tk.Label(root, text="Issue").grid(row=2, column=0)
entry_issue = tk.Entry(root)
entry_issue.grid(row=2, column=1)

tk.Label(root, text="Solution").grid(row=3, column=0)
entry_solution = tk.Entry(root)
entry_solution.grid(row=3, column=1)

tk.Checkbutton(root, text="Part Ordered", variable=var_part).grid(row=0, column=2)
tk.Checkbutton(root, text="Repaired", variable=var_repaired).grid(row=1, column=2)

tk.Button(root, text="Submit", command=submit_record).grid(row=3, column=2)
tk.Button(root, text="Delete", command=delete_record).grid(row=4, column=2)
tk.Button(root, text="Export to Excel", command=export_excel).grid(row=5, column=2)

columns = ("ID", "Engineer", "Unit", "Issue", "Solution", "Part Ordered", "Repaired", "Timestamp")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.grid(row=6, column=0, columnspan=3, sticky="nsew")
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Make table resizable
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(1, weight=1)

init_db()
refresh_tree()
root.mainloop()
