import tkinter as tk
from tkinter import messagebox

def hex_to_dec(hex_str):
    try:
        return int(hex_str, 16)
    except ValueError:
        messagebox.showerror("خطأ", "قيمة HEX غير صحيحة")
        return None

def calculate_factor():
    hex_val = entry_hex.get().replace(" ", "")
    real_val = entry_real.get()

    if not hex_val or not real_val:
        messagebox.showerror("خطأ", "املأ الحقول المطلوبة")
        return

    dec_val = hex_to_dec(hex_val)
    if dec_val is None:
        return

    try:
        real_val = float(real_val)
        factor = real_val / dec_val
        messagebox.showinfo("النتيجة", f"القيمة HEX = {dec_val}\nالمعامل = {factor:.2f}")
    except ZeroDivisionError:
        messagebox.showerror("خطأ", "لا يمكن القسمة على صفر")
    except ValueError:
        messagebox.showerror("خطأ", "القيمة الحقيقية غير صحيحة")

def calculate_real():
    hex_val = entry_hex.get().replace(" ", "")
    factor = entry_factor.get()

    if not hex_val or not factor:
        messagebox.showerror("خطأ", "املأ الحقول المطلوبة")
        return

    dec_val = hex_to_dec(hex_val)
    if dec_val is None:
        return

    try:
        factor = float(factor)
        real_val = dec_val * factor
        messagebox.showinfo("النتيجة", f"القيمة HEX = {dec_val}\nالقيمة المحسوبة = {real_val:.0f}")
    except ValueError:
        messagebox.showerror("خطأ", "المعامل غير صحيح")

root = tk.Tk()
root.title("Hex RPM Converter")

tk.Label(root, text="قيمة HEX (مثال: 001D)").grid(row=0, column=0)
entry_hex = tk.Entry(root)
entry_hex.grid(row=0, column=1)

tk.Label(root, text="القيمة الحقيقية (مثال: 5800)").grid(row=1, column=0)
entry_real = tk.Entry(root)
entry_real.grid(row=1, column=1)

btn_factor = tk.Button(root, text="احسب المعامل", command=calculate_factor)
btn_factor.grid(row=2, column=0, columnspan=2, pady=5)

tk.Label(root, text="المعامل (مثال: 200)").grid(row=3, column=0)
entry_factor = tk.Entry(root)
entry_factor.grid(row=3, column=1)

btn_real = tk.Button(root, text="احسب القيمة النهائية", command=calculate_real)
btn_real.grid(row=4, column=0, columnspan=2, pady=5)

root.mainloop()