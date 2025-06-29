


import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATA_FILE = "data.json"
TASKS = [
"All", "Enterance", "Bagh", "Formalite", "Man",
"Reel", "Export", "Select", "Edit", "Album",
"Chek", "Album send"
]

class ChecklistApp:
def __init__(self, root):
self.root = root
self.root.title("Davoud Customer Checklist")
self.data = self.load_data()

# ناحیه بالا: نوار عنوان‌ها (کارها)
self.header_frame = tk.Frame(root)
self.header_frame.pack(fill=tk.X, padx=5, pady=5)

tk.Label(self.header_frame, text="مشتری", width=15, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=0)

for col, task in enumerate(TASKS):
tk.Label(self.header_frame, text=task, width=10, anchor="center", font=("Arial", 10, "bold")).grid(row=0, column=col+1)

# ناحیه وسط: جدول مشتری‌ها
self.table_frame = tk.Frame(root)
self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5)

self.check_vars = {}

self.render_table()

# ناحیه پایین: دکمه‌ها
self.footer_frame = tk.Frame(root)
self.footer_frame.pack(pady=10)

tk.Button(self.footer_frame, text="➕ افزودن مشتری", command=self.add_client).pack(side=tk.LEFT, padx=10)
tk.Button(self.footer_frame, text="💾 ذخیره", command=self.save_all).pack(side=tk.LEFT)

def load_data(self):
if os.path.exists(DATA_FILE):
with open(DATA_FILE, "r", encoding="utf-8") as f:
try:
return json.load(f)
except:
return {}
else:
return {}

def save_data(self):
with open(DATA_FILE, "w", encoding="utf-8") as f:
json.dump(self.data, f, ensure_ascii=False, indent=2)

def render_table(self):
# حذف قبلی‌ها
for widget in self.table_frame.winfo_children():
widget.destroy()
self.check_vars.clear()

for row, client in enumerate(self.data.keys()):
tk.Label(self.table_frame, text=client, width=15, anchor="w").grid(row=row, column=0, sticky="w", padx=2, pady=2)
self.check_vars[client] = {}
for col, task in enumerate(TASKS):
var = tk.IntVar(value=1 if self.data[client].get(task, False) else 0)
cb = tk.Checkbutton(self.table_frame, variable=var)
cb.grid(row=row, column=col+1, padx=2)
self.check_vars[client][task] = var

def add_client(self):
name = simpledialog.askstring("افزودن مشتری", "نام مشتری را وارد کنید:")
if name:
name = name.strip()
if name in self.data:
messagebox.showwarning("تکراری", "این مشتری قبلاً وجود دارد.")
return
self.data[name] = {task: False for task in TASKS}
self.render_table()
self.save_data()

def save_all(self):
for client in self.check_vars:
self.data[client] = {task: bool(var.get()) for task, var in self.check_vars[client].items()}
self.save_data()
messagebox.showinfo("ذخیره شد", "اطلاعات همه مشتری‌ها ذخیره شد.")

if __name__ == "__main__":
root = tk.Tk()
app = ChecklistApp(root)
root.geometry("1200x600")
root.mainloop()
