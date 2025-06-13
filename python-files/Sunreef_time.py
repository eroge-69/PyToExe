import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

def calculate_end_time():
    start_time_str = entry.get()
    try:
        # Парсимо час у форматі год:хв
        start_time = datetime.strptime(start_time_str, "%H:%M")
        # Додаємо 8 годин і 15 хв
        end_time = start_time + timedelta(hours=8, minutes=15)
        result_label.config(text="Кінець зміни: " + end_time.strftime("%H:%M"))
    except ValueError:
        messagebox.showerror("Помилка", "Введіть час у форматі ГГ:ХХ (наприклад, 08:30)")

# GUI
root = tk.Tk()
root.title("Розрахунок кінця зміни")

tk.Label(root, text="Початок зміни (ГГ:ХХ):").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="Обчислити", command=calculate_end_time).pack(pady=10)
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

root.mainloop()
