import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("گزارش‌گیری - آبفا یار")
root.geometry("800x600")
root.configure(bg="#f9f9f9")
font_style = ("Tahoma", 12)

tk.Label(root, text="سال مالی:", font=font_style, bg="#f9f9f9").grid(row=0, column=0, padx=10, pady=10, sticky="w")
year_filter = ttk.Combobox(root, values=["1402", "1403", "1404"], font=font_style, width=15)
year_filter.grid(row=0, column=1, padx=10, pady=10)
year_filter.set("1403")

tk.Label(root, text="محل پرداخت:", font=font_style, bg="#f9f9f9").grid(row=0, column=2, padx=10, pady=10, sticky="w")
place_filter = ttk.Combobox(root, values=["همه", "جاری", "آب استان", "فاضلاب استان", "آب اهواز", "فاضلاب اهواز"], font=font_style, width=20)
place_filter.grid(row=0, column=3, padx=10, pady=10)
place_filter.set("همه")

tk.Label(root, text="وضعیت:", font=font_style, bg="#f9f9f9").grid(row=0, column=4, padx=10, pady=10, sticky="w")
status_filter = ttk.Combobox(root, values=["همه", "کامل", "ناقص", "بدون قیمت"], font=font_style, width=15)
status_filter.grid(row=0, column=5, padx=10, pady=10)
status_filter.set("همه")

columns = ("عنوان", "قیمت", "محل پرداخت", "سال مالی", "وضعیت")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.grid(row=1, column=0, columnspan=6, padx=10, pady=10)

sample_data = [
    ("آگهی روزنامه", "120000000", "آب اهواز", "1403", "کامل"),
    ("هزینه چاپ", "", "فاضلاب استان", "1403", "بدون قیمت"),
    ("تبلیغات محیطی", "85000000", "جاری", "1403", "ناقص")
]
for item in sample_data:
    tree.insert("", "end", values=item)

tk.Button(root, text="خروجی PDF", font=font_style, bg="#2196F3", fg="white", width=15).grid(row=2, column=2, pady=20)
tk.Button(root, text="خروجی Excel", font=font_style, bg="#4CAF50", fg="white", width=15).grid(row=2, column=3, pady=20)

root.mainloop()