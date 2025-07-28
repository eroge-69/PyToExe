import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# دالة الحساب
def احسب():
    try:
        نسبة = float(ضريبة.get()) / 100
        قيمة = float(المبلغ.get())

        if نوع.get() == "صافي":
            الصافي = قيمة
            القيمة_الضريبية = الصافي * نسبة
            الإجمالي = الصافي + القيمة_الضريبية
        else:
            الإجمالي = قيمة
            الصافي = الإجمالي / (1 + نسبة)
            القيمة_الضريبية = الإجمالي - الصافي

        # تحديث النتائج
        عرض(حقل_صافي, f"{الصافي:.4f}")
        عرض(حقل_ضريبة, f"{القيمة_الضريبية:.4f}")
        عرض(حقل_إجمالي, f"{الإجمالي:.4f}")

    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة")

# تحديث حقل
def عرض(الحقل, قيمة):
    الحقل.config(state="normal")
    الحقل.delete(0, tk.END)
    الحقل.insert(0, قيمة)
    الحقل.config(state="readonly")

# نسخ إلى الحافظة
def نسخ(الحقل):
    نص = الحقل.get()
    نافذة.clipboard_clear()
    نافذة.clipboard_append(نص)
    النسخ_مؤقت.config(text=f"✅ تم نسخ: {نص}")
    نافذة.after(2000, lambda: النسخ_مؤقت.config(text=""))

# الواجهة
نافذة = tk.Tk()
نافذة.title("💰 حاسبة الضريبة الذكية")
نافذة.geometry("420x420")
نافذة.configure(bg="#f0faff")
نافذة.resizable(False, False)

# العنوان
tk.Label(نافذة, text="📊 حاسبة الضريبة", font=("Tahoma", 16, "bold"), bg="#f0faff", fg="#003366").pack(pady=10)

# نوع الحساب
نوع = tk.StringVar(value="صافي")
نوع_إطار = tk.Frame(نافذة, bg="#f0faff")
نوع_إطار.pack()
tk.Radiobutton(نوع_إطار, text="من صافي السعر", variable=نوع, value="صافي", bg="#f0faff", font=("Arial", 10)).pack(side="left", padx=10)
tk.Radiobutton(نوع_إطار, text="من السعر الإجمالي", variable=نوع, value="إجمالي", bg="#f0faff", font=("Arial", 10)).pack(side="left", padx=10)

# إدخالات
def حقل_إدخال(عنوان, المتغير):
    إطار = tk.Frame(نافذة, bg="#f0faff")
    إطار.pack(pady=5)
    tk.Label(إطار, text=عنوان, width=15, anchor="w", bg="#f0faff").pack(side="left")
    إدخال = tk.Entry(إطار, textvariable=المتغير, font=("Arial", 12), justify="center")
    إدخال.pack(side="left", padx=10)
    return إدخال

المبلغ = tk.StringVar()
ضريبة = tk.StringVar(value="16")
حقل_إدخال("💵 المبلغ:", المبلغ)
حقل_إدخال("٪ نسبة الضريبة:", ضريبة)

# زر الحساب
tk.Button(نافذة, text="احسب الآن", font=("Arial", 11, "bold"), bg="#007acc", fg="white", width=20, command=احسب).pack(pady=10)

# النتائج
def بطاقة(العنوان, الحقل_مرجعي):
    إطار = tk.Frame(نافذة, bg="#d9f2ff", bd=1, relief="solid")
    إطار.pack(fill="x", padx=20, pady=5)
    tk.Label(إطار, text=العنوان, width=15, anchor="w", bg="#d9f2ff").pack(side="left", padx=5)
    إدخال = tk.Entry(إطار, state="readonly", font=("Arial", 12), justify="center", relief="flat")
    إدخال.pack(side="left", expand=True, fill="x", padx=5)
    tk.Button(إطار, text="📋 نسخ", command=lambda: نسخ(إدخال), bg="#33b5e5", fg="white").pack(side="right", padx=5)
    return إدخال

حقل_صافي = بطاقة("صافي السعر:", "صافي")
حقل_ضريبة = بطاقة("قيمة الضريبة:", "ضريبة")
حقل_إجمالي = بطاقة("الإجمالي الكلي:", "إجمالي")

# إشعار النسخ
النسخ_مؤقت = tk.Label(نافذة, text="", font=("Arial", 9), fg="green", bg="#f0faff")
النسخ_مؤقت.pack(pady=5)

نافذة.mainloop()
