import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite3 Database Manager - Advanced")
        self.root.geometry("1100x750")
        
        # Переменные
        self.db_name = "my_database.db"
        self.current_table = None
        self.connection = None
        self.joined_tables = []  # Список соединенных таблиц
        self.selected_attributes = []  # Выбранные атрибуты для отображения
        self.table_joins = {}  # Сохраненные соединения для каждой таблицы
        
        self.create_widgets()
        self.connect_to_db()
        
    def connect_to_db(self):
        """Подключение к базе данных"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.update_table_list()
            messagebox.showinfo("Успех", f"Подключено к базе данных: {self.db_name}")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Фрейм для управления базой данных
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Кнопки управления
        ttk.Button(control_frame, text="Создать таблицу", 
                  command=self.create_table_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Добавить запись", 
                  command=self.add_record_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить таблицу", 
                  command=self.delete_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить данные", 
                  command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Соединить таблицы", 
                  command=self.join_tables_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Выбрать атрибуты", 
                  command=self.select_attributes_dialog).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для списка таблиц и данных
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левый фрейм с таблицами и соединениями
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Список таблиц
        table_list_frame = ttk.LabelFrame(left_frame, text="Таблицы", padding="5")
        table_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.table_listbox = tk.Listbox(table_list_frame, width=25, height=12)
        self.table_listbox.pack(fill=tk.BOTH, expand=True)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Информация о соединенных таблицах
        join_info_frame = ttk.LabelFrame(left_frame, text="Активные соединения", padding="5")
        join_info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.join_info_text = tk.Text(join_info_frame, height=8, width=25)
        self.join_info_text.pack(fill=tk.BOTH, expand=True)
        
        join_buttons_frame = ttk.Frame(join_info_frame)
        join_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(join_buttons_frame, text="Очистить соединения", 
                  command=self.clear_joins).pack(side=tk.LEFT, padx=2)
        ttk.Button(join_buttons_frame, text="Удалить соединение", 
                  command=self.remove_join).pack(side=tk.LEFT, padx=2)
        
        # Фрейм для данных таблицы
        data_frame = ttk.LabelFrame(main_frame, text="Данные таблицы", padding="5")
        data_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Панель сортировки и фильтрации
        sort_filter_frame = ttk.Frame(data_frame)
        sort_filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Сортировка
        sort_frame = ttk.LabelFrame(sort_filter_frame, text="Сортировка", padding="5")
        sort_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(sort_frame, text="Атрибут:").pack(side=tk.LEFT)
        self.sort_column = ttk.Combobox(sort_frame, state="readonly", width=15)
        self.sort_column.pack(side=tk.LEFT, padx=5)
        
        # Заменяем ASC/DESC на русские названия
        self.sort_order = ttk.Combobox(sort_frame, 
                                      values=["По возрастанию", "По убыванию"], 
                                      state="readonly", width=15)
        self.sort_order.set("По возрастанию")
        self.sort_order.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(sort_frame, text="Применить", 
                  command=self.apply_sorting).pack(side=tk.LEFT, padx=5)
        
        # Множественная сортировка
        multi_sort_frame = ttk.LabelFrame(sort_filter_frame, text="Множественная сортировка", padding="5")
        multi_sort_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.multi_sort_vars = []
        multi_sort_inner = ttk.Frame(multi_sort_frame)
        multi_sort_inner.pack(fill=tk.X)
        
        ttk.Button(multi_sort_inner, text="Добавить атрибут", 
                  command=self.add_sort_attribute).pack(side=tk.LEFT, padx=2)
        ttk.Button(multi_sort_inner, text="Сортировать", 
                  command=self.apply_multi_sorting).pack(side=tk.LEFT, padx=2)
        ttk.Button(multi_sort_inner, text="Очистить", 
                  command=self.clear_multi_sort).pack(side=tk.LEFT, padx=2)
        
        self.multi_sort_container = ttk.Frame(multi_sort_frame)
        self.multi_sort_container.pack(fill=tk.X, pady=5)
        
        # Информация о выбранных атрибутах
        attributes_frame = ttk.Frame(data_frame)
        attributes_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.attributes_label = ttk.Label(attributes_frame, text="Отображаемые атрибуты: все")
        self.attributes_label.pack(side=tk.LEFT)
        
        # Таблица для отображения данных
        tree_frame = ttk.Frame(data_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview с вертикальной прокруткой
        self.tree = ttk.Treeview(tree_frame, show='headings')  # Убираем колонку #0
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещаем элементы
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Контекстное меню для копирования
        self.create_context_menu()
        
    def create_context_menu(self):
        """Создание контекстного меню для копирования"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать значение", command=self.copy_cell_value)
        self.context_menu.add_command(label="Копировать строку", command=self.copy_row)
        self.context_menu.add_command(label="Копировать заголовок", command=self.copy_header)
        
        # Привязываем правую кнопку мыши
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column != '#0':
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_cell_value(self):
        """Копировать значение ячейки"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            column = self.tree.focus_column()
            if column:
                # Получаем индекс колонки
                col_index = int(column.replace('#', '')) - 1
                values = self.tree.item(item, 'values')
                if values and col_index < len(values):
                    value = str(values[col_index])
                    self.root.clipboard_clear()
                    self.root.clipboard_append(value)
                    messagebox.showinfo("Успех", "Значение скопировано в буфер обмена")
    
    def copy_row(self):
        """Копировать всю строку"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values:
                row_text = "\t".join(str(v) for v in values)
                self.root.clipboard_clear()
                self.root.clipboard_append(row_text)
                messagebox.showinfo("Успех", "Строка скопирована в буфер обмена")
    
    def copy_header(self):
        """Копировать заголовок колонки"""
        column = self.tree.focus_column()
        if column:
            col_index = int(column.replace('#', '')) - 1
            columns = self.tree['columns']
            if col_index < len(columns):
                header = columns[col_index]
                self.root.clipboard_clear()
                self.root.clipboard_append(header)
                messagebox.showinfo("Успех", "Заголовок скопирован в буфер обмена")
    
    def add_sort_attribute(self):
        """Добавление атрибута для множественной сортировки"""
        available_columns = self.get_available_columns()
        if not available_columns:
            messagebox.showwarning("Предупреждение", "Нет доступных атрибутов для сортировки!")
            return
            
        frame = ttk.Frame(self.multi_sort_container)
        frame.pack(fill=tk.X, pady=2)
        
        column_combo = ttk.Combobox(frame, values=available_columns, 
                                   state="readonly", width=15)
        column_combo.set(available_columns[0])
        column_combo.pack(side=tk.LEFT, padx=2)
        
        # Заменяем ASC/DESC на русские названия
        order_combo = ttk.Combobox(frame, values=["По возрастанию", "По убыванию"], 
                                  state="readonly", width=15)
        order_combo.set("По возрастанию")
        order_combo.pack(side=tk.LEFT, padx=2)
        
        remove_btn = ttk.Button(frame, text="×", width=3, 
                               command=lambda: frame.destroy())
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        self.multi_sort_vars.append((column_combo, order_combo, frame))
    
    def clear_multi_sort(self):
        """Очистка множественной сортировки"""
        for _, _, frame in self.multi_sort_vars:
            frame.destroy()
        self.multi_sort_vars.clear()
    
    def apply_multi_sorting(self):
        """Применение множественной сортировки"""
        if not self.multi_sort_vars:
            messagebox.showwarning("Предупреждение", "Добавьте атрибуты для сортировки!")
            return
            
        sort_clauses = []
        for column_combo, order_combo, _ in self.multi_sort_vars:
            if column_combo.get():
                # Преобразуем русские названия обратно в SQL
                order_text = order_combo.get()
                sql_order = "ASC" if order_text == "По возрастанию" else "DESC"
                sort_clauses.append(f"{column_combo.get()} {sql_order}")
        
        if sort_clauses:
            self.display_table_data(sort_clause=", ".join(sort_clauses))
    
    def get_available_columns(self):
        """Получение списка всех доступных атрибутов без повторов"""
        columns_set = set()
        
        # Добавляем атрибуты основной таблицы
        if self.current_table:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"PRAGMA table_info({self.current_table})")
                table_columns = cursor.fetchall()
                for col in table_columns:
                    # Используем только имя атрибута (без имени таблицы)
                    columns_set.add(col[1])
            except sqlite3.Error:
                pass
        
        # Добавляем атрибуты соединенных таблиц (исключая дубликаты)
        for join_info in self.joined_tables:
            table_name = join_info['table2']
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_columns = cursor.fetchall()
                for col in table_columns:
                    col_name = col[1]
                    # Добавляем только если такого имени еще нет
                    if col_name not in columns_set:
                        columns_set.add(col_name)
            except sqlite3.Error:
                pass
        
        return sorted(list(columns_set))
    
    def get_all_tables_columns(self):
        """Получение всех атрибутов с именами таблиц (без повторов)"""
        all_columns = {}
        used_columns = set()
        
        # Основная таблица
        if self.current_table:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"PRAGMA table_info({self.current_table})")
                columns = cursor.fetchall()
                table_columns = []
                for col in columns:
                    if col[1] not in used_columns:
                        table_columns.append(col[1])
                        used_columns.add(col[1])
                all_columns[self.current_table] = table_columns
            except sqlite3.Error:
                pass
        
        # Соединенные таблицы
        for join_info in self.joined_tables:
            table_name = join_info['table2']
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                table_columns = []
                for col in columns:
                    if col[1] not in used_columns:
                        table_columns.append(col[1])
                        used_columns.add(col[1])
                all_columns[table_name] = table_columns
            except sqlite3.Error:
                pass
        
        return all_columns
    
    def update_table_list(self):
        """Обновление списка таблиц"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.table_listbox.delete(0, tk.END)
            for table in tables:
                if table[0] != "sqlite_sequence":  # Исключаем системную таблицу
                    self.table_listbox.insert(tk.END, table[0])
                    
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка получения списка таблиц: {e}")
    
    def on_table_select(self, event):
        """Обработка выбора таблицы"""
        selection = self.table_listbox.curselection()
        if selection:
            new_table = self.table_listbox.get(selection[0])
            
            # Сохраняем текущие соединения для предыдущей таблицы
            if self.current_table and self.joined_tables:
                self.table_joins[self.current_table] = self.joined_tables.copy()
            
            self.current_table = new_table
            
            # Восстанавливаем соединения для новой таблицы
            self.joined_tables = self.table_joins.get(self.current_table, [])
            
            self.selected_attributes.clear()  # Сбрасываем выбранные атрибуты
            self.update_join_info()
            self.update_attributes_label()
            self.display_table_data()
            self.clear_multi_sort()
    
    def display_table_data(self, sort_column=None, sort_order="ASC", sort_clause=None):
        """Отображение данных выбранной таблицы"""
        if not self.current_table and not self.joined_tables:
            return
            
        try:
            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Удаляем все колонки
            for col in self.tree['columns']:
                self.tree.heading(col, text="")
                self.tree.column(col, width=0)
            
            # Получение данных
            query, display_columns = self.build_query(sort_column, sort_order, sort_clause)
            
            if not display_columns:
                messagebox.showwarning("Предупреждение", "Нет атрибутов для отображения!")
                return
            
            # Настройка колонок Treeview
            self.tree['columns'] = display_columns
            
            # Устанавливаем заголовки и ширину колонок
            for col in display_columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, minwidth=80)
            
            # Обновление combobox для сортировки
            available_columns = self.get_available_columns()
            self.sort_column['values'] = available_columns
            if available_columns:
                self.sort_column.set(available_columns[0])
            
            # Выполнение запроса
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Заполнение данными
            for row in rows:
                self.tree.insert("", tk.END, values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {e}")
    
    def build_query(self, sort_column=None, sort_order="ASC", sort_clause=None):
        """Построение SQL запроса с исключением повторяющихся атрибутов"""
        if not self.current_table:
            return "", []
        
        # Определяем какие атрибуты выбирать (исключая дубликаты)
        used_columns = set()
        select_columns = []
        
        # Функция для добавления атрибутов без дубликатов (без приставок t1_, t2_)
        def add_columns(table_name):
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                for col in columns:
                    col_name = col[1]
                    if col_name not in used_columns:
                        select_columns.append(f"{table_name}.{col_name}")
                        used_columns.add(col_name)
            except sqlite3.Error:
                pass
        
        # Добавляем атрибуты основной таблицы
        add_columns(self.current_table)
        
        # Добавляем атрибуты соединенных таблиц (без приставок)
        for join_info in self.joined_tables:
            table_name = join_info['table2']
            add_columns(table_name)
        
        # Если выбраны конкретные атрибуты
        if self.selected_attributes:
            # Преобразуем выбранные атрибуты в формат для запроса
            final_columns = []
            used_columns.clear()
            
            for attr in self.selected_attributes:
                if '.' in attr:
                    table, col = attr.split('.')
                    if col not in used_columns:
                        final_columns.append(attr)
                        used_columns.add(col)
                else:
                    if attr not in used_columns:
                        final_columns.append(attr)
                        used_columns.add(attr)
            
            select_columns = final_columns
        
        if not select_columns:
            return "", []
        
        # Строим SELECT часть
        select_stmt = "SELECT " + ", ".join(select_columns)
        
        # FROM часть
        from_stmt = f"FROM {self.current_table}"
        
        # JOIN части
        join_stmts = []
        for join_info in self.joined_tables:
            join_type = join_info.get('join_type', 'INNER')
            table2 = join_info['table2']
            condition = join_info['condition']
            join_stmts.append(f"{join_type} JOIN {table2} ON {condition}")
        
        # ORDER BY часть (преобразуем русские названия обратно в SQL)
        order_stmt = ""
        if sort_clause:
            # Заменяем русские названия на SQL в sort_clause
            sort_clause = sort_clause.replace("По возрастанию", "ASC").replace("По убыванию", "DESC")
            order_stmt = f"ORDER BY {sort_clause}"
        elif sort_column:
            # Преобразуем русское название порядка сортировки
            if sort_order == "По возрастанию":
                sql_order = "ASC"
            elif sort_order == "По убыванию":
                sql_order = "DESC"
            else:
                sql_order = sort_order
            order_stmt = f"ORDER BY {sort_column} {sql_order}"
        
        # Собираем полный запрос
        query = f"{select_stmt} {from_stmt} {' '.join(join_stmts)} {order_stmt}"
        
        # Для отображения используем только имена атрибутов (без имен таблиц и приставок)
        display_columns = []
        for col in select_columns:
            # Берем только имя атрибута (последнюю часть после точки)
            display_columns.append(col.split('.')[-1])
        
        return query.strip(), display_columns
    
    def apply_sorting(self):
        """Применение сортировки"""
        if (self.current_table or self.joined_tables) and self.sort_column.get():
            # Получаем выбранный порядок сортировки
            sort_order = self.sort_order.get()
            self.display_table_data(self.sort_column.get(), sort_order)
    
    def join_tables_dialog(self):
        """Диалог соединения таблиц"""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Сначала выберите основную таблицу!")
            return
            
        dialog = JoinTablesDialog(self.root, self)
        self.root.wait_window(dialog.top)
    
    def join_tables(self, table2, table1_attr, table2_attr, join_type="INNER"):
        """Соединение таблиц"""
        try:
            # Проверяем существование таблиц и атрибутов
            cursor = self.connection.cursor()
            
            # Проверяем основную таблицу
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            table1_columns = [col[1] for col in cursor.fetchall()]
            if table1_attr not in table1_columns:
                messagebox.showerror("Ошибка", f"Атрибут '{table1_attr}' не найден в таблице '{self.current_table}'")
                return False
            
            # Проверяем вторую таблицу
            cursor.execute(f"PRAGMA table_info({table2})")
            table2_columns = [col[1] for col in cursor.fetchall()]
            if table2_attr not in table2_columns:
                messagebox.showerror("Ошибка", f"Атрибут '{table2_attr}' не найден в таблице '{table2}'")
                return False
            
            # Проверяем нет ли уже такого соединения
            for join_info in self.joined_tables:
                if join_info['table2'] == table2:
                    messagebox.showwarning("Предупреждение", f"Таблица '{table2}' уже соединена!")
                    return False
            
            # Создаем условие соединения
            condition = f"{self.current_table}.{table1_attr} = {table2}.{table2_attr}"
            
            # Сохраняем информацию о соединении
            join_info = {
                'table2': table2,
                'condition': condition,
                'join_type': join_type
            }
            
            self.joined_tables.append(join_info)
            
            # Сохраняем в общий словарь соединений
            self.table_joins[self.current_table] = self.joined_tables.copy()
            
            self.update_join_info()
            self.display_table_data()
            messagebox.showinfo("Успех", f"Таблицы соединены: {self.current_table} ↔ {table2}")
            return True
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения таблиц: {e}")
            return False
    
    def update_join_info(self):
        """Обновление информации о соединениях"""
        self.join_info_text.delete(1.0, tk.END)
        if self.joined_tables:
            self.join_info_text.insert(tk.END, f"Основная: {self.current_table}\n\n")
            for i, join_info in enumerate(self.joined_tables):
                self.join_info_text.insert(tk.END, f"{i+1}. {join_info['table2']}\n")
                self.join_info_text.insert(tk.END, f"   Условие: {join_info['condition']}\n")
                self.join_info_text.insert(tk.END, f"   Тип: {join_info['join_type']}\n\n")
        else:
            self.join_info_text.insert(tk.END, "Нет активных соединений")
    
    def remove_join(self):
        """Удаление выбранного соединения"""
        if not self.joined_tables:
            return
            
        # Простой интерфейс для удаления - удаляем последнее соединение
        if self.joined_tables:
            removed_join = self.joined_tables.pop()
            
            # Обновляем сохраненные соединения
            self.table_joins[self.current_table] = self.joined_tables.copy()
            
            self.update_join_info()
            self.display_table_data()
            messagebox.showinfo("Успех", f"Соединение с '{removed_join['table2']}' удалено")
    
    def clear_joins(self):
        """Очистка всех соединений"""
        self.joined_tables.clear()
        if self.current_table:
            self.table_joins[self.current_table] = []
        self.update_join_info()
        if self.current_table:
            self.display_table_data()
    
    def select_attributes_dialog(self):
        """Диалог выбора атрибутов для отображения"""
        if not self.current_table and not self.joined_tables:
            messagebox.showwarning("Предупреждение", "Сначала выберите таблицу!")
            return
            
        dialog = SelectAttributesDialog(self.root, self)
        self.root.wait_window(dialog.top)
    
    def update_attributes_label(self):
        """Обновление метки с выбранными атрибутами"""
        if self.selected_attributes:
            attrs_text = ", ".join([attr.split('.')[-1] for attr in self.selected_attributes[:3]])
            if len(self.selected_attributes) > 3:
                attrs_text += f"... (+{len(self.selected_attributes)-3})"
            self.attributes_label.config(text=f"Отображаемые атрибуты: {attrs_text}")
        else:
            self.attributes_label.config(text="Отображаемые атрибуты: все")
    
    def set_selected_attributes(self, attributes):
        """Установка выбранных атрибутов"""
        self.selected_attributes = attributes
        self.update_attributes_label()
        self.display_table_data()

    def create_table_dialog(self):
        """Диалог создания таблицы"""
        dialog = CreateTableDialog(self.root, self)
        self.root.wait_window(dialog.top)
    
    def create_table(self, table_name, columns):
        """Создание новой таблицы"""
        try:
            cursor = self.connection.cursor()
            
            # Формирование SQL запроса
            columns_sql = ", ".join([f"{col['name']} {col['type']}" for col in columns])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
            
            cursor.execute(query)
            self.connection.commit()
            
            messagebox.showinfo("Успех", f"Таблица '{table_name}' создана успешно!")
            self.update_table_list()
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка создания таблицы: {e}")
    
    def add_record_dialog(self):
        """Диалог добавления записи"""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу!")
            return
            
        dialog = AddRecordDialog(self.root, self)
        self.root.wait_window(dialog.top)
    
    def add_record(self, values):
        """Добавление новой записи"""
        try:
            cursor = self.connection.cursor()
            
            # Получение структуры таблицы
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Формирование запроса
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {self.current_table} VALUES ({placeholders})"
            
            cursor.execute(query, values)
            self.connection.commit()
            
            messagebox.showinfo("Успех", "Запись добавлена успешно!")
            self.display_table_data()
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления записи: {e}")
    
    def delete_table(self):
        """Удаление выбранной таблицы"""
        if not self.current_table:
            messagebox.showwarning("Предупреждение", "Выберите таблицу для удаления!")
            return
            
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите удалить таблицу '{self.current_table}'?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {self.current_table}")
                self.connection.commit()
                
                messagebox.showinfo("Успех", f"Таблица '{self.current_table}' удалена!")
                self.current_table = None
                self.joined_tables.clear()
                self.selected_attributes.clear()
                if self.current_table in self.table_joins:
                    del self.table_joins[self.current_table]
                self.update_table_list()
                # Очистка Treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.tree['columns'] = []
                self.update_join_info()
                self.update_attributes_label()
                
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления таблицы: {e}")
    
    def refresh_data(self):
        """Обновление данных"""
        if self.current_table or self.joined_tables:
            self.display_table_data()
        self.update_table_list()


class JoinTablesDialog:
    def __init__(self, parent, app):
        self.app = app
        self.top = tk.Toplevel(parent)
        self.top.title("Соединить таблицы")
        self.top.geometry("500x400")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов диалога"""
        ttk.Label(self.top, text="Соединение таблиц", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Основная таблица
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(main_frame, text=f"Основная таблица: {self.app.current_table}", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Выбор второй таблицы
        ttk.Label(main_frame, text="Таблица для соединения:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.table2_var = tk.StringVar()
        self.table2_combo = ttk.Combobox(main_frame, textvariable=self.table2_var, 
                                        state="readonly", width=20)
        
        # Заполняем список таблиц (исключая текущую)
        tables = []
        for i in range(self.app.table_listbox.size()):
            table = self.app.table_listbox.get(i)
            if table != self.app.current_table:
                tables.append(table)
        
        self.table2_combo['values'] = tables
        if tables:
            self.table2_combo.set(tables[0])
        self.table2_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Выбор атрибутов для соединения
        ttk.Label(main_frame, text="Атрибут из основной таблицы:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.attr1_combo = ttk.Combobox(main_frame, state="readonly", width=20)
        self.attr1_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Атрибут из второй таблицы:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.attr2_combo = ttk.Combobox(main_frame, state="readonly", width=20)
        self.attr2_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Тип соединения
        ttk.Label(main_frame, text="Тип соединения:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.join_type = ttk.Combobox(main_frame, values=["INNER JOIN", "LEFT JOIN"], 
                                     state="readonly", width=20)
        self.join_type.set("INNER JOIN")
        self.join_type.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Обновляем атрибуты при выборе таблицы
        self.table2_combo.bind('<<ComboboxSelected>>', self.update_attributes)
        self.update_attributes()
        
        # Предпросмотр запроса
        ttk.Label(main_frame, text="Предпросмотр запроса:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        self.query_preview = tk.Text(main_frame, height=4, width=50)
        self.query_preview.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # Обновляем предпросмотр при изменении
        self.table2_combo.bind('<<ComboboxSelected>>', self.update_query_preview)
        self.attr1_combo.bind('<<ComboboxSelected>>', self.update_query_preview)
        self.attr2_combo.bind('<<ComboboxSelected>>', self.update_query_preview)
        self.join_type.bind('<<ComboboxSelected>>', self.update_query_preview)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.top)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Соединить", 
                  command=self.join_tables).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=self.top.destroy).pack(side=tk.LEFT, padx=10)
        
        self.update_query_preview()
    
    def update_attributes(self, event=None):
        """Обновление списков атрибутов"""
        try:
            cursor = self.app.connection.cursor()
            
            # Атрибуты основной таблицы
            cursor.execute(f"PRAGMA table_info({self.app.current_table})")
            table1_attrs = [col[1] for col in cursor.fetchall()]
            self.attr1_combo['values'] = table1_attrs
            if table1_attrs:
                self.attr1_combo.set(table1_attrs[0])
            
            # Атрибуты второй таблицы
            table2 = self.table2_combo.get()
            if table2:
                cursor.execute(f"PRAGMA table_info({table2})")
                table2_attrs = [col[1] for col in cursor.fetchall()]
                self.attr2_combo['values'] = table2_attrs
                if table2_attrs:
                    self.attr2_combo.set(table2_attrs[0])
                    
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка получения атрибутов: {e}")
    
    def update_query_preview(self, event=None):
        """Обновление предпросмотра SQL запроса"""
        table2 = self.table2_combo.get()
        attr1 = self.attr1_combo.get()
        attr2 = self.attr2_combo.get()
        join_type = self.join_type.get().split()[0]  # Берем только первое слово (INNER, LEFT, etc.)
        
        if table2 and attr1 and attr2:
            query = f"SELECT *\nFROM {self.app.current_table}\n{join_type} JOIN {table2}\nON {self.app.current_table}.{attr1} = {table2}.{attr2}"
            self.query_preview.delete(1.0, tk.END)
            self.query_preview.insert(tk.END, query)
    
    def join_tables(self):
        """Соединение таблиц"""
        table2 = self.table2_combo.get()
        attr1 = self.attr1_combo.get()
        attr2 = self.attr2_combo.get()
        join_type = self.join_type.get().split()[0]
        
        if not table2 or not attr1 or not attr2:
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return
            
        if self.app.join_tables(table2, attr1, attr2, join_type):
            self.top.destroy()


class SelectAttributesDialog:
    def __init__(self, parent, app):
        self.app = app
        self.top = tk.Toplevel(parent)
        self.top.title("Выбор атрибутов для отображения")
        self.top.geometry("500x600")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.selected_attributes = self.app.selected_attributes.copy()
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов диалога"""
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Выберите атрибуты для отображения", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(main_frame, text="Доступные атрибуты:").pack(anchor=tk.W, pady=5)
        
        # Фрейм для чекбоксов атрибутов
        checkboxes_frame = ttk.Frame(main_frame)
        checkboxes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(checkboxes_frame)
        scrollbar = ttk.Scrollbar(checkboxes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Получаем все атрибуты
        all_columns = self.app.get_all_tables_columns()
        self.checkbox_vars = {}
        
        row = 0
        for table_name, columns in all_columns.items():
            # Заголовок таблицы
            ttk.Label(scrollable_frame, text=f"Таблица: {table_name}", 
                     font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
            row += 1
            
            # Чекбоксы для атрибутов таблицы
            for column in columns:
                var = tk.BooleanVar()
                full_attr_name = f"{table_name}.{column}"
                var.set(full_attr_name in self.selected_attributes)
                
                cb = ttk.Checkbutton(scrollable_frame, text=column, variable=var)
                cb.grid(row=row, column=0, sticky=tk.W, pady=2)
                
                self.checkbox_vars[full_attr_name] = var
                row += 1
        
        # Кнопки управления
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.grid(row=row, column=0, sticky=tk.W+tk.E, pady=20)
        
        ttk.Button(buttons_frame, text="Выбрать все", 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Снять все", 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки диалога
        dialog_buttons = ttk.Frame(main_frame)
        dialog_buttons.pack(fill=tk.X, pady=10)
        
        ttk.Button(dialog_buttons, text="Применить", 
                  command=self.apply_selection).pack(side=tk.LEFT, padx=10)
        ttk.Button(dialog_buttons, text="Отмена", 
                  command=self.top.destroy).pack(side=tk.LEFT, padx=10)
        ttk.Button(dialog_buttons, text="Показать все", 
                  command=self.show_all).pack(side=tk.LEFT, padx=10)
    
    def select_all(self):
        """Выбрать все атрибуты"""
        for var in self.checkbox_vars.values():
            var.set(True)
    
    def deselect_all(self):
        """Снять выбор со всех атрибутов"""
        for var in self.checkbox_vars.values():
            var.set(False)
    
    def show_all(self):
        """Показать все атрибуты"""
        self.selected_attributes = []
        self.apply_selection()
    
    def apply_selection(self):
        """Применить выбранные атрибуты"""
        selected = []
        for attr_name, var in self.checkbox_vars.items():
            if var.get():
                selected.append(attr_name)
        
        self.app.set_selected_attributes(selected)
        self.top.destroy()


class CreateTableDialog:
    def __init__(self, parent, app):
        self.app = app
        self.top = tk.Toplevel(parent)
        self.top.title("Создать таблицу")
        self.top.geometry("400x300")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.columns = []
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов диалога"""
        ttk.Label(self.top, text="Название таблицы:").pack(pady=5)
        self.table_name = ttk.Entry(self.top, width=30)
        self.table_name.pack(pady=5)
        
        # Фрейм для колонок
        columns_frame = ttk.LabelFrame(self.top, text="Колонки", padding="10")
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Список колонок
        self.columns_listbox = tk.Listbox(columns_frame, height=8)
        self.columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Фрейм для кнопок управления колонками
        buttons_frame = ttk.Frame(columns_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(buttons_frame, text="Добавить", 
                  command=self.add_column_dialog).pack(pady=2)
        ttk.Button(buttons_frame, text="Удалить", 
                  command=self.remove_column).pack(pady=2)
        
        # Кнопки диалога
        dialog_buttons = ttk.Frame(self.top)
        dialog_buttons.pack(pady=10)
        
        ttk.Button(dialog_buttons, text="Создать", 
                  command=self.create_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(dialog_buttons, text="Отмена", 
                  command=self.top.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_column_dialog(self):
        """Диалог добавления колонки"""
        dialog = tk.Toplevel(self.top)
        dialog.title("Добавить колонку")
        dialog.geometry("300x150")
        dialog.transient(self.top)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Имя колонки:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=20)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Тип данных:").pack(pady=5)
        type_combo = ttk.Combobox(dialog, values=["TEXT", "INTEGER", "REAL", "BLOB"], 
                                 state="readonly")
        type_combo.set("TEXT")
        type_combo.pack(pady=5)
        
        def add_column():
            name = name_entry.get().strip()
            if name:
                column = {"name": name, "type": type_combo.get()}
                self.columns.append(column)
                self.columns_listbox.insert(tk.END, f"{name} ({type_combo.get()})")
                dialog.destroy()
        
        ttk.Button(dialog, text="Добавить", command=add_column).pack(pady=10)
    
    def remove_column(self):
        """Удаление выбранной колонки"""
        selection = self.columns_listbox.curselection()
        if selection:
            index = selection[0]
            self.columns_listbox.delete(index)
            self.columns.pop(index)
    
    def create_table(self):
        """Создание таблицы"""
        table_name = self.table_name.get().strip()
        if not table_name:
            messagebox.showwarning("Предупреждение", "Введите название таблицы!")
            return
            
        if not self.columns:
            messagebox.showwarning("Предупреждение", "Добавьте хотя бы одну колонку!")
            return
            
        self.app.create_table(table_name, self.columns)
        self.top.destroy()


class AddRecordDialog:
    def __init__(self, parent, app):
        self.app = app
        self.top = tk.Toplevel(parent)
        self.top.title("Добавить запись")
        self.top.geometry("300x400")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.entries = {}
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов диалога"""
        try:
            cursor = self.app.connection.cursor()
            cursor.execute(f"PRAGMA table_info({self.app.current_table})")
            columns = cursor.fetchall()
            
            ttk.Label(self.top, text=f"Добавить запись в '{self.app.current_table}'", 
                     font=("Arial", 10, "bold")).pack(pady=10)
            
            # Фрейм для полей ввода
            input_frame = ttk.Frame(self.top)
            input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            for i, column in enumerate(columns):
                col_name = column[1]
                col_type = column[2]
                
                ttk.Label(input_frame, text=f"{col_name} ({col_type}):").grid(
                    row=i, column=0, sticky=tk.W, pady=5)
                
                entry = ttk.Entry(input_frame, width=20)
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
                self.entries[col_name] = entry
            
            input_frame.columnconfigure(1, weight=1)
            
            # Кнопки
            buttons_frame = ttk.Frame(self.top)
            buttons_frame.pack(pady=10)
            
            ttk.Button(buttons_frame, text="Добавить", 
                      command=self.add_record).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Отмена", 
                      command=self.top.destroy).pack(side=tk.LEFT, padx=5)
                      
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка получения структуры таблицы: {e}")
            self.top.destroy()
    
    def add_record(self):
        """Добавление записи"""
        values = []
        for col_name, entry in self.entries.items():
            value = entry.get().strip()
            values.append(value if value else None)
        
        self.app.add_record(values)
        self.top.destroy()


def main():
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
    
    # Закрытие соединения при выходе
    if app.connection:
        app.connection.close()

if __name__ == "__main__":
    main()