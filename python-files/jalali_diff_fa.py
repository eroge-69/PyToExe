
import jdatetime
import tkinter as tk
from tkinter import messagebox

def calculate_difference():
    try:
        start = start_entry.get()
        end = end_entry.get()

        y1, m1, d1 = map(int, start.split('/'))
        y2, m2, d2 = map(int, end.split('/'))

        date1 = jdatetime.date(y1, m1, d1).togregorian()
        date2 = jdatetime.date(y2, m2, d2).togregorian()

        diff = (date2 - date1).days

        result_label.config(text=f"تفاوت بین دو تاریخ: {diff} روز")
    except Exception as e:
        messagebox.showerror("خطا", "ورودی‌ها را به‌صورت درست وارد کنید (مثلاً 1403/01/15).")

root = tk.Tk()
root.title("محاسبه اختلاف دو تاریخ شمسی")
root.geometry("400x250")
root.resizable(False, False)

title_label = tk.Label(root, text="محاسبه اختلاف دو تاریخ شمسی", font=("B Nazanin", 14, "bold"))
title_label.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="تاریخ شروع (مثلاً 1403/01/15):").grid(row=0, column=0, sticky="e")
start_entry = tk.Entry(frame, width=15, justify="center")
start_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="تاریخ پایان (مثلاً 1403/02/20):").grid(row=1, column=0, sticky="e")
end_entry = tk.Entry(frame, width=15, justify="center")
end_entry.grid(row=1, column=1, padx=5, pady=5)

calc_button = tk.Button(root, text="محاسبه اختلاف", font=("B Nazanin", 12), command=calculate_difference)
calc_button.pack(pady=10)

result_label = tk.Label(root, text="", font=("B Nazanin", 12))
result_label.pack(pady=10)

tk.Label(root, text="ساخته شده توسط GPT", font=("Arial", 8)).pack(side="bottom", pady=5)

root.mainloop()
