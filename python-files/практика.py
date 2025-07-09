import tkinter as tk
from tkinter import font as tkfont
from math import sqrt

def f(x):
    return 1 / sqrt(x**3 + 2)

class IntegralCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Интегральный калькулятор")
        self.root.geometry("500x600")
        # Устанавливаем минимальный и максимальный размер окна равным текущему размеру
        self.root.minsize(500, 600)
        self.root.maxsize(500, 600)
        self.root.configure(bg="black")
        
        # Переменные для анимации
        self.animation_in_progress = False
        self.error_message_visible = False
        self.original_positions = {}
        
        # Шрифты
        self.large_font = tkfont.Font(family="Helvetica", size=24)
        self.medium_font = tkfont.Font(family="Helvetica", size=14)
        self.small_font = tkfont.Font(family="Helvetica", size=12)
        
        # Создание элементов интерфейса
        self.create_widgets()
        
        # Привязка событий
        self.entry_a.bind("<FocusIn>", lambda e: self.check_errors(e, self.entry_a))
        self.entry_b.bind("<FocusIn>", lambda e: self.check_errors(e, self.entry_b))
        self.entry_n.bind("<FocusIn>", lambda e: self.check_errors(e, self.entry_n))
        self.entry_a.bind("<KeyRelease>", self.on_entry_change)
        self.entry_b.bind("<KeyRelease>", self.on_entry_change)
        self.entry_n.bind("<KeyRelease>", self.on_entry_change)
    
    def create_widgets(self):
        # Фрейм для формулы
        self.formula_frame = tk.Frame(self.root, bg="black")
        self.formula_frame.pack(pady=20)
        
        # Отображение формулы
        self.formula_label = tk.Label(
            self.formula_frame, 
            text="∫(a→b) 1/√(x³ + 2) dx ≈", 
            font=self.large_font, 
            bg="black", 
            fg="white"
        )
        self.formula_label.pack(side=tk.LEFT)
        
        self.result_label = tk.Label(
            self.formula_frame, 
            text="", 
            font=self.large_font, 
            bg="black", 
            fg="white"
        )
        self.result_label.pack(side=tk.LEFT, padx=10)
        
        # Фрейм для ввода параметров
        self.input_frame = tk.Frame(self.root, bg="black")
        self.input_frame.pack(pady=20)
        
        # Поле для a
        self.label_a = tk.Label(
            self.input_frame, 
            text="Нижний предел (a):", 
            font=self.medium_font, 
            bg="black", 
            fg="white"
        )
        self.label_a.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        
        self.entry_a = tk.Entry(
            self.input_frame, 
            font=self.medium_font, 
            borderwidth=0,
            relief=tk.FLAT,
            justify=tk.RIGHT,
            bg="#333333",
            fg="white",
            insertbackground="white",
            highlightthickness=2,
            highlightbackground="#555555",
            highlightcolor="#777777",
            width=15
        )
        self.entry_a.grid(row=0, column=1, padx=10, pady=5)
        
        # Поле для b
        self.label_b = tk.Label(
            self.input_frame, 
            text="Верхний предел (b):", 
            font=self.medium_font, 
            bg="black", 
            fg="white"
        )
        self.label_b.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        
        self.entry_b = tk.Entry(
            self.input_frame, 
            font=self.medium_font, 
            borderwidth=0,
            relief=tk.FLAT,
            justify=tk.RIGHT,
            bg="#333333",
            fg="white",
            insertbackground="white",
            highlightthickness=2,
            highlightbackground="#555555",
            highlightcolor="#777777",
            width=15
        )
        self.entry_b.grid(row=1, column=1, padx=10, pady=5)
        
        # Поле для n
        self.label_n = tk.Label(
            self.input_frame, 
            text="Число узлов (n):", 
            font=self.medium_font, 
            bg="black", 
            fg="white"
        )
        self.label_n.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        
        self.entry_n = tk.Entry(
            self.input_frame, 
            font=self.medium_font, 
            borderwidth=0,
            relief=tk.FLAT,
            justify=tk.RIGHT,
            bg="#333333",
            fg="white",
            insertbackground="white",
            highlightthickness=2,
            highlightbackground="#555555",
            highlightcolor="#777777",
            width=15
        )
        self.entry_n.grid(row=2, column=1, padx=10, pady=5)
        
        # Сообщение об ошибке
        self.error_label = tk.Label(
            self.input_frame, 
            text="", 
            font=self.small_font, 
            bg="black", 
            fg="#FFA500"
        )
        self.error_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Информация о точности
        self.info_label = tk.Label(
            self.root, 
            text="Точность вычислений: 0.0001", 
            font=self.small_font, 
            bg="black", 
            fg="#777777"
        )
        self.info_label.pack(pady=10)
        
        # Сохраняем оригинальные позиции элементов
        self.save_original_positions()
    
    def save_original_positions(self):
        self.original_positions = {
            'label_a': self.label_a.grid_info(),
            'entry_a': self.entry_a.grid_info(),
            'label_b': self.label_b.grid_info(),
            'entry_b': self.entry_b.grid_info(),
            'label_n': self.label_n.grid_info(),
            'entry_n': self.entry_n.grid_info(),
            'error_label': self.error_label.grid_info()
        }
    
    def calculate_integral(self):
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            n = int(self.entry_n.get())
            
            if a >= b:
                self.show_error("Ошибка: a должно быть меньше b")
                return
                
            if n <= 0:
                self.show_error("Ошибка: n должно быть > 0")
                return
                
            # Вычисление интеграла методом трапеций
            h = (b - a) / n
            total = 0.5 * (f(a) + f(b))
            
            for i in range(1, n):
                total += f(a + i * h)
                
            integral = h * total
            self.formula_label.config(text="∫(a→b) 1/√(x³ + 2) dx ≈")
            self.result_label.config(text=f"{integral:.6f}")
            self.error_label.config(text="")
            self.error_message_visible = False
        except ValueError:
            pass
    
    def on_entry_change(self, event):
        if not self.animation_in_progress:
            if self.entry_a.get() and self.entry_b.get() and self.entry_n.get():
                self.calculate_integral()
            else:
                self.result_label.config(text="")
    
    def check_errors(self, event, entry_widget):
        if self.animation_in_progress:
            return
            
        has_error = False
        error_message = ""
        
        try:
            if entry_widget == self.entry_a or entry_widget == self.entry_b:
                float(entry_widget.get())
            elif entry_widget == self.entry_n:
                int(entry_widget.get())
        except ValueError:
            if entry_widget.get():  # Только если поле не пустое
                has_error = True
                error_message = "Введено некорректное значение"
        
        if has_error and not self.error_message_visible:
            self.error_label.config(text=error_message)
            self.animate_down()
            self.error_message_visible = True
        elif not has_error and self.error_message_visible:
            self.animate_up()
            self.error_message_visible = False
    
    def animate_down(self):
        if self.animation_in_progress:
            return
            
        self.animation_in_progress = True
        
        # Перемещаем элементы вниз
        for i in range(1, 11):
            if not self.animation_in_progress:
                break
                
            new_pady = i
            self.label_b.grid_configure(pady=(5 + new_pady, 5))
            self.entry_b.grid_configure(pady=(5 + new_pady, 5))
            self.label_n.grid_configure(pady=(5 + new_pady, 5))
            self.entry_n.grid_configure(pady=(5 + new_pady, 5))
            self.error_label.grid_configure(pady=(new_pady, 5))
            
            self.root.update()
            self.root.after(10)
        
        self.animation_in_progress = False
    
    def animate_up(self):
        if self.animation_in_progress:
            return
            
        self.animation_in_progress = True
        
        # Возвращаем элементы на исходные позиции
        for i in range(10, -1, -1):
            if not self.animation_in_progress:
                break
                
            new_pady = i
            self.label_b.grid_configure(pady=(5 + new_pady, 5))
            self.entry_b.grid_configure(pady=(5 + new_pady, 5))
            self.label_n.grid_configure(pady=(5 + new_pady, 5))
            self.entry_n.grid_configure(pady=(5 + new_pady, 5))
            self.error_label.grid_configure(pady=(new_pady, 5))
            
            self.root.update()
            self.root.after(10)
        
        self.error_label.config(text="")
        self.animation_in_progress = False
    
    def show_error(self, message):
        self.formula_label.config(text="∫(a→b) 1/√(x³ + 2) dx =")
        self.result_label.config(text="")
        self.error_label.config(text=message)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = IntegralCalculator(root)
    root.mainloop()