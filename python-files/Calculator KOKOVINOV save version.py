import tkinter as tk
from tkinter import messagebox, filedialog

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор с сохранением истории")
        self.root.geometry("400x800")
        
        # Переменные
        self.current_input = ""
        self.full_operation = ""
        self.history = []
        self.operation = None
        self.previous_value = 0
        self.memory = 0
        self.memory_active = False
        
        # Создание интерфейса
        self.create_display()
        self.create_memory_indicator()
        self.create_buttons()
        self.create_history_display()
    
    def create_display(self):
        # Основное табло (5 строк с переносами)
        self.display = tk.Text(self.root, font=('Arial', 20), bd=10, 
                             width=24, height=5, borderwidth=4, 
                             bg='#e6ffe6', wrap=tk.WORD)
        self.display.grid(row=0, column=0, columnspan=4, pady=5, sticky='nsew')
        self.display.insert('1.0', "0")
        self.display.config(state='disabled')
    
    def create_memory_indicator(self):
        # Индикатор памяти
        self.memory_label = tk.Label(self.root, text="", font=('Arial', 12),
                                    fg='blue')
        self.memory_label.grid(row=1, column=0, columnspan=4, sticky='w', padx=15)
    
    def update_memory_indicator(self):
        # Обновление индикатора памяти
        text = "M: " + str(self.memory) if self.memory_active else ""
        self.memory_label.config(text=text)
    
    def create_history_display(self):
        # Табло истории с прокруткой
        self.history_label = tk.Label(self.root, text="История операций:", font=('Arial', 12), anchor='w')
        self.history_label.grid(row=2, column=0, columnspan=4, sticky='w', padx=10)
        
        # Фрейм для истории и скроллбара
        history_frame = tk.Frame(self.root)
        history_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky='nsew')
        
        # Вертикальный скроллбар
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Текстовое поле истории
        self.history_text = tk.Text(history_frame, height=7, width=40, font=('Arial', 10),
                                  state='disabled', bd=2, relief='groove',
                                  yscrollcommand=scrollbar.set)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.history_text.yview)
        
        # Настройка веса строки для правильного масштабирования
        self.root.grid_rowconfigure(3, weight=1)
    
    def update_history(self, entry):
        # Обновление истории с автоматической прокруткой вниз
        self.history.append(entry)
        if len(self.history) > 10:
            self.history.pop(0)
        
        self.history_text.config(state='normal')
        self.history_text.delete(1.0, tk.END)
        
        # Добавляем записи в хронологическом порядке (новые снизу)
        for item in self.history:
            self.history_text.insert(tk.END, item + "\n")
        
        # Автоматическая прокрутка к новой записи
        self.history_text.see(tk.END)
        self.history_text.config(state='disabled')
    
    def save_history(self):
        # Сохранение истории в файл
        if not self.history:
            messagebox.showinfo("Информация", "История операций пуста")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            title="Сохранить историю операций"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("История операций калькулятора:\n")
                    f.write("="*30 + "\n")
                    for item in self.history:
                        f.write(item + "\n")
                messagebox.showinfo("Успех", f"История сохранена в файл:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def update_display(self):
        # Обновление основного табло
        self.display.config(state='normal')
        self.display.delete('1.0', tk.END)
        display_text = self.full_operation if self.full_operation else "0"
        self.display.insert('1.0', display_text)
        self.display.see(tk.END)
        self.display.config(state='disabled')
    
    def create_buttons(self):
        # Кнопки калькулятора с кнопкой сохранения истории
        buttons = [
            # Первый ряд - основные функции
            ('AC', 4, 0), ('C', 4, 1), ('⌫', 4, 2), ('M+', 4, 3),
            # Второй ряд - цифры и M-
            ('7', 5, 0), ('8', 5, 1), ('9', 5, 2), ('M-', 5, 3),
            # Третий ряд
            ('4', 6, 0), ('5', 6, 1), ('6', 6, 2), ('/', 6, 3),
            # Четвертый ряд
            ('1', 7, 0), ('2', 7, 1), ('3', 7, 2), ('*', 7, 3),
            # Пятый ряд - цифры и операторы
            ('0', 8, 0), ('.', 8, 1), ('-', 8, 2), ('+', 8, 3),
            # Шестой ряд - функции памяти и "="
            ('MR', 9, 0), ('MC', 9, 1), ('=', 9, 2, 2),
            # Седьмой ряд - сохранение истории
            ('Сохранить историю', 10, 0, 4)
        ]
        
        # Стили кнопок
        digit_style = {'font': ('Arial', 18), 'padx': 15, 'pady': 12, 'bg': '#f0f0f0'}
        op_style = {'font': ('Arial', 18), 'padx': 15, 'pady': 12, 'bg': '#d9d9d9'}
        special_style = {'font': ('Arial', 16), 'padx': 10, 'pady': 10, 'bg': '#ffcccc'}
        memory_style = {'font': ('Arial', 14), 'padx': 10, 'pady': 8, 'bg': '#e0e0ff'}
        equals_style = {'font': ('Arial', 18), 'padx': 30, 'pady': 12, 'bg': '#b3d9ff'}
        save_style = {'font': ('Arial', 12), 'padx': 5, 'pady': 8, 'bg': '#d9ffd9'}
        
        for button in buttons:
            if len(button) == 4:  # Кнопка с columnspan
                text, row, col, colspan = button
                if text == '=':
                    btn = tk.Button(self.root, text=text, **equals_style,
                                  command=lambda t=text: self.on_button_click(t))
                    btn.grid(row=row, column=col, columnspan=colspan, sticky='nsew')
                elif text == 'Сохранить историю':
                    btn = tk.Button(self.root, text=text, **save_style,
                                  command=self.save_history)
                    btn.grid(row=row, column=col, columnspan=colspan, sticky='nsew')
                continue
            
            text, row, col = button
            
            if text.isdigit():
                style = digit_style
            elif text in '+-*/=':
                style = op_style if text != '=' else equals_style
            elif text in ['AC', 'C', '⌫']:
                style = special_style
            else:
                style = memory_style
                
            button = tk.Button(self.root, text=text, **style,
                             command=lambda t=text: self.on_button_click(t))
            button.grid(row=row, column=col, sticky='nsew')
        
        # Настройка расширения кнопок
        for i in range(11):  # Добавили дополнительный ряд
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
    
    def on_button_click(self, button_text):
        # Обработка цифр и точки
        if button_text.isdigit() or button_text == '.':
            self.current_input += button_text
            self.full_operation += button_text
            self.update_display()
        
        # Обработка удаления
        elif button_text == '⌫':
            self.current_input = self.current_input[:-1]
            self.full_operation = self.full_operation[:-1]
            self.update_display()
        
        # Обработка очистки текущего ввода
        elif button_text == 'C':
            if self.current_input:
                # Удаляем только последнее число из full_operation
                parts = self.full_operation.rsplit(' ', 1)
                if len(parts) > 1 and parts[-1] == self.current_input:
                    self.full_operation = parts[0]
                else:
                    self.full_operation = ""
                
                self.current_input = ""
                self.update_display()
        
        # Обработка полного сброса
        elif button_text == 'AC':
            self.current_input = ""
            self.full_operation = ""
            self.operation = None
            self.previous_value = 0
            self.update_display()
        
        # Обработка операторов
        elif button_text in '+-*/':
            if self.current_input:
                self.previous_value = float(self.current_input)
                self.operation = button_text
                self.full_operation += f" {button_text} "
                self.current_input = ""
                self.update_display()
        
        # Обработка равно
        elif button_text == '=':
            if self.operation and self.current_input:
                try:
                    current_value = float(self.current_input)
                    if self.operation == '+':
                        result = self.previous_value + current_value
                    elif self.operation == '-':
                        result = self.previous_value - current_value
                    elif self.operation == '*':
                        result = self.previous_value * current_value
                    elif self.operation == '/':
                        if current_value == 0:
                            messagebox.showerror("Ошибка", "Деление на ноль невозможно")
                            return
                        result = self.previous_value / current_value
                    
                    # Форматирование для истории (только при нажатии "=")
                    history_entry = f"{self.previous_value} {self.operation} {current_value} = {result}"
                    self.update_history(history_entry)
                    
                    self.full_operation = str(result)
                    self.current_input = str(result)
                    self.update_display()
                    self.operation = None
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный ввод")
                    self.current_input = ""
                    self.full_operation = ""
                    self.update_display()
        
        # Функции памяти
        elif button_text == 'M+':
            if self.current_input:
                self.memory += float(self.current_input)
                self.memory_active = True
                self.update_memory_indicator()
        
        elif button_text == 'M-':
            if self.current_input:
                self.memory -= float(self.current_input)
                self.memory_active = True
                self.update_memory_indicator()
        
        elif button_text == 'MR':
            self.current_input = str(self.memory)
            self.full_operation += str(self.memory)
            self.update_display()
        
        elif button_text == 'MC':
            self.memory = 0
            self.memory_active = False
            self.update_memory_indicator()

if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()