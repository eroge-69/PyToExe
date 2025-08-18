import pandas as pd
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from datetime import date
import os

# --- قائمة السلع ---
items = ["FM 6","FM 8","FM 10","حديد 8","حديد 10","حديد 12","حديد 14",
         "حديد 16","حديد 20","تريا سودي 4","تريا سودي 5",
         "بوترال 8","بوترال 9","بوترال 10","بوترال 11"]

# --- ملفات البيانات ---
DATA_FILE = "inventory_data.xlsx"

# --- إنشاء جداول البيانات أو تحميلها ---
if os.path.exists(DATA_FILE):
    xls = pd.ExcelFile(DATA_FILE)
    if "Transactions" in xls.sheet_names:
        transactions = pd.read_excel(DATA_FILE, sheet_name="Transactions")
    else:
        transactions = pd.DataFrame(columns=["تاريخ", "العميل", "نوع المعاملة", "الوصف", "الكمية"])
    
    if "Stock" in xls.sheet_names:
        stock = pd.read_excel(DATA_FILE, sheet_name="Stock")
    else:
        stock = pd.DataFrame(columns=["الوصف","الصادر","الوارد","المخزون"])
        for item in items:
            stock = stock.append({"الوصف": item, "الصادر": 0, "الوارد": 0, "المخزون":0}, ignore_index=True)
else:
    transactions = pd.DataFrame(columns=["تاريخ", "العميل", "نوع المعاملة", "الوصف", "الكمية"])
    stock = pd.DataFrame(columns=["الوصف","الصادر","الوارد","المخزون"])
    for item in items:
      #   stock = stock.append({"الوصف": item, "الصادر": 0, "الوارد": 0, "المخزون":0}, ignore_index=True)
        stock = pd.concat([stock, pd.DataFrame([{"الوصف": item, "الصادر": 0, "الوارد": 0, "المخزون":0}])], ignore_index=True)


# --- دالة لإضافة المعاملة ---
def add_transaction():
    client = client_entry.get().strip()
    transaction_type = type_combo.get()
    item_name = item_combo.get()
    qty_text = qty_entry.get().strip()
    
    if client == "":
        messagebox.showwarning("خطأ", "يجب إدخال اسم العميل")
        return
    if transaction_type == "":
        messagebox.showwarning("خطأ", "يجب اختيار نوع المعاملة")
        return
    if item_name == "":
        messagebox.showwarning("خطأ", "يجب اختيار السلعة")
        return
    if qty_text == "":
        messagebox.showwarning("خطأ", "يجب إدخال الكمية")
        return
    
    try:
        qty = float(qty_text)
    except:
        messagebox.showwarning("خطأ", "الكمية يجب أن تكون رقمية")
        return
    
    # التحقق من المخزون للصادر
    stock_row = stock[stock["الوصف"] == item_name].index[0]
    current_stock = stock.at[stock_row, "المخزون"]
    if transaction_type == "صادر" and qty > current_stock:
        messagebox.showerror("خطأ", "الكمية الصادرة أكبر من المخزون الحالي!")
        return
    
    # إضافة المعاملة
    today = date.today().strftime("%Y-%m-%d")
    global transactions
    transactions = pd.concat([transactions, pd.DataFrame([{
    "تاريخ": today,
    "العميل": client,
    "نوع المعاملة": transaction_type,
    "الوصف": item_name,
    "الكمية": qty
   }])], ignore_index=True)

    
    # تحديث المخزون
    if transaction_type == "صادر":
        stock.at[stock_row, "الصادر"] += qty
    else:
        stock.at[stock_row, "الوارد"] += qty
    stock.at[stock_row, "المخزون"] = stock.at[stock_row, "الوارد"] - stock.at[stock_row, "الصادر"]
    
    # تنظيف المدخلات
    client_entry.delete(0, END)
    type_combo.set("")
    item_combo.set("")
    qty_entry.delete(0, END)
    
    update_stock_table()
    update_transactions_table()
    messagebox.showinfo("تم", "تمت إضافة المعاملة بنجاح!")

# --- تحديث جدول المخزون في الواجهة ---
def update_stock_table():
    for row in stock_table.get_children():
        stock_table.delete(row)
    for idx, row in stock.iterrows():
        stock_table.insert("", END, values=(row["الوصف"], row["الصادر"], row["الوارد"], row["المخزون"]))

# --- تحديث جدول المعاملات في الواجهة ---
def update_transactions_table():
    for row in trans_table.get_children():
        trans_table.delete(row)
    for idx, row in transactions.iterrows():
        trans_table.insert("", END, values=(row["تاريخ"], row["العميل"], row["نوع المعاملة"], row["الوصف"], row["الكمية"]))

# --- حفظ البيانات إلى ملف Excel ---
def save_data():
    with pd.ExcelWriter(DATA_FILE) as writer:
        transactions.to_excel(writer, sheet_name="Transactions", index=False)
        stock.to_excel(writer, sheet_name="Stock", index=False)
    messagebox.showinfo("تم", "تم حفظ البيانات بنجاح!")

# --- واجهة المستخدم ---
root = Tk()
root.title("نظام إدارة المخزون")

tab_control = ttk.Notebook(root)
tab1 = Frame(tab_control)
tab2 = Frame(tab_control)
tab_control.add(tab1, text="المعاملات")
tab_control.add(tab2, text="المخزون")
tab_control.pack(expand=1, fill="both")

# --- Tab 1: المعاملات ---
Label(tab1, text="اسم العميل").grid(row=0, column=0, padx=5, pady=5)
client_entry = Entry(tab1)
client_entry.grid(row=0, column=1, padx=5, pady=5)

Label(tab1, text="نوع المعاملة").grid(row=0, column=2, padx=5, pady=5)
type_combo = ttk.Combobox(tab1, values=["صادر","وارد"], state="readonly")
type_combo.grid(row=0, column=3, padx=5, pady=5)

Label(tab1, text="السلعة").grid(row=0, column=4, padx=5, pady=5)
item_combo = ttk.Combobox(tab1, values=items, state="readonly")
item_combo.grid(row=0, column=5, padx=5, pady=5)

Label(tab1, text="الكمية").grid(row=0, column=6, padx=5, pady=5)
qty_entry = Entry(tab1)
qty_entry.grid(row=0, column=7, padx=5, pady=5)

Button(tab1, text="إضافة المعاملة", command=add_transaction).grid(row=0, column=8, padx=5, pady=5)
Button(tab1, text="حفظ البيانات", command=save_data).grid(row=0, column=9, padx=5, pady=5)

# جدول المعاملات
trans_table = ttk.Treeview(tab1, columns=("تاريخ","العميل","نوع المعاملة","الوصف","الكمية"), show="headings")
for col in ("تاريخ","العميل","نوع المعاملة","الوصف","الكمية"):
    trans_table.heading(col, text=col)
trans_table.grid(row=1, column=0, columnspan=10, padx=5, pady=5)
update_transactions_table()

# --- Tab 2: المخزون ---
stock_table = ttk.Treeview(tab2, columns=("الوصف","الصادر","الوارد","المخزون"), show="headings")
for col in ("الوصف","الصادر","الوارد","المخزون"):
    stock_table.heading(col, text=col)
stock_table.pack(fill="both", expand=True)
update_stock_table()

# --- الحفظ التلقائي عند الإغلاق ---
def on_closing():
    save_data()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
