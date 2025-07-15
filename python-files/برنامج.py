from tkinter import *
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os

# مسار ملف Excel
excel_file = "بيانات_الكتب.xlsx"

# إنشاء الملف إذا لم يكن موجودًا
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["نوع الكتاب", "الاسم", "رقم الهاتف", "نوع السيارة", "حالة الاستلام", "رقم الكتاب"])
    df.to_excel(excel_file, index=False)

# تحميل البيانات الحالية
data = pd.read_excel(excel_file)

# دوال البرنامج
def save_data():
    new_data = {
        "نوع الكتاب": book_type_var.get(),
        "الاسم": name_var.get(),
        "رقم الهاتف": phone_var.get(),
        "نوع السيارة": car_type_var.get(),
        "حالة الاستلام": status_var.get(),
        "رقم الكتاب": book_number_var.get()
    }
    global data
    data = pd.concat([data, pd.DataFrame([new_data])], ignore_index=True)
    data.to_excel(excel_file, index=False)
    messagebox.showinfo("تم الحفظ", "تم حفظ البيانات بنجاح.")
    clear_fields()

def clear_fields():
    for var in [book_type_var, name_var, phone_var, car_type_var, status_var, book_number_var]:
        var.set("")

def search_data():
    search_term = search_var.get()
    if not search_term:
        messagebox.showwarning("تحذير", "يرجى إدخال كلمة للبحث.")
        return
    results = data[data.apply(lambda row: search_term in row.values.astype(str), axis=1)]
    for row in tree.get_children():
        tree.delete(row)
    for _, row in results.iterrows():
        tree.insert("", "end", values=list(row))

def export_to_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        messagebox.showerror("خطأ", "يجب تثبيت مكتبة fpdf: pip install fpdf")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for i, row in data.iterrows():
        line = " | ".join([f"{col}: {row[col]}" for col in data.columns])
        pdf.cell(200, 10, txt=line, ln=True)
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if save_path:
        pdf.output(save_path)
        messagebox.showinfo("تم", "تم تصدير البيانات إلى PDF.")

# واجهة المستخدم
root = Tk()
root.title("برنامج تسجيل الكتب")
root.geometry("800x600")

book_type_var = StringVar()
name_var = StringVar()
phone_var = StringVar()
car_type_var = StringVar()
status_var = StringVar()
book_number_var = StringVar()
search_var = StringVar()

fields = [
    ("نوع الكتاب", book_type_var),
    ("الاسم", name_var),
    ("رقم الهاتف", phone_var),
    ("نوع السيارة", car_type_var),
    ("حالة الاستلام", status_var),
    ("رقم الكتاب", book_number_var),
]

for i, (label_text, var) in enumerate(fields):
    Label(root, text=label_text, anchor='w').grid(row=i, column=0, sticky=W, padx=10, pady=5)
    Entry(root, textvariable=var, width=30).grid(row=i, column=1, pady=5)

Button(root, text="حفظ", command=save_data).grid(row=6, column=0, pady=10)
Button(root, text="تفريغ", command=clear_fields).grid(row=6, column=1, pady=10)

Label(root, text="بحث").grid(row=7, column=0, sticky=W, padx=10)
Entry(root, textvariable=search_var, width=30).grid(row=7, column=1, pady=5)
Button(root, text="بحث", command=search_data).grid(row=7, column=2)

tree = ttk.Treeview(root, columns=[f"#{i}" for i in range(1, 7)], show="headings")
tree.grid(row=8, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

for i, (label_text, _) in enumerate(fields):
    tree.heading(f"#{i+1}", text=label_text)
    tree.column(f"#{i+1}", width=100)

Button(root, text="تصدير إلى PDF", command=export_to_pdf).grid(row=9, column=1, pady=10)

root.mainloop()
