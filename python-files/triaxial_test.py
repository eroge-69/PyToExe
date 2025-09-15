import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class TriaxialTestGenerator:
    def __init__(self, E, phi, c, sample_height, sample_diameter):
        self.E = E
        self.phi = np.radians(phi)
        self.c = c
        self.sample_height = sample_height  # мм
        self.sample_diameter = sample_diameter  # мм
        self.sample_area = np.pi * (sample_diameter / 2) ** 2  # мм²
        
    def generate_stress_strain_curve(self, sigma_3, num_points=50):
        sigma_1_max = sigma_3 * (1 + np.sin(self.phi))/(1 - np.sin(self.phi)) + 2 * self.c * np.cos(self.phi)/(1 - np.sin(self.phi))
        deviator_max = sigma_1_max - sigma_3
        
        # Относительная деформация
        epsilon_rel = np.linspace(0, deviator_max/self.E * 3, num_points)
        deviator = self.E * epsilon_rel / (1 + epsilon_rel/(deviator_max/self.E))
        
        # Добавление шума для реалистичности
        noise = np.random.normal(0, deviator_max * 0.02, num_points)
        deviator += noise
        
        # Абсолютная линейная деформация (мм)
        delta_h = epsilon_rel * self.sample_height
        
        # Объемная деформация (предполагаем, что коэффициент Пуассона = 0.5 для грунта)
        epsilon_vol = epsilon_rel * (1 - 2 * 0.5)  # Для несжимаемого материала = 0
        
        return epsilon_rel, deviator, sigma_1_max, delta_h, epsilon_vol
    
    def generate_test_series(self, sigma_3_values, num_points=50):
        test_results = []
        
        for sigma_3 in sigma_3_values:
            epsilon_rel, deviator, sigma_1_max, delta_h, epsilon_vol = self.generate_stress_strain_curve(sigma_3, num_points)
            test_results.append({
                'sigma_3': sigma_3,
                'epsilon_rel': epsilon_rel,      # Относительная деформация
                'deviator': deviator,            # Девиатор напряжения
                'sigma_1_max': sigma_1_max,      # Предельное давление
                'delta_h': delta_h,              # Абсолютная деформация, мм
                'epsilon_vol': epsilon_vol,      # Объемная деформация
                'force': deviator * self.sample_area / 1000  # Усилие, кН (кПа * мм² / 1000)
            })
        
        return test_results
    
    def export_to_excel(self, test_results, filename):
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for i, test in enumerate(test_results):
                    df = pd.DataFrame({
                        'Относительная деформация ε, д.е.': test['epsilon_rel'],
                        'Абсолютная деформация Δh, мм': test['delta_h'],
                        'Объемная деформация ε_vol, д.е.': test['epsilon_vol'],
                        'Девиатор напряжения (σ₁-σ₃), кПа': test['deviator'],
                        'Усилие, кН': test['force']
                    })
                    df.to_excel(writer, sheet_name=f'Test_σ₃={test["sigma_3"]:.0f}', index=False)
                
                summary_data = []
                for test in test_results:
                    summary_data.append({
                        'Боковое давление σ₃, кПа': test['sigma_3'],
                        'Предельное давление σ₁, кПа': test['sigma_1_max'],
                        'Предельный девиатор, кПа': test['sigma_1_max'] - test['sigma_3'],
                        'Предельное усилие, кН': (test['sigma_1_max'] - test['sigma_3']) * self.sample_area / 1000,
                        'Модуль деформации E, кПа': self.E,
                        'Угол внутреннего трения φ, °': np.degrees(self.phi),
                        'Удельное сцепление c, кПа': self.c,
                        'Высота образца, мм': self.sample_height,
                        'Диаметр образца, мм': self.sample_diameter,
                        'Площадь сечения, мм²': self.sample_area
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False

class TriaxialTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор испытаний трехосного сжатия")
        self.root.geometry("1100x850")
        
        self.sigma_3_values = []  # Список для хранения значений σ₃
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Ввод параметров
        tab_input = ttk.Frame(notebook)
        notebook.add(tab_input, text="Параметры испытаний")
        
        # Вкладка 2: Результаты
        tab_results = ttk.Frame(notebook)
        notebook.add(tab_results, text="Результаты")
        
        self.setup_input_tab(tab_input)
        self.setup_results_tab(tab_results)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Введите параметры грунта и значения σ₃")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
        
    def setup_input_tab(self, parent):
        # Параметры грунта
        frame_params = ttk.LabelFrame(parent, text="Параметры грунта", padding=10)
        frame_params.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_params, text="Модуль деформации E (кПа):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_E = ttk.Entry(frame_params, width=15)
        self.entry_E.insert(0, "15000")
        self.entry_E.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_params, text="Угол внутреннего трения φ (°):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_phi = ttk.Entry(frame_params, width=15)
        self.entry_phi.insert(0, "25")
        self.entry_phi.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_params, text="Удельное сцепление c (кПа):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_c = ttk.Entry(frame_params, width=15)
        self.entry_c.insert(0, "15")
        self.entry_c.grid(row=2, column=1, padx=5, pady=5)
        
        # Параметры образца
        frame_sample = ttk.LabelFrame(parent, text="Параметры образца", padding=10)
        frame_sample.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_sample, text="Высота образца h₀ (мм):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_height = ttk.Entry(frame_sample, width=15)
        self.entry_height.insert(0, "76")
        self.entry_height.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_sample, text="Диаметр образца d₀ (мм):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_diameter = ttk.Entry(frame_sample, width=15)
        self.entry_diameter.insert(0, "38")
        self.entry_diameter.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_sample, text="Количество точек на кривую:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_num_points = ttk.Entry(frame_sample, width=15)
        self.entry_num_points.insert(0, "50")
        self.entry_num_points.grid(row=2, column=1, padx=5, pady=5)
        
        # Боковые давления
        frame_sigma3 = ttk.LabelFrame(parent, text="Боковые давления σ₃ (кПа)", padding=10)
        frame_sigma3.pack(fill='x', padx=10, pady=10)
        
        # Поле для ввода значений через запятую
        ttk.Label(frame_sigma3, text="Введите значения через запятую:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_sigma3 = ttk.Entry(frame_sigma3, width=50)
        self.entry_sigma3.insert(0, "50, 100, 150, 200")
        self.entry_sigma3.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        
        # Кнопка для автоматической генерации диапазона
        ttk.Button(frame_sigma3, text="Автозаполнить диапазон", 
                  command=self.auto_fill_range).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        # Поля для указания диапазона
        ttk.Label(frame_sigma3, text="Или укажите диапазон:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_sigma3, text="от:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.entry_range_min = ttk.Entry(frame_sigma3, width=10)
        self.entry_range_min.insert(0, "50")
        self.entry_range_min.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_sigma3, text="до:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.entry_range_max = ttk.Entry(frame_sigma3, width=10)
        self.entry_range_max.insert(0, "200")
        self.entry_range_max.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_sigma3, text="количество:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.entry_num_tests = ttk.Entry(frame_sigma3, width=10)
        self.entry_num_tests.insert(0, "4")
        self.entry_num_tests.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(frame_sigma3, text="Сгенерировать диапазон", 
                  command=self.generate_range).grid(row=7, column=0, padx=5, pady=5, sticky='w')
        
        # Текущие значения σ₃
        frame_current = ttk.LabelFrame(parent, text="Текущие значения σ₃", padding=10)
        frame_current.pack(fill='x', padx=10, pady=10)
        
        self.sigma3_listbox = tk.Listbox(frame_current, height=6, width=50)
        self.sigma3_listbox.pack(padx=5, pady=5)
        
        frame_buttons = ttk.Frame(frame_current)
        frame_buttons.pack(pady=5)
        
        ttk.Label(frame_buttons, text="Новое значение:").pack(side='left', padx=5)
        self.entry_new_sigma3 = ttk.Entry(frame_buttons, width=10)
        self.entry_new_sigma3.pack(side='left', padx=5)
        
        ttk.Button(frame_buttons, text="Добавить", command=self.add_sigma3).pack(side='left', padx=5)
        ttk.Button(frame_buttons, text="Удалить выбранное", command=self.remove_sigma3).pack(side='left', padx=5)
        ttk.Button(frame_buttons, text="Очистить список", command=self.clear_sigma3).pack(side='left', padx=5)
        
        # Кнопки управления
        frame_control = ttk.Frame(parent)
        frame_control.pack(pady=20)
        
        self.btn_generate = ttk.Button(frame_control, text="Сгенерировать данные", command=self.generate_data)
        self.btn_generate.pack(side='left', padx=10)
        
        self.btn_export = ttk.Button(frame_control, text="Экспорт в Excel", command=self.export_data)
        self.btn_export.pack(side='left', padx=10)
        
        self.btn_plot = ttk.Button(frame_control, text="Построить графики", command=self.plot_data)
        self.btn_plot.pack(side='left', padx=10)
        
    def setup_results_tab(self, parent):
        # Область для графиков
        self.figure_frame = ttk.Frame(parent)
        self.figure_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Текстовое поле для результатов
        frame_text = ttk.Frame(parent)
        frame_text.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_text, text="Результаты испытаний:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.text_results = scrolledtext.ScrolledText(frame_text, height=12, width=80)
        self.text_results.pack(fill='x', pady=5)
        
    def auto_fill_range(self):
        """Автозаполнение типичными значениями σ₃"""
        self.entry_sigma3.delete(0, tk.END)
        self.entry_sigma3.insert(0, "50, 100, 150, 200, 250, 300")
        self.status_var.set("Заполнены типичные значения σ₃: 50, 100, 150, 200, 250, 300")
    
    def generate_range(self):
        """Генерация диапазона значений σ₃"""
        try:
            min_val = float(self.entry_range_min.get())
            max_val = float(self.entry_range_max.get())
            num_points = int(self.entry_num_tests.get())
            
            if min_val >= max_val or num_points <= 0:
                raise ValueError("Некорректные значения диапазона")
            
            sigma3_values = np.linspace(min_val, max_val, num_points)
            sigma3_str = ", ".join([f"{x:.1f}" for x in sigma3_values])
            
            self.entry_sigma3.delete(0, tk.END)
            self.entry_sigma3.insert(0, sigma3_str)
            
            self.status_var.set(f"Сгенерирован диапазон σ₃: {sigma3_str}")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
    
    def add_sigma3(self):
        """Добавление значения σ₃ в список"""
        try:
            value = float(self.entry_new_sigma3.get())
            if value <= 0:
                raise ValueError("Значение должно быть положительным")
            
            self.sigma3_listbox.insert(tk.END, f"{value:.1f}")
            self.entry_new_sigma3.delete(0, tk.END)
            self.status_var.set(f"Добавлено значение σ₃: {value:.1f} кПа")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное числовое значение")
    
    def remove_sigma3(self):
        """Удаление выбранного значения σ₃"""
        selection = self.sigma3_listbox.curselection()
        if selection:
            value = self.sigma3_listbox.get(selection[0])
            self.sigma3_listbox.delete(selection[0])
            self.status_var.set(f"Удалено значение σ₃: {value}")
    
    def clear_sigma3(self):
        """Очистка списка значений σ₃"""
        self.sigma3_listbox.delete(0, tk.END)
        self.status_var.set("Список значений σ₃ очищен")
    
    def get_sigma3_values(self):
        """Получение всех значений σ₃ из различных источников"""
        sigma3_values = []
        
        # Из списка
        for i in range(self.sigma3_listbox.size()):
            try:
                value = float(self.sigma3_listbox.get(i))
                sigma3_values.append(value)
            except ValueError:
                pass
        
        # Из текстового поле (через запятую)
        text_values = self.entry_sigma3.get()
        if text_values.strip():
            try:
                values = [float(x.strip()) for x in text_values.split(',') if x.strip()]
                sigma3_values.extend(values)
            except ValueError:
                pass
        
        # Удаление дубликатов и сортировка
        sigma3_values = sorted(set(sigma3_values))
        
        return sigma3_values
    
    def generate_data(self):
        try:
            # Получение параметров грунта
            E = float(self.entry_E.get())
            phi = float(self.entry_phi.get())
            c = float(self.entry_c.get())
            
            # Получение параметров образца
            sample_height = float(self.entry_height.get())
            sample_diameter = float(self.entry_diameter.get())
            num_points = int(self.entry_num_points.get())
            
            if E <= 0 or phi <= 0 or c < 0:
                raise ValueError("Параметры грунта должны быть положительными числами")
            
            if sample_height <= 0 or sample_diameter <= 0 or num_points <= 0:
                raise ValueError("Параметры образца должны быть положительными числами")
            
            # Получение значений σ₃
            sigma3_values = self.get_sigma3_values()
            if not sigma3_values:
                raise ValueError("Не указаны значения бокового давления σ₃")
            
            if len(sigma3_values) < 2:
                raise ValueError("Необходимо указать хотя бы 2 значения σ₃")
            
            # Генерация данных
            self.generator = TriaxialTestGenerator(E, phi, c, sample_height, sample_diameter)
            self.test_results = self.generator.generate_test_series(sigma3_values, num_points)
            
            # Вывод результатов в текстовое поле
            self.display_results()
            
            self.status_var.set(f"Данные сгенерированы! Создано {len(sigma3_values)} испытаний по {num_points} точек.")
            messagebox.showinfo("Успех", f"Данные успешно сгенерированы!\nСоздано {len(sigma3_values)} испытаний по {num_points} точек.")
            
        except ValueError as e:
            self.status_var.set("Ошибка ввода данных")
            messagebox.showerror("Ошибка", f"Проверьте правильность введенных данных!\n{e}")
    
    def display_results(self):
        """Отображение результатов в текстовом поле"""
        if not hasattr(self, 'test_results'):
            return
        
        sample_area = np.pi * (self.generator.sample_diameter / 2) ** 2
        
        text = "РЕЗУЛЬТАТЫ ИСПЫТАНИЙ ТРЕХОСНОГО СЖАТИЯ\n"
        text += "=" * 60 + "\n\n"
        
        text += f"Параметры грунта:\n"
        text += f"  - Модуль деформации E: {self.generator.E} кПа\n"
        text += f"  - Угол внутреннего трения φ: {np.degrees(self.generator.phi):.1f}°\n"
        text += f"  - Удельное сцепление c: {self.generator.c} кПа\n\n"
        
        text += f"Параметры образца:\n"
        text += f"  - Высота h₀: {self.generator.sample_height} мм\n"
        text += f"  - Диаметр d₀: {self.generator.sample_diameter} мм\n"
        text += f"  - Площадь сечения: {sample_area:.1f} мм²\n"
        text += f"  - Количество точек на кривую: {len(self.test_results[0]['epsilon_rel'])}\n\n"
        
        text += "Результаты испытаний:\n"
        text += "-" * 60 + "\n"
        
        for i, test in enumerate(self.test_results, 1):
            max_deformation = np.max(test['delta_h'])
            max_force = np.max(test['force'])
            
            text += f"Испытание {i} (σ₃ = {test['sigma_3']:.1f} кПа):\n"
            text += f"  - Предельное давление σ₁: {test['sigma_1_max']:.1f} кПа\n"
            text += f"  - Предельный девиатор: {test['sigma_1_max'] - test['sigma_3']:.1f} кPa\n"
            text += f"  - Макс. абсолютная деформация: {max_deformation:.2f} мм\n"
            text += f"  - Макс. усилие: {max_force:.2f} кН\n"
            text += f"  - Количество точек: {len(test['epsilon_rel'])}\n\n"
        
        self.text_results.delete(1.0, tk.END)
        self.text_results.insert(1.0, text)
    
    def export_data(self):
        if not hasattr(self, 'test_results'):
            messagebox.showerror("Ошибка", "Сначала сгенерируйте данные!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Сохранить файл Excel"
        )
        
        if filename:
            try:
                success = self.generator.export_to_excel(self.test_results, filename)
                if success:
                    self.status_var.set(f"Данные экспортированы в: {os.path.basename(filename)}")
                    messagebox.showinfo("Успех", f"Данные экспортированы в файл:\n{filename}")
                    
                    # Показать графики после экспорта
                    self.plot_data()
                else:
                    messagebox.showerror("Ошибка", "Не удалось экспортировать данные")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def plot_data(self):
        if not hasattr(self, 'test_results'):
            messagebox.showerror("Ошибка", "Сначала сгенерируйте данные!")
            return
        
        # Очистка предыдущих графиков
        for widget in self.figure_frame.winfo_children():
            widget.destroy()
        
        try:
            # Создание графиков с двумя рядами
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            
            # 1. Кривые деформирования (относительная деформация)
            for test in self.test_results:
                ax1.plot(test['epsilon_rel'] * 100, test['deviator'],  # ε в %
                        label=f'σ₃ = {test["sigma_3"]:.1f} кПа')
                ax1.axhline(y=test['sigma_1_max'] - test['sigma_3'], 
                           color='gray', linestyle='--', alpha=0.5)
            
            ax1.set_xlabel('Относительная деформация ε, %')
            ax1.set_ylabel('Девиатор напряжения (σ₁-σ₃), кПа')
            ax1.set_title('Кривые деформирования (относительные)')
            ax1.legend()
            ax1.grid(True)
            
            # 2. Кривые деформирования (абсолютная деформация)
            for test in self.test_results:
                ax2.plot(test['delta_h'], test['deviator'],
                        label=f'σ₃ = {test["sigma_3"]:.1f} кПа')
            
            ax2.set_xlabel('Абсолютная деформация Δh, мм')
            ax2.set_ylabel('Девиатор напряжения (σ₁-σ₃), кПа')
            ax2.set_title('Кривые деформирования (абсолютные)')
            ax2.legend()
            ax2.grid(True)
            
            # 3. Кривые усилия
            for test in self.test_results:
                ax3.plot(test['epsilon_rel'] * 100, test['force'],
                        label=f'σ₃ = {test["sigma_3"]:.1f} кПа')
            
            ax3.set_xlabel('Относительная деформация ε, %')
            ax3.set_ylabel('Усилие, кН')
            ax3.set_title('Зависимость усилия от деформации')
            ax3.legend()
            ax3.grid(True)
            
            # 4. Круги Мора
            for test in self.test_results:
                sigma_3 = test['sigma_3']
                sigma_1 = test['sigma_1_max']
                center = (sigma_1 + sigma_3) / 2
                radius = (sigma_1 - sigma_3) / 2
                
                theta = np.linspace(0, 2*np.pi, 100)
                x = center + radius * np.cos(theta)
                y = radius * np.sin(theta)
                ax4.plot(x, y, 'b-', alpha=0.7)
            
            # Огибающая прочности
            sigma_range = np.linspace(0, max([t['sigma_1_max'] for t in self.test_results]) * 1.2, 100)
            tau = self.generator.c + sigma_range * np.tan(self.generator.phi)
            ax4.plot(sigma_range, tau, 'r-', linewidth=2, 
                   label=f'c = {self.generator.c:.1f} кПа, φ = {np.degrees(self.generator.phi):.1f}°')
            
            ax4.set_xlabel('Нормальное напряжение σ, кПа')
            ax4.set_ylabel('Касательное напряжение τ, кПа')
            ax4.set_title('Круги Мора и огибающая прочности')
            ax4.legend()
            ax4.grid(True)
            ax4.set_aspect('equal')
            
            plt.tight_layout()
            
            # Встраивание графиков в интерфейс
            canvas = FigureCanvasTkAgg(fig, self.figure_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            self.status_var.set("Графики построены успешно")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графиков: {str(e)}")

def main():
    root = tk.Tk()
    app = TriaxialTestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()