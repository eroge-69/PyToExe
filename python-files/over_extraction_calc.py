# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# بانک نیاز آبی محصولات (m³/ha/year) - استخراج از منابع علمی و داده‌های وزارت نیرو/جهاد کشاورزی
water_requirements = {
    "گندم": 4500,
    "یونجه": 9000,
    "سیب زمینی": 7500,
    "جو": 4000,
    "ذرت": 8000,
    "چغندر قند": 10000,
    "خیار": 5500,
    "گوجه فرنگی": 6500,
    "لوبیا": 5000,
    "کدو": 4800,
    "هندوانه": 6000,
    "کلزا": 5500,
    "پنبه": 7000,
    "برنج": 12000,
    "انگور": 6000,
    "پسته": 8500,
    "سیب": 7000,
    "هلو": 7500
}

results = []
result_text = None
entry_license = None
entry_area = None
crop_var = None

def calculate():
    try:
        license_volume = float(entry_license.get())
        extra_area = float(entry_area.get())
        crop = crop_var.get()

        if crop not in water_requirements:
            messagebox.showerror("خطا", "نوع محصول معتبر نیست.")
            return

        real_consumption = water_requirements[crop] * extra_area
        over_extraction = real_consumption - license_volume

        result_text.set(
            f"مصرف واقعی: {real_consumption:,.2f} m³
"
            f"اضافه برداشت: {over_extraction:,.2f} m³"
        )

        results.append({
            "حجم مجاز (m³)": license_volume,
            "مساحت اضافه کشت (ha)": extra_area,
            "نوع محصول": crop,
            "نیاز آبی محصول (m³/ha)": water_requirements[crop],
            "مصرف واقعی (m³)": real_consumption,
            "اضافه برداشت (m³)": over_extraction
        })
    except ValueError:
        messagebox.showerror("خطا", "لطفاً مقادیر عددی معتبر وارد کنید.")

def save_excel():
    if not results:
        messagebox.showerror("خطا", "هیچ داده‌ای برای ذخیره وجود ندارد.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                             filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df = pd.DataFrame(results)
        df.to_excel(file_path, index=False)
        messagebox.showinfo("ذخیره شد", f"فایل با موفقیت ذخیره شد:
{file_path}")

def main_gui():
    global result_text, entry_license, entry_area, crop_var

    root = tk.Tk()
    root.title("محاسبه اضافه برداشت بر اساس نیاز آبی محصولات")
    root.geometry("500x420")

    result_text = tk.StringVar()

    tk.Label(root, text="حجم برداشت مجاز پروانه (m³):").pack(pady=5)
    entry_license = tk.Entry(root)
    entry_license.pack()

    tk.Label(root, text="مساحت اضافه کشت (هکتار):").pack(pady=5)
    entry_area = tk.Entry(root)
    entry_area.pack()

    tk.Label(root, text="نوع محصول:").pack(pady=5)
    crop_var = tk.StringVar()
    crop_combo = ttk.Combobox(root, textvariable=crop_var,
                              values=list(water_requirements.keys()), state="readonly")
    crop_combo.pack()

    tk.Button(root, text="محاسبه", command=calculate).pack(pady=10)
    tk.Label(root, textvariable=result_text, fg="blue").pack()

    tk.Button(root, text="ذخیره در اکسل", command=save_excel).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
