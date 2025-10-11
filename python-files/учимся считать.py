import tkinter as tk
from tkinter import ttk, messagebox
import random

class MathExamplesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор математических примеров")
        self.root.geometry("800x600")
        
        # Создаем набор вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        # Словарь для хранения примеров и ответов
        self.examples = {
            'Сложение': [],
            'Вычитание': [],
            'Умножение': [],
            'Деление': []
        }
        
        self.entries = {}
        self.generate_examples()
        self.create_tabs()
        
    def generate_examples(self):
        # Генерация примеров на сложение
        for _ in range(50):
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            answer = a + b
            self.examples['Сложение'].append((f"{a} + {b} =", answer))
        
        # Генерация примеров на вычитание (результат положительный)
        for _ in range(50):
            a = random.randint(10, 99)
            b = random.randint(10, a)
            answer = a - b
            self.examples['Вычитание'].append((f"{a} - {b} =", answer))
        
        # Генерация примеров на умножение
        for _ in range(50):
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            answer = a * b
            self.examples['Умножение'].append((f"{a} × {b} =", answer))
        
        # Генерация примеров на деление (результат целый)
        for _ in range(50):
            b = random.randint(10, 99)
            answer = random.randint(10, 99)
            a = b * answer
            if a > 999:  # Ограничим максимальное значение
                a = b * random.randint(1, 9)
                answer = a // b
            self.examples['Деление'].append((f"{a} ÷ {b} =", answer))

    def create_tabs(self):
        for operation in self.examples.keys():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=operation)
            self.create_tab_content(frame, operation)

    def create_tab_content(self, parent, operation):
        # Создаем фрейм с прокруткой
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создаем примеры
        self.entries[operation] = []
        for i, (example, answer) in enumerate(self.examples[operation]):
            row = i % 25
            col = i // 25
            
            label = ttk.Label(scrollable_frame, text=example, font=('Arial', 12))
            label.grid(row=row, column=col*3, padx=10, pady=5, sticky='e')
            
            entry = ttk.Entry(scrollable_frame, width=10, font=('Arial', 12))
            entry.grid(row=row, column=col*3+1, padx=5, pady=5)
            entry.answer = answer  # Сохраняем правильный ответ в виджете
            
            self.entries[operation].append(entry)
            
            # Добавляем метку для результата проверки
            result_label = ttk.Label(scrollable_frame, text="", width=3)
            result_label.grid(row=row, column=col*3+2, padx=5)
            entry.result_label = result_label

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка проверки для текущей вкладки
        check_btn = ttk.Button(parent, text="Проверить ответы",
                              command=lambda: self.check_answers(operation))
        check_btn.pack(pady=10)

    def check_answers(self, operation):
        correct = 0
        total = len(self.entries[operation])
        
        for entry in self.entries[operation]:
            try:
                user_answer = int(entry.get())
                if user_answer == entry.answer:
                    entry.result_label.config(text="✓", foreground="green")
                    correct += 1
                else:
                    entry.result_label.config(text="✗", foreground="red")
            except ValueError:
                entry.result_label.config(text="✗", foreground="red")
        
        messagebox.showinfo("Результат", 
                          f"Правильно решено: {correct} из {total}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MathExamplesApp(root)
    root.mainloop()