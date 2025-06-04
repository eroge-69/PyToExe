# Non-interactive Mobile Store App using predefined sample data
# No webcam or user input required

import sqlite3
from datetime import datetime

# Sample data (replace or extend as needed)
sample_entries = [
    {
        "company": "Samsung",
        "model": "Galaxy S23",
        "imei": "123456789012345",
        "color": "Black",
        "ram": "8GB",
        "rom": "256GB",
        "camera": "108MP"
    },
    {
        "company": "Apple",
        "model": "iPhone 14",
        "imei": "987654321098765",
        "color": "Blue",
        "ram": "6GB",
        "rom": "128GB",
        "camera": "12MP"
    }
]

# Database setup
conn = sqlite3.connect('mobile_store.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS mobiles (
    id INTEGER PRIMARY KEY,
    entry_time TEXT,
    company TEXT,
    model TEXT,
    imei TEXT,
    color TEXT,
    ram TEXT,
    rom TEXT,
    camera TEXT
)''')
conn.commit()

# Add mobile to database
def add_mobile(entry):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO mobiles (entry_time, company, model, imei, color, ram, rom, camera)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (time_now, entry['company'], entry['model'], entry['imei'], entry['color'], entry['ram'], entry['rom'], entry['camera']))
    conn.commit()
    print(f"Saved: {entry['company']} {entry['model']} with IMEI {entry['imei']}")

# Main execution
if __name__ == '__main__':
    for entry in sample_entries:
        add_mobile(entry)

conn.close()
print("Database connection closed.")
