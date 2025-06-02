import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import math
from tkcalendar import DateEntry
import json
import os
import tempfile
import webbrowser


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.resizable(False, False)
        self.root.title("Многофункциональный калькулятор")
        self.last_active_entry = None
        self.saves_file = "calculator_saves.json"
        self.saves = self.load_saves()
        self.current_save_id = None
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=5, expand=True, fill='both')
        self.create_bmi_tab()
        self.create_scientific_tab()
        self.create_geometry_tab()
        self.create_discount_tab()
        self.create_age_tab()
        self.create_graph_tab()
        self.create_trip_cost_tab()
        self.create_bill_split_tab()
        self.create_saves_tab()

        # Добавляем новую вкладку "О программе"
        self.create_about_tab()
        self.current_tab = "ИМТ"
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.create_keyboard(root)

    def create_about_tab(self):
        """Создает вкладку 'О программе'."""
        about_tab = ttk.Frame(self.notebook)
        self.notebook.add(about_tab, text='О программе')
        ttk.Label(about_tab, text="Щелкните ниже, чтобы открыть инструкцию:").pack(pady=10)
        # Кнопка для открытия HTML-файла
        ttk.Button(about_tab, text="Открыть инструкцию", command=self.open_about_file).pack(pady=5)

    def open_about_file(self):
        """Открывает HTML-файл с инструкцией."""
        webbrowser.open('file://' + os.path.realpath('index/instrutcion.htm'))

    def create_saves_tab(self):
        """Создает вкладку для управления сохранениями"""
        saves_tab = ttk.Frame(self.notebook)
        self.notebook.add(saves_tab, text='Сохранения')

        frame = ttk.Frame(saves_tab)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Список сохранений
        ttk.Label(frame, text="Сохраненные данные:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.saves_listbox = tk.Listbox(frame, width=40, height=10)
        self.saves_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.saves_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky='ns')
        self.saves_listbox.config(yscrollcommand=scrollbar.set)

        # Поле для имени сохранения
        ttk.Label(frame, text="Имя сохранения:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.save_name_entry = ttk.Entry(frame)
        self.save_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Кнопки управления
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(buttons_frame, text="Сохранить", style="Modern.TButton", command=self.save_current_state).pack(
            side='left', padx=5)
        ttk.Button(buttons_frame, text="Загрузить", style="Modern.TButton", command=self.load_selected_save).pack(
            side='left', padx=5)
        ttk.Button(buttons_frame, text="Удалить", style="Modern.TButton", command=self.delete_selected_save).pack(
            side='left', padx=5)

        # Полоса результата
        self.saves_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.saves_result.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky='ew')

        # Обновляем список сохранений
        self.update_saves_list()

    def create_file_manager_tab(self):
        """Создает вкладку файлового менеджера"""
        file_tab = ttk.Frame(self.notebook)
        self.notebook.add(file_tab, text='Файлы')

        frame = ttk.Frame(file_tab)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Полоса результата
        self.file_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.file_result.pack(fill='x', pady=(0, 10))

        # Основной контейнер с двумя колонками
        main_container = ttk.Frame(frame)
        main_container.pack(fill='both', expand=True)

        # Левая колонка - список файлов
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="Файлы в корневой директории:").pack(anchor='w', pady=(0, 5))

        # Список файлов с прокруткой
        files_frame = ttk.Frame(left_frame)
        files_frame.pack(fill='both', expand=True)

        self.files_listbox = tk.Listbox(files_frame, width=30, height=15)
        self.files_listbox.pack(side='left', fill='both', expand=True)

        files_scrollbar = ttk.Scrollbar(files_frame, orient='vertical', command=self.files_listbox.yview)
        files_scrollbar.pack(side='right', fill='y')
        self.files_listbox.config(yscrollcommand=files_scrollbar.set)

        # Кнопки управления файлами
        file_buttons_frame = ttk.Frame(left_frame)
        file_buttons_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(file_buttons_frame, text="Обновить список", style="Modern.TButton",
                   command=self.refresh_files_list).pack(side='left', padx=(0, 5))
        ttk.Button(file_buttons_frame, text="Открыть файл", style="Modern.TButton",
                   command=self.open_selected_file).pack(side='left', padx=5)

        # Правая колонка - содержимое файла
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="Содержимое файла:").pack(anchor='w', pady=(0, 5))

        # Текстовое поле с прокруткой
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill='both', expand=True)

        self.file_content_text = tk.Text(text_frame, wrap=tk.WORD, width=50, height=15,
                                         bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.file_content_text.pack(side='left', fill='both', expand=True)

        text_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.file_content_text.yview)
        text_scrollbar.pack(side='right', fill='y')
        self.file_content_text.config(yscrollcommand=text_scrollbar.set)

        # Заполняем список файлов
        self.refresh_files_list()

    def refresh_files_list(self):
        """Обновляет список файлов в корневой директории"""
        self.files_listbox.delete(0, tk.END)
        try:
            current_dir = os.getcwd()
            files = os.listdir(current_dir)

            # Сортируем файлы: сначала директории, потом файлы
            dirs = [f for f in files if os.path.isdir(f)]
            files_only = [f for f in files if os.path.isfile(f)]

            # Добавляем директории
            for directory in sorted(dirs):
                self.files_listbox.insert(tk.END, f"📁 {directory}")

            # Добавляем файлы
            for file in sorted(files_only):
                self.files_listbox.insert(tk.END, f"📄 {file}")

            self.file_result.config(text=f"Найдено {len(files)} элементов в директории: {current_dir}")
        except Exception as e:
            self.file_result.config(text=f"Ошибка при чтении директории: {str(e)}")

    def open_selected_file(self):
        """Открывает выбранный файл и отображает его содержимое"""
        selected = self.files_listbox.curselection()
        if not selected:
            self.file_result.config(text="Ошибка: Выберите файл для открытия")
            return

        selected_item = self.files_listbox.get(selected[0])
        # Убираем эмодзи и пробелы
        filename = selected_item.replace("📁 ", "").replace("📄 ", "")

        try:
            # Проверяем, что это файл, а не директория
            if os.path.isdir(filename):
                self.file_result.config(text="Ошибка: Выбранный элемент является директорией")
                return

            # Читаем содержимое файла
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()

            # Очищаем текстовое поле и вставляем содержимое
            self.file_content_text.delete(1.0, tk.END)
            self.file_content_text.insert(1.0, content)

            # Получаем размер файла
            file_size = os.path.getsize(filename)
            lines_count = content.count('\n') + 1

            self.file_result.config(text=f"Файл '{filename}' открыт. Размер: {file_size} байт, строк: {lines_count}")

        except Exception as e:
            self.file_result.config(text=f"Ошибка при открытии файла '{filename}': {str(e)}")
            self.file_content_text.delete(1.0, tk.END)
            self.file_content_text.insert(1.0, f"Не удалось открыть файл:\n{str(e)}")

    def load_saves(self):
        """Загружает сохранения из файла"""
        if os.path.exists(self.saves_file):
            try:
                with open(self.saves_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_saves(self):
        """Сохраняет все сохранения в файл"""
        with open(self.saves_file, 'w', encoding='utf-8') as f:
            json.dump(self.saves, f, ensure_ascii=False, indent=2)

    def update_saves_list(self):
        """Обновляет список сохранений в ListBox"""
        self.saves_listbox.delete(0, tk.END)
        for save_id, save_data in self.saves.items():
            save_name = save_data.get('name', f'Сохранение {save_id}')
            self.saves_listbox.insert(tk.END, f"{save_id}: {save_name}")

    def save_current_state(self):
        """Сохраняет текущее состояние приложения"""
        save_name = self.save_name_entry.get().strip()
        if not save_name:
            self.saves_result.config(text="Ошибка: Введите имя для сохранения")
            return

        # Создаем уникальный ID для сохранения
        save_id = str(datetime.now().timestamp()).replace('.', '')[-8:]

        # Собираем данные для сохранения
        save_data = {
            'name': save_name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data': self.collect_current_data()
        }

        # Добавляем в сохранения
        self.saves[save_id] = save_data
        self.save_saves()
        self.update_saves_list()
        self.saves_result.config(text=f"Данные успешно сохранены под ID: {save_id}")

    def collect_current_data(self):
        """Собирает текущие данные со всех вкладок"""
        data = {}

        # ИМТ
        data['bmi'] = {
            'weight': self.weight_entry.get(),
            'height': self.height_entry.get(),
            'result': self.bmi_result.cget('text')
        }

        # Научный калькулятор
        data['scientific'] = {
            'expression': self.expression_entry.get(),
            'result': self.expression_result.cget('text')
        }

        # Геометрия
        data['geometry'] = {
            'figure': self.figure_var.get(),
            'radius': self.radius_entry.get() if hasattr(self, 'radius_entry') else '',
            'side': self.side_entry.get() if hasattr(self, 'side_entry') else '',
            'length': self.length_entry.get() if hasattr(self, 'length_entry') else '',
            'width': self.width_entry.get() if hasattr(self, 'width_entry') else '',
            'base': self.base_entry.get() if hasattr(self, 'base_entry') else '',
            'height': self.height_triangle_entry.get() if hasattr(self, 'height_triangle_entry') else '',
            'result': self.geometry_result.cget('text')
        }

        # Скидки
        data['discount'] = {
            'amount': self.amount_entry.get(),
            'discount': self.discount_entry.get(),
            'result': self.discount_result.cget('text')
        }

        # Возраст
        data['age'] = {
            'birthdate': self.birthdate_entry.get(),
            'result': self.age_result.cget('text')
        }

        # Графики
        data['graph'] = {
            'function': self.function_entry.get()
        }

        # Стоимость поездки
        data['trip'] = {
            'mode': self.trip_mode_var.get(),
            'distance': self.distance_entry.get() if hasattr(self, 'distance_entry') else '',
            'fuel_price': self.fuel_price_entry.get() if hasattr(self, 'fuel_price_entry') else '',
            'fuel_consumption': self.fuel_consumption_entry.get() if hasattr(self, 'fuel_consumption_entry') else '',
            'start_lat': self.start_lat_entry.get() if hasattr(self, 'start_lat_entry') else '',
            'start_lon': self.start_lon_entry.get() if hasattr(self, 'start_lon_entry') else '',
            'end_lat': self.end_lat_entry.get() if hasattr(self, 'end_lat_entry') else '',
            'end_lon': self.end_lon_entry.get() if hasattr(self, 'end_lon_entry') else '',
            'result': self.trip_cost_result.cget('text')
        }

        # Дележ счета
        data['bill'] = {
            'bill_amount': self.bill_amount_entry.get(),
            'num_people': self.num_people_entry.get(),
            'result': self.bill_split_result.cget('text')
        }

        return data

    def load_selected_save(self):
        """Загружает выбранное сохранение"""
        selected = self.saves_listbox.curselection()
        if not selected:
            self.saves_result.config(text="Ошибка: Выберите сохранение для загрузки")
            return

        # Получаем ID сохранения
        save_id = list(self.saves.keys())[selected[0]]
        save_data = self.saves[save_id]['data']

        # Загружаем данные в интерфейс
        self.apply_saved_data(save_data)
        self.current_save_id = save_id
        self.saves_result.config(text=f"Данные сохранения {save_id} успешно загружены")

    def apply_saved_data(self, data):
        """Применяет сохраненные данные к интерфейсу"""
        # ИМТ
        if 'bmi' in data:
            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, data['bmi']['weight'])
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, data['bmi']['height'])
            self.bmi_result.config(text=data['bmi']['result'])

        # Научный калькулятор
        if 'scientific' in data:
            self.expression_entry.delete(0, tk.END)
            self.expression_entry.insert(0, data['scientific']['expression'])
            self.expression_result.config(text=data['scientific']['result'])

        # Геометрия
        if 'geometry' in data:
            geo_data = data['geometry']
            self.figure_var.set(geo_data['figure'])
            self.figure_combobox.set(geo_data['figure'])
            self.on_figure_select(None)

            if geo_data['figure'] == 'Круг' and hasattr(self, 'radius_entry'):
                self.radius_entry.delete(0, tk.END)
                self.radius_entry.insert(0, geo_data['radius'])
            elif geo_data['figure'] == 'Квадрат' and hasattr(self, 'side_entry'):
                self.side_entry.delete(0, tk.END)
                self.side_entry.insert(0, geo_data['side'])
            elif geo_data['figure'] == 'Прямоугольник':
                if hasattr(self, 'length_entry'):
                    self.length_entry.delete(0, tk.END)
                    self.length_entry.insert(0, geo_data['length'])
                if hasattr(self, 'width_entry'):
                    self.width_entry.delete(0, tk.END)
                    self.width_entry.insert(0, geo_data['width'])
            elif geo_data['figure'] == 'Треугольник':
                if hasattr(self, 'base_entry'):
                    self.base_entry.delete(0, tk.END)
                    self.base_entry.insert(0, geo_data['base'])
                if hasattr(self, 'height_triangle_entry'):
                    self.height_triangle_entry.delete(0, tk.END)
                    self.height_triangle_entry.insert(0, geo_data['height'])

            self.geometry_result.config(text=geo_data['result'])

        # Скидки
        if 'discount' in data:
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, data['discount']['amount'])
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.insert(0, data['discount']['discount'])
            self.discount_result.config(text=data['discount']['result'])

        # Возраст
        if 'age' in data:
            self.birthdate_entry.set_date(data['age']['birthdate'])
            self.age_result.config(text=data['age']['result'])

        # Графики
        if 'graph' in data:
            self.function_entry.delete(0, tk.END)
            self.function_entry.insert(0, data['graph']['function'])

        # Стоимость поездки
        if 'trip' in data:
            trip_data = data['trip']
            self.trip_mode_var.set(trip_data['mode'])
            self.trip_mode_combobox.set(trip_data['mode'])
            self.on_trip_mode_select(None)

            if trip_data['mode'] == "По километрам":
                if hasattr(self, 'distance_entry'):
                    self.distance_entry.delete(0, tk.END)
                    self.distance_entry.insert(0, trip_data['distance'])
                if hasattr(self, 'fuel_price_entry'):
                    self.fuel_price_entry.delete(0, tk.END)
                    self.fuel_price_entry.insert(0, trip_data['fuel_price'])
                if hasattr(self, 'fuel_consumption_entry'):
                    self.fuel_consumption_entry.delete(0, tk.END)
                    self.fuel_consumption_entry.insert(0, trip_data['fuel_consumption'])
            else:
                if hasattr(self, 'start_lat_entry'):
                    self.start_lat_entry.delete(0, tk.END)
                    self.start_lat_entry.insert(0, trip_data['start_lat'])
                if hasattr(self, 'start_lon_entry'):
                    self.start_lon_entry.delete(0, tk.END)
                    self.start_lon_entry.insert(0, trip_data['start_lon'])
                if hasattr(self, 'end_lat_entry'):
                    self.end_lat_entry.delete(0, tk.END)
                    self.end_lat_entry.insert(0, trip_data['end_lat'])
                if hasattr(self, 'end_lon_entry'):
                    self.end_lon_entry.delete(0, tk.END)
                    self.end_lon_entry.insert(0, trip_data['end_lon'])
                if hasattr(self, 'fuel_price_entry'):
                    self.fuel_price_entry.delete(0, tk.END)
                    self.fuel_price_entry.insert(0, trip_data['fuel_price'])
                if hasattr(self, 'fuel_consumption_entry'):
                    self.fuel_consumption_entry.delete(0, tk.END)
                    self.fuel_consumption_entry.insert(0, trip_data['fuel_consumption'])

            self.trip_cost_result.config(text=trip_data['result'])

        # Дележ счета
        if 'bill' in data:
            self.bill_amount_entry.delete(0, tk.END)
            self.bill_amount_entry.insert(0, data['bill']['bill_amount'])
            self.num_people_entry.delete(0, tk.END)
            self.num_people_entry.insert(0, data['bill']['num_people'])
            self.bill_split_result.config(text=data['bill']['result'])

    def delete_selected_save(self):
        """Удаляет выбранное сохранение"""
        selected = self.saves_listbox.curselection()
        if not selected:
            self.saves_result.config(text="Ошибка: Выберите сохранение для удаления")
            return

        # Получаем ID сохранения
        save_id = list(self.saves.keys())[selected[0]]

        # Удаляем сохранение
        del self.saves[save_id]
        self.save_saves()
        self.update_saves_list()
        self.saves_result.config(text=f"Сохранение {save_id} успешно удалено")

    def on_tab_changed(self, event):
        tab_id = self.notebook.select()
        self.current_tab = self.notebook.tab(tab_id, "text")
        self.create_keyboard(self.root)

    def style_entry(self, entry):
        entry.config(font=("Arial", 14))
        entry.configure(width=20)
        entry.bind("<FocusIn>", self.set_active_entry)
        entry.bind("<Control-c>", lambda event: self.root.clipboard_clear() or self.root.clipboard_append(entry.get()))
        entry.bind("<Control-v>", lambda event: self.paste_from_clipboard(event, entry))

    def set_active_entry(self, event):
        self.last_active_entry = event.widget

    def paste_from_clipboard(self, event, entry):
        try:
            clipboard_content = self.root.clipboard_get()
            entry.delete(0, tk.END)
            entry.insert(0, clipboard_content)
            return "break"  # Предотвращает стандартную обработку события
        except tk.TclError:
            pass

    def get_active_entry(self):
        focused_widget = self.root.focus_get()
        if isinstance(focused_widget, (ttk.Entry, DateEntry)):
            return focused_widget
        return self.last_active_entry

    def create_bmi_tab(self):
        bmi_tab = ttk.Frame(self.notebook)
        self.notebook.add(bmi_tab, text='ИМТ')

        frame = ttk.Frame(bmi_tab)
        frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.bmi_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.bmi_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Вес (кг):").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.weight_entry = ttk.Entry(input_frame)
        self.style_entry(self.weight_entry)
        self.weight_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(input_frame, text="Рост (см):").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.height_entry = ttk.Entry(input_frame)
        self.style_entry(self.height_entry)
        self.height_entry.grid(row=1, column=1, padx=2, pady=2)

        ttk.Button(input_frame, text="Рассчитать ИМТ", style="Modern.TButton", command=self.calculate_bmi).grid(row=2,
                                                                                                                column=0,
                                                                                                                columnspan=2,
                                                                                                                pady=5)

    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get()) / 100
            bmi = weight / (height ** 2)
            category = self.get_bmi_category(bmi)
            self.bmi_result.config(text=f"Ваш ИМТ: {bmi:.2f} ({category})")
        except ValueError:
            self.bmi_result.config(text="Ошибка ввода")

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Недостаточный вес"
        elif 18.5 <= bmi < 25:
            return "Нормальный вес"
        elif 25 <= bmi < 30:
            return "Избыточный вес"
        else:
            return "Ожирение"

    def create_scientific_tab(self):
        scientific_tab = ttk.Frame(self.notebook)
        self.notebook.add(scientific_tab, text='Научный')

        frame = ttk.Frame(scientific_tab)
        frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.expression_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.expression_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Введите выражение:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.expression_entry = ttk.Entry(input_frame)
        self.style_entry(self.expression_entry)
        self.expression_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Button(input_frame, text="Вычислить", style="Modern.TButton", command=self.calculate_expression).grid(row=1,
                                                                                                                  column=0,
                                                                                                                  columnspan=2,
                                                                                                                  pady=5)

    def calculate_expression(self):
        try:
            expression = self.expression_entry.get()
            expression = expression.replace('²', '^2')
            expression = expression.replace('³', '^3')
            expression = expression.replace('^', '**')
            result = eval(expression, {'__builtins__': None}, self.get_math_globals())
            self.expression_result.config(text=f"Результат: {result}")
        except Exception as e:
            self.expression_result.config(text=f"Ошибка: {e}")

    def get_math_globals(self):
        return {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log10, 'ln': math.log, 'sqrt': math.sqrt,
            'pi': math.pi, 'e': math.e, 'rad': math.radians,
            'deg': math.degrees, 'fact': math.factorial,
            'abs': abs, 'exp': math.exp
        }

    def create_geometry_tab(self):
        geometry_tab = ttk.Frame(self.notebook)
        self.notebook.add(geometry_tab, text='Геометрия')

        main_frame = ttk.Frame(geometry_tab)
        main_frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.geometry_result = ttk.Label(main_frame, text="", style="Result.TLabel")
        self.geometry_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Выберите фигуру:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.figure_var = tk.StringVar()
        self.figure_combobox = ttk.Combobox(input_frame, textvariable=self.figure_var)
        self.figure_combobox['values'] = ('Круг', 'Квадрат', 'Прямоугольник', 'Треугольник')
        self.figure_combobox.grid(row=0, column=1, padx=2, pady=2)
        self.figure_combobox.bind("<<ComboboxSelected>>", self.on_figure_select)

        self.parameters_frame = ttk.Frame(input_frame)
        self.parameters_frame.grid(row=1, column=0, columnspan=2, pady=2)

        ttk.Button(input_frame, text="Рассчитать", style="Modern.TButton", command=self.calculate_geometry).grid(row=2,
                                                                                                                 column=0,
                                                                                                                 columnspan=2,
                                                                                                                 pady=5)

    def on_figure_select(self, event):
        for widget in self.parameters_frame.winfo_children():
            widget.destroy()

        figure = self.figure_var.get()
        if figure == 'Круг':
            ttk.Label(self.parameters_frame, text="Радиус:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
            self.radius_entry = ttk.Entry(self.parameters_frame)
            self.style_entry(self.radius_entry)
            self.radius_entry.grid(row=0, column=1, padx=2, pady=2)
        elif figure == 'Квадрат':
            ttk.Label(self.parameters_frame, text="Сторона:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
            self.side_entry = ttk.Entry(self.parameters_frame)
            self.style_entry(self.side_entry)
            self.side_entry.grid(row=0, column=1, padx=2, pady=2)
        elif figure == 'Прямоугольник':
            ttk.Label(self.parameters_frame, text="Длина:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
            self.length_entry = ttk.Entry(self.parameters_frame)
            self.style_entry(self.length_entry)
            self.length_entry.grid(row=0, column=1, padx=2, pady=2)

            ttk.Label(self.parameters_frame, text="Ширина:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
            self.width_entry = ttk.Entry(self.parameters_frame)
            self.style_entry(self.width_entry)
            self.width_entry.grid(row=1, column=1, padx=2, pady=2)
        elif figure == 'Треугольник':
            ttk.Label(self.parameters_frame, text="Основание:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
            self.base_entry = ttk.Entry(self.parameters_frame)
            self.style_entry(self.base_entry)
            self.base_entry.grid(row=0, column=1, padx=2, pady=2)

            ttk.Label(self.parameters_frame, text="Высота:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
            self.height_triangle_entry = ttk.Entry(self.parameters_frame)
            self.style_entry(self.height_triangle_entry)
            self.height_triangle_entry.grid(row=1, column=1, padx=2, pady=2)

    def calculate_geometry(self):
        figure = self.figure_var.get()
        try:
            if figure == 'Круг':
                radius = float(self.radius_entry.get())
                area = math.pi * radius ** 2
                self.geometry_result.config(text=f"Площадь круга: {area:.2f}")
            elif figure == 'Квадрат':
                side = float(self.side_entry.get())
                area = side ** 2
                self.geometry_result.config(text=f"Площадь квадрата: {area:.2f}")
            elif figure == 'Прямоугольник':
                length = float(self.length_entry.get())
                width = float(self.width_entry.get())
                area = length * width
                self.geometry_result.config(text=f"Площадь прямоугольника: {area:.2f}")
            elif figure == 'Треугольник':
                base = float(self.base_entry.get())
                height = float(self.height_triangle_entry.get())
                area = 0.5 * base * height
                self.geometry_result.config(text=f"Площадь треугольника: {area:.2f}")
        except ValueError:
            self.geometry_result.config(text="Ошибка ввода")

    def create_discount_tab(self):
        discount_tab = ttk.Frame(self.notebook)
        self.notebook.add(discount_tab, text='Скидки')

        frame = ttk.Frame(discount_tab)
        frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.discount_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.discount_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.amount_entry = ttk.Entry(input_frame)
        self.style_entry(self.amount_entry)
        self.amount_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(input_frame, text="Процент скидки:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.discount_entry = ttk.Entry(input_frame)
        self.style_entry(self.discount_entry)
        self.discount_entry.grid(row=1, column=1, padx=2, pady=2)

        ttk.Button(input_frame, text="Рассчитать скидку", style="Modern.TButton", command=self.calculate_discount).grid(
            row=2, column=0, columnspan=2, pady=5)

    def calculate_discount(self):
        try:
            amount = float(self.amount_entry.get())
            discount = float(self.discount_entry.get())
            final_amount = amount * (1 - discount / 100)
            self.discount_result.config(text=f"Сумма после скидки: {final_amount:.2f}")
        except ValueError:
            self.discount_result.config(text="Ошибка ввода")

    def create_age_tab(self):
        age_tab = ttk.Frame(self.notebook)
        self.notebook.add(age_tab, text='Возраст')

        frame = ttk.Frame(age_tab)
        frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.age_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.age_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Дата рождения (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.birthdate_entry = DateEntry(input_frame, width=20, font=("Arial", 14), date_pattern='dd.mm.yyyy')
        self.style_entry(self.birthdate_entry)
        self.birthdate_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Button(input_frame, text="Рассчитать возраст", style="Modern.TButton", command=self.calculate_age).grid(
            row=1, column=0, columnspan=2, pady=5)

    def calculate_age(self):
        try:
            birthdate_str = self.birthdate_entry.get()
            birthdate = datetime.strptime(birthdate_str, "%d.%m.%Y")
            today = datetime.now()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            self.age_result.config(text=f"Ваш возраст: {age} лет")
        except ValueError:
            self.age_result.config(text="Ошибка ввода")

    def create_graph_tab(self):
        graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(graph_tab, text='Графики')

        frame = ttk.Frame(graph_tab)
        frame.pack(padx=5, pady=5)

        ttk.Label(frame, text="Функция:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.function_entry = ttk.Entry(frame)
        self.style_entry(self.function_entry)
        self.function_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Button(frame, text="Построить график", style="Modern.TButton", command=self.plot_function).grid(row=1,
                                                                                                            column=0,
                                                                                                            columnspan=2,
                                                                                                            pady=5)

        self.figure = plt.Figure(figsize=(5, 3), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.figure, frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2)

    def plot_function(self):
        try:
            self.figure.clear()
            plot = self.figure.add_subplot(111)

            x = [i / 10 for i in range(-100, 101)]
            y = []
            expression = self.function_entry.get()
            # Заменяем символы степени на правильный синтаксис Python
            expression = expression.replace('^', '**')
            expression = expression.replace('x**2', '(x)**2')  # Исправляем x^2
            expression = expression.replace('x**3', '(x)**3')  # И другие степени

            def is_in_domain(x_val, expr):
                try:
                    if 'log(' in expr or 'ln(' in expr:
                        if x_val <= 0:
                            return False
                    if 'sqrt(' in expr:
                        # Проверяем аргумент sqrt
                        test_expr = expr.replace('x', str(x_val))
                        if 'sqrt(' in test_expr and x_val < 0:
                            return False
                    if 'tan(' in expr:
                        tan_val = math.tan(x_val)
                        if abs(tan_val) > 1e6:
                            return False
                    if '/' in expr:
                        try:
                            eval(expr.replace('x', str(x_val)), {'__builtins__': None}, self.get_math_globals())
                        except ZeroDivisionError:
                            return False
                    return True
                except:
                    return False

            for i in x:
                if is_in_domain(i, expression):
                    try:
                        # Создаем локальные переменные для вычисления
                        local_vars = self.get_math_globals()
                        local_vars['x'] = i
                        y_val = eval(expression, {'__builtins__': None}, local_vars)
                        y.append(y_val)
                    except:
                        y.append(None)
                else:
                    y.append(None)

            valid_points = [(xi, yi) for xi, yi in zip(x, y) if yi is not None]
            if not valid_points:
                raise ValueError("Нет допустимых точек для построения графика")
            x_valid, y_valid = zip(*valid_points)

            # Настройка фона графика
            self.figure.patch.set_facecolor('#2e2e2e')
            plot.set_facecolor('#2e2e2e')

            # Построение графика
            plot.plot(x_valid, y_valid, color='#4ecdc4', linewidth=2.5, label=f'y = {expression}')

            # Настройка детальной сетки
            plot.grid(True, which='major', linestyle='-', alpha=0.3, color='#666', linewidth=0.8)
            plot.grid(True, which='minor', linestyle=':', alpha=0.2, color='#555', linewidth=0.5)
            plot.minorticks_on()

            # Основные оси координат
            plot.axhline(0, color='white', linewidth=1.2, alpha=0.8)
            plot.axvline(0, color='white', linewidth=1.2, alpha=0.8)

            # Настройка меток и подписей
            plot.set_xlabel('x', fontsize=12, color='white', fontweight='bold')
            plot.set_ylabel('y', fontsize=12, color='white', fontweight='bold')
            plot.set_title(f'График функции: y = {expression}', fontsize=14, color='white', fontweight='bold', pad=15)

            # Настройка тиков и их цветов
            plot.tick_params(axis='both', which='major', colors='white', labelsize=10, length=6, width=1)
            plot.tick_params(axis='both', which='minor', colors='#888', length=3, width=0.5)

            # Добавление числовых обозначений на осях
            import numpy as np
            x_range = max(x_valid) - min(x_valid)
            y_range = max(y_valid) - min(y_valid)

            # Устанавливаем разумные пределы для осей
            x_margin = x_range * 0.05
            y_margin = y_range * 0.1
            plot.set_xlim(min(x_valid) - x_margin, max(x_valid) + x_margin)
            plot.set_ylim(min(y_valid) - y_margin, max(y_valid) + y_margin)

            # Устанавливаем тики для лучшей читаемости
            x_ticks = np.linspace(min(x_valid), max(x_valid), 11)
            y_ticks = np.linspace(min(y_valid), max(y_valid), 9)
            plot.set_xticks(x_ticks)
            plot.set_yticks(y_ticks)

            # Форматируем метки осей для лучшей читаемости
            plot.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}'))
            plot.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, p: f'{y:.1f}'))

            # Добавляем легенду
            plot.legend(loc='upper right', facecolor='#3e3e3e', edgecolor='white',
                        labelcolor='white', fontsize=10)

            # Убираем белые участки вокруг графика
            self.figure.tight_layout(pad=1.0)

            # Настройка границ графика
            for spine in plot.spines.values():
                spine.set_color('white')
                spine.set_linewidth(1)

            self.canvas.draw()
        except Exception as e:
            print(f"Ошибка: {e}")

    def create_trip_cost_tab(self):
        trip_cost_tab = ttk.Frame(self.notebook)
        self.notebook.add(trip_cost_tab, text='Стоимость поездки')

        frame = ttk.Frame(trip_cost_tab)
        frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.trip_cost_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.trip_cost_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Режим расчета:").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.trip_mode_var = tk.StringVar(value="По километрам")
        self.trip_mode_combobox = ttk.Combobox(input_frame, textvariable=self.trip_mode_var,
                                               values=("По километрам", "По координатам"))
        self.trip_mode_combobox.grid(row=0, column=1, padx=2, pady=2)
        self.trip_mode_combobox.bind("<<ComboboxSelected>>", self.on_trip_mode_select)

        self.trip_parameters_frame = ttk.Frame(input_frame)
        self.trip_parameters_frame.grid(row=1, column=0, columnspan=2, pady=2)

        ttk.Button(input_frame, text="Рассчитать стоимость", style="Modern.TButton",
                   command=self.calculate_trip_cost).grid(row=2, column=0, columnspan=2, pady=5)

        self.on_trip_mode_select(None)

    def on_trip_mode_select(self, event):
        for widget in self.trip_parameters_frame.winfo_children():
            widget.destroy()

        mode = self.trip_mode_var.get()
        if mode == "По километрам":
            ttk.Label(self.trip_parameters_frame, text="Расстояние (км):").grid(row=0, column=0, padx=2, pady=2,
                                                                                sticky="e")
            self.distance_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.distance_entry)
            self.distance_entry.grid(row=0, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Стоимость бензина (руб/л):").grid(row=1, column=0, padx=2,
                                                                                          pady=2, sticky="e")
            self.fuel_price_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.fuel_price_entry)
            self.fuel_price_entry.grid(row=1, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Расход топлива (л/100 км):").grid(row=2, column=0, padx=2,
                                                                                          pady=2, sticky="e")
            self.fuel_consumption_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.fuel_consumption_entry)
            self.fuel_consumption_entry.grid(row=2, column=1, padx=2, pady=2)
        else:
            ttk.Label(self.trip_parameters_frame, text="Широта начальной точки:").grid(row=0, column=0, padx=2, pady=2,
                                                                                       sticky="e")
            self.start_lat_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.start_lat_entry)
            self.start_lat_entry.grid(row=0, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Долгота начальной точки:").grid(row=1, column=0, padx=2, pady=2,
                                                                                        sticky="e")
            self.start_lon_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.start_lon_entry)
            self.start_lon_entry.grid(row=1, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Широта конечной точки:").grid(row=2, column=0, padx=2, pady=2,
                                                                                      sticky="e")
            self.end_lat_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.end_lat_entry)
            self.end_lat_entry.grid(row=2, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Долгота конечной точки:").grid(row=3, column=0, padx=2, pady=2,
                                                                                       sticky="e")
            self.end_lon_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.end_lon_entry)
            self.end_lon_entry.grid(row=3, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Стоимость бензина (руб/л):").grid(row=4, column=0, padx=2,
                                                                                          pady=2, sticky="e")
            self.fuel_price_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.fuel_price_entry)
            self.fuel_price_entry.grid(row=4, column=1, padx=2, pady=2)

            ttk.Label(self.trip_parameters_frame, text="Расход топлива (л/100 км):").grid(row=5, column=0, padx=2,
                                                                                          pady=2, sticky="e")
            self.fuel_consumption_entry = ttk.Entry(self.trip_parameters_frame)
            self.style_entry(self.fuel_consumption_entry)
            self.fuel_consumption_entry.grid(row=5, column=1, padx=2, pady=2)

    def calculate_distance(self, start_lat, start_lon, end_lat, end_lon):
        R = 6371
        lat1 = math.radians(start_lat)
        lon1 = math.radians(start_lon)
        lat2 = math.radians(end_lat)
        lon2 = math.radians(end_lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def calculate_trip_cost(self):
        try:
            mode = self.trip_mode_var.get()
            fuel_price = float(self.fuel_price_entry.get())
            fuel_consumption = float(self.fuel_consumption_entry.get())

            if fuel_price < 0 or fuel_consumption < 0:
                raise ValueError("Значения не могут быть отрицательными")

            if mode == "По километрам":
                distance = float(self.distance_entry.get())
                if distance < 0:
                    raise ValueError("Расстояние не может быть отрицательным")
            else:
                start_lat = float(self.start_lat_entry.get())
                start_lon = float(self.start_lon_entry.get())
                end_lat = float(self.end_lat_entry.get())
                end_lon = float(self.end_lon_entry.get())

                if not (-90 <= start_lat <= 90 and -90 <= end_lat <= 90):
                    raise ValueError("Широта должна быть от -90 до 90")
                if not (-180 <= start_lon <= 180 and -180 <= end_lon <= 180):
                    raise ValueError("Долгота должна быть от -180 до 180")

                distance = self.calculate_distance(start_lat, start_lon, end_lat, end_lon)

            fuel_consumption_per_km = fuel_consumption / 100
            total_cost = distance * fuel_consumption_per_km * fuel_price
            self.trip_cost_result.config(text=f"Стоимость поездки: {total_cost:.2f} руб")
        except ValueError as e:
            self.trip_cost_result.config(text=f"Ошибка: {str(e)}")

    def create_bill_split_tab(self):
        bill_split_tab = ttk.Frame(self.notebook)
        self.notebook.add(bill_split_tab, text='Дележ счета')

        frame = ttk.Frame(bill_split_tab)
        frame.pack(padx=5, pady=5, fill='x')

        # Полоса результата
        self.bill_split_result = ttk.Label(frame, text="", style="Result.TLabel")
        self.bill_split_result.pack(fill='x', pady=(0, 10))

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Общая сумма счета (руб):").grid(row=0, column=0, padx=2, pady=2, sticky="e")
        self.bill_amount_entry = ttk.Entry(input_frame)
        self.style_entry(self.bill_amount_entry)
        self.bill_amount_entry.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(input_frame, text="Количество человек:").grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.num_people_entry = ttk.Entry(input_frame)
        self.style_entry(self.num_people_entry)
        self.num_people_entry.grid(row=1, column=1, padx=2, pady=2)

        ttk.Button(input_frame, text="Рассчитать", style="Modern.TButton", command=self.calculate_bill_split).grid(
            row=2, column=0, columnspan=2, pady=5)

    def get_person_form(self, num):
        """Возвращает правильную форму слова 'человек' в зависимости от числа."""
        if num % 10 == 1 and num % 100 != 11:
            return "человек"
        elif 2 <= num % 10 <= 4 and (num % 100 < 10 or num % 100 >= 20):
            return "человека"
        else:
            return "человек"

    def calculate_bill_split(self):
        try:
            bill_amount = float(self.bill_amount_entry.get())
            num_people = int(self.num_people_entry.get())
            if bill_amount < 0:
                raise ValueError("Сумма счета не может быть отрицательной")
            if num_people < 2:
                raise ValueError("Количество человек должно быть не менее 2")

            bill_kopecks = int(bill_amount * 100)
            base_kopecks = bill_kopecks // num_people
            remainder_kopecks = bill_kopecks % num_people

            base_amount = base_kopecks / 100
            num_higher = remainder_kopecks
            num_lower = num_people - num_higher
            higher_amount = (base_kopecks + 1) / 100 if num_higher > 0 else base_amount

            person_form_lower = self.get_person_form(num_lower)
            person_form_higher = self.get_person_form(num_higher)

            if num_higher == 0:
                result_text = f"Каждый платит: {base_amount:.2f} руб"
            else:
                result_text = (f"{num_lower} {person_form_lower} платят по {base_amount:.2f} руб, "
                               f"{num_higher} {person_form_higher} платят по {higher_amount:.2f} руб")

            self.bill_split_result.config(text=result_text)
        except ValueError as e:
            self.bill_split_result.config(text=f"Ошибка: {str(e)}")

    def create_keyboard(self, parent):
        # Удаляем старые клавиатуры
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.notebook:
                widget.destroy()

        # Создаем основную рамку для клавиатуры
        main_keyboard_frame = ttk.Frame(parent)
        main_keyboard_frame.pack(side="bottom", fill="both", padx=10, pady=(5, 10))

        # Дополнительные кнопки для научного калькулятора и графиков (серые, выше основной клавиатуры)
        if self.current_tab in ["Научный", "Графики"]:
            extended_frame = ttk.Frame(main_keyboard_frame)
            extended_frame.pack(fill="x", pady=(0, 5))

            extended_buttons = [
                ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('π', 0, 3), ('e', 0, 4),
                ('log', 1, 0), ('ln', 1, 1), ('√', 1, 2), ('x', 1, 3), ('abs', 1, 4)
            ]

            for text, row, col in extended_buttons:
                btn = ttk.Button(extended_frame, text=text, style="Extended.TButton",
                                 command=lambda t=text: self.add_to_entry(t))
                btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew", ipadx=8, ipady=5)

            # Растягиваем колонки без пропусков
            for i in range(5):
                extended_frame.columnconfigure(i, weight=1)

        # Основная клавиатура
        keyboard_frame = ttk.Frame(main_keyboard_frame)
        keyboard_frame.pack(fill="both", expand=True)

        # Все кнопки основной клавиатуры
        all_buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3), ('C', 0, 4),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3), ('=', 1, 4),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3), ('+', 2, 4),
            ('0', 3, 0), ('.', 3, 1), ('^', 3, 2), ('(', 3, 3), (')', 3, 4)
        ]

        for text, row, col in all_buttons:
            # Определяем стиль кнопки
            if text in ['=', 'C']:
                style = "Teal.TButton"  # Бирюзовый для = и C
            else:
                style = "TButton"  # Все остальные кнопки одинакового цвета

            # Создаем кнопку с соответствующим действием
            if text == '=':
                btn = ttk.Button(keyboard_frame, text=text, style=style, command=self.equal_button_action)
            elif text == 'C':
                btn = ttk.Button(keyboard_frame, text=text, style=style, command=self.clear_entry)
            else:
                btn = ttk.Button(keyboard_frame, text=text, style=style,
                                 command=lambda t=text: self.add_to_entry(t))

            btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew", ipadx=10, ipady=8)

        # Растягиваем все колонки и строки без пропусков
        for i in range(5):
            keyboard_frame.columnconfigure(i, weight=1)
        for i in range(4):
            keyboard_frame.rowconfigure(i, weight=1)

    def add_to_entry(self, text):
        active_entry = self.get_active_entry()
        if active_entry:
            if text == '√':
                active_entry.insert(tk.INSERT, 'sqrt(')
            elif text == '^':
                active_entry.insert(tk.INSERT, '**')
            elif text == 'π':
                active_entry.insert(tk.INSERT, 'pi')
            elif text == 'x' and self.current_tab == "Графики":
                active_entry.insert(tk.INSERT, 'x')
            elif self.current_tab == "Дележ счета" and active_entry == self.num_people_entry and text == '.':
                return
            elif self.current_tab != "Возраст" or text in '0123456789.':
                active_entry.insert(tk.INSERT, text)

    def clear_entry(self):
        active_entry = self.get_active_entry()
        if active_entry:
            active_entry.delete(0, tk.END)

    def equal_button_action(self):
        tab = self.current_tab
        if tab == "Научный":
            self.calculate_expression()
        elif tab == "Графики":
            self.plot_function()
        elif tab == "ИМТ":
            self.calculate_bmi()
        elif tab == "Геометрия":
            self.calculate_geometry()
        elif tab == "Скидки":
            self.calculate_discount()
        elif tab == "Возраст":
            self.calculate_age()
        elif tab == "Стоимость поездки":
            self.calculate_trip_cost()
        elif tab == "Дележ счета":
            self.calculate_bill_split()
        else:
            self.calculate()

    def calculate(self):
        active_entry = self.get_active_entry()
        if not active_entry:
            return
        try:
            expression = active_entry.get()
            expression = expression.replace('²', '^2')
            expression = expression.replace('³', '^3')
            expression = expression.replace('^', '**')
            expression = expression.replace('√', 'sqrt')
            result = eval(expression, {'__builtins__': None}, self.get_math_globals())
            active_entry.delete(0, tk.END)
            active_entry.insert(tk.END, str(result))
        except Exception as e:
            active_entry.delete(0, tk.END)
            active_entry.insert(tk.END, f"Ошибка: {str(e)}")


def set_dark_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    dark_bg = "#2e2e2e"
    dark_fg = "#ffffff"
    accent = "#444"
    teal_color = "#4ecdc4"  # Бирюзовый цвет для кнопок = и C
    extended_color = "#95a5a6"  # Серый для расширенных функций
    modern_button_color = "#556B2F"  # Цвет для современных кнопок
    result_bg = "#1e1e1e"  # Темный фон для полос результатов

    root.configure(bg=dark_bg)

    # Основные стили
    style.configure("TFrame", background=dark_bg)
    style.configure("TLabel", background=dark_bg, foreground=dark_fg)
    style.configure("TNotebook", background=dark_bg)
    style.configure("TNotebook.Tab", background=accent, foreground=dark_fg)
    style.map("TNotebook.Tab",
              background=[("selected", "#555")],
              foreground=[("selected", "#fff")])

    # Стандартные кнопки (все цифры и операторы одного цвета)
    style.configure("TButton",
                    padding=8,
                    relief="flat",
                    background=accent,
                    foreground=dark_fg,
                    borderwidth=0,
                    focuscolor="none")
    style.map("TButton",
              background=[("active", "#5c5f61"), ("pressed", "#6c6f71")],
              relief=[("pressed", "sunken")])

    # Бирюзовые кнопки для = и C
    style.configure("Teal.TButton",
                    padding=8,
                    relief="flat",
                    background=teal_color,
                    foreground="#ffffff",
                    borderwidth=0,
                    focuscolor="none")
    style.map("Teal.TButton",
              background=[("active", "#26a69a"), ("pressed", "#00695c")],
              relief=[("pressed", "sunken")])

    # Серые кнопки для расширенных функций
    style.configure("Extended.TButton",
                    padding=6,
                    relief="flat",
                    background=extended_color,
                    foreground="#ffffff",
                    borderwidth=0,
                    focuscolor="none")
    style.map("Extended.TButton",
              background=[("active", "#7f8c8d"), ("pressed", "#34495e")],
              relief=[("pressed", "sunken")])

    # Современные кнопки с закругленными краями и градиентом
    style.configure("Modern.TButton",
                    padding=(15, 10),
                    relief="flat",
                    background=teal_color,
                    foreground="#ffffff",
                    borderwidth=0,
                    focuscolor="none",
                    font=("Arial", 11, "bold"))
    style.map("Modern.TButton",
              background=[("active", "#26a69a"), ("pressed", "#00695c")],
              relief=[("pressed", "flat")])

    # Поля ввода
    style.configure("TEntry",
                    fieldbackground=dark_bg,
                    foreground=dark_fg,
                    borderwidth=1,
                    insertcolor=dark_fg)

    # Стиль для полос результатов
    style.configure("Result.TLabel",
                    background=result_bg,
                    foreground="#4ecdc4",
                    font=("Arial", 12, "bold"),
                    padding=(10, 8),
                    relief="flat",
                    borderwidth=0,
                    anchor="center")


if __name__ == "__main__":
    root = tk.Tk()
    set_dark_theme(root)
    app = CalculatorApp(root)
    root.mainloop()
