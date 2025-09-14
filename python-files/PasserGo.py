import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
import random
import time

class ArrayInputApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система контроля доступа")
        self.root.geometry("1200x900")
        
        # Исходная матрица MaxX 10×10
        self.MaxX = np.array([
            [1, 0.3, 0.1, -0.2, -0.6, -0.8, -1, -1.2, -1.5, -2],
            [0.3, 1, 0.3, 0.1, -0.2, -0.6, -0.8, -1, -1.2, -1.5],
            [0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6, -0.8, -1, -1.2],
            [-0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6, -0.8, -1],
            [-0.6, -0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6, 0],
            [-0.8, -0.6, -0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6],
            [-1, -0.8, -0.6,-0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2],
            [-1.2, -1, -0.8, -0.6,-0.2, 0.1, 0.3, 1, 0.3, 0.1],
            [-1.5, -1.2, -1, -0.8, -0.6, -0.2, 0.1, 0.3, 1, 0.3],
            [-2, -1.5, -1.2, -1, -0.8, -0.6, -0.2, 0.1, 0.3, 1]
        ], dtype=float)
        
        # Матрица MaxW 10×10 (входная матрица)
        self.MaxW = np.zeros((10, 10), dtype=int)
        
        # Матрица MaxY 10×10 (результат поэлементного умножения)
        self.MaxY = np.zeros((10, 10), dtype=float)
        
        self.MinPass = 10
        self.MaxPass = 13
        self.ctrMax = 0
        self.is_searching = False
        self.edit_mode = "maxw"  # Режим редактирования: "maxw" или "maxx"
        
        self.create_widgets()
    
    def create_widgets(self):
        # Заголовок
        title_label = ttk.Label(self.root, text="Система контроля доступа", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Фрейм для выбора режима редактирования
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(pady=10)
        
        self.mode_var = tk.StringVar(value="maxw")
        
        ttk.Radiobutton(mode_frame, text="Редактировать MaxW (0/1)", 
                       variable=self.mode_var, value="maxw", 
                       command=self.switch_edit_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Редактировать MaxX (Веса)", 
                       variable=self.mode_var, value="maxx", 
                       command=self.switch_edit_mode).pack(side=tk.LEFT, padx=10)
        
        # Фрейм для матриц
        matrices_frame = ttk.Frame(self.root)
        matrices_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Левая панель - матрица MaxW
        self.maxw_frame = ttk.LabelFrame(matrices_frame, text="Матрица MaxW [10×10]")
        self.maxw_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.maxw_grid = ttk.Frame(self.maxw_frame)
        self.maxw_grid.pack(pady=10, padx=10)
        
        self.maxw_cells = []
        for i in range(10):
            row = []
            for j in range(10):
                cell = tk.Button(self.maxw_grid, text="0", width=4, height=1,
                               command=lambda i=i, j=j: self.toggle_maxw_cell(i, j),
                               font=("Arial", 8))
                cell.grid(row=i, column=j, padx=1, pady=1)
                row.append(cell)
            self.maxw_cells.append(row)
        
        # Правая панель - матрица MaxX
        self.maxx_frame = ttk.LabelFrame(matrices_frame, text="Матрица MaxX [10×10]")
        self.maxx_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.maxx_grid = ttk.Frame(self.maxx_frame)
        self.maxx_grid.pack(pady=10, padx=10)
        
        self.maxx_entries = []
        self.maxx_vars = []
        for i in range(10):
            row_vars = []
            row_entries = []
            for j in range(10):
                var = tk.StringVar(value=str(self.MaxX[i, j]))
                entry = tk.Entry(self.maxx_grid, textvariable=var, width=6, 
                               font=("Arial", 8), justify='center')
                entry.grid(row=i, column=j, padx=1, pady=1)
                entry.bind('<Return>', lambda e, i=i, j=j: self.update_maxx_value(i, j))
                entry.bind('<FocusOut>', lambda e, i=i, j=j: self.update_maxx_value(i, j))
                row_vars.append(var)
                row_entries.append(entry)
            self.maxx_vars.append(row_vars)
            self.maxx_entries.append(row_entries)
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Проверить", 
                  command=self.check_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Автоподбор (100Mлн попыток)", 
                  command=self.auto_find_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Остановить поиск", 
                  command=self.stop_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить MaxW", 
                  command=self.clear_maxw).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Случайная MaxW", 
                  command=self.generate_random_maxw).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сбросить MaxX", 
                  command=self.reset_maxx).pack(side=tk.LEFT, padx=5)
        
        # Прогресс бар
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Готов к работе")
        self.progress_label.pack()
        
        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate', maximum=100000000)
        self.progress.pack(fill=tk.X, pady=5)
        
        self.stats_label = ttk.Label(self.progress_frame, text="Попыток: 0 | Найдено: 0 | Лучшее: -")
        self.stats_label.pack()
        
        # Поле для вывода результата
        result_frame = ttk.LabelFrame(self.root, text="Результаты")
        result_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(result_frame, height=12, width=100, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Изначально активируем режим редактирования MaxW
        self.switch_edit_mode()
    
    def switch_edit_mode(self):
        """Переключение между режимами редактирования"""
        self.edit_mode = self.mode_var.get()
        if self.edit_mode == "maxw":
            self.status_var.set("Режим редактирования: MaxW (кликайте для изменения 0/1)")
        else:
            self.status_var.set("Режим редактирования: MaxX (вводите числа в поля)")
    
    def toggle_maxw_cell(self, i, j):
        """Переключение ячейки матрицы MaxW"""
        if not self.is_searching and self.edit_mode == "maxw":
            self.MaxW[i, j] = 1 - self.MaxW[i, j]
            self.maxw_cells[i][j].config(text=str(self.MaxW[i, j]), 
                                       bg="lightgreen" if self.MaxW[i, j] == 1 else "SystemButtonFace")
    
    def update_maxx_value(self, i, j):
        """Обновление значения матрицы MaxX из поля ввода"""
        if not self.is_searching and self.edit_mode == "maxx":
            try:
                value = float(self.maxx_vars[i][j].get())
                self.MaxX[i, j] = value
                # Подтверждаем успешный ввод
                self.maxx_entries[i][j].config(bg="white")
            except ValueError:
                # Неверный ввод - восстанавливаем предыдущее значение
                self.maxx_vars[i][j].set(str(self.MaxX[i, j]))
                self.maxx_entries[i][j].config(bg="lightcoral")
                self.status_var.set("Ошибка: введите корректное число")
    
    def generate_random_maxw(self):
        """Генерация случайной матрицы MaxW 10×10"""
        if not self.is_searching:
            self.MaxW = np.random.randint(0, 1, (10, 10))
            self.update_maxw_display()
            self.status_var.set("Сгенерирована случайная матрица MaxW")
    
    def clear_maxw(self):
        """Очистка матрицы MaxW"""
        if not self.is_searching:
            self.MaxW = np.zeros((10, 10), dtype=int)
            self.update_maxw_display()
            self.status_var.set("Матрица MaxW очищена")
    
    def reset_maxx(self):
        """Сброс матрицы MaxX к исходным значениям"""
        if not self.is_searching:
            self.MaxX = np.array([
            [1, 0.3, 0.1, -0.2, -0.6, -0.8, -1, -1.2, -1.5, -2],
            [0.3, 1, 0.3, 0.1, -0.2, -0.6, -0.8, -1, -1.2, -1.5],
            [0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6, -0.8, -1, -1.2],
            [-0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6, -0.8, -1],
            [-0.6, -0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6, 0],
            [-0.8, -0.6, -0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2, -0.6],
            [-1, -0.8, -0.6,-0.2, 0.1, 0.3, 1, 0.3, 0.1, -0.2],
            [-1.2, -1, -0.8, -0.6,-0.2, 0.1, 0.3, 1, 0.3, 0.1],
            [-1.5, -1.2, -1, -0.8, -0.6, -0.2, 0.1, 0.3, 1, 0.3],
            [-2, -1.5, -1.2, -1, -0.8, -0.6, -0.2, 0.1, 0.3, 1]
            ], dtype=float)
            self.update_maxx_display()
            self.status_var.set("Матрица MaxX сброшена к исходным значениям")
    
    def update_maxw_display(self):
        """Обновление отображения матрицы MaxW"""
        for i in range(10):
            for j in range(10):
                self.maxw_cells[i][j].config(text=str(self.MaxW[i, j]), 
                                           bg="lightgreen" if self.MaxW[i, j] == 1 else "SystemButtonFace")
    
    def update_maxx_display(self):
        """Обновление отображения матрицы MaxX"""
        for i in range(10):
            for j in range(10):
                self.maxx_vars[i][j].set(str(self.MaxX[i, j]))
                self.maxx_entries[i][j].config(bg="white")
    
    def check_matrix(self):
        """Проверка матрицы"""
        if self.is_searching:
            return
        
        # Обновляем MaxX из полей ввода
        if self.edit_mode == "maxx":
            for i in range(10):
                for j in range(10):
                    try:
                        self.MaxX[i, j] = float(self.maxx_vars[i][j].get())
                    except ValueError:
                        pass
        
        # Поэлементное умножение
        self.MaxY = self.MaxW * self.MaxX
        MaxKey = np.sum(self.MaxY)
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "=== РЕЗУЛЬТАТ ПРОВЕРКИ ===\n")
        self.result_text.insert(tk.END, f"Сумма элементов: {MaxKey:.6f}\n")
        self.result_text.insert(tk.END, f"Целевой диапазон: {self.MinPass} ≤ сумма < {self.MaxPass}\n\n")
        
        if self.MinPass <= MaxKey < self.MaxPass:
            distance_to_10 = abs(MaxKey - 10)
            self.result_text.insert(tk.END, f"✅ ДОСТУП РАЗРЕШЕН! (расстояние до 10: {distance_to_10:.6f})\n")
            messagebox.showinfo("Успех", f"Доступ разрешен!\nСумма: {MaxKey:.6f}")
        elif MaxKey < self.MinPass:
            self.result_text.insert(tk.END, "❌ ДОСТУП ЗАПРЕЩЕН! Сумма слишком мала\n")
            messagebox.showwarning("Отказ", f"Сумма: {MaxKey:.6f} (меньше {self.MinPass})")
        else:
            self.result_text.insert(tk.END, "❌ ДОСТУП ЗАПРЕЩЕН! Сумма слишком велика\n")
            messagebox.showwarning("Отказ", f"Сумма: {MaxKey:.6f} (больше или равно {self.MaxPass})")
    
    def stop_search(self):
        """Остановка поиска"""
        self.is_searching = False
        self.status_var.set("Поиск остановлен пользователем")
    
    def auto_find_matrix(self):
        """Автоматический поиск подходящей матрицы"""
        if self.is_searching:
            return
            
        # Обновляем MaxX из полей ввода перед поиском
        if self.edit_mode == "maxx":
            for i in range(10):
                for j in range(10):
                    try:
                        self.MaxX[i, j] = float(self.maxx_vars[i][j].get())
                    except ValueError:
                        pass
        
        self.is_searching = True
        self.ctrMax = 0
        found_count = 0
        max_attempts = 100000000
        best_key = -float('inf')
        best_matrix = None
        best_distance = float('inf')
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "=== АВТОПОДБОР МАТРИЦЫ ===\n")
        self.result_text.insert(tk.END, "Поиск начат...\n\n")
        self.root.update()
        
        start_time = time.time()
        
        for attempt in range(max_attempts):
            if not self.is_searching:
                break
                
            current_matrix = np.random.randint(0, 2, (10, 10))
            result_matrix = current_matrix * self.MaxX
            total_sum = np.sum(result_matrix)
            distance_to_10 = abs(total_sum - 10)
            
            self.ctrMax += 1
            
            if self.MinPass <= total_sum < self.MaxPass:
                if distance_to_10 < best_distance:
                    best_key = total_sum
                    best_matrix = current_matrix.copy()
                    best_distance = distance_to_10
                    found_count += 1
                    
                    self.MaxW = current_matrix.copy()
                    self.MaxY = result_matrix.copy()
                    
                    self.result_text.insert(tk.END, f"✅ Найдена матрица! Попытка: {self.ctrMax:,}\n")
                    self.result_text.insert(tk.END, f"Сумма: {total_sum:.6f} | Δ: {distance_to_10:.6f}\n")
                    self.result_text.see(tk.END)
                    
                    self.update_maxw_display()
                    self.root.update()
            
            elif total_sum >= self.MinPass and distance_to_10 < best_distance:
                best_key = total_sum
                best_matrix = current_matrix.copy()
                best_distance = distance_to_10
            
            if attempt % 1000 == 0:
                self.progress['value'] = attempt
                status_text = f"Попыток: {attempt:,} | Найдено: {found_count}"
                if best_key != -float('inf'):
                    status_text += f" | Лучшее: {best_key:.6f}"
                self.stats_label.config(text=status_text)
                self.status_var.set(f"Поиск... {attempt:,}/{max_attempts:,}")
                self.root.update()
        
        elapsed_time = time.time() - start_time
        self.is_searching = False
        
        self.result_text.insert(tk.END, f"\n{'='*50}\n")
        self.result_text.insert(tk.END, f"ПОИСК ЗАВЕРШЕН\n")
        self.result_text.insert(tk.END, f"Попыток: {self.ctrMax:,} | Найдено: {found_count}\n")
        self.result_text.insert(tk.END, f"Время: {elapsed_time:.2f} сек\n")
        
        if found_count > 0:
            self.result_text.insert(tk.END, f"Лучшая сумма: {best_key:.6f}\n")
            messagebox.showinfo("Завершено", f"Найдено {found_count} матриц!\nЛучшая сумма: {best_key:.6f}")
        else:
            self.result_text.insert(tk.END, "Подходящие матрицы не найдены\n")
            messagebox.showinfo("Завершено", "Матрицы в целевом диапазоне не найдены")
        
        self.status_var.set(f"Поиск завершен. Найдено: {found_count}")

def main():
    root = tk.Tk()
    app = ArrayInputApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
