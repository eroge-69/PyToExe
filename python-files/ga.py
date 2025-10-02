import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

DATA_FILE = "المخزن/data.json"

# --------------------- كلمة السر ---------------------
def check_password():
    password = simpledialog.askstring("كلمة السر", "أدخل كلمة السر:", show="*")
    if password != "135":
        messagebox.showerror("خطأ", "كلمة السر غير صحيحة!")
        root.destroy()

# --------------------- تحميل/حفظ البيانات ---------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data():
    os.makedirs("المخزن", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --------------------- إضافة ---------------------
def add_item():
    name = entry_name.get().strip()
    qty = entry_qty.get().strip()
    status = combo_status.get()
    person = entry_person.get().strip()
    fatur = entry_fatur.get().strip()
    wasl = entry_wasl.get().strip()
    note = entry_note.get().strip()

    if not name or not qty or not status:
        messagebox.showwarning("تنبيه", "الرجاء ملء جميع الخانات!")
        return

    try:
        qty = int(qty)
        if status == "بيع":
            qty = -abs(qty)
    except:
        messagebox.showerror("خطأ", "العدد غير صحيح!")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    item = {
        "الاسم": name,
        "العدد": qty,
        "الحالة": status,
        "الموظف": person,
        "فاتورة": fatur,
        "الوصل": wasl,
        "ملاحظة": note,
        "التاريخ": now
    }

    data.append(item)
    save_data()
    update_display()
    clear_inputs()

def clear_inputs():
    entry_name.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    combo_status.set("")
    entry_person.delete(0, tk.END)
    entry_fatur.delete(0, tk.END)
    entry_wasl.delete(0, tk.END)
    entry_note.delete(0, tk.END)

# --------------------- عرض ---------------------
def update_display(filter_name=None):
    for row in tree.get_children():
        tree.delete(row)
    total = 0
    for item in data:
        try:
            if filter_name and filter_name not in item.get("الاسم", ""):
                continue
            tree.insert("", tk.END, values=(
                item.get("الاسم",""),
                item.get("العدد",""),
                item.get("الحالة",""),
                item.get("الموظف",""),
                item.get("فاتورة",""),
                item.get("الوصل",""),
                item.get("ملاحظة",""),
                item.get("التاريخ","")
            ))
            total += int(item.get("العدد",0))
        except:
            continue
    lbl_total.config(text=f"المجموع الكلي: {total}")

# --------------------- بحث ---------------------
def search_item():
    query = entry_search.get().strip()
    if not query:
        messagebox.showinfo("بحث", "الرجاء كتابة اسم البضاعة")
    else:
        update_display(query)

# --------------------- تعديل ---------------------
def edit_item():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("تنبيه", "لم يتم اختيار أي عنصر!")
        return
    index = tree.index(selected[0])
    item = data[index]
    clear_inputs()
    entry_name.insert(0, item.get("الاسم",""))
    entry_qty.insert(0, abs(int(item.get("العدد",0))))
    combo_status.set(item.get("الحالة",""))
    entry_person.insert(0, item.get("الموظف",""))
    entry_fatur.insert(0, item.get("فاتورة",""))
    entry_wasl.insert(0, item.get("الوصل",""))
    entry_note.insert(0, item.get("ملاحظة",""))
    del data[index]
    save_data()
    update_display()

# --------------------- حذف ---------------------
def delete_item():
    selected = tree.selection()
    if not selected:
        return
    if messagebox.askyesno("تأكيد", "هل تريد الحذف؟"):
        index = tree.index(selected[0])
        del data[index]
        save_data()
        update_display()

# --------------------- حفظ PDF (جدول) ---------------------
def save_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf")
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=A4)
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))  # خط لدعم العربية

    width, height = A4

    # العنوان الكبير
    c.setFont("STSong-Light", 24)
    c.drawCentredString(width/2, height - 50, "00")

    # التاريخ
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.setFont("STSong-Light", 12)
    c.drawCentredString(width/2, height - 70, now)

    # خط فاصل
    c.line(30, height - 80, width - 30, height - 80)

    # رؤوس الأعمدة
    headers = ["الاسم", "العدد", "الحالة", "الموظف", "فاتورة", "الوصل", "ملاحظة", "التاريخ"]
    col_widths = [70, 50, 60, 70, 70, 70, 80, 100]
    x_positions = [30]
    for w in col_widths[:-1]:
        x_positions.append(x_positions[-1] + w)

    y = height - 100
    c.setFont("STSong-Light", 12)
    for i, h in enumerate(headers):
        c.drawString(x_positions[i], y, h)

    y -= 20
    # البيانات
    for item in data:
        values = [
            item.get("الاسم",""),
            str(item.get("العدد","")),
            item.get("الحالة",""),
            item.get("الموظف",""),
            item.get("فاتورة",""),
            item.get("الوصل",""),
            item.get("ملاحظة",""),
            item.get("التاريخ","")
        ]
        for i, val in enumerate(values):
            c.drawString(x_positions[i], y, str(val))
        y -= 20
        if y < 50:
            c.showPage()
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            c.setFont("STSong-Light", 12)
            y = height - 50

    c.save()
    messagebox.showinfo("PDF", "تم الحفظ بنجاح!")

# --------------------- الواجهة ---------------------
root = tk.Tk()
root.title("کۆگــای گەراجی قوشــتەپە")
root.configure(bg="white")
root.state("zoomed")  # ملء الشاشة

check_password()

# العنوان
lbl_title = tk.Label(root, text="گـۆگای گەراجی قوشـتەپە", font=("Arial", 35, "bold"), bg="white")
lbl_title.pack(pady=22)
tk.Frame(root, height=6, bg="red").pack(fill="x")


frame = tk.Frame(root, bg="white")
frame.pack(fill="both", expand=True)


# عرض البيانات
tree = ttk.Treeview(frame, columns=("الاسم","العدد","الحالة","الموظف","فاتورة","الوصل","ملاحظة","التاريخ"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.pack(side="left", fill="both", expand=True)

# إدخال البيانات
right = tk.Frame(frame, bg="white")
right.pack(side="right", fill="y", padx=10)

tk.Label(right, text="اسم البضاعة").pack()
entry_name = tk.Entry(right, width=25)
entry_name.pack()

tk.Label(right, text="العدد").pack()
entry_qty = tk.Entry(right, width=25)
entry_qty.pack()

tk.Label(right, text="الحالة").pack()
combo_status = ttk.Combobox(right, values=["شراء", "بيع"], width=23)
combo_status.pack()

tk.Label(right, text="الموظف").pack()
entry_person = tk.Entry(right, width=25)
entry_person.pack()

tk.Label(right, text="فاتورة").pack()
entry_fatur = tk.Entry(right, width=25)
entry_fatur.pack()

tk.Label(right, text="الوصل").pack()
entry_wasl = tk.Entry(right, width=25)
entry_wasl.pack()

tk.Label(right, text="ملاحظة").pack()
entry_note = tk.Entry(right, width=25)
entry_note.pack()

tk.Button(right, text="إضافة", command=add_item).pack(pady=5)
tk.Button(right, text="مسح", command=clear_inputs).pack()

# البحث
entry_search = tk.Entry(right, width=30)
entry_search.pack(pady=10)
tk.Button(right, text="بحث", command=search_item).pack()
tk.Button(right, text="عرض الكل", command=lambda: update_display()).pack(pady=5)

# أزرار أسفل
bottom = tk.Frame(root, bg="white")
bottom.pack(fill="x", pady=30)

tk.Button(bottom, text="تعديل", command=edit_item).pack(side="left", padx=5)
tk.Button(bottom, text="حذف", command=delete_item).pack(side="left", padx=5)
tk.Button(bottom, text="طباعة", command=lambda: messagebox.showinfo("طباعة","جهز الطابعة :)")).pack(side="left", padx=5)
tk.Button(bottom, text="حفظ PDF", command=save_pdf).pack(side="left", padx=5)

lbl_total = tk.Label(root, text="المجموع الكلي: 0", fg="black", font=("Arial", 18), bg="white")
lbl_total.pack()

lbl_sig = tk.Label(root, text=" By: G.A", fg="red", font=("Arial", 9), bg="white")
lbl_sig.pack(side="left")

data = load_data()
update_display()

root.mainloop()
