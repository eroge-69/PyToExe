
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import shutil
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Directory setup
DB_PATH = "database/employees.db"
PHOTO_DIR = "images"
os.makedirs(PHOTO_DIR, exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            department TEXT,
            email TEXT,
            join_date TEXT,
            photo_path TEXT
        )
    """)
    conn.commit()
    conn.close()

class EmployeeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Employment Management System")
        self.root.geometry("1000x600")
        self.selected_photo = None

        self.emp_id = tk.StringVar()
        self.first_name = tk.StringVar()
        self.last_name = tk.StringVar()
        self.department = tk.StringVar()
        self.email = tk.StringVar()
        self.join_date = tk.StringVar()

        form_frame = tk.Frame(self.root, bg="gray20", padx=10, pady=10)
        form_frame.pack(side=tk.TOP, fill=tk.X)

        labels = ["Employee ID", "First Name", "Last Name", "Department", "Email", "Join Date"]
        variables = [self.emp_id, self.first_name, self.last_name, self.department, self.email, self.join_date]

        for i, (label, var) in enumerate(zip(labels, variables)):
            tk.Label(form_frame, text=label, fg="white", bg="gray20").grid(row=i, column=0, sticky="e")
            tk.Entry(form_frame, textvariable=var, width=30).grid(row=i, column=1, padx=5, pady=2)

        button_frame = tk.Frame(form_frame, bg="gray20")
        button_frame.grid(row=0, column=2, rowspan=6, padx=10)

        tk.Button(button_frame, text="Add new record", command=self.add_record).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Update selected record", command=self.update_record).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Delete selected record", command=self.delete_record).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Clear form", command=self.clear_form).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Create PDF", command=self.create_pdf).pack(fill=tk.X, pady=2)

        self.photo_label = tk.Label(form_frame, width=120, height=150, bg="gray", relief=tk.RIDGE)
        self.photo_label.grid(row=0, column=3, rowspan=6, padx=10)

        tk.Button(form_frame, text="Upload Photo", command=self.upload_photo).grid(row=6, column=3)

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("emp_id", "first_name", "last_name", "department", "email", "join_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_row_select)

        self.load_data()

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if file_path:
            self.selected_photo = file_path
            img = Image.open(file_path).resize((120, 150))
            self.photo_img = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo_img)

    def add_record(self):
        if not all([self.emp_id.get(), self.first_name.get(), self.email.get()]):
            messagebox.showwarning("Input Error", "Employee ID, First Name, and Email are required")
            return

        photo_dest = ""
        if self.selected_photo:
            photo_dest = os.path.join(PHOTO_DIR, os.path.basename(self.selected_photo))
            shutil.copy(self.selected_photo, photo_dest)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (self.emp_id.get(), self.first_name.get(), self.last_name.get(),
                         self.department.get(), self.email.get(), self.join_date.get(), photo_dest))
            conn.commit()
            self.load_data()
            self.clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Employee ID already exists")
        finally:
            conn.close()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT emp_id, first_name, last_name, department, email, join_date FROM employees")
        for row in cur.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def on_row_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.emp_id.set(values[0])
            self.first_name.set(values[1])
            self.last_name.set(values[2])
            self.department.set(values[3])
            self.email.set(values[4])
            self.join_date.set(values[5])

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT photo_path FROM employees WHERE emp_id=?", (values[0],))
            row = cur.fetchone()
            if row and os.path.exists(row[0]):
                img = Image.open(row[0]).resize((120, 150))
                self.photo_img = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo_img)
            else:
                self.photo_label.config(image="")
            conn.close()

    def update_record(self):
        photo_dest = ""
        if self.selected_photo:
            photo_dest = os.path.join(PHOTO_DIR, os.path.basename(self.selected_photo))
            shutil.copy(self.selected_photo, photo_dest)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            UPDATE employees SET first_name=?, last_name=?, department=?, email=?, join_date=?, photo_path=?
            WHERE emp_id=?
        """, (self.first_name.get(), self.last_name.get(), self.department.get(),
              self.email.get(), self.join_date.get(), photo_dest, self.emp_id.get()))
        conn.commit()
        conn.close()
        self.load_data()
        self.clear_form()

    def delete_record(self):
        if not self.emp_id.get():
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE emp_id=?", (self.emp_id.get(),))
        conn.commit()
        conn.close()
        self.load_data()
        self.clear_form()

    def clear_form(self):
        for var in [self.emp_id, self.first_name, self.last_name, self.department, self.email, self.join_date]:
            var.set("")
        self.selected_photo = None
        self.photo_label.config(image="")

    def create_pdf(self):
        if not self.emp_id.get():
            messagebox.showwarning("No Selection", "Select an employee first.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{self.emp_id.get()}_profile.pdf")
        if not filename:
            return

        c = canvas.Canvas(filename, pagesize=A4)
        text_y = 800
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, text_y, "Employee Profile")
        c.setFont("Helvetica", 12)
        text_y -= 40

        details = [
            f"Employee ID: {self.emp_id.get()}",
            f"First Name: {self.first_name.get()}",
            f"Last Name: {self.last_name.get()}",
            f"Department: {self.department.get()}",
            f"Email: {self.email.get()}",
            f"Join Date: {self.join_date.get()}"
        ]

        for line in details:
            c.drawString(100, text_y, line)
            text_y -= 20

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT photo_path FROM employees WHERE emp_id=?", (self.emp_id.get(),))
        row = cur.fetchone()
        if row and row[0] and os.path.exists(row[0]):
            try:
                c.drawImage(row[0], 400, 700, width=120, height=150)
            except:
                pass
        conn.close()

        c.save()
        messagebox.showinfo("Success", f"PDF saved as '{filename}'")

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = EmployeeManager(root)
    root.mainloop()
