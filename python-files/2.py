import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt


def plot_function():
    raw_input = entry.get().strip().lower().replace('^', '**')

    if not raw_input.startswith('y='):
        messagebox.showerror("Ошибка", "Введите функцию в формате y=выражение")
        return

    expression = raw_input[2:]

    if 'x' not in expression:
        messagebox.showerror("Ошибка", "Функция должна содержать переменную x")
        return

    try:
        x_min = float(entry_x_min.get())
        x_max = float(entry_x_max.get())

        if x_min >= x_max:
            messagebox.showerror("Ошибка", "Минимальное значение x должно быть меньше максимального")
            return

        x = np.linspace(x_min, x_max, 400)
        local_dict = {'x': x, 'np': np}
        y = eval(expression, {"__builtins__": None}, local_dict)

        valid = np.isfinite(y)
        x_valid = x[valid]

        if len(x_valid) == 0:
            raise ValueError("Нет допустимых значений для отображения графика.")

        open_calc_window(expression)

        plt.figure(figsize=(8, 5))
        plt.plot(x, y, label=f'y = {expression}', color='blue')
        plt.title("График функции")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except ValueError:
        messagebox.showerror("Ошибка", "Неверный ввод диапазона x или ошибки в функции")
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль в выражении")
    except SyntaxError:
        messagebox.showerror("Ошибка", "Синтаксическая ошибка в выражении")
    except NameError:
        messagebox.showerror("Ошибка", "Недопустимое имя переменной или функция")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


def open_calc_window(expression):
    def calculate_y():
        try:
            x_val = float(entry_x_val.get())
            local_dict = {'x': x_val, 'np': np}
            y_val = eval(expression, {"__builtins__": None}, local_dict)
            if x_val == 0: result_label.config(text=f"1")
            else: result_label.config(text=f"y = {y_val}")
        except Exception as e:
            result_label.config(text=f"Ошибка: {str(e)}")

    calc_window = tk.Toplevel(root)
    calc_window.title("Расчёт y по заданному x")
    calc_window.geometry("300x150")

    tk.Label(calc_window, text="Введите x:").pack(pady=5)
    entry_x_val = tk.Entry(calc_window)
    entry_x_val.pack()

    tk.Button(calc_window, text="Рассчитать", command=calculate_y).pack(pady=5)
    result_label = tk.Label(calc_window, text="")
    result_label.pack(pady=5)


root = tk.Tk()
root.title("Построение графика функции y(x)")
root.geometry("450x200")
root.resizable(False, False)

label = tk.Label(root, text="Введите функцию:")
label.pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack()

frame_range = tk.Frame(root)
frame_range.pack(pady=5)

label_x_min = tk.Label(frame_range, text="x min:")
label_x_min.grid(row=0, column=0)
entry_x_min = tk.Entry(frame_range, width=10)
entry_x_min.grid(row=0, column=1)
entry_x_min.insert(0, "-10")

label_x_max = tk.Label(frame_range, text="x max:")
label_x_max.grid(row=0, column=2)
entry_x_max = tk.Entry(frame_range, width=10)
entry_x_max.grid(row=0, column=3)
entry_x_max.insert(0, "10")

plot_button = tk.Button(root, text="Построить график", command=plot_function)
plot_button.pack(pady=10)

root.mainloop()