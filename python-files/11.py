import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
from prettytable import PrettyTable
import openpyxl

def save_to_excel(table_data, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "چک‌ها"
    
    # نوشتن هدر جدول
    ws.append(["شماره چک", "مبلغ (تومان)", "تاریخ سررسید"])
    
    # نوشتن داده‌ها
    for row in table_data:
        ws.append([row["شماره چک"], row["مبلغ"], row["تاریخ سررسید"]])
    
    wb.save(filename)

def hesab_chek_gui():
    try:
        ghimat = float(entry_ghimat.get())
        karmazd = float(entry_karmazd.get())
        tedad = int(entry_tedad.get())
        mah_fasele = int(entry_mah_fasele.get())
    except:
        messagebox.showerror("خطا", "لطفاً مقادیر درست وارد کنید!")
        return

    gheymat_kol = ghimat * (1 + karmazd / 100)
    mablagh_har_chek = gheymat_kol / tedad

    today = datetime.today()
    table_data = []
    table = PrettyTable(["شماره چک", "مبلغ (تومان)", "تاریخ سررسید"])
    
    for i in range(1, tedad + 1):
        sarresid = today + timedelta(days=mah_fasele * 30 * i)
        row = {"شماره چک": i, "مبلغ": int(mablagh_har_chek), "تاریخ سررسید": sarresid.strftime("%Y-%m-%d")}
        table_data.append(row)
        table.add_row([row["شماره چک"], row["مبلغ"], row["تاریخ سررسید"]])

    text_table.config(state="normal")
    text_table.delete("1.0", tk.END)
    text_table.insert(tk.END, f"مبلغ کل با کارمزد: {int(gheymat_kol)} تومان\n\n")
    text_table.insert(tk.END, str(table))
    text_table.config(state="disabled")

    # ذخیره به اکسل
    save = messagebox.askyesno("ذخیره اکسل", "می‌خواهید جدول چک‌ها را در فایل اکسل ذخیره کنید؟")
    if save:
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filename:
            save_to_excel(table_data, filename)
            messagebox.showinfo("موفقیت", f"جدول ذخیره شد: {filename}")

# ساخت پنجره
root = tk.Tk()
root.title("محاسبه چک با کارمزد و ماه‌های مختلف")
root.geometry("600x500")

# ورودی‌ها
frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="قیمت نقدی:").grid(row=0, column=0, padx=5, pady=5)
entry_ghimat = tk.Entry(frame_inputs)
entry_ghimat.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_inputs, text="درصد کارمزد:").grid(row=1, column=0, padx=5, pady=5)
entry_karmazd = tk.Entry(frame_inputs)
entry_karmazd.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_inputs, text="تعداد چک:").grid(row=2, column=0, padx=5, pady=5)
entry_tedad = tk.Entry(frame_inputs)
entry_tedad.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_inputs, text="فاصله هر چک (ماه):").grid(row=3, column=0, padx=5, pady=5)
entry_mah_fasele = tk.Entry(frame_inputs)
entry_mah_fasele.grid(row=3, column=1, padx=5, pady=5)

tk.Button(frame_inputs, text="محاسبه", command=hesab_chek_gui).grid(row=4, column=0, columnspan=2, pady=10)

# نمایش جدول
text_table = tk.Text(root, width=70, height=20, state="disabled", font=("Courier", 10))
text_table.pack(pady=10)

root.mainloop()