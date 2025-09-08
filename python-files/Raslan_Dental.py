
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

# قاعدة البيانات
conn = sqlite3.connect("raslan_dental.db")
cursor = conn.cursor()

# إنشاء الجداول
cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, phone TEXT, email TEXT, address TEXT, history TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER, date TEXT, time TEXT, doctor TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT, amount REAL, date TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS daily_income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL, date TEXT)''')

conn.commit()

# إضافة مصروف
def add_expense():
    item = expense_item.get()
    amount = expense_amount.get()
    date = datetime.date.today().strftime("%Y-%m-%d")
    if item and amount:
        cursor.execute("INSERT INTO expenses (item, amount, date) VALUES (?, ?, ?)", (item, amount, date))
        conn.commit()
        messagebox.showinfo("تم", "تم حفظ المصروف")
        expense_item.delete(0, tk.END)
        expense_amount.delete(0, tk.END)
    else:
        messagebox.showwarning("خطأ", "من فضلك أدخل البيانات")

# إضافة دخل يومي
def add_income():
    amount = income_amount.get()
    date = datetime.date.today().strftime("%Y-%m-%d")
    if amount:
        cursor.execute("INSERT INTO daily_income (amount, date) VALUES (?, ?)", (amount, date))
        conn.commit()
        messagebox.showinfo("تم", "تم حفظ الدخل")
        income_amount.delete(0, tk.END)
    else:
        messagebox.showwarning("خطأ", "من فضلك أدخل المبلغ")

# حساب التقرير الشهري
def show_monthly_report():
    month = datetime.date.today().strftime("%Y-%m")
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month+"%",))
    total_expenses = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM daily_income WHERE date LIKE ?", (month+"%",))
    total_income = cursor.fetchone()[0] or 0
    profit = total_income - total_expenses
    messagebox.showinfo("التقرير الشهري", f"إجمالي الدخل: {total_income}\nإجمالي المصروفات: {total_expenses}\nصافي الربح: {profit}")

# التطبيق
root = tk.Tk()
root.title("Raslan Dental - م/محمود رسلان")
root.geometry("600x400")

# Splash Screen
splash = tk.Toplevel()
splash.title("مرحبا")
splash.geometry("400x200")
tk.Label(splash, text="م/محمود رسلان", font=("Arial", 18)).pack(pady=20)
tk.Label(splash, text="Raslan Dental", font=("Arial", 16)).pack(pady=10)
root.withdraw()

def close_splash():
    splash.destroy()
    root.deiconify()

splash.after(2000, close_splash)

# Notebook للتبويبات
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# تبويب Raslan Dental (مصروفات + دخل + تقرير)
raslan_tab = ttk.Frame(notebook)
notebook.add(raslan_tab, text="Raslan Dental")

tk.Label(raslan_tab, text="إضافة مصروف:", font=("Arial", 12)).pack(pady=5)
expense_item = tk.Entry(raslan_tab, width=30)
expense_item.pack(pady=2)
expense_amount = tk.Entry(raslan_tab, width=30)
expense_amount.pack(pady=2)
tk.Button(raslan_tab, text="حفظ المصروف", command=add_expense).pack(pady=5)

tk.Label(raslan_tab, text="إضافة دخل يومي:", font=("Arial", 12)).pack(pady=5)
income_amount = tk.Entry(raslan_tab, width=30)
income_amount.pack(pady=2)
tk.Button(raslan_tab, text="حفظ الدخل", command=add_income).pack(pady=5)

tk.Button(raslan_tab, text="عرض التقرير الشهري", command=show_monthly_report).pack(pady=20)

root.mainloop()
