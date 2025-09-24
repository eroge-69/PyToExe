import tkinter as tk
from tkinter import ttk, messagebox
import math

class EkonivaCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Эконива - Калькулятор этикеток")
        self.root.geometry("650x750")
        self.root.configure(bg='#f0f0f0')
        
        # Стиль
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2e7d32')
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Calculate.TButton', background='#4caf50', foreground='white')
        self.style.configure('Red.TLabel', foreground='#d32f2f', font=('Arial', 11, 'bold'))
        
        self.create_logo()
        self.create_notebook()
        
    def create_logo(self):
        """Создание логотипа"""
        logo_frame = ttk.Frame(self.root)
        logo_frame.pack(pady=10)
        
        logo_text = """╔══════════════════════════════════╗
║           ЭКОНИВА                ║
║   Калькулятор расчета этикеток   ║
╚══════════════════════════════════╝"""
        
        logo_label = ttk.Label(logo_frame, text=logo_text, font=('Courier', 12), 
                              justify='center', background='#e8f5e9')
        logo_label.pack(padx=20, pady=10)
    
    def create_notebook(self):
        """Создание вкладок"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка Честный Знак
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Честный Знак")
        self.create_honest_sign_tab(tab1)
        
        # Вкладка Круглая Этикетка
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Круглая Этикетка")
        self.create_round_label_tab(tab2)
        
        # Вкладка Упаковка flex
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Упаковка 1л flex")
        self.create_package_flex_tab(tab3)
        
        # Вкладка Все расчеты
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Все расчеты")
        self.create_all_calculations_tab(tab4)
    
    def create_honest_sign_tab(self, parent):
        """Вкладка Честный Знак с учетом плотности"""
        # Заголовок
        title_label = ttk.Label(parent, text="Расчет для Честного Знака", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Информация о фиксированных значениях
        info_frame = ttk.LabelFrame(parent, text="Исходные данные")
        info_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(info_frame, text="Известный размер: 245 мм").pack(anchor='w', pady=2)
        ttk.Label(info_frame, text="Известное количество: 20 000 шт").pack(anchor='w', pady=2)
        
        # Поля ввода
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="Новый размер (мм):").grid(row=0, column=0, sticky='w', pady=5)
        self.hs_new_size = tk.StringVar(value="200")
        ttk.Entry(input_frame, textvariable=self.hs_new_size, width=10).grid(row=0, column=1, padx=10)
        
        ttk.Label(input_frame, text="Коэффициент плотности (0.9-1.1):").grid(row=1, column=0, sticky='w', pady=5)
        self.hs_density = tk.StringVar(value="1.0")
        ttk.Entry(input_frame, textvariable=self.hs_density, width=10).grid(row=1, column=1, padx=10)
        
        # Кнопка расчета
        ttk.Button(parent, text="Рассчитать", command=self.calculate_honest_sign,
                  style='Calculate.TButton').pack(pady=10)
        
        # Результат
        result_frame = ttk.LabelFrame(parent, text="Результаты расчета")
        result_frame.pack(fill='x', padx=20, pady=10)
        
        self.hs_base_var = tk.StringVar(value="Базовый расчет: -")
        self.hs_adjusted_var = tk.StringVar(value="С учетом плотности: -")
        self.hs_range_var = tk.StringVar(value="Диапазон (±3%): -")
        
        ttk.Label(result_frame, textvariable=self.hs_base_var).pack(anchor='w', pady=2)
        ttk.Label(result_frame, textvariable=self.hs_adjusted_var).pack(anchor='w', pady=2)
        ttk.Label(result_frame, textvariable=self.hs_range_var, style='Red.TLabel').pack(anchor='w', pady=2)
    
    def create_round_label_tab(self, parent):
        """Вкладка Круглая Этикетка"""
        # Заголовок
        title_label = ttk.Label(parent, text="Расчет для Круглой Этикетки", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Информация о фиксированных значениях
        info_frame = ttk.LabelFrame(parent, text="Исходные данные")
        info_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(info_frame, text="Известный размер: 360 мм").pack(anchor='w', pady=2)
        ttk.Label(info_frame, text="Известное количество: 7 500 шт").pack(anchor='w', pady=2)
        
        # Поле ввода
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="Новый размер (мм):").grid(row=0, column=0, sticky='w', pady=5)
        self.rl_new_size = tk.StringVar(value="200")
        ttk.Entry(input_frame, textvariable=self.rl_new_size, width=10).grid(row=0, column=1, padx=10)
        
        # Кнопка расчета
        ttk.Button(parent, text="Рассчитать", command=self.calculate_round_label,
                  style='Calculate.TButton').pack(pady=10)
        
        # Результат
        self.rl_result_var = tk.StringVar(value="Результат: -")
        result_label = ttk.Label(parent, textvariable=self.rl_result_var, 
                                font=('Arial', 12, 'bold'), foreground='#d32f2f')
        result_label.pack(pady=10)
    
    def create_package_flex_tab(self, parent):
        """Вкладка Упаковка flex (БЕЗ коэффициента плотности)"""
        # Заголовок
        title_label = ttk.Label(parent, text="Расчет для Упаковки 1л flex", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Информация о фиксированных значениях
        info_frame = ttk.LabelFrame(parent, text="Параметры материала")
        info_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(info_frame, text="Внутренний диаметр: 165 мм").pack(anchor='w', pady=2)
        ttk.Label(info_frame, text="Толщина материала: 0.435 мм").pack(anchor='w', pady=2)
        ttk.Label(info_frame, text="Расход на штуку: 0.29 м").pack(anchor='w', pady=2)
        
        # Поле ввода
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(input_frame, text="Внешний диаметр рулона (мм):").grid(row=0, column=0, sticky='w', pady=5)
        self.pf_external_diam = tk.StringVar(value="650")
        ttk.Entry(input_frame, textvariable=self.pf_external_diam, width=10).grid(row=0, column=1, padx=10)
        
        # Кнопка расчета
        ttk.Button(parent, text="Рассчитать", command=self.calculate_package_flex,
                  style='Calculate.TButton').pack(pady=10)
        
        # Результат
        result_frame = ttk.LabelFrame(parent, text="Результаты расчета")
        result_frame.pack(fill='x', padx=20, pady=10)
        
        self.pf_result_var = tk.StringVar(value="Количество штук: -")
        self.pf_details_var = tk.StringVar()
        
        ttk.Label(result_frame, textvariable=self.pf_result_var, style='Red.TLabel').pack(anchor='w', pady=2)
        ttk.Label(result_frame, textvariable=self.pf_details_var, justify='left').pack(anchor='w', pady=2)
    
    def create_all_calculations_tab(self, parent):
        """Вкладка Все расчеты"""
        title_label = ttk.Label(parent, text="Выполнить все расчеты", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Поля ввода
        input_frame = ttk.LabelFrame(parent, text="Параметры для расчета")
        input_frame.pack(fill='x', padx=20, pady=10)
        
        # ЧЗ
        ttk.Label(input_frame, text="Размер для ЧЗ (мм):").grid(row=0, column=0, sticky='w', pady=5, padx=10)
        self.all_hs_size = tk.StringVar(value="200")
        ttk.Entry(input_frame, textvariable=self.all_hs_size, width=10).grid(row=0, column=1, pady=5)
        
        ttk.Label(input_frame, text="Плотность для ЧЗ:").grid(row=0, column=2, sticky='w', pady=5, padx=10)
        self.all_hs_density = tk.StringVar(value="1.0")
        ttk.Entry(input_frame, textvariable=self.all_hs_density, width=8).grid(row=0, column=3, pady=5)
        
        # КЭ
        ttk.Label(input_frame, text="Размер для КЭ (мм):").grid(row=1, column=0, sticky='w', pady=5, padx=10)
        self.all_rl_size = tk.StringVar(value="200")
        ttk.Entry(input_frame, textvariable=self.all_rl_size, width=10).grid(row=1, column=1, pady=5)
        
        # Упаковка
        ttk.Label(input_frame, text="Внешний диаметр (мм):").grid(row=2, column=0, sticky='w', pady=5, padx=10)
        self.all_pf_diam = tk.StringVar(value="650")
        ttk.Entry(input_frame, textvariable=self.all_pf_diam, width=10).grid(row=2, column=1, pady=5)
        
        # Кнопка расчета
        ttk.Button(parent, text="Выполнить все расчеты", command=self.calculate_all,
                  style='Calculate.TButton').pack(pady=10)
        
        # Результаты
        results_frame = ttk.LabelFrame(parent, text="Результаты расчетов")
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.all_results_text = tk.Text(results_frame, height=12, width=60, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.all_results_text.yview)
        self.all_results_text.configure(yscrollcommand=scrollbar.set)
        
        self.all_results_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
    
    def calculate_honest_sign(self):
        """Расчет Честного Знака с учетом плотности"""
        try:
            known_size = 245
            known_quantity = 20000
            new_size = float(self.hs_new_size.get())
            density = float(self.hs_density.get())
            
            if not 0.9 <= density <= 1.1:
                messagebox.showwarning("Внимание", "Коэффициент плотности должен быть в диапазоне 0.9-1.1")
                return
            
            # Базовый расчет по пропорции
            base_quantity = (new_size * known_quantity) / known_size
            
            # Корректировка с учетом плотности
            adjusted_quantity = base_quantity * density
            
            # Учет производственной погрешности (±3%)
            production_tolerance = 0.03
            min_quantity = adjusted_quantity * (1 - production_tolerance)
            max_quantity = adjusted_quantity * (1 + production_tolerance)
            
            self.hs_base_var.set(f"Базовый расчет: {round(base_quantity)} шт")
            self.hs_adjusted_var.set(f"С учетом плотности ({density}): {round(adjusted_quantity)} шт")
            self.hs_range_var.set(f"Диапазон (±3%): {round(min_quantity)} - {round(max_quantity)} шт")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def calculate_round_label(self):
        """Расчет Круглой Этикетки"""
        try:
            known_size = 360
            known_quantity = 7500
            new_size = float(self.rl_new_size.get())
            
            new_quantity = (new_size * known_quantity) / known_size
            result = round(new_quantity)
            
            self.rl_result_var.set(f"Результат: {result} шт")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
    
    def calculate_package_flex(self):
        """Расчет Упаковки flex (БЕЗ коэффициента плотности)"""
        try:
            INTERNAL_DIAMETER = 165
            MATERIAL_THICKNESS = 0.435
            MATERIAL_PER_UNIT = 0.29
            
            external_diameter = float(self.pf_external_diam.get())
            
            # Расчеты (без коэффициента плотности)
            turns = (external_diameter - INTERNAL_DIAMETER) / (2 * MATERIAL_THICKNESS)
            avg_diameter = (external_diameter + INTERNAL_DIAMETER) / 2
            turn_length_m = (math.pi * avg_diameter) / 1000
            total_length_m = turn_length_m * turns
            quantity = round(total_length_m / MATERIAL_PER_UNIT)
            
            self.pf_result_var.set(f"Количество штук: {quantity} шт")
            
            # Детали
            details = f"""Детали расчета:
• Количество витков: {turns:.1f}
• Средний диаметр: {avg_diameter:.1f} мм
• Длина витка: {turn_length_m:.3f} м
• Общая длина материала: {total_length_m:.1f} м"""
            
            self.pf_details_var.set(details)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
    
    def calculate_all(self):
        """Выполнение всех расчетов"""
        try:
            # ЧЗ с плотностью
            hs_size = float(self.all_hs_size.get())
            hs_density = float(self.all_hs_density.get())
            hs_result = round((hs_size * 20000) / 245 * hs_density)
            
            # КЭ
            rl_size = float(self.all_rl_size.get())
            rl_result = round((rl_size * 7500) / 360)
            
            # Упаковка (без плотности)
            pf_diam = float(self.all_pf_diam.get())
            turns = (pf_diam - 165) / (2 * 0.435)
            avg_diam = (pf_diam + 165) / 2
            total_length = (math.pi * avg_diam * turns) / 1000
            pf_result = round(total_length / 0.29)
            
            # Вывод результатов
            results_text = f"""РЕЗУЛЬТАТЫ РАСЧЕТОВ:

ЧЕСТНЫЙ ЗНАК:
• Размер: {hs_size} мм
• Плотность: {hs_density}
• Количество: {hs_result} шт

КРУГЛАЯ ЭТИКЕТКА:
• Размер: {rl_size} мм
• Количество: {rl_result} шт

УПАКОВКА 1л FLEX:
• Внешний диаметр: {pf_diam} мм
• Количество витков: {turns:.1f}
• Средний диаметр: {avg_diam:.1f} мм
• Общая длина: {total_length:.1f} м
• Количество: {pf_result} шт

ИТОГО: {hs_result + rl_result + pf_result} шт (сумма по всем позициям)"""
            
            self.all_results_text.delete(1.0, tk.END)
            self.all_results_text.insert(1.0, results_text)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введенных данных")

def main():
    root = tk.Tk()
    app = EkonivaCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()