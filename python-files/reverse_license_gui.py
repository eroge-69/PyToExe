Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> ```python
import tkinter as tk
from tkinter import messagebox

def reverse_mod(short_code_hex, n):
    mod_val = 2**32
    try:
        short_code_dec = int(short_code_hex, 16)
        full_number = short_code_dec + n * mod_val
        return full_number
    except ValueError:
        return None

def calculate():
    short_code = entry_code.get()
    n_value = entry_n.get()

    if not short_code:
        messagebox.showerror("خطأ", "يرجى إدخال كود العميل (hex).")
        return
    if not n_value.isdigit():
        messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح لـ n.")
        return

    n = int(n_value)
    result = reverse_mod(short_code, n)
    if result is None:
        messagebox.showerror("خطأ", "كود العميل غير صالح (غير hex).")
    else:
        label_result.config(text=f"الرقم الكامل: {result}")

إعداد النافذة
root = tk.Tk()
root.title("استعادة رقم الترخيص الكامل")
root.geometry("400x200")

الواجهة
tk.Label(root, text="كود العميل (Hex):").pack(pady=5)
entry_code = tk.Entry(root)
entry_code.pack(pady=5)

tk.Label(root, text="قيمة n:").pack(pady=5)
entry_n = tk.Entry(root)
entry_n.pack(pady=5)

btn = tk.Button(root, text="احسب الرقم الكامل", command=calculate)
btn.pack(pady=10)

label_result = tk.Label(root, text="")
label_result.pack(pady=10)

root.mainloop()


---
