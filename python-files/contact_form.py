import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pandas as pd
import os

FILE_NAME = "فرمحاسب_data.xlsx"

def init_file():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "تاریخ ثبت", "نام", "نام خانوادگی", "نام شرکت", "شماره تماس",
            "پلتفرم ارسال", "توضیحات تماس اولیه", "تاریخ پیگیری بعدی",
            "توضیحات پیگیری", "وضعیت"
        ])
        df.to_excel(FILE_NAME, index=False)

def save_contact():
    try:
        df = pd.read_excel(FILE_NAME)
        new_data = {
            "تاریخ ثبت": datetime.today().strftime("%Y-%m-%d"),
            "نام": name_var.get(),
            "نام خانوادگی": lname_var.get(),
            "نام شرکت": company_var.get(),
            "شماره تماس": phone_var.get(),
            "پلتفرم ارسال": platform_var.get(),
            "توضیحات تماس اولیه": first_note_text.get("1.0", tk.END).strip(),
            "تاریخ پیگیری بعدی": follow_date_var.get(),
            "توضیحات پیگیری": follow_note_text.get("1.0", tk.END).strip(),
            "وضعیت": status_var.get()
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)
        messagebox.showinfo("موفقیت", "اطلاعات با موفقیت ذخیره شد.")
        name_var.set("")
        lname_var.set("")
        company_var.set("")
        phone_var.set("")
        platform_var.set("")
        first_note_text.delete("1.0", tk.END)
        follow_date_var.set("")
        follow_note_text.delete("1.0", tk.END)
        status_var.set("")
    except Exception as e:
        messagebox.showerror("خطا", f"در ذخیره اطلاعات مشکلی پیش آمد:\n{e}")

init_file()

# طراحی رابط گرافیکی
root = tk.Tk()
root.title("فرم ثبت اطلاعات مشتری")

name_var = tk.StringVar()
lname_var = tk.StringVar()
company_var = tk.StringVar()
phone_var = tk.StringVar()
platform_var = tk.StringVar()
follow_date_var = tk.StringVar()
status_var = tk.StringVar()

tk.Label(root, text="نام").grid(row=0, column=0)
tk.Entry(root, textvariable=name_var).grid(row=0, column=1)

tk.Label(root, text="نام خانوادگی").grid(row=1, column=0)
tk.Entry(root, textvariable=lname_var).grid(row=1, column=1)

tk.Label(root, text="نام شرکت").grid(row=2, column=0)
tk.Entry(root, textvariable=company_var).grid(row=2, column=1)

tk.Label(root, text="شماره تماس").grid(row=3, column=0)
tk.Entry(root, textvariable=phone_var).grid(row=3, column=1)

tk.Label(root, text="پلتفرم ارسال").grid(row=4, column=0)
tk.Entry(root, textvariable=platform_var).grid(row=4, column=1)

tk.Label(root, text="توضیحات تماس اولیه").grid(row=5, column=0)
first_note_text = tk.Text(root, height=3, width=40)
first_note_text.grid(row=5, column=1)

tk.Label(root, text="تاریخ پیگیری بعدی").grid(row=6, column=0)
tk.Entry(root, textvariable=follow_date_var).grid(row=6, column=1)

tk.Label(root, text="توضیحات پیگیری").grid(row=7, column=0)
follow_note_text = tk.Text(root, height=3, width=40)
follow_note_text.grid(row=7, column=1)

tk.Label(root, text="وضعیت").grid(row=8, column=0)
tk.Entry(root, textvariable=status_var).grid(row=8, column=1)

tk.Button(root, text="ذخیره اطلاعات", command=save_contact).grid(row=9, column=0, columnspan=2)

root.mainloop()
