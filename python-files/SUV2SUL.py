import tkinter as tk
from tkinter import ttk

def validate_number(text):
    """Заменяет запятые на точки для корректного ввода чисел"""
    return text.replace(",", ".")

def calculate_suvlbm():
    try:
        gender = gender_combobox.get()
        
        # Получаем и проверяем данные
        height_text = validate_number(height_entry.get())
        weight_text = validate_number(weight_entry.get())
        suvbw_text = validate_number(suvbw_entry.get())
        
        height = float(height_text) if height_text else 0
        weight = float(weight_text) if weight_text else 0
        suvbw = float(suvbw_text) if suvbw_text else 0

        if height <= 0 or weight <= 0 or suvbw <= 0:
            raise ValueError("Все числовые поля должны быть > 0")

        # Расчет LBM
        if gender == "М":
            lbm = 1.1 * weight - 128 * (weight / height) ** 2
        else:
            lbm = 1.07 * weight - 148 * (weight / height) ** 2

        suvlbm = suvbw * lbm / weight
        result_label.config(text=f"SUVlbm: {suvlbm:.2f}")

    except ValueError as e:
        result_label.config(text=f"Ошибка: {str(e)}")

def reset_suvbw():
    """Сброс только поля SUVbw"""
    suvbw_entry.delete(0, tk.END)

def reset_all():
    """Сброс всех полей и результата"""
    gender_combobox.set("М")
    height_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    suvbw_entry.delete(0, tk.END)
    result_label.config(text="SUVlbm: ")

# Настройка окна
app = tk.Tk()
app.title("SUVbw → SUVlbm Calculator")
app.geometry("400x350")

# Стиль для кнопок
style = ttk.Style()
style.configure("TButton", padding=5, font=('Arial', 10))

# Элементы интерфейса
tk.Label(app, text="Пол:").pack()
gender_combobox = ttk.Combobox(app, values=["М", "Ж"])
gender_combobox.pack()
gender_combobox.set("М")

tk.Label(app, text="Рост (см):").pack()
height_entry = tk.Entry(app)
height_entry.pack()

tk.Label(app, text="Вес (кг):").pack()
weight_entry = tk.Entry(app)
weight_entry.pack()

tk.Label(app, text="SUVbw:").pack()
suvbw_entry = tk.Entry(app)
suvbw_entry.pack()

# Фрейм для кнопок
button_frame = tk.Frame(app)
button_frame.pack(pady=10)

calculate_button = ttk.Button(button_frame, text="Рассчитать", command=calculate_suvlbm)
calculate_button.grid(row=0, column=0, padx=5)

reset_suvbw_button = ttk.Button(button_frame, text="Сбросить SUVbw", command=reset_suvbw)
reset_suvbw_button.grid(row=0, column=1, padx=5)

reset_all_button = ttk.Button(button_frame, text="Сбросить всё", command=reset_all)
reset_all_button.grid(row=0, column=2, padx=5)

# Поле результата
result_label = tk.Label(app, text="SUVlbm: ", font=("Arial", 12, "bold"))
result_label.pack()

app.mainloop()