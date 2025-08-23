import tkinter as tk
from tkinter import messagebox

# ����� ����� ��������
root = tk.Tk()
root.title("School Program")
root.geometry("400x300")

# ���� ������ ������
students = []

# ���� ��������
def add_student():
    name = entry_name.get()
    if name:
        students.append(name)
        entry_name.delete(0, tk.END)
        messagebox.showinfo("��", f"�� ����� ������: {name}")
    else:
        messagebox.showwarning("���", "���� ��� ������")

def show_students():
    if students:
        messagebox.showinfo("������", "\n".join(students))
    else:
        messagebox.showinfo("������", "�� ���� ���� ���")

# ����� ��������
tk.Label(root, text="��� ������:").pack(pady=5)
entry_name = tk.Entry(root)
entry_name.pack(pady=5)

tk.Button(root, text="����� ������", command=add_student).pack(pady=5)
tk.Button(root, text="��� ������", command=show_students).pack(pady=5)

root.mainloop()
