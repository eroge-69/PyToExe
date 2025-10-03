import tkinter as tk
from tkinter import messagebox

def on_button_click(char):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(0, current + str(char))

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        expression = entry.get()
        # Защита от выполнения опасных операций
        # Разрешаем только цифры, операторы и точки
        allowed_chars = "0123456789+-*/.() "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        else:
            raise ValueError("Недопустимые символы")
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль невозможно!")
        clear()
    except Exception as e:
        messagebox.showerror("Ошибка", "Некорректное выражение!")
        clear()

# Создание окна
root = tk.Tk()
root.title("Калькулятор")
root.geometry("300x400")
root.resizable(False, False)

# Поле ввода
entry = tk.Entry(root, font=("Arial", 18), width=20, borderwidth=2, relief="solid", justify="right")
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

# Кнопки
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('C', 4, 2), ('+', 4, 3),
    ('=', 5, 0)
]

# Добавление кнопок
for (text, row, col) in buttons:
    if text == 'C':
        btn = tk.Button(root, text=text, font=("Arial", 14), command=clear, bg="#ffcccc")
    elif text == '=':
        btn = tk.Button(root, text=text, font=("Arial", 14), command=calculate, bg="#ccffcc")
        btn.grid(row=row, column=col, columnspan=4, sticky="ew", padx=5, pady=5)
        continue
    else:
        btn = tk.Button(root, text=text, font=("Arial", 14),
                        command=lambda t=text: on_button_click(t))
    btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

# Настройка растягивания кнопок
for i in range(4):
    root.columnconfigure(i, weight=1)
for i in range(6):
    root.rowconfigure(i, weight=1)

# Запуск приложения
root.mainloop()