import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        x = float(entry_x.get())
        if x > 21:
            y = 24080 + (x - 21) * 1400
        elif x > 14:
            y = 14980 + (x - 14) * 1300
        elif x > 7:
            y = 6580 + (x - 7) * 1200
        else:
            y = x * 940
        label_result.config(text=f"Сумма суточных = {y:.2f}")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите число")

# Интерфейс
root = tk.Tk()
root.title("Калькулятор Суточных")

tk.Label(root, text="Введите Количество дней:").pack(pady=5)
entry_x = tk.Entry(root)
entry_x.pack(pady=5)

btn_calc = tk.Button(root, text="Рассчитать", command=calculate)
btn_calc.pack(pady=5)

label_result = tk.Label(root, text="Сумма к выплате = ")
label_result.pack(pady=5)

root.mainloop()
