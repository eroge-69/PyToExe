import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database create
conn = sqlite3.connect("staff.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS staff(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            nic TEXT,
            designation TEXT,
            contact TEXT
            )""")
conn.commit()

# Save record
def save_record():
    fullname = entry_name.get()
    nic = entry_nic.get()
    designation = entry_designation.get()
    contact = entry_contact.get()
    if fullname and nic:
        c.execute("INSERT INTO staff(fullname,nic,designation,contact) VALUES(?,?,?,?)",
                  (fullname, nic, designation, contact))
        conn.commit()
        messagebox.showinfo("Success", "Record saved!")
        clear_form()
    else:
        messagebox.showwarning("Error", "Name & NIC required")

def clear_form():
    entry_name.delete(0, tk.END)
    entry_nic.delete(0, tk.END)
    entry_designation.delete(0, tk.END)
    entry_contact.delete(0, tk.END)

# GUI
root = tk.Tk()
root.title("පලාගල කාර්ය මණ්ඩල තොරතුරු")

tk.Label(root, text="Full Name").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="NIC").grid(row=1, column=0)
entry_nic = tk.Entry(root)
entry_nic.grid(row=1, column=1)

tk.Label(root, text="Designation").grid(row=2, column=0)
entry_designation = tk.Entry(root)
entry_designation.grid(row=2, column=1)

tk.Label(root, text="Contact").grid(row=3, column=0)
entry_contact = tk.Entry(root)
entry_contact.grid(row=3, column=1)

tk.Button(root, text="Save", command=save_record).grid(row=4, column=0)
tk.Button(root, text="Clear", command=clear_form).grid(row=4, column=1)

root.mainloop()
