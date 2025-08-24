import tkinter as tk
from tkinter import ttk, messagebox
import csv, os
from datetime import datetime

FILE_NAME = "part_borrow_data.csv"
PART_FILE = "parts.csv"

# ----------------------------
# สร้างไฟล์ถ้ายังไม่มี
# ----------------------------
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "Employee", "PartName", "Quantity", "Date"])

if not os.path.exists(PART_FILE):
    with open(PART_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["PartName", "Quantity"])


# ----------------------------
# จัดการคลังสินค้า
# ----------------------------
def load_parts():
    parts = {}
    with open(PART_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parts[row["PartName"]] = int(row["Quantity"])
    return parts

def save_parts(parts):
    with open(PART_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["PartName", "Quantity"])
        for name, qty in parts.items():
            writer.writerow([name, qty])

# ----------------------------
# ฟังก์ชันหลัก
# ----------------------------
def save_record():
    employee = entry_employee.get().strip()
    part = combo_part.get().strip()
    qty_str = entry_quantity.get().strip()

    if not employee or not part or not qty_str.isdigit():
        messagebox.showerror("Error", "กรุณากรอกข้อมูลให้ครบถ้วน")
        return

    qty = int(qty_str)
    parts = load_parts()

    if part not in parts:
        messagebox.showerror("Error", "ไม่พบอุปกรณ์นี้ในระบบ")
        return
    if parts[part] < qty:
        messagebox.showerror("Error", f"จำนวนคงเหลือ {parts[part]} ไม่พอ")
        return

    # update stock
    parts[part] -= qty
    save_parts(parts)

    # บันทึกการเบิก
    with open(FILE_NAME, "r", newline="", encoding="utf-8-sig") as f:
        reader = list(csv.reader(f))
        last_id = int(reader[-1][0]) if len(reader) > 1 else 0

    new_id = last_id + 1
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(FILE_NAME, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, employee, part, qty, date_str])

    messagebox.showinfo("Saved", "บันทึกข้อมูลเรียบร้อย")
    show_data()
    show_stock()
    entry_employee.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)

def add_stock(delta):
    part = combo_part.get().strip()
    qty_str = entry_quantity.get().strip()
    if not part or not qty_str.isdigit():
        messagebox.showerror("Error", "กรุณาเลือกอุปกรณ์และใส่จำนวน")
        return
    qty = int(qty_str)
    parts = load_parts()
    if part not in parts:
        messagebox.showerror("Error", "ไม่พบอุปกรณ์นี้ในระบบ")
        return
    parts[part] += delta * qty
    if parts[part] < 0:
        parts[part] = 0
    save_parts(parts)
    show_stock()
    entry_quantity.delete(0, tk.END)

def add_part():
    new_part = entry_new_part.get().strip()
    qty_str = entry_new_qty.get().strip()
    if not new_part or not qty_str.isdigit():
        messagebox.showerror("Error", "กรุณากรอกชื่ออุปกรณ์และจำนวนเริ่มต้น")
        return
    qty = int(qty_str)
    parts = load_parts()
    if new_part in parts:
        messagebox.showerror("Error", "มีอุปกรณ์นี้อยู่แล้ว")
        return
    parts[new_part] = qty
    save_parts(parts)
    messagebox.showinfo("Saved", f"เพิ่มอุปกรณ์ {new_part} เรียบร้อย")
    combo_part["values"] = list(parts.keys())
    entry_new_part.delete(0, tk.END)
    entry_new_qty.delete(0, tk.END)
    show_stock()

def show_data():
    for row in tree_borrow.get_children():
        tree_borrow.delete(row)
    with open(FILE_NAME, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            tree_borrow.insert("", tk.END, values=row)

def show_stock():
    for row in tree_stock.get_children():
        tree_stock.delete(row)
    parts = load_parts()
    for name, qty in parts.items():
        tree_stock.insert("", tk.END, values=(name, qty))

# ----------------------------
# GUI
# ----------------------------
root = tk.Tk()
root.title("Part Borrow & Stock System")
root.geometry("850x600")

frame_form = tk.LabelFrame(root, text="บันทึกการเบิก")
frame_form.pack(pady=10, padx=10, fill="x")

tk.Label(frame_form, text="ชื่อพนักงาน").grid(row=0, column=0, padx=5, pady=5)
entry_employee = tk.Entry(frame_form)
entry_employee.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="รายการชิ้นส่วน").grid(row=1, column=0, padx=5, pady=5)
combo_part = ttk.Combobox(frame_form, values=list(load_parts().keys()))
combo_part.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form, text="จำนวน").grid(row=2, column=0, padx=5, pady=5)
entry_quantity = tk.Entry(frame_form)
entry_quantity.grid(row=2, column=1, padx=5, pady=5)

btn_save = tk.Button(frame_form, text="เบิก", command=save_record)
btn_save.grid(row=3, column=0, columnspan=2, pady=10)

btn_add_stock = tk.Button(frame_form, text="เพิ่มสต๊อก", command=lambda: add_stock(1))
btn_add_stock.grid(row=4, column=0, padx=5, pady=5)

btn_reduce_stock = tk.Button(frame_form, text="ลดสต๊อก", command=lambda: add_stock(-1))
btn_reduce_stock.grid(row=4, column=1, padx=5, pady=5)

frame_new = tk.LabelFrame(root, text="เพิ่มอุปกรณ์ใหม่")
frame_new.pack(pady=10, padx=10, fill="x")

tk.Label(frame_new, text="ชื่ออุปกรณ์").grid(row=0, column=0, padx=5, pady=5)
entry_new_part = tk.Entry(frame_new)
entry_new_part.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_new, text="จำนวนเริ่มต้น").grid(row=1, column=0, padx=5, pady=5)
entry_new_qty = tk.Entry(frame_new)
entry_new_qty.grid(row=1, column=1, padx=5, pady=5)

btn_add_part = tk.Button(frame_new, text="เพิ่มอุปกรณ์", command=add_part)
btn_add_part.grid(row=2, column=0, columnspan=2, pady=10)

frame_tables = tk.Frame(root)
frame_tables.pack(fill="both", expand=True, padx=10, pady=10)

# ตารางเบิก
tree_borrow = ttk.Treeview(frame_tables, columns=("Id","Employee","PartName","Quantity","Date"), show="headings")
for col in ("Id","Employee","PartName","Quantity","Date"):
    tree_borrow.heading(col, text=col)
tree_borrow.pack(side="left", fill="both", expand=True, padx=5)

# ตาราง stock
tree_stock = ttk.Treeview(frame_tables, columns=("PartName","Quantity"), show="headings")
for col in ("PartName","Quantity"):
    tree_stock.heading(col, text=col)
tree_stock.pack(side="right", fill="both", expand=True, padx=5)

show_data()
show_stock()
root.mainloop()
