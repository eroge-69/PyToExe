import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3, os
from datetime import datetime

# Setup DB
conn = sqlite3.connect('school_fees.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_fee REAL NOT NULL,
    paid_fee REAL DEFAULT 0,
    photo_path TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount REAL,
    date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
''')
conn.commit()

# Ensure directories exist
os.makedirs("students", exist_ok=True)
os.makedirs("receipts", exist_ok=True)

class FeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Fees Management System")
        self.selected_photo = None
        
        # === Student Registration ===
        student_frame = ttk.LabelFrame(root, text="Register Student")
        student_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(student_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(student_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(student_frame, text="Total Fee:").grid(row=1, column=0, padx=5, pady=5)
        self.total_fee_entry = ttk.Entry(student_frame)
        self.total_fee_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(student_frame, text="Upload Photo", command=self.upload_photo).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(student_frame, text="Add Student", command=self.add_student).grid(row=3, column=0, columnspan=2, pady=5)

        # === Student Photo Preview ===
        self.photo_label = ttk.Label(student_frame)
        self.photo_label.grid(row=0, column=2, rowspan=4, padx=10)

        # === Payment & Lookup ===
        payment_frame = ttk.LabelFrame(root, text="Payments & Balance")
        payment_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(payment_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
        self.sid_entry = ttk.Entry(payment_frame)
        self.sid_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(payment_frame, text="Amount Paid:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(payment_frame)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(payment_frame, text="Record Payment", command=self.record_payment).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(payment_frame, text="Check Balance", command=self.check_balance).grid(row=3, column=0, columnspan=2, pady=5)

    def upload_photo(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file:
            self.selected_photo = file
            img = Image.open(file).resize((100, 100))
            self.photo_img = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo_img)

    def add_student(self):
        name = self.name_entry.get().strip()
        fee = self.total_fee_entry.get().strip()
        if not name or not fee:
            messagebox.showerror("Error", "Name and Fee are required")
            return
        try:
            fee = float(fee)
        except:
            messagebox.showerror("Error", "Fee must be a number")
            return

        photo_path = None
        if self.selected_photo:
            ext = os.path.splitext(self.selected_photo)[1]
            dest = f"students/{name.replace(' ', '_')}_{int(datetime.now().timestamp())}{ext}"
            Image.open(self.selected_photo).save(dest)
            photo_path = dest

        c.execute("INSERT INTO students (name, total_fee, photo_path) VALUES (?, ?, ?)",
                  (name, fee, photo_path))
        conn.commit()
        messagebox.showinfo("Success", "Student added!")
        self.name_entry.delete(0, tk.END)
        self.total_fee_entry.delete(0, tk.END)
        self.selected_photo = None
        self.photo_label.config(image='')

    def record_payment(self):
        sid = self.sid_entry.get().strip()
        amt = self.amount_entry.get().strip()
        if not sid or not amt:
            messagebox.showerror("Error", "Student ID and Amount are required")
            return
        try:
            sid = int(sid); amt = float(amt)
        except:
            messagebox.showerror("Error", "Invalid ID or amount")
            return
        c.execute("SELECT student_id, name, total_fee, paid_fee FROM students WHERE student_id=?", (sid,))
        student = c.fetchone()
        if not student:
            messagebox.showerror("Error", "Student ID not found")
            return

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO payments (student_id, amount, date) VALUES (?, ?, ?)", (sid, amt, date))
        c.execute("UPDATE students SET paid_fee = paid_fee + ? WHERE student_id=?", (amt, sid))
        conn.commit()

        student_rec = c.execute("SELECT student_id, name, total_fee, paid_fee FROM students WHERE student_id=?", (sid,)).fetchone()
        self.generate_receipt(student_rec, amt, date)
        messagebox.showinfo("Success", "Payment recorded!")

    def check_balance(self):
        sid = self.sid_entry.get().strip()
        if not sid:
            messagebox.showerror("Error", "Student ID required")
            return
        try:
            sid = int(sid)
        except:
            messagebox.showerror("Error", "Invalid ID")
            return

        c.execute("SELECT name, total_fee, paid_fee FROM students WHERE student_id=?", (sid,))
        student = c.fetchone()
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        name, total, paid = student
        balance = total - paid
        messagebox.showinfo("Balance Details",
                            f"Name: {name}\nTotal Fee: {total}\nPaid: {paid}\nBalance: {balance}")

    def generate_receipt(self, student, amt, date):
        sid, name, total, paid = student
        balance = total - paid
        content = (
            f"--- School Fee Receipt ---\n"
            f"Date: {date}\n"
            f"Student ID: {sid}\n"
            f"Name: {name}\n"
            f"Paid: {amt}\n"
            f"Total Fee: {total}\n"
            f"Total Paid: {paid}\n"
            f"Balance Remaining: {balance}\n"
        )
        fname = f"receipts/receipt_{sid}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(fname, "w") as f:
            f.write(content)

if __name__ == "__main__":
    root = tk.Tk()
    app = FeeApp(root)
    root.mainloop()
