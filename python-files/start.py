import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime, timedelta
import os
import re
import traceback

class TravelTimeAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор времени в пути")
        self.root.geometry("1400x800")  # Увеличил высоту для вкладок
        
        # Данные
        self.df = None
        self.travel_data = {}  # Теперь словарь: {объект: {день: данные}}
        self.objects = []  # Список уникальных объектов
        self.object_trees = {}  # Словарь для хранения деревьев каждого объекта
        self.object_models = {}  # Словарь для хранения моделей объектов
        
        # Время обеда в минутах
        self.LUNCH_BREAK_MINUTES = 90
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
    def setup_styles(self):
        """Настройка стилей для элементов интерфейса"""
        style = ttk.Style()
        
        # Настройка стиля для заголовков таблицы
        style.configure("Treeview.Heading", 
                      font=('Arial', 8, 'bold'),  # Шрифт, размер, жирность
                      padding=(5, 5))  # Внутренние отступы (вертикальный, горизонтальный)
        
        # Настройка стиля для ячеек таблицы
        style.configure("Treeview", 
                      font=('Arial', 9),
                      rowheight=25)  # Высота строк
        
        # Дополнительный стиль для увеличенных заголовков
        style.configure("LargeHeading.Treeview.Heading", 
                      font=('Arial', 9, 'bold'),
                      padding=(2, 40))
        
    def create_widgets(self):
        # Фрейм для загрузки файла
        file_frame = ttk.Frame(self.root, padding="10")
        file_frame.pack(fill=tk.X)
        
        ttk.Label(file_frame, text="Файл Excel:").pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Button(file_frame, text="Выбрать файл", command=self.select_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Анализировать", command=self.analyze_data).pack(side=tk.LEFT, padx=(5, 0))
        
        # Фрейм для результатов
        results_frame = ttk.Frame(self.root, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Общая статистика
        stats_frame = ttk.LabelFrame(results_frame, text="Общая статистика по всем объектам", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=6, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.X)
        
        # Создаем блокнот для вкладок по объектам
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки экспорта
        export_frame = ttk.Frame(self.root, padding="10")
        export_frame.pack(fill=tk.X)
        
        ttk.Button(export_frame, text="Экспорт в Excel", command=self.export_excel).pack(side=tk.LEFT)
        ttk.Button(export_frame, text="Экспорт статистики", command=self.export_stats).pack(side=tk.LEFT, padx=(10, 0))
        
    def create_object_tab(self, object_name, object_model):
        """Создание вкладки для конкретного объекта с указанием модели"""
        try:
            # Формируем название вкладки из объекта и модели
            tab_name = f"{object_name} ({object_model})"
            
            # Ограничиваем длину названия вкладки (максимум 50 символов)
            if len(tab_name) > 50:
                tab_name = tab_name[:47] + "..."
            
            # Создаем фрейм для вкладки
            tab_frame = ttk.Frame(self.notebook)
            
            # Создаем таблицу для этого объекта
            columns = ("Дата", "Смена", "Количество\nпоездок", "Общее\nвремя", "Общее\nрасстояние", 
                      "Средняя \nскорость", "Коэф. \nиспользования", "Коэф. хол.хода  \nво время простоя", 
                      "Общее \nвремя \nстоянки", "Время \nхол. хода",
                      "Первая \nпоездка", "Последняя \nпоездка")
            
            tree = ttk.Treeview(tab_frame, columns=columns, show="headings", height=15, style="LargeHeading.Treeview")
            
            # Настройка заголовков и ширины колонок
            column_widths = {
                "Дата": 100, 
                "Смена": 80,
                "Количество поездок": 100, 
                "Общее время": 100, 
                "Общее расстояние": 100, 
                "Ср. скорость": 90, 
                "Коэф. использования": 250,
                "Коэф. простоя": 100,
                "Общее время стоянки": 120,
                "Время хол. хода": 100,
                "Первая поездка": 100, 
                "Последняя поездка": 100
            }
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=column_widths.get(col, 100), anchor='center')
            
            # Скроллбар для таблицы
            scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Добавляем вкладку в блокнот
            self.notebook.add(tab_frame, text=tab_name)
            
            return tree
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании вкладки для объекта {object_name}: {str(e)}")
            return None
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def parse_datetime(self, date_str):
        """Парсинг даты и времени из строки"""
        try:
            return datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                return None
    
    def calculate_duration(self, start_time, end_time):
        """Расчет длительности между двумя временными точками"""
        if isinstance(start_time, str):
            start_time = self.parse_datetime(start_time)
        if isinstance(end_time, str):
            end_time = self.parse_datetime(end_time)
        
        if start_time and end_time:
            duration = end_time - start_time
            return duration
        return None
    
    def find_column(self, possible_names):
        """Поиск колонки по возможным названиям"""
        if self.df is None:
            return None
        
        for col in self.df.columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    return col
        return None
    
    def format_duration(self, duration):
        """Форматирование длительности в читаемый вид"""
        if duration is None:
            return "Н/Д"
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}м"
        elif minutes > 0:
            return f"{minutes}м"
        else:
            return f"{seconds}с"
    
    def parse_idle_time(self, idle_str):
        """Парсинг времени холостого хода из строки формата 'X ч. Y мин.' или 'Y мин.'"""
        if pd.isna(idle_str):
            return 0
        
        idle_str = str(idle_str)
        hours = 0
        minutes = 0
        
        # Ищем часы
        hours_match = re.search(r'(\d+)\s*ч', idle_str)
        if hours_match:
            hours = int(hours_match.group(1))
        
        # Ищем минуты
        minutes_match = re.search(r'(\d+)\s*мин', idle_str)
        if minutes_match:
            minutes = int(minutes_match.group(1))
        
        # Общее время в минутах
        total_minutes = hours * 60 + minutes
        return total_minutes
    
    def determine_shift(self, last_trip_time):
        """Определение смены по времени последней поездки"""
        if last_trip_time is None:
            return "Н/Д"
        
        if last_trip_time.hour < 17 or (last_trip_time.hour == 17 and last_trip_time.minute <= 30):
            return "до 17:00"
        else:
            return "до 20:00"
    
    def calculate_utilization_coefficient(self, total_duration, shift_type):
        """Расчет коэффициента использования"""
        if total_duration.total_seconds() == 0:
            return 0.0
        
        if shift_type == "до 17:00":
            shift_minutes = 450  # 7.5 часов * 60 минут
        else:
            shift_minutes = 630  # 10.5 часов * 60 минут
            
        used_minutes = total_duration.total_seconds() / 60
        coefficient = used_minutes / shift_minutes
        
        return coefficient
    
    def calculate_idle_coefficient(self, day_data):
        """
        Расчет коэффициента простоя = (время стоянки - обед) / холостой ход
        Время стоянки берется из фактических данных стоянок между поездками
        Холостой ход берется из колонки "Хол. ход" в данных
        """
        # Фактическое время стоянки из данных
        standing_time = day_data.get('total_standing_time', timedelta())
        
        # Вычитаем время обеда
        standing_time_without_lunch = standing_time - timedelta(minutes=self.LUNCH_BREAK_MINUTES)
        if standing_time_without_lunch.total_seconds() < 0:
            standing_time_without_lunch = timedelta(0)
        
        # Холостой ход из данных таблицы (суммируем за день)
        total_idle_run = day_data.get('total_idle_run', 0)
        
        # Коэффициент простоя
        if total_idle_run > 0:
            # Переводим время стоянки (без обеда) в минуты для соответствия единицам холостого хода
            standing_minutes = standing_time_without_lunch.total_seconds() / 60
            idle_coefficient =   total_idle_run / standing_minutes
        else:
            idle_coefficient = 0.0
        
        return idle_coefficient
    
    def analyze_data(self):
        try:
            if not self.file_path_var.get():
                messagebox.showerror("Ошибка", "Пожалуйста, выберите Excel файл")
                return
            
            # Загрузка данных - сначала попробуем найти правильную строку заголовков
            temp_df = pd.read_excel(self.file_path_var.get(), header=None)
            
            # Поиск строки с заголовков (ищем строку содержащую "№", "Объект", "Событие" и т.д.)
            header_row = None
            for i, row in temp_df.iterrows():
                row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)]).lower()
                if any(keyword in row_str for keyword in ['объект', 'событие', 'начало', 'конец', 'модель']):
                    header_row = i
                    break
            
            if header_row is None:
                messagebox.showerror("Ошибка", "Не удалось найти строку с заголовками")
                return
            
            # Загружаем данные с правильной строки заголовков
            self.df = pd.read_excel(self.file_path_var.get(), header=header_row)
            
            # Очистка предыдущих результатов
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            self.travel_data = {}
            self.objects = []
            self.object_trees = {}
            self.object_models = {}
            
            # Вывод информации о колонках для отладки
            print("Найденные колонки:", self.df.columns.tolist())
            
            # Проверка наличия необходимых колонок
            required_columns = ['Объект', 'Событие', 'Начало', 'Конец']
            missing_columns = []
            for col in required_columns:
                if not any(col.lower() in str(c).lower() for c in self.df.columns):
                    missing_columns.append(col)
            
            if missing_columns:
                messagebox.showerror("Ошибка", f"Отсутствуют необходимые колонки: {', '.join(missing_columns)}")
                return
            
            # Фильтрация движений и стоянок
            movements = self.df[self.df['Событие'].astype(str).str.contains('Движение', na=False)].copy()
            parkings = self.df[self.df['Событие'].astype(str).str.contains('Стоянка', na=False)].copy()
            
            if movements.empty:
                messagebox.showwarning("Предупреждение", "В файле не найдено данных о движении")
                return
            
            # Получаем уникальные объекты
            object_column = None
            for col in self.df.columns:
                if 'объект' in col.lower():
                    object_column = col
                    break
            
            if object_column is None:
                messagebox.showerror("Ошибка", "Не найдена колонка 'Объект'")
                return
            
            # Находим колонку с моделью объекта
            model_column = None
            for col in self.df.columns:
                if 'модель' in col.lower() and 'объекта' in col.lower():
                    model_column = col
                    break
            
            self.objects = movements[object_column].unique().tolist()
            
            # Создаем словарь соответствия объекта и его модели
            if model_column:
                for obj in self.objects:
                    # Находим первую запись для этого объекта
                    obj_rows = movements[movements[object_column] == obj]
                    if not obj_rows.empty:
                        model = str(obj_rows.iloc[0][model_column])
                        self.object_models[obj] = model
                    else:
                        self.object_models[obj] = ""
            else:
                # Если колонка с моделью не найдена, используем пустую строку
                for obj in self.objects:
                    self.object_models[obj] = ""
            
            # Группировка по объектам и дням
            for obj in self.objects:
                try:
                    # Инициализация данных для объекта
                    self.travel_data[obj] = {}
                    
                    # Фильтрация движений для текущего объекта
                    obj_movements = movements[movements[object_column] == obj].copy()
                    
                    # Фильтрация стоянок для текущего объекта
                    obj_parkings = parkings[parkings[object_column] == obj].copy()
                    
                    # Фильтрация только движений после 8:00
                    filtered_movements = []
                    for index, row in obj_movements.iterrows():
                        start_time = self.parse_datetime(str(row['Начало']))
                        if start_time and start_time.hour >= 8:
                            filtered_movements.append(row)
                    
                    if not filtered_movements:
                        print(f"Для объекта {obj} не найдено движений после 8:00")
                        continue
                    
                    # Группировка по дням для текущего объекта
                    for row in filtered_movements:
                        start_time = self.parse_datetime(str(row['Начало']))
                        end_time = self.parse_datetime(str(row['Конец']))
                        
                        if start_time and end_time:
                            date_key = start_time.date()
                            duration = self.calculate_duration(start_time, end_time)
                            
                            # Безопасное извлечение числовых значений
                            try:
                                distance = float(str(row.get('Пробег, км', 0)).replace(',', '.'))
                            except (ValueError, TypeError):
                                distance = 0
                            
                            try:
                                avg_speed = float(str(row.get('Ср. скорость, км/ч', 0)).replace(',', '.'))
                            except (ValueError, TypeError):
                                avg_speed = 0
                            
                            address = str(row.get('Адрес', ''))
                            
                            # Инициализация данных для дня если их еще нет
                            if date_key not in self.travel_data[obj]:
                                self.travel_data[obj][date_key] = {
                                    'trips': [],
                                    'total_duration': timedelta(),
                                    'total_distance': 0,
                                    'total_idle_run': 0,  # в минутах
                                    'total_standing_time': timedelta(),  # фактическое время стоянки
                                    'first_trip': None,
                                    'last_trip': None
                                }
                            
                            # Добавление поездки в день
                            trip_data = {
                                'start_time': start_time,
                                'end_time': end_time,
                                'duration': duration,
                                'distance': distance,
                                'avg_speed': avg_speed,
                                'address': address
                            }
                            
                            self.travel_data[obj][date_key]['trips'].append(trip_data)
                            self.travel_data[obj][date_key]['total_duration'] += duration
                            self.travel_data[obj][date_key]['total_distance'] += distance
                            
                            # Определение первой и последней поездки дня
                            if self.travel_data[obj][date_key]['first_trip'] is None or start_time < self.travel_data[obj][date_key]['first_trip']:
                                self.travel_data[obj][date_key]['first_trip'] = start_time
                            
                            if self.travel_data[obj][date_key]['last_trip'] is None or end_time > self.travel_data[obj][date_key]['last_trip']:
                                self.travel_data[obj][date_key]['last_trip'] = end_time
                    
                    # Обработка стоянок для расчета времени стоянки и холостого хода
                    for date_key in self.travel_data[obj].keys():
                        day_data = self.travel_data[obj][date_key]
                        if day_data['first_trip'] and day_data['last_trip']:
                            # Фильтрация стоянок в рабочее время для этого дня
                            for index, parking_row in obj_parkings.iterrows():
                                parking_start = self.parse_datetime(str(parking_row['Начало']))
                                parking_end = self.parse_datetime(str(parking_row['Конец']))
                                
                                if (parking_start and parking_end and 
                                    parking_start.date() == date_key and
                                    parking_start >= day_data['first_trip'] and 
                                    parking_end <= day_data['last_trip']):
                                    
                                    # Добавляем время стоянки (фактическая длительность из данных)
                                    parking_duration = self.calculate_duration(parking_start, parking_end)
                                    if parking_duration:
                                        day_data['total_standing_time'] += parking_duration
                                    
                                    # Парсим время холостого хода
                                    idle_run = self.parse_idle_time(parking_row.get('Хол. ход', 0))
                                    day_data['total_idle_run'] += idle_run
                
                except Exception as e:
                    print(f"Ошибка при обработке объекта {obj}: {str(e)}")
                    traceback.print_exc()
                    continue
            
            # Создаем вкладки для каждого объекта
            for obj in self.objects:
                if obj in self.travel_data and self.travel_data[obj]:  # Проверяем, что есть данные для объекта
                    # Получаем модель объекта
                    obj_model = self.object_models.get(obj, "")
                    tree = self.create_object_tab(obj, obj_model)
                    if tree is not None:
                        self.object_trees[obj] = tree
                        
                        # Заполняем таблицу для этого объекта
                        for date_key in sorted(self.travel_data[obj].keys()):
                            try:
                                day_data = self.travel_data[obj][date_key]
                                trip_count = len(day_data['trips'])
                                day_duration = day_data['total_duration']
                                day_distance = day_data['total_distance']
                                
                                # Определение смены
                                shift_type = self.determine_shift(day_data['last_trip'])
                                
                                # Расчет коэффициента использования
                                utilization_coef = self.calculate_utilization_coefficient(day_duration, shift_type)
                                
                                # Расчет коэффициента простоя (с учетом вычета обеда)
                                idle_coef = self.calculate_idle_coefficient(day_data)
                                
                                # Средняя скорость за день
                                if day_duration.total_seconds() > 0:
                                    day_avg_speed = day_distance / (day_duration.total_seconds() / 3600)
                                else:
                                    day_avg_speed = 0
                                
                                # Рассчитываем время стоянки без учета обеда
                                standing_time_without_lunch = day_data['total_standing_time'] - timedelta(minutes=self.LUNCH_BREAK_MINUTES)
                                if standing_time_without_lunch.total_seconds() < 0:
                                    standing_time_without_lunch = timedelta(0)
                                
                                # Форматируем время стоянки в минутах (без обеда)
                                standing_time_minutes = int(standing_time_without_lunch.total_seconds() / 60)
                                idle_time_str = f"{day_data['total_idle_run']} мин"
                                
                                tree.insert('', 'end', values=(
                                    date_key.strftime("%d.%m.%Y"),
                                    shift_type,
                                    trip_count,
                                    self.format_duration(day_duration),
                                    f"{day_distance:.2f} км",
                                    f"{day_avg_speed:.1f} км/ч",
                                    f"{utilization_coef:.2f}",
                                    f"{idle_coef:.2f}",
                                    f"{standing_time_minutes} мин",
                                    idle_time_str,
                                    day_data['first_trip'].strftime("%H:%M") if day_data['first_trip'] else "",
                                    day_data['last_trip'].strftime("%H:%M") if day_data['last_trip'] else ""
                                ))
                            except Exception as e:
                                print(f"Ошибка при добавлении данных для {obj} на {date_key}: {str(e)}")
                                continue
            
            # Обновление общей статистики
            self.update_overall_statistics()
            
            if not self.travel_data:
                messagebox.showwarning("Предупреждение", "В файле не найдено данных о движениях после 8:00")
            
        except Exception as e:
            error_msg = f"Ошибка при обработке файла: {str(e)}\n\nПодробности:\n{traceback.format_exc()}"
            messagebox.showerror("Ошибка", error_msg)
            print(error_msg)
    
    def update_overall_statistics(self):
        """Обновление общей статистики по всем объектам"""
        try:
            total_objects = len(self.travel_data)
            total_days = 0
            total_trips = 0
            total_distance = 0
            total_duration = timedelta()
            
            for obj_data in self.travel_data.values():
                total_days += len(obj_data)
                for day_data in obj_data.values():
                    total_trips += len(day_data['trips'])
                    total_distance += day_data['total_distance']
                    total_duration += day_data['total_duration']
            
            avg_trips_per_day = total_trips / total_days if total_days > 0 else 0
            avg_duration_per_day = total_duration / total_days if total_days > 0 else timedelta()
            avg_distance_per_day = total_distance / total_days if total_days > 0 else 0
            
            stats_text = f"""Фильтр: движения после 8:00 утра
Время обеда: {self.LUNCH_BREAK_MINUTES} минут
Всего объектов: {total_objects}
Всего дней с поездками: {total_days}
Всего поездок: {total_trips}
Общее время в пути: {self.format_duration(total_duration)}
Общее расстояние: {total_distance:.2f} км
Средние показатели за день:
  Поездок в день: {avg_trips_per_day:.1f}
  Время в пути в день: {self.format_duration(avg_duration_per_day)}
  Расстояние в день: {avg_distance_per_day:.2f} км
Общие средние показатели:
  Время поездки: {self.format_duration(total_duration / total_trips if total_trips > 0 else timedelta())}
  Расстояние поездки: {total_distance / total_trips if total_trips > 0 else 0:.2f} км
  Скорость: {total_distance / (total_duration.total_seconds() / 3600) if total_duration.total_seconds() > 0 else 0:.1f} км/ч"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {str(e)}")
            traceback.print_exc()
    
    def export_excel(self):
        """Экспорт данных в Excel с форматированием"""
        try:
            if not self.travel_data:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Сохранить Excel файл",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path:
                # Создание Excel файла с форматированием
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Создаем лист для каждого объекта
                    for obj, obj_data in self.travel_data.items():
                        export_data = []
                        
                        for date_key, day_data in obj_data.items():
                            shift_type = self.determine_shift(day_data['last_trip'])
                            utilization_coef = self.calculate_utilization_coefficient(day_data['total_duration'], shift_type)
                            idle_coef = self.calculate_idle_coefficient(day_data)
                            
                            day_avg_speed = day_data['total_distance'] / (day_data['total_duration'].total_seconds() / 3600) if day_data['total_duration'].total_seconds() > 0 else 0
                            
                            # Рассчитываем время стоянки без учета обеда
                            standing_time_without_lunch = day_data['total_standing_time'] - timedelta(minutes=self.LUNCH_BREAK_MINUTES)
                            if standing_time_without_lunch.total_seconds() < 0:
                                standing_time_without_lunch = timedelta(0)
                            
                            export_data.append({
                                'Дата': date_key.strftime("%d.%m.%Y"),
                                'Смена': shift_type,
                                'Количество поездок': len(day_data['trips']),
                                'Общее время (мин)': round(day_data['total_duration'].total_seconds() / 60, 1),
                                'Общее время': self.format_duration(day_data['total_duration']),
                                'Общее расстояние (км)': round(day_data['total_distance'], 2),
                                'Средняя скорость (км/ч)': round(day_avg_speed, 1),
                                'Коэффициент использования': round(utilization_coef, 3),
                                'Коэффициент простоя': round(idle_coef, 3),
                                'Общее время стоянки (мин)': round(standing_time_without_lunch.total_seconds() / 60, 1),
                                'Время хол. хода (мин)': day_data['total_idle_run'],
                                'Первая поездка': day_data['first_trip'].strftime("%H:%M") if day_data['first_trip'] else "",
                                'Последняя поездка': day_data['last_trip'].strftime("%H:%M") if day_data['last_trip'] else ""
                            })
                        
                        # Формируем имя листа
                        obj_model = self.object_models.get(obj, "")
                        sheet_name = f"{obj} ({obj_model})"
                        # Ограничиваем длину имени листа (максимум 31 символ)
                        if len(sheet_name) > 31:
                            sheet_name = sheet_name[:28] + "..."
                        
                        # Экспорт данных объекта
                        export_df = pd.DataFrame(export_data)
                        export_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Форматирование листа
                        worksheet = writer.sheets[sheet_name]
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    # Создание листа со сводной статистикой
                    stats_data = []
                    total_duration = timedelta()
                    total_distance = 0
                    total_trips = 0
                    total_days = 0
                    total_standing_time = timedelta()
                    total_idle_run = 0
                    
                    for obj_data in self.travel_data.values():
                        for day_data in obj_data.values():
                            total_duration += day_data['total_duration']
                            total_distance += day_data['total_distance']
                            total_trips += len(day_data['trips'])
                            total_standing_time += day_data['total_standing_time']
                            total_idle_run += day_data['total_idle_run']
                        total_days += len(obj_data)
                    
                    # Рассчитываем общее время стоянки без учета обедов
                    total_standing_time_without_lunch = total_standing_time - timedelta(minutes=self.LUNCH_BREAK_MINUTES * total_days)
                    if total_standing_time_without_lunch.total_seconds() < 0:
                        total_standing_time_without_lunch = timedelta(0)
                    
                    stats_data.append(['Показатель', 'Значение'])
                    stats_data.append(['Время обеда (мин)', self.LUNCH_BREAK_MINUTES])
                    stats_data.append(['Всего объектов', len(self.travel_data)])
                    stats_data.append(['Всего дней с поездками', total_days])
                    stats_data.append(['Всего поездок', total_trips])
                    stats_data.append(['Общее время в пути (мин)', round(total_duration.total_seconds() / 60, 1)])
                    stats_data.append(['Общее расстояние (км)', round(total_distance, 2)])
                    stats_data.append(['Общее время стоянки (мин)', round(total_standing_time_without_lunch.total_seconds() / 60, 1)])
                    stats_data.append(['Общее время хол. хода (мин)', total_idle_run])
                    stats_data.append(['Средние поездок в день', round(total_trips / total_days if total_days > 0 else 0, 1)])
                    stats_data.append(['Среднее время в пути в день (мин)', round(total_duration.total_seconds() / 60 / total_days if total_days > 0 else 0, 1)])
                    stats_data.append(['Среднее расстояние в день (км)', round(total_distance / total_days if total_days > 0 else 0, 2)])
                    stats_data.append(['Среднее время поездки (мин)', round(total_duration.total_seconds() / 60 / total_trips if total_trips > 0 else 0, 1)])
                    stats_data.append(['Среднее расстояние поездки (км)', round(total_distance / total_trips if total_trips > 0 else 0, 2)])
                    stats_data.append(['Средняя скорость (км/ч)', round(total_distance / (total_duration.total_seconds() / 3600) if total_duration.total_seconds() > 0 else 0, 1)])
                    
                    stats_df = pd.DataFrame(stats_data[1:], columns=stats_data[0])
                    stats_df.to_excel(writer, sheet_name='Сводная статистика', index=False)
                    
                    # Форматирование листа статистики
                    stats_worksheet = writer.sheets['Сводная статистика']
                    for column in stats_worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        stats_worksheet.column_dimensions[column_letter].width = adjusted_width
                
                messagebox.showinfo("Успех", f"Данные экспортированы в Excel файл:\n{file_path}")
                
        except Exception as e:
            error_msg = f"Ошибка при экспорте в Excel: {str(e)}\n\nПодробности:\n{traceback.format_exc()}"
            messagebox.showerror("Ошибка", error_msg)
            print(error_msg)
    
    def export_stats(self):
        """Экспорт статистики в текстовый файл"""
        try:
            if not self.travel_data:
                messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Сохранить статистику",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("СТАТИСТИКА ВРЕМЕНИ В ПУТИ ПО ДНЯМ (движения после 8:00)\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Время обеда: {self.LUNCH_BREAK_MINUTES} минут\n")
                    f.write(self.stats_text.get(1.0, tk.END))
                    
                    # Детальные данные по каждому объекту
                    for obj, obj_data in self.travel_data.items():
                        obj_model = self.object_models.get(obj, "")
                        f.write(f"\n\nОБЪЕКТ: {obj} ({obj_model})\n")
                        f.write("=" * 60 + "\n\n")
                        
                        for date_key in sorted(obj_data.keys()):
                            day_data = obj_data[date_key]
                            shift_type = self.determine_shift(day_data['last_trip'])
                            utilization_coef = self.calculate_utilization_coefficient(day_data['total_duration'], shift_type)
                            idle_coef = self.calculate_idle_coefficient(day_data)
                            
                            # Рассчитываем время стоянки без учета обеда
                            standing_time_without_lunch = day_data['total_standing_time'] - timedelta(minutes=self.LUNCH_BREAK_MINUTES)
                            if standing_time_without_lunch.total_seconds() < 0:
                                standing_time_without_lunch = timedelta(0)
                            
                            standing_time_minutes = int(standing_time_without_lunch.total_seconds() / 60)
                            
                            f.write(f"ДАТА: {date_key.strftime('%d.%m.%Y')}\n")
                            f.write(f"Смена: {shift_type}\n")
                            f.write(f"Количество поездок: {len(day_data['trips'])}\n")
                            f.write(f"Общее время в пути: {self.format_duration(day_data['total_duration'])}\n")
                            f.write(f"Общее расстояние: {day_data['total_distance']:.2f} км\n")
                            f.write(f"Общее время стоянки (без учета обеда): {standing_time_minutes} мин\n")
                            f.write(f"Время хол. хода: {day_data['total_idle_run']} мин\n")
                            f.write(f"Коэффициент использования: {utilization_coef:.3f}\n")
                            f.write(f"Коэффициент простоя: {idle_coef:.3f}\n")
                            f.write(f"Первая поездка: {day_data['first_trip'].strftime('%H:%M') if day_data['first_trip'] else 'Н/Д'}\n")
                            f.write(f"Последняя поездка: {day_data['last_trip'].strftime('%H:%M') if day_data['last_trip'] else 'Н/Д'}\n")
                            
                            f.write("\nПоездки:\n")
                            for i, trip in enumerate(day_data['trips'], 1):
                                f.write(f"  #{i}: {trip['start_time'].strftime('%H:%M')}-{trip['end_time'].strftime('%H:%M')} ")
                                f.write(f"({self.format_duration(trip['duration'])}, {trip['distance']:.2f}км, {trip['avg_speed']:.1f}км/ч)\n")
                            f.write("\n" + "-" * 50 + "\n\n")
                
                messagebox.showinfo("Успех", f"Статистика экспортирована в {file_path}")
                
        except Exception as e:
            error_msg = f"Ошибка при экспорте статистики: {str(e)}\n\nПодробности:\n{traceback.format_exc()}"
            messagebox.showerror("Ошибка", error_msg)
            print(error_msg)

def main():
    root = tk.Tk()
    app = TravelTimeAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()