import tkinter as tk
from tkinter import ttk, messagebox
from itertools import product

class BeamCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор стеллажных балок")
        self.root.geometry("900x650")
        
        # Данные о профилях рам
        self.profiles = {
            "П70х1,5": 70,
            "П90х1,5": 90, 
            "П110х2": 110
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header = ttk.Label(main_frame, text="РАСЧЕТ КОМБИНАЦИЙ СТЕЛЛАЖНЫХ БАЛОК", 
                          font=('Arial', 12, 'bold'))
        header.pack(pady=10)
        
        # Выбор профиля рамы
        profile_frame = ttk.Frame(main_frame)
        profile_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(profile_frame, text="Профиль рамы:").pack(side=tk.LEFT)
        self.profile_var = tk.StringVar(value="П70х1,5")
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var, 
                                    values=list(self.profiles.keys()), width=15, state="readonly")
        profile_combo.pack(side=tk.LEFT, padx=5)
        
        # Ввод длины стены
        length_frame = ttk.Frame(main_frame)
        length_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(length_frame, text="Длина стены (мм):").pack(side=tk.LEFT)
        self.wall_length_var = tk.StringVar()
        length_entry = ttk.Entry(length_frame, textvariable=self.wall_length_var, width=15)
        length_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(length_frame, text="(0 для выхода)").pack(side=tk.LEFT, padx=5)
        
        # Выбор балок
        beams_frame = ttk.LabelFrame(main_frame, text="Доступные балки", padding=10)
        beams_frame.pack(pady=10, fill=tk.X)
        
        self.beam_vars = {}
        standard_beams = [1800, 2250, 2700, 3300]
        
        beams_inner_frame = ttk.Frame(beams_frame)
        beams_inner_frame.pack()
        
        for i, beam in enumerate(standard_beams):
            self.beam_vars[beam] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(beams_inner_frame, text=f"{beam} мм", 
                                variable=self.beam_vars[beam])
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Рассчитать", 
                  command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", 
                  command=self.clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Область результатов
        results_frame = ttk.LabelFrame(main_frame, text="Результаты", padding=10)
        results_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Таблица результатов (без столбца "Сумма балок")
        columns = ("№", "Комбинация", "Габарит", "Зазор", "Секций", "Заполнение")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
        
        # Настройка столбцов
        column_widths = {"№": 40, "Комбинация": 180, "Габарит": 100, 
                        "Зазор": 80, "Секций": 70, "Заполнение": 80}
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
        
        # Scrollbar для таблицы
        tree_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                   command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Привязка события выбора в таблице
        self.results_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
    def calculate_total_dimension(self, beams_combo, profile_width):
        """
        Рассчитывает общий габарит стеллажа с учетом рам
        Формула: (количество_рам * ширина_рамы) + сумма_балок
        Количество рам = количество секций + 1
        """
        num_sections = len(beams_combo)
        total_beams_length = sum(beams_combo)
        total_frames_width = (num_sections + 1) * profile_width
        return total_beams_length + total_frames_width
    
    def find_all_combinations(self, wall_length, beams, profile_width):
        """
        Находит все комбинации балок и сортирует их по зазору
        """
        if not beams:
            return []
            
        beams.sort(reverse=True)
        all_combinations = []
        
        # Ограничиваем максимальное количество балок для производительности
        min_beam = min(beams)
        max_beams = min(12, wall_length // min_beam + 2) if min_beam > 0 else 12
        
        for num_beams in range(1, max_beams + 1):
            for combo in product(beams, repeat=num_beams):
                total_dimension = self.calculate_total_dimension(combo, profile_width)
                if total_dimension <= wall_length:
                    gap = wall_length - total_dimension
                    all_combinations.append((list(combo), total_dimension, gap))
        
        # Сортируем по зазору (от меньшего к большему)
        all_combinations.sort(key=lambda x: x[2])
        
        return all_combinations
    
    def get_unique_combinations(self, combinations):
        """
        Убирает дубликаты комбинаций
        """
        unique_combinations = []
        seen = set()
        
        for combo, total_dim, gap in combinations:
            combo_tuple = tuple(sorted(combo))
            if combo_tuple not in seen:
                seen.add(combo_tuple)
                unique_combinations.append((combo, total_dim, gap))
        
        return unique_combinations
    
    def calculate(self):
        try:
            wall_length = int(self.wall_length_var.get())
            if wall_length == 0:
                self.root.quit()
                return
            if wall_length <= 0:
                messagebox.showerror("Ошибка", "Длина стены должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите целое число для длины стены!")
            return
        
        # Получаем выбранный профиль
        selected_profile = self.profile_var.get()
        profile_width = self.profiles[selected_profile]
        
        # Получаем выбранные балки
        available_beams = []
        for beam, var in self.beam_vars.items():
            if var.get():
                available_beams.append(beam)
        
        if not available_beams:
            messagebox.showerror("Ошибка", "Не выбрано ни одной балки!")
            return
        
        self.status_var.set("Выполняется расчет...")
        self.root.update()
        
        try:
            all_combinations = self.find_all_combinations(wall_length, available_beams, profile_width)
            unique_combinations = self.get_unique_combinations(all_combinations)
            
            if not unique_combinations:
                messagebox.showinfo("Результат", "Не найдено ни одной подходящей комбинации балок.")
                self.status_var.set("Готов к работе")
                return
            
            # Очищаем таблицу
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Заполняем таблицу (ограничиваем 50 комбинациями)
            min_gap = unique_combinations[0][2]
            for i, (combo, total_dim, gap) in enumerate(unique_combinations[:50]):
                utilization = (total_dim / wall_length) * 100
                combo_str = " + ".join(f"{beam}" for beam in combo)
                
                is_best = "★" if gap == min_gap else ""
                
                self.results_tree.insert("", "end", values=(
                    f"{i+1}{is_best}", 
                    combo_str, 
                    f"{total_dim} мм", 
                    f"{gap} мм", 
                    len(combo), 
                    f"{utilization:.1f}%"
                ))
            
            self.status_var.set(f"Найдено {len(unique_combinations)} комбинаций. Лучший зазор: {min_gap} мм")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при расчете: {e}")
            self.status_var.set("Ошибка расчета")
    
    def on_tree_select(self, event):
        selected_item = self.results_tree.selection()
        if not selected_item:
            return
        
        item = self.results_tree.item(selected_item[0])
        values = item['values']
        
        # Получаем ширину профиля для детального расчета
        profile_width = self.profiles[self.profile_var.get()]
        
        # Формируем детальную информацию
        detail_info = f"Профиль рамы: {self.profile_var.get()} ({profile_width}мм)\n"
        detail_info += f"Комбинация балок: {values[1]}\n"
        detail_info += f"Общий габарит: {values[2]}\n"
        detail_info += f"Зазор: {values[3]}\n"
        detail_info += f"Количество секций: {values[4]}\n"
        detail_info += f"Заполнение: {values[5]}\n\n"
        
        # Показываем расчет рам
        num_sections = int(values[4])
        num_frames = num_sections + 1
        total_frames_width = num_frames * profile_width
        
        # Рассчитываем сумму балок для детального отображения
        combo_beams = [int(beam) for beam in values[1].split(" + ")]
        total_beams = sum(combo_beams)
        
        detail_info += f"Состав: {num_frames} рам + {num_sections} балок\n"
        detail_info += f"Рамы: {num_frames} × {profile_width}мм = {total_frames_width}мм\n"
        detail_info += f"Балки: {values[1]} = {total_beams}мм\n"
        detail_info += f"Итого: {total_frames_width}мм + {total_beams}мм = {values[2]}"
        
        # Показываем информацию в всплывающем окне
        messagebox.showinfo("Детали комбинации", detail_info)
    
    def clear(self):
        self.wall_length_var.set("")
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.status_var.set("Готов к работе")

def main():
    root = tk.Tk()
    app = BeamCalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()