
import tkinter as tk
from tkinter import messagebox, simpledialog

products = {}

def add_purchase():
    name = simpledialog.askstring("مشتريات", "اسم المنتج:")
    if not name:
        return
    try:
        buy_price = float(simpledialog.askstring("مشتريات", "سعر الشراء للمنتج:"))
        quantity = int(simpledialog.askstring("مشتريات", "الكمية المشتراة:"))
    except (TypeError, ValueError):
        messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة.")
        return
    if name not in products:
        products[name] = {'buy_price': buy_price, 'sell_price': 0, 'purchased': 0, 'sold': 0}
    products[name]['buy_price'] = buy_price
    products[name]['purchased'] += quantity
    messagebox.showinfo("تم", f"تم تسجيل شراء {quantity} من {name}.")

def set_sell_price():
    name = simpledialog.askstring("سعر البيع", "اسم المنتج:")
    if not name or name not in products:
        messagebox.showerror("خطأ", "المنتج غير موجود أو لم تتم إضافته كمشتريات.")
        return
    try:
        sell_price = float(simpledialog.askstring("سعر البيع", "سعر البيع للمنتج:"))
    except (TypeError, ValueError):
        messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح.")
        return
    products[name]['sell_price'] = sell_price
    messagebox.showinfo("تم", f"تم تحديد سعر بيع {name} بـ{sell_price} جنيه.")

def sell_product():
    name = simpledialog.askstring("مبيعات", "اسم المنتج المباع:")
    if not name or name not in products or products[name]['sell_price'] <= 0:
        messagebox.showerror("خطأ", "المنتج غير موجود أو لم يتم تحديد سعر البيع.")
        return
    try:
        quantity = int(simpledialog.askstring("مبيعات", "الكمية المباعة:"))
    except (TypeError, ValueError):
        messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح.")
        return
    if products[name]['purchased'] - products[name]['sold'] >= quantity:
        products[name]['sold'] += quantity
        messagebox.showinfo("تم", f"تم بيع {quantity} من {name}.")
    else:
        messagebox.showerror("خطأ", "الكمية غير كافية في المخزون!")

def show_report():
    report = ""
    grand_profit = 0
    total_sales = 0
    for name, info in products.items():
        remaining = info['purchased'] - info['sold']
        profit_per_item = info['sell_price'] - info['buy_price']
        profit_total = profit_per_item * info['sold']
        profit_ratio = (profit_per_item / info['buy_price'] * 100) if info['buy_price'] else 0
        report += (f"{name}: مشتريات={info['purchased']}, مبيعات={info['sold']}, متبقي={remaining}, "
                   f"ربح={profit_total:.2f} جنيه، نسبة الربح={profit_ratio:.2f}%
")
        grand_profit += profit_total
        total_sales += info['sell_price'] * info['sold']
    report += f"
إجمالي الربح: {grand_profit:.2f} جنيه
إجمالي قيمة المبيعات: {total_sales:.2f} جنيه"
    messagebox.showinfo("تقرير المبيعات", report)

def main():
    root = tk.Tk()
    root.title("برنامج مبيعات ومشتريات")
    root.geometry("350x250")

    tk.Button(root, text="إضافة مشتريات", command=add_purchase, width=25).pack(pady=5)
    tk.Button(root, text="تحديد سعر البيع", command=set_sell_price, width=25).pack(pady=5)
    tk.Button(root, text="إضافة مبيعات", command=sell_product, width=25).pack(pady=5)
    tk.Button(root, text="عرض التقرير", command=show_report, width=25).pack(pady=5)
    tk.Button(root, text="خروج", command=root.destroy, width=25).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
