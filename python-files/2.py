Python 3.13.0 (tags/v3.13.0:60403a5, Oct  7 2024, 09:38:07) [MSC v.1941 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# --- Βάση δεδομένων ---
conn = sqlite3.connect("dance_school_erp.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_name TEXT,
    phone TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount REAL,
    method TEXT,
    date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()

# --- GUI ---
class DanceSchoolERP(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dance School ERP")
        self.geometry("600x400")

        tab_control = ttk.Notebook(self)
        self.tab_students = ttk.Frame(tab_control)
        self.tab_payments = ttk.Frame(tab_control)

        tab_control.add(self.tab_students, text="Μαθητές")
        tab_control.add(self.tab_payments, text="Πληρωμές")
        tab_control.pack(expand=1, fill="both")

        self.create_students_tab()
        self.create_payments_tab()

    def create_students_tab(self):
        frame = self.tab_students

        # Φόρμα εισαγωγής μαθητή
        form = ttk.Frame(frame)
        form.pack(pady=10, padx=10, fill="x")

        ttk.Label(form, text="Όνομα Μαθητή:").grid(row=0, column=0, sticky="w")
        self.entry_name = ttk.Entry(form)
        self.entry_name.grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Όνομα Γονέα:").grid(row=1, column=0, sticky="w")
        self.entry_parent = ttk.Entry(form)
        self.entry_parent.grid(row=1, column=1, sticky="ew")

        ttk.Label(form, text="Τηλέφωνο:").grid(row=2, column=0, sticky="w")
        self.entry_phone = ttk.Entry(form)
        self.entry_phone.grid(row=2, column=1, sticky="ew")

        btn_add = ttk.Button(form, text="Προσθήκη Μαθητή", command=self.add_student)
        btn_add.grid(row=3, column=0, columnspan=2, pady=5)

        form.columnconfigure(1, weight=1)

        # Πίνακας μαθητών
        self.tree_students = ttk.Treeview(frame, columns=("id", "name", "parent", "phone"), show="headings")
        self.tree_students.heading("id", text="ID")
        self.tree_students.column("id", width=30)
        self.tree_students.heading("name", text="Όνομα Μαθητή")
        self.tree_students.heading("parent", text="Όνομα Γονέα")
        self.tree_students.heading("phone", text="Τηλέφωνο")
        self.tree_students.pack(expand=1, fill="both", padx=10, pady=10)

        self.load_students()

    def create_payments_tab(self):
        frame = self.tab_payments

        form = ttk.Frame(frame)
        form.pack(pady=10, padx=10, fill="x")

        ttk.Label(form, text="Μαθητής (ID):").grid(row=0, column=0, sticky="w")
        self.entry_student_id = ttk.Entry(form)
        self.entry_student_id.grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Ποσό:").grid(row=1, column=0, sticky="w")
        self.entry_amount = ttk.Entry(form)
        self.entry_amount.grid(row=1, column=1, sticky="ew")

        ttk.Label(form, text="Τρόπος Πληρωμής:").grid(row=2, column=0, sticky="w")
        self.entry_method = ttk.Entry(form)
        self.entry_method.grid(row=2, column=1, sticky="ew")

        ttk.Label(form, text="Ημερομηνία (π.χ. 2025-06-12):").grid(row=3, column=0, sticky="w")
        self.entry_date = ttk.Entry(form)
        self.entry_date.grid(row=3, column=1, sticky="ew")

        btn_add = ttk.Button(form, text="Καταχώρηση Πληρωμής", command=self.add_payment)
        btn_add.grid(row=4, column=0, columnspan=2, pady=5)

        form.columnconfigure(1, weight=1)

        # Πίνακας πληρωμών
        self.tree_payments = ttk.Treeview(frame, columns=("id", "student_id", "amount", "method", "date"), show="headings")
        self.tree_payments.heading("id", text="ID")
        self.tree_payments.column("id", width=30)
        self.tree_payments.heading("student_id", text="ID Μαθητή")
        self.tree_payments.heading("amount", text="Ποσό")
        self.tree_payments.heading("method", text="Τρόπος Πληρωμής")
        self.tree_payments.heading("date", text="Ημερομηνία")
        self.tree_payments.pack(expand=1, fill="both", padx=10, pady=10)

        self.load_payments()

    def add_student(self):
        name = self.entry_name.get().strip()
        parent = self.entry_parent.get().strip()
        phone = self.entry_phone.get().strip()

        if not name:
            messagebox.showwarning("Σφάλμα", "Το όνομα μαθητή είναι υποχρεωτικό!")
            return

        cur.execute("INSERT INTO students (name, parent_name, phone) VALUES (?, ?, ?)", (name, parent, phone))
        conn.commit()
        self.load_students()

        self.entry_name.delete(0, tk.END)
        self.entry_parent.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

    def load_students(self):
        for row in self.tree_students.get_children():
            self.tree_students.delete(row)
        for row in cur.execute("SELECT id, name, parent_name, phone FROM students ORDER BY id"):
            self.tree_students.insert("", tk.END, values=row)

    def add_payment(self):
        try:
...             student_id = int(self.entry_student_id.get().strip())
...             amount = float(self.entry_amount.get().strip())
...         except ValueError:
...             messagebox.showwarning("Σφάλμα", "Το ID μαθητή και το ποσό πρέπει να είναι αριθμοί!")
...             return
...         method = self.entry_method.get().strip()
...         date = self.entry_date.get().strip()
... 
...         # Έλεγχος αν υπάρχει μαθητής με το ID
...         cur.execute("SELECT id FROM students WHERE id = ?", (student_id,))
...         if not cur.fetchone():
...             messagebox.showwarning("Σφάλμα", "Δεν βρέθηκε μαθητής με το συγκεκριμένο ID!")
...             return
... 
...         cur.execute("INSERT INTO payments (student_id, amount, method, date) VALUES (?, ?, ?, ?)",
...                     (student_id, amount, method, date))
...         conn.commit()
...         self.load_payments()
... 
...         self.entry_student_id.delete(0, tk.END)
...         self.entry_amount.delete(0, tk.END)
...         self.entry_method.delete(0, tk.END)
...         self.entry_date.delete(0, tk.END)
... 
...     def load_payments(self):
...         for row in self.tree_payments.get_children():
...             self.tree_payments.delete(row)
...         for row in cur.execute("SELECT id, student_id, amount, method, date FROM payments ORDER BY id"):
...             self.tree_payments.insert("", tk.END, values=row)
... 
... if __name__ == "__main__":
...     app = DanceSchoolERP()
...     app.mainloop()
... 
... conn.close()
