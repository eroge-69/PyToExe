# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def compare_columns():
    file_path = filedialog.askopenfilename(title="انتخاب فایل اکسل", filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)
        if df.shape[1] < 2:
            messagebox.showwarning("خطا", "فایل باید حداقل دو ستون داشته باشد.")
            return

        col1 = df.iloc[:, 0]
        col2 = df.iloc[:, 1]
        common = col1[col1.isin(col2)].dropna().drop_duplicates()

        output_df = pd.DataFrame({'مقادیر مشترک': common})
        output_path = os.path.join(os.path.dirname(file_path), "نتیجه_مقایسه.xlsx")
        output_df.to_excel(output_path, index=False)

        messagebox.showinfo("موفقیت", f"✅ فایل خروجی ساخته شد:\n{output_path}")
    except Exception as e:
        messagebox.showerror("خطا", f"❌ خطا در پردازش فایل:\n{e}")

# رابط گرافیکی
root = tk.Tk()
root.title("مقایسه دو ستون اکسل")
root.geometry("300x150")

label = tk.Label(root, text="برای انتخاب فایل اکسل کلیک کنید:")
label.pack(pady=10)

btn = tk.Button(root, text="انتخاب فایل و شروع", command=compare_columns)
btn.pack(pady=10)

root.mainloop()
