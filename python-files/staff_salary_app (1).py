# This script is intended to be run in a local Python environment that supports tkinter.
# If tkinter is not available (e.g. in certain sandboxed environments), GUI will not work.

import sqlite3
import sys
from datetime import date

# Check tkinter availability
try:
    from tkinter import *
    from tkinter import ttk
    tkinter_available = True
except ModuleNotFoundError:
    tkinter_available = False

# Database Setup
def init_db():
    conn = sqlite3.connect("staff_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        designation TEXT,
        daily_salary REAL,
        join_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER,
        date TEXT,
        status TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS advance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER,
        date TEXT,
        amount REAL,
        remarks TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS deduction (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER,
        date TEXT,
        amount REAL,
        reason TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS emolument (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER,
        date TEXT,
        amount REAL,
        type TEXT,
        remarks TEXT
    )''')

    conn.commit()
    conn.close()

# GUI Setup
if tkinter_available:
    class StaffApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Staff Management App")
            self.root.geometry("800x600")

            self.tabControl = ttk.Notebook(root)

            self.staff_tab = Frame(self.tabControl)
            self.tabControl.add(self.staff_tab, text='Staff')
            self.tabControl.pack(expand=1, fill="both")

            self.build_staff_tab()

        def build_staff_tab(self):
            Label(self.staff_tab, text="Name:").grid(row=0, column=0)
            self.name_entry = Entry(self.staff_tab)
            self.name_entry.grid(row=0, column=1)

            Label(self.staff_tab, text="Designation:").grid(row=1, column=0)
            self.designation_entry = Entry(self.staff_tab)
            self.designation_entry.grid(row=1, column=1)

            Label(self.staff_tab, text="Daily Salary:").grid(row=2, column=0)
            self.salary_entry = Entry(self.staff_tab)
            self.salary_entry.grid(row=2, column=1)

            Label(self.staff_tab, text="Join Date (YYYY-MM-DD):").grid(row=3, column=0)
            self.join_date_entry = Entry(self.staff_tab)
            self.join_date_entry.grid(row=3, column=1)

            Button(self.staff_tab, text="Add Staff", command=self.add_staff).grid(row=4, column=0, columnspan=2)

        def add_staff(self):
            name = self.name_entry.get()
            designation = self.designation_entry.get()
            try:
                salary = float(self.salary_entry.get())
            except ValueError:
                print("Invalid salary input. Please enter a numeric value.")
                return

            join_date = self.join_date_entry.get()

            conn = sqlite3.connect("staff_data.db")
            c = conn.cursor()
            c.execute("INSERT INTO staff (name, designation, daily_salary, join_date) VALUES (?, ?, ?, ?)",
                      (name, designation, salary, join_date))
            conn.commit()
            conn.close()

            self.name_entry.delete(0, END)
            self.designation_entry.delete(0, END)
            self.salary_entry.delete(0, END)
            self.join_date_entry.delete(0, END)
            print("Staff Added")

# Entry Point
if __name__ == '__main__':
    init_db()
    if tkinter_available:
        root = Tk()
        app = StaffApp(root)
        root.mainloop()
    else:
        print("tkinter is not available in this environment. GUI will not be displayed.")
