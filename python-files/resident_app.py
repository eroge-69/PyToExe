import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Database setup
conn = sqlite3.connect('residents.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS residents
             (name TEXT, apartment TEXT, phone TEXT, options TEXT)''')
conn.commit()

# GUI setup
root = tk.Tk()
root.title("Resident Information")

# Data Entry Section
tk.Label(root, text="Resident Name").place(x=20, y=20)
name_entry = tk.Entry(root)
name_entry.place(x=150, y=20)

tk.Label(root, text="Apartment Number").place(x=20, y=60)
apartment_entry = tk.Entry(root)
apartment_entry.place(x=150, y=60)

tk.Label(root, text="Phone Number").place(x=20, y=100)
phone_entry = tk.Entry(root)
phone_entry.place(x=150, y=100)

checkbuttons = []
for i in range(1, 13):
    var = tk.IntVar()
    checkbuttons.append(var)
    tk.Checkbutton(root, text=str(i), variable=var).place(x=20 + (i-1) % 6 * 50, y=140 + (i-1) // 6 * 30)

def submit():
    name = name_entry.get()
    apartment = apartment_entry.get()
    phone = phone_entry.get()
    selected_options = [str(i + 1) for i, var in enumerate(checkbuttons) if var.get()]

    if not phone.isdigit():
        messagebox.showerror("Error", "Phone number must be digits only.")
        return

    c.execute("SELECT * FROM residents WHERE LOWER(name) = ? OR LOWER(apartment) = ?", (name.lower(), apartment.lower()))
    existing_record = c.fetchone()
    if existing_record:
        c.execute("DELETE FROM residents WHERE name = ? OR apartment = ?", (existing_record[0], existing_record[1]))

    c.execute("INSERT INTO residents (name, apartment, phone, options) VALUES (?, ?, ?, ?)", (name, apartment, phone, ','.join(selected_options)))
    conn.commit()
    update_treeview()

def update_treeview():
    for row in tree.get_children():
        tree.delete(row)
    c.execute("SELECT * FROM residents")
    for record in c.fetchall():
        tree.insert("", "end", values=record)

tk.Button(root, text="Submit", command=submit).place(x=20, y=300)

# Search Section
tk.Label(root, text="Search Resident Name").place(x=400, y=20)
search_name_entry = tk.Entry(root)
search_name_entry.place(x=550, y=20)

tk.Label(root, text="Search Apartment Number").place(x=400, y=60)
search_apartment_entry = tk.Entry(root)
search_apartment_entry.place(x=550, y=60)

def search():
    name = search_name_entry.get()
    apartment = search_apartment_entry.get()

    if name:
        c.execute("SELECT apartment, options FROM residents WHERE LOWER(name) = ?", (name.lower(),))
        result = c.fetchone()
        if result:
            messagebox.showinfo("Search Result", f"Apartment: {result[0]}, Selected Options: {result[1]}")
        else:
            messagebox.showinfo("Search Result", "No record found.")
    elif apartment:
        c.execute("SELECT name, options FROM residents WHERE LOWER(apartment) = ?", (apartment.lower(),))
        result = c.fetchone()
        if result:
            messagebox.showinfo("Search Result", f"Resident: {result[0]}, Selected Options: {result[1]}")
        else:
            messagebox.showinfo("Search Result", "No record found.")

tk.Button(root, text="Search", command=search).place(x=400, y=100)

# Data Display
tree = ttk.Treeview(root, columns=("Name", "Apartment", "Phone", "Options"), show='headings')
tree.heading("Name", text="Resident Name")
tree.heading("Apartment", text="Apartment Number")
tree.heading("Phone", text="Phone Number")
tree.heading("Options", text="Selected Options")
tree.place(x=150, y=300, width=1000, height=700)

update_treeview()

root.mainloop()
conn.close()
