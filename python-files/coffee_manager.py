import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from collections import defaultdict
import jdatetime
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf.enums import XPos, YPos

# تابع شکل‌دهی متن فارسی برای نمایش درست در PDF
def reshape_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# گرفتن شماره فاکتور بعدی از فایل
def get_next_invoice_number():
    invoice_file = "invoice_number.txt"
    if not os.path.exists(invoice_file):
        with open(invoice_file, "w") as f:
            f.write("1")
        return 1
    with open(invoice_file, "r") as f:
        number = f.read()
    try:
        number = int(number)
    except:
        number = 1
    next_number = number + 1
    with open(invoice_file, "w") as f:
        f.write(str(next_number))
    return number

# ایجاد و ذخیره فاکتور PDF با جدول
def save_invoice_pdf(date_str, time_str, customer_name, selected_items, total_price, payment_method):
    invoice_number = get_next_invoice_number()

    if not os.path.exists("factors"):
        os.makedirs("factors")

    pdf = FPDF()
    pdf.add_page()

    pdf.add_font("Vazir", "", "Vazir.ttf")
    pdf.set_font("Vazir", size=16)

    pdf.cell(0, 15, reshape_text(f"شماره فاکتور : {invoice_number}"), new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.ln(20)

    pdf.set_font("Vazir", size=14)
    pdf.cell(0, 10, reshape_text(f"تاریخ: {date_str} ساعت: {time_str}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
    pdf.cell(0, 10, reshape_text(f"نام مشتری: {customer_name}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
    pdf.cell(0, 10, reshape_text(f"روش پرداخت: {payment_method}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
    pdf.ln(10)

    # جدول آیتم‌ها
    pdf.set_font("Vazir", size=12)
    col_widths = [90, 30, 30, 40]
    headers = ["نام کالا", "تعداد", "قیمت واحد", "جمع"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 10, reshape_text(h), border=1, align='C')
    pdf.ln()

    for item, qty in selected_items.items():
        price_unit = ITEMS[item]
        total_item = price_unit * qty
        pdf.cell(col_widths[0], 10, reshape_text(item), border=1, align='R')
        pdf.cell(col_widths[1], 10, str(qty), border=1, align='C')
        pdf.cell(col_widths[2], 10, f"{price_unit:,}", border=1, align='R')
        pdf.cell(col_widths[3], 10, f"{total_item:,}", border=1, align='R')
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Vazir", size=14)
    pdf.cell(0, 12, reshape_text(f"مبلغ کل: {total_price:,} تومان"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

    filename = f"factors/{invoice_number}.pdf"
    pdf.output(filename)


# تنظیمات پنجره اصلی
root = tk.Tk()
root.title("حسابداری کافه")
root.geometry("750x800")
root.state("zoomed")

CSV_FILE = "sales_log.csv"

ITEMS = {
    "اسپرسو": 50000,
    "آمریکانو": 60000,
    "آیس آمریکانو": 65000,
    "چای": 15000,
    "چای خاص": 55000,
    "دمنوش زعفران": 80000
}

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        headers = ["Invoice Number", "Date", "Time", "Customer", "Items", "Total (Toman)", "Payment Method"]
        writer.writerow(headers)

def save_order(customer_name, selected_items, total_price, payment_method):
    now = jdatetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    items_str = ", ".join([f"{item} x{qty}" for item, qty in selected_items.items()])

    invoice_number = get_next_invoice_number()

    row = [invoice_number, date_str, time_str, customer_name, items_str, total_price, payment_method]

    with open(CSV_FILE, "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

    # ذخیره فاکتور PDF
    save_invoice_pdf(date_str, time_str, customer_name, selected_items, total_price, payment_method)

def calculate_income(start_date=None, end_date=None):
    daily_income = defaultdict(int)
    total_income = 0
    cash_total = 0
    card_total = 0
    orders = []
    try:
        with open(CSV_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row["Date"]
                if (start_date and date < start_date) or (end_date and date > end_date):
                    continue
                amount = int(row["Total (Toman)"])
                payment = row["Payment Method"]
                daily_income[date] += amount
                total_income += amount
                if payment == "نقدی":
                    cash_total += amount
                elif payment == "کارت":
                    card_total += amount
                orders.append(row)
    except FileNotFoundError:
        return {}, 0, 0, 0, []
    return daily_income, total_income, cash_total, card_total, orders

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# --- سفارش ---
order_frame = tk.Frame(notebook)
notebook.add(order_frame, text="ثبت سفارش")

customer_label = tk.Label(order_frame, text="نام مشتری:", anchor="e")
customer_label.pack(pady=5, fill="x")

customer_entry = tk.Entry(order_frame, justify="right")
customer_entry.insert(0, "مشتری")
customer_entry.pack(pady=5, fill="x")

tk.Label(order_frame, text="منو", anchor="e").pack(pady=10, fill="x")

# بخش پایین صفحه برای انتخاب تعداد و تایید
bottom_frame = tk.Frame(order_frame, relief="raised", bd=2)
bottom_frame.pack(side="bottom", fill="x")
bottom_frame.pack_forget()  # ابتدا مخفی است

selected_item = None
selected_qty = tk.IntVar(value=1)
price_label = None
qty_label = None

def open_bottom_menu(item):
    global selected_item, selected_qty, price_label, qty_label
    selected_item = item
    selected_qty.set(1)
    bottom_frame.pack(side="bottom", fill="x")

    for widget in bottom_frame.winfo_children():
        widget.destroy()

    tk.Label(bottom_frame, text=f"قیمت {item}: {ITEMS[item]:,} تومان", anchor="e").pack(side="right", padx=10)

    def increase_qty():
        selected_qty.set(selected_qty.get() + 1)
        qty_label.config(text=str(selected_qty.get()))

    def decrease_qty():
        if selected_qty.get() > 1:
            selected_qty.set(selected_qty.get() - 1)
            qty_label.config(text=str(selected_qty.get()))

    tk.Button(bottom_frame, text="-", width=3, command=decrease_qty).pack(side="left", padx=5, pady=5)
    qty_label = tk.Label(bottom_frame, text=str(selected_qty.get()), width=4, anchor="center")
    qty_label.pack(side="left")
    tk.Button(bottom_frame, text="+", width=3, command=increase_qty).pack(side="left", padx=5, pady=5)

    def confirm():
        qty = selected_qty.get()
        if qty <= 0:
            messagebox.showwarning("خطا", "تعداد باید حداقل ۱ باشد.")
            return
        if item in order_items:
            order_items[item] += qty
        else:
            order_items[item] = qty
        update_order_display()
        update_total()
        bottom_frame.pack_forget()

    tk.Button(bottom_frame, text="تایید", bg="green", fg="white", command=confirm).pack(side="left", padx=20)

order_items = {}

order_buttons_frame = tk.Frame(order_frame)
order_buttons_frame.pack(pady=5, fill="x")

def update_order_display():
    for widget in order_buttons_frame.winfo_children():
        widget.destroy()
    if not order_items:
        tk.Label(order_buttons_frame, text="هیچ آیتمی انتخاب نشده", fg="gray").pack()
        return
    for item, qty in order_items.items():
        tk.Label(order_buttons_frame, text=f"{item} x{qty}").pack(side="right", padx=10)

def update_total():
    total = 0
    for item, qty in order_items.items():
        total += ITEMS[item] * qty
    total_label.config(text=f"مبلغ کل: {total:,} تومان")

for item, price in ITEMS.items():
    b = tk.Button(order_frame, text=f"{item} - {price:,} تومان", anchor="e",
                  command=lambda i=item: open_bottom_menu(i))
    b.pack(fill="x", padx=10, pady=3)

payment_var = tk.StringVar(value="کارت")
tk.Label(order_frame, text="روش پرداخت:", anchor="e").pack(pady=10, fill="x")
tk.Radiobutton(order_frame, text="نقدی", variable=payment_var, value="نقدی").pack(anchor="e")
tk.Radiobutton(order_frame, text="کارت", variable=payment_var, value="کارت").pack(anchor="e")

total_label = tk.Label(order_frame, text="مبلغ کل: 0 تومان", anchor="e")
total_label.pack(pady=10, fill="x")

def submit_order():
    customer = customer_entry.get().strip()
    if not customer:
        messagebox.showwarning("خطا", "نام مشتری وارد نشده.")
        return
    if not order_items:
        messagebox.showwarning("خطا", "هیچ آیتمی انتخاب نشده.")
        return
    total = sum(ITEMS[item] * qty for item, qty in order_items.items())
    save_order(customer, order_items.copy(), total, payment_var.get())
    messagebox.showinfo("ثبت شد", "سفارش ثبت شد.")
    order_items.clear()
    update_order_display()
    update_total()

def cancel_order():
    if not order_items:
        messagebox.showinfo("لغو سفارش", "هیچ سفارشی برای لغو وجود ندارد.")
        return
    if messagebox.askyesno("لغو سفارش", "آیا مطمئن هستید که می‌خواهید سفارش را لغو کنید؟"):
        order_items.clear()
        update_order_display()
        update_total()
        bottom_frame.pack_forget()

button_frame = tk.Frame(order_frame)
button_frame.pack(pady=20)

tk.Button(button_frame, text="ثبت سفارش", command=submit_order, bg="green", fg="white").pack(side="left", padx=10)
tk.Button(button_frame, text="لغو سفارش", command=cancel_order, bg="red", fg="white").pack(side="left", padx=10)

# --- گزارش ---
report_frame = tk.Frame(notebook)
notebook.add(report_frame, text="گزارش درآمد")

tk.Label(report_frame, text="از تاریخ (YYYY-MM-DD):").pack(pady=3)
start_date_entry = tk.Entry(report_frame, justify="right")
start_date_entry.pack()

tk.Label(report_frame, text="تا تاریخ (YYYY-MM-DD):").pack(pady=3)
end_date_entry = tk.Entry(report_frame, justify="right")
end_date_entry.pack()

today = jdatetime.date.today().strftime("%Y-%m-%d")
start_date_entry.insert(0, today)
end_date_entry.insert(0, today)

summary_frame = tk.Frame(report_frame)
summary_frame.pack(pady=5, fill="x")

card_label = tk.Label(summary_frame, text="مجموع کارت: 0 تومان", fg="green", anchor="e")
card_label.pack(side="right", padx=10)

cash_label = tk.Label(summary_frame, text="مجموع نقدی: 0 تومان", fg="blue", anchor="e")
cash_label.pack(side="right", padx=10)

total_label_report = tk.Label(summary_frame, text="مجموع کل: 0 تومان", fg="black", anchor="e")
total_label_report.pack(side="right", padx=10)

columns = ("شماره فاکتور", "تاریخ", "ساعت", "سفارش دهنده", "سفارش", "مجموع", "نوع پرداخت")
tree = ttk.Treeview(report_frame, columns=columns, show="headings", height=15)
tree.pack(expand=True, fill="both", padx=10, pady=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

def show_report():
    start = start_date_entry.get().strip()
    end = end_date_entry.get().strip()

    for i in tree.get_children():
        tree.delete(i)

    income, total, cash, card, orders = calculate_income(start, end)

    card_label.config(text=f"مجموع کارت: {card:,} تومان")
    cash_label.config(text=f"مجموع نقدی: {cash:,} تومان")
    total_label_report.config(text=f"مجموع کل: {total:,} تومان")

    if not orders:
        messagebox.showinfo("گزارش", "سفارشی یافت نشد.")
        return

    for o in orders:
        tree.insert("", "end", values=(
            o["Invoice Number"],
            o["Date"],
            o["Time"],
            o["Customer"],
            o["Items"],
            f"{int(o['Total (Toman)']):,} تومان",
            o["Payment Method"]
        ))

tk.Button(report_frame, text="مشاهده گزارش", command=show_report, bg="blue", fg="white").pack(pady=10)

root.mainloop()
