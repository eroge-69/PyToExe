import tkinter as tk
from tkinter import messagebox, ttk

# قائمة لحفظ المعاملات
المعاملات = []

# وظيفة إضافة معاملة
def اضافة_معاملة():
    نافذة = tk.Toplevel(root)
    نافذة.title("إضافة معاملة")
    نافذة.configure(bg="#2b2b2b")
    نافذة.geometry("500x500")  # تكبير النافذة

    tk.Label(نافذة, text="إضافة معاملة", fg="white", bg="#2b2b2b", font=("Arial", 16, "bold")).pack(pady=15)
    
    tk.Label(نافذة, text="عنوان المعاملة (مطلوب):", fg="white", bg="#2b2b2b").pack(anchor="w", padx=10)
    entry_title = tk.Entry(نافذة, width=50)
    entry_title.pack(padx=10, pady=5)
    
    tk.Label(نافذة, text="رقم الهوية (اختياري):", fg="white", bg="#2b2b2b").pack(anchor="w", padx=10)
    entry_id = tk.Entry(نافذة, width=50)
    entry_id.pack(padx=10, pady=5)
    
    tk.Label(نافذة, text="التاريخ (اختياري):", fg="white", bg="#2b2b2b").pack(anchor="w", padx=10)
    entry_date = tk.Entry(نافذة, width=50)
    entry_date.pack(padx=10, pady=5)
    
    tk.Label(نافذة, text="رقم المعاملة:", fg="white", bg="#2b2b2b").pack(anchor="w", padx=10)
    entry_number = tk.Entry(نافذة, width=50)
    entry_number.pack(padx=10, pady=5)
    
    # زر المسح الضوئي
    tk.Button(نافذة, text="مسح ضوئي (سكنر)", fg="white", bg="#444", font=("Arial", 12, "bold"),
              command=lambda: messagebox.showinfo("مسح ضوئي", "تم اختيار السكنر!")).pack(pady=15)
    
    # زر حفظ المعاملة
    def حفظ_المعاملة():
        عنوان = entry_title.get()
        هوية = entry_id.get()
        تاريخ = entry_date.get()
        رقم = entry_number.get()
        if عنوان.strip() == "":
            messagebox.showerror("خطأ", "العنوان مطلوب!")
            return
        المعاملة = {"عنوان": عنوان, "رقم الهوية": هوية, "التاريخ": تاريخ, "رقم المعاملة": رقم}
        المعاملات.append(المعاملة)
        messagebox.showinfo("نجاح", "تمت إضافة المعاملة بنجاح!")
        نافذة.destroy()
        
    tk.Button(نافذة, text="حفظ المعاملة", fg="white", bg="#5a5", font=("Arial", 12, "bold"), command=حفظ_المعاملة).pack(pady=10)

# وظيفة البحث عن معاملة
def بحث_عن_معاملة():
    نافذة = tk.Toplevel(root)
    نافذة.title("بحث عن معاملة")
    نافذة.configure(bg="#2b2b2b")
    نافذة.geometry("500x400")

    tk.Label(نافذة, text="بحث عن معاملة", fg="white", bg="#2b2b2b", font=("Arial", 16, "bold")).pack(pady=15)
    tk.Label(نافذة, text="يمكن البحث باستخدام العنوان أو رقم الهوية أو رقم المعاملة", fg="white", bg="#2b2b2b").pack(pady=5)
    
    entry_search = tk.Entry(نافذة, width=50)
    entry_search.pack(pady=5)

    listbox = tk.Listbox(نافذة, width=80)
    listbox.pack(pady=10)

    def تنفيذ_البحث():
        listbox.delete(0, tk.END)
        نص_البحث = entry_search.get().lower()
        for idx, معامل in enumerate(المعاملات):
            if نص_البحث in معامل["عنوان"].lower() or نص_البحث in معامل["رقم الهوية"].lower() or نص_البحث in معامل["رقم المعاملة"].lower():
                listbox.insert(tk.END, f"{idx+1}. {معامل['عنوان']} | {معامل['رقم الهوية']} | {معامل['رقم المعاملة']} | {معامل['التاريخ']}")

    tk.Button(نافذة, text="بحث", fg="white", bg="#5a5", font=("Arial", 12, "bold"), command=تنفيذ_البحث).pack(pady=5)

# وظيفة تعديل أو حذف معاملة
def تعديل_او_حذف():
    نافذة = tk.Toplevel(root)
    نافذة.title("تعديل أو حذف معاملة")
    نافذة.configure(bg="#2b2b2b")
    نافذة.geometry("600x500")

    tk.Label(نافذة, text="تعديل أو حذف معاملة", fg="white", bg="#2b2b2b", font=("Arial", 16, "bold")).pack(pady=15)

    entry_search = tk.Entry(نافذة, width=50)
    entry_search.pack(pady=5)

    listbox = tk.Listbox(نافذة, width=100)
    listbox.pack(pady=10)

    def تحديث_القائمة():
        listbox.delete(0, tk.END)
        for idx, معامل in enumerate(المعاملات):
            listbox.insert(tk.END, f"{idx+1}. {معامل['عنوان']} | {معامل['رقم الهوية']} | {معامل['رقم المعاملة']} | {معامل['التاريخ']}")

    def تنفيذ_البحث():
        نص_البحث = entry_search.get().lower()
        listbox.delete(0, tk.END)
        for idx, معامل in enumerate(المعاملات):
            if نص_البحث in معامل["عنوان"].lower() or نص_البحث in معامل["رقم الهوية"].lower() or نص_البحث in معامل["رقم المعاملة"].lower():
                listbox.insert(tk.END, f"{idx+1}. {معامل['عنوان']} | {معامل['رقم الهوية']} | {معامل['رقم المعاملة']} | {معامل['التاريخ']}")

    def حذف_المعاملة():
        اختيار = listbox.curselection()
        if not اختيار:
            messagebox.showerror("خطأ", "الرجاء اختيار المعاملة لحذفها")
            return
        idx = اختيار[0]
        del المعاملات[idx]
        تحديث_القائمة()
        messagebox.showinfo("نجاح", "تم حذف المعاملة بنجاح!")

    tk.Button(نافذة, text="بحث", fg="white", bg="#5a5", font=("Arial", 12, "bold"), command=تنفيذ_البحث).pack(pady=5)
    tk.Button(نافذة, text="حذف المعاملة المحددة", fg="white", bg="#d55", font=("Arial", 12, "bold"), command=حذف_المعاملة).pack(pady=5)

    تحديث_القائمة()

# إنشاء الواجهة الرئيسية
root = tk.Tk()
root.title("أرشفة معاملات")
root.configure(bg="#2b2b2b")
root.geometry("500x500")

# الترحيب
tk.Label(root, text="أهلا بك في تطبيق أرشفة معاملات", fg="white", bg="#2b2b2b", font=("Arial", 16, "bold")).pack(pady=20)
tk.Label(root, text="برنامج بسيط لا يأخذ مساحة", fg="white", bg="#2b2b2b").pack(pady=5)

# الأزرار
tk.Button(root, text="إضافة معاملة", width=30, command=اضافة_معاملة).pack(pady=10)
tk.Button(root, text="بحث عن معاملة", width=30, command=بحث_عن_معاملة).pack(pady=10)
tk.Button(root, text="تعديل أو حذف معاملة", width=30, command=تعديل_او_حذف).pack(pady=10)

# تواصل للبرنامج
tk.Label(root, text="للتواصل لعمل برنامج الرجاء التواصل عن طريق الواتس اب: 0550178859", 
         fg="white", bg="#2b2b2b", wraplength=480, justify="center").pack(side="bottom", pady=20)

root.mainloop()