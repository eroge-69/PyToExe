#!/usr/bin/env python3
# jalali_diff_gui.py
# GUI program (Tkinter) to compute exact difference in days between two Jalali (Persian) dates.
# Input format: yyyy/mm/dd  (e.g., 1403/07/01)
# Requires Python 3.7+. To build EXE on Windows, use PyInstaller: pyinstaller --onefile --windowed jalali_diff_gui.py

import tkinter as tk
from tkinter import messagebox

def jalali_to_jdn(jy, jm, jd):
    # Algorithm from "Practical Astronomy with your Calculator" adapted for Jalali (Khiyam-Jalali)
    # More robust canonical implementation for converting Persian date to JDN
    jy = int(jy)
    jm = int(jm)
    jd = int(jd)
    epbase = jy - (474 if jy >= 0 else 473)
    epyear = 474 + (epbase % 2820)
    if jm <= 7:
        mdays = (jm - 1) * 31
    else:
        mdays = (jm - 1) * 30 + 6
    jdn = jd + mdays + int(((epyear * 682) - 110) / 2816) + (epyear - 1) * 365 + int(epbase / 2820) * 1029983 + (1948320 - 1)
    return jdn

def parse_jalali_str(s):
    # Accepts yyyy/mm/dd or yyyy-mm-dd with optional spaces
    s = s.strip()
    for sep in ('/', '-', '\\\\'):
        if sep in s:
            parts = s.split(sep)
            if len(parts) == 3:
                y, m, d = parts
                return int(y), int(m), int(d)
    raise ValueError("فرمت تاریخ باید yyyy/mm/dd باشد. مثال: 1403/07/01")

def compute_diff():
    a = entry_a.get().strip()
    b = entry_b.get().strip()
    try:
        y1, m1, d1 = parse_jalali_str(a)
        y2, m2, d2 = parse_jalali_str(b)
    except Exception as e:
        messagebox.showerror("خطا", f"فرمت تاریخ نامعتبر است:\n{e}")
        return
    try:
        j1 = jalali_to_jdn(y1, m1, d1)
        j2 = jalali_to_jdn(y2, m2, d2)
        diff = j2 - j1
        label_result.config(text=f"اختلاف: {diff} روز")
    except Exception as e:
        messagebox.showerror("خطا", f"محاسبه انجام نشد:\n{e}")

def swap_dates():
    a = entry_a.get()
    entry_a.delete(0, tk.END)
    entry_a.insert(0, entry_b.get())
    entry_b.delete(0, tk.END)
    entry_b.insert(0, a)

root = tk.Tk()
root.title("محاسبه اختلاف دو تاریخ شمسی — Jalali Diff")
root.geometry("420x200")
root.resizable(False, False)

frame = tk.Frame(root, padx=12, pady=12)
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="تاریخ ۱ (yyyy/mm/dd):").grid(row=0, column=0, sticky="w")
entry_a = tk.Entry(frame, width=20, justify="center")
entry_a.grid(row=0, column=1, padx=8, pady=6)
entry_a.insert(0, "1402/05/15")

tk.Label(frame, text="تاریخ ۲ (yyyy/mm/dd):").grid(row=1, column=0, sticky="w")
entry_b = tk.Entry(frame, width=20, justify="center")
entry_b.grid(row=1, column=1, padx=8, pady=6)
entry_b.insert(0, "1402/05/20")

btn_frame = tk.Frame(frame)
btn_frame.grid(row=2, column=0, columnspan=2, pady=8)

btn_calc = tk.Button(btn_frame, text="محاسبه", width=12, command=compute_diff)
btn_calc.pack(side=tk.LEFT, padx=6)

btn_swap = tk.Button(btn_frame, text="جابجایی", width=12, command=swap_dates)
btn_swap.pack(side=tk.LEFT, padx=6)

label_result = tk.Label(frame, text="اختلاف: —", font=("Helvetica", 12, "bold"))
label_result.grid(row=3, column=0, columnspan=2, pady=10)

note = tk.Label(frame, text="فرمت ورودی: yyyy/mm/dd  —  مثال: 1402/05/15", fg="gray")
note.grid(row=4, column=0, columnspan=2, sticky="w")

# Center the window on screen
root.update_idletasks()
w = root.winfo_width()
h = root.winfo_height()
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws // 2) - (w // 2)
y = (hs // 2) - (h // 2)
root.geometry(f'{w}x{h}+{x}+{y}')

root.mainloop()
