import tkinter as tk
from tkinter import messagebox

def say_hello():
    name = entry.get()
    if name:
        messagebox.showinfo("Приветствие", f"Привет, {name}!")
    else:
        messagebox.showerror("Ошибка", "Введите имя!")

# Создаем окно
root = tk.Tk()
root.title("Тестовое приложение")
root.geometry("300x150")

# Поле ввода
label = tk.Label(root, text="Введите ваше имя:")
label.pack(pady=10)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)

# Кнопка
button = tk.Button(root, text="Поприветствовать", command=say_hello)
button.pack(pady=10)

root.mainloop()