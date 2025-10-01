import tkinter as tk
from tkinter import ttk
import math

class PCCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор параметров печатных плат")
        
  
 # Устанавливаем начальный размер окна
        self.root.geometry("1000x700")
        
        # Устанавливаем МИНИМАЛЬНЫЙ размер окна - окно нельзя будет сделать меньше
        self.root.minsize(1400, 700)  # Минимальная ширина 950px, высота 650px
        self.root.configure(bg='#f5f7fa')
        
        # Стили
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f5f7fa')
        self.style.configure('TLabel', background='#f5f7fa', font=('Segoe UI', 10))
        self.style.configure('Title.TLabel', background='#f5f7fa', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Result.TLabel', background='#ecf0f1', font=('Courier New', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        
        # Словари для единиц измерения
        self.thickness_units = {
            "унция/фут²": 0.0035,
            "мил": 0.00254,
            "мм": 0.1,
            "мкм": 0.0001
        }
        
        self.temp_units = {
            "°C": "C",
            "°F": "F"
        }
        
        self.length_units = {
            "дюйм": 0.393701,
            "фут": 0.032808,
            "мил": 393.7008,
            "мм": 10.0,
            "мкм": 10000.0,
            "см": 1.0,
            "м": 0.01
        }
        
        self.width_units = {
            "мил": 0.00254,
            "мм": 0.1,
            "мкм": 0.0001
        }
        
        self.create_widgets()
        self.compute()  # Первоначальный расчет
        
    def create_widgets(self):
        # Заголовок
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=20, padx=20, fill='x')
        
        title_label = ttk.Label(header_frame, text="Калькулятор параметров печатных плат", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Расчет ширины дорожек, сопротивления, падения напряжения и потерь мощности для внутренних и внешних слоев печатной платы",
                                  justify='center')
        subtitle_label.pack(pady=10)
        
        status_label = ttk.Label(header_frame, text="✓ Автоматический расчет при изменении параметров")
        status_label.pack()
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Создаем три колонки
        self.create_input_section(main_frame)
        self.create_internal_section(main_frame)
        self.create_external_section(main_frame)
        
        # Кнопка сброса
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        reset_btn = ttk.Button(button_frame, text="Сбросить значения", command=self.reset_form)
        reset_btn.pack(pady=10)
        
        # Информационная панель
        self.create_info_section()
        
        # Настройка сетки главного контейнера
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
    
    def create_input_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Общие входные данные", padding=15)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Сила тока
        ttk.Label(frame, text="Сила тока в цепи, А").grid(row=0, column=0, sticky='w', pady=5)
        self.current_var = tk.DoubleVar(value=0)
        current_entry = ttk.Entry(frame, textvariable=self.current_var)
        current_entry.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        current_entry.bind('<KeyRelease>', lambda e: self.compute())
        
        # Толщина фольги
        ttk.Label(frame, text="Толщина слоя фольги").grid(row=1, column=0, sticky='w', pady=5)
        thickness_frame = ttk.Frame(frame)
        thickness_frame.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        self.thickness_var = tk.DoubleVar(value=0)
        thickness_entry = ttk.Entry(thickness_frame, textvariable=self.thickness_var, width=15)
        thickness_entry.pack(side='left', fill='x', expand=True)
        thickness_entry.bind('<KeyRelease>', lambda e: self.compute())
        
        self.thickness_unit_var = tk.StringVar(value="мм")
        thickness_unit = ttk.Combobox(thickness_frame, textvariable=self.thickness_unit_var, 
                                     values=list(self.thickness_units.keys()), 
                                     state="readonly", width=12)
        thickness_unit.pack(side='right')
        thickness_unit.bind('<<ComboboxSelected>>', lambda e: self.compute())
        
        # Повышение температуры
        ttk.Label(frame, text="Повышение температуры").grid(row=2, column=0, sticky='w', pady=5)
        temp_frame = ttk.Frame(frame)
        temp_frame.grid(row=2, column=1, pady=5, padx=5, sticky='ew')
        
        self.temp_rise_var = tk.DoubleVar(value=0)
        temp_entry = ttk.Entry(temp_frame, textvariable=self.temp_rise_var, width=15)
        temp_entry.pack(side='left', fill='x', expand=True)
        temp_entry.bind('<KeyRelease>', lambda e: self.compute())
        
        self.temp_rise_unit_var = tk.StringVar(value="°C")
        temp_unit = ttk.Combobox(temp_frame, textvariable=self.temp_rise_unit_var, 
                                values=list(self.temp_units.keys()), state="readonly", width=8)
        temp_unit.pack(side='right')
        temp_unit.bind('<<ComboboxSelected>>', lambda e: self.compute())
        
        # Температура окружающей среды
        ttk.Label(frame, text="Температура окружающей среды").grid(row=3, column=0, sticky='w', pady=5)
        amb_temp_frame = ttk.Frame(frame)
        amb_temp_frame.grid(row=3, column=1, pady=5, padx=5, sticky='ew')
        
        self.amb_temp_var = tk.DoubleVar(value=0)
        amb_temp_entry = ttk.Entry(amb_temp_frame, textvariable=self.amb_temp_var, width=15)
        amb_temp_entry.pack(side='left', fill='x', expand=True)
        amb_temp_entry.bind('<KeyRelease>', lambda e: self.compute())
        
        self.amb_temp_unit_var = tk.StringVar(value="°C")
        amb_temp_unit = ttk.Combobox(amb_temp_frame, textvariable=self.amb_temp_unit_var, 
                                    values=list(self.temp_units.keys()), state="readonly", width=8)
        amb_temp_unit.pack(side='right')
        amb_temp_unit.bind('<<ComboboxSelected>>', lambda e: self.compute())
        
        # Длина дорожки
        ttk.Label(frame, text="Длина дорожки").grid(row=4, column=0, sticky='w', pady=5)
        length_frame = ttk.Frame(frame)
        length_frame.grid(row=4, column=1, pady=5, padx=5, sticky='ew')
        
        self.length_var = tk.DoubleVar(value=0)
        length_entry = ttk.Entry(length_frame, textvariable=self.length_var, width=15)
        length_entry.pack(side='left', fill='x', expand=True)
        length_entry.bind('<KeyRelease>', lambda e: self.compute())
        
        self.length_unit_var = tk.StringVar(value="мм")
        length_unit = ttk.Combobox(length_frame, textvariable=self.length_unit_var, 
                                  values=list(self.length_units.keys()), 
                                  state="readonly", width=12)
        length_unit.pack(side='right')
        length_unit.bind('<<ComboboxSelected>>', lambda e: self.compute())
        
        # Настройка веса колонок
        frame.columnconfigure(1, weight=1)
    
    def create_internal_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Расчет для внутренних слоев", padding=15)
        frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        # Ширина дорожки
        ttk.Label(frame, text="Рекомендуемая ширина дорожки").grid(row=0, column=0, sticky='w', pady=5)
        width_frame = ttk.Frame(frame)
        width_frame.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        
        self.int_width_var = tk.StringVar()
        width_entry = ttk.Entry(width_frame, textvariable=self.int_width_var, state='readonly', width=15)
        width_entry.pack(side='left', fill='x', expand=True)
        
        self.int_width_unit_var = tk.StringVar(value="мм")
        width_unit = ttk.Combobox(width_frame, textvariable=self.int_width_unit_var, 
                                 values=list(self.width_units.keys()), state="readonly", width=12)
        width_unit.pack(side='right')
        width_unit.bind('<<ComboboxSelected>>', lambda e: self.compute())
        
        # Результаты
        results_frame = ttk.Frame(frame)
        results_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Сопротивление
        resistance_frame = ttk.Frame(results_frame)
        resistance_frame.pack(fill='x', pady=5)
        ttk.Label(resistance_frame, text="Сопротивление, Ом:").pack(side='left')
        self.int_resistance_var = tk.StringVar(value="-")
        ttk.Label(resistance_frame, textvariable=self.int_resistance_var, 
                 style='Result.TLabel').pack(side='right', fill='x', expand=True)
        
        # Падение напряжения
        voltage_frame = ttk.Frame(results_frame)
        voltage_frame.pack(fill='x', pady=5)
        ttk.Label(voltage_frame, text="Падение напряжения, В:").pack(side='left')
        self.int_voltage_var = tk.StringVar(value="-")
        ttk.Label(voltage_frame, textvariable=self.int_voltage_var, 
                 style='Result.TLabel').pack(side='right', fill='x', expand=True)
        
        # Потеря мощности
        power_frame = ttk.Frame(results_frame)
        power_frame.pack(fill='x', pady=5)
        ttk.Label(power_frame, text="Потеря мощности, Вт:").pack(side='left')
        self.int_power_var = tk.StringVar(value="-")
        ttk.Label(power_frame, textvariable=self.int_power_var, 
                 style='Result.TLabel').pack(side='right', fill='x', expand=True)
        
        frame.columnconfigure(1, weight=1)
    
    def create_external_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Расчет для внешних слоев", padding=15)
        frame.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        
        # Ширина дорожки
        ttk.Label(frame, text="Рекомендуемая ширина дорожки").grid(row=0, column=0, sticky='w', pady=5)
        width_frame = ttk.Frame(frame)
        width_frame.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        
        self.ext_width_var = tk.StringVar()
        width_entry = ttk.Entry(width_frame, textvariable=self.ext_width_var, state='readonly', width=15)
        width_entry.pack(side='left', fill='x', expand=True)
        
        self.ext_width_unit_var = tk.StringVar(value="мил")
        width_unit = ttk.Combobox(width_frame, textvariable=self.ext_width_unit_var, 
                                 values=list(self.width_units.keys()), state="readonly", width=12)
        width_unit.pack(side='right')
        width_unit.bind('<<ComboboxSelected>>', lambda e: self.compute())
        
        # Результаты
        results_frame = ttk.Frame(frame)
        results_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Сопротивление
        resistance_frame = ttk.Frame(results_frame)
        resistance_frame.pack(fill='x', pady=5)
        ttk.Label(resistance_frame, text="Сопротивление, Ом:").pack(side='left')
        self.ext_resistance_var = tk.StringVar(value="-")
        ttk.Label(resistance_frame, textvariable=self.ext_resistance_var, 
                 style='Result.TLabel').pack(side='right', fill='x', expand=True)
        
        # Падение напряжения
        voltage_frame = ttk.Frame(results_frame)
        voltage_frame.pack(fill='x', pady=5)
        ttk.Label(voltage_frame, text="Падение напряжения, В:").pack(side='left')
        self.ext_voltage_var = tk.StringVar(value="-")
        ttk.Label(voltage_frame, textvariable=self.ext_voltage_var, 
                 style='Result.TLabel').pack(side='right', fill='x', expand=True)
        
        # Потеря мощности
        power_frame = ttk.Frame(results_frame)
        power_frame.pack(fill='x', pady=5)
        ttk.Label(power_frame, text="Потеря мощности, Вт:").pack(side='left')
        self.ext_power_var = tk.StringVar(value="-")
        ttk.Label(power_frame, textvariable=self.ext_power_var, 
                 style='Result.TLabel').pack(side='right', fill='x', expand=True)
        
        frame.columnconfigure(1, weight=1)
    
    def create_info_section(self):
        info_frame = ttk.LabelFrame(self.root, text="О калькуляторе", padding=15)
        info_frame.pack(pady=20, padx=20, fill='x')
        
        # Создаем три колонки для информации
        info_container = ttk.Frame(info_frame)
        info_container.pack(fill='x')
        
        # Колонка 1
        col1 = ttk.Frame(info_container)
        col1.pack(side='left', fill='x', expand=True, padx=10)
        ttk.Label(col1, text="Как использовать", style='Title.TLabel').pack(anchor='w')
        ttk.Label(col1, text="Введите параметры вашей печатной платы в левой колонке. Расчет происходит автоматически при изменении любого параметра.", 
                 wraplength=250).pack(anchor='w', pady=5)
        
        # Колонка 2
        col2 = ttk.Frame(info_container)
        col2.pack(side='left', fill='x', expand=True, padx=10)
        ttk.Label(col2, text="Формулы расчета", style='Title.TLabel').pack(anchor='w')
        ttk.Label(col2, text="Калькулятор использует формулы IPC-2221 для расчета площади поперечного сечения дорожки на основе тока и повышения температуры.", 
                 wraplength=250).pack(anchor='w', pady=5)
        
        # Колонка 3
        col3 = ttk.Frame(info_container)
        col3.pack(side='left', fill='x', expand=True, padx=10)
        ttk.Label(col3, text="Применение", style='Title.TLabel').pack(anchor='w')
        ttk.Label(col3, text="Этот инструмент помогает правильно выбрать ширину дорожек для обеспечения надежной работы схемы без перегрева.", 
                 wraplength=250).pack(anchor='w', pady=5)
    
    def A_external(self, current, rise):
        k = 0.048
        b = 0.44
        c = 0.725
        return (current / (k * (rise ** b))) ** (1 / c)
    
    def A_internal(self, current, rise):
        k = 0.024
        b = 0.44
        c = 0.725
        return (current / (k * (rise ** b))) ** (1 / c)
    
    def compute(self, event=None):
        try:
            # Получаем значения
            Cur = self.current_var.get()
            if Cur <= 0:
                self.update_results_with_placeholders()
                return
            
            tempR = self.temp_rise_var.get()
            if tempR <= 0:
                self.update_results_with_placeholders()
                return
            
            # Конвертируем температуру если нужно
            temp_unit_key = self.temp_rise_unit_var.get()
            if self.temp_units[temp_unit_key] == "F":
                tempR = tempR * 5 / 9
            
            thick_value = self.thickness_var.get()
            if thick_value <= 0:
                self.update_results_with_placeholders()
                return
            
            thick_unit_key = self.thickness_unit_var.get()
            thick = thick_value * self.thickness_units[thick_unit_key]
            
            ambT = self.amb_temp_var.get()
            amb_temp_unit_key = self.amb_temp_unit_var.get()
            if self.temp_units[amb_temp_unit_key] == "F":
                ambT = (ambT - 32) * 5 / 9
            
            length_value = self.length_var.get()
            if length_value <= 0:
                self.update_results_with_placeholders()
                return
            
            length_unit_key = self.length_unit_var.get()
            traceL = length_value / self.length_units[length_unit_key]
            
            # Константы
            rho = 1.7e-6
            alpha = 3.9e-3
            
            # Расчет для внутренних слоев
            Ai = self.A_internal(Cur, tempR)
            Ai_converted = Ai * 2.54 * 2.54 / 1e6
            RTWi = Ai_converted / thick
            
            int_width_unit_key = self.int_width_unit_var.get()
            RTWi = RTWi / self.width_units[int_width_unit_key]
            
            Tval = ambT + tempR
            RSi = (rho * traceL / Ai_converted) * (1 + alpha * (Tval - 25))
            VDi = RSi * Cur
            PLi = Cur * Cur * RSi
            
            # Расчет для внешних слоев
            Ae = self.A_external(Cur, tempR)
            Ae_converted = Ae * 2.54 * 2.54 / 1e6
            RTWe = Ae_converted / thick
            
            ext_width_unit_key = self.ext_width_unit_var.get()
            RTWe = RTWe / self.width_units[ext_width_unit_key]
            
            RSe = (rho * traceL / Ae_converted) * (1 + alpha * (Tval - 25))
            VDe = RSe * Cur
            PLe = Cur * Cur * RSe
            
            # Обновляем интерфейс
            self.int_width_var.set(f"{RTWi:.10f}")
            self.int_resistance_var.set(f"{RSi:.10f}")
            self.int_voltage_var.set(f"{VDi:.10f}")
            self.int_power_var.set(f"{PLi:.10f}")
            
            self.ext_width_var.set(f"{RTWe:.10f}")
            self.ext_resistance_var.set(f"{RSe:.10f}")
            self.ext_voltage_var.set(f"{VDe:.10f}")
            self.ext_power_var.set(f"{PLe:.10f}")
            
        except (ValueError, ZeroDivisionError, TypeError, KeyError) as e:
            print(f"Ошибка расчета: {e}")
            self.update_results_with_placeholders()
    
    def update_results_with_placeholders(self):
        self.int_width_var.set("")
        self.int_resistance_var.set("-")
        self.int_voltage_var.set("-")
        self.int_power_var.set("-")
        
        self.ext_width_var.set("")
        self.ext_resistance_var.set("-")
        self.ext_voltage_var.set("-")
        self.ext_power_var.set("-")
    
    def reset_form(self):
        self.current_var.set(0)
        self.thickness_var.set(0)
        self.thickness_unit_var.set("мм")
        self.temp_rise_var.set(0)
        self.temp_rise_unit_var.set("°C")
        self.amb_temp_var.set(0)
        self.amb_temp_unit_var.set("°C")
        self.length_var.set(0)
        self.length_unit_var.set("мм")
        self.int_width_unit_var.set("мм")
        self.ext_width_unit_var.set("мм")
        
        self.compute()

def main():
    root = tk.Tk()
    app = PCCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()