import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
import csv
from tkinter import filedialog

# Initialize DB
conn = sqlite3.connect("kits.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS kits (
    id INTEGER PRIMARY KEY,
    kit_number TEXT,
    system TEXT,
    serial_number TEXT
)""")
conn.commit()

# Functions

def view_data():
    records = cur.execute("SELECT * FROM kits").fetchall()
    update_table(records)

def search_data():
    query = f"""
        SELECT * FROM kits WHERE
        kit_number LIKE ? AND
        system LIKE ? AND
        serial_number LIKE ?
    """
    values = (
        f"%{kit_var.get()}%",
        f"%{system_var.get()}%",
        f"%{serial_var.get()}%"
    )
    records = cur.execute(query, values).fetchall()
    update_table(records)

def add_data():
    if not (kit_var.get() and system_var.get() and serial_var.get()):
        messagebox.showwarning("Input Error", "All fields are required.")
        return
    cur.execute("INSERT INTO kits (kit_number, system, serial_number) VALUES (?, ?, ?)",
                (kit_var.get(), system_var.get(), serial_var.get()))
    conn.commit()
    view_data()
    clear_fields()

def delete_data():
    selected = tree.focus()
    if not selected:
        messagebox.showinfo("Select Record", "Please select a record to delete.")
        return
    record_id = tree.item(selected)['values'][0]
    cur.execute("DELETE FROM kits WHERE id=?", (record_id,))
    conn.commit()
    view_data()

def clear_fields():
    kit_var.set("")
    system_var.set("")
    serial_var.set("")

def on_select(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected)['values']
        kit_var.set(values[1])
        system_var.set(values[2])
        serial_var.set(values[3])

def update_table(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert('', 'end', values=row)
def export_to_csv():
    filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            title="Save as")
    if not filename:
        return

    cur.execute("SELECT * FROM kits")
    rows = cur.fetchall()

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Kit Number", "System", "Serial Number"])
            writer.writerows(rows)
        messagebox.showinfo("Export Successful", f"Data exported to {filename}")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))
def import_from_csv():
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")],
                                          title="Select CSV File to Import")

    if not filename:
        return

    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip header row

            if headers != ["Kit Number", "System", "Serial Number"]:
                messagebox.showerror("Invalid Format", "CSV file must have headers: Kit Number, System, Serial Number")
                return

            imported_count = 0
            for row in reader:
                if len(row) != 3:
                    continue  # Skip malformed rows
                cur.execute("INSERT INTO kits (kit_number, system, serial_number) VALUES (?, ?, ?)", row)
                imported_count += 1

            conn.commit()
            messagebox.showinfo("Import Successful", f"{imported_count} records imported successfully.")
            view_data()  # Refresh the table
    except Exception as e:
        messagebox.showerror("Import Failed", str(e))

# UI Setup
root = Tk()
root.title("Kit Manager by Mark Schmitt")
root.geometry("800x400")

kit_var = StringVar()
system_var = StringVar()
serial_var = StringVar()

# Input Fields
Label(root, text="Kit Number").grid(row=0, column=0, padx=5, pady=5)
Entry(root, textvariable=kit_var).grid(row=0, column=1)

Label(root, text="System").grid(row=1, column=0, padx=5, pady=5)
Entry(root, textvariable=system_var).grid(row=1, column=1)

Label(root, text="Serial Number").grid(row=2, column=0, padx=5, pady=5)
Entry(root, textvariable=serial_var).grid(row=2, column=1)

# Buttons
Button(root, text="Add", command=add_data).grid(row=0, column=2, padx=10)
Button(root, text="Search", command=search_data).grid(row=1, column=2)
Button(root, text="Delete", command=delete_data).grid(row=2, column=2)
Button(root, text="Clear", command=clear_fields).grid(row=3, column=2)
Button(root, text="View All", command=view_data).grid(row=3, column=1)
Button(root, text="Export to CSV", command=export_to_csv).grid(row=5, column=1, pady=10)
Button(root, text="Import from CSV", command=import_from_csv).grid(row=5, column=2, pady=10)
 
# Table
columns = ("id", "kit_number", "system", "serial_number")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col.capitalize())
    tree.column(col, anchor="center")
tree.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")
tree.bind("<<TreeviewSelect>>", on_select)

# Scrollbar
scrollbar = Scrollbar(root, orient=VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=4, column=3, sticky='ns')

view_data()
root.mainloop()
