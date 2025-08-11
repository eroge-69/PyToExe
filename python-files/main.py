import tkinter as tk
from tkinter import messagebox

def calculate_bmi():
    try:
        height_cm = float(entry_height.get())
        weight_kg = float(entry_weight.get())

        if height_cm <= 0 or weight_kg <= 0:
            messagebox.showerror("Ошибка", "Рост и вес должны быть больше нуля!")
            return

        # Переводим рост в метры
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)

        # Интерпретация
        if bmi < 18.5:
            status = "Недостаток веса"
        elif 18.5 <= bmi < 25:
            status = "Нормальный вес"
        elif 25 <= bmi < 30:
            status = "Избыточный вес"
        else:
            status = "Ожирение"

        label_result.config(text=f"Ваш ИМТ: {bmi:.2f}\n{status}")
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа!")

# Создаём окно
window = tk.Tk()
window.title("Калькулятор ИМТ")
window.geometry("300x250")
window.resizable(False, False)

# Заголовок
tk.Label(window, text="Калькулятор индекса массы тела", font=("Arial", 12, "bold")).pack(pady=10)

# Поле для роста
tk.Label(window, text="Рост (см):").pack()
entry_height = tk.Entry(window)
entry_height.pack()

# Поле для веса
tk.Label(window, text="Вес (кг):").pack()
entry_weight = tk.Entry(window)
entry_weight.pack()

# Кнопка
tk.Button(window, text="Рассчитать ИМТ", command=calculate_bmi).pack(pady=15)

# Результат
label_result = tk.Label(window, text="", font=("Arial", 10), fg="blue")
label_result.pack()

# Запуск
window.mainloop()