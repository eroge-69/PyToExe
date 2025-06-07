Python 3.13.4 (tags/v3.13.4:8a526ec, Jun  3 2025, 17:46:04) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database setup
conn = sqlite3.connect("pankaj_jewellers.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS borrowers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        borrower_id INTEGER,
        amount REAL,
        interest_rate REAL,
        duration_months INTEGER,
        description TEXT,
        weight REAL,
        FOREIGN KEY(borrower_id) REFERENCES borrowers(id)
    )
''')
... conn.commit()
... conn.close()
... 
... # GUI setup
... root = tk.Tk()
... root.title("Pankaj Jewellers - गहना गिरवी प्रबंधन")
... 
... # Functions
... def add_borrower():
...     name = entry_name.get()
...     mobile = entry_mobile.get()
...     if name and mobile:
...         conn = sqlite3.connect("pankaj_jewellers.db")
...         cursor = conn.cursor()
...         cursor.execute("INSERT INTO borrowers (name, mobile) VALUES (?, ?)", (name, mobile))
...         conn.commit()
...         conn.close()
...         messagebox.showinfo("सफलता", "उधारकर्ता जोड़ा गया")
...         entry_name.delete(0, tk.END)
...         entry_mobile.delete(0, tk.END)
...     else:
...         messagebox.showerror("त्रुटि", "कृपया सभी फ़ील्ड भरें")
... 
... # UI layout
... frame = ttk.Frame(root, padding=20)
... frame.grid()
... 
... ttk.Label(frame, text="नाम:").grid(column=0, row=0, sticky=tk.W)
... entry_name = ttk.Entry(frame, width=30)
... entry_name.grid(column=1, row=0)
... 
... ttk.Label(frame, text="मोबाइल नंबर:").grid(column=0, row=1, sticky=tk.W)
... entry_mobile = ttk.Entry(frame, width=30)
... entry_mobile.grid(column=1, row=1)
... 
... add_button = ttk.Button(frame, text="उधारकर्ता जोड़ें", command=add_borrower)
... add_button.grid(column=0, row=2, columnspan=2, pady=10)
... 
