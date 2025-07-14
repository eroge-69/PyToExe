import tkinter as tk

def add():
    result.set(float(entry1.get()) + float(entry2.get()))

def subtract():
    result.set(float(entry1.get()) - float(entry2.get()))

def multiply():
    result.set(float(entry1.get()) * float(entry2.get()))

def divide():
    if float(entry2.get()) != 0:
        result.set(float(entry1.get()) / float(entry2.get()))
    else:
        result.set("Ошибка: Деление на ноль")

# Создание основного окна
root = tk.Tk()
root.title("Калькулятор")

entry1 = tk.Entry(root)
entry1.grid(row=0, column=1)

entry2 = tk.Entry(root)
entry2.grid(row=1, column=1)

result = tk.StringVar()
result_label = tk.Label(root, textvariable=result)
result_label.grid(row=2, column=1)

tk.Label(root, text="Число 1").grid(row=0, column=0)
tk.Label(root, text="Число 2").grid(row=1, column=0)

tk.Button(root, text="+", command=add).grid(row=3, column=0)
tk.Button(root, text="-", command=subtract).grid(row=3, column=1)
tk.Button(root, text="*", command=multiply).grid(row=3, column=2)
tk.Button(root, text="/", command=divide).grid(row=3, column=3)

root.mainloop()