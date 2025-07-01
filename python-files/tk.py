import tkinter as tk
from datetime import datetime

# Создаем главное окно
root = tk.Tk()
root.title("Текущее время и дата")
root.geometry("400x300")  # Размер окна
root.configure(bg="white")

# Создаем рамку для отображения времени
time_frame = tk.Frame(root, bg="white")
time_frame.pack(pady=20)

# Функция для обновления времени
def update_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    time_label.config(text=current_time)
    
    # Обновляем дату и день недели
    month_label.config(text=now.strftime("%B"))
    day_label.config(text=now.strftime("%A"))
    
    # Запускаем функцию снова через 1 секунду
    root.after(1000, update_time)

# Создаем метки для отображения времени
time_label = tk.Label(time_frame, text="00:00:00", font=("Digital-7", 48), bg="white", fg="black")
time_label.grid(row=0, column=0, padx=10, pady=10)

# Создаем метки для отображения месяца и дня недели
month_label = tk.Label(root, text="", font=("Arial", 24), bg="white", fg="black")
month_label.pack(pady=10)

day_label = tk.Label(root, text="", font=("Arial", 24), bg="white", fg="black")
day_label.pack(pady=10)

# Запускаем функцию обновления времени
update_time()

# Запускаем главный цикл окна
root.mainloop()