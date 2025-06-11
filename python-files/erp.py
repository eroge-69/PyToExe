Python 3.13.0 (tags/v3.13.0:60403a5, Oct  7 2024, 09:38:07) [MSC v.1941 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import sqlite3
from tkinter import *
from tkinter import messagebox

DB_FILE = 'dance_school.db'

def create_db():
...     conn = sqlite3.connect(DB_FILE)
...     c = conn.cursor()
...     c.execute('''
...         CREATE TABLE IF NOT EXISTS students (
...             id INTEGER PRIMARY KEY AUTOINCREMENT,
...             name TEXT NOT NULL,
...             parent TEXT NOT NULL
...         )
...     ''')
...     c.execute('''
...         CREATE TABLE IF NOT EXISTS payments (
...             id INTEGER PRIMARY KEY AUTOINCREMENT,
...             student_id INTEGER,
...             amount REAL,
...             method TEXT,
...             FOREIGN KEY(student_id) REFERENCES students(id)
...         )
...     ''')
...     conn.commit()
...     conn.close()
... 
... def add_student(name, parent):
...     conn = sqlite3.connect(DB_FILE)
...     c = conn.cursor()
...     c.execute("INSERT INTO students (name, parent) VALUES (?, ?)", (name, parent))
...     conn.commit()
...     conn.close()
... 
... def add_payment(student_id, amount, method):
...     conn = sqlite3.connect(DB_FILE)
...     c = conn.cursor()
...     c.execute("INSERT INTO payments (student_id, amount, method) VALUES (?, ?, ?)", (student_id, amount, method))
...     conn.commit()
...     conn.close()
... 
... def get_students():
...     conn = sqlite3.connect(DB_FILE)
...     c = conn.cursor()
    c.execute("SELECT id, name FROM students")
    students = c.fetchall()
    conn.close()
    return students

class DanceSchoolApp:
    def __init__(self, root):
        self.root = root
        root.title("ERP Σχολής Χορού")
        root.geometry("450x350")
        
        # Δημιουργία βάσης
        create_db()
        
        # --- Widgets για Μαθητές ---
        Label(root, text="Όνομα Μαθητή:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.student_name = Entry(root)
        self.student_name.grid(row=0, column=1, padx=5, pady=5)
        
        Label(root, text="Όνομα Γονέα:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.parent_name = Entry(root)
        self.parent_name.grid(row=1, column=1, padx=5, pady=5)
        
        Button(root, text="Προσθήκη Μαθητή", command=self.add_student).grid(row=2, column=1, pady=10)
        
        # --- Widgets για Πληρωμές ---
        Label(root, text="Επιλογή Μαθητή:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        self.student_var = StringVar()
        self.student_dropdown = OptionMenu(root, self.student_var, [])
        self.student_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        Label(root, text="Ποσό Πληρωμής (€):").grid(row=4, column=0, sticky=W, padx=5, pady=5)
        self.payment_amount = Entry(root)
        self.payment_amount.grid(row=4, column=1, padx=5, pady=5)
        
        Label(root, text="Τρόπος Πληρωμής:").grid(row=5, column=0, sticky=W, padx=5, pady=5)
        self.payment_method = Entry(root)
        self.payment_method.grid(row=5, column=1, padx=5, pady=5)
        
        Button(root, text="Καταχώρηση Πληρωμής", command=self.add_payment).grid(row=6, column=1, pady=10)
        
        # Ανανεώνουμε το dropdown με τους μαθητές
        self.refresh_students()

    def refresh_students(self):
        students = get_students()
        menu = self.student_dropdown["menu"]
        menu.delete(0, "end")
        for sid, name in students:
            menu.add_command(label=name, command=lambda value=name: self.student_var.set(value))
        if students:
            self.student_var.set(students[0][1])
        else:
            self.student_var.set("")

    def add_student(self):
        name = self.student_name.get().strip()
        parent = self.parent_name.get().strip()
        if not name or not parent:
            messagebox.showwarning("Προσοχή", "Συμπλήρωσε όλα τα πεδία για τον μαθητή.")
            return
        add_student(name, parent)
        messagebox.showinfo("Επιτυχία", "Ο μαθητής προστέθηκε.")
        self.student_name.delete(0, END)
        self.parent_name.delete(0, END)
        self.refresh_students()

    def add_payment(self):
        student_name = self.student_var.get()
        amount_str = self.payment_amount.get().strip()
        method = self.payment_method.get().strip()
        
        if not student_name or not amount_str or not method:
            messagebox.showwarning("Προσοχή", "Συμπλήρωσε όλα τα πεδία για την πληρωμή.")
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Προσοχή", "Το ποσό πρέπει να είναι αριθμός.")
            return
        
        students = get_students()
        student_id = None
        for sid, name in students:
            if name == student_name:
                student_id = sid
                break
        
        if student_id is None:
            messagebox.showerror("Σφάλμα", "Ο μαθητής δεν βρέθηκε.")
            return
        
        add_payment(student_id, amount, method)
        messagebox.showinfo("Επιτυχία", "Η πληρωμή καταχωρήθηκε.")
        self.payment_amount.delete(0, END)
        self.payment_method.delete(0, END)

if __name__ == "__main__":
    root = Tk()
    app = DanceSchoolApp(root)
    root.mainloop()
