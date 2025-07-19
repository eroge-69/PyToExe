import tkinter as tk
from tkinter import ttk, messagebox

class Student:
    def _init_(self, name, fees_paid=0, total_fees=0):
        self.name = name
        self.fees_paid = fees_paid
        self.total_fees = total_fees
        self.payment_records = []

    def pay_fee(self, amount):
        self.fees_paid += amount
        self.payment_records.append(amount)

    def check_balance(self):
        return self.total_fees - self.fees_paid

    def generate_receipt(self, amount):
        return f"Receipt for {self.name}: KES {amount} paid."

class FeeManagementSystem:
    def _init_(self, root):
        self.root = root
        self.students = {}
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        self.frame1 = tk.Frame(self.notebook)
        self.frame2 = tk.Frame(self.notebook)
        self.frame3 = tk.Frame(self.notebook)
        self.frame4 = tk.Frame(self.notebook)
        self.frame5 = tk.Frame(self.notebook)

        self.notebook.add(self.frame1, text="Add Student")
        self.notebook.add(self.frame2, text="Pay Fee")
        self.notebook.add(self.frame3, text="Check Balance")
        self.notebook.add(self.frame4, text="Generate Receipt")
        self.notebook.add(self.frame5, text="View Payment Records")

        self.add_student_widgets()
        self.pay_fee_widgets()
        self.check_balance_widgets()
        self.generate_receipt_widgets()
        self.view_payment_records_widgets()

    def add_student_widgets(self):
        tk.Label(self.frame1, text="Student Name").pack()
        self.student_name_entry = tk.Entry(self.frame1)
        self.student_name_entry.pack()
        tk.Label(self.frame1, text="Total Fees").pack()
        self.total_fees_entry = tk.Entry(self.frame1)
        self.total_fees_entry.pack()
        self.add_student_button = tk.Button(self.frame1, text="Add Student", command=self.add_student)
        self.add_student_button.pack()

    def pay_fee_widgets(self):
        tk.Label(self.frame2, text="Student Name").pack()
        self.student_name_entry_pay = tk.Entry(self.frame2)
        self.student_name_entry_pay.pack()
        tk.Label(self.frame2, text="Amount").pack()
        self.amount_entry = tk.Entry(self.frame2)
        self.amount_entry.pack()
        self.pay_fee_button = tk.Button(self.frame2, text="Pay Fee", command=self.pay_fee)
        self.pay_fee_button.pack()

    def check_balance_widgets(self):
        tk.Label(self.frame3, text="Student Name").pack()
        self.student_name_entry_balance = tk.Entry(self.frame3)
        self.student_name_entry_balance.pack()
        self.check_balance_button = tk.Button(self.frame3, text="Check Balance", command=self.check_balance)
        self.check_balance_button.pack()
        self.balance_label = tk.Label(self.frame3, text="")
        self.balance_label.pack()

    def generate_receipt_widgets(self):
        tk.Label(self.frame4, text="Student Name").pack()
        self.student_name_entry_receipt = tk.Entry(self.frame4)
        self.student_name_entry_receipt.pack()
        tk.Label(self.frame4, text="Amount").pack()
        self.amount_entry_receipt = tk.Entry(self.frame4)
        self.amount_entry_receipt.pack()
        self.generate_receipt_button = tk.Button(self.frame4, text="Generate Receipt", command=self.generate_receipt)
        self.generate_receipt_button.pack()
        self.receipt_label = tk.Label(self.frame4, text="")
        self.receipt_label.pack()

    def view_payment_records_widgets(self):
        tk.Label(self.frame5, text="Student Name").pack()
        self.student_name_entry_records = tk.Entry(self.frame5)
        self.student_name_entry_records.pack()
        self.view_payment_records_button = tk.Button(self.frame5, text="View Payment Records", command=self.view_payment_records)
        self.view_payment_records_button.pack()
        self.payment_records_label = tk.Label(self.frame5, text="")
        self.payment_records_label.pack()

    def add_student(self):
        name = self.student_name_entry.get()
        total_fees = float(self.total_fees_entry.get())
        self.students[name] = Student(name, total_fees=total_fees)
        messagebox.showinfo("Student Added", f"Student {name} added successfully.")

    def pay_fee(self):
        name = self.student_name_entry_pay.get()
        amount = float(self.amount_entry.get())
        if name in self.students:
            self.students[name].pay
