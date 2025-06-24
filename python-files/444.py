import tkinter as tk
from tkinter import ttk, messagebox

class BallValveConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Конфигуратор шарового крана")
        self.root.geometry("600x500")
        
        # Создаем стиль
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 10), padding=5)
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TEntry', font=('Arial', 10), padding=5)
        
        # Основной фрейм
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Конфигуратор шарового крана", 
            font=('Arial', 14, 'bold')
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Поля ввода
        self.create_input_fields()
        
        # Кнопка расчета
        self.calculate_btn = ttk.Button(
            self.main_frame, 
            text="Рассчитать конфигурацию", 
            command=self.calculate_configuration
        )
        self.calculate_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Поле вывода результатов
        self.result_text = tk.Text(
            self.main_frame, 
            height=15, 
            width=60, 
            font=('Arial', 10), 
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.result_text.grid(row=4, column=0, columnspan=2)
        
        # Полоса прокрутки
        self.scrollbar = ttk.Scrollbar(
            self.main_frame, 
            orient=tk.VERTICAL, 
            command=self.result_text.yview
        )
        self.scrollbar.grid(row=4, column=2, sticky='ns')
        self.result_text['yscrollcommand'] = self.scrollbar.set
        
        # Настройка веса строк и столбцов
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def create_input_fields(self):
        """Создает поля для ввода параметров"""
        # Диаметр
        self.diameter_label = ttk.Label(self.main_frame, text="Диаметр (мм):")
        self.diameter_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.diameter_entry = ttk.Entry(self.main_frame)
        self.diameter_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Температура
        self.temp_label = ttk.Label(self.main_frame, text="Температура (°C):")
        self.temp_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.temp_entry = ttk.Entry(self.main_frame)
        self.temp_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Давление
        self.pressure_label = ttk.Label(self.main_frame, text="Давление (КГС):")
        self.pressure_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.pressure_entry = ttk.Entry(self.main_frame)
        self.pressure_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
    
    def calculate_configuration(self):
        """Рассчитывает конфигурацию на основе введенных данных"""
        try:
            # Получаем значения из полей ввода
            a = int(self.diameter_entry.get())
            b = int(self.temp_entry.get())
            c = int(self.pressure_entry.get())
            
            # Проверяем диапазоны
            diametr = range(0, 3000)
            temperatura = range(-196, 600)
            davlenie = range(0, 600)
            
            if a not in diametr or b not in temperatura or c not in davlenie:
                messagebox.showerror(
                    "Ошибка", 
                    "Пожалуйста, введите значения в допустимых диапазонах:\n"
                    "Диаметр: 0-3000 мм\n"
                    "Температура: -196 до 600 °C\n"
                    "Давление: 0-600 КГС"
                )
                return
            
            # Очищаем поле вывода
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            
            # Добавляем результаты в поле вывода
            self.result_text.insert(tk.END, "=== РЕЗУЛЬТАТЫ КОНФИГУРАЦИИ ===\n\n")
            
            # Логика конфигурации (из вашего кода)
            if a in diametr and b in temperatura and c in davlenie:
                self.result_text.insert(tk.END, f"Сталь корпуса: LF2\n")
                
                if a < 50:
                    if b < 200:
                        self.result_text.insert(tk.END, "Шар: F321\n")
                        self.result_text.insert(tk.END, "Седло: PTFE\n")
                        self.result_text.insert(tk.END, "Материал штока: 17-4PH\n")
                        self.result_text.insert(tk.END, "Материал уплотнения: Металл/полимер\n")
                    elif b >= 200:
                        self.result_text.insert(tk.END, "Шар: F321+STL/Ni\n")
                        self.result_text.insert(tk.END, "Седло: F321+STL/Ni\n")
                        self.result_text.insert(tk.END, "Материал штока: 17-4PH\n")
                        self.result_text.insert(tk.END, "Материал уплотнения: Металл/металл\n")
                    
                    if c <= 50:
                        self.result_text.insert(tk.END, "Фланцевое соединение: B ГОСТ 33259\n")
                    elif 63 <= c < 250:
                        self.result_text.insert(tk.END, "Фланцевое соединение: J ГОСТ 33259\n")
                    elif c >= 250:
                        self.result_text.insert(tk.END, "Фланцевое соединение: RTJ Class 1500 ASME B16.5\n")
                
                elif a == 50:
                    if b < 200:
                        self.result_text.insert(tk.END, "Шар: LF2+ENP\n")
                        self.result_text.insert(tk.END, "Седло: PTFE\n")
                        self.result_text.insert(tk.END, "Материал штока: 17-4PH\n")
                        self.result_text.insert(tk.END, "Материал уплотнения: Металл/полимер\n")
                    elif b >= 200:
                        self.result_text.insert(tk.END, "Шар: F321+STL/Ni\n")
                        self.result_text.insert(tk.END, "Седло: F321+STL/Ni\n")
                        self.result_text.insert(tk.END, "Материал штока: 17-4PH\n")
                        self.result_text.insert(tk.END, "Материал уплотнения: Металл/металл\n")
                    
                    if c <= 50:
                        self.result_text.insert(tk.END, "Фланцевое соединение: B ГОСТ 33259\n")
                    elif 63 <= c < 250:
                        self.result_text.insert(tk.END, "Фланцевое соединение: J ГОСТ 33259\n")
                    elif c >= 250:
                        self.result_text.insert(tk.END, "Фланцевое соединение: RTJ Class 1500 ASME B16.5\n")
                
                elif a > 50:
                    if b < 200:
                        self.result_text.insert(tk.END, "Шар: LF2+ENP\n")
                        self.result_text.insert(tk.END, "Седло: LF2+ENP+PTFE\n")
                        self.result_text.insert(tk.END, "Материал штока: 17-4PH\n")
                        self.result_text.insert(tk.END, "Материал уплотнения: Металл/полимер\n")
                    elif b >= 200:
                        self.result_text.insert(tk.END, "Шар: F321+STL/Ni\n")
                        self.result_text.insert(tk.END, "Седло: F321+STL/Ni\n")
                        self.result_text.insert(tk.END, "Материал штока: 17-4PH\n")
                        self.result_text.insert(tk.END, "Материал уплотнения: Металл/металл\n")
                    
                    if c <= 50:
                        self.result_text.insert(tk.END, "Фланцевое соединение: B ГОСТ 33259\n")
                    elif 63 <= c < 250:
                        self.result_text.insert(tk.END, "Фланцевое соединение: J ГОСТ 33259\n")
                    elif c >= 250:
                        self.result_text.insert(tk.END, "Фланцевое соединение: RTJ Class 1500 ASME B16.5\n")
            
            # Делаем поле вывода снова доступным только для чтения
            self.result_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror(
                "Ошибка", 
                "Пожалуйста, введите корректные числовые значения во все поля"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = BallValveConfigurator(root)
    root.mainloop()