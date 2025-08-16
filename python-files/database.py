import sqlite3

def connect_db():
    """Creates a connection to the SQLite database and sets up tables if they don't exist."""
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()

    # Create MenuItems table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MenuItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)

    # Create Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_amount REAL NOT NULL,
        gst REAL NOT NULL,
        grand_total REAL NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create OrderItems table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OrderItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item_name TEXT,
        quantity INTEGER,
        price REAL,
        subtotal REAL,
        FOREIGN KEY (order_id) REFERENCES Orders(id)
    )
    """)

    conn.commit()
    return conn

def add_menu_item(name, category, price):
    """Adds a new item to the menu."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO MenuItems (name, category, price) VALUES (?, ?, ?)", 
                       (name, category, price))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # This error occurs if the item name already exists
        return False

def get_menu_items():
    """Fetches all items from the menu."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, category, price FROM MenuItems ORDER BY category, name")
    items = cursor.fetchall()
    conn.close()
    return items

def get_item_price(name):
    """Gets the price of a specific menu item."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM MenuItems WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_order(total_amount, gst, grand_total, order_items):
    """Saves the final bill and its items to the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Insert into Orders table
    cursor.execute("INSERT INTO Orders (total_amount, gst, grand_total) VALUES (?, ?, ?)",
                   (total_amount, gst, grand_total))
    order_id = cursor.lastrowid

    # Insert into OrderItems table
    for item in order_items:
        cursor.execute("""
        INSERT INTO OrderItems (order_id, item_name, quantity, price, subtotal) 
        VALUES (?, ?, ?, ?, ?)
        """, (order_id, item['name'], item['quantity'], item['price'], item['subtotal']))
    
    conn.commit()
    conn.close()
    return order_id