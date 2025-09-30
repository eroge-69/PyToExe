```python
import tkinter as tk
from tkinter import ttk, messagebox
import openpyxl
import datetime
import win32print
import win32ui

# ����� ������ �������� �� Excel
def load_students(file="students.xlsx"):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    students = []
    for row in sheet.iter_rows(min_row=2, values_only=True):  # ���� ��������
        if all(row):  # ����� ������ �������
            name, classroom, number = row
            students.append({"name": str(name), "class": str(classroom), "number": str(number)})
    return students

students = load_students()

# ���� �������
def print_ticket(selected_students):
    today = datetime.date.today().strftime("%d/%m/%Y")
    now_time = datetime.datetime.now().strftime("%H:%M")  # ������� ������
    printer_name = win32print.GetDefaultPrinter()
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(printer_name)

    dc.StartDoc("���� �������")
    for s in selected_students:
        text = f"""
        ����� �����
        -----------------
        ���� �������

        �����   : {s['name']}
        �����   : {s['class']}
        ������� : {today}
        �����   : {now_time}

        �������: __________
        """
        dc.StartPage()
        dc.TextOut(100, 100, text)
        dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()

# ����� ��������
root = tk.Tk()
root.title("����� ���� �������")
root.geometry("500x400")

# �����
def search():
    query = search_var.get().lower()
    results_list.delete(*results_list.get_children())
    for s in students:
        if query in s["name"].lower():
            results_list.insert("", "end", values=(s["name"], s["class"], s["number"]))

tk.Label(root, text="���� �� ������� ������:").pack(pady=5)
search_var = tk.StringVar()
tk.Entry(root, textvariable=search_var).pack(pady=5)
tk.Button(root, text="���", command=search).pack(pady=5)

# ���� �������
columns = ("�����", "�����", "�����")
results_list = ttk.Treeview(root, columns=columns, show="headings", selectmode="extended")
for col in columns:
    results_list.heading(col, text=col)
results_list.pack(padx=10, pady=10, fill="both", expand=True)

# �� �������
def print_selected():
    selected_items = results_list.selection()
    if not selected_items:
        messagebox.showwarning("�����", "������ ������ ����� ���� ��� �����")
        return
    selected_students = []
    for item in selected_items:
        vals = results_list.item(item, "values")
        selected_students.append({"name": vals[0], "class": vals[1], "number": vals[2]})
    print_ticket(selected_students)
    messagebox.showinfo("����", "��� ������� �����")

tk.Button(root, text="�����", command=print_selected, bg="lightgreen").pack(pady=10)

root.mainloop()
```
