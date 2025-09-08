import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
from datetime import datetime

class DekanCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор материалов Декан ВЭ")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Переменные для хранения данных
        self.coating_type = tk.IntVar(value=1)
        self.diameter = tk.DoubleVar(value=0.325)
        self.length = tk.DoubleVar(value=1.0)
        self.tape_width = tk.DoubleVar(value=0.1)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка расчета
        calc_frame = ttk.Frame(notebook)
        notebook.add(calc_frame, text="Расчет")
        
        # Вкладка справки
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Справка")
        
        self.setup_calculation_tab(calc_frame)
        self.setup_info_tab(info_frame)
        
    def setup_calculation_tab(self, parent):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(parent, text="Входные параметры")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Тип покрытия
        ttk.Label(input_frame, text="Тип существующего покрытия:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Radiobutton(input_frame, text="Заводское полиэтиленовое покрытие", variable=self.coating_type, value=1).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Radiobutton(input_frame, text="Битумное, битумно-полимерное, полимерное покрытие", variable=self.coating_type, value=2).grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Диаметр
        ttk.Label(input_frame, text="Диаметр (м):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.diameter, width=10).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Длина участка
        ttk.Label(input_frame, text="Длина изолируемого участка (м):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.length, width=10).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Ширина ленты
        ttk.Label(input_frame, text="Ширина ленты ДЕКАН-ВЭ/WB (м):").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(input_frame, textvariable=self.tape_width, values=[0.1, 0.15], width=8, state="readonly").grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # Кнопка расчета
        ttk.Button(input_frame, text="Рассчитать", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Фрейм для результатов
        result_frame = ttk.LabelFrame(parent, text="Результаты расчета")
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Текстовое поле для результатов
        self.result_text = tk.Text(result_frame, height=15, wrap='word')
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=(0, 5), pady=5)
        
        # Кнопки экспорта
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Сохранить в файл", command=self.save_to_file).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить результаты", command=self.clear_results).pack(side='left', padx=5)
        
    def setup_info_tab(self, parent):
        info_text = """
        Калькулятор материалов Декан ВЭ
        
        *Материал Декан-ВЭ изготавливается в рулонах в двух типоразмерах:
        - Материал рулонный вязкоэластичный "Декан-ВЭ" 100х2 
          (ширина рулона 100мм, длина рулона 10м);
        - Материал рулонный вязкоэластичный "Декан-ВЭ" 150х2 
          (ширина рулона 150мм, длина рулона 10м).
        
        ** Лента-обертка изготавливается в рулонах одного типоразмера:
        - Лента-обертка "ДЕКАН-ВЭ Обертка" 100-30 
          (ширина рулона 100мм, длина рулона 30м).
        
        *** Рекомендуемый запас к расчётному количеству 20%
        (нелинейность покрытия, человеческий фактор).
        
        Формулы расчета:
        - Длина окружности = диаметр × 3.14
        - Площадь участка = (длина + нахлест) × длина окружности
        - Количество витков (1 слой) = округление_вверх((длина + нахлест)/(ширина_ленты - 0.01) + 2)
        - Расход ленты (1 слой) = округление_вверх(количество_витков × длина_окружности)
        - Количество витков (2 слой) = округление_вверх((длина + нахлест)/(ширина_ленты_обертки/2) + 3)
        - Расход ленты (2 слой) = округление_вверх(количество_витков × длина_окружности)
        """
        
        text_widget = tk.Text(parent, wrap='word', height=25)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)
        
    def calculate(self):
        try:
            # Получаем значения из переменных
            coating_type = self.coating_type.get()
            diameter = self.diameter.get()
            length = self.length.get()
            tape_width = self.tape_width.get()
            
            # Проверяем корректность введенных данных
            if diameter <= 0 or length <= 0:
                messagebox.showerror("Ошибка", "Диаметр и длина должны быть положительными числами")
                return
                
            # Определяем коэффициент нахлеста
            if coating_type == 1:
                overlap_coef = 0.1 * 2  # нахлёст на существующее покрытие
            else:
                overlap_coef = 0.15 * 2  # нахлёст на существующее покрытие
            
            # Расчет основных параметров
            circumference = diameter * 3.14  # Длина окружности
            area = (length + overlap_coef) * circumference  # Площадь участка
            
            # Расчет для первого слоя ДЕКАН-ВЭ
            turns_1 = math.ceil((length + overlap_coef) / (tape_width - 0.01) + 2)
            consumption_1 = math.ceil(turns_1 * circumference)
            
            # Расчет для второго слоя ДЕКАН-ВЭ Обертка
            tape_width_2 = 0.1  # Фиксированная ширина для обертки
            turns_2 = math.ceil((length + overlap_coef) / (tape_width_2 / 2) + 3)
            consumption_2 = math.ceil(turns_2 * circumference)
            
            # Учет рекомендуемого запаса 20%
            consumption_1_with_margin = math.ceil(consumption_1 * 1.2)
            consumption_2_with_margin = math.ceil(consumption_2 * 1.2)
            
            # Конвертация в рулоны
            if tape_width == 0.1:
                rolls_1 = math.ceil(consumption_1_with_margin / 10)  # Рулоны по 10м
                tape_type = "ДЕКАН-ВЭ 100х2"
            else:
                rolls_1 = math.ceil(consumption_1_with_margin / 10)  # Рулоны по 10м
                tape_type = "ДЕКАН-ВЭ 150х2"
            
            rolls_2 = math.ceil(consumption_2_with_margin / 30)  # Рулоны по 30м
            
            # Формируем результат
            result = f"""РАСЧЕТ МАТЕРИАЛОВ ДЕКАН-ВЭ
Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}
            
Входные параметры:
Тип покрытия: {'Заводское полиэтиленовое' if coating_type == 1 else 'Битумное, битумно-полимерное, полимерное'}
Диаметр: {diameter} м
Длина участка: {length} м
Ширина ленты ДЕКАН-ВЭ/WB: {tape_width} м
            
Основные расчеты:
Длина окружности: {circumference:.2f} м
Площадь участка: {area:.2f} м²
Нахлест: {overlap_coef} м
            
Первый слой ДЕКАН-ВЭ:
Количество витков: {turns_1}
Расход ленты: {consumption_1} м.п.
Расход с учетом запаса 20%: {consumption_1_with_margin} м.п.
Количество рулонов {tape_type}: {rolls_1} шт.
            
Второй слой ДЕКАН-ВЭ Обертка:
Количество витков: {turns_2}
Расход ленты: {consumption_2} м.п.
Расход с учетом запаса 20%: {consumption_2_with_margin} м.п.
Количество рулонов ДЕКАН-ВЭ Обертка 100-30: {rolls_2} шт.
            
Примечание: Рекомендуемый запас к расчётному количеству 20% 
(учитывает нелинейность покрытия и человеческий фактор).
"""
            
            # Выводим результат
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")
        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "Ширина ленты не может быть меньше или равна 0.01 м")
            
    def save_to_file(self):
        try:
            # Получаем текст из поля результатов
            result_text = self.result_text.get(1.0, tk.END)
            if not result_text.strip():
                messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
                return
                
            # Предлагаем выбрать место для сохранения
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
                title="Сохранить результаты расчета"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(result_text)
                messagebox.showinfo("Успех", "Результаты успешно сохранены")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
            
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = DekanCalculator(root)
    root.mainloop()