import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp


class FunctionPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("График функции одной переменной")
        self.mode = tk.StringVar(value="formula")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Способ задания функции:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.root, text="Формула", variable=self.mode, value="formula", command=self.toggle_mode).grid(
            row=0, column=1)
        ttk.Radiobutton(self.root, text="Таблица", variable=self.mode, value="table", command=self.toggle_mode).grid(
            row=0, column=2)

        self.formula_entry = ttk.Entry(self.root, width=40)
        ttk.Label(self.root, text="Формула (например, sin(x) + log(x)):").grid(row=1, column=0, columnspan=2,
                                                                               sticky="w")
        self.formula_entry.grid(row=1, column=2, columnspan=2)

        self.a_entry = ttk.Entry(self.root, width=10)
        self.b_entry = ttk.Entry(self.root, width=10)
        self.step_entry = ttk.Entry(self.root, width=10)

        ttk.Label(self.root, text="Интервал от:").grid(row=2, column=0, sticky="w")
        self.a_entry.grid(row=2, column=1)
        ttk.Label(self.root, text="до:").grid(row=2, column=2, sticky="e")
        self.b_entry.grid(row=2, column=3)

        ttk.Label(self.root, text="Шаг:").grid(row=3, column=0, sticky="w")
        self.step_entry.grid(row=3, column=1)

        self.x_entry = ttk.Entry(self.root, width=40)
        self.y_entry = ttk.Entry(self.root, width=40)
        ttk.Label(self.root, text="x (через пробел):").grid(row=4, column=0, columnspan=2, sticky="w")
        self.x_entry.grid(row=4, column=2, columnspan=2)
        ttk.Label(self.root, text="y (через пробел):").grid(row=5, column=0, columnspan=2, sticky="w")
        self.y_entry.grid(row=5, column=2, columnspan=2)
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=6, column=0, columnspan=4, pady=10)

        plot_btn = ttk.Button(button_frame, text="Построить график", command=self.plot)
        plot_btn.pack(side=tk.LEFT, padx=10)

        help_btn = ttk.Button(button_frame, text="Справка", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=10)

        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=5)

        self.toggle_mode()

    def toggle_mode(self):
        mode = self.mode.get()
        state_formula = "normal" if mode == "formula" else "disabled"
        state_table = "normal" if mode == "table" else "disabled"

        for widget in [self.formula_entry, self.a_entry, self.b_entry, self.step_entry]:
            widget.configure(state=state_formula)
        for widget in [self.x_entry, self.y_entry]:
            widget.configure(state=state_table)

    def show_help(self):
        help_text = (
            "📘 Справка по вводу функции\n\n"
            "Вы можете ввести математическое выражение от переменной x.\n"
            "Программа построит график функции на указанном интервале с заданным шагом.\n\n"

            "✅ Поддерживаемые операции:\n"
            "  +   — сложение (пример: x + 2)\n"
            "  -   — вычитание (пример: x - 1)\n"
            "  *   — умножение (пример: 2 * x)\n"
            "  /   — деление (пример: x / 3)\n"
            "  **  — возведение в степень (пример: x**2)\n\n"

            "✅ Поддерживаемые математические функции (из sympy/numpy):\n"
            "  sin(x)   — синус\n"
            "  cos(x)   — косинус\n"
            "  tan(x)   — тангенс\n"
            "  log(x)   — натуральный логарифм\n"
            "  exp(x)   — экспонента (e^x)\n"
            "  sqrt(x)  — квадратный корень\n\n"

            "🧠 Особенности:\n"
            "• Переменная должна называться именно 'x'\n"
            "• Дробные числа вводятся через точку (пример: 6.6)\n"
            "• Вместо ^ используйте ** (пример: x**2, а не x^2)\n"
            "• Если интервал и шаг не заданы, используются значения по умолчанию: от -10 до 10, шаг 0.1\n\n"

            "🔍 Пример корректной формулы:\n"
            "  sin(x) + log(x) + x**2\n\n"

            "📊 Табличный режим:\n"
            "• Введите значения x и y через пробел\n"
            "• Количество значений x и y должно совпадать\n"
            "• Пример:\n"
            "    x: -2 -1 0 1 2\n"
            "    y:  4  1 0 1 4\n"
        )

        messagebox.showinfo("Справка по формулам", help_text)

    def plot(self):
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        try:
            if self.mode.get() == "formula":
                expr_text = self.formula_entry.get()
                a_text = self.a_entry.get().strip()
                b_text = self.b_entry.get().strip()
                step_text = self.step_entry.get().strip()

                a = float(a_text) if a_text else -10
                b = float(b_text) if b_text else 10
                step = float(step_text) if step_text else 0.1

                if step <= 0 or a >= b:
                    raise ValueError("Неверные значения интервала или шага.")

                x_sym = sp.Symbol('x')
                try:
                    expr_sym = sp.sympify(expr_text, evaluate=False)
                except Exception as e:
                    raise ValueError(f"Ошибка в формуле: {e}")

                f_np = sp.lambdify(x_sym, expr_sym, modules=["numpy"])

                num_points = int((b - a) / step) + 1
                x_vals = np.linspace(a, b, num_points)
                y_vals = f_np(x_vals)

                x_vals = np.array(x_vals)
                y_vals = np.array(y_vals)

                # Найдём участки, где значения допустимы
                mask = np.isfinite(y_vals)

                # Разбиваем по непрерывным отрезкам
                if not np.any(mask):
                    raise ValueError("Функция не определена на всём интервале.")

                start = 0
                while start < len(x_vals):
                    while start < len(x_vals) and not mask[start]:
                        start += 1
                    end = start
                    while end < len(x_vals) and mask[end]:
                        end += 1
                    if start < end:
                        ax.plot(x_vals[start:end], y_vals[start:end], linestyle='-', label=expr_text)
                    start = end

            else:
                x_vals = list(map(float, self.x_entry.get().split()))
                y_vals = list(map(float, self.y_entry.get().split()))
                if len(x_vals) != len(y_vals):
                    raise ValueError("Количество значений x и y должно совпадать.")
                ax.plot(x_vals, y_vals, marker='o', linestyle='-')

            ax.set_title("График функции")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.grid(True)
            ax.legend()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график:\n\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FunctionPlotter(root)
    root.mainloop()

