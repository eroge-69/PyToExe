import tkinter as tk
from tkinter import messagebox

def حساب_بعد_الضريبة():
    try:
        السعر = float(entry_السعر.get())
        نسبة = float(entry_نسبة_الضريبة.get()) / 100
        السعر_بعد = السعر * (1 + نسبة)
        entry_النتيجة.delete(0, tk.END)
        entry_النتيجة.insert(0, f"{السعر_بعد:.4f}")
    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في الحقول.")

def حساب_قبل_الضريبة():
    try:
        السعر = float(entry_السعر.get())
        نسبة = float(entry_نسبة_الضريبة.get()) / 100
        السعر_قبل = السعر / (1 + نسبة)
        entry_النتيجة.delete(0, tk.END)
        entry_النتيجة.insert(0, f"{السعر_قبل:.4f}")
    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في الحقول.")

# نافذة البرنامج
root = tk.Tk()
root.title("حساب السعر مع / بدون الضريبة")
root.geometry("400x300")
root.resizable(False, False)
root.configure(bg="#f5faff")

font = ("Tahoma", 12)

# إدخال السعر
tk.Label(root, text="أدخل السعر:", font=font, bg="#f5faff").pack(pady=5)
entry_السعر = tk.Entry(root, font=font, justify="center")
entry_السعر.pack()

# إدخال نسبة الضريبة
tk.Label(root, text="نسبة الضريبة (%):", font=font, bg="#f5faff").pack(pady=5)
entry_نسبة_الضريبة = tk.Entry(root, font=font, justify="center")
entry_نسبة_الضريبة.insert(0, "16")
entry_نسبة_الضريبة.pack()

# الأزرار
tk.Button(root, text="حساب السعر بعد الضريبة", font=font, bg="#4caf50", fg="white", command=حساب_بعد_الضريبة).pack(pady=10)
tk.Button(root, text="حساب السعر قبل الضريبة", font=font, bg="#2196f3", fg="white", command=حساب_قبل_الضريبة).pack()

# حقل النتيجة
tk.Label(root, text="النتيجة:", font=font, bg="#f5faff").pack(pady=5)
entry_النتيجة = tk.Entry(root, font=font, justify="center")
entry_النتيجة.pack()

# تشغيل البرنامج
root.mainloop()
