import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
import json
import os

DATA_FILE = "customers.json"

# بارگذاری مشتری‌ها از فایل
def load_customers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ذخیره مشتری‌ها در فایل
def save_customers():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=4)

# ثبت مشتری جدید
def register_customer():
    name = entry_name.get()
    phone = entry_phone.get()
    code = entry_code.get()

    if name and phone and code:
        customer = {
            "نام": name,
            "شماره": phone,
            "کد مشتری": code
        }
        customers.append(customer)
        save_customers()
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_code.delete(0, tk.END)
        messagebox.showinfo("ثبت شد", "مشتری با موفقیت ثبت شد.")
    else:
        messagebox.showwarning("هشدار", "لطفاً همه فیلدها را پر کنید.")

# نمایش لیست مشتری‌ها در پنجره جدید
def show_customers():
    list_window = Toplevel(window)
    list_window.title("لیست مشتری‌ها")
    list_window.geometry("400x400")

    text = tk.Text(list_window, wrap="word", font=("Arial", 12))
    text.pack(expand=True, fill="both")

    if customers:
        for c in customers:
            code = c.get("کد مشتری", "ندارد")
            info = f"نام: {c['نام']}\nشماره: {c['شماره']}\nکد مشتری: {code}\n{'-'*30}\n"
            text.insert(tk.END, info)
    else:
        text.insert(tk.END, "هنوز هیچ مشتری ثبت نشده است.")

# ساخت پنجره اصلی
window = tk.Tk()
window.title("ثبت مشتری‌های میوه‌فروشی")
window.geometry("500x550")

# بارگذاری تصویر پس‌زمینه با Pillow
image = Image.open("b.png")
image = image.resize((500, 550))
bg_image = ImageTk.PhotoImage(image)

canvas = tk.Canvas(window, width=500, height=550)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_image, anchor="nw")

# ویجت‌های ورودی
entry_name = tk.Entry(window)
entry_phone = tk.Entry(window)
entry_code = tk.Entry(window)

btn_register = tk.Button(
    window,
    text="ثبت مشتری",
    command=register_customer,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 11, "bold"),
    activebackground="#45a049"
)

btn_show = tk.Button(
    window,
    text="نمایش لیست مشتری‌ها",
    command=show_customers,
    bg="#2196F3",
    fg="white",
    font=("Arial", 11, "bold"),
    activebackground="#1976D2"
)

# قرار دادن ویجت‌ها روی canvas
canvas.create_window(250, 50, window=tk.Label(window, text="نام مشتری:", bg="#ffffff"))
canvas.create_window(250, 80, window=entry_name)

canvas.create_window(250, 120, window=tk.Label(window, text="شماره تماس:", bg="#ffffff"))
canvas.create_window(250, 150, window=entry_phone)

canvas.create_window(250, 190, window=tk.Label(window, text="کد مشتری:", bg="#ffffff"))
canvas.create_window(250, 220, window=entry_code)

canvas.create_window(250, 270, window=btn_register)
canvas.create_window(250, 320, window=btn_show)

# نوشته پایانی
footer_text = "هایپر میوه خندوانه\nبرنامه‌نویسی شده توسط: مهرداد مختاریان"
canvas.create_window(250, 480, window=tk.Label(window, text=footer_text, bg="#ffffff", font=("Arial", 10, "italic")))

# بارگذاری داده‌ها
customers = load_customers()

# اجرای برنامه
window.mainloop()
