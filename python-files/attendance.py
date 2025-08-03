import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A5
import arabic_reshaper
from bidi.algorithm import get_display

# ====== تحميل خط عربي للPDF ======
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # لازم يكون خط arial.ttf في نفس فولدر البرنامج

# ====== قاعدة البيانات ======
conn = sqlite3.connect("clinic.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS patients (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT,
             date TEXT,
             condition TEXT,
             diagnosis TEXT,
             tests TEXT,
             procedure TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS prescriptions (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             doctor TEXT,
             patient_name TEXT,
             date TEXT,
             diagnosis TEXT,
             medicine TEXT)""")
conn.commit()

# ====== دوال المرضى ======
def add_patient():
    name = name_entry.get()
    date = date_entry.get_date().strftime("%Y-%m-%d")
    condition = condition_entry.get()
    diagnosis = diagnosis_entry.get()
    tests = tests_entry.get()
    procedure = procedure_entry.get()

    if name:
        c.execute("INSERT INTO patients (name, date, condition, diagnosis, tests, procedure) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, date, condition, diagnosis, tests, procedure))
        conn.commit()
        show_records()
        clear_entries()
    else:
        messagebox.showwarning("خطأ", "ادخل اسم المريض")

def update_patient():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("خطأ", "اختر مريض للتعديل")
        return
    record_id = tree.item(selected[0])["values"][0]
    c.execute("""UPDATE patients SET name=?, date=?, condition=?, diagnosis=?, tests=?, procedure=? WHERE id=?""",
              (name_entry.get(), date_entry.get_date().strftime("%Y-%m-%d"), condition_entry.get(),
               diagnosis_entry.get(), tests_entry.get(), procedure_entry.get(), record_id))
    conn.commit()
    show_records()
    clear_entries()

def delete_patient():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("خطأ", "اختر مريض للحذف")
        return
    record_id = tree.item(selected[0])["values"][0]
    c.execute("DELETE FROM patients WHERE id=?", (record_id,))
    conn.commit()
    show_records()

def search_patient():
    query = search_entry.get()
    for row in tree.get_children():
        tree.delete(row)
    c.execute("""SELECT * FROM patients WHERE name LIKE ? OR date LIKE ? OR diagnosis LIKE ?""",
              (f"%{query}%", f"%{query}%", f"%{query}%"))
    for row in c.fetchall():
        tree.insert("", "end", values=row)

def clear_entries():
    name_entry.delete(0, tk.END)
    condition_entry.delete(0, tk.END)
    diagnosis_entry.delete(0, tk.END)
    tests_entry.delete(0, tk.END)
    procedure_entry.delete(0, tk.END)

def load_selected(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])["values"]
        name_entry.delete(0, tk.END); name_entry.insert(0, item[1])
        # تاريخ يتظبط في DateEntry
        condition_entry.delete(0, tk.END); condition_entry.insert(0, item[3])
        diagnosis_entry.delete(0, tk.END); diagnosis_entry.insert(0, item[4])
        tests_entry.delete(0, tk.END); tests_entry.insert(0, item[5])
        procedure_entry.delete(0, tk.END); procedure_entry.insert(0, item[6])

def show_records():
    for row in tree.get_children():
        tree.delete(row)
    c.execute("SELECT * FROM patients")
    for row in c.fetchall():
        tree.insert("", "end", values=row)

def export_excel():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if file_path:
        c.execute("SELECT * FROM patients")
        data = c.fetchall()
        headers = ["ID", "الاسم", "التاريخ", "الحالة المرضية", "التشخيص", "نوع الفحوص", "الإجراء المطلوب"]
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        messagebox.showinfo("تم", "تم حفظ الملف")

# ====== نافذة الروشتة ======
def open_prescription_window():
    pres_win = tk.Toplevel(root)
    pres_win.title("🧾 إنشاء روشتة")
    pres_win.geometry("400x300")

    tk.Label(pres_win, text="👨‍⚕️ اسم الدكتور:").pack()
    doctor = tk.Entry(pres_win); doctor.insert(0, "دكتور يحيى الناقه"); doctor.pack()

    tk.Label(pres_win, text="👤 اسم المريض:").pack()
    patient = tk.Entry(pres_win); patient.pack()

    tk.Label(pres_win, text="📅 التاريخ:").pack()
    date_p = DateEntry(pres_win, date_pattern='yyyy-mm-dd'); date_p.pack()

    tk.Label(pres_win, text="🧠 التشخيص:").pack()
    diag = tk.Entry(pres_win); diag.pack()

    tk.Label(pres_win, text="💊 العلاج:").pack()
    medicine = tk.Entry(pres_win); medicine.pack()

    def save_prescription():
        c.execute("INSERT INTO prescriptions (doctor, patient_name, date, diagnosis, medicine) VALUES (?, ?, ?, ?, ?)",
                  (doctor.get(), patient.get(), date_p.get_date().strftime("%Y-%m-%d"), diag.get(), medicine.get()))
        conn.commit()
        messagebox.showinfo("تم", "تم حفظ الروشتة")
        generate_pdf(doctor.get(), patient.get(), date_p.get_date().strftime("%Y-%m-%d"), diag.get(), medicine.get())
        pres_win.destroy()

    tk.Button(pres_win, text="💾 حفظ وطباعة PDF", command=save_prescription).pack(pady=10)

# ====== إنشاء PDF يدعم العربي ======
def draw_ar_text(pdf, text, x, y, size=12):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    pdf.setFont("Arial", size)
    pdf.drawRightString(x, y, bidi_text)

def generate_pdf(doctor, patient, date, diagnosis, medicine):
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf = canvas.Canvas(file_path, pagesize=A5)
        width, height = A5

        draw_ar_text(pdf, "🏥 روشتة طبية", width - 100, height - 40, 18)
        draw_ar_text(pdf, f"👨‍⚕️ الطبيب: {doctor}", width - 40, height - 100)
        draw_ar_text(pdf, f"👤 المريض: {patient}", width - 40, height - 130)
        draw_ar_text(pdf, f"📅 التاريخ: {date}", width - 40, height - 160)
        draw_ar_text(pdf, f"🧠 التشخيص: {diagnosis}", width - 40, height - 190)
        draw_ar_text(pdf, f"💊 العلاج: {medicine}", width - 40, height - 220)

        pdf.save()
        messagebox.showinfo("تم", "تم إنشاء روشتة PDF تدعم العربي")

# ====== واجهة البرنامج ======
root = tk.Tk()
root.title("🏥 نظام عيادة العظام")
root.geometry("1000x550")

# ====== الإدخالات ======
labels = ["👤 اسم المريض:", "📅 التاريخ:", "🩺 الحالة المرضية:", "🧠 التشخيص:", "🔬 نوع الفحوص:", "📝 الإجراء المطلوب:"]
entries = []
for i, text in enumerate(labels):
    tk.Label(root, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
    if i == 1:  # خانة التاريخ
        e = DateEntry(root, date_pattern='yyyy-mm-dd')
    else:
        e = tk.Entry(root, width=30)
    e.grid(row=i, column=1, padx=5, pady=5)
    entries.append(e)

name_entry, date_entry, condition_entry, diagnosis_entry, tests_entry, procedure_entry = entries

# ====== الأزرار في صف مرتب ======
button_frame = tk.Frame(root)
button_frame.grid(row=6, column=0, columnspan=5, pady=10)

tk.Button(button_frame, text="➕ إضافة", width=12, command=add_patient).pack(side="left", padx=5)
tk.Button(button_frame, text="✏️ تعديل", width=12, command=update_patient).pack(side="left", padx=5)
tk.Button(button_frame, text="🗑️ حذف", width=12, command=delete_patient).pack(side="left", padx=5)
tk.Button(button_frame, text="📤 حفظ Excel", width=12, command=export_excel).pack(side="left", padx=5)
tk.Button(button_frame, text="🧾 روشتة", width=12, command=open_prescription_window).pack(side="left", padx=5)

# ====== البحث ======
tk.Label(root, text="🔍 بحث:").grid(row=7, column=0, padx=5, pady=5)
search_entry = tk.Entry(root, width=30); search_entry.grid(row=7, column=1, padx=5, pady=5)
tk.Button(root, text="بحث", command=search_patient).grid(row=7, column=2, padx=5)
tk.Button(root, text="عرض الكل", command=show_records).grid(row=7, column=3, padx=5)

# ====== الجدول ======
columns = ("ID", "الاسم", "التاريخ", "الحالة المرضية", "التشخيص", "نوع الفحوص", "الإجراء المطلوب")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.grid(row=8, column=0, columnspan=5, pady=10)
tree.bind("<ButtonRelease-1>", load_selected)

show_records()
root.mainloop()
