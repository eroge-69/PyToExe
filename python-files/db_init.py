# db_init.py
import sqlite3
from datetime import datetime

def init_db(path="planning.db"):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        brand TEXT,
        initial_qty REAL,
        min_qty REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        unit TEXT,
        initial_qty REAL,
        min_qty REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS packing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        initial_qty REAL,
        min_qty REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS product_tech (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        material_id INTEGER,
        qty_per_unit REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS product_pack (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        pack_id INTEGER,
        qty_per_unit INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_date TEXT,
        invoice_no TEXT,
        customer TEXT,
        product_id INTEGER,
        brand TEXT,
        qty REAL,
        status TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS mos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        product_id INTEGER,
        brand TEXT,
        qty REAL,
        suggested_silo TEXT,
        status TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS qc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mo_id INTEGER,
        sample_date TEXT,
        result TEXT,
        notes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mo_id INTEGER,
        product_id INTEGER,
        batch TEXT,
        qty REAL,
        silo TEXT,
        start_time TEXT,
        end_time TEXT,
        status TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ship_date TEXT,
        customer TEXT,
        invoice_no TEXT,
        product_id INTEGER,
        qty REAL,
        driver TEXT,
        plate TEXT,
        notes TEXT
    )""")
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", ('امیری','shimi2025','planner'))
        c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", ('روحانی زاده','shimi2025','planner'))
    except:
        pass
    try:
        c.executemany("INSERT INTO products (name,brand,initial_qty,min_qty) VALUES (?,?,?,?)", [
            ('سم نمونه','برند X',300,50),
            ('علف‌کش X','برند A',120,30),
            ('حشره‌کش Y','برند B',0,20),
        ])
    except:
        pass
    try:
        c.executemany("INSERT INTO materials (name,unit,initial_qty,min_qty) VALUES (?,?,?,?)", [
            ('A','kg',10000,500),
            ('B','kg',8000,400),
        ])
    except:
        pass
    try:
        c.executemany("INSERT INTO packing (name,initial_qty,min_qty) VALUES (?,?,?)", [
            ('بطری',1000,200),
            ('درب',1000,200),
            ('لیبل',2000,500),
            ('کارتن',500,100),
            ('نایلون شیرینگ',1000,200),
        ])
    except:
        pass
    try:
        c.executemany("INSERT INTO product_tech (product_id,material_id,qty_per_unit) VALUES (?,?,?)", [
            (1,1,2.0),
            (2,1,5.0),
            (3,1,1.5),
        ])
    except:
        pass
    try:
        c.executemany("INSERT INTO product_pack (product_id,pack_id,qty_per_unit) VALUES (?,?,?)", [
            (1,1,1),(1,2,1),(1,3,1),(1,4,1),(1,5,1),
            (2,1,1),(2,2,1),(2,3,1),(2,4,1),(2,5,1),
            (3,1,1),(3,2,1),(3,3,1),(3,4,1),(3,5,1),
        ])
    except:
        pass
    conn.commit()
    conn.close()
    print("DB initialized at", path)

if __name__ == "__main__":
    init_db("planning.db")
