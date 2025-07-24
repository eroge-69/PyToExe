import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

root = tk.Tk()
root.title("فرم ثبت اطلاعات - آبفا یار")
root.geometry("700x700")
root.configure(bg="#f2f2f2")
font_style = ("Tahoma", 12)

payment_places = ["جاری", "آب استان", "فاضلاب استان", "آب اهواز", "فاضلاب اهواز"]
financial_years = ["1402", "1403", "1404"]

def create_labeled_entry(parent, label_text, row):
    tk.Label(parent, text=label_text, font=font_style, bg="#f2f2f2").grid(row=row, column=0, sticky="w", padx=10, pady=5)
    entry = tk.Entry(parent, font=font_style, width=40)
    entry.grid(row=row, column=1, padx=10, pady=5)
    return entry

def create_labeled_date(parent, label_text, row):
    tk.Label(parent, text=label_text, font=font_style, bg="#f2f2f2").grid(row=row, column=0, sticky="w", padx=10, pady=5)
    date = DateEntry(parent, font=font_style, width=20, date_pattern='yyyy/mm/dd')
    date.grid(row=row, column=1, padx=10, pady=5)
    return date

def create_labeled_combobox(parent, label_text, values, row):
    tk.Label(parent, text=label_text, font=font_style, bg="#f2f2f2").grid(row=row, column=0, sticky="w", padx=10, pady=5)
    combo = ttk.Combobox(parent, values=values, font=font_style, width=37)
    combo.grid(row=row, column=1, padx=10, pady=5)
    combo.set(values[0])
    return combo

title_entry = create_labeled_entry(root, "عنوان", 0)
newspaper_entry = create_labeled_entry(root, "نام روزنامه", 1)
payment_combo = create_labeled_combobox(root, "محل پرداخت", payment_places, 2)
withdraw_combo = create_labeled_combobox(root, "محل برداشت مبلغ", payment_places, 3)
print_date1 = create_labeled_date(root, "تاریخ چاپ اول", 4)
print_date2 = create_labeled_date(root, "تاریخ چاپ دوم", 5)
price_entry = create_labeled_entry(root, "قیمت (ریال)", 6)
ershad_date = create_labeled_date(root, "تاریخ نامه به ارشاد", 7)
ershad_number = create_labeled_entry(root, "شماره نامه به ارشاد", 8)
auto_date = create_labeled_date(root, "تاریخ نامه اتوماسیون", 9)
auto_number = create_labeled_entry(root, "شماره نامه اتوماسیون", 10)
tracking_entry = create_labeled_entry(root, "پیگیری", 11)
tk.Label(root, text="توضیحات", font=font_style, bg="#f2f2f2").grid(row=12, column=0, sticky="nw", padx=10, pady=5)
desc_text = tk.Text(root, font=font_style, width=50, height=5)
desc_text.grid(row=12, column=1, padx=10, pady=5)
year_combo = create_labeled_combobox(root, "سال مالی", financial_years, 13)

tk.Button(root, text="ذخیره اطلاعات", font=font_style, bg="#4CAF50", fg="white", width=20).grid(row=14, column=1, pady=20)

root.mainloop()