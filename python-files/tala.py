import customtkinter as ctk
from tkinter import messagebox, filedialog, StringVar
import csv
import os
import configparser
import requests
from bs4 import BeautifulSoup

# ==============================
# گرفتن قیمت روز طلا از سایت ایرانی
# ==============================
def get_gold_price():
    default_price = 1500000  # قیمت پیش‌فرض اگر سایت در دسترس نبود
    try:
        url = "https://geram.ir/"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        # این قسمت باید مطابق HTML سایت واقعی تنظیم شود
        price_tag = soup.find("span", class_="gold-price")  # نمونه
        if price_tag:
            price_str = price_tag.text.strip().replace(",", "").replace(" تومان", "")
            return int(price_str)
        else:
            return default_price
    except:
        return default_price

# ==============================
# تنظیمات کاربر
# ==============================
config_file = "config.ini"
config = configparser.ConfigParser()
if os.path.exists(config_file):
    config.read(config_file)
else:
    config['SETTINGS'] = {
        'theme': 'Light',
        'tax': '9',
        'cost': '2',
        'labor': '3',
        'default_karat': '24'
    }
    with open(config_file, 'w') as f:
        config.write(f)

def save_config():
    config['SETTINGS']['theme'] = ctk.get_appearance_mode()
    config['SETTINGS']['tax'] = entry_tax.get()
    config['SETTINGS']['cost'] = entry_cost.get()
    config['SETTINGS']['labor'] = entry_labor.get()
    config['SETTINGS']['default_karat'] = karat_var.get()
    with open(config_file, 'w') as f:
        config.write(f)

# ==============================
# توابع اصلی
# ==============================
history_stack = []

def format_number(entry):
    value = entry.get().replace(",", "")
    try:
        if value:
            formatted = f"{float(value):,}"
            entry.delete(0, ctk.END)
            entry.insert(0, formatted)
    except ValueError:
        pass

def calculate_price():
    try:
        pri = float(entry_price.get().replace(",", "")) if entry_price.get() else 0
        g = float(entry_weight.get().replace(",", "")) if entry_weight.get() else 0
        tax_percent = float(entry_tax.get().replace(",", "")) if entry_tax.get() else 0
        cost_percent = float(entry_cost.get().replace(",", "")) if entry_cost.get() else 0
        labor_percent = float(entry_labor.get().replace(",", "")) if entry_labor.get() else 0
        karat = int(karat_var.get())

        price_per_gram = pri * karat / 24
        price = price_per_gram * g
        o = price * (tax_percent / 100)
        k = (price + o) * (cost_percent / 100)
        m = (price + o + k) * (labor_percent / 100)
        total_price = price + o + k + m

        history_stack.append((entry_price.get(), entry_weight.get(), entry_tax.get(),
                              entry_cost.get(), entry_labor.get(), karat_var.get()))

        label_result.configure(
            text=f"💰 قیمت نهایی: {total_price:,.0f} تومان\n"
                 f"مالیات: {o:,.0f} | کارمزد: {k:,.0f} | اجرت: {m:,.0f} | سود تقریبی: {k+m:,.0f}"
        )
        return total_price
    except ValueError:
        messagebox.showerror("خطا", "لطفا اعداد معتبر وارد کنید")
        return None

def undo_last():
    if history_stack:
        last = history_stack.pop()
        entry_price.delete(0, ctk.END)
        entry_price.insert(0, last[0])
        entry_weight.delete(0, ctk.END)
        entry_weight.insert(0, last[1])
        entry_tax.delete(0, ctk.END)
        entry_tax.insert(0, last[2])
        entry_cost.delete(0, ctk.END)
        entry_cost.insert(0, last[3])
        entry_labor.delete(0, ctk.END)
        entry_labor.insert(0, last[4])
        karat_var.set(last[5])
        calculate_price()

def clear_entries():
    for e in [entry_price, entry_weight, entry_tax, entry_cost, entry_labor]:
        e.delete(0, ctk.END)
    label_result.configure(text="💰 قیمت نهایی: ")
    history_stack.clear()
def save_to_csv():
    total = calculate_price()
    if total is None:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if file_path:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["قیمت هر گرم","وزن","درصد مالیات","درصد کارمزد","درصد اجرت","عیار","قیمت نهایی"])
            writer.writerow([entry_price.get(), entry_weight.get(), entry_tax.get(), entry_cost.get(),
                             entry_labor.get(), karat_var.get(), f"{total:,.0f}"])
        messagebox.showinfo("ذخیره شد", f"محاسبه در {file_path} ذخیره شد")

def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
    if not file_path:
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    top = ctk.CTkToplevel(root)
    top.title("نمایش CSV")
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            label = ctk.CTkLabel(top, text=value, width=15, anchor="w")
            label.grid(row=i, column=j, padx=5, pady=2)

# ==============================
# رابط کاربری
# ==============================
ctk.set_appearance_mode(config['SETTINGS']['theme'])
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Gold Calculator")
root.geometry("650x650")

# عنوان
title_label = ctk.CTkLabel(root, text="💎 Gold Calculator", font=("B Nazanin", 24, "bold"))
title_label.pack(pady=10)

frame = ctk.CTkFrame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# ورودی‌ها
labels_entries = [
    ("قیمت هر گرم طلا (تومان):", "price"),
    ("وزن طلا (گرم):", "weight"),
    ("درصد مالیات:", "tax"),
    ("درصد کارمزد:", "cost"),
    ("درصد اجرت ساخت:", "labor")
]

entries = {}
default_price = get_gold_price()

for label_text, key in labels_entries:
    row = ctk.CTkFrame(frame)
    row.pack(fill="x", pady=5)
    lbl = ctk.CTkLabel(row, text=label_text, font=("B Nazanin", 14))
    lbl.pack(side="left", padx=5)
    placeholder = f"قیمت پیش‌فرض: {default_price:,}" if key=="price" else ""
    entry = ctk.CTkEntry(row, width=200, font=("Tahoma", 14), placeholder_text=placeholder)
    entry.pack(side="right", padx=5)
    if key=="price":
        entry.insert(0, str(default_price))
    entry.bind("<FocusOut>", lambda e, en=entry: format_number(en))
    entry.bind("<KeyRelease>", lambda e: calculate_price())
    entries[key] = entry

entry_price = entries["price"]
entry_weight = entries["weight"]
entry_tax = entries["tax"]
entry_cost = entries["cost"]
entry_labor = entries["labor"]

# انتخاب عیار طلا
karat_var = StringVar(value=config['SETTINGS']['default_karat'])
karat_frame = ctk.CTkFrame(frame)
karat_frame.pack(fill="x", pady=5)
karat_label = ctk.CTkLabel(karat_frame, text="عیار طلا:", font=("B Nazanin", 14))
karat_label.pack(side="left", padx=5)
karat_entry = ctk.CTkOptionMenu(
    karat_frame,
    values=["24","18","14"],
    variable=karat_var,
    command=lambda _: calculate_price()
)
karat_entry.pack(side="right", padx=5)

# نتیجه و جزئیات
label_result = ctk.CTkLabel(root, text="💰 قیمت نهایی: ", font=("B Nazanin", 16, "bold"), text_color="green")
label_result.pack(pady=10)

# دکمه‌ها
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=10)

btn_clear = ctk.CTkButton(btn_frame, text="🧹 پاک کردن", fg_color="red", command=clear_entries)
btn_clear.pack(side="left", padx=5)

btn_undo = ctk.CTkButton(btn_frame, text="↩️ Undo", command=undo_last)
btn_undo.pack(side="left", padx=5)

btn_save_csv = ctk.CTkButton(btn_frame, text="💾 ذخیره CSV", command=save_to_csv)
btn_save_csv.pack(side="right", padx=5)

btn_load_csv = ctk.CTkButton(btn_frame, text="📂 بازخوانی CSV", command=load_csv)
btn_load_csv.pack(side="right", padx=5)

# انتخاب تم
def change_theme(choice):
    ctk.set_appearance_mode(choice)
    save_config()
theme_menu = ctk.CTkOptionMenu(root, values=["Light","Dark","System"], command=change_theme)
theme_menu.set(config['SETTINGS']['theme'])
theme_menu.pack(pady=10)

# کلیدهای میانبر
def shortcuts(event):
    if event.keysym == "Return":
        calculate_price()
    elif event.keysym == "Escape":
        clear_entries()
    elif event.keysym.lower() == "z" and event.state & 0x0004:  # Ctrl+Z
        undo_last()

root.bind("<Key>", shortcuts)

root.mainloop()
save_config()
