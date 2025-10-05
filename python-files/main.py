import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Калькулятор")
root.configure(bg='black')
root.resizable(False, False)

current_text = ""
history_file = "history.txt"

def add_to_display(value):
    global current_text
    current_text += str(value)
    display.delete(0, tk.END)
    display.insert(0, current_text)

def clear_display():
    global current_text
    current_text = ""
    display.delete(0, tk.END)

def delete_last():
    global current_text
    current_text = current_text[:-1]
    display.delete(0, tk.END)
    display.insert(0, current_text)

def calculate():
    global current_text
    try:
        result = eval(current_text)
        save_to_history(f"{current_text} = {result}")
        current_text = str(result)
        display.delete(0, tk.END)
        display.insert(0, current_text)
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль!")
        clear_display()
    except Exception:
        messagebox.showerror("Ошибка", "Неправильное выражение")
        clear_display()

def save_to_history(entry):
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

# Поле ввода
display = tk.Entry(root, font=('Arial', 14), justify='right', 
                   bg='black', fg='white', insertbackground='white')
display.grid(row=0, column=0, columnspan=4, sticky='we', padx=5, pady=5)

# Стиль кнопок
button_style = {
    'font': ('Arial', 12),
    'bg': '#4B0082',
    'fg': 'white',
    'activebackground': '#800080',
    'activeforeground': 'white',
    'relief': 'flat',
    'border': 0,
    'width': 5,
    'height': 2
}

buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3)
]

for (text, row, col) in buttons:
    if text == '=':
        tk.Button(root, text=text, **button_style, command=calculate).grid(row=row, column=col, padx=2, pady=2, sticky='we')
    else:
        tk.Button(root, text=text, **button_style, command=lambda t=text: add_to_display(t)).grid(row=row, column=col, padx=2, pady=2, sticky='we')

tk.Button(root, text='C', **button_style, command=clear_display).grid( row=5, column=0, columnspan=2, padx=2, pady=2, sticky='we')
tk.Button(root, text='⌫', **button_style, command=delete_last).grid(row=5, column=2, columnspan=2, padx=2, pady=2, sticky='we')

for i in range(5):
    root.grid_rowconfigure(i, weight=1)
for i in range(4):
    root.grid_columnconfigure(i, weight=1)

root.mainloop()