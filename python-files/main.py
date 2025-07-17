import tkinter as tk
from tkinter import messagebox


def calculate():
    try:
        # Получаем данные из полей ввода
        circles = int(circles_entry.get())
        initial_amount = float(amount_entry.get())
        buy_rate = float(buy_rate_entry.get())
        sell_rate = float(sell_rate_entry.get())

        if circles < 0 or initial_amount < 0 or buy_rate <= 0 or sell_rate <= 0:
            raise ValueError("Все значения должны быть положительными")

        current_amount = initial_amount

        # Выполняем вычисления: (сумма / курс_покупки) * курс_продажи
        for _ in range(circles):
            current_amount = (current_amount / buy_rate) * sell_rate

        # Вычисляем разницу
        difference = current_amount - initial_amount

        # Формируем результат
        result_text = (
            f"Изначальная сумма: {initial_amount:.2f}\n"
            f"Получившаяся сумма: {current_amount:.2f}\n"
            f"Разница: {difference:.2f}"
        )

        # Выводим результат
        result_label.config(text=result_text)

    except ValueError as e:
        messagebox.showerror("Ошибка", f"Некорректные данные: {e}")


# Создаем главное окно
root = tk.Tk()
root.title("Калькулятор обмена валют")
root.geometry("400x440")

# Поля для ввода данных
tk.Label(root, text="Количество кругов:").pack(pady=5)
circles_entry = tk.Entry(root)
circles_entry.pack(pady=5)

tk.Label(root, text="Изначальная сумма:").pack(pady=5)
amount_entry = tk.Entry(root)
amount_entry.pack(pady=5)

tk.Label(root, text="Курс покупки (например, 80):").pack(pady=5)
buy_rate_entry = tk.Entry(root)
buy_rate_entry.insert(0, "80")  # Значение по умолчанию
buy_rate_entry.pack(pady=5)

tk.Label(root, text="Курс продажи (например, 83):").pack(pady=5)
sell_rate_entry = tk.Entry(root)
sell_rate_entry.insert(0, "83")  # Значение по умолчанию
sell_rate_entry.pack(pady=5)

# Кнопка расчёта
calculate_btn = tk.Button(root, text="Рассчитать", command=calculate)
calculate_btn.pack(pady=15)

# Поле для вывода результата
result_label = tk.Label(root, text="", justify=tk.LEFT)
result_label.pack(pady=10)

# Запуск приложения
root.mainloop()