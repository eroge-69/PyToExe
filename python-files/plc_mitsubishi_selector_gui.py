import tkinter as tk
from tkinter import ttk, messagebox

# Справочник оборудования и ПЛК (остаётся без изменений)
equipment_types = {
    "Датчик температуры": (1, 0),
    "Пневмоцилиндр": (1, 2),
    "Частотный преобразователь": (2, 1),
    "Сенсорный датчик": (1, 0),
    "Реле": (0, 1),
    "Конвейерная лента": (2, 3),
}

plc_models = {
    "FX3U-16MR/ES": (8, 8),
    "FX3U-32MR/ES": (16, 16),
    "FX5U-32MT/ES": (16, 16),
    "FX5U-64MT/ES": (32, 32),
    "FX5U-128MT/ES": (64, 64),
}

class PLCSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Подбор ПЛК Mitsubishi")
        self.root.geometry("500x500")
        
        # Переменные
        self.equipment_list = []
        
        # Создание виджетов
        self.create_widgets()
    
    def create_widgets(self):
        # Комбобокс для выбора оборудования
        self.label_eq = ttk.Label(self.root, text="Выберите тип оборудования:")
        self.label_eq.pack(pady=5)
        
        self.eq_combobox = ttk.Combobox(self.root, values=list(equipment_types.keys()))
        self.eq_combobox.pack(pady=5)
        
        # Поле для количества
        self.label_count = ttk.Label(self.root, text="Количество:")
        self.label_count.pack(pady=5)
        
        self.count_entry = ttk.Entry(self.root)
        self.count_entry.pack(pady=5)
        
        # Кнопка "Добавить"
        self.add_button = ttk.Button(self.root, text="Добавить оборудование", command=self.add_equipment)
        self.add_button.pack(pady=10)
        
        # Листбокс для отображения добавленного оборудования
        self.listbox_label = ttk.Label(self.root, text="Добавленное оборудование:")
        self.listbox_label.pack(pady=5)
        
        self.equipment_listbox = tk.Listbox(self.root, height=8)
        self.equipment_listbox.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Кнопка "Рассчитать"
        self.calculate_button = ttk.Button(self.root, text="Подобрать ПЛК", command=self.calculate_plc)
        self.calculate_button.pack(pady=10)
        
        # Поле для вывода результатов
        self.result_label = ttk.Label(self.root, text="Результаты:")
        self.result_label.pack(pady=5)
        
        self.result_text = tk.Text(self.root, height=8, state="disabled")
        self.result_text.pack(pady=5, fill=tk.BOTH, expand=True)
    
    def add_equipment(self):
        eq_type = self.eq_combobox.get()
        count = self.count_entry.get()
        
        if not eq_type or not count:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        try:
            count = int(count)
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть числом!")
            return
        
        self.equipment_list.append((eq_type, count))
        self.equipment_listbox.insert(tk.END, f"{eq_type} x{count}")
        
        # Очистка полей
        self.count_entry.delete(0, tk.END)
    
    def calculate_plc(self):
        if not self.equipment_list:
            messagebox.showerror("Ошибка", "Не добавлено оборудование!")
            return
        
        # Считаем входы/выходы
        total_inputs = 0
        total_outputs = 0
        
        for item in self.equipment_list:
            eq_type, count = item
            inputs, outputs = equipment_types.get(eq_type, (0, 0))
            total_inputs += inputs * count
            total_outputs += outputs * count
        
        # Запас 10%
        total_inputs = int(total_inputs * 1.1)
        total_outputs = int(total_outputs * 1.1)
        
        # Подбор ПЛК
        suggestion = []
        for model, (max_inputs, max_outputs) in plc_models.items():
            if max_inputs >= total_inputs and max_outputs >= total_outputs:
                suggestion.append(model)
        
        # Вывод результатов
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, f"Общие входы (с запасом 10%): {total_inputs}\n")
        self.result_text.insert(tk.END, f"Общие выходы (с запасом 10%): {total_outputs}\n\n")
        
        if suggestion:
            self.result_text.insert(tk.END, "Подходящие ПЛК:\n")
            for plc in suggestion:
                self.result_text.insert(tk.END, f"- {plc}\n")
        else:
            self.result_text.insert(tk.END, "Нет подходящего ПЛК в базе 🚫\nРассмотрите каскадную схему.")
        
        self.result_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = PLCSelectorApp(root)
    root.mainloop()
