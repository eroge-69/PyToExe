import tkinter as tk

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Помилка!")

# Створення вікна
root = tk.Tk()
root.title("Калькулятор")

# Поле введення
entry = tk.Entry(root, width=20, font=("Arial", 14), borderwidth=5)
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

# Кнопки
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', 'C', '=', '+'
]

row = 1
col = 0
for button in buttons:
    if button == '=':
        tk.Button(root, text=button, padx=20, pady=10, command=calculate).grid(row=row, column=col)
    elif button == 'C':
        tk.Button(root, text=button, padx=20, pady=10, command=lambda: entry.delete(0, tk.END)).grid(row=row, column=col)
    else:
        tk.Button(root, text=button, padx=20, pady=10, command=lambda b=button: entry.insert(tk.END, b)).grid(row=row, column=col)
    
    col += 1
    if col > 3:
        col = 0
        row += 1

root.mainloop()
