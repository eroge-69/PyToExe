import tkinter as tk
from tkinter import messagebox

def login():
    """
    الدالة التي يتم استدعاؤها عند الضغط على زر تسجيل الدخول.
    تقوم بالتحقق من اسم المستخدم وكلمة المرور.
    """
    username = username_entry.get()
    password = password_entry.get()

    if username == "nawaf" and password == "1234":
        messagebox.showinfo("نجاح", "تم تسجيل الدخول بنجاح!")
        # يمكنك إضافة الكود الخاص بك هنا لتوجيه المستخدم لصفحة أخرى
        root.destroy()  # لإغلاق نافذة تسجيل الدخول بعد النجاح
    else:
        messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة.")

# إنشاء النافذة الرئيسية
root = tk.Tk()
root.title("تسجيل الدخول")
root.geometry("300x200") # تحديد حجم النافذة

# إنشاء إطار لتنظيم العناصر
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

# تسمية حقل اسم المستخدم
username_label = tk.Label(frame, text="اسم المستخدم:")
username_label.pack(pady=5)

# حقل إدخال اسم المستخدم
username_entry = tk.Entry(frame)
username_entry.pack(pady=5)
username_entry.focus_set() # لجعل حقل اسم المستخدم هو النشط عند فتح الواجهة

# تسمية حقل كلمة المرور
password_label = tk.Label(frame, text="كلمة المرور:")
password_label.pack(pady=5)

# حقل إدخال كلمة المرور (مع إخفاء الأحرف)
password_entry = tk.Entry(frame, show="*")
password_entry.pack(pady=5)

# زر تسجيل الدخول
login_button = tk.Button(frame, text="تسجيل الدخول", command=login)
login_button.pack(pady=10)

# تشغيل حلقة الواجهة الرسومية
root.mainloop()