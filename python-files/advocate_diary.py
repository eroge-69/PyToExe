import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

# Database setup
def init_db():
    conn = sqlite3.connect('advocate_diary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 case_number TEXT,
                 client_name TEXT,
                 case_type TEXT,
                 court_name TEXT,
                 hearing_date TEXT,
                 case_status TEXT
                 )''')
    conn.commit()
    conn.close()

# Main application window
class AdvocateDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advocate Diary")
        self.root.geometry("800x600")

        # Initialize database
        init_db()

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Case input fields
        ttk.Label(self.main_frame, text="Case Number:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.case_number = ttk.Entry(self.main_frame)
        self.case_number.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.main_frame, text="Client Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.client_name = ttk.Entry(self.main_frame)
        self.client_name.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.main_frame, text="Case Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.case_type = ttk.Entry(self.main_frame)
        self.case_type.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.main_frame, text="Court Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.court_name = ttk.Entry(self.main_frame)
        self.court_name.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.main_frame, text="Hearing Date (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.hearing_date = ttk.Entry(self.main_frame)
        self.hearing_date.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.main_frame, text="Case Status:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.case_status = ttk.Combobox(self.main_frame, values=["Running", "Closed"])
        self.case_status.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        self.case_status.set("Running")

        # Buttons
        ttk.Button(self.main_frame, text="Add Case", command=self.add_case).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(self.main_frame, text="View Cases", command=self.view_cases).grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(self.main_frame, text="Clear Fields", command=self.clear_fields).grid(row=8, column=0, columnspan=2, pady=10)

        # Treeview for displaying cases
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Case Number", "Client Name", "Case Type", "Court Name", "Hearing Date", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Case Number", text="Case Number")
        self.tree.heading("Client Name", text="Client Name")
        self.tree.heading("Case Type", text="Case Type")
        self.tree.heading("Court Name", text="Court Name")
        self.tree.heading("Hearing Date", text="Hearing Date")
        self.tree.heading("Status", text="Status")
        self.tree.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind("<Double-1>", self.on_double_click)

    def add_case(self):
        case_number = self.case_number.get()
        client_name = self.client_name.get()
        case_type = self.case_type.get()
        court_name = self.court_name.get()
        hearing_date = self.hearing_date.get()
        case_status = self.case_status.get()

        if not all([case_number, client_name, case_type, court_name, hearing_date, case_status]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            datetime.strptime(hearing_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
            return

        conn = sqlite3.connect('advocate_diary.db')
        c = conn.cursor()
        c.execute("INSERT INTO cases (case_number, client_name, case_type, court_name, hearing_date, case_status) VALUES (?, ?, ?, ?, ?, ?)",
                  (case_number, client_name, case_type, court_name, hearing_date, case_status))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Case added successfully!")
        self.clear_fields()
        self.view_cases()

    def view_cases(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect('advocate_diary.db')
        c = conn.cursor()
        c.execute("SELECT * FROM cases")
        rows = c.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def clear_fields(self):
        self.case_number.delete(0, tk.END)
        self.client_name.delete(0, tk.END)
        self.case_type.delete(0, tk.END)
        self.court_name.delete(0, tk.END)
        self.hearing_date.delete(0, tk.END)
        self.case_status.set("Running")

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        self.case_number.delete(0, tk.END)
        self.case_number.insert(0, values[1])
        self.client_name.delete(0, tk.END)
        self.client_name.insert(0, values[2])
        self.case_type.delete(0, tk.END)
        self.case_type.insert(0, values[3])
        self.court_name.delete(0, tk.END)
        self.court_name.insert(0, values[4])
        self.hearing_date.delete(0, tk.END)
        self.hearing_date.insert(0, values[5])
        self.case_status.set(values[6])

        ttk.Button(self.main_frame, text="Update Case", command=lambda: self.update_case(values[0])).grid(row=6, column=1, pady=10)

    def update_case(self, case_id):
        case_number = self.case_number.get()
        client_name = self.client_name.get()
        case_type = self.case_type.get()
        court_name = self.court_name.get()
        hearing_date = self.hearing_date.get()
        case_status = self.case_status.get()

        if not all([case_number, client_name, case_type, court_name, hearing_date, case_status]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            datetime.strptime(hearing_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
            return

        conn = sqlite3.connect('advocate_diary.db')
        c = conn.cursor()
        c.execute("UPDATE cases SET case_number=?, client_name=?, case_type=?, court_name=?, hearing_date=?, case_status=? WHERE id=?",
                  (case_number, client_name, case_type, court_name, hearing_date, case_status, case_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Case updated successfully!")
        self.clear_fields()
        self.view_cases()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvocateDiaryApp(root)
    root.mainloop()