import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os
from datetime import datetime

DATA_FILE = "expenses_data.csv"

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Manager")
        self.root.geometry("850x500")  # ����� ����� �� ��� ������
        self.root.resizable(False, False)
        self.root.config(bg="#f0f0f0")

        # Variables
        self.daily_expense = tk.StringVar()
        self.side_expense = tk.StringVar()

        # Frames
        frame_inputs = tk.Frame(self.root, bg="#d1e7dd", pady=10)
        frame_inputs.pack(fill="x", padx=10, pady=5)

        frame_table = tk.Frame(self.root, bg="#fff3cd", pady=10)
        frame_table.pack(fill="both", expand=True, padx=10, pady=5)

        frame_totals = tk.Frame(self.root, bg="#f8d7da", pady=10)
        frame_totals.pack(fill="x", padx=10, pady=5)

        # Input fields
        tk.Label(frame_inputs, text="Daily Expense:", bg="#d1e7dd", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
        tk.Entry(frame_inputs, textvariable=self.daily_expense, width=12, font=("Arial", 12)).grid(row=0, column=1, padx=5)

        tk.Label(frame_inputs, text="Side Expense:", bg="#d1e7dd", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5)
        tk.Entry(frame_inputs, textvariable=self.side_expense, width=12, font=("Arial", 12)).grid(row=0, column=3, padx=5)

        tk.Button(frame_inputs, text="Add", command=self.add_expense, bg="#0d6efd", fg="white", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=10)
        tk.Button(frame_inputs, text="Edit Selected", command=self.edit_selected, bg="#ffc107", fg="black", font=("Arial", 12, "bold")).grid(row=0, column=5, padx=10)
        tk.Button(frame_inputs, text="Delete Selected", command=self.delete_selected, bg="#dc3545", fg="white", font=("Arial", 12, "bold")).grid(row=0, column=6, padx=10)

        # Main table
        self.tree = ttk.Treeview(frame_table, columns=("date", "daily", "side", "total"), show="headings", height=12)
        self.tree.heading("date", text="Date")
        self.tree.heading("daily", text="Daily Expense")
        self.tree.heading("side", text="Side Expense")
        self.tree.heading("total", text="Total")
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), foreground="#ffffff", background="#198754")
        style.map("Treeview.Heading", background=[('active','#198754')])
        style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff")
        style.map('Treeview', background=[('selected', '#0d6efd')], foreground=[('selected', '#ffffff')])

        # Totals table
        self.totals_tree = ttk.Treeview(frame_totals, columns=("total_daily", "total_side", "grand_total"), show="headings", height=1)
        self.totals_tree.heading("total_daily", text="Total Daily")
        self.totals_tree.heading("total_side", text="Total Side")
        self.totals_tree.heading("grand_total", text="Grand Total")
        self.totals_tree.pack(fill="x", padx=5, pady=5)

        style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#dc3545", foreground="white")
        style.configure("Treeview", font=("Arial", 12, "bold"))

        # Load existing data
        self.expenses = []
        self.load_data()
        self.update_totals()

    def add_expense(self):
        try:
            daily = float(self.daily_expense.get()) if self.daily_expense.get() else 0
            side = float(self.side_expense.get()) if self.side_expense.get() else 0
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return

        total = daily + side
        date = datetime.now().strftime("%Y-%m-%d")
        row = [date, daily, side, total]

        self.expenses.append(row)
        item_id = self.tree.insert("", "end", values=row)
        # Color daily and side columns
        self.tree.tag_configure('daily', foreground='blue')
        self.tree.tag_configure('side', foreground='green')
        self.tree.item(item_id, tags=('daily','side'))
        self.save_data()
        self.update_totals()

        self.daily_expense.set("")
        self.side_expense.set("")

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No row selected")
            return

        index = self.tree.index(selected[0])
        old_values = self.expenses[index]

        new_daily = simpledialog.askstring("Edit Daily Expense", "Enter new daily expense:", initialvalue=old_values[1])
        new_side = simpledialog.askstring("Edit Side Expense", "Enter new side expense:", initialvalue=old_values[2])

        if new_daily is None or new_side is None:
            return  # Cancelled

        try:
            new_daily = float(new_daily)
            new_side = float(new_side)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return

        new_total = new_daily + new_side
        new_row = [old_values[0], new_daily, new_side, new_total]

        self.expenses[index] = new_row
        self.tree.item(selected[0], values=new_row)
        self.save_data()
        self.update_totals()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No row selected")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected row?")
        if not confirm:
            return

        index = self.tree.index(selected[0])
        self.tree.delete(selected[0])
        del self.expenses[index]
        self.save_data()
        self.update_totals()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        daily = float(row[1])
                        side = float(row[2])
                        total = float(row[3])
                        self.expenses.append([row[0], daily, side, total])
                        item_id = self.tree.insert("", "end", values=[row[0], daily, side, total])
                        self.tree.tag_configure('daily', foreground='blue')
                        self.tree.tag_configure('side', foreground='green')
                        self.tree.item(item_id, tags=('daily','side'))
                    except:
                        continue

    def save_data(self):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.expenses)

    def update_totals(self):
        total_daily = sum(row[1] for row in self.expenses)
        total_side = sum(row[2] for row in self.expenses)
        total_all = total_daily + total_side

        for item in self.totals_tree.get_children():
            self.totals_tree.delete(item)

        self.totals_tree.insert("", "end", values=(total_daily, total_side, total_all))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
