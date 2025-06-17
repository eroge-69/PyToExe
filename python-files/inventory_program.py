
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import os
from datetime import datetime
import webbrowser

FILE_NAME = "حركة_الوارد_والصادر.xlsx"

if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["التاريخ", "اسم الصنف", "الكمية", "نوع الحركة", "ملاحظات"])
    df.to_excel(FILE_NAME, index=False)

def save_all():
    global inputs
    rows = []
    for item_entry, qty_entry, movement_var, note_entry, _ in inputs:
        item = item_entry.get()
        qty = qty_entry.get()
        movement = movement_var.get()
        notes = note_entry.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not item or not qty:
            continue
        try:
            qty = float(qty)
        except ValueError:
            continue

        rows.append([date, item, qty, movement, notes])

    if not rows:
        messagebox.showerror("خطأ", "لم يتم إدخال بيانات صالحة.")
        return

    df_old = pd.read_excel(FILE_NAME)
    df_new = pd.DataFrame(rows, columns=["التاريخ", "اسم الصنف", "الكمية", "نوع الحركة", "ملاحظات"])
    df_all = pd.concat([df_old, df_new], ignore_index=True)
    df_all.to_excel(FILE_NAME, index=False)

    messagebox.showinfo("تم", "تم حفظ جميع البيانات.")
    for widgets in rows_container.winfo_children():
        widgets.destroy()
    inputs = []
    add_row()

def open_excel():
    path = os.path.abspath(FILE_NAME)
    webbrowser.open(f"file://{path}")

def delete_row(row_frame):
    row_frame.destroy()
    inputs[:] = [entry for entry in inputs if entry[4] != row_frame]

def add_row():
    row_frame = tk.Frame(rows_container)
    row_frame.pack(fill="x", pady=2)

    item = tk.Entry(row_frame, width=20)
    item.pack(side="left", padx=2)

    qty = tk.Entry(row_frame, width=10)
    qty.pack(side="left", padx=2)

    movement = tk.StringVar()
    movement.set("وارد")
    tk.OptionMenu(row_frame, movement, "وارد", "صادر").pack(side="left", padx=2)

    note = tk.Entry(row_frame, width=20)
    note.pack(side="left", padx=2)

    del_btn = tk.Button(row_frame, text="❌", command=lambda: delete_row(row_frame), bg="red", fg="white")
    del_btn.pack(side="right", padx=2)

    inputs.append((item, qty, movement, note, row_frame))

def search_items():
    query = search_entry.get().strip()
    if not query:
        messagebox.showinfo("تنبيه", "من فضلك أدخل اسم صنف للبحث.")
        return

    df = pd.read_excel(FILE_NAME)
    result = df[df["اسم الصنف"].str.contains(query, case=False, na=False)]

    if result.empty:
        messagebox.showinfo("نتيجة البحث", "لم يتم العثور على نتائج.")
    else:
        result_file = "نتائج_البحث.xlsx"
        result.to_excel(result_file, index=False)
        webbrowser.open(f"file://{os.path.abspath(result_file)}")

def calculate_stock():
    df = pd.read_excel(FILE_NAME)
    df["الكمية"] = pd.to_numeric(df["الكمية"], errors="coerce")
    df = df.dropna(subset=["اسم الصنف", "الكمية", "نوع الحركة"])
    df["الكمية"] = df.apply(lambda row: row["الكمية"] if row["نوع الحركة"] == "وارد" else -row["الكمية"], axis=1)
    stock = df.groupby("اسم الصنف")["الكمية"].sum().reset_index()
    stock.columns = ["اسم الصنف", "الرصيد الحالي"]
    stock_file = "رصيد_المخزون.xlsx"
    stock.to_excel(stock_file, index=False)
    webbrowser.open(f"file://{os.path.abspath(stock_file)}")

root = tk.Tk()
root.title("برنامج إدارة الصادر والوارد")
root.geometry("650x600")

frame_top = tk.Frame(root)
frame_top.pack(pady=10)
tk.Label(frame_top, text="➕ إضافة صنف جديد").pack()
tk.Button(frame_top, text="➕ إضافة صف", command=add_row, bg="orange").pack()

rows_container = tk.Frame(root)
rows_container.pack(fill="both", expand=True, pady=10)

inputs = []
add_row()

tk.Button(root, text="💾 حفظ كل البيانات", command=save_all, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="📂 عرض السجل", command=open_excel, bg="blue", fg="white").pack(pady=5)

search_frame = tk.Frame(root)
search_frame.pack(pady=5)
tk.Label(search_frame, text="🔍 بحث باسم الصنف:").pack(side="left")
search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", padx=5)
tk.Button(search_frame, text="بحث", command=search_items, bg="gray", fg="white").pack(side="left")

tk.Button(root, text="📊 عرض رصيد المخزون", command=calculate_stock, bg="purple", fg="white").pack(pady=10)

root.mainloop()
