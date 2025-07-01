import tkinter as tk
from datetime import datetime

def update_clock():
    now = datetime.now()

    # Форматируем время (часы:минуты:секунды)
    time_str = now.strftime("%H:%M:%S")
    
    # Форматируем месяц
    month_str = now.strftime("%B")
    
    # Форматируем день недели
    weekday_str = now.strftime("%A")
    
    # Форматируем дату (день.месяц.год)
    date_str = now.strftime("%d.%m.%Y")
    
    # Обновляем тексты меток
    time_label.config(text=time_str)
    month_label.config(text=month_str)
    weekday_label.config(text=weekday_str)
    date_label.config(text=date_str)
    
    # Запускаем функцию снова через 1000 мс (1 секунда)
    root.after(1000, update_clock)

# Создаем главное окно
root = tk.Tk()
root.title("Часы")
root.geometry("200x300")  # Фиксированный размер окна
root.resizable(False, False)  # Запрещаем масштабирование

# Создаем рамку для центрирования содержимого
frame = tk.Frame(root, bg="black")
frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

# Метка для отображения времени
time_label = tk.Label(
    frame,
    font=("Digital-7", 40),  # Шрифт для циферблата
    fg="white",
    bg="black",
    anchor=tk.CENTER,
    borderwidth=2,
    relief=tk.RIDGE  # Добавляем границу
)
time_label.pack(pady=10, fill=tk.X)

# Метка для месяца
month_label = tk.Label(
    frame,
    font=("Arial", 16),
    fg="white",
    bg="black",
    relief=tk.RIDGE,  # Добавляем границу
    anchor=tk.CENTER,
    borderwidth=2
)
month_label.pack(pady=5, fill=tk.X)

# Метка для дня недели
weekday_label = tk.Label(
    frame,
    font=("Arial", 16),
    fg="white",
    bg="black",
    relief=tk.RIDGE,  # Добавляем границу
    anchor=tk.CENTER,
    borderwidth=2
)
weekday_label.pack(pady=5, fill=tk.X)

# Метка для даты
date_label = tk.Label(
    frame,
    font=("Digital-7", 20),
    fg="white",
    bg="black",
    anchor=tk.CENTER,
    borderwidth=2,
    relief=tk.RIDGE  # Добавляем границу
)
date_label.pack(pady=10, fill=tk.X)

# Запускаем функцию обновления часов
update_clock()

# Запускаем главный цикл
root.mainloop()