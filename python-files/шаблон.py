import tkinter as tk
from tkinter import ttk, messagebox
import random

def generate_numbers(target, tolerance, count):
    delta = target * tolerance
    numbers = []
    for _ in range(count):
        num = random.uniform(target - delta, target + delta)
        num = round(num, 3)
        numbers.append(num)
    return numbers

def run_generation():
    try:
        # Получение данных из полей
        target1 = float(entry_target1.get())
        tolerance1 = float(entry_tolerance1.get())
        count1 = int(entry_num_numbers1.get())

        target2 = float(entry_target2.get())
        tolerance2 = float(entry_tolerance2.get())
        count2 = int(entry_num_numbers2.get())

        target3 = float(entry_target3.get())
        tolerance3 = float(entry_tolerance3.get())
        count3 = int(entry_num_numbers3.get())

        # Очистка результата
        result_text.delete('1.0', tk.END)

        # Генерация и вывод для каждого набора
        for i, (target, tolerance, count) in enumerate([
            (target1, tolerance1, count1),
            (target2, tolerance2, count2),
            (target3, tolerance3, count3)
        ], start=1):
            numbers = generate_numbers(target, tolerance, count)
            for num in numbers:
                formatted = f"{num:.3f}".replace('.', ',')
                result_text.insert(tk.END, formatted + "\n")
    except Exception as e:
        messagebox.showerror("Ошибка", "Проверьте правильность введённых данных.\n" + str(e))

# Создаем главное окно
root = tk.Tk()
root.title("Генератор чисел с настройками")

# Основной фрейм
main_frame = ttk.Frame(root)
main_frame.pack(padx=10, pady=10, fill='both', expand=True)

# Поле вывода слева
result_frame = ttk.Frame(main_frame)
result_frame.pack(side='left', fill='both', expand=True)

tk.Label(result_frame, text="Результаты:").pack(anchor='nw')
result_text = tk.Text(result_frame, height=20, width=50)
result_text.pack(fill='both', expand=True)

# Панель настроек справа
settings_frame = ttk.Frame(main_frame)
settings_frame.pack(side='right', fill='y', padx=10)

# Функция для добавления настроек
def add_setting_row(parent, label_prefix, default_target, default_tolerance, default_count):
    frame = ttk.Frame(parent)
    frame.pack(pady=5, fill='x')

    ttk.Label(frame, text=label_prefix).grid(row=0, column=0, columnspan=2)

    ttk.Label(frame, text="Объем").grid(row=1, column=0, sticky='w')
    target_entry = ttk.Entry(frame, width=8)
    target_entry.insert(0, str(default_target))
    target_entry.grid(row=1, column=1, padx=5)

    ttk.Label(frame, text="Погрешность").grid(row=2, column=0, sticky='w')
    tolerance_entry = ttk.Entry(frame, width=8)
    tolerance_entry.insert(0, str(default_tolerance))
    tolerance_entry.grid(row=2, column=1, padx=5)

    ttk.Label(frame, text="Кол-во").grid(row=3, column=0, sticky='w')
    count_entry = ttk.Entry(frame, width=8)
    count_entry.insert(0, str(default_count))
    count_entry.grid(row=3, column=1, padx=5)

    return target_entry, tolerance_entry, count_entry

# Создаём три набора настроек
entry_target1, entry_tolerance1, entry_num_numbers1 = add_setting_row(settings_frame, "Набор 1", 100, 0.005, 10)
entry_target2, entry_tolerance2, entry_num_numbers2 = add_setting_row(settings_frame, "Набор 2", 500, 0.003, 10)
entry_target3, entry_tolerance3, entry_num_numbers3 = add_setting_row(settings_frame, "Набор 3", 1000, 0.003, 10)

# Кнопка для запуска
generate_button = ttk.Button(root, text="Генерировать", command=run_generation)
generate_button.pack(pady=10)

root.mainloop()