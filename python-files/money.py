import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

transactions = []

def add_transaction():
    try:
        amount = float(amount_entry.get())
        category = category_var.get()
        type_ = type_var.get()
        note = note_entry.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if type_ == "هزینه":
            amount = -abs(amount)

        transactions.append({
            "تاریخ": date,
            "مبلغ": amount,
            "نوع": type_,
            "دسته‌بندی": category,
            "توضیح": note
        })

        update_balance()
        messagebox.showinfo("ثبت شد", "✅ تراکنش با موفقیت ثبت شد.")
        clear_fields()
    except ValueError:
        messagebox.showerror("خطا", "لطفاً مبلغ معتبر وارد کنید.")

def update_balance():
    total = sum(t["مبلغ"] for t in transactions)
    balance_var.set(f"💰 موجودی فعلی: {total:.2f} تومان")

def clear_fields():
    amount_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)

def save_data():
    if transactions:
        df = pd.DataFrame(transactions)
        df.to_csv("finance_data.csv", index=False)
        messagebox.showinfo("ذخیره شد", "✅ اطلاعات ذخیره شدند.")
    else:
        messagebox.showwarning("هشدار", "هیچ تراکنشی ثبت نشده است.")

def show_chart():
    if transactions:
        df = pd.DataFrame(transactions)
        df["ماه"] = pd.to_datetime(df["تاریخ"]).dt.strftime("%Y-%m")
        monthly = df.groupby(["ماه", "نوع"])["مبلغ"].sum().unstack().fillna(0)

        monthly.plot(kind="bar", figsize=(8, 4), color=["green", "red"])
        plt.title("📊 نمودار درآمد و هزینه ماهانه")
        plt.ylabel("مبلغ (تومان)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showwarning("هشدار", "هیچ داده‌ای برای نمایش وجود ندارد.")

# رابط گرافیکی
window = tk.Tk()
window.title("💸 مدیریت مالی شخصی")
window.geometry("500x450")
window.configure(bg="#f7f7f7")
window.resizable(False, False)

# موجودی
balance_var = tk.StringVar()
balance_label = tk.Label(window, textvariable=balance_var, font=("B Nazanin", 16), bg="#f7f7f7", fg="#333")
balance_label.pack(pady=10)
update_balance()

# فرم ورود اطلاعات
form_frame = tk.Frame(window, bg="#f7f7f7")
form_frame.pack(pady=10)

tk.Label(form_frame, text="مبلغ:", bg="#f7f7f7").grid(row=0, column=0, sticky="e")
amount_entry = tk.Entry(form_frame)
amount_entry.grid(row=0, column=1)

tk.Label(form_frame, text="نوع:", bg="#f7f7f7").grid(row=1, column=0, sticky="e")
type_var = tk.StringVar(value="هزینه")
ttk.Combobox(form_frame, textvariable=type_var, values=["هزینه", "درآمد"], width=17).grid(row=1, column=1)

tk.Label(form_frame, text="دسته‌بندی:", bg="#f7f7f7").grid(row=2, column=0, sticky="e")
category_var = tk.StringVar(value="عمومی")
ttk.Combobox(form_frame, textvariable=category_var, values=["غذا", "حمل‌ونقل", "حقوق", "سرگرمی", "دیگر"], width=17).grid(row=2, column=1)

tk.Label(form_frame, text="توضیح:", bg="#f7f7f7").grid(row=3, column=0, sticky="e")
note_entry = tk.Entry(form_frame)
note_entry.grid(row=3, column=1)

# دکمه‌ها
btn_frame = tk.Frame(window, bg="#f7f7f7")
btn_frame.pack(pady=15)

ttk.Button(btn_frame, text="➕ افزودن تراکنش", command=add_transaction).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="💾 ذخیره اطلاعات", command=save_data).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="📈 نمایش نمودار", command=show_chart).grid(row=0, column=2, padx=5)

window.mainloop()
