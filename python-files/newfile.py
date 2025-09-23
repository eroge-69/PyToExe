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
        label_result.config(text=f"Сумма суточных = {y:.2f} руб.")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите число")

# Интерфейс
root = tk.Tk()
root.title("Калькулятор суточных")
root.geometry("300x150")
root.resizable(False, False)
root.configure(bg="blue") # Установка синего фона

tk.Label(root, text="Введите количество дней:", bg="blue", fg="white").pack(pady=10)
entry_x = tk.Entry(root, width=20)
entry_x.pack(pady=10)

btn_calc = tk.Button(root, text="Рассчитать", command=calculate)
btn_calc.pack(pady=10)

label_result = tk.Label(root, text="Сумма суточных = ", bg="blue", fg="white")
label_result.pack(pady=10)

root.mainloop()