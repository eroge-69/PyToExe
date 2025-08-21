# Electric Mode DSP - Python Implementation
# Математическое моделирование распределения напряжения электрического тока в ванне дугоплавильной электропечи
# Перевод с C# на Python

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import threading
import time
from typing import List, Tuple, Optional

class ElectrodeData:
    """Класс для хранения данных электрода"""
    def __init__(self):
        self.x_el = 0.0
        self.y_el = 0.0

class PointData:
    """Класс для хранения данных точки"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, tag: str = "-"):
        self.x = x
        self.y = y 
        self.z = z
        self.tag = tag

class SolutionEquations:
    """Класс для решения СЛАУ методом Гаусса"""
    
    @staticmethod
    def gauss_solve(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Решение СЛАУ методом Гаусса"""
        n = len(B)
        
        # Создаем копии для работы
        matrix = A.copy().astype(float)
        vector = B.copy().astype(float)
        
        # Прямой ход
        for i in range(n):
            # Поиск максимального элемента для выбора главного элемента
            max_row = i
            for k in range(i + 1, n):
                if abs(matrix[k, i]) > abs(matrix[max_row, i]):
                    max_row = k
            
            # Перестановка строк
            if max_row != i:
                matrix[[i, max_row]] = matrix[[max_row, i]]
                vector[i], vector[max_row] = vector[max_row], vector[i]
            
            # Проверка на нулевой диагональный элемент
            if abs(matrix[i, i]) < 1e-10:
                matrix[i, i] = 1e-10
            
            # Приведение к треугольному виду
            for k in range(i + 1, n):
                factor = matrix[k, i] / matrix[i, i]
                for j in range(i, n):
                    matrix[k, j] -= factor * matrix[i, j]
                vector[k] -= factor * vector[i]
        
        # Обратный ход
        solution = np.zeros(n)
        for i in range(n - 1, -1, -1):
            solution[i] = vector[i]
            for j in range(i + 1, n):
                solution[i] -= matrix[i, j] * solution[j]
            solution[i] /= matrix[i, i]
        
        return solution

class DiscretizationRegion:
    """Класс для разбиения области методом сеток"""
    
    @staticmethod
    def discretize(step_data: np.ndarray, list_xy: List[PointData], 
                  number_list_xy: List[PointData], number_electrode: List[PointData]) -> np.ndarray:
        """Разбиение исходной области с помощью метода сеток"""
        
        nx = int(step_data[0, 0] - 1)
        ny = int(step_data[1, 0] - 1) 
        nz = int(step_data[2, 0])
        
        # Создание 3D массива для разбиения
        razb = np.zeros((nx, ny, nz))
        
        # Поиск минимальных координат
        if number_list_xy:
            min_x = min(int(p.x) for p in number_list_xy)
            min_y = min(int(p.y) for p in number_list_xy)
        else:
            min_x = min_y = 0
        
        # Подсчет количества точек
        point_count = sum(1 for p in list_xy if p.tag == "-")
        
        # Заполнение массива разбиения
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    for idx, num_point in enumerate(number_list_xy):
                        if (int(num_point.x) == i + min_x and 
                            int(num_point.y) == j + min_y):
                            
                            razb[i, j, k] = list_xy[idx].z + k * point_count
                            
                            # Если это электрод
                            if list_xy[idx].tag != "-":
                                razb[i, j, k] = -1 * int(list_xy[idx].tag)
                            
                            # Проверка предыдущего слоя для электродов
                            if k > 0 and razb[i, j, k-1] <= 0:
                                razb[i, j, k] = razb[i, j, k-1]
                            break
        
        return razb

class CalculationMatrix:
    """Класс для составления СЛАУ"""
    
    @staticmethod
    def build_system(step_data: np.ndarray, razb: np.ndarray, 
                    Um: np.ndarray, w: float, t: float, j1: float, 
                    mu: float, gamma: float, point_count: int) -> Tuple[np.ndarray, np.ndarray]:
        """Составление СЛАУ для решения поставленной задачи"""
        
        nx = int(step_data[0, 0] - 1)
        ny = int(step_data[1, 0] - 1)
        nz = int(step_data[2, 0])
        
        total_points = point_count * nz
        A = np.zeros((total_points + 1, total_points + 1))
        B = np.zeros(total_points + 1)
        
        step_x = step_data[0, 1]
        step_y = step_data[1, 1]  
        step_z = step_data[2, 1]
        
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    # Проверка глубины для расчета коэффициента
                    depth_factor = 0
                    if 0.76 - k * (0.7 / (nz - 1)) <= 0.26:
                        depth_factor = 1
                    
                    current_point = int(razb[i, j, k])
                    if current_point > 0:
                        # Диагональный элемент
                        A[current_point, current_point] = (
                            4.0 * step_x**2 + 2.0 * step_z**2 - 
                            j1 * w * mu * gamma
                        )
                        
                        # Соседи по X
                        if i > 0:
                            neighbor = razb[i-1, j, k]
                            if neighbor < 0:
                                electrode_idx = int(-neighbor - 1)
                                phase = -2 * (neighbor - 2) * math.pi / 3.0
                                B[current_point] += (depth_factor * Um[electrode_idx] * 
                                                   math.sin(w * t + phase))
                            elif neighbor > 0:
                                A[int(neighbor), current_point] = step_x**2
                                A[current_point, int(neighbor)] = step_x**2
                        
                        if i < nx - 1:
                            neighbor = razb[i+1, j, k]
                            if neighbor < 0:
                                electrode_idx = int(-neighbor - 1)
                                phase = -2 * (neighbor - 2) * math.pi / 3.0
                                B[current_point] += (depth_factor * Um[electrode_idx] * 
                                                   math.sin(w * t + phase))
                            elif neighbor > 0:
                                A[current_point, int(neighbor)] = step_x**2
                                A[int(neighbor), current_point] = step_x**2
                        
                        # Соседи по Y
                        if j > 0:
                            neighbor = razb[i, j-1, k]
                            if neighbor < 0:
                                electrode_idx = int(-neighbor - 1)
                                phase = -2 * (neighbor - 2) * math.pi / 3.0
                                B[current_point] += (depth_factor * Um[electrode_idx] * 
                                                   math.sin(w * t + phase))
                            elif neighbor > 0:
                                A[current_point, int(neighbor)] = step_x**2
                                A[int(neighbor), current_point] = step_x**2
                        
                        if j < ny - 1:
                            neighbor = razb[i, j+1, k]
                            if neighbor < 0:
                                electrode_idx = int(-neighbor - 1)
                                phase = -2 * (neighbor - 2) * math.pi / 3.0
                                B[current_point] += (depth_factor * Um[electrode_idx] * 
                                                   math.sin(w * t + phase))
                            elif neighbor > 0:
                                A[current_point, int(neighbor)] = step_x**2
                                A[int(neighbor), current_point] = step_x**2
                        
                        # Соседи по Z
                        if k > 0:
                            neighbor = razb[i, j, k-1]
                            if neighbor < 0:
                                electrode_idx = int(-neighbor - 1)
                                phase = -2 * (neighbor - 2) * math.pi / 3.0
                                B[current_point] += (depth_factor * Um[electrode_idx] * 
                                                   math.sin(w * t + phase))
                            elif neighbor > 0:
                                A[current_point, int(neighbor)] = step_z**2
                                A[int(neighbor), current_point] = step_z**2
                        
                        if k < nz - 1:
                            neighbor = razb[i, j, k+1]
                            if neighbor < 0:
                                electrode_idx = int(-neighbor - 1)
                                phase = -2 * (neighbor - 2) * math.pi / 3.0
                                B[current_point] += (depth_factor * Um[electrode_idx] * 
                                                   math.sin(w * t + phase))
                            elif neighbor > 0:
                                A[current_point, int(neighbor)] = step_z**2
                                A[int(neighbor), current_point] = step_z**2
        
        return A, B

class ElectricModeGUI:
    """Главный класс GUI приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Электрический режим ДСП")
        self.root.geometry("900x600")
        
        # Глобальные переменные (аналог статических переменных C#)
        self.radius_dsp = 10.0
        self.radius_electrod = 2.0
        self.z0 = 0.06
        self.w = 628.0
        self.t = 1.0
        self.gamma = 0.8
        self.mu = 1.0
        self.j1 = 1.0
        self.step = np.array([[10, 2], [10, 2], [2, 0.1]])  # [количество разбиений, шаг]
        
        self.list_xy: List[PointData] = []
        self.electrode: List[PointData] = []
        self.number_list_xy: List[PointData] = []
        self.number_electrode: List[PointData] = []
        self.razb_electrode: List[PointData] = []
        
        self.point_count = 0
        self.Um = np.array([398.0, 398.0, 398.0])
        self.razb: Optional[np.ndarray] = None
        self.A: Optional[np.ndarray] = None
        self.B: Optional[np.ndarray] = None
        self.U_result: Optional[np.ndarray] = None
        
        self.flag_calculated = False
        self.job_complete = False
        
        self.setup_gui()
    
    def setup_gui(self):
        """Настройка графического интерфейса"""
        
        # Создание меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        exit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Выход", menu=exit_menu)
        exit_menu.add_command(label="Выход", command=self.root.quit)
        
        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка "Разбиение"
        self.tab_discretization = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_discretization, text="Разбиение")
        self.setup_discretization_tab()
        
        # Вкладка "Расчет"
        self.tab_calculation = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_calculation, text="Расчет")
        self.setup_calculation_tab()
        
        # Вкладка "Графический анализ"
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text="Графический анализ")
        self.setup_analysis_tab()
    
    def setup_discretization_tab(self):
        """Настройка вкладки разбиения"""
        
        # Левая панель с параметрами
        left_frame = ttk.Frame(self.tab_discretization)
        left_frame.pack(side='left', fill='both', padx=10, pady=10)
        
        # Группа параметров ДСП
        dsp_group = ttk.LabelFrame(left_frame, text="Параметры ДСП")
        dsp_group.pack(fill='x', pady=5)
        
        # Радиус ДСП
        ttk.Label(dsp_group, text="Радиус:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.radius_entry = ttk.Entry(dsp_group, width=15)
        self.radius_entry.insert(0, "10")
        self.radius_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Количество разбиений
        ttk.Label(dsp_group, text="Количество разбиений:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        
        ttk.Label(dsp_group, text="по оси X:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.nx_spinbox = ttk.Spinbox(dsp_group, from_=4, to=30, width=10, value=10)
        self.nx_spinbox.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(dsp_group, text="по оси Y:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.ny_spinbox = ttk.Spinbox(dsp_group, from_=4, to=30, width=10, value=10)
        self.ny_spinbox.grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(dsp_group, text="по оси Z:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.nz_spinbox = ttk.Spinbox(dsp_group, from_=1, to=7, width=10, value=2)
        self.nz_spinbox.grid(row=4, column=1, padx=5, pady=2)
        
        # Группа параметров электрода
        electrode_group = ttk.LabelFrame(left_frame, text="Расположение электрода")
        electrode_group.pack(fill='x', pady=5)
        
        ttk.Label(electrode_group, text="Координаты центра одного из электродов:").grid(row=0, column=0, columnspan=2, padx=5, pady=2)
        
        ttk.Label(electrode_group, text="X =").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.electrode_x_entry = ttk.Entry(electrode_group, width=10)
        self.electrode_x_entry.insert(0, "0")
        self.electrode_x_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(electrode_group, text="Y =").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.electrode_y_entry = ttk.Entry(electrode_group, width=10)
        self.electrode_y_entry.insert(0, "6")
        self.electrode_y_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(electrode_group, text="Радиус:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.electrode_radius_entry = ttk.Entry(electrode_group, width=10)
        self.electrode_radius_entry.insert(0, "2")
        self.electrode_radius_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Кнопка построения
        self.build_button = ttk.Button(left_frame, text="Построить", command=self.build_discretization)
        self.build_button.pack(pady=10)
        
        # Область визуализации сетки
        self.setup_grid_visualization()
    
    def setup_calculation_tab(self):
        """Настройка вкладки расчета"""
        
        # Левая панель с параметрами
        left_frame = ttk.Frame(self.tab_calculation)
        left_frame.pack(side='left', fill='both', padx=10, pady=10)
        
        # Параметры точек области
        points_group = ttk.LabelFrame(left_frame, text="Параметры точек области")
        points_group.pack(fill='x', pady=5)
        
        # Шаг по оси Z
        ttk.Label(points_group, text="по оси Z:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.step_z_entry = ttk.Entry(points_group, width=15)
        self.step_z_entry.insert(0, "0.1")
        self.step_z_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Высота расположения 1-го слоя
        ttk.Label(points_group, text="Высота расположения 1-го слоя:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.z0_entry = ttk.Entry(points_group, width=15)
        self.z0_entry.insert(0, "0.06")
        self.z0_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # j
        ttk.Label(points_group, text="j:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.j_entry = ttk.Entry(points_group, width=15)
        self.j_entry.insert(0, "1")
        self.j_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Удельная электрическая проводимость
        ttk.Label(points_group, text="Удельная электрическая\\nпроводимость среды:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.gamma_entry = ttk.Entry(points_group, width=15)
        self.gamma_entry.insert(0, "0.8")
        self.gamma_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Магнитная проницаемость
        ttk.Label(points_group, text="Магнитная проницаемость среды:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.mu_entry = ttk.Entry(points_group, width=15)
        self.mu_entry.insert(0, "1")
        self.mu_entry.grid(row=4, column=1, padx=5, pady=2)
        
        # Параметры граничных условий
        boundary_group = ttk.LabelFrame(left_frame, text="Параметры граничных условий")
        boundary_group.pack(fill='x', pady=5)
        
        # Частота
        ttk.Label(boundary_group, text="Частота:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.frequency_entry = ttk.Entry(boundary_group, width=15)
        self.frequency_entry.insert(0, "628")
        self.frequency_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Время
        ttk.Label(boundary_group, text="Время:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.time_entry = ttk.Entry(boundary_group, width=15)
        self.time_entry.insert(0, "1")
        self.time_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Напряжения электродов
        ttk.Label(boundary_group, text="Uam:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.uam_entry = ttk.Entry(boundary_group, width=10)
        self.uam_entry.insert(0, "398")
        self.uam_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(boundary_group, text="Ubm:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.ubm_entry = ttk.Entry(boundary_group, width=10)
        self.ubm_entry.insert(0, "398")
        self.ubm_entry.grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(boundary_group, text="Ucm:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.ucm_entry = ttk.Entry(boundary_group, width=10)
        self.ucm_entry.insert(0, "398")
        self.ucm_entry.grid(row=4, column=1, padx=5, pady=2)
        
        # Кнопка расчета
        self.calculate_button = ttk.Button(left_frame, text="Расчет", command=self.start_calculation)
        self.calculate_button.pack(pady=10)
        
        # Правая панель с результатами
        right_frame = ttk.Frame(self.tab_calculation)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Таблица результатов
        self.results_tree = ttk.Treeview(right_frame, columns=("Voltage",), show="tree headings")
        self.results_tree.heading("#0", text="Номер точки")
        self.results_tree.heading("Voltage", text="Напряжение")
        self.results_tree.pack(fill='both', expand=True)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.results_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_tree.configure(yscrollcommand=scrollbar.set)
    
    def setup_analysis_tab(self):
        """Настройка вкладки графического анализа"""
        
        # Верхняя панель управления
        control_frame = ttk.Frame(self.tab_analysis)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(control_frame, text="Выберите график зависимости:").pack(side='left', padx=5)
        
        self.graph_type_combobox = ttk.Combobox(control_frame, values=[
            "напряжение от высоты",
            "напряжение от удаленности от электрода"
        ], state='readonly')
        self.graph_type_combobox.pack(side='left', padx=5)
        self.graph_type_combobox.bind('<<ComboboxSelected>>', self.on_graph_type_changed)
        
        # Область для графика
        self.setup_analysis_plot()
    
    def setup_grid_visualization(self):
        """Настройка области визуализации сетки"""
        
        # Правая панель для сетки
        right_frame = ttk.Frame(self.tab_discretization)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Создание canvas для сетки
        self.grid_frame = ttk.Frame(right_frame)
        self.grid_frame.pack(fill='both', expand=True)
        
        # Информация о выбранной точке
        info_frame = ttk.LabelFrame(right_frame, text="Параметры точки")
        info_frame.pack(fill='x', pady=5)
        
        self.point_info_label = ttk.Label(info_frame, text="Выберите точку на сетке")
        self.point_info_label.pack(padx=5, pady=5)
    
    def setup_analysis_plot(self):
        """Настройка области для графиков анализа"""
        
        # Создание matplotlib фигуры
        self.analysis_fig = Figure(figsize=(10, 6), dpi=100)
        self.analysis_ax = self.analysis_fig.add_subplot(111)
        
        # Встраивание в tkinter
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, self.tab_analysis)
        self.analysis_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def validate_inputs(self) -> bool:
        """Валидация входных данных"""
        try:
            # Проверка параметров ДСП
            radius = float(self.radius_entry.get())
            if radius <= 0:
                raise ValueError("Радиус должен быть положительным")
            
            # Проверка разбиений
            nx = int(self.nx_spinbox.get())
            ny = int(self.ny_spinbox.get())
            nz = int(self.nz_spinbox.get())
            
            if nx < 4 or nx > 30 or ny < 4 or ny > 30 or nz < 1 or nz > 7:
                raise ValueError("Неверные параметры разбиения")
            
            # Проверка электрода
            ex = float(self.electrode_x_entry.get())
            ey = float(self.electrode_y_entry.get())
            er = float(self.electrode_radius_entry.get())
            
            if er <= 0:
                raise ValueError("Радиус электрода должен быть положительным")
            
            # Проверка, что электрод не выходит за пределы печи
            if abs(ex) + er > radius or abs(ey) + er > radius:
                raise ValueError("Электрод не может выходить за пределы печи")
            
            # Проверка, что центр электрода лежит на одной из осей
            if not ((ex == 0 and ey != 0) or (ex != 0 and ey == 0)):
                raise ValueError("Задайте электрод, центр которого совпадает с одной из осей")
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return False
    
    def build_discretization(self):
        """Построение разбиения области"""
        
        if not self.validate_inputs():
            return
        
        try:
            # Получение параметров
            self.radius_dsp = float(self.radius_entry.get())
            self.radius_electrod = float(self.electrode_radius_entry.get())
            
            nx = int(self.nx_spinbox.get())
            ny = int(self.ny_spinbox.get())
            nz = int(self.nz_spinbox.get())
            
            self.step[0, 0] = nx
            self.step[1, 0] = ny
            self.step[2, 0] = nz
            
            # Вычисление шагов
            self.step[0, 1] = 2.0 * self.radius_dsp / nx
            self.step[1, 1] = 2.0 * self.radius_dsp / ny
            self.step[2, 1] = 2.0 * self.radius_dsp / nz
            
            # Очистка предыдущих данных
            self.list_xy.clear()
            self.electrode.clear()
            self.number_list_xy.clear()
            self.number_electrode.clear()
            self.razb_electrode.clear()
            
            # Создание сетки точек внутри окружности
            self.create_circular_grid()
            
            # Размещение электродов
            ex = float(self.electrode_x_entry.get())
            ey = float(self.electrode_y_entry.get())
            self.place_electrodes(ex, ey)
            
            # Подсчет точек и создание разбиения
            self.point_count = sum(1 for p in self.list_xy if p.tag == "-")
            self.razb = DiscretizationRegion.discretize(
                self.step, self.list_xy, self.number_list_xy, self.number_electrode
            )
            
            # Обновление визуализации
            self.update_grid_visualization()
            
            messagebox.showinfo("Успех", "Разбиение области выполнено успешно!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении разбиения: {str(e)}")
    
    def create_circular_grid(self):
        """Создание сетки точек внутри окружности"""
        
        nx = int(self.step[0, 0])
        ny = int(self.step[1, 0])
        
        step_x = self.step[0, 1]
        step_y = self.step[1, 1]
        
        for i in range(ny + 1):
            for j in range(nx + 1):
                x = -self.radius_dsp + step_x * j
                y = self.radius_dsp - step_y * i
                
                # Проверка, что точка внутри окружности
                if x*x + y*y < self.radius_dsp*self.radius_dsp:
                    point = PointData(round(x, 8), round(y, 8), 0.0, "-")
                    self.list_xy.append(point)
                    
                    number_point = PointData(float(j), float(i))
                    self.number_list_xy.append(number_point)
    
    def place_electrodes(self, x_electrode: float, y_electrode: float):
        """Размещение трех электродов в трехфазной системе"""
        
        # Первый электрод
        self.place_single_electrode(x_electrode, y_electrode, 1)
        
        # Второй и третий электроды (с поворотом на 120 градусов)
        if x_electrode == 0 and y_electrode != 0:
            distance = abs(y_electrode)
            # Второй электрод
            x2 = round(-distance * math.sqrt(3) / 2, 1)
            y2 = -y_electrode / 2
            self.place_single_electrode(x2, y2, 2)
            
            # Третий электрод
            x3 = -x2
            y3 = y2
            self.place_single_electrode(x3, y3, 3)
            
        elif x_electrode != 0 and y_electrode == 0:
            distance = abs(x_electrode)
            # Второй электрод
            x2 = -x_electrode / 2
            y2 = round(-distance * math.sqrt(3) / 2, 1)
            self.place_single_electrode(x2, y2, 2)
            
            # Третий электрод
            x3 = x2
            y3 = -y2
            self.place_single_electrode(x3, y3, 3)
    
    def place_single_electrode(self, x_center: float, y_center: float, electrode_num: int):
        """Размещение одного электрода"""
        
        # Поиск ближайшей точки к центру электрода
        min_distance = float('inf')
        closest_idx = -1
        
        for i, point in enumerate(self.list_xy):
            distance = math.sqrt((point.x - x_center)**2 + (point.y - y_center)**2)
            if distance < min_distance:
                min_distance = distance
                closest_idx = i
        
        if closest_idx >= 0:
            # Добавление координат электрода
            electrode_point = PointData(self.list_xy[closest_idx].x, self.list_xy[closest_idx].y)
            self.electrode.append(electrode_point)
            
            number_point = PointData(self.number_list_xy[closest_idx].x, self.number_list_xy[closest_idx].y)
            self.number_electrode.append(number_point)
            
            # Пометка точек в области электрода
            for i, point in enumerate(self.list_xy):
                distance_sq = ((point.x - self.list_xy[closest_idx].x)**2 + 
                              (point.y - self.list_xy[closest_idx].y)**2)
                
                if distance_sq <= self.radius_electrod**2:
                    self.list_xy[i].tag = str(electrode_num)
    
    def update_grid_visualization(self):
        """Обновление визуализации сетки"""
        
        # Очистка предыдущей визуализации
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Создание новой визуализации
        fig = Figure(figsize=(8, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        # Отображение точек сетки
        for i, point in enumerate(self.list_xy):
            if point.tag == "-":
                # Обычная точка
                ax.scatter(point.x, point.y, c='gray', s=20, alpha=0.7)
            elif point.tag in ["1", "2", "3"]:
                # Область электрода
                ax.scatter(point.x, point.y, c='green', s=30, alpha=0.8)
        
        # Отображение центров электродов
        for electrode_point in self.electrode:
            ax.scatter(electrode_point.x, electrode_point.y, c='yellow', s=100, marker='s')
        
        # Отображение границы печи
        circle = plt.Circle((0, 0), self.radius_dsp, fill=False, color='black', linewidth=2)
        ax.add_patch(circle)
        
        ax.set_xlim(-self.radius_dsp*1.1, self.radius_dsp*1.1)
        ax.set_ylim(-self.radius_dsp*1.1, self.radius_dsp*1.1)
        ax.set_aspect('equal')
        ax.set_title('Дискретизированная область ДСП')
        ax.grid(True, alpha=0.3)
        
        # Встраивание в tkinter
        canvas = FigureCanvasTkAgg(fig, self.grid_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def start_calculation(self):
        """Запуск расчета в отдельном потоке"""
        
        if self.razb is None:
            messagebox.showerror("Ошибка", "Не было выполнено разбиение исходной области")
            return
        
        if not self.validate_calculation_inputs():
            return
        
        # Запуск расчета в отдельном потоке
        self.job_complete = False
        calculation_thread = threading.Thread(target=self.perform_calculation)
        calculation_thread.start()
        
        # Показ окна ожидания
        self.show_progress_window()
    
    def validate_calculation_inputs(self) -> bool:
        """Валидация входных данных для расчета"""
        try:
            # Проверка всех полей
            self.step[2, 1] = float(self.step_z_entry.get())
            self.z0 = float(self.z0_entry.get())
            self.j1 = float(self.j_entry.get())
            self.gamma = float(self.gamma_entry.get())
            self.mu = float(self.mu_entry.get())
            self.w = float(self.frequency_entry.get())
            self.t = float(self.time_entry.get())
            
            self.Um[0] = float(self.uam_entry.get())
            self.Um[1] = float(self.ubm_entry.get())
            self.Um[2] = float(self.ucm_entry.get())
            
            # Проверка ограничений
            total_points = self.point_count * int(self.step[2, 0])
            if total_points > 3000:
                raise ValueError("Уменьшите число разбиений")
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Не все значения введены или введены неправильно!\n{str(e)}")
            return False
    
    def perform_calculation(self):
        """Выполнение расчета СЛАУ"""
        try:
            # Построение системы уравнений
            self.A, self.B = CalculationMatrix.build_system(
                self.step, self.razb, self.Um, self.w, self.t,
                self.j1, self.mu, self.gamma, self.point_count
            )
            
            # Подготовка матриц для решения
            total_points = self.point_count * int(self.step[2, 0])
            A_solve = self.A[1:total_points+1, 1:total_points+1]
            B_solve = self.B[1:total_points+1]
            
            # Решение СЛАУ
            self.U_result = SolutionEquations.gauss_solve(A_solve, B_solve)
            
            self.flag_calculated = True
            self.job_complete = True
            
            # Обновление результатов в главном потоке
            self.root.after(0, self.update_results)
            
        except Exception as e:
            self.job_complete = True
            self.root.after(0, lambda: messagebox.showerror("Ошибка", 
                f"Невозможно решить СЛАУ. Уменьшите число разбиений.\n{str(e)}"))
    
    def show_progress_window(self):
        """Показ окна ожидания"""
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Выполнение расчета")
        self.progress_window.geometry("400x100")
        self.progress_window.resizable(False, False)
        
        # Центрирование окна
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        ttk.Label(self.progress_window, 
                 text="Выполняются вычисления, пожалуйста, подождите...",
                 font=("Arial", 12)).pack(pady=20)
        
        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(self.progress_window, mode='indeterminate')
        self.progress_bar.pack(pady=10, padx=20, fill='x')
        self.progress_bar.start()
        
        # Проверка завершения
        self.check_calculation_complete()
    
    def check_calculation_complete(self):
        """Проверка завершения расчета"""
        if self.job_complete:
            self.progress_bar.stop()
            self.progress_window.destroy()
        else:
            self.root.after(100, self.check_calculation_complete)
    
    def update_results(self):
        """Обновление таблицы результатов"""
        # Очистка предыдущих результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Добавление новых результатов
        if self.U_result is not None:
            for i, voltage in enumerate(self.U_result):
                self.results_tree.insert("", "end", text=str(i+1), values=(f"{voltage:.6f}",))
        
        messagebox.showinfo("Успех", "Расчет выполнен успешно!")
    
    def on_graph_type_changed(self, event):
        """Обработчик изменения типа графика"""
        if not self.flag_calculated:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет!")
            return
        
        graph_type = self.graph_type_combobox.get()
        self.analysis_ax.clear()
        
        if graph_type == "напряжение от высоты":
            self.plot_voltage_vs_height()
        elif graph_type == "напряжение от удаленности от электрода":
            self.plot_voltage_vs_distance()
        
        self.analysis_canvas.draw()
    
    def plot_voltage_vs_height(self):
        """График зависимости напряжения от высоты"""
        if self.U_result is None:
            return
        
        nz = int(self.step[2, 0])
        
        # Выбираем несколько точек для отображения
        points_to_plot = min(5, self.point_count)
        
        for i in range(0, points_to_plot):
            heights = []
            voltages = []
            
            for k in range(nz):
                point_idx = i + k * self.point_count
                if point_idx < len(self.U_result):
                    height = self.z0 + self.step[2, 1] * k
                    voltage = self.U_result[point_idx]
                    
                    heights.append(height)
                    voltages.append(voltage)
            
            if heights:
                self.analysis_ax.plot(voltages, heights, 'o-', label=f'Точка {i+1}', linewidth=2)
        
        self.analysis_ax.set_title('Зависимость напряжения от высоты в точках ДСП')
        self.analysis_ax.set_xlabel('Напряжение, В')
        self.analysis_ax.set_ylabel('Высота, м')
        self.analysis_ax.legend()
        self.analysis_ax.grid(True, alpha=0.3)
    
    def plot_voltage_vs_distance(self):
        """График зависимости напряжения от удаленности от электрода"""
        if self.U_result is None or not self.electrode:
            return
        
        # Для первого слоя
        distances = []
        voltages = []
        
        for i in range(min(self.point_count, len(self.U_result))):
            if i < len(self.list_xy) and self.list_xy[i].tag == "-":
                # Находим расстояние до ближайшего электрода
                min_distance = float('inf')
                for electrode_point in self.electrode:
                    dist = math.sqrt((self.list_xy[i].x - electrode_point.x)**2 + 
                                   (self.list_xy[i].y - electrode_point.y)**2)
                    min_distance = min(min_distance, dist)
                
                distances.append(min_distance)
                voltages.append(self.U_result[i])
        
        if distances:
            self.analysis_ax.scatter(distances, voltages, c='black', s=50)
            self.analysis_ax.set_title('Зависимость напряжения от расстояния до электрода на слоях ДСП')
            self.analysis_ax.set_xlabel('Расстояние до ближайшего электрода, м')
            self.analysis_ax.set_ylabel('Напряжение, В')
            self.analysis_ax.grid(True, alpha=0.3)
    
    def show_about(self):
        """Показ окна "О программе" """
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        about_text = """
        Математическое моделирование распределения
        напряжения электрического тока в ванне ДСП
        
        Версия 1.0 (Python)
        
        Выполнил:
        Овчинников Д.В., 2015г.
        
        Научный руководитель:
        Галкин А.В.
        
        Переведено на Python в 2025г.
        """
        
        ttk.Label(about_window, text=about_text, justify='center').pack(pady=20)
        ttk.Button(about_window, text="ОК", command=about_window.destroy).pack(pady=10)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

def main():
    """Главная функция"""
    app = ElectricModeGUI()
    app.run()

if __name__ == "__main__":
    main()