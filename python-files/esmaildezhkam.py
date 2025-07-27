import sqlite3
import tkinter as tk
from tkinter import messagebox

# اتصال به دیتابیس
conn = sqlite3.connect("vakeel_simple.db")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS appointments
               (id INTEGER PRIMARY KEY, name TEXT, date TEXT, time TEXT, type TEXT)''')
conn.commit()

# توابع
def add():
    if name.get() and date.get() and time.get() and type_.get():
        cur.execute("INSERT INTO appointments (name, date, time, type) VALUES (?, ?, ?, ?)",
                    (name.get(), date.get(), time.get(), type_.get()))
        conn.commit()
        show()
        clear()
    else:
        messagebox.showwarning("error")

def show():
    listbox.delete(0, tk.END)
    for row in cur.execute("SELECT * FROM appointments"):
        listbox.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} {row[3]} | {row[4]}")

def select(event):
    global selected_id
    if not listbox.curselection():
        return
    idx = listbox.curselection()[0]
    data = listbox.get(idx).split(" | ")
    selected_id = int(data[0])
    name.delete(0, tk.END); name.insert(0, data[1])
    date.delete(0, tk.END); date.insert(0, data[2].split()[0])
    time.delete(0, tk.END); time.insert(0, data[2].split()[1])
    type_.delete(0, tk.END); type_.insert(0, data[3])

def delete():
    if selected_id:
        cur.execute("DELETE FROM appointments WHERE id=?", (selected_id,))
        conn.commit()
        show()
        clear()

def update():
    if selected_id:
        cur.execute("UPDATE appointments SET name=?, date=?, time=?, type=? WHERE id=?",
                    (name.get(), date.get(), time.get(), type_.get(), selected_id))
        conn.commit()
        show()
        clear()

def clear():
    name.delete(0, tk.END)
    date.delete(0, tk.END)
    time.delete(0, tk.END)
    type_.delete(0, tk.END)

# رابط گرافیکی
root = tk.Tk()
root.title("مدیریت جلسات اسماعیل دژکام")

tk.Label(root, text="name").grid(row=0, column=0)
tk.Label(root, text="date").grid(row=1, column=0)
tk.Label(root, text="hour").grid(row=2, column=0)
tk.Label(root, text="type").grid(row=3, column=0)

name = tk.Entry(root); name.grid(row=0, column=1)
date = tk.Entry(root); date.grid(row=1, column=1)
time = tk.Entry(root); time.grid(row=2, column=1)
type_ = tk.Entry(root); type_.grid(row=3, column=1)

tk.Button(root, text="ok", command=add).grid(row=4, column=0)
tk.Button(root, text="edit", command=update).grid(row=4, column=1)
tk.Button(root, text="delete", command=delete).grid(row=4, column=2)

listbox = tk.Listbox(root, width=50)
listbox.grid(row=5, column=0, columnspan=3)
listbox.bind("<<ListboxSelect>>", select)

selected_id = None
show()
root.mainloop()