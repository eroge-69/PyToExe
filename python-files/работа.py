import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
from decimal import Decimal, getcontext

# Устанавливаем точность для decimal (количество знаков после запятой)
getcontext().prec = 50  # Увеличиваем точность

class RootCalculator:
    def __init__(self, root):
        self.root = root
        root.title("Вычисление корня ª√b")

        # Ввод a
        a_label = ttk.Label(root, text="Введите a (степень корня):")
        a_label.pack()
        self.a_entry = ttk.Entry(root)
        self.a_entry.pack()

        # Ввод b
        b_label = ttk.Label(root, text="Введите b (число под корнем):")
        b_label.pack()
        self.b_entry = ttk.Entry(root)
        self.b_entry.pack()

        # Кнопка
        calculate_button = ttk.Button(root, text="Вычислить", command=self.calculate_root)
        calculate_button.pack()

        # Результат методом половинного деления
        self.bisection_result_label = ttk.Label(self.root, text="")
        self.bisection_result_label.pack()

        # Результат методом Ньютона
        self.newton_result_label = ttk.Label(self.root, text="")
        self.newton_result_label.pack()

    def calculate_root(self):
        a_str = self.a_entry.get()
        b_str = self.b_entry.get()

        # Проверяем, что a и b - числа
        try:
            a = Decimal(a_str)
            b = Decimal(b_str)
        except ValueError as e:
            self.bisection_result_label.config(text=f"Ошибка: a и b должны быть числами: {e}")
            self.newton_result_label.config(text="")
            return

        # Добавляем проверку на a и b
        if a <= 0:
            self.bisection_result_label.config(text="Ошибка: Степень корня (a) должна быть положительным числом.")
            self.newton_result_label.config(text="")
            return
        if b < 0 and (a % 2 == 0):  # Проверка на четность
            self.bisection_result_label.config(text="Ошибка: Отрицательное число под корнем не может быть возведено в четную степень.")
            self.newton_result_label.config(text="")
            return

        try:
            result_bisection, result_newton = self.try_automatic_calculation()
            self.bisection_result_label.config(text=f"Метод половинного деления: {result_bisection}")
            self.newton_result_label.config(text=f"Метод Ньютона: {result_newton}")

            # Проверяем результаты и спрашиваем пользователя, если нужно
            if isinstance(result_bisection, str) or isinstance(result_newton, str):
                if isinstance(result_bisection, str) and isinstance(result_newton, str):
                    message = (
                        "Оба метода не смогли найти корень при автоматическом расчете.\n"
                        "Попробовать пересчитать вручную?"
                    )
                elif isinstance(result_bisection, str):
                    message = (
                        "Метод половинного деления не смог найти корень при автоматическом расчете.\n"
                        "Попробовать пересчитать вручную?"
                    )
                else:  # isinstance(result_newton, str)
                    message = (
                        "Метод Ньютона не смог найти корень при автоматическом расчете.\n"
                        "Попробовать пересчитать вручную?"
                    )

                if messagebox.askyesno("Ручной ввод", message):
                    self.open_manual_input_window(a, b)

        except (ValueError, OverflowError) as e:
            # Обрабатываем системные ошибки
            self.bisection_result_label.config(text=f"Ошибка: {e}")
            self.newton_result_label.config(text="")
        except Exception as e:
            # Другие ошибки
            self.bisection_result_label.config(text=f"Неизвестная ошибка: {e}")
            self.newton_result_label.config(text="")

    def try_automatic_calculation(self):
        a_str = self.a_entry.get()
        b_str = self.b_entry.get()

        # Проверяем, что a и b - числа
        try:
            a = Decimal(a_str)
            b = Decimal(b_str)
        except ValueError as e:
            raise ValueError(f"a и b должны быть числами: {e}")
        except Exception as e:
            raise Exception(f"Неизвестная ошибка: {e}")

        # Добавляем проверку на a (чтобы избежать деления на ноль)
        if a <= 0:
            raise ValueError("Степень корня (a) должна быть положительным числом.")
        if b < 0 and (a % 2 != 1):  # Проверяем, что если степень нечётная и число под корнем отрицательное
            return "Ошибка, не получается посчитать выражение автоматически", ""  

        tolerance = Decimal("0.001")
        # Функция для вычисления значения b**(1/a) (корень степени a из b)
        def f(x):
            return x**a - b  # Не используется в bisection и newton, но оставлено для ясности.

        # Метод половинного деления (с автоматическим выбором интервала)
        def bisection(f, tolerance, max_iterations=100):
            # Попытка автоматического выбора интервала
            if b == 0:
                return Decimal(0)
            if a == 1:
                return b

            x_est = Decimal(1)  # Начальная оценка корня
            a_interval = Decimal(0) if b > 0 else Decimal(-1)  # Начальный интервал
            b_interval = max(b, Decimal(1)) if b > 0 else Decimal(0)
            # Увеличиваем интервал, пока знаки f(a) и f(b) не станут разными
            for _ in range(10):  # Уменьшили количество итераций, чтобы избежать зацикливания
                try:
                    if (a_interval**a - b) * (b_interval**a - b) < 0:
                        break
                    else:
                        if (a_interval**a - b) > 0:  # Расширяем интервал более агрессивно
                            b_interval *= 10
                        else:
                            a_interval /= 10
                except OverflowError as e:
                    raise OverflowError(f"Переполнение в bisection: {e}")  # Пробрасываем ошибку

            # Проверяем, удалось ли найти интервал
            if (a_interval**a - b) * (b_interval**a - b) >= 0:
                return "Не удалось автоматически выбрать интервал"
            # Алгоритм метода бисекции
            a_val = a_interval
            b_val = b_interval

            for _ in range(max_iterations):
                try:
                    c = (a_val + b_val) / 2
                    if abs(b_val - a_val) < tolerance:
                        return c.quantize(Decimal("0.001"))  # Округляем результат
                    if (c**a - b) * (a_val**a - b) < 0:
                        b_val = c
                    else:
                        a_val = c
                except OverflowError as e:
                    raise OverflowError(f"Переполнение в bisection: {e}")  # Пробрасываем ошибку
            return f"Метод не сошелся (после {max_iterations} итераций)"

        # Метод Ньютона (с автоматическим выбором начального приближения)
        def newton(f, tolerance, max_iterations=100):  
            # Используем метод половинного деления для получения начального приближения
            initial_guess = bisection(f, tolerance, max_iterations=100)  
            # Проверяем, что бисекция вернула нам оценку корня, а не ошибку
            if isinstance(initial_guess, str):
                return initial_guess  # Пробрасываем ошибку из Bisection

            x = initial_guess  # Начальное приближение
            # Немного модифицируем начальное приближение
            x = x * Decimal("1.0001")  # Небольшой сдвиг

            for i in range(max_iterations):
                try:
                    h = Decimal("1e-6")
                    derivative = a * (x**(a - 1))
                    if abs(derivative) < Decimal("1e-8"):
                        return "Производная близка к нулю"
                    x_new = x - (x**a - b) / derivative
                    if abs(x_new - x) < tolerance:
                        return x_new.quantize(Decimal("0.001"))  # Округляем результат
                    x = x_new
                except OverflowError as e:
                    raise OverflowError(f"Переполнение в newton: {e}")  # Пробрасываем ошибку
            return f"Метод не сошелся (после {max_iterations} итераций)"

        # Вычисление корня методом половинного деления (без интервала)
        root_bisection = bisection(f, tolerance)

        # Вычисление корня методом Ньютона (без начального приближения)
        root_newton = newton(f, tolerance)

        return root_bisection, root_newton

    def open_manual_input_window(self, a, b):
        self.manual_window = tk.Toplevel(self.root)
        self.manual_window.title("Ручной ввод параметров")

        # a и b не редактируются
        a_manual_label = ttk.Label(self.manual_window, text="a (степень корня):")
        a_manual_label.grid(row=0, column=0, padx=5, pady=5)
        self.a_manual_entry = ttk.Entry(self.manual_window)
        self.a_manual_entry.grid(row=0, column=1, padx=5, pady=5)
        self.a_manual_entry.insert(0, str(a))  # Отображаем a
        self.a_manual_entry.config(state="disabled")  # Запрещаем редактирование

        b_manual_label = ttk.Label(self.manual_window, text="b (число под корнем):")
        b_manual_label.grid(row=1, column=0, padx=5, pady=5)
        self.b_manual_entry = ttk.Entry(self.manual_window)
        self.b_manual_entry.grid(row=1, column=1, padx=5, pady=5)
        self.b_manual_entry.insert(0, str(b))  # Отображаем b
        self.b_manual_entry.config(state="disabled")  # Запрещаем редактирование

        # Ввод начала интервала (для ручного ввода)
        a_interval_manual_label = ttk.Label(self.manual_window, text="Начало интервала:")
        a_interval_manual_label.grid(row=2, column=0, padx=5, pady=5)
        self.a_interval_manual_entry = ttk.Entry(self.manual_window)
        self.a_interval_manual_entry.grid(row=2, column=1, padx=5, pady=5)

        # Ввод конца интервала (для ручного ввода)
        b_interval_manual_label = ttk.Label(self.manual_window, text="Конец интервала:")
        b_interval_manual_label.grid(row=3, column=0, padx=5, pady=5)
        self.b_interval_manual_entry = ttk.Entry(self.manual_window)
        self.b_interval_manual_entry.grid(row=3, column=1, padx=5, pady=5)

        # Ввод начального приближения (для ручного ввода)
        x0_manual_label = ttk.Label(self.manual_window, text="Начальное приближение:")
        x0_manual_label.grid(row=4, column=0, padx=5, pady=5)
        self.x0_manual_entry = ttk.Entry(self.manual_window)
        self.x0_manual_entry.grid(row=4, column=1, padx=5, pady=5)

        # Кнопка "Вычислить вручную"
        calculate_manual_button = ttk.Button(self.manual_window, text="Вычислить вручную", command=self.calculate_manually)
        calculate_manual_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Метки для отображения результатов (в ручном режиме)
        self.bisection_result_manual_label = ttk.Label(self.manual_window, text="")
        self.bisection_result_manual_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        self.newton_result_manual_label = ttk.Label(self.manual_window, text="")
        self.newton_result_manual_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def calculate_manually(self):
        try:
            # Получаем значения из полей ввода. a и b берем из self.a_entry и self.b_entry
            a_interval_start_str = self.a_interval_manual_entry.get()
            b_interval_end_str = self.b_interval_manual_entry.get()
            x0_str = self.x0_manual_entry.get()

            # Проверяем, что все значения - числа
            try:
                a_val = Decimal(self.a_entry.get())  # Переименовали локальную переменную a
                b_val = Decimal(self.b_entry.get())  # Переименовали локальную переменную b
                a_interval_start = Decimal(a_interval_start_str)
                a_interval_end = Decimal(b_interval_end_str)
                x0 = Decimal(x0_str)
            except ValueError:
                raise ValueError("Все введенные значения должны быть числами")

            # Дополнительная валидация
            if a_interval_start >= a_interval_end:
                raise ValueError("Начало интервала должно быть меньше конца интервала")
            if a_val <= 0:  # Используем переименованную переменную a_val
                raise ValueError("Степень корня (a) должна быть положительным числом.")
            if b_val < 0 and (a_val % 2 == 0):  # Используем переименованную переменную b_val и используем a_val
                raise ValueError("Отрицательное число под корнем не может быть возведено в четную степень.")

            tolerance = Decimal("0.001")
            # Функция для вычисления значения b**(1/a) (корень степени a из b)
            def f(x):
                return x**a_val - b_val  # Используем a_val и b_val

            # Метод половинного деления (с ручным интервалом)
            def bisection(f, a_interval_start, b_interval_end, tolerance, max_iterations=100):
                a_local = a_interval_start  # переименовали переменную a
                b_local = b_interval_end  # переименовали переменную b
                if f(a_local) * f(b_local) >= 0:  # Проверка наличия корня
                    return "На данном интервале нет корня или их четное число"
                for _ in range(max_iterations):
                    c = (a_local + b_local) / 2
                    if abs(b_local - a_local) < tolerance:
                        return c.quantize(Decimal("0.001"))  # Округляем результат
                    if (c**a_val - b_val) * (a_local**a_val - b_val) < 0:  # Используем a_val и b_val
                        b_local = c
                    else:
                        a_local = c
                return f"Метод не сошелся (после {max_iterations} итераций)"

            # Метод Ньютона (с ручным начальным приближением)
            def newton(f, x0, tolerance, max_iterations=1000):  
                x = x0
                for i in range(max_iterations):
                    h = Decimal("1e-6")
                    derivative = a_val * (x**(a_val - 1))
                    if abs(derivative) < Decimal("1e-8"):
                        return "Производная близка к нулю"
                    x_new = x - (x**a_val - b_val) / derivative
                    if abs(x_new - x) < tolerance:
                        return x_new.quantize(Decimal("0.001"))  # Округляем результат
                    x = x_new
                return f"Метод не сошелся (после {max_iterations} итераций)"

            # Вычисление корня методом половинного деления (с ручным интервалом)
            root_bisection = bisection(f, a_interval_start, a_interval_end, tolerance)

            # Вычисление корня методом Ньютона (с ручным начальным приближением)
            root_newton = newton(f, x0, tolerance)

            # Вывод результатов (в ручном режиме)
            self.bisection_result_manual_label.config(text=f"Метод половинного деления: {root_bisection}")
            self.newton_result_manual_label.config(text=f"Метод Ньютона: {root_newton}")

        except ValueError as ve:
            self.bisection_result_manual_label.config(text=f"Ошибка: {ve}")
            self.newton_result_manual_label.config(text="")
        except Exception as e:
            self.bisection_result_manual_label.config(text=f"Ошибка: {e}")
            self.newton_result_manual_label.config(text="")

# Запуск приложения
root = tk.Tk()
calculator = RootCalculator(root)
root.mainloop()