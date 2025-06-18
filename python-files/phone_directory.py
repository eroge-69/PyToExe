import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

# --- Constants ---
PASSWORD = "admin123"
FONT = ("Arial", 20)
DISTRICTS = [
    "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo",
    "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara",
    "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar",
    "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya",
    "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"
]

# --- Database Setup ---
conn = sqlite3.connect("contacts.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
    dealer_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    district TEXT,
    phone1 TEXT,
    phone2 TEXT
)''')
conn.commit()

# --- Functions ---
def clear_fields():
    for entry in [entry_code, entry_name, entry_phone1, entry_phone2]:
        entry.delete(0, tk.END)
    district_var.set("")

def add_contact():
    code = entry_code.get()
    name = entry_name.get()
    district = district_var.get()
    phone1 = entry_phone1.get()
    phone2 = entry_phone2.get()

    if not code or not name:
        messagebox.showerror("Error", "Dealer Code and Name are required")
        return
    try:
        cursor.execute("INSERT INTO contacts VALUES (?, ?, ?, ?, ?)", (code, name, district, phone1, phone2))
        conn.commit()
        messagebox.showinfo("Success", "Contact added successfully")
        view_contacts()
        clear_fields()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Dealer Code already exists")

def view_contacts():
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute("SELECT * FROM contacts ORDER BY dealer_code ASC")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

def search_contact():
    code = entry_code.get()
    cursor.execute("SELECT * FROM contacts WHERE dealer_code=?", (code,))
    result = cursor.fetchone()
    if result:
        entry_name.delete(0, tk.END)
        entry_name.insert(0, result[1])
        district_var.set(result[2])
        entry_phone1.delete(0, tk.END)
        entry_phone1.insert(0, result[3])
        entry_phone2.delete(0, tk.END)
        entry_phone2.insert(0, result[4])
    else:
        messagebox.showinfo("Not Found", "No contact found with that Dealer Code")

def update_contact():
    if not verify_password(): return
    code = entry_code.get()
    name = entry_name.get()
    district = district_var.get()
    phone1 = entry_phone1.get()
    phone2 = entry_phone2.get()
    cursor.execute("UPDATE contacts SET name=?, district=?, phone1=?, phone2=? WHERE dealer_code=?",
                   (name, district, phone1, phone2, code))
    conn.commit()
    messagebox.showinfo("Updated", "Contact updated successfully")
    view_contacts()

def verify_password():
    pw = simpledialog.askstring("Password Required", "Enter password:", show='*')
    if pw is None:
        return False
    if pw == PASSWORD:
        return True
    else:
        messagebox.showerror("Access Denied", "Incorrect password")
        return False

def delete_contact():
    if not verify_password():
        return
    code = entry_code.get()
    cursor.execute("DELETE FROM contacts WHERE dealer_code=?", (code,))
    conn.commit()
    messagebox.showinfo("Deleted", "Contact deleted successfully")
    view_contacts()
    clear_fields()

def focus_next(event):
    event.widget.tk_focusNext().focus()
    return "break"

def focus_prev(event):
    event.widget.tk_focusPrev().focus()
    return "break"

# --- UI ---
root = tk.Tk()
root.title("Contact Directory")

# Make full screen (Windows only)
root.state('zoomed')  # Use root.attributes('-fullscreen', True) for cross-platform full screen

# Allow exit on Esc key
root.bind("<Escape>", lambda e: root.quit())

# Labels & Entries
tk.Label(root, text="Dealer Code", font=FONT).grid(row=0, column=0, padx=10, pady=10, sticky='e')
entry_code = tk.Entry(root, font=FONT)
entry_code.grid(row=0, column=1, sticky='w')

tk.Label(root, text="Name", font=FONT).grid(row=1, column=0, padx=10, pady=10, sticky='e')
entry_name = tk.Entry(root, font=FONT)
entry_name.grid(row=1, column=1, sticky='w')

tk.Label(root, text="District", font=FONT).grid(row=2, column=0, padx=10, pady=10, sticky='e')
district_var = tk.StringVar()
combo_district = ttk.Combobox(root, textvariable=district_var, font=FONT, values=DISTRICTS, state='readonly')
combo_district.grid(row=2, column=1, sticky='w')

tk.Label(root, text="Phone 1", font=FONT).grid(row=3, column=0, padx=10, pady=10, sticky='e')
entry_phone1 = tk.Entry(root, font=FONT)
entry_phone1.grid(row=3, column=1, sticky='w')

tk.Label(root, text="Phone 2", font=FONT).grid(row=4, column=0, padx=10, pady=10, sticky='e')
entry_phone2 = tk.Entry(root, font=FONT)
entry_phone2.grid(row=4, column=1, sticky='w')

# Buttons
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=2, rowspan=6, padx=20, pady=10, sticky='n')

tk.Button(button_frame, text="Add", font=FONT, command=add_contact, width=10).pack(pady=5)
tk.Button(button_frame, text="Search", font=FONT, command=search_contact, width=10).pack(pady=5)
tk.Button(button_frame, text="Update", font=FONT, command=update_contact, width=10).pack(pady=5)
tk.Button(button_frame, text="Delete", font=FONT, command=delete_contact, width=10).pack(pady=5)
tk.Button(button_frame, text="View All", font=FONT, command=view_contacts, width=10).pack(pady=5)
tk.Button(button_frame, text="Exit", font=FONT, command=root.quit, width=10).pack(pady=5)

# Treeview
tree = ttk.Treeview(root, columns=("Code", "Name", "District", "Phone1", "Phone2"), show="headings", height=15)
tree.grid(row=6, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=180, anchor='center')

# Allow resizing
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(1, weight=1)

# Keyboard Navigation
for widget in [entry_code, entry_name, combo_district, entry_phone1, entry_phone2]:
    widget.bind("<Return>", focus_next)
    widget.bind("<Shift-Tab>", focus_prev)

# Load Initial Data
view_contacts()
root.mainloop()
