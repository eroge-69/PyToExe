import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ساخت دیتابیس
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    date TEXT
)''')
conn.commit()

# تابع برای نمایش همه کارها
def load_tasks():
    for i in tree.get_children():
        tree.delete(i)
    c.execute('SELECT * FROM tasks')
    for row in c.fetchall():
        tree.insert('', 'end', values=row)

# افزودن کار جدید
def add_task():
    title = title_entry.get()
    desc = desc_entry.get('1.0', 'end').strip()
    date = date_entry.get()
    if title == '':
        messagebox.showwarning('هشدار', 'لطفاً عنوان را وارد کنید')
        return
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('هشدار', 'تاریخ نامعتبر است. لطفاً از فرمت YYYY-MM-DD استفاده کنید.')
            return
    c.execute('INSERT INTO tasks (title, description, date) VALUES (?, ?, ?)', (title, desc, date))
    conn.commit()
    messagebox.showinfo('موفق', 'کار افزوده شد')
    clear_entries()
    load_tasks()

# حذف کار
def delete_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning('هشدار', 'هیچ کاری انتخاب نشده')
        return
    for sel in selected:
        item = tree.item(sel)
        c.execute('DELETE FROM tasks WHERE id=?', (item['values'][0],))
    conn.commit()
    load_tasks()

# ویرایش کار
def edit_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning('هشدار', 'هیچ کاری انتخاب نشده')
        return
    item = tree.item(selected[0])
    task_id = item['values'][0]
    title = title_entry.get()
    desc = desc_entry.get('1.0', 'end').strip()
    date = date_entry.get()
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('هشدار', 'تاریخ نامعتبر است. لطفاً از فرمت YYYY-MM-DD استفاده کنید.')
            return
    c.execute('UPDATE tasks SET title=?, description=?, date=? WHERE id=?', (title, desc, date, task_id))
    conn.commit()
    load_tasks()
    messagebox.showinfo('موفق', 'ویرایش انجام شد')

# جستجو
def search_task():
    key = search_entry.get()
    for i in tree.get_children():
        tree.delete(i)
    c.execute('SELECT * FROM tasks WHERE title LIKE ? OR date LIKE ?', (f'%{key}%', f'%{key}%'))
    results = c.fetchall()
    if results:
        for row in results:
            tree.insert('', 'end', values=row)
    else:
        messagebox.showinfo('نتیجه', 'هیچ کاری یافت نشد')

# پاک کردن فیلدها
def clear_entries():
    title_entry.delete(0, 'end')
    desc_entry.delete('1.0', 'end')
    date_entry.delete(0, 'end')

# رابط گرافیکی
root = tk.Tk()
root.title('مدیریت کارها')
root.geometry('700x500')

# فرم ورودی
form_frame = tk.Frame(root)
form_frame.pack(pady=10)

tk.Label(form_frame, text='عنوان کار:').grid(row=0, column=2)
title_entry = tk.Entry(form_frame, width=30, justify='right')
title_entry.grid(row=0, column=1)

tk.Label(form_frame, text='تاریخ (YYYY-MM-DD):').grid(row=1, column=2)
date_entry = tk.Entry(form_frame, width=30, justify='right')
date_entry.grid(row=1, column=1)

tk.Label(form_frame, text='توضیح:').grid(row=2, column=2)
desc_entry = tk.Text(form_frame, height=3, width=30)
desc_entry.grid(row=2, column=1)

# دکمه‌ها
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text='افزودن', command=add_task).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text='ویرایش', command=edit_task).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text='حذف', command=delete_task).grid(row=0, column=1, padx=5)

tk.Label(btn_frame, text='جستجو:').grid(row=0, column=0, padx=5)
search_entry = tk.Entry(btn_frame, width=20)
search_entry.grid(row=0, column=4)
tk.Button(btn_frame, text='جستجو', command=search_task).grid(row=0, column=5, padx=5)
tk.Button(btn_frame, text='نمایش همه', command=load_tasks).grid(row=0, column=6, padx=5)

# جدول کارها
columns = ('id', 'title', 'description', 'date')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col, text in zip(columns, ['شماره', 'عنوان کار', 'توضیح', 'تاریخ']):
    tree.heading(col, text=text, anchor='e')
    tree.column(col, anchor='e', width=150)

tree.pack(fill='both', expand=True)

load_tasks()

root.mainloop()
conn.close()

