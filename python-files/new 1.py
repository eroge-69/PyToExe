import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect("stock_management.db")
cur = conn.cursor()

# Create tables
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

# Functions
def add_incoming_stock(item, qty):
    cur.execute("INSERT INTO stock (item_name, quantity, date) VALUES (?, ?, ?)",
                (item, qty, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

def consume_stock(item, qty, customer, area):
    cur.execute("INSERT INTO consumption (item_name, quantity, customer_name, area, date) VALUES (?, ?, ?, ?, ?)",
                (item, qty, customer, area, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

def add_faulty_stock(item, qty, remarks):
    cur.execute("INSERT INTO faulty_stock (item_name, quantity, remarks, date) VALUES (?, ?, ?, ?)",
                (item, qty, remarks, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

def issue_stock(item, qty, customer, area):
    cur.execute("INSERT INTO issued_stock (item_name, quantity, customer_name, area, date) VALUES (?, ?, ?, ?, ?)",
                (item, qty, customer, area, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

# Reports
def report_datewise(date):
    cur.execute("SELECT * FROM issued_stock WHERE date=?", (date,))
    return cur.fetchall()

def report_customerwise(customer):
    cur.execute("SELECT * FROM issued_stock WHERE customer_name=?", (customer,))
    return cur.fetchall()

def report_areawise(area):
    cur.execute("SELECT * FROM issued_stock WHERE area=?", (area,))
    return cur.fetchall()

# Example usage
if __name__ == "__main__":
    # Add records
    add_incoming_stock("Bearing", 100)
    consume_stock("Bearing", 10, "ABC Ltd", "Delhi")
    add_faulty_stock("Bearing", 2, "Damaged in transport")
    issue_stock("Bearing", 5, "XYZ Pvt Ltd", "Mumbai")

    # Reports
    print("\n--- Date-wise Report ---")
    print(report_datewise(datetime.now().strftime("%Y-%m-%d")))

    print("\n--- Customer-wise Report (ABC Ltd) ---")
    print(report_customerwise("ABC Ltd"))

    print("\n--- Area-wise Report (Mumbai) ---")
    print(report_areawise("Mumbai"))
