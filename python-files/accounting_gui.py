import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os

FILE_NAME = "transactions.csv"

# إنشاء ملف CSV إذا لم يكن موجودًا
def initialize_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['التاريخ', 'النوع', 'المبلغ', 'الوصف'])

def save_transaction(date, type_, amount, description):
    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, type_, amount, description])

def load_transactions():
    transactions = []
    if not os.path.exists(FILE_NAME):
        return transactions
    with open(FILE_NAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append(row)
    return transactions

def calculate_report():
    income = 0
    expense = 0
    for row in load_transactions():
        amount = float(row['المبلغ'])
        if row['النوع'] == 'دخل':
            income += amount
        elif row['النوع'] == 'مصروف':
            expense += amount
    return income, expense, income - expense

# واجهة المستخدم
def add_transaction():
    date = date_entry.get()
    type_ = type_var.get()
    amount = amount_entry.get()
    description = desc_entry.get()

    if not date or not amount or not description or type_ not in ['دخل', 'مصروف']:
        messagebox.showerror("خطأ", "يرجى ملء جميع الحقول بشكل صحيح.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("خطأ", "يجب أن يكون المبلغ رقمًا.")
        return

    save_transaction(date, type_, amount, description)
    messagebox.showinfo("تم", "تمت إضافة المعاملة بنجاح.")
    update_report()
    clear_fields()
    load_tree()

def clear_fields():
    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)

def update_report():
    income, expense, balance = calculate_report()
    report_var.set(f"الدخل: {income} | المصروف: {expense} | الرصيد: {balance}")

def load_tree():
    for row in tree.get_children():
        tree.delete(row)
    for t in load_transactions():
        tree.insert('', tk.END, values=(t['التاريخ'], t['النوع'], t['المبلغ'], t['الوصف']))

# إنشاء الواجهة
root = tk.Tk()
root.title("برنامج محاسبة بسيط")
root.geometry("600x500")

# الحقول
tk.Label(root, text="التاريخ (YYYY-MM-DD):").pack()
date_entry = tk.Entry(root)
date_entry.pack()

tk.Label(root, text="النوع:").pack()
type_var = tk.StringVa_
