import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

file_path = r"C:\Users\SOLAIMAN\Desktop\أوراق السيارات  2025.xlsx"
sheet_name = "ROMIX"

try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
except Exception as e:
    messagebox.showerror("خطأ", f"تعذر فتح Excel: {e}")
    exit()

today = datetime.today().date()

root = tk.Tk()
root.title("تنبيه صلاحية أوراق السيارات")
root.geometry("900x400")

tree = ttk.Treeview(root)
tree["columns"] = ("Car", "Driver", "Doc", "Expiry", "Status")
tree.heading("#0", text="")
tree.column("#0", width=0, stretch=tk.NO)
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=150)
tree.pack(fill=tk.BOTH, expand=True)

for idx, row in df.iloc[3:].iterrows():
    car = row[1]
    driver = row[2]
    for j in range(3, len(row)):
        doc = df.iloc[2, j]
        exp = row[j]
        if pd.notna(exp) and isinstance(exp, pd.Timestamp):
            diff = (exp.date() - today).days
            if diff < 0:
                status = "منتهي"
                tag = "alert"
            elif diff <= 30:
                status = f"باقي {diff} يوم"
                tag = "warning"
            else:
                continue
            tree.insert("", tk.END, values=(car, driver, doc, exp.date(), status), tags=(tag,))
tree.tag_configure("alert", background="#ffcccc", font=("Tahoma", 10, "bold"))
tree.tag_configure("warning", background="#fff3cd", font=("Tahoma", 10))

root.mainloop()
