import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
import os


class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет склада - Нипи ПЕГАЗ")
        self.root.geometry("1200x800")  # Увеличенный размер окна
        self.root.minsize(1000, 600)  # Минимальный размер окна

        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка склада
        self.warehouse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.warehouse_frame, text='Склад')

        # Вкладка журнала
        self.journal_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.journal_frame, text='Журнал выдачи')

        # Инициализация компонентов
        self.init_warehouse_tab()
        self.init_journal_tab()

        # Загрузка данных
        self.load_data()

    def init_warehouse_tab(self):
        # Фрейм для элементов управления
        control_frame = ttk.LabelFrame(self.warehouse_frame, text="Управление складом")
        control_frame.pack(fill='x', padx=10, pady=10, ipady=5)

        # Кнопки управления
        ttk.Button(control_frame, text="Добавить товар", command=self.add_item_dialog).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Сохранить в файл", command=self.save_data).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Загрузить из файла", command=self.load_data).pack(side='left', padx=5)

        # Создание таблицы склада
        columns = ("id", "article", "name", "balance", "last_update")
        self.warehouse_tree = ttk.Treeview(
            self.warehouse_frame,
            columns=columns,
            show='headings',
            height=20,
            selectmode='browse'
        )

        # Настройка столбцов
        self.warehouse_tree.heading("id", text="Номер позиции")
        self.warehouse_tree.heading("article", text="Артикул товара")
        self.warehouse_tree.heading("name", text="Наименование")
        self.warehouse_tree.heading("balance", text="Остаток на складе")
        self.warehouse_tree.heading("last_update", text="Последняя дата обновления")

        # Ширины столбцов
        self.warehouse_tree.column("id", width=100, anchor='center')
        self.warehouse_tree.column("article", width=150, anchor='center')
        self.warehouse_tree.column("name", width=300, anchor='w')
        self.warehouse_tree.column("balance", width=120, anchor='center')
        self.warehouse_tree.column("last_update", width=180, anchor='center')

        # Добавление скроллбаров
        scrollbar_y = ttk.Scrollbar(self.warehouse_frame, orient="vertical", command=self.warehouse_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.warehouse_frame, orient="horizontal", command=self.warehouse_tree.xview)
        self.warehouse_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Размещение элементов с использованием pack
        self.warehouse_tree.pack(side='top', fill='both', expand=True, padx=10, pady=(0, 5))
        scrollbar_x.pack(side='bottom', fill='x', padx=10)
        scrollbar_y.pack(side='right', fill='y', padx=(0, 10))

        # Фрейм для кнопок действий
        action_frame = ttk.Frame(self.warehouse_frame)
        action_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(action_frame, text="Редактировать товар",
                   command=self.edit_warehouse_item).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Выдать товар",
                   command=self.issue_selected_item).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Удалить товар",
                   command=self.delete_warehouse_item).pack(side='left', padx=5)

    def init_journal_tab(self):
        # Фрейм для элементов управления журналом
        control_frame = ttk.LabelFrame(self.journal_frame, text="Управление журналом")
        control_frame.pack(fill='x', padx=10, pady=10, ipady=5)

        # Кнопки управления
        ttk.Button(control_frame, text="Обновить журнал", command=self.load_journal).pack(side='left', padx=5)

        # Создание таблицы журнала
        columns = ("id", "article", "name", "fio", "department", "quantity", "date")
        self.journal_tree = ttk.Treeview(
            self.journal_frame,
            columns=columns,
            show='headings',
            height=20
        )

        # Настройка столбцов
        self.journal_tree.heading("id", text="ID позиции")
        self.journal_tree.heading("article", text="Артикул")
        self.journal_tree.heading("name", text="Наименование")
        self.journal_tree.heading("fio", text="ФИО получателя")
        self.journal_tree.heading("department", text="Отдел")
        self.journal_tree.heading("quantity", text="Количество")
        self.journal_tree.heading("date", text="Дата выдачи")

        # Ширины столбцов
        self.journal_tree.column("id", width=80, anchor='center')
        self.journal_tree.column("article", width=100, anchor='center')
        self.journal_tree.column("name", width=200, anchor='w')
        self.journal_tree.column("fio", width=150, anchor='w')
        self.journal_tree.column("department", width=120, anchor='w')
        self.journal_tree.column("quantity", width=80, anchor='center')
        self.journal_tree.column("date", width=120, anchor='center')

        # Добавление скроллбаров
        scrollbar_y = ttk.Scrollbar(self.journal_frame, orient="vertical", command=self.journal_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.journal_frame, orient="horizontal", command=self.journal_tree.xview)
        self.journal_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Размещение элементов с использованием pack
        self.journal_tree.pack(side='top', fill='both', expand=True, padx=10, pady=(0, 5))
        scrollbar_x.pack(side='bottom', fill='x', padx=10)
        scrollbar_y.pack(side='right', fill='y', padx=(0, 10))

        # Фрейм для кнопок действий
        action_frame = ttk.Frame(self.journal_frame)
        action_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(action_frame, text="Редактировать запись",
                   command=self.edit_journal_entry).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Удалить запись",
                   command=self.delete_journal_entry).pack(side='left', padx=5)

    def load_data(self):
        # Загрузка данных склада
        try:
            self.warehouse_tree.delete(*self.warehouse_tree.get_children())

            if not os.path.exists('warehouse.csv'):
                with open('warehouse.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'id', 'article', 'name', 'balance', 'last_update'
                    ])
                    writer.writeheader()

            with open('warehouse.csv', 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.warehouse_tree.insert('', 'end', values=(
                        row['id'],
                        row['article'],
                        row['name'],
                        row['balance'],
                        row['last_update']
                    ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных склада: {str(e)}")

        # Загрузка журнала выдачи
        self.load_journal()

    def load_journal(self):
        try:
            self.journal_tree.delete(*self.journal_tree.get_children())

            if not os.path.exists('journal.csv'):
                with open('journal.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'id', 'article', 'name', 'fio', 'department', 'quantity', 'date'
                    ])
                    writer.writeheader()

            with open('journal.csv', 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.journal_tree.insert('', 'end', values=(
                        row['id'],
                        row['article'],
                        row['name'],
                        row['fio'],
                        row['department'],
                        row['quantity'],
                        row['date']
                    ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки журнала: {str(e)}")

    def save_data(self):
        try:
            # Сохраняем склад
            with open('warehouse.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'article', 'name', 'balance', 'last_update'
                ])
                writer.writeheader()

                for item in self.warehouse_tree.get_children():
                    values = self.warehouse_tree.item(item)['values']
                    writer.writerow({
                        'id': values[0],
                        'article': values[1],
                        'name': values[2],
                        'balance': values[3],
                        'last_update': values[4]
                    })

            # Сохраняем журнал
            with open('journal.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'article', 'name', 'fio', 'department', 'quantity', 'date'
                ])
                writer.writeheader()

                for item in self.journal_tree.get_children():
                    values = self.journal_tree.item(item)['values']
                    writer.writerow({
                        'id': values[0],
                        'article': values[1],
                        'name': values[2],
                        'fio': values[3],
                        'department': values[4],
                        'quantity': values[5],
                        'date': values[6]
                    })

            messagebox.showinfo("Успех", "Данные успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения данных: {str(e)}")

    def add_item_dialog(self):
        self.add_dialog = tk.Toplevel(self.root)
        self.add_dialog.title("Добавление товара")
        self.add_dialog.geometry("500x350")
        self.add_dialog.transient(self.root)
        self.add_dialog.grab_set()

        # Основной фрейм
        main_frame = ttk.Frame(self.add_dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Поля формы
        ttk.Label(main_frame, text="Номер позиции:").grid(row=0, column=0, sticky='w', pady=5)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(main_frame, text="Артикул товара:").grid(row=1, column=0, sticky='w', pady=5)
        self.article_entry = ttk.Entry(main_frame, width=40)
        self.article_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(main_frame, text="Наименование:").grid(row=2, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(main_frame, text="Количество на складе:").grid(row=3, column=0, sticky='w', pady=5)
        self.balance_entry = ttk.Entry(main_frame, width=40)
        self.balance_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        self.balance_entry.insert(0, "0")

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Добавить", command=self.add_item).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.add_dialog.destroy).pack(side='right', padx=10)

        # Настройка весов столбцов
        main_frame.columnconfigure(1, weight=1)

    def add_item(self):
        # Получаем значения
        item_id = self.id_entry.get().strip()
        article = self.article_entry.get().strip()
        name = self.name_entry.get().strip()
        balance = self.balance_entry.get().strip()

        # Проверка данных
        if not all([item_id, article, name, balance]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return

        try:
            balance = int(balance)
            if balance < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return

        # Проверка уникальности ID
        for item in self.warehouse_tree.get_children():
            if self.warehouse_tree.item(item)['values'][0] == item_id:
                messagebox.showerror("Ошибка", "Товар с таким номером уже существует")
                return

        # Добавляем в таблицу
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.warehouse_tree.insert('', 'end', values=(
            item_id,
            article,
            name,
            balance,
            current_date
        ))

        self.add_dialog.destroy()
        messagebox.showinfo("Успех", "Товар успешно добавлен на склад")

    def edit_warehouse_item(self):
        # Получаем выделенный элемент
        selected = self.warehouse_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для редактирования")
            return

        item_id = selected[0]
        values = self.warehouse_tree.item(item_id)['values']

        self.edit_dialog = tk.Toplevel(self.root)
        self.edit_dialog.title("Редактирование товара")
        self.edit_dialog.geometry("500x350")
        self.edit_dialog.transient(self.root)
        self.edit_dialog.grab_set()

        # Основной фрейм
        main_frame = ttk.Frame(self.edit_dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Поля формы
        ttk.Label(main_frame, text="Номер позиции:").grid(row=0, column=0, sticky='w', pady=5)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.id_entry.insert(0, values[0])
        self.id_entry.config(state='readonly')

        ttk.Label(main_frame, text="Артикул товара:").grid(row=1, column=0, sticky='w', pady=5)
        self.article_entry = ttk.Entry(main_frame, width=40)
        self.article_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.article_entry.insert(0, values[1])

        ttk.Label(main_frame, text="Наименование:").grid(row=2, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        self.name_entry.insert(0, values[2])

        ttk.Label(main_frame, text="Количество на складе:").grid(row=3, column=0, sticky='w', pady=5)
        self.balance_entry = ttk.Entry(main_frame, width=40)
        self.balance_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        self.balance_entry.insert(0, values[3])

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Сохранить",
                   command=lambda: self.update_item(item_id)).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена",
                   command=self.edit_dialog.destroy).pack(side='right', padx=10)

        # Настройка весов столбцов
        main_frame.columnconfigure(1, weight=1)

    def update_item(self, item_id):
        # Получаем значения
        article = self.article_entry.get().strip()
        name = self.name_entry.get().strip()
        balance = self.balance_entry.get().strip()

        # Проверка данных
        if not all([article, name, balance]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return

        try:
            balance = int(balance)
            if balance < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return

        # Обновляем данные
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_id = self.id_entry.get()

        # Обновляем запись в таблице
        self.warehouse_tree.item(item_id, values=(
            current_id,
            article,
            name,
            balance,
            current_date
        ))

        self.edit_dialog.destroy()
        messagebox.showinfo("Успех", "Товар успешно обновлен")

    def issue_selected_item(self):
        # Получаем выделенный элемент
        selected = self.warehouse_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для выдачи")
            return

        item_id = selected[0]
        self.issue_item(item_id)

    def issue_item(self, item_id):
        # Получаем данные о товаре
        values = self.warehouse_tree.item(item_id)['values']
        if not values:
            return

        self.selected_item = {
            'id': values[0],
            'article': values[1],
            'name': values[2],
            'balance': int(values[3])
        }

        # Создаем диалоговое окно выдачи
        self.issue_dialog = tk.Toplevel(self.root)
        self.issue_dialog.title("Выдача товара")
        self.issue_dialog.geometry("500x350")
        self.issue_dialog.transient(self.root)
        self.issue_dialog.grab_set()

        # Основной фрейм
        main_frame = ttk.Frame(self.issue_dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Информация о товаре
        ttk.Label(main_frame, text=f"Товар: {self.selected_item['name']}").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Label(main_frame, text=f"Артикул: {self.selected_item['article']}").grid(row=1, column=0, sticky='w',
                                                                                     pady=5)
        ttk.Label(main_frame, text=f"Доступно: {self.selected_item['balance']}").grid(row=2, column=0, sticky='w',
                                                                                      pady=5)

        # Поля формы
        ttk.Label(main_frame, text="ФИО получателя:").grid(row=3, column=0, sticky='w', pady=5)
        self.fio_entry = ttk.Entry(main_frame, width=40)
        self.fio_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(main_frame, text="Отдел:").grid(row=4, column=0, sticky='w', pady=5)
        self.department_entry = ttk.Entry(main_frame, width=40)
        self.department_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(main_frame, text="Количество:").grid(row=5, column=0, sticky='w', pady=5)
        self.quantity_var = tk.StringVar()
        self.quantity_spin = ttk.Spinbox(
            main_frame,
            from_=1,
            to=self.selected_item['balance'],
            textvariable=self.quantity_var,
            width=10
        )
        self.quantity_spin.grid(row=5, column=1, sticky='w', padx=5, pady=5)
        self.quantity_spin.set(1)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Выдать", command=lambda: self.confirm_issue(item_id)).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.issue_dialog.destroy).pack(side='right', padx=10)

        # Настройка весов столбцов
        main_frame.columnconfigure(1, weight=1)

    def confirm_issue(self, item_id):
        # Проверка данных
        fio = self.fio_entry.get().strip()
        department = self.department_entry.get().strip()

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
                return
            if quantity > self.selected_item['balance']:
                messagebox.showerror("Ошибка", "Недостаточно товара на складе")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество")
            return

        if not fio or not department:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return

        # Обновляем склад
        new_balance = self.selected_item['balance'] - quantity
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Обновляем данные в таблице
        values = self.warehouse_tree.item(item_id)['values']
        self.warehouse_tree.item(item_id, values=(
            values[0],
            values[1],
            values[2],
            new_balance,
            current_date
        ))

        # Добавляем запись в журнал
        journal_entry = {
            'id': self.selected_item['id'],
            'article': self.selected_item['article'],
            'name': self.selected_item['name'],
            'fio': fio,
            'department': department,
            'quantity': quantity,
            'date': current_date
        }

        # Добавляем в таблицу журнала
        self.journal_tree.insert('', 'end', values=(
            journal_entry['id'],
            journal_entry['article'],
            journal_entry['name'],
            journal_entry['fio'],
            journal_entry['department'],
            journal_entry['quantity'],
            journal_entry['date']
        ))

        self.issue_dialog.destroy()
        messagebox.showinfo("Успех", "Товар успешно выдан")

    def delete_warehouse_item(self):
        # Получаем выделенный элемент
        selected = self.warehouse_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот товар?"):
            return

        # Удаляем запись
        self.warehouse_tree.delete(selected[0])
        messagebox.showinfo("Успех", "Товар успешно удален")

    def edit_journal_entry(self):
        # Получаем выделенный элемент
        selected = self.journal_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return

        item_id = selected[0]
        values = self.journal_tree.item(item_id)['values']

        self.edit_dialog = tk.Toplevel(self.root)
        self.edit_dialog.title("Редактирование записи журнала")
        self.edit_dialog.geometry("600x400")
        self.edit_dialog.transient(self.root)
        self.edit_dialog.grab_set()

        # Основной фрейм
        main_frame = ttk.Frame(self.edit_dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Поля формы
        ttk.Label(main_frame, text="ID позиции:").grid(row=0, column=0, sticky='w', pady=5)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.id_entry.insert(0, values[0])
        self.id_entry.config(state='readonly')

        ttk.Label(main_frame, text="Артикул:").grid(row=1, column=0, sticky='w', pady=5)
        self.article_entry = ttk.Entry(main_frame, width=40)
        self.article_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.article_entry.insert(0, values[1])
        self.article_entry.config(state='readonly')

        ttk.Label(main_frame, text="Наименование:").grid(row=2, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        self.name_entry.insert(0, values[2])
        self.name_entry.config(state='readonly')

        ttk.Label(main_frame, text="ФИО получателя:").grid(row=3, column=0, sticky='w', pady=5)
        self.fio_entry = ttk.Entry(main_frame, width=40)
        self.fio_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        self.fio_entry.insert(0, values[3])

        ttk.Label(main_frame, text="Отдел:").grid(row=4, column=0, sticky='w', pady=5)
        self.department_entry = ttk.Entry(main_frame, width=40)
        self.department_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        self.department_entry.insert(0, values[4])

        ttk.Label(main_frame, text="Количество:").grid(row=5, column=0, sticky='w', pady=5)
        self.quantity_entry = ttk.Entry(main_frame, width=40)
        self.quantity_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        self.quantity_entry.insert(0, values[5])

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Сохранить",
                   command=lambda: self.update_journal_entry(item_id)).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена",
                   command=self.edit_dialog.destroy).pack(side='right', padx=10)

        # Настройка весов столбцов
        main_frame.columnconfigure(1, weight=1)

    def update_journal_entry(self, item_id):
        # Получаем значения
        fio = self.fio_entry.get().strip()
        department = self.department_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        # Проверка данных
        if not all([fio, department, quantity]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return

        # Обновляем запись
        values = self.journal_tree.item(item_id)['values']
        self.journal_tree.item(item_id, values=(
            values[0],
            values[1],
            values[2],
            fio,
            department,
            quantity,
            values[6]
        ))

        self.edit_dialog.destroy()
        messagebox.showinfo("Успех", "Запись журнала обновлена")

    def delete_journal_entry(self):
        # Получаем выделенный элемент
        selected = self.journal_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            return

        # Удаляем запись
        self.journal_tree.delete(selected[0])
        messagebox.showinfo("Успех", "Запись журнала удалена")


if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()