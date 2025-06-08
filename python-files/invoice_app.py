import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime
import os

# --- إعداد المسارات ---
base_file_path = r"C:\Users\moram\Desktop\قاعدة البيانات.xlsx"
log_file_path = r"C:\Users\moram\Desktop\سجل الفواتير.xlsx"

# --- 1. تحميل بيانات العملاء من ملف Excel ---
def load_client_data():
    try:
        sheet_name = 0
        df = pd.read_excel(base_file_path, sheet_name=sheet_name)

        if "اسم العميل" not in df.columns:
            raise Exception("لا يوجد عمود باسم 'اسم العميل'")

        client_names = df["اسم العميل"].unique().tolist()
        return df, client_names

    except FileNotFoundError:
        messagebox.showerror("خطأ", "لم يتم العثور على ملف Excel")
        return None, None
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل في قراءة ملف Excel:\n{e}")
        return None, None

# --- 2. استرجاع بيانات العميل ---
def fetch_client(event=None):
    if df is None:
        messagebox.showerror("خطأ", "لم يتم تحميل البيانات")
        return

    selected_name = combo_clients.get()
    if not selected_name:
        return

    client_row = df[df["اسم العميل"] == selected_name]

    if client_row.empty:
        messagebox.showinfo("معلومة", "لم يتم العثور على العميل")
        return

    try:
        name = client_row["اسم العميل"].values[0]
        balance = float(client_row["الرصيد الحالي"].values[0])
    except (KeyError, ValueError, TypeError):
        messagebox.showerror("خطأ", "قيمة الرصيد الحالي غير صالحة أو العمود مفقود")
        return

    entry_name.config(state='normal')
    entry_balance.config(state='normal')

    entry_name.delete(0, tk.END)
    entry_name.insert(0, name)

    entry_balance.delete(0, tk.END)
    entry_balance.insert(0, f"{balance:.2f}")

    entry_name.config(state='readonly')
    entry_balance.config(state='readonly')

# --- 3. حفظ الرصيد الجديد في ملف العملاء ---
def save_updated_balance(name, new_balance):
    try:
        df.loc[df["اسم العميل"] == name, "الرصيد الحالي"] = new_balance
        df.to_excel(base_file_path, index=False)
    except Exception as e:
        messagebox.showerror("خطأ", f"خطأ أثناء حفظ الرصيد:\n{e}")

# --- 4. تسجيل العملية في سجل الفواتير ---
def log_invoice_operation(name, date, invoice_amount, paid, old_balance, new_balance):
    log_data = {
        "اسم العميل": name,
        "تاريخ الفاتورة": date,
        "قيمة الفاتورة": invoice_amount,
        "المدفوع": paid,
        "الرصيد السابق": old_balance,
        "الرصيد الجديد": new_balance
    }

    try:
        if os.path.exists(log_file_path):
            log_df = pd.read_excel(log_file_path)
            log_df = pd.concat([log_df, pd.DataFrame([log_data])], ignore_index=True)
        else:
            log_df = pd.DataFrame([log_data])

        log_df.to_excel(log_file_path, index=False)
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل في تسجيل الفاتورة:\n{e}")

# --- 5. حساب الرصيد وتسجيل العملية ---
def calculate_final_balance():
    try:
        invoice_amount = float(entry_new_invoice.get())
        paid_amount = float(entry_paid.get())
        current_balance = float(entry_balance.get())
        name = entry_name.get()
        date = datetime.today().strftime("%Y-%m-%d")

        final_balance = current_balance + invoice_amount - paid_amount

        if final_balance < 0:
            result = f"الرصيد الإجمالي للعميل:\n{final_balance:.2f} جنيه\n(له رصيد زائد)"
            label_result.config(fg="green")
        elif final_balance > 0:
            result = f"الرصيد الإجمالي للعميل:\n{-final_balance:.2f} جنيه\n(عليه رصيد)"
            label_result.config(fg="red")
        else:
            result = "الرصيد الإجمالي: 0.00 جنيه"
            label_result.config(fg="black")

        label_result.config(text=result)

        # تحديث الرصيد في الواجهة
        entry_balance.config(state='normal')
        entry_balance.delete(0, tk.END)
        entry_balance.insert(0, f"{final_balance:.2f}")
        entry_balance.config(state='readonly')

        # حفظ الرصيد في ملف العملاء
        save_updated_balance(name, final_balance)

        # تسجيل العملية في سجل الفواتير
        log_invoice_operation(name, date, invoice_amount, paid_amount, current_balance, final_balance)

        messagebox.showinfo("✔تم", "تم حفظ الفاتورة وتحديث الرصيد بنجاح.")

        # 🟢 مسح الحقول بعد العملية:
        entry_new_invoice.delete(0, tk.END)
        entry_paid.delete(0, tk.END)
        label_result.config(text="")

    except ValueError:
        messagebox.showerror("خطأ", "يرجى إدخال أرقام صالحة في الحقول")

# --- 6. واجهة المستخدم ---
window = tk.Tk()
window.title("برنامج إدارة فواتير العملاء")
window.geometry("700x550")
window.resizable(False, False)
window.configure(bg="#f0f0f0")

title_label = tk.Label(window, text="حساب الرصيد الإجمالي وتسجيل الفواتير", font=("Arial", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

df, client_names = load_client_data()
if df is None or client_names is None:
    messagebox.showerror("خطأ", "تعذر تحميل البيانات، سيتم إغلاق البرنامج.")
    window.destroy()
    exit()

label_client_search = tk.Label(window, text="اختر اسم العميل:", font=("Arial", 12), bg="#f0f0f0")
label_client_search.pack()
combo_clients = ttk.Combobox(window, values=client_names, font=("Arial", 12))
combo_clients.pack(pady=5)
combo_clients.bind("<<ComboboxSelected>>", fetch_client)

label_name = tk.Label(window, text="اسم العميل:", font=("Arial", 12), bg="#f0f0f0")
label_name.pack()
entry_name = tk.Entry(window, width=30, font=("Arial", 12), state='readonly')
entry_name.pack(pady=5)

label_balance = tk.Label(window, text="الرصيد الحالي:", font=("Arial", 12), bg="#f0f0f0")
label_balance.pack()
entry_balance = tk.Entry(window, width=30, font=("Arial", 12), state='readonly')
entry_balance.pack(pady=5)

label_new_invoice = tk.Label(window, text="مبلغ الفاتورة الجديدة:", font=("Arial", 12), bg="#f0f0f0")
label_new_invoice.pack()
entry_new_invoice = tk.Entry(window, width=30, font=("Arial", 12))
entry_new_invoice.pack(pady=5)

label_paid = tk.Label(window, text="المدفوع من الفاتورة:", font=("Arial", 12), bg="#f0f0f0")
label_paid.pack()
entry_paid = tk.Entry(window, width=30, font=("Arial", 12))
entry_paid.pack(pady=5)

btn_calculate = tk.Button(window, text="احسب وسجل الفاتورة", command=calculate_final_balance,
                          width=25, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
btn_calculate.pack(pady=10)

label_result = tk.Label(window, text="", font=("Arial", 14), bg="#f0f0f0", justify="center")
label_result.pack(pady=10)

window.mainloop()
