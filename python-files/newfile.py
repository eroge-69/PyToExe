import tkinter as tk
from tkinter import messagebox
import random

def show_answer():
    answers = [
        "Коньченый",
        "Пидорасик",
        "Хуеплет",
        "Хуесос ",
        "Уебок"
    ]
    messagebox.showinfo("Ответ", random.choice(answers))

# Создаем главное окно
root = tk.Tk()
root.title("Узнай о физруке")
root.geometry("400x300")
root.configure(bg='#e6f2ff')

# Заголовок
title_label = tk.Label(
    root,
    text="Вопрос дня",
    font=("Arial", 20, "bold"),
    bg='#e6f2ff',
    fg='#0066cc'
)
title_label.pack(pady=20)

# Основная кнопка
button = tk.Button(
    root,
    text="Кто физрук?",
    command=show_answer,
    font=("Arial", 18, "bold"),
    bg='#ffcc00',
    fg='#333333',
    padx=30,
    pady=15,
    borderwidth=4,
    relief="groove",
    cursor="hand2"
)
button.pack(expand=True)

# Подсказка внизу
hint_label = tk.Label(
    root,
    text="Смело нажимайте на кнопку!",
    font=("Arial", 12, "italic"),
    bg='#e6f2ff',
    fg='#666666'
)
hint_label.pack(side='bottom', pady=20)

# Запускаем приложение
root.mainloop()
