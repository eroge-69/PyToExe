import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import openpyxl

# ===== ���� ������ =====
conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    date TEXT,
    description TEXT,
    amount REAL,
    status TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
)
""")
conn.commit()

# ===== ������� � Excel =====
def export_clients_to_excel():
    cursor.execute("SELECT * FROM clients")
    data = cursor.fetchall()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "�������"

    ws.append(["ID", "���", "�������", "E-mail"])
    for row in data:
        ws.append(row)

    wb.save("clients.xlsx")
    messagebox.showinfo("�������", "���� clients.xlsx ������� ��������!")

def export_orders_to_excel():
    cursor.execute("""SELECT orders.id, clients.name, orders.date, orders.description, orders.amount, orders.status
                      FROM orders LEFT JOIN clients ON clients.id = orders.client_id""")
    data = cursor.fetchall()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "������"

    ws.append(["ID ������", "������", "����", "��������", "�����", "������"])
    for row in data:
        ws.append(row)

    wb.save("orders.xlsx")
    messagebox.showinfo("�������", "���� orders.xlsx ������� ��������!")

# ===== �������� ���� =====
root = tk.Tk()
root.title("���� �������� � �������")
root.geometry("1050x700")

tabControl = ttk.Notebook(root)
tab_clients = ttk.Frame(tabControl)
tab_orders = ttk.Frame(tabControl)
tabControl.add(tab_clients, text='�������')
tabControl.add(tab_orders, text='������')
tabControl.pack(expand=1, fill="both")

# ===== ������� =====
def load_clients(filter_text=None):
    for row in tree_clients.get_children():
        tree_clients.delete(row)
    if filter_text:
        cursor.execute("SELECT * FROM clients WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?",
                       (f"%{filter_text}%", f"%{filter_text}%", f"%{filter_text}%"))
    else:
        cursor.execute("SELECT * FROM clients")
    for r in cursor.fetchall():
        tree_clients.insert("", "end", values=r)

def add_client():
    name, phone, email = entry_name.get(), entry_phone.get(), entry_email.get()
    if not name:
        messagebox.showwarning("������", "������� ��� �������")
        return
    cursor.execute("INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
    conn.commit()
    load_clients()

def delete_client():
    selected = tree_clients.selection()
    if not selected:
        return
    client_id = tree_clients.item(selected[0])["values"][0]
    cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
    cursor.execute("DELETE FROM orders WHERE client_id=?", (client_id,))
    conn.commit()
    load_clients()
    load_orders()

def edit_client():
    selected = tree_clients.selection()
    if not selected:
        return
    data = tree_clients.item(selected[0])["values"]

    win = tk.Toplevel(root)
    win.title("������������� �������")

    tk.Label(win, text="���:").grid(row=0, column=0)
    e_name = tk.Entry(win)
    e_name.insert(0, data[1])
    e_name.grid(row=0, column=1)

    tk.Label(win, text="�������:").grid(row=1, column=0)
    e_phone = tk.Entry(win)
    e_phone.insert(0, data[2])
    e_phone.grid(row=1, column=1)

    tk.Label(win, text="E-mail:").grid(row=2, column=0)
    e_email = tk.Entry(win)
    e_email.insert(0, data[3])
    e_email.grid(row=2, column=1)

    def save():
        cursor.execute("UPDATE clients SET name=?, phone=?, email=? WHERE id=?",
                       (e_name.get(), e_phone.get(), e_email.get(), data[0]))
        conn.commit()
        load_clients()
        win.destroy()

    tk.Button(win, text="���������", command=save).grid(row=3, columnspan=2, pady=10)

frame_c = tk.Frame(tab_clients)
frame_c.pack(pady=10)

tk.Label(frame_c, text="���:").grid(row=0, column=0)
entry_name = tk.Entry(frame_c)
entry_name.grid(row=0, column=1)

tk.Label(frame_c, text="�������:").grid(row=0, column=2)
entry_phone = tk.Entry(frame_c)
entry_phone.grid(row=0, column=3)

tk.Label(frame_c, text="E-mail:").grid(row=0, column=4)
entry_email = tk.Entry(frame_c)
entry_email.grid(row=0, column=5)

tk.Button(frame_c, text="��������", command=add_client).grid(row=0, column=6, padx=5)
tk.Button(frame_c, text="�������������", command=edit_client).grid(row=0, column=7, padx=5)
tk.Button(frame_c, text="�������", command=delete_client).grid(row=0, column=8, padx=5)
tk.Button(frame_c, text="������� � Excel", command=export_clients_to_excel).grid(row=0, column=9, padx=5)

frame_c_search = tk.Frame(tab_clients)
frame_c_search.pack(pady=5)
tk.Label(frame_c_search, text="�����:").pack(side=tk.LEFT)
search_client_entry = tk.Entry(frame_c_search)
search_client_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_c_search, text="������", command=lambda: load_clients(search_client_entry.get())).pack(side=tk.LEFT, padx=5)
tk.Button(frame_c_search, text="�������� ���", command=lambda: load_clients()).pack(side=tk.LEFT, padx=5)

tree_clients = ttk.Treeview(tab_clients, columns=("id", "name", "phone", "email"), show="headings")
for col in ("id", "name", "phone", "email"):
    tree_clients.heading(col, text=col)
tree_clients.pack(expand=True, fill="both", pady=10)

# ===== ������ =====
def load_orders(filter_text=None):
    for row in tree_orders.get_children():
        tree_orders.delete(row)
    if filter_text:
        cursor.execute("""SELECT orders.id, clients.name, orders.date, orders.description, orders.amount, orders.status
                          FROM orders LEFT JOIN clients ON clients.id = orders.client_id
                          WHERE clients.name LIKE ? OR orders.description LIKE ? OR orders.status LIKE ?""",
                       (f"%{filter_text}%", f"%{filter_text}%", f"%{filter_text}%"))
    else:
        cursor.execute("""SELECT orders.id, clients.name, orders.date, orders.description, orders.amount, orders.status
                          FROM orders LEFT JOIN clients ON clients.id = orders.client_id""")
    for r in cursor.fetchall():
        tree_orders.insert("", "end", values=r)

def add_order():
    client_id = entry_client_id.get()
    date, desc, amount, status = entry_date.get(), entry_desc.get(), entry_amount.get(), entry_status.get()
    if not client_id:
        messagebox.showwarning("������", "������� ID �������")
        return
    cursor.execute("INSERT INTO orders (client_id, date, description, amount, status) VALUES (?, ?, ?, ?, ?)",
                   (client_id, date, desc, amount, status))
    conn.commit()
    load_orders()

def delete_order():
    selected = tree_orders.selection()
    if not selected:
        return
    order_id = tree_orders.item(selected[0])["values"][0]
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    load_orders()

def edit_order():
    selected = tree_orders.selection()
    if not selected:
        return
    data = tree_orders.item(selected[0])["values"]

    win = tk.Toplevel(root)
    win.title("������������� �����")

    tk.Label(win, text="����:").grid(row=0, column=0)
    e_date = tk.Entry(win)
    e_date.insert(0, data[2])
    e_date.grid(row=0, column=1)

    tk.Label(win, text="��������:").grid(row=1, column=0)
    e_desc = tk.Entry(win)
    e_desc.insert(0, data[3])
    e_desc.grid(row=1, column=1)

    tk.Label(win, text="�����:").grid(row=2, column=0)
    e_amount = tk.Entry(win)
    e_amount.insert(0, data[4])
    e_amount.grid(row=2, column=1)

    tk.Label(win, text="������:").grid(row=3, column=0)
    e_status = tk.Entry(win)
    e_status.insert(0, data[5])
    e_status.grid(row=3, column=1)

    def save():
        cursor.execute("UPDATE orders SET date=?, description=?, amount=?, status=? WHERE id=?",
                       (e_date.get(), e_desc.get(), e_amount.get(), e_status.get(), data[0]))
        conn.commit()
        load_orders()
        win.destroy()

    tk.Button(win, text="���������", command=save).grid(row=4, columnspan=2, pady=10)

frame_o = tk.Frame(tab_orders)
frame_o.pack(pady=10)

tk.Label(frame_o, text="ID �������:").grid(row=0, column=0)
entry_client_id = tk.Entry(frame_o, width=5)
entry_client_id.grid(row=0, column=1)

tk.Label(frame_o, text="����:").grid(row=0, column=2)
entry_date = tk.Entry(frame_o, width=10)
entry_date.grid(row=0, column=3)

tk.Label(frame_o, text="��������:").grid(row=0, column=4)
entry_desc = tk.Entry(frame_o, width=20)
entry_desc.grid(row=0, column=5)

tk.Label(frame_o, text="�����:").grid(row=0, column=6)
entry_amount = tk.Entry(frame_o, width=10)
entry_amount.grid(row=0, column=7)

tk.Label(frame_o, text="������:").grid(row=0, column=8)
entry_status = tk.Entry(frame_o, width=10)
entry_status.grid(row=0, column=9)

tk.Button(frame_o, text="��������", command=add_order).grid(row=0, column=10, padx=5)
tk.Button(frame_o, text="�������������", command=edit_order).grid(row=0, column=11, padx=5)
tk.Button(frame_o, text="�������", command=delete_order).grid(row=0, column=12, padx=5)
tk.Button(frame_o, text="������� � Excel", command=export_orders_to_excel).grid(row=0, column=13, padx=5)

frame_o_search = tk.Frame(tab_orders)
frame_o_search.pack(pady=5)
tk.Label(frame_o_search, text="�����:").pack(side=tk.LEFT)
search_order_entry = tk.Entry(frame_o_search)
search_order_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_o_search, text="������", command=lambda: load_orders(search_order_entry.get())).pack(side=tk.LEFT, padx=5)
tk.Button(frame_o_search, text="�������� ���", command=lambda: load_orders()).pack(side=tk.LEFT, padx=5)

tree_orders = ttk.Treeview(tab_orders, columns=("id", "client", "date", "desc", "amount", "status"), show="headings")
for col in ("id", "client", "date", "desc", "amount", "status"):
    tree_orders.heading(col, text=col)
tree_orders.pack(expand=True, fill="both", pady=10)

# ===== ����� =====
load_clients()
load_orders()
root.mainloop()
