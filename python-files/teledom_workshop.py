
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

def create_db():
    conn = sqlite3.connect('teledom_workshop.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        phone_number TEXT,
        address TEXT
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        name TEXT,
        serial_number TEXT,
        screen_size REAL
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS repairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        equipment_id INTEGER,
        repair_description TEXT,
        technician TEXT,
        repair_date TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id),
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
    )''')
    conn.commit()
    conn.close()

def add_client():
    full_name = entry_name.get()
    phone_number = entry_phone.get()
    address = entry_address.get()
    if full_name and phone_number and address:
        conn = sqlite3.connect('teledom_workshop.db')
        c = conn.cursor()
        c.execute('''
        INSERT INTO clients (full_name, phone_number, address)
        VALUES (?, ?, ?)''', (full_name, phone_number, address))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Client added successfully!")
        update_client_list()

def add_equipment():
    model = entry_model.get()
    name = entry_name.get()
    serial_number = entry_serial.get()
    screen_size = entry_screen_size.get()
    if model and name and serial_number and screen_size:
        conn = sqlite3.connect('teledom_workshop.db')
        c = conn.cursor()
        c.execute('''
        INSERT INTO equipment (model, name, serial_number, screen_size)
        VALUES (?, ?, ?, ?)''', (model, name, serial_number, screen_size))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Equipment added successfully!")
        update_equipment_list()

def update_client_list():
    conn = sqlite3.connect('teledom_workshop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clients")
    rows = c.fetchall()
    for row in client_treeview.get_children():
        client_treeview.delete(row)
    for row in rows:
        client_treeview.insert("", "end", values=row)
    conn.close()

def update_equipment_list():
    conn = sqlite3.connect('teledom_workshop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM equipment")
    rows = c.fetchall()
    for row in equipment_treeview.get_children():
        equipment_treeview.delete(row)
    for row in rows:
        equipment_treeview.insert("", "end", values=row)
    conn.close()

def search_client():
    query = entry_search_client.get()
    conn = sqlite3.connect('teledom_workshop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clients WHERE full_name LIKE ?", ('%' + query + '%',))
    rows = c.fetchall()
    for row in client_treeview.get_children():
        client_treeview.delete(row)
    for row in rows:
        client_treeview.insert("", "end", values=row)
    conn.close()

def search_equipment():
    query = entry_search_equipment.get()
    conn = sqlite3.connect('teledom_workshop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM equipment WHERE model LIKE ?", ('%' + query + '%',))
    rows = c.fetchall()
    for row in equipment_treeview.get_children():
        equipment_treeview.delete(row)
    for row in rows:
        equipment_treeview.insert("", "end", values=row)
    conn.close()

root = tk.Tk()
root.title("ТелеДом Мастерская")
root.geometry("800x600")
root.config(bg="#f5f5f5")

frame_input = tk.Frame(root, bg="#f5f5f5")
frame_input.pack(pady=20)

tk.Label(frame_input, text="Full Name", bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5)
entry_name = tk.Entry(frame_input)
entry_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Phone Number", bg="#f5f5f5").grid(row=1, column=0, padx=10, pady=5)
entry_phone = tk.Entry(frame_input)
entry_phone.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Address", bg="#f5f5f5").grid(row=2, column=0, padx=10, pady=5)
entry_address = tk.Entry(frame_input)
entry_address.grid(row=2, column=1, padx=10, pady=5)

tk.Button(frame_input, text="Add Client", command=add_client).grid(row=3, column=1, padx=10, pady=10)

tk.Label(frame_input, text="Model", bg="#f5f5f5").grid(row=4, column=0, padx=10, pady=5)
entry_model = tk.Entry(frame_input)
entry_model.grid(row=4, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Name", bg="#f5f5f5").grid(row=5, column=0, padx=10, pady=5)
entry_name = tk.Entry(frame_input)
entry_name.grid(row=5, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Serial Number", bg="#f5f5f5").grid(row=6, column=0, padx=10, pady=5)
entry_serial = tk.Entry(frame_input)
entry_serial.grid(row=6, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Screen Size", bg="#f5f5f5").grid(row=7, column=0, padx=10, pady=5)
entry_screen_size = tk.Entry(frame_input)
entry_screen_size.grid(row=7, column=1, padx=10, pady=5)

tk.Button(frame_input, text="Add Equipment", command=add_equipment).grid(row=8, column=1, padx=10, pady=10)

frame_search_clients = tk.Frame(root, bg="#f5f5f5")
frame_search_clients.pack(pady=20)

tk.Label(frame_search_clients, text="Search Clients", bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5)
entry_search_client = tk.Entry(frame_search_clients)
entry_search_client.grid(row=0, column=1, padx=10, pady=5)

tk.Button(frame_search_clients, text="Search", command=search_client).grid(row=0, column=2, padx=10, pady=5)

frame_search_equipment = tk.Frame(root, bg="#f5f5f5")
frame_search_equipment.pack(pady=20)

tk.Label(frame_search_equipment, text="Search Equipment", bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5)
entry_search_equipment = tk.Entry(frame_search_equipment)
entry_search_equipment.grid(row=0, column=1, padx=10, pady=5)

tk.Button(frame_search_equipment, text="Search", command=search_equipment).grid(row=0, column=2, padx=10, pady=5)

frame_clients_list = tk.Frame(root, bg="#f5f5f5")
frame_clients_list.pack(pady=20)

client_treeview = ttk.Treeview(frame_clients_list, columns=("ID", "Full Name", "Phone Number", "Address"), show="headings")
client_treeview.heading("ID", text="ID")
client_treeview.heading("Full Name", text="Full Name")
client_treeview.heading("Phone Number", text="Phone Number")
client_treeview.heading("Address", text="Address")
client_treeview.pack()

frame_equipment_list = tk.Frame(root, bg="#f5f5f5")
frame_equipment_list.pack(pady=20)

equipment_treeview = ttk.Treeview(frame_equipment_list, columns=("ID", "Model", "Name", "Serial Number", "Screen Size"), show="headings")
equipment_treeview.heading("ID", text="ID")
equipment_treeview.heading("Model", text="Model")
equipment_treeview.heading("Name", text="Name")
equipment_treeview.heading("Serial Number", text="Serial Number")
equipment_treeview.heading("Screen Size", text="Screen Size")
equipment_treeview.pack()

update_client_list()
update_equipment_list()

root.mainloop()
