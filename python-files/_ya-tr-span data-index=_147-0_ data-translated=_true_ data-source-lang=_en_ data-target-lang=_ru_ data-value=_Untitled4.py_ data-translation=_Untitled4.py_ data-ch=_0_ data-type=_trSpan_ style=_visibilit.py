import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

def parse_time_dot_format(time_str):
    try:
        return datetime.strptime(time_str.replace('.', ':'), "%H:%M")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите время в формате чч.мм (например, 08.30)")
        return None

def calculate_end_time():
    start_time_str = entry_start.get()
    work_hours_str = entry_hours.get()
    lunch_option = lunch_var.get()

    try:
        work_hours = float(work_hours_str)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите количество рабочих часов числом (например, 6)")
        return

    start_time = parse_time_dot_format(start_time_str)
    if not start_time:
        return

    if lunch_option == "1":
        lunch_start_str = entry_lunch_start.get()
        lunch_end_str = entry_lunch_end.get()

        lunch_start = parse_time_dot_format(lunch_start_str)
        lunch_end = parse_time_dot_format(lunch_end_str)
        if not lunch_start or not lunch_end:
            return

        lunch_duration = lunch_end - lunch_start
        end_time = start_time + timedelta(hours=work_hours) + lunch_duration
    else:
        end_time = start_time + timedelta(hours=work_hours)

    result = end_time.strftime("%H.%M")
    messagebox.showinfo("Результат", f"Время окончания рабочего дня: {result}")

# Создание окна
root = tk.Tk()
root.title("Калькулятор рабочего дня")
root.geometry("400x300")
root.resizable(False, False)

# Заголовок
tk.Label(root, text="Введите данные", font=("Arial", 14)).pack(pady=10)

# Время начала
tk.Label(root, text="Начало рабочего дня (чч.мм):").pack()
entry_start = tk.Entry(root)
entry_start.pack()

# Кол-во часов
tk.Label(root, text="Продолжительность рабочего времени (в часах):").pack()
entry_hours = tk.Entry(root)
entry_hours.pack()

# Обед
tk.Label(root, text="Есть ли обед? (1 — да, 2 — нет):").pack()
lunch_var = tk.StringVar(value="2")
tk.Entry(root, textvariable=lunch_var).pack()

# Время обеда
tk.Label(root, text="Начало обеда (чч.мм):").pack()
entry_lunch_start = tk.Entry(root)
entry_lunch_start.pack()

tk.Label(root, text="Окончание обеда (чч.мм):").pack()
entry_lunch_end = tk.Entry(root)
entry_lunch_end.pack()

# Кнопка расчёта
tk.Button(root, text="Рассчитать", command=calculate_end_time, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=15)

# Запуск
root.mainloop()
