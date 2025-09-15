import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class TriaxialTestGenerator:
    def __init__(self, E, phi, c, sample_height, sample_diameter, poisson_ratio=0.3):
        self.E = E
        self.phi = np.radians(phi)
        self.c = c
        self.sample_height = sample_height  # мм
        self.sample_diameter = sample_diameter  # мм
        self.poisson_ratio = poisson_ratio  # Коэффициент Пуассона
        
        # Расчет исходных параметров образца
        self.initial_area = np.pi * (sample_diameter / 2) ** 2  # мм²
        self.initial_volume = self.initial_area * sample_height  # мм³
        
    def generate_stress_strain_curve(self, sigma_3, num_points=50):
        sigma_1_max = sigma_3 * (1 + np.sin(self.phi))/(1 - np.sin(self.phi)) + 2 * self.c * np.cos(self.phi)/(1 - np.sin(self.phi))
        deviator_max = sigma_1_max - sigma_3
        
        # Относительная деформация
        epsilon_axial = np.linspace(0, deviator_max/self.E * 3, num_points)
        deviator = self.E * epsilon_axial / (1 + epsilon_axial/(deviator_max/self.E))
        
        # Добавление шума для реалистичности
        noise = np.random.normal(0, deviator_max * 0.02, num_points)
        deviator += noise
        
        # Абсолютная осевая деформация (мм)
        delta_h = epsilon_axial * self.sample_height
        
        # Поперечная деформация (радиальная)
        epsilon_radial = -self.poisson_ratio * epsilon_axial
        
        # Относительная объемная деформация
        epsilon_vol = epsilon_axial + 2 * epsilon_radial  # ε_vol = ε_axial + 2*ε_radial
        
        # Абсолютное изменение объема (мм³)
        delta_V = epsilon_vol * self.initial_volume
        
        # Текущий объем на каждом шаге (мм³)
        current_volume = self.initial_volume + delta_V
        
        # Текущая высота и диаметр (приближенно)
        current_height = self.sample_height + delta_h
        current_diameter = self.sample_diameter * (1 + epsilon_radial)
        current_area = np.pi * (current_diameter / 2) ** 2
        
        return {
            'epsilon_axial': epsilon_axial,      # Относительная осевая деформация
            'epsilon_radial': epsilon_radial,    # Относительная радиальная деформация
            'epsilon_vol': epsilon_vol,          # Относительная объемная деформация
            'deviator': deviator,                # Девиатор напряжения
            'sigma_1_max': sigma_1_max,          # Предельное давление
            'delta_h': delta_h,                  # Абсолютная осевая деформация, мм
            'delta_V': delta_V,                  # Абсолютное изменение объема, мм³
            'current_volume': current_volume,    # Текущий объем, мм³
            'current_height': current_height,    # Текущая высота, мм
            'current_diameter': current_diameter,# Текущий диаметр, мм
            'current_area': current_area,        # Текущая площадь, мм²
            'force': deviator * self.initial_area / 1000  # Усилие, кН
        }
    
    def generate_test_series(self, sigma_3_values, num_points=50):
        test_results = []
        
        for sigma_3 in sigma_3_values:
            curve_data = self.generate_stress_strain_curve(sigma_3, num_points)
            curve_data['sigma_3'] = sigma_3
            test_results.append(curve_data)
        
        return test_results
    
    def export_to_excel(self, test_results, filename):
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for i, test in enumerate(test_results):
                    df = pd.DataFrame({
                        'Относительная осевая деформация ε_axial, д.е.': test['epsilon_axial'],
                        'Относительная радиальная деформация ε_radial, д.е.': test['epsilon_radial'],
                        'Относительная объемная деформация ε_vol, д.е.': test['epsilon_vol'],
                        'Абсолютная осевая деформация Δh, мм': test['delta_h'],
                        'Абсолютное изменение объема ΔV, мм³': test['delta_V'],
                        'Текущий объем, мм³': test['current_volume'],
                        'Текущая высота, мм': test['current_height'],
                        'Текущий диаметр, мм': test['current_diameter'],
                        'Текущая площадь, мм²': test['current_area'],
                        'Девиатор напряжения (σ₁-σ₃), кПа': test['deviator'],
                        'Усилие, кН': test['force']
                    })
                    df.to_excel(writer, sheet_name=f'Test_σ₃={test["sigma_3"]:.0f}', index=False)
                
                summary_data = []
                for test in test_results:
                    max_force_idx = np.argmax(test['force'])
                    
                    summary_data.append({
                        'Боковое давление σ₃, кПа': test['sigma_3'],
                        'Предельное давление σ₁, кПа': test['sigma_1_max'],
                        'Предельный девиатор, кПа': test['sigma_1_max'] - test['sigma_3'],
                        'Макс. усилие, кН': np.max(test['force']),
                        'Макс. осевая деформация, %': np.max(test['epsilon_axial']) * 100,
                        'Макс. объемная деформация, %': np.max(test['epsilon_vol']) * 100,
                        'Изменение объема при макс. нагрузке, мм³': test['delta_V'][max_force_idx],
                        'Модуль деформации E, кПа': self.E,
                        'Угол внутреннего трения φ, °': np.degrees(self.phi),
                        'Удельное сцепление c, кПа': self.c,
                        'Коэффициент Пуассона ν': self.poisson_ratio,
                        'Исходная высота, мм': self.sample_height,
                        'Исходный диаметр, мм': self.sample_diameter,
                        'Исходная площадь, мм²': self.initial_area,
                        'Исходный объем, мм³': self.initial_volume
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Добавляем лист с параметрами образца
                sample_params = pd.DataFrame({
                    'Параметр': [
                        'Модуль деформации E', 'Угол внутреннего трения φ', 
                        'Удельное сцепление c', 'Коэффициент Пуассона ν',
                        'Высота образца', 'Диаметр образца', 
                        'Площадь сечения', 'Объем образца'
                    ],
                    'Значение': [
                        f'{self.E} кПа', f'{np.degrees(self.phi):.1f}°', 
                        f'{self.c} кПа', f'{self.poisson_ratio}',
                        f'{self.sample_height} мм', f'{self.sample_diameter} мм',
                        f'{self.initial_area:.1f} мм²', f'{self.initial_volume:.1f} мм³'
                    ],
                    'Единицы измерения': [
                        'кПа', '°', 'кПа', '-', 'мм', 'мм', 'мм²', 'мм³'
                    ]
                })
                sample_params.to_excel(writer, sheet_name='Параметры образца', index=False)
                
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False

class TriaxialTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор испытаний трехосного сжатия")
        self.root.geometry("1200x900")
        
        self.sigma_3_values = []
        self.create_widgets()
        
    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        tab_input = ttk.Frame(notebook)
        notebook.add(tab_input, text="Параметры испытаний")
        
        tab_results = ttk.Frame(notebook)
        notebook.add(tab_results, text="Результаты")
        
        self.setup_input_tab(tab_input)
        self.setup_results_tab(tab_results)
        
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
        
        ttk.Label(frame_params, text="Коэффициент Пуассона ν:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.entry_poisson = ttk.Entry(frame_params, width=15)
        self.entry_poisson.insert(0, "0.3")
        self.entry_poisson.grid(row=3, column=1, padx=5, pady=5)
        
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
        
        # Расчетные параметры
        ttk.Label(frame_sample, text="Площадь сечения A₀ (мм²):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.label_area = ttk.Label(frame_sample, text="2269.8")
        self.label_area.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_sample, text="Объем образца V₀ (мм³):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.label_volume = ttk.Label(frame_sample, text="172500.0")
        self.label_volume.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_sample, text="Количество точек на кривую:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.entry_num_points = ttk.Entry(frame_sample, width=15)
        self.entry_num_points.insert(0, "50")
        self.entry_num_points.grid(row=4, column=1, padx=5, pady=5)
        
        # Боковые давления
        frame_sigma3 = ttk.LabelFrame(parent, text="Боковые давления σ₃ (кПа)", padding=10)
        frame_sigma3.pack(fill='x', padx=10, pady=10)
        
        self.entry_sigma3 = ttk.Entry(frame_sigma3, width=50)
        self.entry_sigma3.insert(0, "50, 100, 150, 200")
        self.entry_sigma3.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
        
        # Кнопки управления
        frame_control = ttk.Frame(parent)
        frame_control.pack(pady=20)
        
        self.btn_generate = ttk.Button(frame_control, text="Сгенерировать данные", command=self.generate_data)
        self.btn_generate.pack(side='left', padx=10)
        
        self.btn_export = ttk.Button(frame_control, text="Экспорт в Excel", command=self.export_data)
        self.btn_export.pack(side='left', padx=10)
        
        self.btn_plot = ttk.Button(frame_control, text="Построить графики", command=self.plot_data)
        self.btn_plot.pack(side='left', padx=10)
        
        # Привязка событий для пересчета площади и объема
        self.entry_height.bind('<KeyRelease>', self.calculate_geometry)
        self.entry_diameter.bind('<KeyRelease>', self.calculate_geometry)
        
    def calculate_geometry(self, event=None):
        try:
            height = float(self.entry_height.get() or 76)
            diameter = float(self.entry_diameter.get() or 38)
            
            area = np.pi * (diameter / 2) ** 2
            volume = area * height
            
            self.label_area.config(text=f"{area:.1f}")
            self.label_volume.config(text=f"{volume:.1f}")
        except:
            self.label_area.config(text="2269.8")
            self.label_volume.config(text="172500.0")
        
    def setup_results_tab(self, parent):
        self.figure_frame = ttk.Frame(parent)
        self.figure_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        frame_text = ttk.Frame(parent)
        frame_text.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_text, text="Результаты испытаний:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.text_results = scrolledtext.ScrolledText(frame_text, height=15, width=80)
        self.text_results.pack(fill='x', pady=5)
        
    def get_sigma3_values(self):
        sigma3_values = []
        text_values = self.entry_sigma3.get()
        if text_values.strip():
            try:
                values = [float(x.strip()) for x in text_values.split(',') if x.strip()]
                sigma3_values.extend(values)
            except ValueError:
                pass
        
        sigma3_values = sorted(set(sigma3_values))
        return sigma3_values
    
    def generate_data(self):
        try:
            E = float(self.entry_E.get())
            phi = float(self.entry_phi.get())
            c = float(self.entry_c.get())
            poisson = float(self.entry_poisson.get())
            sample_height = float(self.entry_height.get())
            sample_diameter = float(self.entry_diameter.get())
            num_points = int(self.entry_num_points.get())
            
            if any(x <= 0 for x in [E, phi, sample_height, sample_diameter, num_points]):
                raise ValueError("Все параметры должны быть положительными числами")
            
            if poisson <= 0 or poisson >= 0.5:
                raise ValueError("Коэффициент Пуассона должен быть между 0 и 0.5")
            
            sigma3_values = self.get_sigma3_values()
            if not sigma3_values:
                raise ValueError("Не указаны значения бокового давления σ₃")
            
            if len(sigma3_values) < 2:
                raise ValueError("Необходимо указать хотя бы 2 значения σ₃")
            
            self.generator = TriaxialTestGenerator(E, phi, c, sample_height, sample_diameter, poisson)
            self.test_results = self.generator.generate_test_series(sigma3_values, num_points)
            
            self.display_results()
            
            self.status_var.set(f"Данные сгенерированы! Создано {len(sigma3_values)} испытаний по {num_points} точек.")
            messagebox.showinfo("Успех", f"Данные успешно сгенерированы!\nСоздано {len(sigma3_values)} испытаний по {num_points} точек.")
            
        except ValueError as e:
            self.status_var.set("Ошибка ввода данных")
            messagebox.showerror("Ошибка", f"Проверьте правильность введенных данных!\n{e}")
    
    def display_results(self):
        if not hasattr(self, 'test_results'):
            return
        
        text = "РЕЗУЛЬТАТЫ ИСПЫТАНИЙ ТРЕХОСНОГО СЖАТИЯ\n"
        text += "=" * 70 + "\n\n"
        
        text += f"Параметры грунта:\n"
        text += f"  - Модуль деформации E: {self.generator.E} кПа\n"
        text += f"  - Угол внутреннего трения φ: {np.degrees(self.generator.phi):.1f}°\n"
        text += f"  - Удельное сцепление c: {self.generator.c} кПа\n"
        text += f"  - Коэффициент Пуассона ν: {self.generator.poisson_ratio}\n\n"
        
        text += f"Параметры образца:\n"
        text += f"  - Высота h₀: {self.generator.sample_height} мм\n"
        text += f"  - Диаметр d₀: {self.generator.sample_diameter} мм\n"
        text += f"  - Площадь сечения A₀: {self.generator.initial_area:.1f} мм²\n"
        text += f"  - Объем V₀: {self.generator.initial_volume:.1f} мм³\n"
        text += f"  - Количество точек на кривую: {len(self.test_results[0]['epsilon_axial'])}\n\n"
        
        text += "Результаты испытаний:\n"
        text += "-" * 70 + "\n"
        
        for i, test in enumerate(self.test_results, 1):
            max_force_idx = np.argmax(test['force'])
            
            text += f"Испытание {i} (σ₃ = {test['sigma_3']:.1f} кПа):\n"
            text += f"  - Предельное давление σ₁: {test['sigma_1_max']:.1f} кПа\n"
            text += f"  - Предельный девиатор: {test['sigma_1_max'] - test['sigma_3']:.1f} кПа\n"
            text += f"  - Макс. осевая деформация: {np.max(test['epsilon_axial']) * 100:.2f} %\n"
            text += f"  - Макс. объемная деформация: {np.max(test['epsilon_vol']) * 100:.2f} %\n"
            text += f"  - Изменение объема при макс. нагрузке: {test['delta_V'][max_force_idx]:.1f} мм³\n"
            text += f"  - Макс. усилие: {np.max(test['force']):.2f} кН\n\n"
        
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
                    self.plot_data()
                else:
                    messagebox.showerror("Ошибка", "Не удалось экспортировать данные")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def plot_data(self):
        if not hasattr(self, 'test_results'):
            return
        
        for widget in self.figure_frame.winfo_children():
            widget.destroy()
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            
            # 1. Кривые деформирования (осевая деформация)
            for test in self.test_results:
                ax1.plot(test['epsilon_axial'] * 100, test['deviator'], 
                        label=f'σ₃ = {test["sigma_3"]:.1f} кПа')
            
            ax1.set_xlabel('Осевая деформация ε_axial, %')
            ax1.set_ylabel('Девиатор напряжения (σ₁-σ₃), кПа')
            ax1.set_title('Кривые деформирования (осевые)')
            ax1.legend()
            ax1.grid(True)
            
            # 2. Объемные деформации
            for test in self.test_results:
                ax2.plot(test['epsilon_axial'] * 100, test['epsilon_vol'] * 100,
                        label=f'σ₃ = {test["sigma_3"]:.1f} кПа')
            
            ax2.set_xlabel('Осевая деформация ε_axial, %')
            ax2.set_ylabel('Объемная деформация ε_vol, %')
            ax2.set_title('Объемные деформации')
            ax2.legend()
            ax2.grid(True)
            
            # 3. Абсолютное изменение объема
            for test in self.test_results:
                ax3.plot(test['epsilon_axial'] * 100, test['delta_V'],
                        label=f'σ₃ = {test["sigma_3"]:.1f} кПа')
            
            ax3.set_xlabel('Осевая деформация ε_axial, %')
            ax3.set_ylabel('Изменение объема ΔV, мм³')
            ax3.set_title('Абсолютное изменение объема')
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