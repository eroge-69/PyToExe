import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector, Button, RadioButtons
from matplotlib.patches import Rectangle
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from scipy.optimize import curve_fit
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class VoltammetryAnalyzer:
    def __init__(self):
        self.data = None
        self.voltage = None
        self.disk_current = None
        self.ring_current = None
        
        # Выделенные области
        self.disk_background_range = None
        self.disk_plateau_range = None
        self.ring_background_range = None
        self.ring_plateau_range = None
        
        # Модели фона
        self.disk_bg_model = None
        self.ring_bg_model = None
        
        # Скорректированные данные
        self.disk_current_corrected = None
        self.ring_current_corrected = None
        
        # Результаты
        self.results = {}
        
        # Настройки
        self.current_dataset = 'disk'  # 'disk' или 'ring'
        self.selection_mode = 'background'  # 'background' или 'plateau'
        self.model_type = 'linear'  # 'linear' или 'polynomial'
        self.polynomial_degree = 2
        
        self.setup_gui()
        
    def setup_gui(self):
        """Создание графического интерфейса"""
        self.root = tk.Tk()
        self.root.title("Анализатор вольтамперограмм")
        self.root.geometry("1400x800")
        
        # Главная рамка
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Кнопки загрузки данных
        data_frame = ttk.LabelFrame(control_frame, text="Данные", padding=5)
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(data_frame, text="Загрузить файл", 
                  command=self.load_data).pack(fill=tk.X, pady=2)
        ttk.Button(data_frame, text="Тестовые данные", 
                  command=self.generate_test_data).pack(fill=tk.X, pady=2)
        
        # Настройки анализа
        settings_frame = ttk.LabelFrame(control_frame, text="Настройки", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор датасета
        ttk.Label(settings_frame, text="Активный датасет:").pack(anchor=tk.W)
        self.dataset_var = tk.StringVar(value='disk')
        dataset_combo = ttk.Combobox(settings_frame, textvariable=self.dataset_var,
                                   values=['disk', 'ring'], state='readonly')
        dataset_combo.pack(fill=tk.X, pady=2)
        dataset_combo.bind('<<ComboboxSelected>>', self.on_dataset_change)
        
        # Режим выделения
        ttk.Label(settings_frame, text="Режим выделения:").pack(anchor=tk.W, pady=(10, 0))
        self.mode_var = tk.StringVar(value='background')
        mode_combo = ttk.Combobox(settings_frame, textvariable=self.mode_var,
                                values=['background', 'plateau'], state='readonly')
        mode_combo.pack(fill=tk.X, pady=2)
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # Тип модели
        ttk.Label(settings_frame, text="Модель фона:").pack(anchor=tk.W, pady=(10, 0))
        self.model_var = tk.StringVar(value='linear')
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var,
                                 values=['linear', 'polynomial'], state='readonly')
        model_combo.pack(fill=tk.X, pady=2)
        model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Степень полинома
        ttk.Label(settings_frame, text="Степень полинома:").pack(anchor=tk.W, pady=(10, 0))
        self.degree_var = tk.StringVar(value='2')
        degree_combo = ttk.Combobox(settings_frame, textvariable=self.degree_var,
                                  values=['2', '3'], state='readonly')
        degree_combo.pack(fill=tk.X, pady=2)
        degree_combo.bind('<<ComboboxSelected>>', self.on_degree_change)
        
        # Кнопки обработки
        process_frame = ttk.LabelFrame(control_frame, text="Обработка", padding=5)
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(process_frame, text="Коррекция фона", 
                  command=self.correct_background).pack(fill=tk.X, pady=2)
        ttk.Button(process_frame, text="Измерить плато", 
                  command=self.measure_plateau).pack(fill=tk.X, pady=2)
        ttk.Button(process_frame, text="Сохранить результаты", 
                  command=self.save_results).pack(fill=tk.X, pady=2)
        
        # Статус выделений
        status_frame = ttk.LabelFrame(control_frame, text="Статус", padding=5)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_labels = {}
        for name in ['Диск фон', 'Диск плато', 'Кольцо фон', 'Кольцо плато']:
            frame = ttk.Frame(status_frame)
            frame.pack(fill=tk.X, pady=1)
            ttk.Label(frame, text=f"{name}:").pack(side=tk.LEFT)
            label = ttk.Label(frame, text="✗", foreground='red')
            label.pack(side=tk.RIGHT)
            self.status_labels[name] = label
        
        # Результаты
        self.results_frame = ttk.LabelFrame(control_frame, text="Результаты", padding=5)
        self.results_frame.pack(fill=tk.X, expand=True)
        
        # Правая панель с графиком
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_plot()
        
    def setup_plot(self):
        """Настройка matplotlib графика"""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.subplots_adjust(bottom=0.15)
        
        # Встраивание в tkinter
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()
        
        # Селектор для выделения областей
        self.span_selector = SpanSelector(
            self.ax, self.on_select, 'horizontal',
            useblit=True, props=dict(alpha=0.3, facecolor='red')
        )
        
    def generate_test_data(self):
        """Генерация тестовых данных"""
        voltage = np.linspace(-0.2, 1.0, 200)
        
        # Диск: ступенчатая функция с дрифтом
        disk_bg = 0.1 * voltage + 0.02 * np.sin(voltage * 10)
        disk_signal = np.where(voltage > 0.5, 2.0, 0)
        disk_noise = 0.05 * np.random.randn(len(voltage))
        disk_current = disk_bg + disk_signal + disk_noise
        
        # Кольцо: другая ступенчатая функция
        ring_bg = -0.05 * voltage + 0.01 * np.cos(voltage * 15)
        ring_signal = np.where(voltage > 0.3, -1.5, 0)
        ring_noise = 0.03 * np.random.randn(len(voltage))
        ring_current = ring_bg + ring_signal + ring_noise
        
        self.data = pd.DataFrame({
            'voltage': voltage,
            'disk_current': disk_current,
            'ring_current': ring_current
        })
        
        self.voltage = voltage
        self.disk_current = disk_current
        self.ring_current = ring_current
        
        self.plot_data()
        messagebox.showinfo("Успех", "Тестовые данные загружены")
        
    def load_data(self):
        """Загрузка данных из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Пробуем разные разделители
            for sep in [',', ';', '\t']:
                try:
                    data = pd.read_csv(file_path, sep=sep)
                    if data.shape[1] >= 3:
                        break
                except:
                    continue
            
            # Проверяем количество колонок
            if data.shape[1] < 3:
                messagebox.showerror("Ошибка", 
                    "Файл должен содержать минимум 3 колонки: напряжение, ток диска, ток кольца")
                return
            
            # Назначаем колонки
            columns = data.columns.tolist()
            self.voltage = data.iloc[:, 0].values
            self.disk_current = data.iloc[:, 1].values
            self.ring_current = data.iloc[:, 2].values
            
            self.data = pd.DataFrame({
                'voltage': self.voltage,
                'disk_current': self.disk_current,
                'ring_current': self.ring_current
            })
            
            self.plot_data()
            messagebox.showinfo("Успех", f"Данные загружены: {len(self.data)} точек")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def plot_data(self):
        """Построение графика"""
        if self.data is None:
            return
            
        self.ax.clear()
        
        # Выбираем данные для отображения
        if self.current_dataset == 'disk':
            current = self.disk_current_corrected if self.disk_current_corrected is not None else self.disk_current
            color = 'blue'
            label = 'Диск'
        else:
            current = self.ring_current_corrected if self.ring_current_corrected is not None else self.ring_current
            color = 'red'
            label = 'Кольцо'
        
        self.ax.plot(self.voltage, current, color=color, linewidth=2, label=label)
        
        # Отображение выделенных областей
        self.highlight_selections()
        
        self.ax.set_xlabel('Напряжение, В')
        self.ax.set_ylabel('Ток, мкА')
        self.ax.set_title(f'Вольтамперограмма - {label} ({self.selection_mode})')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        self.canvas.draw()
        
    def highlight_selections(self):
        """Подсветка выделенных областей"""
        if self.current_dataset == 'disk':
            bg_range = self.disk_background_range
            plateau_range = self.disk_plateau_range
        else:
            bg_range = self.ring_background_range
            plateau_range = self.ring_plateau_range
            
        if bg_range:
            self.ax.axvspan(bg_range[0], bg_range[1], alpha=0.2, color='green', label='Фон')
            
        if plateau_range:
            self.ax.axvspan(plateau_range[0], plateau_range[1], alpha=0.2, color='orange', label='Плато')
    
    def on_select(self, vmin, vmax):
        """Обработка выделения области"""
        if self.data is None:
            return
            
        # Сохраняем выделенную область
        selection = (vmin, vmax)
        
        if self.current_dataset == 'disk':
            if self.selection_mode == 'background':
                self.disk_background_range = selection
                self.status_labels['Диск фон'].config(text="✓", foreground='green')
            else:
                self.disk_plateau_range = selection
                self.status_labels['Диск плато'].config(text="✓", foreground='green')
        else:
            if self.selection_mode == 'background':
                self.ring_background_range = selection
                self.status_labels['Кольцо фон'].config(text="✓", foreground='green')
            else:
                self.ring_plateau_range = selection
                self.status_labels['Кольцо плато'].config(text="✓", foreground='green')
        
        self.plot_data()
        print(f"Выделена область {self.selection_mode} для {self.current_dataset}: {vmin:.3f} - {vmax:.3f} В")
    
    def on_dataset_change(self, event=None):
        """Смена активного датасета"""
        self.current_dataset = self.dataset_var.get()
        self.plot_data()
        
    def on_mode_change(self, event=None):
        """Смена режима выделения"""
        self.selection_mode = self.mode_var.get()
        self.plot_data()
        
    def on_model_change(self, event=None):
        """Смена типа модели"""
        self.model_type = self.model_var.get()
        
    def on_degree_change(self, event=None):
        """Смена степени полинома"""
        self.polynomial_degree = int(self.degree_var.get())
    
    def get_region_data(self, voltage_range, dataset='disk'):
        """Получение данных в выделенной области"""
        if voltage_range is None:
            return None, None
            
        mask = (self.voltage >= voltage_range[0]) & (self.voltage <= voltage_range[1])
        x = self.voltage[mask]
        
        if dataset == 'disk':
            y = self.disk_current[mask]
        else:
            y = self.ring_current[mask]
            
        return x, y
    
    def fit_background_model(self, x, y):
        """Подгонка модели фона"""
        if len(x) < 2:
            return None
            
        if self.model_type == 'linear':
            # Линейная регрессия
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            return {
                'type': 'linear',
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2
            }
        else:
            # Полиномиальная регрессия
            try:
                coeffs = np.polyfit(x, y, self.polynomial_degree)
                return {
                    'type': 'polynomial',
                    'coefficients': coeffs,
                    'degree': self.polynomial_degree
                }
            except:
                # Fallback на линейную модель
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                return {
                    'type': 'linear',
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value**2
                }
    
    def evaluate_background_model(self, model, voltage):
        """Вычисление фонового тока по модели"""
        if model is None:
            return np.zeros_like(voltage)
            
        if model['type'] == 'linear':
            return model['slope'] * voltage + model['intercept']
        else:
            return np.polyval(model['coefficients'], voltage)
    
    def correct_background(self):
        """Коррекция фонового тока"""
        if self.data is None:
            messagebox.showerror("Ошибка", "Сначала загрузите данные")
            return
            
        # Проверяем наличие выделенных областей фона
        if self.disk_background_range is None or self.ring_background_range is None:
            messagebox.showerror("Ошибка", 
                "Выделите области фона для диска и кольца")
            return
        
        try:
            # Подгонка модели для диска
            disk_bg_x, disk_bg_y = self.get_region_data(self.disk_background_range, 'disk')
            self.disk_bg_model = self.fit_background_model(disk_bg_x, disk_bg_y)
            
            # Подгонка модели для кольца
            ring_bg_x, ring_bg_y = self.get_region_data(self.ring_background_range, 'ring')
            self.ring_bg_model = self.fit_background_model(ring_bg_x, ring_bg_y)
            
            # Коррекция данных
            disk_bg_corrected = self.evaluate_background_model(self.disk_bg_model, self.voltage)
            ring_bg_corrected = self.evaluate_background_model(self.ring_bg_model, self.voltage)
            
            self.disk_current_corrected = self.disk_current - disk_bg_corrected
            self.ring_current_corrected = self.ring_current - ring_bg_corrected
            
            self.plot_data()
            messagebox.showinfo("Успех", "Фоновый ток скорректирован")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при коррекции фона: {str(e)}")
    
    def measure_plateau(self):
        """Измерение высоты плато"""
        if self.disk_current_corrected is None or self.ring_current_corrected is None:
            messagebox.showerror("Ошибка", "Сначала выполните коррекцию фона")
            return
            
        if self.disk_plateau_range is None or self.ring_plateau_range is None:
            messagebox.showerror("Ошибка", 
                "Выделите области плато для диска и кольца")
            return
        
        try:
            # Измерение плато диска
            disk_mask = ((self.voltage >= self.disk_plateau_range[0]) & 
                        (self.voltage <= self.disk_plateau_range[1]))
            disk_plateau_values = self.disk_current_corrected[disk_mask]
            
            disk_height = np.mean(disk_plateau_values)
            disk_std = np.std(disk_plateau_values)
            
            # Измерение плато кольца
            ring_mask = ((self.voltage >= self.ring_plateau_range[0]) & 
                        (self.voltage <= self.ring_plateau_range[1]))
            ring_plateau_values = self.ring_current_corrected[ring_mask]
            
            ring_height = np.mean(ring_plateau_values)
            ring_std = np.std(ring_plateau_values)
            
            # Эффективность сбора
            collection_efficiency = abs(ring_height / disk_height) if disk_height != 0 else 0
            
            self.results = {
                'disk_plateau_height': disk_height,
                'disk_plateau_std': disk_std,
                'ring_plateau_height': ring_height,
                'ring_plateau_std': ring_std,
                'collection_efficiency': collection_efficiency,
                'disk_plateau_points': len(disk_plateau_values),
                'ring_plateau_points': len(ring_plateau_values)
            }
            
            self.display_results()
            messagebox.showinfo("Успех", "Измерения плато выполнены")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при измерении плато: {str(e)}")
    
    def display_results(self):
        """Отображение результатов"""
        # Очищаем предыдущие результаты
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not self.results:
            return
            
        # Результаты для диска
        disk_frame = ttk.LabelFrame(self.results_frame, text="Диск", padding=5)
        disk_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(disk_frame, text=f"Высота: {self.results['disk_plateau_height']:.6f} мкА").pack(anchor=tk.W)
        ttk.Label(disk_frame, text=f"Ст.откл: {self.results['disk_plateau_std']:.6f} мкА").pack(anchor=tk.W)
        ttk.Label(disk_frame, text=f"Точек: {self.results['disk_plateau_points']}").pack(anchor=tk.W)
        
        # Результаты для кольца
        ring_frame = ttk.LabelFrame(self.results_frame, text="Кольцо", padding=5)
        ring_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(ring_frame, text=f"Высота: {self.results['ring_plateau_height']:.6f} мкА").pack(anchor=tk.W)
        ttk.Label(ring_frame, text=f"Ст.откл: {self.results['ring_plateau_std']:.6f} мкА").pack(anchor=tk.W)
        ttk.Label(ring_frame, text=f"Точек: {self.results['ring_plateau_points']}").pack(anchor=tk.W)
        
        # Общие результаты
        general_frame = ttk.LabelFrame(self.results_frame, text="Общие", padding=5)
        general_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(general_frame, 
                 text=f"Эффективность: {self.results['collection_efficiency']:.4f}").pack(anchor=tk.W)
    
    def save_results(self):
        """Сохранение результатов"""
        if not self.results:
            messagebox.showerror("Ошибка", "Нет результатов для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Результаты анализа вольтамперограммы\n")
                f.write("="*50 + "\n\n")
                
                f.write("ДИСК:\n")
                f.write(f"Высота плато: {self.results['disk_plateau_height']:.6f} мкА\n")
                f.write(f"Стандартное отклонение: {self.results['disk_plateau_std']:.6f} мкА\n")
                f.write(f"Количество точек: {self.results['disk_plateau_points']}\n\n")
                
                f.write("КОЛЬЦО:\n")
                f.write(f"Высота плато: {self.results['ring_plateau_height']:.6f} мкА\n")
                f.write(f"Стандартное отклонение: {self.results['ring_plateau_std']:.6f} мкА\n")
                f.write(f"Количество точек: {self.results['ring_plateau_points']}\n\n")
                
                f.write("ОБЩИЕ РЕЗУЛЬТАТЫ:\n")
                f.write(f"Эффективность сбора: {self.results['collection_efficiency']:.4f}\n")
                
                # Параметры модели фона
                if self.disk_bg_model:
                    f.write(f"\nПараметры модели фона диска:\n")
                    if self.disk_bg_model['type'] == 'linear':
                        f.write(f"Наклон: {self.disk_bg_model['slope']:.6f}\n")
                        f.write(f"Пересечение: {self.disk_bg_model['intercept']:.6f}\n")
                        f.write(f"R²: {self.disk_bg_model['r_squared']:.6f}\n")
                    else:
                        f.write(f"Коэффициенты полинома: {self.disk_bg_model['coefficients']}\n")
                
                if self.ring_bg_model:
                    f.write(f"\nПараметры модели фона кольца:\n")
                    if self.ring_bg_model['type'] == 'linear':
                        f.write(f"Наклон: {self.ring_bg_model['slope']:.6f}\n")
                        f.write(f"Пересечение: {self.ring_bg_model['intercept']:.6f}\n")
                        f.write(f"R²: {self.ring_bg_model['r_squared']:.6f}\n")
                    else:
                        f.write(f"Коэффициенты полинома: {self.ring_bg_model['coefficients']}\n")
            
            messagebox.showinfo("Успех", f"Результаты сохранены в {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

# Дополнительный класс для расширенного анализа
class AdvancedVoltammetryAnalyzer(VoltammetryAnalyzer):
    """Расширенная версия с дополнительными возможностями"""
    
    def __init__(self):
        super().__init__()
        self.add_advanced_features()
    
    def add_advanced_features(self):
        """Добавление расширенных функций"""
        # Дополнительная панель
        advanced_frame = ttk.LabelFrame(self.control_frame, text="Расширенный анализ", padding=5)
        advanced_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(advanced_frame, text="Асимметричные МНК", 
                  command=self.asymmetric_least_squares).pack(fill=tk.X, pady=2)
        ttk.Button(advanced_frame, text="Анализ шума", 
                  command=self.noise_analysis).pack(fill=tk.X, pady=2)
        ttk.Button(advanced_frame, text="Сравнить модели", 
                  command=self.compare_models).pack(fill=tk.X, pady=2)
    
    def asymmetric_least_squares(self):
        """Метод асимметричных наименьших квадратов для сложного дрифта"""
        if self.data is None:
            messagebox.showerror("Ошибка", "Сначала загрузите данные")
            return
            
        try:
            # Упрощенная реализация асимметричных МНК
            # В реальной реализации здесь был бы более сложный алгоритм
            
            def asymmetric_loss(params, x, y, asymmetry=0.1):
                if self.model_type == 'linear':
                    y_pred = params[0] * x + params[1]
                else:
                    y_pred = np.polyval(params, x)
                
                residuals = y - y_pred
                weights = np.where(residuals > 0, asymmetry, 1 - asymmetry)
                return np.sum(weights * residuals**2)
            
            # Получаем данные фона
            if self.current_dataset == 'disk':
                bg_range = self.disk_background_range
            else:
                bg_range = self.ring_background_range
                
            if bg_range is None:
                messagebox.showerror("Ошибка", "Выделите область фона")
                return
                
            x, y = self.get_region_data(bg_range, self.current_dataset)
            
            if len(x) < 3:
                messagebox.showerror("Ошибка", "Недостаточно точек для анализа")
                return
                
            # Оптимизация с асимметричной функцией потерь
            from scipy.optimize import minimize
            
            if self.model_type == 'linear':
                initial_guess = [0, np.mean(y)]
            else:
                initial_guess = np.polyfit(x, y, self.polynomial_degree)
            
            result = minimize(asymmetric_loss, initial_guess, args=(x, y), method='BFGS')
            
            if result.success:
                if self.current_dataset == 'disk':
                    if self.model_type == 'linear':
                        self.disk_bg_model = {
                            'type': 'linear',
                            'slope': result.x[0],
                            'intercept': result.x[1],
                            'method': 'asymmetric'
                        }
                    else:
                        self.disk_bg_model = {
                            'type': 'polynomial',
                            'coefficients': result.x,
                            'degree': self.polynomial_degree,
                            'method': 'asymmetric'
                        }
                else:
                    if self.model_type == 'linear':
                        self.ring_bg_model = {
                            'type': 'linear',
                            'slope': result.x[0],
                            'intercept': result.x[1],
                            'method': 'asymmetric'
                        }
                    else:
                        self.ring_bg_model = {
                            'type': 'polynomial',
                            'coefficients': result.x,
                            'degree': self.polynomial_degree,
                            'method': 'asymmetric'
                        }
                
                messagebox.showinfo("Успех", f"Асимметричная модель построена для {self.current_dataset}")
            else:
                messagebox.showerror("Ошибка", "Не удалось построить асимметричную модель")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка асимметричных МНК: {str(e)}")
    
    def noise_analysis(self):
        """Анализ шума в данных"""
        if self.data is None:
            messagebox.showerror("Ошибка", "Сначала загрузите данные")
            return
            
        try:
            # Анализ шума в исходных данных
            disk_noise = np.std(np.diff(self.disk_current))
            ring_noise = np.std(np.diff(self.ring_current))
            
            # Если есть скорректированные данные
            if self.disk_current_corrected is not None:
                disk_noise_corrected = np.std(np.diff(self.disk_current_corrected))
                ring_noise_corrected = np.std(np.diff(self.ring_current_corrected))
            else:
                disk_noise_corrected = None
                ring_noise_corrected = None
            
            # Создаем окно с результатами
            noise_window = tk.Toplevel(self.root)
            noise_window.title("Анализ шума")
            noise_window.geometry("400x300")
            
            ttk.Label(noise_window, text="Анализ шума", font=('Arial', 14, 'bold')).pack(pady=10)
            
            results_text = f"""
Исходные данные:
Диск: {disk_noise:.6f} мкА (RMS шума)
Кольцо: {ring_noise:.6f} мкА (RMS шума)
"""
            
            if disk_noise_corrected is not None:
                results_text += f"""
После коррекции фона:
Диск: {disk_noise_corrected:.6f} мкА (RMS шума)
Кольцо: {ring_noise_corrected:.6f} мкА (RMS шума)

Улучшение S/N:
Диск: {disk_noise/disk_noise_corrected:.2f}x
Кольцо: {ring_noise/ring_noise_corrected:.2f}x
"""
            
            ttk.Label(noise_window, text=results_text, justify=tk.LEFT).pack(padx=20, pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка анализа шума: {str(e)}")
    
    def compare_models(self):
        """Сравнение различных моделей фона"""
        if self.data is None:
            messagebox.showerror("Ошибка", "Сначала загрузите данные")
            return
            
        if self.disk_background_range is None:
            messagebox.showerror("Ошибка", "Выделите область фона для диска")
            return
            
        try:
            x, y = self.get_region_data(self.disk_background_range, 'disk')
            
            # Тестируем разные модели
            models = {}
            
            # Линейная модель
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            y_pred_linear = slope * x + intercept
            rmse_linear = np.sqrt(np.mean((y - y_pred_linear)**2))
            models['Линейная'] = {
                'rmse': rmse_linear,
                'r_squared': r_value**2,
                'params': f"y = {slope:.6f}x + {intercept:.6f}"
            }
            
            # Полиномиальные модели
            for degree in [2, 3]:
                try:
                    coeffs = np.polyfit(x, y, degree)
                    y_pred_poly = np.polyval(coeffs, x)
                    rmse_poly = np.sqrt(np.mean((y - y_pred_poly)**2))
                    
                    # R²
                    ss_res = np.sum((y - y_pred_poly)**2)
                    ss_tot = np.sum((y - np.mean(y))**2)
                    r_squared = 1 - (ss_res / ss_tot)
                    
                    models[f'Полином {degree}°'] = {
                        'rmse': rmse_poly,
                        'r_squared': r_squared,
                        'params': f"Коэффициенты: {coeffs}"
                    }
                except:
                    pass
            
            # Создаем окно сравнения
            compare_window = tk.Toplevel(self.root)
            compare_window.title("Сравнение моделей")
            compare_window.geometry("600x400")
            
            ttk.Label(compare_window, text="Сравнение моделей фона", 
                     font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Таблица результатов
            tree = ttk.Treeview(compare_window, columns=('RMSE', 'R²'), show='tree headings')
            tree.heading('#0', text='Модель')
            tree.heading('RMSE', text='RMSE')
            tree.heading('R²', text='R²')
            
            for model_name, metrics in models.items():
                tree.insert('', 'end', text=model_name, 
                           values=(f"{metrics['rmse']:.6f}", f"{metrics['r_squared']:.6f}"))
            
            tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Рекомендация
            best_model = min(models.items(), key=lambda x: x[1]['rmse'])
            ttk.Label(compare_window, 
                     text=f"Рекомендуемая модель: {best_model[0]} (наименьший RMSE)",
                     font=('Arial', 12, 'bold')).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сравнения моделей: {str(e)}")

def main():
    """Главная функция для запуска приложения"""
    print("Запуск анализатора вольтамперограмм...")
    print("Требуемые библиотеки: numpy, pandas, matplotlib, scipy, tkinter")
    
    try:
        # Проверяем наличие всех необходимых библиотек
        import numpy
        import pandas
        import matplotlib
        import scipy
        print("✓ Все библиотеки найдены")
        
        # Запуск приложения
        app = AdvancedVoltammetryAnalyzer()
        
        print("\nИнструкция по использованию:")
        print("1. Загрузите данные (CSV/TXT) или используйте тестовые данные")
        print("2. Выберите активный датасет (диск/кольцо)")
        print("3. Переключите режим на 'background' и выделите область фона")
        print("4. Повторите для второго датасета")
        print("5. Переключите режим на 'plateau' и выделите области плато")
        print("6. Выполните коррекцию фона")
        print("7. Измерьте высоты плато")
        print("8. Сохраните результаты")
        print("\nДля выделения области используйте мышь на графике")
        
        app.run()
        
    except ImportError as e:
        print(f"Ошибка: Не найдена библиотека {e.name}")
        print("Установите необходимые зависимости:")
        print("pip install numpy pandas matplotlib scipy")
    except Exception as e:
        print(f"Ошибка запуска: {str(e)}")

# Пример использования с автоматической обработкой
class BatchProcessor:
    """Класс для пакетной обработки множества файлов"""
    
    def __init__(self):
        self.results_summary = []
    
    def process_file(self, file_path, disk_bg_range, disk_plateau_range, 
                    ring_bg_range, ring_plateau_range):
        """Обработка одного файла с заданными параметрами"""
        try:
            # Загрузка данных
            data = pd.read_csv(file_path)
            voltage = data.iloc[:, 0].values
            disk_current = data.iloc[:, 1].values
            ring_current = data.iloc[:, 2].values
            
            # Коррекция фона диска
            disk_bg_mask = (voltage >= disk_bg_range[0]) & (voltage <= disk_bg_range[1])
            disk_bg_x = voltage[disk_bg_mask]
            disk_bg_y = disk_current[disk_bg_mask]
            
            disk_slope, disk_intercept = np.polyfit(disk_bg_x, disk_bg_y, 1)
            disk_bg_corrected = disk_slope * voltage + disk_intercept
            disk_current_corrected = disk_current - disk_bg_corrected
            
            # Коррекция фона кольца
            ring_bg_mask = (voltage >= ring_bg_range[0]) & (voltage <= ring_bg_range[1])
            ring_bg_x = voltage[ring_bg_mask]
            ring_bg_y = ring_current[ring_bg_mask]
            
            ring_slope, ring_intercept = np.polyfit(ring_bg_x, ring_bg_y, 1)
            ring_bg_corrected = ring_slope * voltage + ring_intercept
            ring_current_corrected = ring_current - ring_bg_corrected
            
            # Измерение плато
            disk_plateau_mask = (voltage >= disk_plateau_range[0]) & (voltage <= disk_plateau_range[1])
            ring_plateau_mask = (voltage >= ring_plateau_range[0]) & (voltage <= ring_plateau_range[1])
            
            disk_plateau_height = np.mean(disk_current_corrected[disk_plateau_mask])
            ring_plateau_height = np.mean(ring_current_corrected[ring_plateau_mask])
            
            disk_plateau_std = np.std(disk_current_corrected[disk_plateau_mask])
            ring_plateau_std = np.std(ring_current_corrected[ring_plateau_mask])
            
            collection_efficiency = abs(ring_plateau_height / disk_plateau_height)
            
            result = {
                'file': file_path,
                'disk_plateau_height': disk_plateau_height,
                'disk_plateau_std': disk_plateau_std,
                'ring_plateau_height': ring_plateau_height,
                'ring_plateau_std': ring_plateau_std,
                'collection_efficiency': collection_efficiency
            }
            
            self.results_summary.append(result)
            return result
            
        except Exception as e:
            print(f"Ошибка обработки файла {file_path}: {str(e)}")
            return None
    
    def save_batch_results(self, output_path):
        """Сохранение результатов пакетной обработки"""
        if not self.results_summary:
            print("Нет результатов для сохранения")
            return
            
        df = pd.DataFrame(self.results_summary)
        df.to_csv(output_path, index=False)
        print(f"Результаты сохранены в {output_path}")

# Пример скрипта для автоматической обработки
def automated_analysis_example():
    """Пример автоматической обработки данных"""
    
    # Генерируем тестовые данные
    voltage = np.linspace(-0.2, 1.0, 200)
    disk_bg = 0.1 * voltage + 0.02 * np.sin(voltage * 10)
    disk_signal = np.where(voltage > 0.5, 2.0, 0)
    disk_noise = 0.05 * np.random.randn(len(voltage))
    disk_current = disk_bg + disk_signal + disk_noise
    
    ring_bg = -0.05 * voltage + 0.01 * np.cos(voltage * 15)
    ring_signal = np.where(voltage > 0.3, -1.5, 0)
    ring_noise = 0.03 * np.random.randn(len(voltage))
    ring_current = ring_bg + ring_signal + ring_noise
    
    # Коррекция фона (автоматическое определение областей)
    # Область фона до сигнала
    bg_mask = voltage < 0.2
    
    # Подгонка линейной модели для диска
    disk_bg_coeffs = np.polyfit(voltage[bg_mask], disk_current[bg_mask], 1)
    disk_bg_model = np.polyval(disk_bg_coeffs, voltage)
    disk_corrected = disk_current - disk_bg_model
    
    # Подгонка линейной модели для кольца
    ring_bg_coeffs = np.polyfit(voltage[bg_mask], ring_current[bg_mask], 1)
    ring_bg_model = np.polyval(ring_bg_coeffs, voltage)
    ring_corrected = ring_current - ring_bg_model
    
    # Измерение плато
    disk_plateau_mask = voltage > 0.7  # Область плато
    ring_plateau_mask = voltage > 0.5
    
    disk_plateau_height = np.mean(disk_corrected[disk_plateau_mask])
    ring_plateau_height = np.mean(ring_corrected[ring_plateau_mask])
    
    disk_plateau_std = np.std(disk_corrected[disk_plateau_mask])
    ring_plateau_std = np.std(ring_corrected[ring_plateau_mask])
    
    collection_efficiency = abs(ring_plateau_height / disk_plateau_height)
    
    # Результаты
    print("Результаты автоматического анализа:")
    print(f"Диск - высота плато: {disk_plateau_height:.6f} ± {disk_plateau_std:.6f} мкА")
    print(f"Кольцо - высота плато: {ring_plateau_height:.6f} ± {ring_plateau_std:.6f} мкА")
    print(f"Эффективность сбора: {collection_efficiency:.4f}")
    
    # Построение результирующего графика
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Исходные данные
    ax1.plot(voltage, disk_current, 'b-', label='Диск исходный', alpha=0.7)
    ax1.plot(voltage, ring_current, 'r-', label='Кольцо исходный', alpha=0.7)
    ax1.plot(voltage, disk_bg_model, 'b--', label='Фон диска', alpha=0.8)
    ax1.plot(voltage, ring_bg_model, 'r--', label='Фон кольца', alpha=0.8)
    ax1.set_ylabel('Ток, мкА')
    ax1.set_title('Исходные данные и модели фона')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Скорректированные данные
    ax2.plot(voltage, disk_corrected, 'b-', label='Диск скорректированный', linewidth=2)
    ax2.plot(voltage, ring_corrected, 'r-', label='Кольцо скорректированный', linewidth=2)
    ax2.axhspan(disk_plateau_height - disk_plateau_std, disk_plateau_height + disk_plateau_std, 
                alpha=0.2, color='blue', label='Плато диска ±σ')
    ax2.axhspan(ring_plateau_height - ring_plateau_std, ring_plateau_height + ring_plateau_std, 
                alpha=0.2, color='red', label='Плато кольца ±σ')
    ax2.set_xlabel('Напряжение, В')
    ax2.set_ylabel('Ток, мкА')
    ax2.set_title('Скорректированные данные')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return {
        'disk_plateau_height': disk_plateau_height,
        'disk_plateau_std': disk_plateau_std,
        'ring_plateau_height': ring_plateau_height,
        'ring_plateau_std': ring_plateau_std,
        'collection_efficiency': collection_efficiency
    }

# Установка и запуск
if __name__ == "__main__":
    print("=== Анализатор вольтамперограмм ===")
    print("\nВыберите режим работы:")
    print("1. Интерактивное приложение (GUI)")
    print("2. Автоматический анализ (пример)")
    print("3. Пакетная обработка")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            main()
        elif choice == "2":
            print("\nЗапуск автоматического анализа...")
            results = automated_analysis_example()
            print("\nАнализ завершен. График отображен.")
        elif choice == "3":
            print("\nПакетная обработка:")
            print("Создайте объект BatchProcessor и используйте метод process_file")
            print("для обработки множества файлов с одинаковыми параметрами")
            
            # Пример использования
            processor = BatchProcessor()
            print("Пример создан. Используйте processor.process_file() для обработки.")
        else:
            print("Неверный выбор. Запуск интерактивного приложения...")
            main()
            
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

"""
ИНСТРУКЦИЯ ПО УСТАНОВКЕ И ИСПОЛЬЗОВАНИЮ:

1. УСТАНОВКА ЗАВИСИМОСТЕЙ:
pip install numpy pandas matplotlib scipy tkinter

2. ФОРМАТ ВХОДНЫХ ДАННЫХ:
CSV/TXT файл с тремя колонками:
- Колонка 1: Напряжение (В)
- Колонка 2: Ток диска (мкА)  
- Колонка 3: Ток кольца (мкА)

Разделители: запятая, точка с запятой или табуляция

3. АЛГОРИТМ РАБОТЫ:
   
   Для каждого электрода (диск/кольцо):
   а) Выделение области фона (до или после ступени)
   б) Подгонка модели фона (линейная или полиномиальная)
   в) Вычитание фонового тока из всех данных
   г) Выделение области плато (постоянный ток)
   д) Измерение средней высоты и стандартного отклонения

4. МЕТОДЫ КОРРЕКЦИИ ФОНА:
   - Линейная регрессия: для простого дрифта
   - Полиномы 2-3 степени: для сложного дрифта
   - Асимметричные МНК: для нелинейного дрифта

5. РЕЗУЛЬТАТЫ:
   - Высота плато для диска и кольца
   - Стандартные отклонения
   - Эффективность сбора (отношение токов)
   - Параметры моделей фона
   - Статистика качества подгонки

6. ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ:
   - Анализ шума в данных
   - Сравнение различных моделей фона
   - Пакетная обработка множества файлов
   - Автоматическое определение оптимальной модели

Приложение полностью реализует описанный алгоритм и предоставляет
интуитивно понятный интерфейс для интерактивного анализа.
"""
                