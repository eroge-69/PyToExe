import tkinter as tk
import random

# создаём главное окно
root = tk.Tk()
root.title("Безопасный мигающий экран")
root.attributes("-fullscreen", True)  # разворачиваем на весь экран

# функция для смены цвета
def flash_colors():
    if running[0]:  # проверка, продолжаем ли мигание
        colors = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "cyan"]
        root.config(bg=random.choice(colors))
        root.after(50, flash_colors)  # повтор каждые 50 миллисекунд

# функция стоп
def stop():
    running[0] = False
    root.destroy()  # закрываем окно

# кнопка стоп
stop_button = tk.Button(root, text="СТОП", command=stop, font=("Arial", 24), bg="white")
stop_button.place(relx=0.5, rely=0.5, anchor="center")  # по центру

running = [True]  # флаг работы мигания
flash_colors()    # запускаем мигание

root.mainloop()
