import tkinter as tk
import random
import time
import threading

# Функция для открытия окна с текстом
def open_window():
    window = tk.Tk()
    window.title("Предупреждение")
    label = tk.Label(window, text="Не играй с читами", font=("Arial", 20))
    label.pack(padx=50, pady=50)
    window.geometry("400x200")
    window.mainloop()

# Функция для мигания экрана разными цветами
def flash_screen():
    while True:
        color = random.choice(["red", "green", "blue", "yellow", "purple", "cyan", "orange"])
        root.configure(bg=color)
        time.sleep(0.5)  # Задержка между сменами цветов

# Создаем 50 окон
for _ in range(50):
    threading.Thread(target=open_window, daemon=True).start()

import random

# Создание главного окна
root = tk.Tk()
root.geometry("400x400")  # Установите размер окна
root.attributes("-fullscreen", True)  # Разворачиваем окно на весь экран

# Список цветов, между которыми будет происходить мигание
colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan']

# Функция для мигания экрана
def blink():
    color = random.choice(colors)  # Выбираем случайный цвет
    root.configure(bg=color)  # Изменяем фон окна на выбранный цвет
    root.after(25, blink)  # Вызываем функцию снова через 500 миллисекунд

# Начать мигание
blink()

# Запуск основного цикла приложения
root.mainloop()
