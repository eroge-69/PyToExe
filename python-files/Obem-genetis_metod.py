import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, Toplevel, Button
from PIL import Image, ImageTk
from scipy.stats import truncnorm


catagenesis_levels = ['МК1', 'МК2', 'МК3', 'МК4', 'МК5', 'АК1', 'АК2', 'АК3']

# Сапропелевое органическое вещество
sapropelic_catagenesis_data = {
    'МК1': {'C_star': 71.0, 'M_ost': 69.09, 'K_gen_oil': 0.0001, 'K_gen_gas': 0.91},
    'МК2': {'C_star': 76.5, 'M_ost': 54.0, 'K_gen_oil': 8.2, 'K_gen_gas': 0.91},
    'МК3': {'C_star': 78.6, 'M_ost': 32.5, 'K_gen_oil': 28.24, 'K_gen_gas': 1.33},
    'МК4': {'C_star': 82.2, 'M_ost': 27.0, 'K_gen_oil': 28.24, 'K_gen_gas': 4.0},
    'МК5': {'C_star': 81.5, 'M_ost': 25.5, 'K_gen_oil': 28.24, 'K_gen_gas': 4.5},
    'АК1': {'C_star': 81.3, 'M_ost': 24.3, 'K_gen_oil': 28.24, 'K_gen_gas': 4.8},
    'АК2': {'C_star': 84.3, 'M_ost': 22.0, 'K_gen_oil': 28.24, 'K_gen_gas': 6.3},
    'АК3': {'C_star': 88.2, 'M_ost': 20.5, 'K_gen_oil': 28.24, 'K_gen_gas': 6.7}
}

# Гумусовое органическое вещество
humic_catagenesis_data = {
    'МК1': {'C_star': 76.0, 'M_ost': 78.45, 'K_gen_oil': 0.60, 'K_gen_gas': 1.55},
    'МК2': {'C_star': 79.4, 'M_ost': 71.36, 'K_gen_oil': 1.64, 'K_gen_gas': 2.35},
    'МК3': {'C_star': 84.8, 'M_ost': 63.41, 'K_gen_oil': 1.64, 'K_gen_gas': 3.03},
    'МК4': {'C_star': 88.3, 'M_ost': 60.26, 'K_gen_oil': 1.64, 'K_gen_gas': 4.15},
    'МК5': {'C_star': 90.0, 'M_ost': 58.36, 'K_gen_oil': 1.64, 'K_gen_gas': 4.85},
    'АК1': {'C_star': 90.6, 'M_ost': 57.16, 'K_gen_oil': 1.64, 'K_gen_gas': 5.70},
    'АК2': {'C_star': 91.6, 'M_ost': 55.21, 'K_gen_oil': 1.64, 'K_gen_gas': 7.75},
    'АК3': {'C_star': 93.5, 'M_ost': 52.76, 'K_gen_oil': 1.64, 'K_gen_gas': 8.85},
}

# Смешанное органическое вещество
mixed_catagenesis_data = {
    'МК1': {'C_star': 78.0, 'M_ost': 93.37, 'K_gen_oil': 0.55, 'K_gen_gas': 0.90},
    'МК2': {'C_star': 80, 'M_ost': 81.74, 'K_gen_oil': 4.33, 'K_gen_gas': 3.91},
    'МК3': {'C_star': 80.0, 'M_ost': 70.39, 'K_gen_oil': 6.25, 'K_gen_gas': 5.12},
    'МК4': {'C_star': 81.6, 'M_ost': 69.01, 'K_gen_oil': 6.25, 'K_gen_gas': 5.28},
    'МК5': {'C_star': 83.0, 'M_ost': 66.69, 'K_gen_oil': 6.25, 'K_gen_gas': 6.28},
    'АК1': {'C_star': 85.0, 'M_ost': 64.96, 'K_gen_oil': 6.25, 'K_gen_gas': 8.12},
    'АК2': {'C_star': 87.0, 'M_ost': 60.44, 'K_gen_oil': 6.25, 'K_gen_gas': 9.66},
    'АК3': {'C_star': 88.0, 'M_ost': 58.94, 'K_gen_oil': 6.25, 'K_gen_gas': 10.56},
}

# Миграционные данные для сапропелевого органического вещества
migration = {
    'МК1': {'R_mig_nef': 0.02, 'K_mig_gaz': 0.9},
    'МК2': {'R_mig_nef': 0.05, 'K_mig_gaz': 0.9},
    'МК3': {'R_mig_nef': 0.32, 'K_mig_gaz': 0.9},
    'МК4': {'R_mig_nef': 0.56, 'K_mig_gaz': 0.9},
    'МК5': {'R_mig_nef': 0.65, 'K_mig_gaz': 0.9},
    'АК1': {'R_mig_nef': 0.85, 'K_mig_gaz': 0.9},
    'АК2': {'R_mig_nef': 0.85, 'K_mig_gaz': 0.9},
    'АК3': {'R_mig_nef': 0.9,  'K_mig_gaz': 0.9},
}


#Данные для расчета скорости миграции
speed_migration = {
    "нефть": {
        "0°30'": {
            0.001: 0.4,
            0.01: 4.8,
            0.05: 24.0,
            0.1: 47.9
        },
        "5°00'": {
            0.001: 4.8,
            0.01: 48.0,
            0.05: 240.0,
            0.1: 490.6
        },
        "10°": {
            0.001: 9.5,
            0.01: 95.6,
            0.05: 478.5,
            0.1: 956.9
        },
        "30°": {
            0.001: 27.5,
            0.01: 275.6,
            0.05: 1378.0,
            0.1: 2756.2
        }
    },
    "газ": {
        "0°30'": {
            0.001: 36.5,
            0.01: 365.4,
            0.05: 1827.0,
            0.1: 3654.0
        },
        "5°00'": {
            0.001: 366.2,
            0.01: 3662.4,
            0.05: 18312.0,
            0.1: 36624.0
        },
        "10°": {
            0.001: 729.1,
            0.01: 7291.2,
            0.05: 36456.0,
            0.1: 72912.0
        },
        "30°": {
            0.001: 2100.0,
            0.01: 21100.0,
            0.05: 105500.0,
            0.1: 211000.0
        }
    }
}



class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# Функция расчета площади контура (метод Гаусса)
def calculate_area(points):
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0

# Функция расчета объемов/плотностей с учетом эмиграции для нефти и газа
def run_simulation_range(start_level, end_level, c_min, c_avg, c_max,
                         h_min, h_avg, h_max, c_dist_type, h_dist_type,
                         custom_rho, rho_value, custom_params, C_star_val,
                         M_ost_val, K_gen_oil_val, K_gen_gas_val,
                         R_mig_nef_val, K_mig_gaz_val, mode, catagenesis_data,
                         migration_data, org_type, area=None, N=1000,
                         oil_divisor=1e6, gas_divisor=1e9):
    start_idx = catagenesis_levels.index(start_level)
    end_idx = catagenesis_levels.index(end_level)
    if start_idx > end_idx:
        messagebox.showerror("Ошибка", "Начальный уровень должен быть ≤ конечного")
        return None, None

    # Генерация C_org и h_mp с учетом выбранного типа распределения
    C_org = generate_random_values(c_dist_type, c_min, c_avg, c_max, N)
    rho_mp = np.full(N, rho_value) if custom_rho else 2.3
    h_mp = generate_random_values(h_dist_type, h_min, h_avg, h_max, N)

    levels = catagenesis_levels[start_idx:end_idx + 1]
    results_oil = []
    results_gas = []

    for level in levels:
        if custom_params:
            C_star, M_ost = C_star_val, M_ost_val
            K_oil, K_gas = K_gen_oil_val, K_gen_gas_val
            R_mig_nef_base, K_mig_gaz_base = R_mig_nef_val, K_mig_gaz_val
        else:
            params = catagenesis_data[level]
            C_star, M_ost = params['C_star'], params['M_ost']
            K_oil, K_gas = params['K_gen_oil'], params['K_gen_gas']
            migration_params = migration_data[level]
            R_mig_nef_base, K_mig_gaz_base = migration_params['R_mig_nef'], migration_params['K_mig_gaz']

        # Генерация случайных коэффициентов с разбросом в зависимости от типа вещества
        if org_type == "Сапропелевый":
            R_mig_nef = np.random.uniform(R_mig_nef_base * 0.85, R_mig_nef_base * 1.15, N)
            K_mig_gaz = np.random.uniform(K_mig_gaz_base * 0.85, K_mig_gaz_base * 1.15, N)
        elif org_type == "Гуммусовый":
            R_mig_nef = np.random.uniform(R_mig_nef_base * 0.85, R_mig_nef_base, N)
            K_mig_gaz = np.random.uniform(K_mig_gaz_base * 0.85, K_mig_gaz_base * 1.15, N)
        elif org_type == "Смешанный":
            R_mig_nef = np.random.uniform(R_mig_nef_base * 0.90, R_mig_nef_base * 1.10, N)
            K_mig_gaz = np.random.uniform(K_mig_gaz_base * 0.90, K_mig_gaz_base * 1.10, N)
        else:
            raise ValueError("Неизвестный тип органического вещества")

        # Плотность генерации нефти и газа с учетом выбранных единиц
        q_oil_gen = ((C_org * rho_mp * h_mp * K_oil * 1e5) / (C_star * M_ost)) / oil_divisor
        q_gas_gen = ((C_org * rho_mp * h_mp * K_gas * 1e9) / (C_star * M_ost)) / gas_divisor

        # Плотность эмиграции нефти и газа с использованием случайных коэффициентов
        q_oil_emig_density = q_oil_gen * R_mig_nef
        q_gas_emig_density = q_gas_gen * K_mig_gaz

        # Объемы генерации и эмиграции
        if area is not None:
            area_km2 = area
            q_oil_gen_volume = q_oil_gen * area_km2
            q_gas_gen_volume = q_gas_gen * area_km2
            q_oil_emig_volume = q_oil_emig_density * area_km2
            q_gas_emig_volume = q_gas_emig_density * area_km2
        else:
            q_oil_gen_volume = None
            q_gas_gen_volume = None
            q_oil_emig_volume = None
            q_gas_emig_volume = None

        # Выбор результата в зависимости от режима
        if mode == "gen_density":
            res_oil = q_oil_gen
            res_gas = q_gas_gen
        elif mode == "gen_volume":
            if area is None:
                messagebox.showerror("Ошибка", "Для расчета объема необходима площадь")
                return None, None
            res_oil = q_oil_gen_volume
            res_gas = q_gas_gen_volume
        elif mode == "emig_density":
            res_oil = q_oil_emig_density
            res_gas = q_gas_emig_density
        elif mode == "emig_volume":
            if area is None:
                messagebox.showerror("Ошибка", "Для расчета объема необходима площадь")
                return None, None
            res_oil = q_oil_emig_volume
            res_gas = q_gas_emig_volume
        else:
            res_oil = q_oil_gen
            res_gas = q_gas_gen

        results_oil.append((level, res_oil))
        results_gas.append((level, res_gas))

    return results_oil, results_gas

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Объёмно-генетический метод с оцифровкой карт")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)

        self.tab_main = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text="Основные параметры")
        self.tab_map = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_map, text="Оцифровка карт")
        self.tab_accumulation = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_accumulation, text="Объём аккумуляции")
        self.tab_migration = ttk.Frame(self.notebook)  # Новая вкладка
        self.notebook.add(self.tab_migration, text="Скорость миграции")

        self.init_main_tab()
        self.init_map_tab()
        self.init_accumulation_tab()
        self.init_migration_tab()  # Инициализация новой вкладки

        self.scale = None
        self.contours_data = {}
        self.emigration_results = None  # Для хранения результатов эмиграции
        self.migration_speed = None
        self.current_contour = []

        # Добавляем переменные для масштабирования
        self.scale_factor = 1.0  # Начальный масштаб
        self.min_scale = 0.1  # Минимальный масштаб
        self.max_scale = 10.0  # Максимальный масштаб
        self.scale_step = 0.1  # Шаг изменения масштаба

    def init_main_tab(self):
        # Режим расчета
        mode_frame = ttk.Frame(self.tab_main)
        mode_frame.pack(padx=10, pady=5, anchor='w')
        self.calc_mode_var = tk.StringVar(value="params")
        ttk.Radiobutton(mode_frame, text="По параметрам", variable=self.calc_mode_var, value="params",
                        command=self.toggle_mode).pack(side='left')
        ttk.Radiobutton(mode_frame, text="С карты", variable=self.calc_mode_var, value="map",
                        command=self.toggle_mode).pack(side='left')

        # Тип расчета
        gen_frame = ttk.Frame(self.tab_main)
        gen_frame.pack(padx=10, pady=5, anchor='w')
        self.mode_var = tk.StringVar(value="gen_density")
        ttk.Radiobutton(gen_frame, text="Плотность генерации", variable=self.mode_var, value="gen_density",
                        command=self.toggle_mode).pack(side='left')
        ttk.Radiobutton(gen_frame, text="Объем генерации", variable=self.mode_var, value="gen_volume",
                        command=self.toggle_mode).pack(side='left')
        ttk.Radiobutton(gen_frame, text="Плотность эмиграции", variable=self.mode_var, value="emig_density",
                        command=self.toggle_mode).pack(side='left')
        ttk.Radiobutton(gen_frame, text="Объем эмиграции", variable=self.mode_var, value="emig_volume",
                        command=self.toggle_mode).pack(side='left')

        # Единицы измерения
        units_frame = ttk.Frame(self.tab_main)
        units_frame.pack(padx=10, pady=5, anchor='w')
        ttk.Label(units_frame, text="Единицы для нефти").grid(row=0, column=0, sticky='w')
        self.oil_unit_var = tk.StringVar(value="млн т/км²")
        ttk.Combobox(units_frame, textvariable=self.oil_unit_var, values=["млн т/км²", "тыс т/км²", "млрд т/км²"],
                     state='readonly').grid(row=0, column=1)
        ttk.Label(units_frame, text="Единицы для газа").grid(row=1, column=0, sticky='w')
        self.gas_unit_var = tk.StringVar(value="млрд м³/км²")
        ttk.Combobox(units_frame, textvariable=self.gas_unit_var, values=["млрд м³/км²", "млн м³/км²", "трлн м³/км²"],
                     state='readonly').grid(row=1, column=1)

        # Параметры
        frame1 = ttk.Frame(self.tab_main)
        frame1.pack(padx=10, pady=10)

        # Start level
        ttk.Label(frame1, text="Начальный уровень").grid(row=1, column=0, sticky='w')
        self.start_var = tk.StringVar(value=catagenesis_levels[0])
        self.start_combobox = ttk.Combobox(frame1, textvariable=self.start_var, values=catagenesis_levels,
                                           state='readonly')
        self.start_combobox.grid(row=1, column=1)

        ttk.Button(frame1, text="Запустить расчет", command=self.run_simulation).grid(row=0, column=0, columnspan=2,
                                                                                      pady=5)
        # End level
        ttk.Label(frame1, text="Конечный уровень").grid(row=2, column=0, sticky='w')
        self.end_var = tk.StringVar(value=catagenesis_levels[-1])
        self.end_combobox = ttk.Combobox(frame1, textvariable=self.end_var, values=catagenesis_levels, state='readonly')
        self.end_combobox.grid(row=2, column=1)

        # Organic type
        ttk.Label(frame1, text="Тип органического вещества").grid(row=3, column=0, sticky='w')
        self.org_type_var = tk.StringVar(value="Сапропелевый")
        self.org_type_combobox = ttk.Combobox(frame1, textvariable=self.org_type_var,
                                              values=["Сапропелевый", "Гуммусовый", "Смешанный"], state='readonly')
        self.org_type_combobox.grid(row=3, column=1)

        # Area input (hidden by default)
        self.area_label = ttk.Label(frame1, text="Площадь, км²")
        self.area_label.grid(row=4, column=0, sticky='w')
        self.area_label.grid_remove()
        self.area_entry = ttk.Entry(frame1, width=10)
        self.area_entry.grid(row=4, column=1)
        self.area_entry.grid_remove()

        # C_org min
        ttk.Label(frame1, text="Cорг min (%)").grid(row=5, column=0, sticky='w')
        self.c_min = ttk.Entry(frame1)
        self.c_min.grid(row=5, column=1)
        self.c_min.insert(0, "1.5")

        # C_org avg
        ttk.Label(frame1, text="Cорг ср (%)").grid(row=6, column=0, sticky='w')
        self.c_avg = ttk.Entry(frame1)
        self.c_avg.grid(row=6, column=1)
        self.c_avg.insert(0, "2.5")

        # C_org max
        ttk.Label(frame1, text="Cорг max (%)").grid(row=7, column=0, sticky='w')
        self.c_max = ttk.Entry(frame1)
        self.c_max.grid(row=7, column=1)
        self.c_max.insert(0, "4.0")

        # h_mp min
        ttk.Label(frame1, text="h_мп min (м)").grid(row=8, column=0, sticky='w')
        self.h_min = ttk.Entry(frame1)
        self.h_min.grid(row=8, column=1)
        self.h_min.insert(0, "50")

        # h_mp avg
        ttk.Label(frame1, text="h_мп ср (м)").grid(row=9, column=0, sticky='w')
        self.h_avg = ttk.Entry(frame1)
        self.h_avg.grid(row=9, column=1)
        self.h_avg.insert(0, "100")

        # h_mp max
        ttk.Label(frame1, text="h_мп max (м)").grid(row=10, column=0, sticky='w')
        self.h_max = ttk.Entry(frame1)
        self.h_max.grid(row=10, column=1)
        self.h_max.insert(0, "150")

        # Custom rho
        self.custom_rho = tk.BooleanVar()
        self.custom_rho_check = ttk.Checkbutton(frame1, text="Собственная плотность ρ_мп", variable=self.custom_rho,
                                                command=self.toggle_rho_entry)
        self.custom_rho_check.grid(row=11, column=0, columnspan=2, sticky='w')

        # Rho entry (hidden by default)
        self.rho_label = ttk.Label(frame1, text="ρ_мп (т/м³)")
        self.rho_label.grid(row=12, column=0, sticky='w')
        self.rho_label.grid_remove()
        self.rho_entry = ttk.Entry(frame1)
        self.rho_entry.grid(row=12, column=1)
        self.rho_entry.insert(0, "2.3")
        self.rho_entry.grid_remove()

        # Number of iterations
        ttk.Label(frame1, text="Количество итераций").grid(row=13, column=0, sticky='w')
        self.n_iter_entry = ttk.Entry(frame1)
        self.n_iter_entry.grid(row=13, column=1)
        self.n_iter_entry.insert(0, "1000")

        # Добавляем выбор типа распределения для C_org
        ttk.Label(frame1, text="Тип распределения для C_org").grid(row=14, column=0, sticky='w')
        self.c_dist_var = tk.StringVar(value="Нормальное")
        self.c_dist_combobox = ttk.Combobox(frame1, textvariable=self.c_dist_var,
                                            values=["Треугольное", "Нормальное", "Логнормальное",
                                                    "Парето", "Равномерное", "Бета"],
                                            state='readonly')
        self.c_dist_combobox.grid(row=14, column=1)

        # Добавляем выбор типа распределения для h_mp
        ttk.Label(frame1, text="Тип распределения для h_mp").grid(row=15, column=0, sticky='w')
        self.h_dist_var = tk.StringVar(value="Нормальное")
        self.h_dist_combobox = ttk.Combobox(frame1, textvariable=self.h_dist_var,
                                            values=["Треугольное", "Нормальное", "Логнормальное",
                                                    "Парето", "Равномерное", "Бета"],
                                            state='readonly')
        self.h_dist_combobox.grid(row=15, column=1)

        # Пользовательские параметры катагенеза
        frame2 = ttk.Frame(self.tab_main)
        frame2.pack(padx=10, pady=10)
        self.custom_params = tk.BooleanVar()
        chk_custom = ttk.Checkbutton(frame2, text="Задать свои C*, M_ост, K_gen, K_mig", variable=self.custom_params)
        chk_custom.grid(row=0, column=0, columnspan=2, sticky='w')
        ToolTip(chk_custom,
                "Коэффициенты для различных типов органического вещества и градаций катагенеза\nвзяты из:\n"
                "Неручев С. Г. и др. Оценка потенциальных ресурсов углеводородов на основе\n"
                "моделирования процессов их генерации, миграции и аккумуляции. СПб.: Недра, 2006. – 364 с.")
        ttk.Label(frame2, text="C*").grid(row=1, column=0, sticky='w')
        self.C_star_entry = ttk.Entry(frame2)
        self.C_star_entry.grid(row=1, column=1)
        self.C_star_entry.insert(0, "82.2")
        ttk.Label(frame2, text="M_ост").grid(row=2, column=0, sticky='w')
        self.M_ost_entry = ttk.Entry(frame2)
        self.M_ost_entry.grid(row=2, column=1)
        self.M_ost_entry.insert(0, "27")
        ttk.Label(frame2, text="K_gen_neft").grid(row=3, column=0, sticky='w')
        self.K_oil_entry = ttk.Entry(frame2)
        self.K_oil_entry.grid(row=3, column=1)
        self.K_oil_entry.insert(0, "28.24")
        ttk.Label(frame2, text="K_gen_gas").grid(row=4, column=0, sticky='w')
        self.K_gas_entry = ttk.Entry(frame2)
        self.K_gas_entry.grid(row=4, column=1)
        self.K_gas_entry.insert(0, "4")
        ttk.Label(frame2, text="K_mig_nef").grid(row=5, column=0, sticky='w')
        self.R_mig_nef_entry = ttk.Entry(frame2)
        self.R_mig_nef_entry.grid(row=5, column=1)
        self.R_mig_nef_entry.insert(0, "0.001")
        ttk.Label(frame2, text="K_mig_gaz").grid(row=6, column=0, sticky='w')
        self.K_mig_gaz_entry = ttk.Entry(frame2)
        self.K_mig_gaz_entry.grid(row=6, column=1)
        self.K_mig_gaz_entry.insert(0, "0.0001")

        # Визуализация
        viz_frame = ttk.Frame(self.tab_main)
        viz_frame.pack(padx=10, pady=5, anchor='w')
        ttk.Label(viz_frame, text="Визуализация для нефти").grid(row=0, column=0, sticky='w')
        self.viz_oil_var = tk.StringVar(value="Histogram")
        ttk.Combobox(viz_frame, textvariable=self.viz_oil_var,
                     values=["Histogram", "Box Plot", "Violin Plot", "Percentiles P10, P50, P90", "CDF", "P-curves"],
                     state='readonly'
                     ).grid(row=0, column=1)

        ttk.Label(viz_frame, text="Визуализация для газа").grid(row=1, column=0, sticky='w')
        self.viz_gas_var = tk.StringVar(value="Histogram")
        ttk.Combobox(viz_frame, textvariable=self.viz_gas_var,
                     values=["Histogram", "Box Plot", "Violin Plot", "Percentiles P10, P50, P90", "CDF", "P-curves"],
                     state='readonly'
                     ).grid(row=1, column=1)

    def toggle_mode(self):
        if self.mode_var.get() in ("gen_volume", "emig_volume") and self.calc_mode_var.get() == "params":
            self.area_label.grid()
            self.area_entry.grid()
        else:
            self.area_label.grid_remove()
            self.area_entry.grid_remove()

    def toggle_rho_entry(self):
        if self.custom_rho.get():
            self.rho_label.grid()
            self.rho_entry.grid()
        else:
            self.rho_label.grid_remove()
            self.rho_entry.grid_remove()

    def init_map_tab(self):
        # Создаем фрейм для кнопок слева
        button_frame = ttk.Frame(self.tab_map)
        button_frame.pack(side='left', fill='y')

        # Кнопка загрузки изображения
        self.load_button = tk.Button(button_frame, text="Загрузить изображение", command=self.load_image)
        self.load_button.pack(pady=5)

        # Кнопка задания масштаба
        self.set_scale_button = tk.Button(button_frame, text="Задать масштаб", command=self.set_scale)
        self.set_scale_button.pack(pady=5)

        # Кнопки масштабирования
        zoom_frame = ttk.Frame(button_frame)
        zoom_frame.pack(pady=5)
        ttk.Button(zoom_frame, text="Приблизить", command=self.zoom_in).pack(side='top')
        ttk.Button(zoom_frame, text="Отдалить", command=self.zoom_out).pack(side='top')

        # Комбобокс для уровня катагенеза
        ttk.Label(button_frame, text="Уровень катагенеза").pack(pady=5)
        self.contour_level = tk.StringVar(value=catagenesis_levels[0])
        ttk.Combobox(button_frame, textvariable=self.contour_level, values=catagenesis_levels, state='readonly').pack()

        # Кнопка завершения контура
        self.finish_button = tk.Button(button_frame, text="Завершить контур", command=self.finish_contour)
        self.finish_button.pack(pady=5)

        # Кнопка показа данных контуров
        self.show_data_button = tk.Button(button_frame, text="Показать данные контуров", command=self.show_contour_data)
        self.show_data_button.pack(pady=5)

        # Холст для изображения с отступом сверху
        self.canvas = tk.Canvas(self.tab_map, width=600, height=400)
        self.canvas.pack(side='left', fill='both', expand=True, pady=(20, 0))  # Добавлен отступ сверху 20 пикселей


    def zoom_in(self):
        """Увеличение масштаба изображения"""
        new_scale = self.scale_factor + self.scale_step
        if new_scale <= self.max_scale:
            self.scale_factor = new_scale
            self.update_image()

    def zoom_out(self):
        """Уменьшение масштаба изображения"""
        new_scale = self.scale_factor - self.scale_step
        if new_scale >= self.min_scale:
            self.scale_factor = new_scale
            self.update_image()

    def update_image(self):
        """Обновление изображения на холсте с учетом текущего масштаба"""
        if self.image:
            # Рассчитываем новые размеры изображения
            new_width = int(self.image.width * self.scale_factor)
            new_height = int(self.image.height * self.scale_factor)
            # Изменяем размер изображения
            resized_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            # Обновляем холст
            self.canvas.config(width=new_width, height=new_height)
            self.canvas.delete("all")  # Очищаем холст перед отрисовкой
            self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
            # Перерисовываем существующие контуры и точки с учетом масштаба
            self.redraw_contours()


    def redraw_contours(self):
        """Перерисовка всех контуров с учетом текущего масштаба"""
        for level, contours in self.contours_data.items():
            for contour in contours:
                points = contour.get('points', [])
                if points:
                    scaled_points = [(x * self.scale_factor, y * self.scale_factor) for x, y in points]
                    for i, (x, y) in enumerate(scaled_points):
                        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')
                        if i > 0:
                            self.canvas.create_line(scaled_points[i-1], scaled_points[i], fill='blue')
                    if len(scaled_points) > 2:
                        self.canvas.create_line(scaled_points[-1], scaled_points[0], fill='blue')

    def init_accumulation_tab(self):
        # Площадь
        ttk.Label(self.tab_accumulation, text="Площадь, км²").grid(row=0, column=0, sticky='w')
        self.accumulation_area_entry = ttk.Entry(self.tab_accumulation)
        self.accumulation_area_entry.grid(row=0, column=1)

        # Коэффициент аккумуляции
        ttk.Label(self.tab_accumulation, text="Коэффициент аккумуляции min (%)").grid(row=1, column=0, sticky='w')
        self.accumulation_coeff_min = ttk.Entry(self.tab_accumulation)
        self.accumulation_coeff_min.grid(row=1, column=1)
        self.accumulation_coeff_min.insert(0, "1.0")

        ttk.Label(self.tab_accumulation, text="Коэффициент аккумуляции max (%)").grid(row=2, column=0, sticky='w')
        self.accumulation_coeff_max = ttk.Entry(self.tab_accumulation)
        self.accumulation_coeff_max.grid(row=2, column=1)
        self.accumulation_coeff_max.insert(0, "2.0")

        ttk.Label(self.tab_accumulation, text="Шаг коэффициента аккумуляции (%)").grid(row=3, column=0, sticky='w')
        self.accumulation_coeff_step = ttk.Entry(self.tab_accumulation)
        self.accumulation_coeff_step.grid(row=3, column=1)
        self.accumulation_coeff_step.insert(0, "0.1")

        # Кнопка для запуска расчета
        ttk.Button(self.tab_accumulation, text="Рассчитать объём аккумуляции",
                   command=self.calculate_accumulation).grid(row=4, column=0, columnspan=2, pady=10)

    def init_migration_tab(self):
        """Инициализация вкладки 'Скорость миграции' с полями ввода."""

        # Коэффициент проницаемости поровой среды
        ttk.Label(self.tab_migration, text="Коэффициент проницаемости (безразмерная)").grid(row=0, column=0, sticky='w')
        self.k_entry = ttk.Entry(self.tab_migration)
        self.k_entry.grid(row=0, column=1)
        self.k_entry.insert(0, "0.1")

        ttk.Label(self.tab_migration, text="Фазовая проницаемость (мк м2)").grid(row=1, column=0, sticky='w')
        self.pron_entry = ttk.Entry(self.tab_migration)
        self.pron_entry.grid(row=1, column=1)
        self.pron_entry.insert(0, "1")
        # Вязкость нефти
        ttk.Label(self.tab_migration, text="Вязкость нефти (Па·с)").grid(row=2, column=0, sticky='w')
        self.mu_entry = ttk.Entry(self.tab_migration)
        self.mu_entry.grid(row=2, column=1)
        self.mu_entry.insert(0, "0.001")

        # Плотность минерализованной воды
        ttk.Label(self.tab_migration, text="Плотность воды (т/м³)").grid(row=3, column=0, sticky='w')
        self.rho_water_entry = ttk.Entry(self.tab_migration)
        self.rho_water_entry.grid(row=3, column=1)
        self.rho_water_entry.insert(0, "1.0")

        # Плотность нефти
        ttk.Label(self.tab_migration, text="Плотность нефти (т/м³)").grid(row=4, column=0, sticky='w')
        self.rho_oil_entry = ttk.Entry(self.tab_migration)
        self.rho_oil_entry.grid(row=4, column=1)
        self.rho_oil_entry.insert(0, "0.800")

        # Пористость коллектора
        ttk.Label(self.tab_migration, text="Пористость (%)").grid(row=5, column=0, sticky='w')
        self.phi_entry = ttk.Entry(self.tab_migration)
        self.phi_entry.grid(row=5, column=1)
        self.phi_entry.insert(0, "20")

        # Угол наклона пласта
        ttk.Label(self.tab_migration, text="Угол наклона (градусы)").grid(row=6, column=0, sticky='w')
        self.alpha_entry = ttk.Entry(self.tab_migration)
        self.alpha_entry.grid(row=6, column=1)
        self.alpha_entry.insert(0, "5")

        # Время
        ttk.Label(self.tab_migration, text="Время (млн. лет)").grid(row=7, column=0, sticky='w')
        self.time_entry = ttk.Entry(self.tab_migration)
        self.time_entry.grid(row=7, column=1)
        self.time_entry.insert(0, "10")

        # Кнопка для расчета скорости миграции
        ttk.Button(self.tab_migration, text="Рассчитать скорость миграции",
                   command=self.calculate_migration).grid(row=8, column=0, columnspan=2, pady=5)

        # Кнопка для расчета расстояния миграции
        ttk.Button(self.tab_migration, text="Рассчитать расстояние миграции",
                   command=self.calculate_migration_distance).grid(row=9, column=0, columnspan=2, pady=5)

    def calculate_migration(self):
        """Расчет истинной линейной скорости миграции с учетом вариаций параметров и выбранных распределений."""
        try:
            # Считываем средние значения
            k_avg = float(self.k_entry.get())
            pron_avg = float(self.pron_entry.get())
            mu_avg = float(self.mu_entry.get())
            rho_water_avg = float(self.rho_water_entry.get())
            rho_oil_avg = float(self.rho_oil_entry.get())
            phi_avg = float(self.phi_entry.get()) / 100  # Переводим в доли
            alpha_avg = float(self.alpha_entry.get())
            g = 9.81  # Ускорение свободного падения, м/с²
            N = 10000  # Количество итераций для вариаций
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте значения полей")
            return

        # Определяем min и max для каждого параметра
        k_min, k_max = k_avg * 0.75, k_avg * 1.25
        pron_min, pron_max = pron_avg * 0.75, pron_avg * 1.25
        mu_min = mu_avg * 0.75
        mu_max = mu_avg * 1.25
        rho_water_min, rho_water_max = max(1.0, rho_water_avg * 0.75), rho_water_avg * 1.25
        rho_oil_min = max(0.730, rho_oil_avg * 0.75)
        rho_oil_max = min(0.99, rho_oil_avg * 1.25)
        phi_min, phi_max = phi_avg * 0.65, phi_avg * 1.35  # ±35%
        alpha_min, alpha_max = alpha_avg * 0.75, alpha_avg * 1.25

        # Генерация случайных значений для каждого параметра с учетом выбранного типа распределения
        k_var = np.random.normal(k_avg, (k_max - k_min) / 4, N)
        pron_var = np.random.normal(pron_avg, (pron_max - pron_min) / 4, N)
        mu_var = np.random.normal(mu_avg, (mu_max - mu_min) / 4, N)
        rho_water_var = np.random.normal(rho_water_avg, (rho_water_max - rho_water_min) / 4, N)
        rho_oil_var = np.random.normal(rho_oil_avg, (rho_oil_max - rho_oil_min) / 4, N)
        phi_var = np.random.normal(phi_avg, (phi_max - phi_min) / 4, N)
        alpha_var = np.random.normal(alpha_avg, (alpha_max - alpha_min) / 4, N)

        # Предполагаем, что фазовая проницаемость нефти (kr_oil) = 1 для упрощения

        # Расчет скорости миграции
        v_raw = (pron_var*10**-6 * k_var * (rho_water_var - rho_oil_var) * g * np.sin(np.radians(alpha_var)) * 10 ** 6) / (
                    mu_var * phi_var)
        v = np.maximum(v_raw, 0)

        self.migration_speed = v

        # Визуализация результатов
        self.plot_migration(v)

    def calculate_migration_distance(self):
        """Расчет расстояния миграции на основе скорости и времени."""
        if self.migration_speed is None:
            messagebox.showerror("Ошибка", "Сначала выполните расчет скорости миграции")
            return

        try:
            time_million_years = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте значение времени")
            return

        # Расчет расстояния миграции (скорость в км/млн. лет * время в млн. лет)
        distance = self.migration_speed * time_million_years

        # Визуализация результатов
        self.plot_migration_distance(distance)


    def plot_migration(self, v):
        """Визуализация распределения скорости миграции."""
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(v, bins=50, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Скорость миграции (км/млн. лет)')
        ax.set_ylabel('Частота')
        ax.set_title('Распределение скорости миграции')
        plt.show()

    def plot_migration_distance(self, distance):
        """Визуализация распределения расстояния миграции."""
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(distance, bins=50, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Расстояние миграции (км)')
        ax.set_ylabel('Частота')
        ax.set_title('Распределение расстояния миграции')
        plt.show()

    def calculate_migration_distance(self):
        """Расчет расстояния миграции на основе скорости и времени."""
        if self.migration_speed is None:
            messagebox.showerror("Ошибка", "Сначала выполните расчет скорости миграции")
            return

        try:
            time_million_years = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте значение времени")
            return

        # Существующий расчет расстояния миграции на основе ранее вычисленной скорости
        distance = self.migration_speed * time_million_years

        # Визуализация существующего распределения расстояния миграции
        self.plot_migration_distance(distance)

        # Расчет и построение двух отдельных графиков на основе speed_migration
        try:
            alpha = float(self.alpha_entry.get())
            k = float(self.k_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте значения alpha и k")
            return

        # Словарь углов наклона: строковые ключи соответствуют числовым значениям в градусах
        angles = {
            "0°30'": 0.5,
            "5°00'": 5.0,
            "10°": 10.0,
            "30°": 30.0
        }

        # Доступные значения k из speed_migration
        k_values = [0.001, 0.01, 0.05, 0.1]

        # Нахождение ближайшего значения alpha
        closest_alpha_str = min(angles, key=lambda x: abs(angles[x] - alpha))

        # Нахождение ближайшего значения k
        closest_k = min(k_values, key=lambda x: abs(x - k))

        # Извлечение скоростей миграции из speed_migration для нефти и газа
        speed_oil = speed_migration["нефть"][closest_alpha_str][closest_k]
        speed_gas = speed_migration["газ"][closest_alpha_str][closest_k]

        # Создание массива времени от 0 до time_million_years с шагом 1 млн. лет
        time_array = np.arange(0, time_million_years + 1, 1)

        # Расчет расстояния миграции для нефти и газа для каждого момента времени
        distance_oil = speed_oil * time_array
        distance_gas = speed_gas * time_array

        # Построение графика для нефти
        plt.figure()
        plt.plot(time_array, distance_oil, label='Нефть', color='blue')
        plt.xlabel('Время (млн. лет)')
        plt.ylabel('Расстояние миграции (км)')
        plt.title('Динамика расстояния миграции нефти от времени')
        plt.grid(True)
        plt.legend()

        # Построение графика для газа
        plt.figure()
        plt.plot(time_array, distance_gas, label='Газ', color='green')
        plt.xlabel('Время (млн. лет)')
        plt.ylabel('Расстояние миграции (км)')
        plt.title('Динамика расстояния миграции газа от времени')
        plt.grid(True)
        plt.legend()

        # Отображение обоих графиков
        plt.show()

    def load_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg")])
        if image_path:
            self.original_image = Image.open(image_path)  # Сохраняем исходное изображение
            original_width, original_height = self.original_image.size
            max_width, max_height = 700, 400
            aspect_ratio = original_width / original_height
            canvas_ratio = max_width / max_height
            if aspect_ratio > canvas_ratio:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            self.image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.config(width=new_width, height=new_height)
            self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
            self.canvas.bind("<Button-1>", self.add_point)
            self.scale_factor = 1.0  # Сбрасываем масштаб при загрузке нового изображения

    def set_scale(self):
        self.scale_points = []
        self.canvas.bind("<Button-1>", self.add_scale_point)
        messagebox.showinfo("Инструкция", "Кликните по двум точкам на изображении для задания масштаба.")

    def add_scale_point(self, event):
        x, y = event.x, event.y
        self.scale_points.append((x, y))
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='green')
        if len(self.scale_points) == 2:
            self.canvas.create_line(self.scale_points[0], self.scale_points[1], fill='green')
            self.calculate_scale()

    def calculate_scale(self):
        if len(self.scale_points) != 2:
            return
        p1, p2 = self.scale_points
        pixel_distance = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        km = simpledialog.askfloat("Ввод", "Введите количество километров для этой линии:")
        if km:
            self.scale = km / pixel_distance
            messagebox.showinfo("Успех", f"Масштаб установлен: {self.scale:.6f} км/пиксель")
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.add_point)

    def add_point(self, event):
        """Добавление точки с учетом текущего масштаба"""
        x, y = event.x / self.scale_factor, event.y / self.scale_factor  # Корректируем координаты
        self.current_contour.append((x, y))
        scaled_x, scaled_y = event.x, event.y
        self.canvas.create_oval(scaled_x - 3, scaled_y - 3, scaled_x + 3, scaled_y + 3, fill='red')
        if len(self.current_contour) > 1:
            prev_x, prev_y = self.current_contour[-2]
            self.canvas.create_line(
                prev_x * self.scale_factor, prev_y * self.scale_factor,
                x * self.scale_factor, y * self.scale_factor,
                fill='blue'
            )

    def finish_contour(self):
        # Проверка на минимальное количество точек
        if len(self.current_contour) < 3:
            messagebox.showerror("Ошибка", "Контур должен содержать минимум 3 точки")
            return

        # Получение уровня контура и расчет площади
        level = self.contour_level.get()
        area_pixels = calculate_area(self.current_contour)
        area_km2 = area_pixels * (self.scale ** 2) if self.scale else area_pixels

        # Ввод параметров контура
        params = self.input_contour_params()
        if not params:
            return

        # Сохранение данных контура
        if level not in self.contours_data:
            self.contours_data[level] = []
        contour_number = len(self.contours_data[level]) + 1
        self.contours_data[level].append({
            'number': contour_number,
            'area': area_km2,
            'c_min': params[0], 'c_avg': params[1], 'c_max': params[2],
            'h_min': params[3], 'h_avg': params[4], 'h_max': params[5],
            'points': self.current_contour[:]  # Сохранение копии точек контура
        })

        # Масштабирование точек и рисование линии
        scaled_points = [(x * self.scale_factor, y * self.scale_factor) for x, y in self.current_contour]
        self.canvas.create_line(scaled_points[-1], scaled_points[0], fill='blue')

        # Отображение информации о площади
        unit = "кв. км" if self.scale else "кв. пикселей"
        messagebox.showinfo("Площадь", f"Площадь контура {level} (контур {contour_number}): {area_km2:.2f} {unit}")

        # Очистка текущего контура после всех операций
        self.current_contour = []

    def input_contour_params(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Параметры контура")
        dialog.geometry("300x300")
        dialog.grab_set()

        entries = []
        labels = ["C_org min (%)", "C_org avg (%)", "C_org max (%)", "h_mp min (м)", "h_mp avg (м)", "h_mp max (м)"]
        defaults = ["1.5", "2.5", "4.0", "50", "100", "150"]
        for i, (label, default) in enumerate(zip(labels, defaults)):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, default)
            entries.append(entry)

        result = []

        def save_params():
            try:
                vals = [float(entry.get()) for entry in entries]
                if not (vals[0] <= vals[1] <= vals[2] and vals[3] <= vals[4] <= vals[5]):
                    raise ValueError
                result.extend(vals)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте значения параметров")

        ttk.Button(dialog, text="Сохранить", command=save_params).grid(row=6, column=0, columnspan=2, pady=10)
        dialog.wait_window()
        return result if result else None

    def show_contour_data(self):
        if not self.contours_data:
            messagebox.showinfo("Данные", "Нет сохраненных контуров")
            return
        text = "Данные контуров:\n"
        for level, contours in self.contours_data.items():
            text += f"\nУровень {level}:\n"
            for contour in contours:
                text += f"  Контур {contour['number']}: {contour['area']:.2f} кв. км, "
                text += f"C_org: {contour['c_min']}/{contour['c_avg']}/{contour['c_max']}, "
                text += f"h_mp: {contour['h_min']}/{contour['h_avg']}/{contour['h_max']}\n"
        messagebox.showinfo("Данные контуров", text)

    def run_simulation(self):
        try:
            rho_val = float(self.rho_entry.get()) if self.custom_rho.get() else None
            Cs = float(self.C_star_entry.get()) if self.custom_params.get() else None
            Mo = float(self.M_ost_entry.get()) if self.custom_params.get() else None
            Ko = float(self.K_oil_entry.get()) if self.custom_params.get() else None
            Kg = float(self.K_gas_entry.get()) if self.custom_params.get() else None
            R_mig_nef_val = float(self.R_mig_nef_entry.get()) if self.custom_params.get() else None
            K_mig_gaz_val = float(self.K_mig_gaz_entry.get()) if self.custom_params.get() else None
            N = int(self.n_iter_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте значения параметров")
            return

        viz_oil = self.viz_oil_var.get()
        viz_gas = self.viz_gas_var.get()

        org_type = self.org_type_var.get()
        if org_type == "Сапропелевый":
            catagenesis_data = sapropelic_catagenesis_data
            migration_data = migration
        elif org_type == "Гуммусовый":
            catagenesis_data = humic_catagenesis_data
            migration_data = migration
        else:  # "Смешанный"
            catagenesis_data = mixed_catagenesis_data
            migration_data = migration

        oil_divisors = {"млн т/км²": 1e6, "тыс т/км²": 1e3, "млрд т/км²": 1e9}
        gas_divisors = {"млрд м³/км²": 1e9, "млн м³/км²": 1e6, "трлн м³/км²": 1e12}
        oil_unit = self.oil_unit_var.get()
        gas_unit = self.gas_unit_var.get()
        oil_divisor = oil_divisors[oil_unit]
        gas_divisor = gas_divisors[gas_unit]

        c_dist_type = self.c_dist_var.get()
        h_dist_type = self.h_dist_var.get()

        if self.calc_mode_var.get() == "params":
            # Код для режима "params" остается без изменений
            try:
                vals = [float(x.get()) for x in
                        (self.c_min, self.c_avg, self.c_max, self.h_min, self.h_avg, self.h_max)]
                if not (vals[0] <= vals[1] <= vals[2] and vals[3] <= vals[4] <= vals[5]):
                    raise ValueError
                area = float(self.area_entry.get()) if self.mode_var.get() in ("gen_volume", "emig_volume") else None
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте значения полей")
                return

            results_oil, results_gas = run_simulation_range(
                self.start_var.get(), self.end_var.get(),
                vals[0], vals[1], vals[2], vals[3], vals[4], vals[5],
                c_dist_type, h_dist_type,
                self.custom_rho.get(), rho_val, self.custom_params.get(),
                Cs, Mo, Ko, Kg, R_mig_nef_val, K_mig_gaz_val, self.mode_var.get(),
                catagenesis_data, migration_data, org_type, area, N,
                oil_divisor=oil_divisor, gas_divisor=gas_divisor
            )

            self.emigration_results = {"oil": results_oil, "gas": results_gas}

            self.plot_results(results_oil, results_gas, viz_oil, viz_gas, "params")
        else:  # режим "map"
            if not self.contours_data:
                messagebox.showerror("Ошибка", "Нет данных о контурах")
                return

            all_results_oil = []
            all_results_gas = []
            summed_results_oil = {}
            summed_results_gas = {}

            # Расчет результатов для каждого контура и суммирование по уровням
            for level, contours in self.contours_data.items():
                summed_oil = None
                summed_gas = None
                for contour in contours:
                    res_oil, res_gas = run_simulation_range(
                        level, level,
                        contour['c_min'], contour['c_avg'], contour['c_max'],
                        contour['h_min'], contour['h_avg'], contour['h_max'],
                        c_dist_type, h_dist_type,
                        self.custom_rho.get(), rho_val, self.custom_params.get(),
                        Cs, Mo, Ko, Kg, R_mig_nef_val, K_mig_gaz_val, self.mode_var.get(),
                        catagenesis_data, migration_data, org_type,
                        contour['area'] if self.mode_var.get() in ("gen_volume", "emig_volume") else None, N,
                        oil_divisor=oil_divisor, gas_divisor=gas_divisor
                    )
                    label = f"{level} контур {contour['number']}"
                    all_results_oil.append((label, res_oil[0][1]))
                    all_results_gas.append((label, res_gas[0][1]))

                    # Суммирование значений для одинаковых уровней катагенеза
                    if self.mode_var.get() in ("gen_volume", "emig_volume"):
                        if summed_oil is None:
                            summed_oil = res_oil[0][1].copy()
                            summed_gas = res_gas[0][1].copy()
                        else:
                            summed_oil += res_oil[0][1]
                            summed_gas += res_gas[0][1]

                # Сохранение суммарных значений для уровня катагенеза
                if self.mode_var.get() in ("gen_volume", "emig_volume") and summed_oil is not None:
                    summed_results_oil[level] = summed_oil
                    summed_results_gas[level] = summed_gas

            # Визуализация для отдельных контуров
            self.plot_results(all_results_oil, all_results_gas, viz_oil, viz_gas, "map")

            # Визуализация суммарных значений для режимов gen_volume и emig_volume
            if self.mode_var.get() in ("gen_volume", "emig_volume") and summed_results_oil:
                summed_oil_list = [(level, summed_results_oil[level]) for level in summed_results_oil]
                summed_gas_list = [(level, summed_results_gas[level]) for level in summed_results_gas]
                self.plot_results(summed_oil_list, summed_gas_list, viz_oil, viz_gas, "map_summed")

            # Сохранение результатов для режима emig_volume
            if self.mode_var.get() == "emig_volume":
                self.emigration_results = {"oil": all_results_oil, "gas": all_results_gas}

            # Добавление суммирования всех значений для всех контуров и уровней
            total_oil = np.sum([res[1] for res in all_results_oil], axis=0)
            total_gas = np.sum([res[1] for res in all_results_gas], axis=0)

            # Построение гистограмм для суммарных значений
            self.plot_total_histograms(total_oil, total_gas, "map")

    def calculate_accumulation(self):
        if not self.emigration_results:
            messagebox.showerror("Ошибка",
                                 "Сначала выполните расчет объёма эмиграции на вкладке 'Основные параметры' или 'Оцифровка карт'")
            return

        try:
            area = float(self.accumulation_area_entry.get())   # Площадь в км²
            coeff_min = float(self.accumulation_coeff_min.get()) / 100  # Мин. коэффициент в долях
            coeff_max = float(self.accumulation_coeff_max.get()) / 100  # Макс. коэффициент в долях
            # Используем средний коэффициент как фиксированный
            coeff_fixed = (coeff_min + coeff_max) / 2
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте значения полей")
            return

        # Предполагаем, что все уровни имеют одинаковое количество симуляций N
        N = len(self.emigration_results["oil"][0][1])
        total_accum_oil = np.zeros(N)  # Массив для суммарных объемов нефти
        total_accum_gas = np.zeros(N)  # Массив для суммарных объемов газа

        # Суммируем эмиграционные объемы по всем уровням для каждого запуска симуляции
        for level, emig_oil in self.emigration_results["oil"]:
            total_accum_oil += np.array(emig_oil) * area * coeff_fixed
        for level, emig_gas in self.emigration_results["gas"]:
            total_accum_gas += np.array(emig_gas) * area * coeff_fixed

        # Передаем суммарные объемы для построения гистограммы
        self.plot_accumulation(total_accum_oil, total_accum_gas)

    def plot_total_histograms(self, total_oil, total_gas, mode):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Определение единиц измерения
        if self.mode_var.get() in ("gen_volume", "emig_volume"):
            unit_oil = self.oil_unit_var.get().replace("/км²", "")
            unit_gas = self.gas_unit_var.get().replace("/км²", "")
        else:
            unit_oil = self.oil_unit_var.get()
            unit_gas = self.gas_unit_var.get()

        # Гистограмма для нефти
        ax1.hist(total_oil, bins=50, alpha=0.7, edgecolor='black', label='Распределение')
        p10_oil, p50_oil, p90_oil = np.percentile(total_oil, [10, 50, 90])
        ax1.axvline(p10_oil, color='red', linestyle='--', label=f'P90 ({p10_oil:.1f})')
        ax1.axvline(p50_oil, color='green', linestyle='-', label=f'P50 ({p50_oil:.1f})')
        ax1.axvline(p90_oil, color='blue', linestyle='--', label=f'P10 ({p90_oil:.1f})')
        ax1.set_xlabel(f'Суммарный объём нефти ({unit_oil})')
        ax1.set_ylabel('Частота')
        ax1.set_title('Гистограмма суммарного объёма нефти')
        ax1.legend()

        # Гистограмма для газа
        ax2.hist(total_gas, bins=50, alpha=0.7, edgecolor='black', label='Распределение')
        p10_gas, p50_gas, p90_gas = np.percentile(total_gas, [10, 50, 90])
        ax2.axvline(p10_gas, color='red', linestyle='--', label=f'P90 ({p10_gas:.1f})')
        ax2.axvline(p50_gas, color='green', linestyle='-', label=f'P50 ({p50_gas:.1f})')
        ax2.axvline(p90_gas, color='blue', linestyle='--', label=f'P10 ({p90_gas:.1f})')
        ax2.set_xlabel(f'Суммарный объём газа ({unit_gas})')
        ax2.set_ylabel('Частота')
        ax2.set_title('Гистограмма суммарного объёма газа')
        ax2.legend()

        plt.tight_layout()
        plt.show()


    def plot_accumulation(self, total_accum_oil, total_accum_gas):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Единицы измерения без "/км²", так как это объемы
        oil_unit = self.oil_unit_var.get().replace("/км²", "")
        gas_unit = self.gas_unit_var.get().replace("/км²", "")

        # Гистограмма для нефти
        ax1.hist(total_accum_oil, bins=50, alpha=0.7, edgecolor='black', label='Распределение')
        p10_oil, p50_oil, p90_oil = np.percentile(total_accum_oil, [10, 50, 90])
        ax1.axvline(p10_oil, color='red', linestyle='--', label=f'P90 ({p10_oil:.1f})')
        ax1.axvline(p50_oil, color='green', linestyle='-', label=f'P50 ({p50_oil:.1f})')
        ax1.axvline(p90_oil, color='blue', linestyle='--', label=f'P10 ({p90_oil:.1f})')
        ax1.set_xlabel(f'Общий объём аккумуляции нефти ({oil_unit})')
        ax1.set_ylabel('Частота')
        ax1.set_title('Гистограмма общего объёма аккумуляции нефти')
        ax1.legend()

        # Гистограмма для газа
        ax2.hist(total_accum_gas, bins=50, alpha=0.7, edgecolor='black', label='Распределение')
        p10_gas, p50_gas, p90_gas = np.percentile(total_accum_gas, [10, 50, 90])
        ax2.axvline(p10_gas, color='red', linestyle='--', label=f'P90 ({p10_gas:.1f})')
        ax2.axvline(p50_gas, color='green', linestyle='-', label=f'P50 ({p50_gas:.1f})')
        ax2.axvline(p90_gas, color='blue', linestyle='--', label=f'P10 ({p90_gas:.1f})')
        ax2.set_xlabel(f'Общий объём аккумуляции газа ({gas_unit})')
        ax2.set_ylabel('Частота')
        ax2.set_title('Гистограмма общего объёма аккумуляции газа')
        ax2.legend()

        plt.tight_layout()
        plt.show()

    def plot_results(self, results_oil, results_gas, viz_oil, viz_gas, mode):
        if not results_oil or not results_gas:
            return

        if viz_oil == "Percentiles P10, P50, P90":
            self.show_percentiles(results_oil, "нефть")
        else:
            self.plot_visualization(results_oil, viz_oil, "нефть", mode)

        if viz_gas == "Percentiles P10, P50, P90":
            self.show_percentiles(results_gas, "газ")
        else:
            self.plot_visualization(results_gas, viz_gas, "газ", mode)

    def plot_visualization(self, results, viz_type, fluid, mode):
        n = len(results)
        fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
        axes = np.atleast_1d(axes)

        # Определяем unit в начале метода
        if self.mode_var.get() in ("gen_volume", "emig_volume"):
            unit = self.oil_unit_var.get().replace("/км²", "") if fluid == "нефть" else self.gas_unit_var.get().replace(
                "/км²", "")
        else:
            unit = self.oil_unit_var.get() if fluid == "нефть" else self.gas_unit_var.get()

        for i, (label, q) in enumerate(results):
            ax = axes[i]
            if viz_type == "Histogram":
                ax.hist(q, bins=50, alpha=0.7, edgecolor='black', label='Распределение')
                p10, p50, p90 = np.percentile(q, [10, 50, 90])
                ax.axvline(p10, color='red', linestyle='--', label=f'P90 ({p10:.1f})')
                ax.axvline(p50, color='green', linestyle='-', label=f'P50 ({p50:.1f})')
                ax.axvline(p90, color='blue', linestyle='--', label=f'P10 ({p90:.1f})')
                ax.legend()
            elif viz_type == "Box Plot":
                ax.boxplot(q, vert=False)
                ax.set_xlabel(f"q_{fluid[0]} ({unit})")
            elif viz_type == "Violin Plot":
                ax.violinplot(q, vert=False)
                ax.set_xlabel(f"q_{fluid[0]} ({unit})")
            elif viz_type == "CDF":
                ax.hist(q, bins=50, cumulative=True, density=True, alpha=0.7, edgecolor='black')
                ax.set_xlabel(f"q_{fluid[0]} ({unit})")
            elif viz_type == "P-curves":
                sorted_q = np.sort(q)
                p = np.arange(1, len(sorted_q) + 1) / len(sorted_q)
                ax.plot(sorted_q, p)
                ax.set_xlabel("Значение")
                ax.set_ylabel("Вероятность")
                p10, p50, p90 = np.percentile(q, [10, 50, 90])
                ax.axvline(p10, color='red', linestyle='--', label=f'P90') #({p10:.1f})')
                ax.axvline(p50, color='green', linestyle='-', label=f'P50') #({p50:.1f})')
                ax.axvline(p90, color='blue', linestyle='--', label=f'P10') #({p90:.1f})')
                ax.axhline(0.1, color='red', linestyle='--', linewidth=0.5)  # P10 (10%)
                ax.axhline(0.5, color='green', linestyle='-', linewidth=0.5)  # P50 (50%)
                ax.axhline(0.9, color='blue', linestyle='--', linewidth=0.5)  # P90 (90%)
                ax.legend()

            ax.set_title(f"{label} — {fluid}")
            ax.set_xlabel(f"q_{fluid[0]} ({unit})")

        title_map = {
            "gen_density": "Плотность генерации",
            "gen_volume": "Объём генерации",
            "emig_density": "Плотность эмиграции",
            "emig_volume": "Объём эмиграции"
        }
        title_type = title_map.get(mode, "")
        fig.suptitle(f"{title_type} ({viz_type})")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def show_percentiles(self, results, fluid):
        text = f"Процентили для {fluid}:\n"
        for label, q in results:
            p10, p50, p90 = np.percentile(q, [10, 50, 90])
            text += f"{label}: P90={p10:.1f}, P50={p50:.1f}, P10={p90:.1f}\n"
        messagebox.showinfo("Процентили", text)

def generate_random_values(dist_type, min_val, avg_val, max_val, N):
    if dist_type == "Треугольное":
        return np.random.triangular(min_val, avg_val, max_val, N)
    elif dist_type == "Нормальное":
        mean = avg_val
        std = (max_val - min_val) / 3
        a = (min_val - mean) / std
        b = (max_val - mean) / std
        # Генерируем значения из усеченного нормального распределения
        values = truncnorm.rvs(a, b, loc=mean, scale=std, size=N)
        return values
    elif dist_type == "Логнормальное":
        mu = np.log(avg_val)
        sigma = (np.log(max_val) - np.log(min_val)) / 4
        return np.random.lognormal(mu, sigma, N)
    elif dist_type == "Парето":
        xm = min_val
        alpha = 1 + np.log(avg_val / min_val)
        return (np.random.pareto(alpha, N) + 1) * xm
    elif dist_type == "Равномерное":
        return np.random.uniform(min_val, max_val, N)
    elif dist_type == "Бета":
        a, b = 2, 2
        beta_samples = np.random.beta(a, b, N)
        return min_val + (max_val - min_val) * beta_samples
    else:
        raise ValueError("Неизвестный тип распределения")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()