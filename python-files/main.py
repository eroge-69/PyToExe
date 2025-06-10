import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
import itertools
import csv
import threading
import pendulum
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import differential_evolution
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sympy import simplify, symbols, sympify

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def simplify_expression(expr_str):
    x = symbols('x')
    expr = sympify(expr_str)  # Преобразование строки в символьное выражение
    simplified = simplify(expr)  # Упрощение
    return str(simplified)  # Возврат в виде строки


class MyTextbox(ctk.CTkTextbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Привязываем комбинации клавиш
        self.bind("<Control-c>", self.copy_text)
        self.bind("<Control-x>", self.cut_text)
        self.bind("<Control-v>", self.paste_text)

    def copy_text(self, event=None):
        try:
            selected_text = self.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass
        return "break"

    def cut_text(self, event=None):
        try:
            selected_text = self.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(selected_text)
            self.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        return "break"

    def paste_text(self, event=None):
        try:
            text = self.clipboard_get()
            self.insert("insert", text)
        except tk.TclError:
            pass
        return "break"


class FunctionApproximationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Аппроксимация ряда")

        # Настройка сетки
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Левая панель настроек
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        self.settings_frame.grid_propagate(False)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Правая панель результатов
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        self.results_frame.grid_rowconfigure(2, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Создание элементов интерфейса
        self.create_settings_panel()
        self.create_results_panel()

    # region settings_panel
    def create_settings_panel(self):
        # Заголовок
        self._create_settings_header()

        # Поля ввода параметров
        self._create_input_fields()

        # Выбор функций
        self._create_function_selection()

        # Кнопки управления
        self._create_control_buttons()

    def _create_settings_header(self):
        ctk.CTkLabel(
            self.settings_frame,
            text="Параметры аппроксимации",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=10, pady=(10, 0))

    def _create_input_fields(self):
        input_frame = ctk.CTkFrame(self.settings_frame)
        input_frame.pack(padx=10, pady=(10, 0), fill="x")

        # Словарь с параметрами для полей ввода
        input_params = {
            "Размер тренировочной выборки:": ("20", "train_size_entry"),
            "Размер тестовой выборки:": ("20", "test_size_entry"),
            "Граница параметров:": ("10000", "bound_magnitude_entry"),
            "Глубина вложенности:": ("2", "nesting_depth_entry"),
            "Количество слагаемых": ("1", "count_terms_entry")
        }

        # Создание полей ввода
        for i, (label_text, (default_value, attr_name)) in enumerate(input_params.items()):
            ctk.CTkLabel(input_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ctk.CTkEntry(input_frame, width=50)
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, sticky="e", padx=(0, 5), pady=5)
            setattr(self, attr_name, entry)

    def _create_function_selection(self):
        func_frame = ctk.CTkFrame(self.settings_frame)
        func_frame.pack(pady=(10, 0), padx=10, fill="x")

        # Создаем группы функций
        self.binary_ops = {
            "plus_var": "+",
            "mult_var": "*",
            "div_var": "/",
            "div2_var": "//",
            "pow_var": "**",
            "mod_var": "%"
        }
        self._create_function_group(func_frame, "Бинарные операции", self.binary_ops)

        self.trig_funcs = {
            "sin_var": "sin",
            "cos_var": "cos",
            "tan_var": "tan",
            "asin_var": "asin",
            "acos_var": "acos",
            "atan_var": "atan",
            "atan2_var": "atan2"
        }
        self._create_function_group(func_frame, "Тригонометрические функции", self.trig_funcs)

        self.hyperbolic_funcs = {
            "sinh_var": "sinh",
            "cosh_var": "cosh",
            "tanh_var": "tanh",
            "asinh_var": "asinh",
            "acosh_var": "acosh",
            "atanh_var": "atanh"
        }
        self._create_function_group(func_frame, "Гиперболические функции", self.hyperbolic_funcs)

        self.exp_log_funcs = {
            "exp_var": "exp",
            "log_var": "log",
            "log10_var": "log10",
            "log2_var": "log2",
            "sqrt_var": "sqrt"
        }
        self._create_function_group(func_frame, "Экспонента, корень и логарифмы", self.exp_log_funcs)

        self.rounding_funcs = {
            "ceil_var": "ceil",
            "floor_var": "floor",
            "trunc_var": "trunc",
            "round_var": "round",
            "abs_var": "abs"
        }
        self._create_function_group(func_frame, "Округление и модуль", self.rounding_funcs)

    def _create_function_group(self, parent, title, functions):
        # Создаем основной фрейм группы
        group_frame = ctk.CTkFrame(parent)
        group_frame.pack(fill="x", padx=5, pady=5)

        # Фрейм для заголовка группы
        header_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)

        # Чекбокс для выбора всей группы
        group_var = ctk.StringVar(value="on")
        group_check = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=group_var,
            onvalue="on",
            offvalue="off",
            width=20,
            command=lambda: self._toggle_all_functions(functions, group_var)
        )
        group_check.pack(side="left", padx=(5, 0))

        # Кнопка для раскрытия/скрытия группы
        expand_btn = ctk.CTkButton(
            header_frame,
            text=title + " ▲",
            width=120,
            height=25,
            fg_color="transparent",
            hover_color=("#EEEEEE", "#333333"),
            command=lambda: self._toggle_group_content(content_frame, expand_btn)
        )
        expand_btn.pack(side="left", padx=(0, 5))

        # Фрейм для содержимого группы (изначально видим)
        content_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=5, pady=2)

        # Добавляем отступ для древовидного вида
        indent_frame = ctk.CTkFrame(content_frame, width=35, height=1, fg_color="transparent")
        indent_frame.pack(side="left", fill="y")

        # Фрейм для чекбоксов функций
        functions_frame = ctk.CTkFrame(content_frame)
        functions_frame.pack(side="left", fill="x", expand=True)

        # Сохраняем переменные группы для управления состоянием
        group_vars = {}

        # Добавляем чекбоксы для функций
        for var_name, symbol in functions.items():
            var = ctk.StringVar(value="on")
            setattr(self, var_name, var)
            group_vars[var_name] = var

            # Фрейм для одного чекбокса (для выравнивания)
            cb_frame = ctk.CTkFrame(functions_frame, fg_color="transparent")
            cb_frame.pack(fill="x", pady=2)

            ctk.CTkCheckBox(
                cb_frame,
                text=symbol,
                variable=var,
                onvalue="on",
                offvalue="off"
            ).pack(side="left")

        # Сохраняем ссылки для управления группой
        setattr(self, f"{title.replace(' ', '_').lower()}_vars", group_vars)
        setattr(self, f"{title.replace(' ', '_').lower()}_group_var", group_var)

    def _toggle_group_content(self, content_frame, button):
        if content_frame.winfo_viewable():
            content_frame.pack_forget()
            sigh = "▼"
        else:
            content_frame.pack(fill="x", padx=0, pady=(0, 5))
            sigh = "▲"
        button.configure(text=f"{button.cget('text').replace(' ▼', '').replace(' ▲', '')} {sigh}")

    def _toggle_all_functions(self, functions, group_var):
        state = group_var.get()
        for var_name in functions.keys():
            var = getattr(self, var_name)
            var.set(state)

    def _create_control_buttons(self):
        button_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        button_frame.pack(pady=(5, 0), padx=10, fill="x")

        self.load_btn = ctk.CTkButton(
            button_frame,
            text="Загрузить CSV",
            command=self.load_csv
        )
        self.load_btn.pack(pady=5, fill="x")

        self.train_btn = ctk.CTkButton(
            button_frame,
            text="Запустить обучение",
            command=self.start_training,
            state="disabled"
        )
        self.train_btn.pack(pady=5, fill="x")

    # endregion

    # region results_panel
    def create_results_panel(self):
        # Текстовое поле для функции
        self._create_function_display()

        # Прогресс-бар
        self._create_progress_bar()

        # Область для графика
        self._create_plot_area()

        # Информация об ошибке
        # self._create_error_label()

    def _create_function_display(self):
        func_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        func_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        func_frame.grid_columnconfigure(0, weight=1)

        self.function_label = ctk.CTkLabel(
            func_frame,
            text="Итоговая функция:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.function_label.pack(anchor="w")

        self.function_text = MyTextbox(func_frame, height=100)
        self.function_text.pack(fill="x", pady=(10, 0))
        self.function_text.insert("1.0", "Функция будет отображена после обучения")

    def _create_progress_bar(self):
        progress_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        progress_frame.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack()

    def _create_plot_area(self):
        plot_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        plot_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        plot_frame.grid_columnconfigure(0, weight=1)
        plot_frame.grid_rowconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    # endregion

    def load_csv(self):
        file_path = ctk.filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self.data, self.time = [], []
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row[1] == 'None':
                        continue

                    time, value = map(float, row)
                    self.time.append(time)
                    self.data.append(value)

            self.data = np.array(self.data)
            self.time = np.array(self.time)

            ctk.CTkLabel(self.settings_frame, text=f"Загружено {len(self.data)} точек",
                         text_color="green").pack(pady=5)
            self.train_btn.configure(state="normal")  # Активируем кнопку обучения
            self.plot_results()  # Строим график после загрузки данных
        except Exception as e:
            ctk.CTkLabel(self.settings_frame, text=f"Ошибка загрузки: {str(e)}",
                         text_color="red").pack(pady=5)

    def start_training(self):
        # Получение параметров из интерфейса
        try:
            self.TRAIN_SIZE = int(self.train_size_entry.get())
            self.TEST_SIZE = int(self.test_size_entry.get())
            self.BOUND_MAGNITUDE = float(self.bound_magnitude_entry.get())
            self.NESTING_DEPTH = int(self.nesting_depth_entry.get())
            self.COUNT_TERMS = int(self.count_terms_entry.get())

        except ValueError:
            ctk.CTkLabel(self.settings_frame, text="Некорректные параметры!",
                         text_color="red").pack(pady=5)
            return

        # Сбор выбранных операций
        self.BINARY_OPS = []
        for op in self.binary_ops:
            if getattr(self, op).get() == "on":
                self.BINARY_OPS.append(self.binary_ops[op])

        self.UNARY_FUNCS = []
        for type in [self.trig_funcs, self.hyperbolic_funcs, self.exp_log_funcs, self.rounding_funcs]:
            for func in type:
                if getattr(self, func).get() == "on":
                    self.UNARY_FUNCS.append("C*np." + type[func])

        # Запуск обучения в отдельном потоке
        threading.Thread(target=self.train_model).start()

        self.train_btn.configure(state="disabled", text="Обучение...")

    def generate_functions(self, n=None):
        if n is None:
            n = self.NESTING_DEPTH
        if n < 1:
            return {}
        if n == 1:
            return {'C*x', 'C'}

        prev_funcs = self.generate_functions(n - 1)
        current_funcs = set()

        for func1, func2 in itertools.product(prev_funcs, repeat=2):
            for op in self.BINARY_OPS:
                current_funcs.add(f"({func1}){op}({func2})")

        for func in prev_funcs:
            for u_func in self.UNARY_FUNCS:
                current_funcs.add(f"{u_func}({func})")

        current_funcs.update(prev_funcs)
        return current_funcs

    def train_model(self):
        # Подготовка данных
        x_train = self.time[:self.TRAIN_SIZE]
        y_train = self.data[:self.TRAIN_SIZE]

        # Обработка пропущенных значений
        mask_train = y_train != 0
        x_train = x_train[mask_train]
        y_train = y_train[mask_train]

        x_test = self.time[:self.TRAIN_SIZE + self.TEST_SIZE]
        y_test = self.data[:self.TRAIN_SIZE + self.TEST_SIZE]

        # Обработка пропущенных значений в тестовой выборке
        mask_test = y_test != 0
        x_test = x_test[mask_test]
        y_test = y_test[mask_test]

        # Инициализация лучшей модели
        self.best_f = 'params[0]+x*0'
        self.best_params = [0]

        # Расчет ошибки лучшей модели
        num_params = self.best_f.count('params[')
        y_pred_test = eval(self.best_f, {'x': x_test, 'params': self.best_params, 'np': np})
        if isinstance(y_pred_test, int):
            y_pred_test = np.array([y_pred_test] * len(x_test))
        self.best_error = mean_squared_error(y_test, y_pred_test)

        # Генерация кандидатных функций
        candidate_funcs = self.generate_functions()
        total_funcs = len(candidate_funcs) * self.COUNT_TERMS

        start, N = pendulum.now(), 0
        # Процесс обучения
        for _ in range(self.COUNT_TERMS):
            simplified_f = self.best_f
            num_params = simplified_f.count('params[')
            for i in range(num_params):
                simplified_f = simplified_f.replace(f'params[{i}]', 'C')

            for func_expr in candidate_funcs:
                # Создание расширенной функции
                extended_func = func_expr + f'+{simplified_f}'
                num_constants = extended_func.count('C')

                # Подготовка параметризованной функции
                param_func = ""
                param_idx = 0
                for char in extended_func:
                    if char == 'C':
                        param_func += f'params[{param_idx}]'
                        param_idx += 1
                    else:
                        param_func += char

                # Оптимизация параметров
                bounds = [(-self.BOUND_MAGNITUDE, self.BOUND_MAGNITUDE)] * num_constants

                train_error_func = lambda params: mean_squared_error(
                    y_train,
                    eval(param_func, {'x': x_train, 'params': params, 'np': np})
                )

                try:
                    optimized_params = differential_evolution(
                        train_error_func,
                        bounds,
                        maxiter=1000
                    ).x

                    # Оценка на тестовых данных
                    test_error_func = lambda params: mean_squared_error(
                        y_test,
                        eval(param_func, {'x': x_test, 'params': params, 'np': np})
                    )

                    current_error = test_error_func(optimized_params)

                    # Проверка на улучшение
                    if current_error < self.best_error:
                        # Обновление лучшей модели
                        self.best_f = param_func
                        self.best_params = optimized_params
                        self.best_error = current_error

                        y_pred_test = eval(self.best_f, {'x': x_test, 'params': self.best_params, 'np': np})
                        errors = [current_error, mean_absolute_percentage_error(y_test, y_pred_test)]

                        # Обновление интерфейса
                        display_f = param_func
                        for j in range(len(optimized_params)):
                            display_f = display_f.replace(f'params[{j}]', f'{optimized_params[j]:.2f}')
                        self.after(0, self.update_results, simplify_expression(display_f.replace('np.', '')), errors)
                except Exception as e:
                    print(f'{param_func}: {e}')

                # Обновление прогресс-бара
                N += 1
                progress = N / total_funcs
                remaining_time = ((pendulum.now() - start) / N) * (total_funcs - N)
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda t=total_funcs: self.progress_label.configure(
                    text=f"Обработка функции {N} из {t} ({remaining_time})"
                ))

        # Обновление интерфейса после завершения обучения
        self.after(0, lambda: self.train_btn.configure(state="normal", text="Запустить обучение"))
        self.after(0, lambda: self.progress_label.configure(text="Обучение завершено"))

    def update_results(self, func_str, errors):
        self.function_text.delete("1.0", "end")
        self.function_text.insert("1.0", func_str)
        self.function_label.configure(text=f"Итоговая функция: MSE={errors[0]:.2f}, MAPE={errors[1] * 100:.2f}%")
        self.plot_results()  # Строим график при обновлении результатов

    def plot_results(self):
        self.ax.clear()
        x = np.array(self.time)
        self.ax.plot(x, self.data, label='Данные')
        self.ax.fill_between(x, self.data * 0.9, self.data * 1.1, alpha=0.2)

        if hasattr(self, 'TRAIN_SIZE'):
            self.ax.axvline(self.TRAIN_SIZE + self.TEST_SIZE + 0.5, color='grey', linestyle=':')

        if hasattr(self, 'best_f'):
            x_pred = np.arange(self.time[0], self.time[-1] + 20 + 1)
            y_pred = eval(
                self.best_f,
                {'x': x_pred, 'params': self.best_params, 'np': np}
            )
            if isinstance(y_pred, int) or isinstance(y_pred, float):
                y_pred = np.array([y_pred] * len(x))
            self.ax.plot(x_pred, y_pred, '--', label='Аппроксимация')

        self.ax.set_xlabel('Дни')
        self.ax.set_ylabel('Значение')
        self.ax.grid(True, alpha=0.2)
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = FunctionApproximationApp()
    app.mainloop()
