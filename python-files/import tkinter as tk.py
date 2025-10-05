import tkinter as tk
from tkinter import messagebox
import json
import os

history_file = 'history.json'
history = []

def load_history():
    global history
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []

def save_history():
    with open(history_file, 'w') as f:
        json.dump(history, f)

def button_click(key):
    try:
        if key == '=':
            calculate()
        elif key == 'CE':
            display.delete(0, tk.END)
        elif key == 'DEL':
            current = display.get()
            display.delete(0, tk.END)
            display.insert(0, current[:-1])
        else:
            display.insert(tk.END, key)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

def calculate():
    try:
        expression = display.get()
        if not expression:
            return
            
        result = eval(expression)
        display.delete(0, tk.END)
        display.insert(0, str(result))
        
        # Сохранение в историю
        history.append(f"{expression} = {result}")
        save_history()
        
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль невозможно!")
    except Exception as e:
        messagebox.showerror("Ошибка", "Неверное математическое выражение")

window = tk.Tk()
window.title("Калькулятор")
window.iconbitmap("C:/Users/user/Downloads/fff.ico")
window.configure(bg='#FFFFFF')
window.resizable(False, False)

display_font = ('Arial', 18)
button_font = ('Arial', 14)

load_history()

display = tk.Entry(
    window,
    font=display_font,
    justify='right',
    bg='#000000',
    fg='#FFFFFF',
    insertbackground='#ff192d',
    borderwidth=10
)

buttons = [
    ('7', '#ff192d'), ('8', '#ff192d'), ('9', '#ff192d'), ('/', '#90EE90'),
    ('4', '#ff192d'), ('5', '#ff192d'), ('6', '#ff192d'), ('*', '#90EE90'),
    ('1', '#ff192d'), ('2', '#ff192d'), ('3', '#ff192d'), ('-', '#90EE90'),
    ('0', '#ff192d'), ('.', '#ff192d'), ('+', '#90EE90'),
    ('CE', '#DB7093'), ('DEL', '#DB7093'), ('=', '#90EE90')
]

button_widgets = {}
for text, color in buttons:
    button_widgets[text] = tk.Button(
        window,
        text=text,
        font=button_font,
        bg=color,
        fg='#FFFFFF',
        activebackground='#E6E6FA',
        activeforeground='#000000',
        borderwidth=0,
        command=lambda t=text: button_click(t)
    )

display.grid(row=0, column=0, columnspan=4, sticky='we', padx=10, pady=10)


button_layout = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', '.', '+', '='],
    ['CE', 'DEL', '', '']
]

for i, row in enumerate(button_layout):
    for j, text in enumerate(row):
        if text:
            button_widgets[text].grid(
                row=i+1, 
                column=j, 
                sticky='we', 
                padx=5, 
                pady=5,
                ipadx=10,
                ipady=10
            )

for i in range(5):
    window.grid_rowconfigure(i+1, weight=1)
for i in range(4):
    window.grid_columnconfigure(i, weight=1)

window.mainloop()