
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

conn = sqlite3.connect("invoices.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    total_amount REAL,
    paid_amount REAL DEFAULT 0,
    payment_status TEXT DEFAULT 'غير مدفوعة',
    created_at TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    amount_paid REAL,
    payment_time TEXT,
    FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id)
)""")

conn.commit()

def add_invoice():
    name = entry_name.get()
    total = entry_total.get()
    if not name or not total:
        messagebox.showwarning("تنبيه", "يرجى إدخال اسم العميل والمبلغ الكلي")
        return
    try:
        total = float(total)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO invoices (customer_name, total_amount, created_at) VALUES (?, ?, ?)",
                  (name, total, now))
        conn.commit()
        messagebox.showinfo("تم", "تمت إضافة الفاتورة بنجاح")
        entry_name.delete(0, tk.END)
        entry_total.delete(0, tk.END)
        refresh_invoices()
    except ValueError:
        messagebox.showerror("خطأ", "يجب إدخال مبلغ صحيح")

def add_payment():
    try:
        invoice_id = int(entry_invoice_id.get())
        amount = float(entry_payment_amount.get())
    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال رقم فاتورة صحيح ومبلغ صالح")
        return

    c.execute("SELECT total_amount, paid_amount FROM invoices WHERE invoice_id = ?", (invoice_id,))
    row = c.fetchone()
    if not row:
        messagebox.showerror("خطأ", "الفاتورة غير موجودة")
        return
    total, paid = row
    new_paid = paid + amount
    if new_paid > total:
        messagebox.showwarning("تحذير", "المبلغ المدفوع يتجاوز المبلغ الكلي")
        return

    status = 'مدفوعة بالكامل' if new_paid == total else 'مدفوعة جزئيًا'
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO payments (invoice_id, amount_paid, payment_time) VALUES (?, ?, ?)",
              (invoice_id, amount, now))
    c.execute("UPDATE invoices SET paid_amount = ?, payment_status = ? WHERE invoice_id = ?",
              (new_paid, status, invoice_id))
    conn.commit()
    messagebox.showinfo("تم", "تم تسجيل الدفعة")
    entry_invoice_id.delete(0, tk.END)
    entry_payment_amount.delete(0, tk.END)
    refresh_invoices()

def refresh_invoices():
    for row in tree.get_children():
        tree.delete(row)
    c.execute("SELECT invoice_id, customer_name, total_amount, paid_amount, payment_status FROM invoices")
    for row in c.fetchall():
        tree.insert('', 'end', values=row)

def show_invoice_report():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("تنبيه", "يرجى اختيار فاتورة من القائمة")
        return
    invoice_id = tree.item(selected[0])['values'][0]
    c.execute("SELECT customer_name, total_amount, paid_amount FROM invoices WHERE invoice_id = ?", (invoice_id,))
    invoice = c.fetchone()
    if not invoice:
        messagebox.showerror("خطأ", "تعذر العثور على الفاتورة")
        return

    customer_name, total, paid = invoice
    remaining = total - paid

    report = tk.Toplevel(root)
    report.title(f"تقرير الفاتورة رقم {invoice_id}")
    report.geometry("600x400")

    tk.Label(report, text=f"رقم الفاتورة: {invoice_id}", font=('Arial', 12, 'bold')).pack(pady=5)
    tk.Label(report, text=f"اسم العميل: {customer_name}", font=('Arial', 12)).pack(pady=5)
    tk.Label(report, text=f"المبلغ الأصلي: {total:.2f} ريال", font=('Arial', 12)).pack(pady=5)
    tk.Label(report, text=f"المدفوع: {paid:.2f} ريال", font=('Arial', 12)).pack(pady=5)
    tk.Label(report, text=f"المتبقي: {remaining:.2f} ريال", font=('Arial', 12)).pack(pady=5)

    tk.Label(report, text="تفاصيل الدفعات:", font=('Arial', 12, 'underline')).pack(pady=10)
    payments_tree = ttk.Treeview(report, columns=("المبلغ", "الوقت"), show="headings", height=6)
    payments_tree.heading("المبلغ", text="المبلغ المدفوع")
    payments_tree.heading("الوقت", text="تاريخ ووقت الدفعة")
    payments_tree.pack(padx=10, pady=5, fill="both", expand=True)

    c.execute("SELECT amount_paid, payment_time FROM payments WHERE invoice_id = ?", (invoice_id,))
    for row in c.fetchall():
        payments_tree.insert('', 'end', values=row)

root = tk.Tk()
root.title("نظام إدارة الفواتير والدفعات")
root.geometry("800x600")

frame1 = tk.LabelFrame(root, text="إدخال فاتورة جديدة", padx=10, pady=10)
frame1.pack(padx=10, pady=5, fill="x")

tk.Label(frame1, text="اسم العميل").grid(row=0, column=0)
entry_name = tk.Entry(frame1)
entry_name.grid(row=0, column=1)

tk.Label(frame1, text="المبلغ الكلي").grid(row=0, column=2)
entry_total = tk.Entry(frame1)
entry_total.grid(row=0, column=3)

tk.Button(frame1, text="إضافة الفاتورة", command=add_invoice).grid(row=0, column=4, padx=10)

frame2 = tk.LabelFrame(root, text="تسجيل دفعة", padx=10, pady=10)
frame2.pack(padx=10, pady=5, fill="x")

tk.Label(frame2, text="رقم الفاتورة").grid(row=0, column=0)
entry_invoice_id = tk.Entry(frame2)
entry_invoice_id.grid(row=0, column=1)

tk.Label(frame2, text="قيمة الدفعة").grid(row=0, column=2)
entry_payment_amount = tk.Entry(frame2)
entry_payment_amount.grid(row=0, column=3)

tk.Button(frame2, text="إضافة الدفعة", command=add_payment).grid(row=0, column=4, padx=10)

frame3 = tk.LabelFrame(root, text="سجل الفواتير", padx=10, pady=10)
frame3.pack(padx=10, pady=10, fill="both", expand=True)

columns = ("رقم الفاتورة", "اسم العميل", "المبلغ الكلي", "المدفوع", "الحالة")
tree = ttk.Treeview(frame3, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER)
tree.pack(fill="both", expand=True)

tk.Button(root, text="عرض تقرير الفاتورة المحددة", command=show_invoice_report, bg="#3A7", fg="white").pack(pady=5)

refresh_invoices()
root.mainloop()
