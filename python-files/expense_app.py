import csv
import datetime as dt
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt

CSV_FILE = "expenses_history.csv"


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        root.title("💰 Monthly Expense Calculator")
        root.geometry("550x600")
        root.configure(bg="#f4f4f4")

        self.income_var = tk.DoubleVar()
        self.rows = []

        title = tk.Label(
            root,
            text="Monthly Expense Calculator",
            font=("Helvetica", 18, "bold"),
            bg="#f4f4f4",
            fg="#007B7F"
        )
        title.pack(pady=10)

        # ===== Income Entry =====
        income_frame = tk.Frame(root, bg="#f4f4f4")
        income_frame.pack(pady=10)
        tk.Label(
            income_frame,
            text="Monthly Income (₹):",
            font=("Arial", 12, "bold"),
            bg="#f4f4f4"
        ).pack(side="left", padx=5)
        tk.Entry(
            income_frame,
            textvariable=self.income_var,
            width=20,
            font=("Arial", 11)
        ).pack(side="left")

        # ===== Expenses Section =====
        self.expense_frame = tk.LabelFrame(
            root,
            text="Expenses",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#007B7F",
            bd=2,
            relief="groove",
            padx=10,
            pady=10
        )
        self.expense_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.add_row()

        # ===== Buttons Section =====
        btn_frame = tk.Frame(root, bg="#f4f4f4")
        btn_frame.pack(pady=10)

        self.make_button(btn_frame, "➕ Add Expense", self.add_row).grid(row=0, column=0, padx=10)
        self.make_button(btn_frame, "💾 Calculate & Save", self.calculate).grid(row=0, column=1, padx=10)
        self.make_button(btn_frame, "📂 View History CSV", self.open_csv).grid(row=0, column=2, padx=10)

        # Footer
        tk.Label(root, text="By YourFinanceApp", font=("Arial", 9), bg="#f4f4f4", fg="#999999").pack(side="bottom", pady=5)

    # ----------------------------------------------------------
    # Custom Button Factory
    # ----------------------------------------------------------
    def make_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            bg="#007B7F",
            fg="white",
            activebackground="#009fa5",
            padx=10,
            pady=5,
            relief="raised",
            bd=2,
            cursor="hand2"
        )
        return btn

    # ----------------------------------------------------------
    # Add/Delete Expense Rows
    # ----------------------------------------------------------
    def add_row(self):
        name_var = tk.StringVar()
        amount_var = tk.DoubleVar()

        row_frame = tk.Frame(self.expense_frame, bg="#ffffff")
        row_frame.pack(anchor="w", pady=4)

        tk.Entry(row_frame, textvariable=name_var, width=22, font=("Arial", 10)).pack(side="left", padx=5)
        tk.Entry(row_frame, textvariable=amount_var, width=12, font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(
            row_frame,
            text="❌",
            command=lambda: self.delete_row(row_frame),
            fg="white",
            bg="#d9534f",
            activebackground="#c9302c",
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=6
        ).pack(side="left", padx=5)

        self.rows.append((name_var, amount_var, row_frame))

    def delete_row(self, row_frame):
        self.rows = [(n, a, f) for (n, a, f) in self.rows if f != row_frame]
        row_frame.destroy()

    # ----------------------------------------------------------
    # Core Logic
    # ----------------------------------------------------------
    def calculate(self):
        income = self.income_var.get()

        expenses = {}
        for name_var, amount_var, _ in self.rows:
            amount = amount_var.get()
            if amount > 0:
                name = name_var.get().strip() or "Unnamed"
                expenses[name] = expenses.get(name, 0) + amount

        if income <= 0:
            messagebox.showwarning("Oops!", "Please enter a positive income.")
            return
        if not expenses:
            messagebox.showwarning("Oops!", "Please add at least one valid expense.")
            return

        total_expense = sum(expenses.values())
        balance = income - total_expense

        self.save_to_csv(income, expenses, total_expense, balance)

        messagebox.showinfo("Summary", f"Total Expenses: ₹{total_expense:.2f}\nRemaining: ₹{balance:.2f}")
        self.show_pie_chart(expenses)

    def save_to_csv(self, income, expenses, total_expense, balance):
        header = ["Date", "Income"] + list(expenses.keys()) + ["Total_Expense", "Balance"]
        data_row = [dt.date.today().isoformat(), income] + list(expenses.values()) + [total_expense, balance]

        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(data_row)

    def show_pie_chart(self, expenses):
        labels = list(expenses.keys())
        sizes = list(expenses.values())

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Expense Distribution")
        plt.axis("equal")
        plt.show()

    def open_csv(self):
        if os.path.isfile(CSV_FILE):
            filedialog.askopenfilename(initialfile=CSV_FILE)
        else:
            messagebox.showinfo("No history yet", "The CSV file has not been created yet.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
