import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import random
import hashlib

# Пути к файлам для хранения данных
USERS_FILE = 'users.txt'
PRODUCTS_FILE = 'products.txt'
ORDERS_FILE = 'orders_all.txt'

# Глобальные переменные
users = {}
products = []
orders = []

# =========================== Загрузка данных ==============================
def load_users():
    global users
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        phone, pwd_hash = line.split(',', 1)
                        users[phone] = pwd_hash
        except Exception as e:
            print(f"Ошибка при загрузке пользователей: {e}")

def save_users():
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            for phone, pwd_hash in users.items():
                f.write(f"{phone},{pwd_hash}\n")
    except Exception as e:
        print(f"Ошибка при сохранении пользователей: {e}")

def load_products():
    global products
    products = []
    if os.path.exists(PRODUCTS_FILE):
        try:
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 6:
                            photo_path, name, description, article, price_str, _=parts
                            try:
                                price = float(price_str)
                                products.append({
                                    'photo_path': photo_path,
                                    'name': name,
                                    'description': description,
                                    'article': article,
                                    'price': price
                                })
                            except:
                                continue
        except Exception as e:
            print(f"Ошибка при загрузке продуктов: {e}")

def save_product(product):
    try:
        with open(PRODUCTS_FILE, 'a', encoding='utf-8') as f:
            line = f"{product['photo_path']}|{product['name']}|{product['description']}|{product['article']}|{product['price']}|dummy\n"
            f.write(line)
    except Exception as e:
        print(f"Ошибка при сохранении продукта: {e}")

def load_orders():
    global orders
    orders = []
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line=line.strip()
                    if line:
                        parts=line.split('|')
                        if len(parts)==5:
                            code,satus,name,qty_str,total_str=parts
                            try:
                                qty=int(qty_str)
                                total=float(total_str)
                                orders.append({
                                    'code':code,
                                    'status':satus,
                                    'name':name,
                                    'quantity':qty,
                                    'total':total
                                })
                            except:
                                continue
        except Exception as e:
            print(f"Ошибка при загрузке заказов: {e}")

def save_orders():
    try:
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            for order in orders:
                line=f"{order['code']}|{order['status']}|{order['name']}|{order['quantity']}|{order['total']}"
                f.write(line+'\n')
    except Exception as e:
        print(f"Ошибка при сохранении заказов: {e}")

# ======================= Хеширование паролей ================================
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(pwd, hash_value):
    return hash_password(pwd)==hash_value

# =================== Основные функции аутентификации =========================
def register_user(phone, password):
    global users
    if phone in users:
        return False
    users[phone] = hash_password(password)
    save_users()
    return True

def authenticate_user(phone, password):
    if phone in users:
        return verify_password(password, users[phone])
    return False

# =================== Главное окно и интерфейс ================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Магазин с заказами")
        self.root.geometry("800x600")
        self.current_user = None
        self.is_admin = False
        load_users()
        load_products()
        load_orders()
        self.create_main_ui()

    def create_main_ui(self):
        # Создаем фрейм для входа / регистрации
        self.frame_login = ttk.Frame(self.root)
        self.frame_login.pack(fill='both', expand=True)

        ttk.Label(self.frame_login, text="Добро пожаловать! Войдите или Зарегистрируйтесь", font=("Arial",14)).pack(pady=10)

        self.login_phone_var = tk.StringVar()
        self.login_pwd_var = tk.StringVar()

        ttk.Label(self.frame_login, text="Телефон:").pack(pady=5)
        self.entry_login_phone = ttk.Entry(self.frame_login, textvariable=self.login_phone_var)
        self.entry_login_phone.pack(pady=5)

        ttk.Label(self.frame_login, text="Пароль:").pack(pady=5)
        self.entry_login_pwd = ttk.Entry(self.frame_login, textvariable=self.login_pwd_var, show='*')
        self.entry_login_pwd.pack(pady=5)

        ttk.Button(self.frame_login, text="Войти", command=self.login).pack(pady=10)
        ttk.Button(self.frame_login, text="Регистрация", command=self.show_registration).pack()

        # Для регистрации
        self.frame_register = ttk.Frame(self.root)

        ttk.Label(self.frame_register, text="Регистрация", font=("Arial",14)).pack(pady=10)

        self.reg_phone_var = tk.StringVar()
        self.reg_pwd_var = tk.StringVar()

        ttk.Label(self.frame_register, text="Телефон:").pack(pady=5)
        ttk.Entry(self.frame_register, textvariable=self.reg_phone_var).pack(pady=5)

        ttk.Label(self.frame_register, text="Пароль:").pack(pady=5)
        ttk.Entry(self.frame_register, textvariable=self.reg_pwd_var, show='*').pack(pady=5)

        ttk.Button(self.frame_register, text="Зарегистрироваться", command=self.register).pack(pady=10)
        ttk.Button(self.frame_register, text="Назад", command=self.show_login).pack()

    def show_registration(self):
        self.frame_login.pack_forget()
        self.frame_register.pack(fill='both', expand=True)

    def show_login(self):
        self.frame_register.pack_forget()
        self.frame_login.pack(fill='both', expand=True)

    def login(self):
        phone = self.login_phone_var.get().strip()
        pwd = self.login_pwd_var.get().strip()
        if authenticate_user(phone, pwd):
            self.current_user = phone
            self.is_admin = (phone == "+79270482888")
            messagebox.showinfo("Успех", "Вы успешно вошли!")
            self.open_user_dashboard()
        else:
            messagebox.showerror("Ошибка", "Неверный номер или пароль!")

    def register(self):
        phone = self.reg_phone_var.get().strip()
        pwd = self.reg_pwd_var.get().strip()
        if not phone or not pwd:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        if register_user(phone, pwd):
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.show_login()
        else:
            messagebox.showerror("Ошибка", "Пользователь с этим номером уже зарегистрирован!")

    def open_user_dashboard(self):
        self.frame_login.pack_forget()
        self.root.update()
        self.dashboard = ttk.Frame(self.root)
        self.dashboard.pack(fill='both', expand=True)
        welcome_text = f"Добро пожаловать, {self.current_user}"
        ttk.Label(self.dashboard, text=welcome_text, font=("Arial",14)).pack(pady=10)
        if self.is_admin:
            self.create_admin_panel()
        else:
            self.create_employee_panel()

        ttk.Button(self.dashboard, text="Выход", command=self.logout).pack(pady=10)

    def logout(self):
        self.dashboard.destroy()
        self.current_user = None
        self.is_admin = False
        self.create_main_ui()

    # ======================= Панель администратора ============================
    def create_admin_panel(self):
        frame_admin = ttk.Frame(self.dashboard)
        frame_admin.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая часть: управление товарами
        frame_left = ttk.Frame(frame_admin)
        frame_left.pack(side='left', fill='y', expand=True, padx=5)

        ttk.Label(frame_left, text="Управление товарами", font=("Arial",12)).pack(pady=5)
        ttk.Button(frame_left, text="Добавить товар", command=self.open_add_product_window).pack(pady=5)
        ttk.Button(frame_left, text="Просмотр товаров", command=self.show_products_list).pack(pady=5)

        # Правая часть: заказы и создание заказа
        frame_right = ttk.Frame(frame_admin)
        frame_right.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        ttk.Label(frame_right, text="Заказы", font=("Arial",12)).pack(pady=5)

        ttk.Button(frame_right, text="Обзор всех заказов", command=self.show_all_orders).pack(pady=5)

        # Кнопки для создания тестовых заказов и нового заказа вручную
        ttk.Button(frame_right, text="Создать тестовый заказ", command=self.create_test_order).pack(pady=5)
        ttk.Button(frame_right, text="Создать заказ вручную", command=self.create_manual_order).pack(pady=5)

        # Поле поиска по заказам
        search_frame = ttk.Frame(frame_right)
        search_frame.pack(pady=10)
        self.order_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.order_search_var, width=30).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_orders).pack(side='left')

        # Область для отображения списка товаров
        self.product_listbox = tk.Listbox(frame_left, height=15)
        self.load_products_in_listbox()
        self.product_listbox.pack(pady=5, fill='both', expand=True)

    def load_products_in_listbox(self):
        self.product_listbox.delete(0,'end')
        for prod in products:
            self.product_listbox.insert('end', prod['name'])

    def open_add_product_window(self):
        win = tk.Toplevel(self.root)
        win.title("Добавить товар")
        win.geometry("500x600")

        photo_path_var = tk.StringVar()
        name_var = tk.StringVar()
        desc_var = tk.StringVar()
        article_var = tk.StringVar()
        price_var = tk.StringVar()

        def select_image():
            path = filedialog.askopenfilename(title="Выберите изображение", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
            if path:
                photo_path_var.set(path)

        ttk.Label(win, text="Фото:").pack(pady=5)
        ttk.Button(win, text="Выбрать изображение", command=select_image).pack()
        ttk.Label(win, textvariable=photo_path_var).pack(pady=2)

        ttk.Label(win, text="Название:").pack(pady=5)
        ttk.Entry(win, textvariable=name_var).pack()

        ttk.Label(win, text="Описание:").pack(pady=5)
        ttk.Entry(win, textvariable=desc_var).pack()

        ttk.Label(win, text="Артикул:").pack(pady=5)
        ttk.Entry(win, textvariable=article_var).pack()

        ttk.Label(win, text="Цена:").pack(pady=5)
        ttk.Entry(win, textvariable=price_var).pack()

        def save_product_data():
            path = photo_path_var.get()
            name = name_var.get()
            desc = desc_var.get()
            article = article_var.get()
            try:
                price = float(price_var.get())
            except:
                messagebox.showerror("Ошибка", "Некорректная цена")
                return
            if not all([path, name, desc, article]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            new_product = {
                'photo_path': path,
                'name': name,
                'description': desc,
                'article': article,
                'price': price
            }
            save_product(new_product)
            load_products()
            self.load_products_in_listbox()
            messagebox.showinfo("Успех", "Товар добавлен успешно")
            win.destroy()

        ttk.Button(win, text="Добавить товар", command=save_product_data).pack(pady=10)

    def show_products_list(self):
        win = tk.Toplevel(self.root)
        win.title("Список товаров")
        win.geometry("700x500")
        tree = ttk.Treeview(win, columns=("Фото", "Название", "Описание", "Артикул", "Цена"), show='headings')
        tree.pack(fill='both', expand=True)

        for col in ("Фото", "Название", "Описание", "Артикул", "Цена"):
            tree.heading(col, text=col)
            if col=='Фото':
                tree.column(col, width=100)
            elif col=='Цена':
                tree.column(col, width=80)
            else:
                tree.column(col, width=150)

        for idx, prod in enumerate(products):
            tree.insert('', 'end', values=( "Фото", prod['name'], prod['description'], prod['article'], f"{prod['price']:.2f}"))

        def show_detail(event):
            item_id = tree.focus()
            if not item_id:
                return
            index = tree.index(item_id)
            prod = products[index]
            detail_win = tk.Toplevel(win)
            detail_win.title(f"Детали товара: {prod['name']}")
            try:
                img = Image.open(prod['photo_path'])
                img.thumbnail((250,250))
                photo_img = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(detail_win, image=photo_img)
                lbl_img.image = photo_img
                lbl_img.pack()
            except:
                tk.Label(detail_win, text="Изображение недоступно").pack()
            tk.Label(detail_win, text=f"Название: {prod['name']}").pack()
            tk.Label(detail_win, text=f"Описание: {prod['description']}").pack()
            tk.Label(detail_win, text=f"Артикул: {prod['article']}").pack()
            tk.Label(detail_win, text=f"Цена: {prod['price']:.2f}").pack()

        tree.bind('<Double-1>', show_detail)

    def show_all_orders(self):
        win = tk.Toplevel(self.root)
        win.title("Все заказы")
        win.geometry("800x600")
        columns=('Код заказа', 'Статус', 'Содержимое', 'Общая сумма')
        tree = ttk.Treeview(win, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            if col=='Общая сумма':
                tree.column(col, width=100)
            else:
                tree.column(col, width=200)
        tree.pack(fill='both', expand=True)

        # Собираем и показываем заказы
        for order in orders:
            content_str = ''
            sum_order=0
            for item in orders:
                if item['code']==order['code']:
                    content_str+=f"{item['name']} x{item['quantity']}, "
                    sum_order+=item['total']
            if content_str.endswith(', '):
                content_str=content_str[:-2]
            tree.insert('', 'end', values=(order['code'], order['status'], content_str, f"{sum_order:.2f}"))

        def show_order_detail(event):
            selected_item = tree.focus()
            if not selected_item:
                return
            values = tree.item(selected_item, 'values')
            code = values[0]
            detail_win = tk.Toplevel(win)
            detail_win.title(f"Заказ {code}")
            tk.Label(detail_win, text=f"Код заказа: {code}", font=("Arial",12)).pack(pady=5)
            content_lines=[]
            total_sum=0
            for item in orders:
                if item['code']==code:
                    content_lines.append(f"{item['name']} x{item['quantity']}")
                    total_sum+=item['total']
            tk.Label(detail_win, text="Содержимое заказа:").pack(pady=5)
            for line in content_lines:
                tk.Label(detail_win, text=line).pack()
            tk.Label(detail_win, text=f"Общая сумма: {total_sum:.2f}").pack(pady=5)

        tree.bind('<Double-1>', show_order_detail)
        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

    def create_test_order(self):
        # Генерируем тестовый заказ
        if not products:
            messagebox.showwarning("Предупреждение", "Нет товаров для создания заказа")
            return
        order_code = f"{random.randint(1000,9999)}"
        selected_product = random.choice(products)
        quantity = random.randint(1,3)
        total = selected_product['price']*quantity
        new_order = {
            'code': order_code,
            'status': 'Обрабатывается',
            'name': selected_product['name'],
            'quantity': quantity,
            'total': total
        }
        orders.append(new_order)
        save_orders()
        messagebox.showinfo("Готово", f"Создан тестовый заказ {order_code}")

    def create_manual_order(self):
        # Создаем окно для ручного добавления заказа
        win = tk.Toplevel(self.root)
        win.title("Создать заказ вручную")
        win.geometry("600x600")

        selected_products = []

        def add_product():
            idx = listbox.curselection()
            if idx:
                for i in idx:
                    selected_products.append(products[i])
                update_order()

        def remove_selected():
            idxs = listbox.curselection()
            for i in reversed(idxs):
                del selected_products[i]
            update_order()

        def update_order():
            txt_order.delete('1.0', tk.END)
            total=0
            for p in selected_products:
                txt_order.insert(tk.END, f"{p['name']} - {p['price']:.2f}\n")
                total+=p['price']
            lbl_total.config(text=f"Общая сумма: {total:.2f}")

        def confirm_order():
            if not selected_products:
                messagebox.showwarning("Предупреждение", "Нет выбранных товаров")
                return
            code = f"{random.randint(10000,99999)}"
            total_order=0
            for p in selected_products:
                total_order+=p['price']
            for p in selected_products:
                order_entry={
                    'code':code,
                    'status':'Обрабатывается',
                    'name':p['name'],
                    'quantity':1,
                    'total':p['price']
                }
                orders.append(order_entry)
            save_orders()
            messagebox.showinfo("Успех", f"Заказ {code} успешно создан")
            win.destroy()

        ttk.Label(win, text="Выберите товары для заказа:").pack(pady=5)
        listbox = tk.Listbox(win, selectmode='multiple')
        listbox.pack(pady=5, fill='both', expand=True)

        for p in products:
            listbox.insert('end', p['name'])

        ttk.Button(win, text="Добавить выбранное", command=add_product).pack(pady=5)
        ttk.Button(win, text="Удалить выбранное", command=remove_selected).pack(pady=5)

        ttk.Label(win, text="Выбранные товары:").pack(pady=5)
        txt_order = scrolledtext.ScrolledText(win, height=8)
        txt_order.pack(pady=5, fill='both', expand=True)

        lbl_total = ttk.Label(win, text="Общая сумма: 0.00")
        lbl_total.pack(pady=5)

        ttk.Button(win, text="Подтвердить заказ", command=confirm_order).pack(pady=10)

    def search_orders(self):
        query = self.order_search_var.get().strip()
        if not query:
            messagebox.showinfo("Поиск", "Введите номер заказа для поиска")
            return
        # Показываем заказы с этим кодом
        result_orders = [o for o in orders if o['code'] == query]
        if not result_orders:
            messagebox.showinfo("Поиск", "Заказы не найдены")
            return
        # Открываем окно с результатами
        win = tk.Toplevel(self.root)
        win.title("Результаты поиска")
        win.geometry("800x600")
        columns=('Код заказа', 'Статус', 'Содержимое', 'Общая сумма')
        tree = ttk.Treeview(win, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            if col=='Общая сумма':
                tree.column(col, width=100)
            else:
                tree.column(col, width=200)
        tree.pack(fill='both', expand=True)
        for order in result_orders:
            content_str = ''
            sum_order=0
            for item in orders:
                if item['code']==order['code']:
                    content_str+=f"{item['name']} x{item['quantity']}, "
                    sum_order+=item['total']
            if content_str.endswith(', '):
                content_str=content_str[:-2]
            tree.insert('', 'end', values=(order['code'], order['status'], content_str, f"{sum_order:.2f}"))
        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

    # ======================= Панель сотрудника ============================
    def create_employee_panel(self):
        frame_emp = ttk.Frame(self.dashboard)
        frame_emp.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame_emp, text="Панель работника", font=("Arial", 14)).pack(pady=10)

        # Поле поиска по заказам
        search_frame = ttk.Frame(frame_emp)
        search_frame.pack(pady=10)

        self.employee_order_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.employee_order_search_var, width=30).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Найти заказ", command=self.search_employee_orders).pack(side='left', padx=5)

        # Кнопка "Заказы"
        ttk.Button(frame_emp, text="Все заказы", command=self.show_employee_orders).pack(pady=10)

    def search_employee_orders(self):
        query = self.employee_order_search_var.get().strip()
        if not query:
            messagebox.showinfo("Поиск", "Введите номер заказа для поиска")
            return
        result_orders = [o for o in orders if o['code'] == query]
        if not result_orders:
            messagebox.showinfo("Поиск", "Заказы не найдены")
            return
        self.show_orders_table(result_orders)

    def show_employee_orders(self):
        self.show_orders_table(orders)

    def show_orders_table(self, orders_list):
        win = tk.Toplevel(self.root)
        win.title("Список заказов")
        win.geometry("800x600")
        columns = ('Код заказа', 'Статус', 'Содержимое', 'Общая сумма')
        tree = ttk.Treeview(win, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            if col == 'Общая сумма':
                tree.column(col, width=100)
            else:
                tree.column(col, width=200)
        tree.pack(fill='both', expand=True)

        for order in orders_list:
            content_str = ''
            total_sum = 0
            for item in orders:
                if item['code'] == order['code']:
                    content_str += f"{item['name']} x{item['quantity']}, "
                    total_sum += item['total']
            if content_str.endswith(', '):
                content_str = content_str[:-2]
            tree.insert('', 'end', values=(order['code'], order['status'], content_str, f"{total_sum:.2f}"))

        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

    def create_new_order(self):
        win = tk.Toplevel(self.root)
        win.title("Создать заказ")
        win.geometry("600x400")

        sel_products = []

        def add_product_to_order():
            selected_indices = listbox.curselection()
            for idx in selected_indices:
                sel_products.append(products[idx])
            update_order()

        def remove_selected():
            selected_indices = listbox.curselection()
            for idx in reversed(selected_indices):
                del sel_products[idx]
            update_order()

        def update_order():
            txt_order.delete('1.0', tk.END)
            total=0
            for p in sel_products:
                txt_order.insert(tk.END, f"{p['name']} - {p['price']:.2f}\n")
                total+=p['price']
            lbl_total.config(text=f"Общая сумма: {total:.2f}")

        ttk.Label(win, text="Выберите товары для заказа:").pack(pady=5)
        listbox = tk.Listbox(win, selectmode='multiple')
        listbox.pack(pady=5, fill='both', expand=True)

        for p in products:
            listbox.insert('end', p['name'])

        ttk.Button(win, text="Добавить выбранные", command=add_product_to_order).pack(pady=5)
        ttk.Button(win, text="Удалить выбранное", command=remove_selected).pack(pady=5)

        ttk.Label(win, text="Выбранные товары:").pack(pady=5)
        txt_order = scrolledtext.ScrolledText(win, height=8)
        txt_order.pack(pady=5, fill='both', expand=True)

        lbl_total = ttk.Label(win, text="Общая сумма: 0.00")
        lbl_total.pack(pady=5)

        def confirm_order():
            if not sel_products:
                messagebox.showwarning("Предупреждение", "Нет товаров для заказа")
                return
            code = f"{random.randint(10000,99999)}"
            total_sum=0
            for p in sel_products:
                total_sum+=p['price']
            for p in sel_products:
                order_entry={
                    'code':code,
                    'status':'Обрабатывается',
                    'name':p['name'],
                    'quantity':1,
                    'total':p['price']
                }
                orders.append(order_entry)
            save_orders()
            messagebox.showinfo("Успех", f"Заказ {code} создан успешно")
            win.destroy()

        ttk.Button(win, text="Подтвердить заказ", command=confirm_order).pack(pady=10)

# ======================= Запуск приложения ================================
if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
