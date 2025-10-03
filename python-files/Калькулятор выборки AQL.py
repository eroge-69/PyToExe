import tkinter as tk
from tkinter import messagebox

# === Логика ===

def calculate_sample_size(order_size):
    if order_size <= 1:
        return 0
    elif 2 <= order_size <= 8:
        return 2
    elif 9 <= order_size <= 15:
        return 3
    elif 16 <= order_size <= 25:
        return 5
    elif 26 <= order_size <= 50:
        return 8
    elif 51 <= order_size <= 90:
        return 13
    elif 91 <= order_size <= 150:
        return 20
    elif 151 <= order_size <= 280:
        return 32
    elif 281 <= order_size <= 500:
        return 50
    elif 501 <= order_size <= 1200:
        return 80
    elif 1201 <= order_size <= 3200:
        return 125
    elif 3201 <= order_size <= 10000:
        return 200
    elif 10001 <= order_size <= 35000:
        return 315
    elif 35001 <= order_size <= 150000:
        return 500
    elif 150001 <= order_size <= 500000:
        return 1250
    elif order_size > 500000:
        return 2000
    else:
        return 0

def calculate_defect_percentage(defect_count, order_size):
    try:
        return (defect_count / order_size) * 100
    except ZeroDivisionError:
        return 0

def calculate_adjusted_sample(order_size, sample_size, defect_percentage):
    if sample_size == 0 or defect_percentage == 0:
        return sample_size
    elif defect_percentage <= 3:
        return min(order_size, int(sample_size + order_size * 0.10))
    elif 3 < defect_percentage <= 10:
        return min(order_size, int(sample_size + order_size * 0.50))
    else:
        return order_size

# === Интерфейс ===

def process_inputs():
    try:
        order = int(entry_order.get())
        defect_input = entry_defects.get().strip()

        # Если поле с браком пустое — считать 0
        defects = int(defect_input) if defect_input else 0

        sample = calculate_sample_size(order)
        defect_percent = calculate_defect_percentage(defects, order)
        adjusted = calculate_adjusted_sample(order, sample, defect_percent)

        result_text.set(f"""
Размер выборки: {sample}
Процент брака: {defect_percent:.2f}%
{"Выборка увеличена до: " + str(adjusted) if adjusted > sample else "Окончательная выборка: " + str(adjusted)}
""")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректный размер заказа!")

# === Окно ===

root = tk.Tk()
root.title("Калькулятор выборки")
root.geometry("400x260")

tk.Label(root, text="Размер заказа:").pack()
entry_order = tk.Entry(root)
entry_order.pack()

tk.Label(root, text="Количество брака:").pack()
entry_defects = tk.Entry(root)
entry_defects.pack()

tk.Button(root, text="Рассчитать", command=process_inputs).pack(pady=10)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, justify="left").pack()

root.mainloop()
