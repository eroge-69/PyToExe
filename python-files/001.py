import sqlite3
from datetime import datetime
import os, sys

# ---------- Database Path (works in .exe too) ----------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # when running as exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stock_management.db")

# ---------- Connect to SQLite ----------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ---------- Create Tables ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    quantity INTEGER,
    date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS consumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    quantity INTEGER,
    customer_name TEXT,
    area TEXT,
    date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS faulty_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    quantity INTEGER,
    remarks TEXT,
    date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS issued_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    quantity INTEGER,
    customer_name TEXT,
    area TEXT,
    date TEXT
)
""")

conn.commit()

# ---------- Functions ----------
def add_incoming_stock():
    item = input("Enter item name: ")
    qty = int(input("Enter quantity received: "))
    cur.execute("INSERT INTO stock (item_name, quantity, date) VALUES (?, ?, ?)",
                (item, qty, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    print("Incoming stock added successfully!\n")

def consume_stock():
    item = input("Enter item name: ")
    qty = int(input("Enter quantity consumed: "))
    customer = input("Enter customer name: ")
    area = input("Enter area: ")
    cur.execute("INSERT INTO consumption (item_name, quantity, customer_name, area, date) VALUES (?, ?, ?, ?, ?)",
                (item, qty, customer, area, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    print("Stock consumption recorded!\n")

def add_faulty_stock():
    item = input("Enter faulty item name: ")
    qty = int(input("Enter faulty quantity: "))
    remarks = input("Enter remarks: ")
    cur.execute("INSERT INTO faulty_stock (item_name, quantity, remarks, date) VALUES (?, ?, ?, ?)",
                (item, qty, remarks, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    print("Faulty stock recorded!\n")

def issue_stock():
    item = input("Enter item name: ")
    qty = int(input("Enter quantity issued: "))
    customer = input("Enter customer name: ")
    area = input("Enter area: ")
    cur.execute("INSERT INTO issued_stock (item_name, quantity, customer_name, area, date) VALUES (?, ?, ?, ?, ?)",
                (item, qty, customer, area, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    print("Stock issued successfully!\n")

# ---------- Reports ----------
def report_datewise():
    date = input("Enter date (YYYY-MM-DD): ")
    cur.execute("SELECT * FROM issued_stock WHERE date=?", (date,))
    rows = cur.fetchall()
    print(f"\n--- Date-wise Report for {date} ---")
    for row in rows:
        print(row)
    print()

def report_customerwise():
    customer = input("Enter customer name: ")
    cur.execute("SELECT * FROM issued_stock WHERE customer_name=?", (customer,))
    rows = cur.fetchall()
    print(f"\n--- Customer-wise Report for {customer} ---")
    for row in rows:
        print(row)
    print()

def report_areawise():
    area = input("Enter area: ")
    cur.execute("SELECT * FROM issued_stock WHERE area=?", (area,))
    rows = cur.fetchall()
    print(f"\n--- Area-wise Report for {area} ---")
    for row in rows:
        print(row)
    print()

# ---------- Main Menu ----------
def main_menu():
    while True:
        print("""
========= STOCK MANAGEMENT =========
1. Add Incoming Stock
2. Record Consumption
3. Record Faulty Stock
4. Issue Stock
5. Reports
6. Exit
""")
        choice = input("Enter choice: ")

        if choice == "1":
            add_incoming_stock()
        elif choice == "2":
            consume_stock()
        elif choice == "3":
            add_faulty_stock()
        elif choice == "4":
            issue_stock()
        elif choice == "5":
            print("""
--- REPORT MENU ---
1. Date-wise Report
2. Customer-wise Report
3. Area-wise Report
""")
            rpt = input("Enter choice: ")
            if rpt == "1":
                report_datewise()
            elif rpt == "2":
                report_customerwise()
            elif rpt == "3":
                report_areawise()
        elif choice == "6":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice, try again.\n")

# ---------- Run ----------
if __name__ == "__main__":
    main_menu()
