import tkinter as tk
from tkinter import messagebox, font

def calculate():
    try:
        user = var.get()
        num1 = float(entry_width.get())
        num2 = float(entry_height.get())
        
        if user == 1:  # چرم - فوت مربع
            masahat = num1 * num2
            foot = 30.48 * 30.48
            masahat_foot = masahat / foot
            result_var.set(f"مساحت چرم به فوت مربع: {masahat_foot:.4f}")
            
        elif user == 2:  # آستر - متر مربع
            masahat_m = (num1 / 100) * (num2 / 100)
            result_var.set(f"مساحت آستر به متر مربع: {masahat_m:.4f}")
        else:
            messagebox.showerror("خطا", "لطفاً چرم یا آستر را انتخاب کنید.")
    except ValueError:
        messagebox.showerror("خطا", "لطفاً اعداد معتبر وارد کنید.")

# پنجره اصلی
root = tk.Tk()
root.title("محاسبه مساحت چرم و آستر")
root.geometry("400x320")
root.configure(bg="#f0f4f8")

# فونت‌ها
title_font = font.Font(family="B Nazanin", size=16, weight="bold")
label_font = font.Font(family="B Nazanin", size=12)
result_font = font.Font(family="B Nazanin", size=14, weight="bold")

# عنوان
label_title = tk.Label(root, text="محاسبه مساحت چرم و آستر", bg="#f0f4f8", fg="#2c3e50", font=title_font)
label_title.pack(pady=15)

# فریم برای نوع محصول
frame_type = tk.Frame(root, bg="#f0f4f8")
frame_type.pack(pady=10)

var = tk.IntVar(value=1)

radio_charm = tk.Radiobutton(frame_type, text="چرم", variable=var, value=1, bg="#f0f4f8", font=label_font)
radio_astar = tk.Radiobutton(frame_type, text="آستر", variable=var, value=2, bg="#f0f4f8", font=label_font)
radio_charm.grid(row=0, column=0, padx=20)
radio_astar.grid(row=0, column=1, padx=20)

# فریم برای ورودی‌ها
frame_inputs = tk.Frame(root, bg="#f0f4f8")
frame_inputs.pack(pady=10)

label_width = tk.Label(frame_inputs, text="عرض (سانتی‌متر):", bg="#f0f4f8", font=label_font)
label_width.grid(row=0, column=0, sticky="e", padx=10, pady=5)
entry_width = tk.Entry(frame_inputs, font=label_font, width=15)
entry_width.grid(row=0, column=1, padx=10, pady=5)

label_height = tk.Label(frame_inputs, text="طول (سانتی‌متر):", bg="#f0f4f8", font=label_font)
label_height.grid(row=1, column=0, sticky="e", padx=10, pady=5)
entry_height = tk.Entry(frame_inputs, font=label_font, width=15)
entry_height.grid(row=1, column=1, padx=10, pady=5)

# دکمه محاسبه
btn_calculate = tk.Button(root, text="محاسبه", command=calculate, bg="#2980b9", fg="white", font=label_font, width=20, relief="raised", bd=3)
btn_calculate.pack(pady=15)

# نمایش نتیجه
result_var = tk.StringVar()
label_result = tk.Label(root, textvariable=result_var, bg="#f0f4f8", fg="#27ae60", font=result_font)
label_result.pack(pady=10)

root.mainloop()
