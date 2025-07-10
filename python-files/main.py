
import tkinter as tk
from tkinter import messagebox
import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a sample table
cursor.execute('''CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    truck_no TEXT,
    driver TEXT,
    party TEXT,
    loading_point TEXT,
    unloading_point TEXT,
    material TEXT,
    km INTEGER,
    bags INTEGER,
    quantity REAL,
    rate REAL,
    amount REAL
)''')
conn.commit()

# Main application
def save_entry():
    data = (date_entry.get(), truck_entry.get(), driver_entry.get(), party_entry.get(),
            loading_entry.get(), unloading_entry.get(), material_entry.get(),
            km_entry.get(), bags_entry.get(), quantity_entry.get(), rate_entry.get(),
            float(quantity_entry.get()) * float(rate_entry.get()))
    cursor.execute('INSERT INTO trips (date, truck_no, driver, party, loading_point, unloading_point, material, km, bags, quantity, rate, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
    conn.commit()
    messagebox.showinfo("Success", "Trip saved!")

app = tk.Tk()
app.title("Transport Management Software")

tk.Label(app, text="Date").grid(row=0, column=0)
tk.Label(app, text="Truck No").grid(row=1, column=0)
tk.Label(app, text="Driver").grid(row=2, column=0)
tk.Label(app, text="Party").grid(row=3, column=0)
tk.Label(app, text="Loading").grid(row=4, column=0)
tk.Label(app, text="Unloading").grid(row=5, column=0)
tk.Label(app, text="Material").grid(row=6, column=0)
tk.Label(app, text="KM").grid(row=7, column=0)
tk.Label(app, text="Bags").grid(row=8, column=0)
tk.Label(app, text="Quantity").grid(row=9, column=0)
tk.Label(app, text="Rate").grid(row=10, column=0)

date_entry = tk.Entry(app)
truck_entry = tk.Entry(app)
driver_entry = tk.Entry(app)
party_entry = tk.Entry(app)
loading_entry = tk.Entry(app)
unloading_entry = tk.Entry(app)
material_entry = tk.Entry(app)
km_entry = tk.Entry(app)
bags_entry = tk.Entry(app)
quantity_entry = tk.Entry(app)
rate_entry = tk.Entry(app)

date_entry.grid(row=0, column=1)
truck_entry.grid(row=1, column=1)
driver_entry.grid(row=2, column=1)
party_entry.grid(row=3, column=1)
loading_entry.grid(row=4, column=1)
unloading_entry.grid(row=5, column=1)
material_entry.grid(row=6, column=1)
km_entry.grid(row=7, column=1)
bags_entry.grid(row=8, column=1)
quantity_entry.grid(row=9, column=1)
rate_entry.grid(row=10, column=1)

tk.Button(app, text="Save Trip", command=save_entry).grid(row=11, columnspan=2)

app.mainloop()
