import tkinter as tk
from tkinter import ttk

def calculate():
    try:
        number = int(entry.get())
        divisor = int(choice.get())
        stacks = number // divisor
        remainder = number % divisor
        result.set(f"{stacks} ст. {remainder} шт.")
    except ValueError:
        result.set("Введите число!")

# Главное окно
root = tk.Tk()
root.title("MineStackerCalc")
root.geometry("250x200")
root.resizable(False, False)

# Поле для ввода числа
tk.Label(root, text="Введите число:").pack(pady=5)
entry = tk.Entry(root, justify="center")
entry.pack()

# Выбор делителя
tk.Label(root, text="Делить на:").pack(pady=5)
choice = tk.StringVar(value="64")
ttk.Radiobutton(root, text="64", variable=choice, value="64").pack()
ttk.Radiobutton(root, text="16", variable=choice, value="16").pack()

# Кнопка "Посчитать"
tk.Button(root, text="Посчитать", command=calculate).pack(pady=10)

# Поле для результата
result = tk.StringVar()
tk.Label(root, textvariable=result, font=("Arial", 12, "bold")).pack(pady=10)

root.mainloop()
