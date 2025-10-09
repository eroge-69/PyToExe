import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class HeatTransferCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчет теплопередачи цилиндрической стенки")
        self.root.geometry("800x700")
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка для ввода параметров
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="Входные параметры")
        
        # Вкладка для результатов
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Результаты")
        
        self.setup_input_tab()
        self.setup_results_tab()
        
    def setup_input_tab(self):
        # Создаем фреймы с прокруткой
        canvas = tk.Canvas(self.input_frame)
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Переменные для хранения ввода
        self.entries = {}
        
        # Параметры газа внутри трубки
        inner_frame = ttk.LabelFrame(self.scrollable_frame, text="Параметры газа ВНУТРИ трубки", padding=10)
        inner_frame.grid(row=0, column=0, sticky="we", padx=10, pady=5)
        
        params_inner = [
            ("G1", "Расход газа в трубке [кг/с]", "0.1"),
            ("mu1", "Динамическая вязкость газа в трубке [Па·с]", "2.1e-5"),
            ("T1_in", "Температура газа в трубке на входе [K]", "473.15"),  # 200°C в K
            ("w1", "Скорость потока в трубке [м/с]", "5"),
            ("cp1", "Изобарная теплоемкость газа в трубке [Дж/(кг·К)]", "1010"),
            ("rho1", "Плотность газа в трубке [кг/м³]", "0.8"),
            ("lambda_gas1", "Коэффициент теплопроводности газа в трубке [Вт/(м·К)]", "0.03")
        ]
        
        for i, (key, label, default) in enumerate(params_inner):
            ttk.Label(inner_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.entries[key] = ttk.Entry(inner_frame)
            self.entries[key].insert(0, default)
            self.entries[key].grid(row=i, column=1, sticky="we", pady=2, padx=(10, 0))
        
        # Параметры газа снаружи трубки
        outer_frame = ttk.LabelFrame(self.scrollable_frame, text="Параметры газа СНАРУЖИ трубки", padding=10)
        outer_frame.grid(row=1, column=0, sticky="we", padx=10, pady=5)
        
        params_outer = [
            ("G2", "Расход газа снаружи [кг/с]", "0.2"),
            ("mu2", "Динамическая вязкость газа снаружи [Па·с]", "1.8e-5"),
            ("T2_in", "Температура снаружи на входе [K]", "293.15"),  # 20°C в K
            ("w2", "Скорость потока вне трубки [м/с]", "10"),
            ("cp2", "Изобарная теплоемкость воздуха снаружи [Дж/(кг·К)]", "1005"),
            ("rho2", "Плотность воздуха снаружи [кг/м³]", "1.2"),
            ("lambda_gas2", "Коэффициент теплопроводности газа снаружи [Вт/(м·К)]", "0.03")
        ]
        
        for i, (key, label, default) in enumerate(params_outer):
            ttk.Label(outer_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.entries[key] = ttk.Entry(outer_frame)
            self.entries[key].insert(0, default)
            self.entries[key].grid(row=i, column=1, sticky="we", pady=2, padx=(10, 0))
        
        # Геометрические параметры
        geom_frame = ttk.LabelFrame(self.scrollable_frame, text="Геометрические параметры трубки", padding=10)
        geom_frame.grid(row=2, column=0, sticky="we", padx=10, pady=5)
        
        params_geom = [
            ("d1", "Внутренний диаметр трубки [м]", "0.05"),
            ("d2", "Наружный диаметр трубки [м]", "0.055"),
            ("L", "Длина трубы [м]", "10"),
            ("lambda_tube", "Коэффициент теплопроводности материала трубки [Вт/(м·К)]", "50")
        ]
        
        for i, (key, label, default) in enumerate(params_geom):
            ttk.Label(geom_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.entries[key] = ttk.Entry(geom_frame)
            self.entries[key].insert(0, default)
            self.entries[key].grid(row=i, column=1, sticky="we", pady=2, padx=(10, 0))
        
        # Параметры расчета
        calc_frame = ttk.LabelFrame(self.scrollable_frame, text="Параметры расчета", padding=10)
        calc_frame.grid(row=3, column=0, sticky="we", padx=10, pady=5)
        
        ttk.Label(calc_frame, text="Максимальное количество итераций").grid(row=0, column=0, sticky="w", pady=2)
        self.entries["max_iter"] = ttk.Entry(calc_frame)
        self.entries["max_iter"].insert(0, "100")
        self.entries["max_iter"].grid(row=0, column=1, sticky="we", pady=2, padx=(10, 0))
        
        ttk.Label(calc_frame, text="Точность сходимости [K]").grid(row=1, column=0, sticky="w", pady=2)
        self.entries["tolerance"] = ttk.Entry(calc_frame)
        self.entries["tolerance"].insert(0, "0.001")
        self.entries["tolerance"].grid(row=1, column=1, sticky="we", pady=2, padx=(10, 0))
        
        # Кнопка расчета
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=4, column=0, pady=20)
        
        ttk.Button(button_frame, text="Выполнить расчет", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Очистить все", command=self.clear_all).pack(side="left", padx=5)
        
        # Настройка веса колонок для правильного растягивания
        inner_frame.columnconfigure(1, weight=1)
        outer_frame.columnconfigure(1, weight=1)
        geom_frame.columnconfigure(1, weight=1)
        calc_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(0, weight=1)
    
    def setup_results_tab(self):
        # Текстовое поле для вывода результатов
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=30,
            font=("Courier New", 10)
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Кнопка сохранения результатов
        ttk.Button(self.results_frame, text="Сохранить результаты в файл", 
                  command=self.save_results).pack(pady=5)
    
    def get_float_value(self, key, default=None):
        """Безопасное извлечение числового значения из поля ввода"""
        try:
            value = self.entries[key].get().strip()
            if value:
                return float(value)
            elif default is not None:
                return default
            else:
                raise ValueError(f"Пустое значение для параметра: {key}")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректное значение для параметра {key}: {e}")
            raise
    
    def calculate(self):
        """Выполнение расчета"""
        try:
            # Получаем все параметры
            params = {
                'G1': self.get_float_value('G1'),
                'mu1': self.get_float_value('mu1'),
                'T1_in': self.get_float_value('T1_in'),
                'w1': self.get_float_value('w1'),
                'cp1': self.get_float_value('cp1'),
                'rho1': self.get_float_value('rho1'),
                'lambda_gas1': self.get_float_value('lambda_gas1'),
                
                'G2': self.get_float_value('G2'),
                'mu2': self.get_float_value('mu2'),
                'T2_in': self.get_float_value('T2_in'),
                'w2': self.get_float_value('w2'),
                'cp2': self.get_float_value('cp2'),
                'rho2': self.get_float_value('rho2'),
                'lambda_gas2': self.get_float_value('lambda_gas2'),
                
                'd1': self.get_float_value('d1'),
                'd2': self.get_float_value('d2'),
                'L': self.get_float_value('L'),
                'lambda_tube': self.get_float_value('lambda_tube'),
                
                'max_iter': int(self.get_float_value('max_iter', 100)),
                'tolerance': self.get_float_value('tolerance', 0.001)
            }
            
            # Выполняем расчет
            results = self.calculate_heat_transfer(params)
            
            # Выводим результаты
            self.display_results(results)
            
            # Переключаемся на вкладку с результатами
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Ошибка расчета", f"Произошла ошибка при расчете: {e}")
    
    def calculate_heat_transfer(self, params):
        """
        Расчет теплопередачи цилиндрической стенки
        """
        # Распаковываем параметры
        G1 = params['G1']
        mu1 = params['mu1']
        T1_in = params['T1_in']  # Уже в Кельвинах
        w1 = params['w1']
        cp1 = params['cp1']
        rho1 = params['rho1']
        lambda_gas1 = params['lambda_gas1']
        
        G2 = params['G2']
        mu2 = params['mu2']
        T2_in = params['T2_in']  # Уже в Кельвинах
        w2 = params['w2']
        cp2 = params['cp2']
        rho2 = params['rho2']
        lambda_gas2 = params['lambda_gas2']
        
        d1 = params['d1']
        d2 = params['d2']
        L = params['L']
        lambda_tube = params['lambda_tube']
        
        max_iter = params['max_iter']
        tolerance = params['tolerance']
        
        # Начальные приближения (в Кельвинах)
        T1_avg = T1_in
        T2_avg = T2_in
        T1_out = T1_in - 10  # начальное предположение (в Кельвинах)
        T2_out = T2_in + 10  # начальное предположение (в Кельвинах)
        
        for iteration in range(max_iter):
            # Сохраняем предыдущие значения для проверки сходимости
            T1_prev = T1_avg
            T2_prev = T2_avg
            
            # 1. Расчет чисел Рейнольдса
            Re1 = (w1 * d1 * rho1) / mu1
            Re2 = (w2 * d2 * rho2) / mu2
            
            # 2. Расчет чисел Прандтля
            Pr1 = (mu1 * cp1) / lambda_gas1
            Pr2 = (mu2 * cp2) / lambda_gas2
            
            # 3. Расчет чисел Нуссельта
            
            # Для внутреннего потока (турбулентный режим в трубе)
            if Re1 > 2300:
                # Уравнение Диттуса-Бойлтера для охлаждения (n=0.3)
                Nu1 = 0.023 * (Re1 ** 0.8) * (Pr1 ** 0.3)
            else:
                # Для ламинарного режима (используем более простое приближение)
                Nu1 = 3.66  # Для постоянной температуры стенки
            
            # Для внешнего потока (поперечное обтекание трубы)
            # Определяем коэффициенты C и m в зависимости от Re
            if Re2 < 40:
                C, m = 0.75, 0.4
            elif Re2 < 1000:
                C, m = 0.51, 0.5
            elif Re2 < 2e5:
                C, m = 0.26, 0.6
            else:  # 2e5 < Re2 < 1e6
                C, m = 0.076, 0.7
                
            Nu2 = C * (Re2 ** m) * (Pr2 ** 0.33)
            
            # 4. Расчет коэффициентов теплоотдачи
            alpha1 = (Nu1 * lambda_gas1) / d1  # [Вт/(м²·К)]
            alpha2 = (Nu2 * lambda_gas2) / d2  # [Вт/(м²·К)]
            
            # 5. Расчет полного термического сопротивления
            R_total = 1/(math.pi * L) * (1/(alpha1 * d1) + 
                                        (1/(2 * lambda_tube)) * math.log(d2/d1) + 
                                        1/(alpha2 * d2))  # [К/Вт]
            
            # 6. Расчет теплового потока
            Q = (T1_avg - T2_avg) / R_total  # [Вт]
            
            # 7. Расчет новых выходных температур
            T1_out_new = T1_in - Q / (G1 * cp1)
            T2_out_new = T2_in + Q / (G2 * cp2)
            
            # 8. Расчет новых средних температур
            T1_avg_new = (T1_in + T1_out_new) / 2
            T2_avg_new = (T2_in + T2_out_new) / 2
            
            # Проверка сходимости
            if (abs(T1_avg_new - T1_prev) < tolerance and 
                abs(T2_avg_new - T2_prev) < tolerance):
                print(f"Сходимость достигнута на итерации {iteration + 1}")
                T1_avg = T1_avg_new
                T2_avg = T2_avg_new
                T1_out = T1_out_new
                T2_out = T2_out_new
                break
            
            # Обновление значений для следующей итерации
            T1_avg = T1_avg_new
            T2_avg = T2_avg_new
            T1_out = T1_out_new
            T2_out = T2_out_new
        
        else:
            print(f"Достигнуто максимальное количество итераций ({max_iter})")
        
        # Дополнительные расчеты
        # Температуры стенок
        R_alpha1 = 1 / (alpha1 * math.pi * d1 * L)
        R_alpha2 = 1 / (alpha2 * math.pi * d2 * L)
        
        T_wall_inner = T1_avg - Q * R_alpha1
        T_wall_outer = T2_avg + Q * R_alpha2
        
        # Коэффициент теплопередачи
        U = 1 / (R_total * math.pi * d1 * L)  # [Вт/(м²·К)]
        
        # Разницы температур
        delta_T1 = T1_in - T1_out  # Разница температур в трубке
        delta_T2 = T2_out - T2_in  # Разница температур снаружи
        
        return {
            'heat_flux': Q,           # Тепловой поток [Вт]
            'T1_in': T1_in,           # Температура газа на входе в трубку [K]
            'T1_out': T1_out,         # Температура газа на выходе из трубки [K]
            'T2_in': T2_in,           # Температура наружного газа на входе [K]
            'T2_out': T2_out,         # Температура наружного газа на выходе [K]
            'delta_T1': delta_T1,     # Разница температур в трубке [K]
            'delta_T2': delta_T2,     # Разница температур снаружи [K]
            'alpha1': alpha1,         # Коэффициент теплоотдачи внутри [Вт/(м²·К)]
            'alpha2': alpha2,         # Коэффициент теплоотдачи снаружи [Вт/(м²·К)]
            'R_total': R_total,       # Полное термическое сопротивление [К/Вт]
            'Re1': Re1,              # Число Рейнольдса внутри
            'Re2': Re2,              # Число Рейнольдса снаружи
            'Nu1': Nu1,              # Число Нуссельта внутри
            'Nu2': Nu2,              # Число Нуссельта снаружи
            'T_wall_inner': T_wall_inner,  # Температура внутренней стенки [K]
            'T_wall_outer': T_wall_outer,  # Температура внешней стенки [K]
            'U': U,                  # Коэффициент теплопередачи [Вт/(м²·К)]
            'iterations': iteration + 1  # Количество выполненных итераций
        }
    
    def display_results(self, results):
        """Отображение результатов в текстовом поле"""
        # Функция для конвертации Кельвинов в Цельсии
        def k_to_c(k):
            return k - 273.15
        
        output = "=" * 60 + "\n"
        output += "РЕЗУЛЬТАТЫ РАСЧЕТА ТЕПЛОПЕРЕДАЧИ\n"
        output += "=" * 60 + "\n\n"
        
        output += "ОСНОВНЫЕ РЕЗУЛЬТАТЫ:\n"
        output += f"  Тепловой поток: {results['heat_flux']:.2f} Вт\n"
        output += f"  Коэффициент теплопередачи: {results['U']:.2f} Вт/(м²·К)\n\n"
        
        output += "ТЕМПЕРАТУРЫ В ТРУБКЕ:\n"
        output += f"  На входе: {results['T1_in']:.2f} K ({k_to_c(results['T1_in']):.2f} °C)\n"
        output += f"  На выходе: {results['T1_out']:.2f} K ({k_to_c(results['T1_out']):.2f} °C)\n"
        output += f"  Разница температур (ΔT): {results['delta_T1']:.2f} K\n\n"
        
        output += "ТЕМПЕРАТУРЫ СНАРУЖИ:\n"
        output += f"  На входе: {results['T2_in']:.2f} K ({k_to_c(results['T2_in']):.2f} °C)\n"
        output += f"  На выходе: {results['T2_out']:.2f} K ({k_to_c(results['T2_out']):.2f} °C)\n"
        output += f"  Разница температур (ΔT): {results['delta_T2']:.2f} K\n\n"
        
        output += "ТЕМПЕРАТУРЫ СТЕНОК:\n"
        output += f"  Внутренняя стенка: {results['T_wall_inner']:.2f} K ({k_to_c(results['T_wall_inner']):.2f} °C)\n"
        output += f"  Внешняя стенка: {results['T_wall_outer']:.2f} K ({k_to_c(results['T_wall_outer']):.2f} °C)\n\n"
        
        output += "КОЭФФИЦИЕНТЫ ТЕПЛООТДАЧИ:\n"
        output += f"  Внутренний (α1): {results['alpha1']:.2f} Вт/(м²·К)\n"
        output += f"  Внешний (α2): {results['alpha2']:.2f} Вт/(м²·К)\n\n"
        
        output += "КРИТЕРИИ ПОДОБИЯ:\n"
        output += f"  Число Рейнольдса внутри (Re1): {results['Re1']:.0f}\n"
        output += f"  Число Рейнольдса снаружи (Re2): {results['Re2']:.0f}\n"
        output += f"  Число Нуссельта внутри (Nu1): {results['Nu1']:.2f}\n"
        output += f"  Число Нуссельта снаружи (Nu2): {results['Nu2']:.2f}\n\n"
        
        output += "ПАРАМЕТРЫ РАСЧЕТА:\n"
        output += f"  Полное термическое сопротивление: {results['R_total']:.6f} К/Вт\n"
        output += f"  Количество итераций: {results['iterations']}\n"
        
        # Определение режимов течения
        regime1 = "турбулентный" if results['Re1'] > 2300 else "ламинарный"
        regime2 = "турбулентный" if results['Re2'] > 4000 else "ламинарный"
        output += f"  Режим течения внутри: {regime1}\n"
        output += f"  Режим течения снаружи: {regime2}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, output)
    
    def save_results(self):
        """Сохранение результатов в файл"""
        try:
            filename = "heat_transfer_results.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.results_text.get(1.0, tk.END))
            messagebox.showinfo("Сохранение", f"Результаты сохранены в файл: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл: {e}")
    
    def clear_all(self):
        """Очистка всех полей ввода"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Установка значений по умолчанию
        defaults = {
            'G1': '0.1', 'mu1': '2.1e-5', 'T1_in': '473.15', 'w1': '5', 'cp1': '1010',
            'rho1': '0.8', 'lambda_gas1': '0.03', 'G2': '0.2', 'mu2': '1.8e-5',
            'T2_in': '293.15', 'w2': '10', 'cp2': '1005', 'rho2': '1.2', 'lambda_gas2': '0.03',
            'd1': '0.05', 'd2': '0.055', 'L': '10', 'lambda_tube': '50',
            'max_iter': '100', 'tolerance': '0.001'
        }
        
        for key, value in defaults.items():
            self.entries[key].insert(0, value)

def main():
    root = tk.Tk()
    app = HeatTransferCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()