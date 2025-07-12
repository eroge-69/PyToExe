Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.

================================ RESTART: Shell ================================
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- ПІДКЛЮЧЕННЯ ДО БАЗИ ДАНИХ ---
conn = sqlite3.connect('service_center.db')
cursor = conn.cursor()

# --- ІНІЦІАЛІЗАЦІЯ ТАБЛИЦЬ ---
def init_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        brand TEXT,
        model TEXT,
        imei TEXT,
        defect TEXT,
        repair_cost REAL,
        spare_part_id INTEGER,
        spare_part_cost REAL,
        scheduled_date TEXT,
        master TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SpareParts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        quantity INTEGER,
        unit_price REAL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Repairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        date TEXT,
        total_cost REAL,
        spare_part_id INTEGER,
        spare_part_qty INTEGER,
        master TEXT,
        FOREIGN KEY(customer_id) REFERENCES Customers(id),
        FOREIGN KEY(spare_part_id) REFERENCES SpareParts(id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Masters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )''')

    conn.commit()

# --- ДОДАТИ КЛІЄНТА ---
def add_customer():
    name = entry_name.get()
    phone = entry_phone.get()
    brand = entry_brand.get()
    model = entry_model.get()
    imei = entry_imei.get()
    defect = entry_defect.get()
    try:
        repair_cost = float(entry_repair_cost.get())
    except:
        messagebox.showerror("Помилка", "Введіть коректну вартість ремонту")
        return
    scheduled_date = entry_date.get()
    master_name = combo_master.get()

    cursor.execute('''
    INSERT INTO Customers (name, phone, brand, model, imei, defect, repair_cost, scheduled_date, master)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (name, phone, brand, model, imei, defect, repair_cost, scheduled_date, master_name))
    conn.commit()
    messagebox.showinfo("Успіх", "Клієнта додано!")
    clear_entries()
    refresh_customers()

def clear_entries():
    for e in (entry_name, entry_phone, entry_brand, entry_model, entry_imei, entry_defect, entry_repair_cost, entry_date):
        e.delete(0, tk.END)

# --- ДОДАТИ МАЙСТРА ---
def add_master():
    name = entry_master.get()
    if not name:
        messagebox.showerror("Помилка", "Введіть ім'я майстра")
        return
    cursor.execute('INSERT INTO Masters (name) VALUES (?)', (name,))
    conn.commit()
    refresh_masters()
    entry_master.delete(0, tk.END)

def refresh_masters():
    cursor.execute('SELECT name FROM Masters')
    masters = cursor.fetchall()
    combo_master['values'] = [m[0] for m in masters]

# --- ВИВІД КЛІЄНТІВ ---
def refresh_customers():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute('SELECT * FROM Customers')
    for row in cursor.fetchall():
        tree.insert('', tk.END, values=row)

# --- ВИВІД ЗАПЧАСТИН ---
def refresh_spare_parts():
    for row in tree_spare.get_children():
        tree_spare.delete(row)
    cursor.execute('SELECT * FROM SpareParts')
    for row in cursor.fetchall():
        tree_spare.insert('', tk.END, values=row)

# --- ДОДАТИ ЗАПЧАСТИНУ ---
def add_spare_part():
    name = entry_spare_name.get()
    try:
        quantity = int(entry_spare_qty.get())
        price = float(entry_spare_price.get())
    except:
        messagebox.showerror("Помилка", "Некоректне введення кількості або ціни")
        return
    cursor.execute('INSERT INTO SpareParts (name, quantity, unit_price) VALUES (?, ?, ?)',
                   (name, quantity, price))
    conn.commit()
    refresh_spare_parts()
    for e in (entry_spare_name, entry_spare_qty, entry_spare_price):
        e.delete(0, tk.END)

# --- ОФОРМЛЕННЯ РЕМОНТУ ---
def register_repair():
    selected = tree_customers.selection()
    if not selected:
        messagebox.showerror("Помилка", "Оберіть клієнта")
        return
    customer_id = tree_customers.item(selected[0])['values'][0]
    spare_part_name = combo_spare.get()
    qty_str = entry_spare_qty_repair.get()
    try:
        qty = int(qty_str)
    except:
        messagebox.showerror("Помилка", "Некоректна кількість запчастин")
        return

    cursor.execute('SELECT id, quantity, unit_price FROM SpareParts WHERE name=?', (spare_part_name,))
    sp = cursor.fetchone()
    if not sp:
        messagebox.showerror("Помилка", "Запчастина не знайдена")
        return
    sp_id, sp_qty, sp_price = sp
    if sp_qty < qty:
        messagebox.showerror("Помилка", "Недостатньо запчастин на складі")
        return

    new_qty = sp_qty - qty
    cursor.execute('UPDATE SpareParts SET quantity=? WHERE id=?', (new_qty, sp_id))
    cursor.execute('SELECT repair_cost FROM Customers WHERE id=?', (customer_id,))
    repair_cost = cursor.fetchone()[0]
    total_cost = repair_cost + (sp_price * qty)
    master_name = cursor.execute('SELECT master FROM Customers WHERE id=?', (customer_id,)).fetchone()[0]

    cursor.execute('''
    INSERT INTO Repairs (customer_id, date, total_cost, spare_part_id, spare_part_qty, master)
    VALUES (?, date('now'), ?, ?, ?, ?)''', (customer_id, total_cost, sp_id, qty, master_name))
    conn.commit()
    messagebox.showinfo("Успіх", "Ремонт зареєстрований")
    refresh_repairs()

# --- ВИВІД РЕМОНТІВ ---
def refresh_repairs():
    for row in tree_repairs.get_children():
        tree_repairs.delete(row)
    cursor.execute('''
    SELECT Repairs.id, Customers.name, Repairs.date, Repairs.total_cost, SpareParts.name, Repairs.spare_part_qty
    FROM Repairs
    JOIN Customers ON Repairs.customer_id=Customers.id
    JOIN SpareParts ON Repairs.spare_part_id=SpareParts.id
    ''')
    for row in cursor.fetchall():
        tree_repairs.insert('', tk.END, values=row)

# --- ДРУК КВИТАНЦІЇ (ВИПРАВЛЕНО) ---
def print_receipt():
    selected = tree_customers.selection()
    if not selected:
        messagebox.showerror("Помилка", "Оберіть клієнта")
        return
    customer_id = tree_customers.item(selected[0])['values'][0]
    cursor.execute('SELECT * FROM Customers WHERE id=?', (customer_id,))
    customer = cursor.fetchone()
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not filename:
        return
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Квитанція ремонтних робіт\n")
        f.write(f"Клієнт: {customer[1]}\n")
        f.write(f"Телефон: {customer[2]}\n")
        f.write(f"Модель: {customer[4]} {customer[3]}\n")
        f.write(f"IMEI: {customer[5]}\n")
        f.write(f"Заявлена несправність: {customer[6]}\n")
        f.write(f"Вартість ремонту: {customer[7]}\n")

        cursor.execute('SELECT * FROM Repairs WHERE customer_id=?', (customer_id,))
        repairs = cursor.fetchall()
        f.write("\nРоботи виконані:\n")
        total_expenses = 0
        for r in repairs:
            part_id = r[4]
            qty = r[5]
            cursor.execute('SELECT name, unit_price FROM SpareParts WHERE id=?', (part_id,))
            part_info = cursor.fetchone()
            if part_info:
                sp_name, unit_price = part_info
                f.write(f"- Запчастина: {sp_name}, кількість: {qty}, ціна за шт: {unit_price:.2f}\n")
                total_expenses += unit_price * qty

        total_income = customer[7]
        f.write(f"\nЗагальні доходи: {total_income:.2f}\n")
        f.write(f"Загальні витрати: {total_expenses:.2f}\n")
        f.write(f"Баланс: {total_income - total_expenses:.2f}\n")
    messagebox.showinfo("Готово", "Квитанція збережена")

# --- ІНТЕРФЕЙС ---
init_db()
root = tk.Tk()
root.title("Облік ремонту мобільних телефонів")

tab_control = ttk.Notebook(root)
tab1, tab2, tab3, tab4 = ttk.Frame(tab_control), ttk.Frame(tab_control), ttk.Frame(tab_control), ttk.Frame(tab_control)
tab_control.add(tab1, text='Клієнти')
tab_control.add(tab2, text='Запчастини')
tab_control.add(tab3, text='Ремонти')
tab_control.add(tab4, text='Статистика')
tab_control.pack(expand=1, fill='both')

# --- ВКЛАДКА КЛІЄНТІВ ---
tree = ttk.Treeview(tab1, columns=('ID','Name','Phone','Brand','Model','IMEI','Defect','Cost','Date','Master'), show='headings')
for col in tree['columns']:
    tree.heading(col, text=col)
tree.pack(fill='both', expand=True)
ttk.Button(tab1, text='Обновити', command=refresh_customers).pack()

frame_add_customer = ttk.Frame(tab1)
frame_add_customer.pack(pady=10)
fields = ['Ім\'я','Телефон','Марка','Модель','IMEI','Заявлена несправність','Вартість ремонту','Орієнтовна дата']
entries = []
for i, label in enumerate(fields):
    ttk.Label(frame_add_customer, text=label).grid(row=i, column=0)
    entry = ttk.Entry(frame_add_customer)
    entry.grid(row=i, column=1)
    entries.append(entry)
entry_name, entry_phone, entry_brand, entry_model, entry_imei, entry_defect, entry_repair_cost, entry_date = entries

ttk.Label(frame_add_customer, text='Майстер').grid(row=8, column=0)
combo_master = ttk.Combobox(frame_add_customer)
combo_master.grid(row=8, column=1)

ttk.Button(frame_add_customer, text='Додати клієнта', command=add_customer).grid(row=9, column=0, columnspan=2)

# --- МАЙСТРИ ---
ttk.Label(tab1, text='Додати майстра').pack(pady=5)
frame_master = ttk.Frame(tab1)
frame_master.pack()
entry_master = ttk.Entry(frame_master)
entry_master.pack(side=tk.LEFT)
ttk.Button(frame_master, text='Додати майстра', command=add_master).pack(side=tk.LEFT)

# --- ВКЛАДКА ЗАПЧАСТИН ---
tree_spare = ttk.Treeview(tab2, columns=('ID','Name','Qty','Price'), show='headings')
for col in ('ID','Name','Qty','Price'):
    tree_spare.heading(col, text=col)
tree_spare.pack(fill='both', expand=True)
ttk.Button(tab2, text='Обновити', command=refresh_spare_parts).pack()

frame_spare = ttk.Frame(tab2)
frame_spare.pack(pady=10)
ttk.Label(frame_spare, text='Назва').grid(row=0, column=0)
entry_spare_name = ttk.Entry(frame_spare)
entry_spare_name.grid(row=0, column=1)

ttk.Label(frame_spare, text='Кількість').grid(row=1, column=0)
entry_spare_qty = ttk.Entry(frame_spare)
entry_spare_qty.grid(row=1, column=1)

ttk.Label(frame_spare, text='Ціна за шт').grid(row=2, column=0)
entry_spare_price = ttk.Entry(frame_spare)
entry_spare_price.grid(row=2, column=1)

ttk.Button(frame_spare, text='Додати запчастину', command=add_spare_part).grid(row=3, column=0, columnspan=2)

... # --- ВКЛАДКА РЕМОНТІВ ---
... tree_customers = tree  # використовуємо ту ж таблицю
... tree_repairs = ttk.Treeview(tab3, columns=('ID','Клієнт','Дата','Вартість','Запчастина','Кількість'), show='headings')
... for col in tree_repairs['columns']:
...     tree_repairs.heading(col, text=col)
... tree_repairs.pack(fill='both', expand=True)
... 
... ttk.Button(tab3, text='Обновити ремонти', command=refresh_repairs).pack(pady=5)
... 
... frame_repair = ttk.Frame(tab3)
... frame_repair.pack(pady=10)
... ttk.Label(frame_repair, text='Запчастина').grid(row=0, column=0)
... combo_spare = ttk.Combobox(frame_repair)
... combo_spare.grid(row=0, column=1)
... 
... ttk.Label(frame_repair, text='Кількість').grid(row=1, column=0)
... entry_spare_qty_repair = ttk.Entry(frame_repair)
... entry_spare_qty_repair.grid(row=1, column=1)
... 
... ttk.Button(frame_repair, text='Зареєструвати ремонт', command=register_repair).grid(row=2, column=0, columnspan=2)
... ttk.Button(tab3, text='Друкувати квитанцію', command=print_receipt).pack(pady=5)
... 
... # --- НАВАНТАЖЕННЯ ДАНИХ ---
... def load_data():
...     refresh_customers()
...     refresh_spare_parts()
...     refresh_masters()
...     update_comboboxes()
... 
... def update_comboboxes():
...     cursor.execute('SELECT name FROM SpareParts')
...     combo_spare['values'] = [r[0] for r in cursor.fetchall()]
...     refresh_masters()
... 
... load_data()
... root.mainloop()
... conn.close()
