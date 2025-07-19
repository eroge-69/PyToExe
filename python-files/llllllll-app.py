import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime

STUDENT_FILE = 'students.csv'
PAYMENT_FILE = 'payments.csv'

# Ensure files exist with headers
def setup_files():
    with open(STUDENT_FILE, 'a+', newline='') as f:
        writer = csv.writer(f)
        f.seek(0)
        if not f.readline():
            writer.writerow(['StudentID', 'Name', 'Class', 'TotalFees'])
    with open(PAYMENT_FILE, 'a+', newline='') as f:
        writer = csv.writer(f)
        f.seek(0)
        if not f.readline():
            writer.writerow(['StudentID', 'Term', 'AmountPaid', 'Date', 'Method'])

setup_files()

# GUI Application Class
class FeeManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Fee Management System")
        self.root.geometry("800x600")

        tab_control = ttk.Notebook(root)

        self.register_tab = ttk.Frame(tab_control)
        self.payment_tab = ttk.Frame(tab_control)
        self.balance_tab = ttk.Frame(tab_control)
        self.history_tab = ttk.Frame(tab_control)

        tab_control.add(self.register_tab, text='Register Student')
        tab_control.add(self.payment_tab, text='Record Payment')
        tab_control.add(self.balance_tab, text='Show Balance')
        tab_control.add(self.history_tab, text='Payment History')

        tab_control.pack(expand=1, fill="both")

        self.create_register_tab()
        self.create_payment_tab()
        self.create_balance_tab()
        self.create_history_tab()

    def create_register_tab(self):
        tk.Label(self.register_tab, text="Student ID").pack()
        self.reg_id = tk.Entry(self.register_tab)
        self.reg_id.pack()

        tk.Label(self.register_tab, text="Full Name").pack()
        self.reg_name = tk.Entry(self.register_tab)
        self.reg_name.pack()

        tk.Label(self.register_tab, text="Class").pack()
        self.reg_class = tk.Entry(self.register_tab)
        self.reg_class.pack()

        tk.Label(self.register_tab, text="Total Fees").pack()
        self.reg_fees = tk.Entry(self.register_tab)
        self.reg_fees.pack()

        tk.Button(self.register_tab, text="Register", command=self.register_student).pack(pady=10)

    def register_student(self):
        data = [
            self.reg_id.get(),
            self.reg_name.get(),
            self.reg_class.get(),
            self.reg_fees.get()
        ]
        with open(STUDENT_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)
        messagebox.showinfo("Success", "Student Registered Successfully")

    def create_payment_tab(self):
        tk.Label(self.payment_tab, text="Student ID").pack()
        self.pay_id = tk.Entry(self.payment_tab)
        self.pay_id.pack()

        tk.Label(self.payment_tab, text="Term").pack()
        self.pay_term = tk.Entry(self.payment_tab)
        self.pay_term.pack()

        tk.Label(self.payment_tab, text="Amount Paid").pack()
        self.pay_amount = tk.Entry(self.payment_tab)
        self.pay_amount.pack()

        tk.Label(self.payment_tab, text="Payment Method").pack()
        self.pay_method = tk.Entry(self.payment_tab)
        self.pay_method.pack()

        tk.Button(self.payment_tab, text="Record Payment", command=self.record_payment).pack(pady=10)

    def record_payment(self):
        date = datetime.now().strftime("%Y-%m-%d")
        data = [
            self.pay_id.get(),
            self.pay_term.get(),
            self.pay_amount.get(),
            date,
            self.pay_method.get()
        ]
        with open(PAYMENT_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)
        receipt = f"Student ID: {data[0]}\nTerm: {data[1]}\nAmount Paid: {data[2]}\nDate: {data[3]}\nMethod: {data[4]}"
        messagebox.showinfo("Payment Recorded", f"Receipt:\n{receipt}")

    def create_balance_tab(self):
        tk.Label(self.balance_tab, text="Student ID").pack()
        self.bal_id = tk.Entry(self.balance_tab)
        self.bal_id.pack()

        tk.Label(self.balance_tab, text="Term").pack()
        self.bal_term = tk.Entry(self.balance_tab)
        self.bal_term.pack()

        tk.Button(self.balance_tab, text="Show Balance", command=self.show_balance).pack(pady=10)
        self.balance_result = tk.Label(self.balance_tab, text="")
        self.balance_result.pack()

        self.payment_dates_result = tk.Label(self.balance_tab, text="")
        self.payment_dates_result.pack()

    def show_balance(self):
        student_id = self.bal_id.get()
        term = self.bal_term.get()
        total_fees = 0

        with open(STUDENT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['StudentID'] == student_id:
                    total_fees = float(row['TotalFees'])

        total_paid = 0
        payment_dates = []
        with open(PAYMENT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['StudentID'] == student_id and row['Term'] == term:
                    total_paid += float(row['AmountPaid'])
                    payment_dates.append(f"{row['Date']} ({row['Method']})")

        balance = total_fees - total_paid
        self.balance_result.config(text=f"Total Paid: {total_paid}\nBalance: {balance}")
        self.payment_dates_result.config(text=f"Payments made: {'; '.join(payment_dates)}")

    def create_history_tab(self):
        tk.Label(self.history_tab, text="Student ID").pack()
        self.hist_id = tk.Entry(self.history_tab)
        self.hist_id.pack()

        tk.Button(self.history_tab, text="View Payments", command=self.view_history).pack(pady=10)

        self.tree = ttk.Treeview(self.history_tab, columns=('Term', 'AmountPaid', 'Date', 'Method'), show='headings')
        for col in ('Term', 'AmountPaid', 'Date', 'Method'):
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

    def view_history(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        student_id = self.hist_id.get()
        with open(PAYMENT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['StudentID'] == student_id:
                    self.tree.insert('', 'end', values=(row['Term'], row['AmountPaid'], row['Date'], row['Method']))


if __name__ == "__main__":
    root = tk.Tk()
    app = FeeManagementApp(root)
    root.mainloop()
