import tkinter as tk
from tkinter import ttk

class SalaryCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор з/п для Насти")
        self.root.geometry("800x500")
        
        # Плотность металла (константа)
        self.density = 8  # г/см³
        
        # Цены для каждого вида обработки (до, после)
        self.prices = {
            "Полировка": (120, 205),
            "AquaSteel": (75, 75),
            "Шлифовка": (120, 150),
            "Текстура": (50, 60),
            "Узорка/Матирование": (60, 125),
            "Нитрид все цвета": (14200, 8000),
            "Нитрид золото, шампань и розовое золото": (7600, 6000)
        }
        
        # Создаем основные фреймы
        self.create_input_frame()
        self.create_result_frame()
        
    def create_input_frame(self):
        input_frame = ttk.LabelFrame(self.root, text="Параметры листа", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Размер листа
        ttk.Label(input_frame, text="Раскрой листа:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sheet_size = tk.StringVar()
        sizes = ["1000х2000", "1250х2500", "1500х3000"]
        size_combobox = ttk.Combobox(input_frame, textvariable=self.sheet_size, values=sizes, state="readonly")
        size_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        size_combobox.current(0)
        
        # Толщина листа
        ttk.Label(input_frame, text="Толщина (мм):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.thickness = tk.StringVar()
        thicknesses = ["0,5", "0,7", "0,8", "1,0", "1,2", "1,5", "2,0", "2,5", "3,0"]
        thickness_combobox = ttk.Combobox(input_frame, textvariable=self.thickness, values=thicknesses, state="readonly")
        thickness_combobox.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        thickness_combobox.current(0)
        
        # Вид обработки
        ttk.Label(input_frame, text="Вид обработки:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.treatment = tk.StringVar()
        treatments = list(self.prices.keys())
        treatment_combobox = ttk.Combobox(input_frame, textvariable=self.treatment, values=treatments, state="readonly")
        treatment_combobox.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        treatment_combobox.current(0)
        
        # Количество листов
        ttk.Label(input_frame, text="Количество листов:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quantity = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity)
        quantity_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Кнопка расчета
        calculate_btn = ttk.Button(input_frame, text="Рассчитать з/п", command=self.calculate)
        calculate_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Настройка расширяемости колонок
        input_frame.columnconfigure(1, weight=1)
    
    def create_result_frame(self):
        result_frame = ttk.LabelFrame(self.root, text="Результаты расчета зарплаты", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица зарплаты
        salary_columns = ("Параметр", "З/П до", "З/П после")
        self.salary_tree = ttk.Treeview(result_frame, columns=salary_columns, show="headings", height=2)
        
        # Настройка колонок
        for col in salary_columns:
            self.salary_tree.heading(col, text=col)
            self.salary_tree.column(col, width=200, anchor=tk.CENTER)
        
        self.salary_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Таблица деталей
        details_columns = ("Параметр", "Значение")
        self.details_tree = ttk.Treeview(result_frame, columns=details_columns, show="headings", height=5)
        
        self.details_tree.heading("Параметр", text="Параметр")
        self.details_tree.heading("Значение", text="Значение")
        self.details_tree.column("Параметр", width=250, anchor=tk.W)
        self.details_tree.column("Значение", width=250, anchor=tk.W)
        
        self.details_tree.pack(fill=tk.BOTH, expand=True)
    
    def calculate(self):
        # Очищаем предыдущие результаты
        for item in self.salary_tree.get_children():
            self.salary_tree.delete(item)
        
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        try:
            # Получаем параметры
            size = self.sheet_size.get()
            thickness = float(self.thickness.get().replace(",", "."))
            treatment = self.treatment.get()
            quantity = int(self.quantity.get())
            
            if quantity <= 0:
                raise ValueError("Количество должно быть положительным числом")
            
            # Размеры листа в мм
            width, height = map(int, size.split("х"))
            
            # Рассчитываем массу листа
            volume_cm3 = (width / 10) * (height / 10) * (thickness / 10)  # см * см * см = см³
            mass_kg = (volume_cm3 * self.density) / 1000  # кг
            
            # Получаем цены для выбранной обработки
            price_before, price_after = self.prices[treatment]
            
            # Рассчитываем зарплату
            salary_before = quantity * mass_kg * price_before
            salary_after = quantity * mass_kg * price_after
            
            # Добавляем результаты в таблицу зарплаты
            self.salary_tree.insert("", tk.END, values=(
                f"За {quantity} лист(ов)", 
                f"{salary_before:.2f} руб", 
                f"{salary_after:.2f} руб"
            ))
            
            # Добавляем детали расчета
            self.details_tree.insert("", tk.END, values=("Размер листа", f"{width}×{height} мм"))
            self.details_tree.insert("", tk.END, values=("Толщина листа", f"{thickness} мм"))
            self.details_tree.insert("", tk.END, values=("Вид обработки", treatment))
            self.details_tree.insert("", tk.END, values=("Масса одного листа", f"{mass_kg:.2f} кг"))
            self.details_tree.insert("", tk.END, values=("Общая масса", f"{mass_kg * quantity:.2f} кг"))
            self.details_tree.insert("", tk.END, values=("Цена до", f"{price_before} руб/кг"))
            self.details_tree.insert("", tk.END, values=("Цена после обработки", f"{price_after} руб/кг"))
        
        except ValueError as e:
            self.details_tree.insert("", tk.END, values=("Ошибка", "Проверьте правильность введенных данных"))
            self.details_tree.insert("", tk.END, values=("Сообщение", str(e)))

if __name__ == "__main__":
    root = tk.Tk()
    app = SalaryCalculatorApp(root)
    root.mainloop()