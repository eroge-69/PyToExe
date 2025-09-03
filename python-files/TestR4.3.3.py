import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class VagonTolkatelCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор параметров вагоно-толкателя")
        self.root.geometry("1200x800")
        
        # Переменные для хранения данных
        self.speed_var = tk.DoubleVar(value=5.0)
        self.accel_time_var = tk.DoubleVar(value=90.0)
        self.mass_min_var = tk.DoubleVar(value=500.0)
        self.mass_max_var = tk.DoubleVar(value=2000.0)
        self.mass_step_var = tk.DoubleVar(value=500.0)
        self.vt_mass_var = tk.DoubleVar(value=50.0)
        self.wheel_diameter_var = tk.DoubleVar(value=1050.0)
        self.engine_rpm_var = tk.DoubleVar(value=725.0)
        self.engine_eff_var = tk.DoubleVar(value=0.87)
        self.engine_cos_var = tk.DoubleVar(value=0.85)
        self.aux_power_var = tk.DoubleVar(value=11.0)
        self.turn_radius_var = tk.DoubleVar(value=150.0)
        self.slope_angle_var = tk.DoubleVar(value=3.0)
        self.axle_load_var = tk.DoubleVar(value=21.5)
        self.overload_factor_var = tk.DoubleVar(value=1.25)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Создаем notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка ввода параметров
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="Параметры")
        
        # Параметры движения
        movement_frame = ttk.LabelFrame(input_frame, text="Параметры движения")
        movement_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(movement_frame, text="Скорость (км/ч):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(movement_frame, textvariable=self.speed_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(movement_frame, text="Время разгона (с):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(movement_frame, textvariable=self.accel_time_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(movement_frame, text="Масса ВТ (т):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(movement_frame, textvariable=self.vt_mass_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(movement_frame, text="Диаметр колеса (мм):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(movement_frame, textvariable=self.wheel_diameter_var, width=15).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(movement_frame, text="Радиус поворота (м):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(movement_frame, textvariable=self.turn_radius_var, width=15).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(movement_frame, text="Уклон (‰):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(movement_frame, textvariable=self.slope_angle_var, width=15).grid(row=5, column=1, padx=5, pady=5)
        
        # Параметры двигателя
        engine_frame = ttk.LabelFrame(input_frame, text="Параметры двигателя")
        engine_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(engine_frame, text="Обороты двигателя (об/мин):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(engine_frame, textvariable=self.engine_rpm_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(engine_frame, text="КПД двигателя:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(engine_frame, textvariable=self.engine_eff_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(engine_frame, text="Cos φ двигателя:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(engine_frame, textvariable=self.engine_cos_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(engine_frame, text="Мощность соб. нужд (кВт):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(engine_frame, textvariable=self.aux_power_var, width=15).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(engine_frame, text="Нагрузка на ось (т):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(engine_frame, textvariable=self.axle_load_var, width=15).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(engine_frame, text="Коэф. перегрузки:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(engine_frame, textvariable=self.overload_factor_var, width=15).grid(row=5, column=1, padx=5, pady=5)
        
        # Параметры расчета
        calc_frame = ttk.LabelFrame(input_frame, text="Параметры расчета")
        calc_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(calc_frame, text="Минимальная масса груза (т):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(calc_frame, textvariable=self.mass_min_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(calc_frame, text="Максимальная масса груза (т):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(calc_frame, textvariable=self.mass_max_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(calc_frame, text="Шаг массы груза (т):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(calc_frame, textvariable=self.mass_step_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопка расчета
        ttk.Button(calc_frame, text="Выполнить расчет", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Вкладка результатов
        self.result_frame = ttk.Frame(notebook)
        notebook.add(self.result_frame, text="Результаты")
        
        # Вкладка графиков
        self.plot_frame = ttk.Frame(notebook)
        notebook.add(self.plot_frame, text="Графики")
        
        # Настройка весов строк и столбцов для правильного масштабирования
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.rowconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
    def calculate(self):
        try:
            # Получаем значения из полей ввода
            speed = self.speed_var.get()
            accel_time = self.accel_time_var.get()
            mass_min = self.mass_min_var.get()
            mass_max = self.mass_max_var.get()
            mass_step = self.mass_step_var.get()
            vt_mass = self.vt_mass_var.get()
            wheel_diameter = self.wheel_diameter_var.get() / 1000  # переводим в метры
            engine_rpm = self.engine_rpm_var.get()
            engine_eff = self.engine_eff_var.get()
            engine_cos = self.engine_cos_var.get()
            aux_power = self.aux_power_var.get()
            turn_radius = self.turn_radius_var.get()
            slope_angle = self.slope_angle_var.get()
            axle_load = self.axle_load_var.get()
            overload_factor = self.overload_factor_var.get()
            
            # Генерируем диапазон масс
            masses = np.arange(mass_min, mass_max + mass_step, mass_step)
            
            # Выполняем расчеты
            results = self.perform_calculations(
                masses, speed, accel_time, vt_mass, wheel_diameter, 
                engine_rpm, engine_eff, engine_cos, aux_power, 
                turn_radius, slope_angle, axle_load, overload_factor
            )
            
            # Отображаем результаты
            self.show_results(results, masses)
            
            # Строим графики
            self.plot_results(results, masses)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при расчетах: {str(e)}")
    
    def perform_calculations(self, masses, speed, accel_time, vt_mass, wheel_diameter, 
                           engine_rpm, engine_eff, engine_cos, aux_power, 
                           turn_radius, slope_angle, axle_load, overload_factor):
        results = {
            'normal': {},
            'turn': {},
            'slope': {}
        }
        
        # Константы
        g = 9.81  # ускорение свободного падения, м/с²
        wheel_radius = wheel_diameter / 2  # радиус колеса, м
        
        # Расчетные параметры
        speed_ms = speed / 3.6  # скорость в м/с
        acceleration = speed_ms / accel_time  # ускорение, м/с²
        
        # Удельные сопротивления (правильные формулы из Excel)
        w0_vt = (1.9 + 0.01 * speed + 0.0003 * speed**2) * g  # для ВТ
        w0_wagon = (0.7 + (3 + 0.1 * speed + 0.0025 * speed**2) / axle_load) * g  # для вагонов
        
        # Кинематические расчеты
        wheel_angular_velocity = speed_ms / wheel_radius  # угловая скорость колеса, рад/с
        wheel_rpm = (wheel_angular_velocity * 60) / (2 * np.pi)  # об/мин
        total_gear_ratio = engine_rpm / wheel_rpm  # общее передаточное число
        
        # Дополнительные коэффициенты сопротивления (исправленные формулы)
        turn_resistance_coef = 700 / turn_radius  # для поворотов (из Excel)
        slope_resistance_coef = slope_angle * g  # для уклонов (из Excel)
        
        # Расчет для разных условий и масс
        for mass in masses:
            total_mass = vt_mass + mass  # общая масса, т
            
            # Нормальные условия (без изменений)
            resistance_vt = w0_vt * vt_mass  # сопротивление ВТ, Н
            resistance_wagon = w0_wagon * mass  # сопротивление вагонов, Н
            total_resistance = resistance_vt + resistance_wagon  # общее сопротивление, Н
            traction_force = total_resistance + total_mass * 1000 * acceleration  # сила тяги, Н
            wheel_torque = traction_force * wheel_radius  # момент на колесе, Н·м
            engine_torque = wheel_torque / (total_gear_ratio * 0.96 * 0.96)  # момент на двигателе, Н·м
            engine_power = (engine_torque * (engine_rpm * 2 * np.pi / 60)) / 1000  # мощность двигателя, кВт
            total_power = engine_power * overload_factor + aux_power  # общая мощность, кВт
            
            results['normal'][mass] = {
                'resistance_vt': resistance_vt,
                'resistance_wagon': resistance_wagon,
                'total_resistance': total_resistance,
                'traction_force': traction_force,
                'wheel_torque': wheel_torque,
                'engine_torque': engine_torque,
                'engine_power': engine_power,
                'total_power': total_power
            }
            
            # Условия поворота (исправленная формула)
            resistance_vt_turn = (w0_vt + turn_resistance_coef) * vt_mass
            resistance_wagon_turn = (w0_wagon + turn_resistance_coef) * mass
            total_resistance_turn = resistance_vt_turn + resistance_wagon_turn
            traction_force_turn = total_resistance_turn + total_mass * 1000 * acceleration
            wheel_torque_turn = traction_force_turn * wheel_radius
            engine_torque_turn = wheel_torque_turn / (total_gear_ratio * 0.96 * 0.96)
            engine_power_turn = (engine_torque_turn * (engine_rpm * 2 * np.pi / 60)) / 1000
            total_power_turn = engine_power_turn * overload_factor + aux_power
            
            results['turn'][mass] = {
                'resistance_vt': resistance_vt_turn,
                'resistance_wagon': resistance_wagon_turn,
                'total_resistance': total_resistance_turn,
                'traction_force': traction_force_turn,
                'wheel_torque': wheel_torque_turn,
                'engine_torque': engine_torque_turn,
                'engine_power': engine_power_turn,
                'total_power': total_power_turn
            }
            
            # Условия уклона (исправленная формула)
            resistance_vt_slope = (w0_vt + slope_resistance_coef) * vt_mass
            resistance_wagon_slope = (w0_wagon + slope_resistance_coef) * mass
            total_resistance_slope = resistance_vt_slope + resistance_wagon_slope
            traction_force_slope = total_resistance_slope + total_mass * 1000 * acceleration
            wheel_torque_slope = traction_force_slope * wheel_radius
            engine_torque_slope = wheel_torque_slope / (total_gear_ratio * 0.96 * 0.96)
            engine_power_slope = (engine_torque_slope * (engine_rpm * 2 * np.pi / 60)) / 1000
            total_power_slope = engine_power_slope * overload_factor + aux_power
            
            results['slope'][mass] = {
                'resistance_vt': resistance_vt_slope,
                'resistance_wagon': resistance_wagon_slope,
                'total_resistance': total_resistance_slope,
                'traction_force': traction_force_slope,
                'wheel_torque': wheel_torque_slope,
                'engine_torque': engine_torque_slope,
                'engine_power': engine_power_slope,
                'total_power': total_power_slope
            }
        
        # Добавляем общие расчетные параметры
        results['common_params'] = {
            'speed_ms': speed_ms,
            'acceleration': acceleration,
            'w0_vt': w0_vt,
            'w0_wagon': w0_wagon,
            'wheel_angular_velocity': wheel_angular_velocity,
            'wheel_rpm': wheel_rpm,
            'total_gear_ratio': total_gear_ratio,
            'turn_resistance_coef': turn_resistance_coef,
            'slope_resistance_coef': slope_resistance_coef
        }
        
        return results
    
    def show_results(self, results, masses):
        # Очищаем frame с результатами
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # Создаем Treeview для отображения результатов
        tree = ttk.Treeview(self.result_frame, columns=('mass', 'condition', 'traction_force', 'wheel_torque', 'engine_torque', 'engine_power'), show='headings')
        
        # Настраиваем колонки
        tree.heading('mass', text='Масса груза, т')
        tree.heading('condition', text='Условия')
        tree.heading('traction_force', text='Сила тяги, кН')
        tree.heading('wheel_torque', text='Момент на колесе, Н·м')
        tree.heading('engine_torque', text='Момент двигателя, Н·м')  # Новая колонка
        tree.heading('engine_power', text='Мощность двигателя, кВт')
        
        tree.column('mass', width=100)
        tree.column('condition', width=150)
        tree.column('traction_force', width=150)
        tree.column('wheel_torque', width=150)
        tree.column('engine_torque', width=150)  # Новая колонка
        tree.column('engine_power', width=150)
        
        # Добавляем данные (переводим Н в кН для силы тяги)
        for mass in masses:
            tree.insert('', 'end', values=(
                mass, 'Нормальные', 
                f"{results['normal'][mass]['traction_force'] / 1000:.1f}",  # Переводим в кН
                f"{results['normal'][mass]['wheel_torque']:.0f}",
                f"{results['normal'][mass]['engine_torque']:.1f}",  # Момент двигателя
                f"{results['normal'][mass]['total_power']:.1f}"
            ))
            
            tree.insert('', 'end', values=(
                mass, 'Поворот', 
                f"{results['turn'][mass]['traction_force'] / 1000:.1f}",  # Переводим в кН
                f"{results['turn'][mass]['wheel_torque']:.0f}",
                f"{results['turn'][mass]['engine_torque']:.1f}",  # Момент двигателя
                f"{results['turn'][mass]['total_power']:.1f}"
            ))
            
            tree.insert('', 'end', values=(
                mass, 'Уклон', 
                f"{results['slope'][mass]['traction_force'] / 1000:.1f}",  # Переводим в кН
                f"{results['slope'][mass]['wheel_torque']:.0f}",
                f"{results['slope'][mass]['engine_torque']:.1f}",  # Момент двигателя
                f"{results['slope'][mass]['total_power']:.1f}"
            ))
        
        # Добавляем scrollbar
        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # Упаковываем элементы
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Отображаем общие параметры
        common_params = results['common_params']
        params_text = f"""
        Общие расчетные параметры:
        Скорость: {self.speed_var.get()} км/ч ({common_params['speed_ms']:.2f} м/с)
        Ускорение: {common_params['acceleration']:.4f} м/с²
        Удельное сопротивление ВТ: {common_params['w0_vt']:.2f} Н/т
        Удельное сопротивление вагонов: {common_params['w0_wagon']:.2f} Н/т
        Угловая скорость колеса: {common_params['wheel_angular_velocity']:.2f} рад/с
        Частота вращения колеса: {common_params['wheel_rpm']:.2f} об/мин
        Общее передаточное число: {common_params['total_gear_ratio']:.2f}
        Доп. сопротивление на повороте: {common_params['turn_resistance_coef']:.2f} Н/т
        Доп. сопротивление на уклоне: {common_params['slope_resistance_coef']:.2f} Н/т
        """
        
        params_label = ttk.Label(self.result_frame, text=params_text, justify=tk.LEFT)
        params_label.pack(pady=10)
    
    def plot_results(self, results, masses):
        # Очищаем frame с графиками
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Создаем фигуру с несколькими графиками
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Подготавливаем данные для графиков (переводим Н в кН для силы тяги)
        mass_values = list(masses)
        traction_normal = [results['normal'][m]['traction_force'] / 1000 for m in masses]  # Переводим в кН
        traction_turn = [results['turn'][m]['traction_force'] / 1000 for m in masses]      # Переводим в кН
        traction_slope = [results['slope'][m]['traction_force'] / 1000 for m in masses]    # Переводим в кН
        
        torque_normal = [results['normal'][m]['wheel_torque'] for m in masses]
        torque_turn = [results['turn'][m]['wheel_torque'] for m in masses]
        torque_slope = [results['slope'][m]['wheel_torque'] for m in masses]
        
        engine_torque_normal = [results['normal'][m]['engine_torque'] for m in masses]  # Момент двигателя
        engine_torque_turn = [results['turn'][m]['engine_torque'] for m in masses]      # Момент двигателя
        engine_torque_slope = [results['slope'][m]['engine_torque'] for m in masses]    # Момент двигателя
        
        power_normal = [results['normal'][m]['total_power'] for m in masses]
        power_turn = [results['turn'][m]['total_power'] for m in masses]
        power_slope = [results['slope'][m]['total_power'] for m in masses]
        
        # График силы тяги (в кН) с точками
        ax1.plot(mass_values, traction_normal, 'b-', marker='o', label='Нормальные условия')
        ax1.plot(mass_values, traction_turn, 'r-', marker='s', label='Поворот')
        ax1.plot(mass_values, traction_slope, 'g-', marker='^', label='Уклон')
        ax1.set_xlabel('Масса груза, т')
        ax1.set_ylabel('Сила тяги, кН')
        ax1.set_title('Зависимость силы тяги от массы груза')
        ax1.grid(True)
        ax1.legend()
        
        # График момента на колесе с точками
        ax2.plot(mass_values, torque_normal, 'b-', marker='o', label='Нормальные условия')
        ax2.plot(mass_values, torque_turn, 'r-', marker='s', label='Поворот')
        ax2.plot(mass_values, torque_slope, 'g-', marker='^', label='Уклон')
        ax2.set_xlabel('Масса груза, т')
        ax2.set_ylabel('Момент на колесе, Н·м')
        ax2.set_title('Зависимость момента на колесе от массы груза')
        ax2.grid(True)
        ax2.legend()
        
        # График мощности двигателя с точками
        ax3.plot(mass_values, power_normal, 'b-', marker='o', label='Нормальные условия')
        ax3.plot(mass_values, power_turn, 'r-', marker='s', label='Поворот')
        ax3.plot(mass_values, power_slope, 'g-', marker='^', label='Уклон')
        ax3.set_xlabel('Масса груза, т')
        ax3.set_ylabel('Мощность двигателя, кВт')
        ax3.set_title('Зависимость мощности двигателя от массы груза')
        ax3.grid(True)
        ax3.legend()
        
        # График момента двигателя с точками
        ax4.plot(mass_values, engine_torque_normal, 'b-', marker='o', label='Нормальные условия')
        ax4.plot(mass_values, engine_torque_turn, 'r-', marker='s', label='Поворот')
        ax4.plot(mass_values, engine_torque_slope, 'g-', marker='^', label='Уклон')
        ax4.set_xlabel('Масса груза, т')
        ax4.set_ylabel('Момент двигателя, Н·м')
        ax4.set_title('Зависимость момента двигателя от массы груза')
        ax4.grid(True)
        ax4.legend()
        
        plt.tight_layout()
        
        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = VagonTolkatelCalculator(root)
    root.mainloop()