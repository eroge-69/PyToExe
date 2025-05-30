import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
from collections import defaultdict

# Цвета оформления
BG_PINK = '#ffe6f0'  # очень нежный розовый
FG_TEXT = '#333333'  # тёмно-серый
BTN_PINK = '#ffd1e6' # чуть более насыщенный розовый для кнопок
ENTRY_BG = '#fff6fa' # почти белый с розовым оттенком

def initial_moment(values, probabilities, k):
    return sum((v ** k) * p for v, p in zip(values, probabilities))

def central_moment(values, probabilities, mean, k):
    return sum(((v - mean) ** k) * p for v, p in zip(values, probabilities))

def create_distribution_series(values, probabilities):
    distribution = defaultdict(float)
    for v, p in zip(values, probabilities):
        distribution[v] += p
    return dict(distribution)

def add_distributions(dist1, dist2):
    result = defaultdict(float)
    for x1, p1 in dist1.items():
        for x2, p2 in dist2.items():
            result[x1 + x2] += p1 * p2
    return dict(result)

def subtract_distributions(dist1, dist2):
    result = defaultdict(float)
    for x1, p1 in dist1.items():
        for x2, p2 in dist2.items():
            result[x1 - x2] += p1 * p2
    return dict(result)

def multiply_distributions(dist1, dist2):
    result = defaultdict(float)
    for x1, p1 in dist1.items():
        for x2, p2 in dist2.items():
            result[x1 * x2] += p1 * p2
    return dict(result)

def multiply_by_constant(dist, constant):
    result = defaultdict(float)
    for x, p in dist.items():
        result[x * constant] = p
    return dict(result)

def distribution_stats(dist):
    values = list(dist.keys())
    probabilities = list(dist.values())
    MX = sum(x * px for x, px in zip(values, probabilities))
    MX2 = sum((x ** 2) * px for x, px in zip(values, probabilities))
    DX = MX2 - MX ** 2
    sigmaX = math.sqrt(DX) if DX >= 0 else 0
    muXc3 = central_moment(values, probabilities, MX, 3)
    muXc4 = central_moment(values, probabilities, MX, 4)
    skewX = muXc3 / (sigmaX ** 3) if sigmaX != 0 else 0
    kurtosisX = (muXc4 / (sigmaX ** 4)) - 3 if sigmaX != 0 else 0
    moments = [initial_moment(values, probabilities, k) for k in range(1, 5)]
    cmoments = [central_moment(values, probabilities, MX, k) for k in range(1, 5)]
    return {
        'mean': MX,
        'var': DX,
        'moments': moments,
        'cmoments': cmoments,
        'std': sigmaX,
        'skew': skewX,
        'kurt': kurtosisX
    }

# --- Графический интерфейс ---
class DistributionApp:
    def __init__(self, root):
        """Инициализация главного окна и всех переменных приложения."""
        self.root = root
        self.root.title("Анализ дискретных распределений")
        self.root.geometry("950x750")
        self.root.configure(bg=BG_PINK)
        self.setup_styles()
        self.create_widgets()
        self.X, self.Y, self.pX, self.pY = [], [], [], []
        self.distX, self.distY = {}, {}

    def setup_styles(self):
        """Настройка стилей для всех элементов интерфейса."""
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TFrame', background=BG_PINK)
        style.configure('TLabel', background=BG_PINK, foreground=FG_TEXT)
        style.configure('TButton', background=BTN_PINK, foreground=FG_TEXT)
        style.configure('TCombobox', fieldbackground=ENTRY_BG, background=ENTRY_BG)
        style.configure('Treeview', background=ENTRY_BG, fieldbackground=ENTRY_BG, foreground=FG_TEXT)
        style.map('TButton', background=[('active', BTN_PINK)])

    def create_widgets(self):
        """Создание всех виджетов главного окна: таблиц, кнопок, выпадающих списков и текстового поля для вывода результатов."""
        frame_tables = tk.Frame(self.root, bg=BG_PINK)
        frame_tables.pack(pady=10)
        self.frame_X, self.table_X = self.create_table(frame_tables, "X")
        self.frame_X.grid(row=0, column=0, padx=20)
        self.frame_Y, self.table_Y = self.create_table(frame_tables, "Y")
        self.frame_Y.grid(row=0, column=1, padx=20)

        frame_table_btns = tk.Frame(self.root, bg=BG_PINK)
        frame_table_btns.pack(pady=2)
        btns = [
            ("Добавить строку X", lambda: self.add_row(self.table_X)),
            ("Удалить строку X", lambda: self.delete_row(self.table_X)),
            ("Добавить строку Y", lambda: self.add_row(self.table_Y)),
            ("Удалить строку Y", lambda: self.delete_row(self.table_Y)),
            ("Сохранить данные", self.save_main_table)
        ]
        for text, cmd in btns:
            tk.Button(frame_table_btns, text=text, command=cmd, bg=BTN_PINK, fg=FG_TEXT, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        frame_select = tk.Frame(self.root, bg=BG_PINK)
        frame_select.pack(pady=5)
        tk.Label(frame_select, text="Выберите характеристику для вывода:", bg=BG_PINK, fg=FG_TEXT).pack(side=tk.LEFT)
        self.checks_list = [
            ("Вывести все", "all"),
            ("Математическое ожидание", "mean"),
            ("Дисперсия", "var"),
            ("Начальные моменты", "moments"),
            ("Центральные моменты", "cmoments"),
            ("Среднеквадратичное отклонение", "std"),
            ("Коэффициент асимметрии", "skew"),
            ("Коэффициент эксцесса", "kurt"),
        ]
        self.selected_char = tk.StringVar(value=self.checks_list[0][0])
        self.char_menu = ttk.Combobox(frame_select, textvariable=self.selected_char, values=[x[0] for x in self.checks_list], state="readonly", width=35)
        self.char_menu.pack(side=tk.LEFT, padx=10)
        self.char_menu.configure(background=ENTRY_BG)

        frame_btns = tk.Frame(self.root, bg=BG_PINK)
        frame_btns.pack(pady=10)
        tk.Button(frame_btns, text="Рассчитать характеристики", command=self.calculate_stats, bg=BTN_PINK, fg=FG_TEXT, relief=tk.FLAT, activebackground=BTN_PINK).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btns, text="Калькулятор распределений", command=self.open_calculator, bg=BTN_PINK, fg=FG_TEXT, relief=tk.FLAT, activebackground=BTN_PINK).pack(side=tk.LEFT, padx=10)

        self.stats_text = tk.Text(self.root, height=15, width=110, font=("Consolas", 10), bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        self.stats_text.pack(pady=10)

    def create_table(self, parent, name):
        """Создаёт таблицу с вертикальным скроллбаром для массива X или Y."""
        frame = tk.Frame(parent, bg=BG_PINK)
        tk.Label(frame, text=f"Случайная величина {name}", bg=BG_PINK, fg=FG_TEXT).pack()
        table_frame = tk.Frame(frame, bg=BG_PINK)
        table_frame.pack()
        table = ttk.Treeview(table_frame, columns=("val", "prob"), show="headings", height=8, style=f"{name}.Treeview")
        table.heading("val", text=f"{name}i")
        table.heading("prob", text=f"p{name}i")
        table.column("val", width=60, anchor=tk.CENTER)
        table.column("prob", width=80, anchor=tk.CENTER)
        yscroll = tk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=yscroll.set)
        table.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        table.bind('<Double-1>', lambda e, t=table: self.edit_cell_main(e, t))
        return frame, table

    def calculate_stats(self):
        """Вычисляет и выводит выбранные характеристики для массивов X и Y."""
        if not self.X or not self.Y:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте данные!")
            return
        MX = sum(x * px for x, px in zip(self.X, self.pX))
        MY = sum(y * py for y, py in zip(self.Y, self.pY))
        MX2 = sum((x ** 2) * px for x, px in zip(self.X, self.pX))
        MY2 = sum((y ** 2) * py for y, py in zip(self.Y, self.pY))
        DX = MX2 - MX ** 2
        DY = MY2 - MY ** 2
        sigmaX = math.sqrt(DX)
        sigmaY = math.sqrt(DY)
        muXc3 = central_moment(self.X, self.pX, MX, 3)
        muYc3 = central_moment(self.Y, self.pY, MY, 3)
        skewX = muXc3 / (sigmaX ** 3) if sigmaX != 0 else 0
        skewY = muYc3 / (sigmaY ** 3) if sigmaY != 0 else 0
        muXc4 = central_moment(self.X, self.pX, MX, 4)
        muYc4 = central_moment(self.Y, self.pY, MY, 4)
        kurtosisX = (muXc4 / (sigmaX ** 4)) - 3 if sigmaX != 0 else 0
        kurtosisY = (muYc4 / (sigmaY ** 4)) - 3 if sigmaY != 0 else 0
        text = ""
        char = self.selected_char.get()
        if char == "Вывести все":
            text += f"Математическое ожидание:\nM(X) = {MX:.4f}\nM(Y) = {MY:.4f}\n"
            text += f"\nДисперсия:\nD(X) = {DX:.4f}\nD(Y) = {DY:.4f}\n"
            text += "\nНачальные моменты:\n"
            for k in range(1, 5):
                muX = initial_moment(self.X, self.pX, k)
                muY = initial_moment(self.Y, self.pY, k)
                text += f"μ{k}(X) = {muX:.4f}\nμ{k}(Y) = {muY:.4f}\n"
            text += "\nЦентральные моменты:\n"
            for k in range(1, 5):
                muXc = central_moment(self.X, self.pX, MX, k)
                muYc = central_moment(self.Y, self.pY, MY, k)
                text += f"μ°{k}(X) = {muXc:.4f}\nμ°{k}(Y) = {muYc:.4f}\n"
            text += f"\nСреднеквадратичное отклонение:\nσ(X) = {sigmaX:.4f}\nσ(Y) = {sigmaY:.4f}\n"
            text += f"\nКоэффициент асимметрии:\nAs(X) = {skewX:.4f}\nAs(Y) = {skewY:.4f}\n"
            text += f"\nКоэффициент эксцесса:\nEx(X) = {kurtosisX:.4f}\nEx(Y) = {kurtosisY:.4f}\n"
        elif char == "Математическое ожидание":
            text += f"Математическое ожидание:\nM(X) = {MX:.4f}\nM(Y) = {MY:.4f}\n"
        elif char == "Дисперсия":
            text += f"Дисперсия:\nD(X) = {DX:.4f}\nD(Y) = {DY:.4f}\n"
        elif char == "Начальные моменты":
            text += "Начальные моменты:\n"
            for k in range(1, 5):
                muX = initial_moment(self.X, self.pX, k)
                muY = initial_moment(self.Y, self.pY, k)
                text += f"μ{k}(X) = {muX:.4f}\nμ{k}(Y) = {muY:.4f}\n"
        elif char == "Центральные моменты":
            text += "Центральные моменты:\n"
            for k in range(1, 5):
                muXc = central_moment(self.X, self.pX, MX, k)
                muYc = central_moment(self.Y, self.pY, MY, k)
                text += f"μ°{k}(X) = {muXc:.4f}\nμ°{k}(Y) = {muYc:.4f}\n"
        elif char == "Среднеквадратичное отклонение":
            text += f"Среднеквадратичное отклонение:\nσ(X) = {sigmaX:.4f}\nσ(Y) = {sigmaY:.4f}\n"
        elif char == "Коэффициент асимметрии":
            text += f"Коэффициент асимметрии:\nAs(X) = {skewX:.4f}\nAs(Y) = {skewY:.4f}\n"
        elif char == "Коэффициент эксцесса":
            text += f"Коэффициент эксцесса:\nEx(X) = {kurtosisX:.4f}\nEx(Y) = {kurtosisY:.4f}\n"
        else:
            text = "Выберите характеристику!"
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)

    def open_calculator(self):
        if not self.distX or not self.distY:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте данные!")
            return
        win = tk.Toplevel(self.root)
        win.title("Калькулятор распределений")
        win.geometry("1200x800")
        win.configure(bg=BG_PINK)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TFrame', background=BG_PINK)
        style.configure('TLabel', background=BG_PINK, foreground=FG_TEXT)
        style.configure('TButton', background=BTN_PINK, foreground=FG_TEXT)
        style.configure('TCombobox', fieldbackground=ENTRY_BG, background=ENTRY_BG)
        style.configure('Treeview', background=ENTRY_BG, fieldbackground=ENTRY_BG, foreground=FG_TEXT)
        style.map('TButton', background=[('active', BTN_PINK)])
        tk.Label(win, text="Выберите операцию:", bg=BG_PINK, fg=FG_TEXT).pack(pady=5)
        operations = [
            ("Сложение aX^n + bY^m", add_distributions, 'xy'),
            ("Умножение aX^n * bY^m", multiply_distributions, 'xy'),
            ("Преобразование X: cX^n", None, 'cxn'),
            ("Преобразование Y: cY^n", None, 'cyn'),
            ("Сложение aX^n + bX^m", add_distributions, 'xx'),
            ("Умножение aX^n * bX^m", multiply_distributions, 'xx'),
            ("Сложение aY^n + bY^m", add_distributions, 'yy'),
            ("Умножение aY^n * bY^m", multiply_distributions, 'yy'),
        ]
        op_names = [op[0] for op in operations]
        op_var = tk.StringVar(value=op_names[0])
        op_menu = ttk.Combobox(win, textvariable=op_var, values=op_names, state="readonly", width=45)
        op_menu.pack(pady=5)

        # Поля для коэффициентов a, b и степеней n, m (по умолчанию скрыты)
        coeffs_frame = tk.Frame(win, bg=BG_PINK)
        a_label = tk.Label(coeffs_frame, text="a (X/Y):", bg=BG_PINK, fg=FG_TEXT)
        a_entry = tk.Entry(coeffs_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        a_entry.insert(0, "1")
        n_label = tk.Label(coeffs_frame, text="n (степень X/Y):", bg=BG_PINK, fg=FG_TEXT)
        n_entry = tk.Entry(coeffs_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        n_entry.insert(0, "1")
        b_label = tk.Label(coeffs_frame, text="b (Y/X):", bg=BG_PINK, fg=FG_TEXT)
        b_entry = tk.Entry(coeffs_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        b_entry.insert(0, "1")
        m_label = tk.Label(coeffs_frame, text="m (степень Y/X):", bg=BG_PINK, fg=FG_TEXT)
        m_entry = tk.Entry(coeffs_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        m_entry.insert(0, "1")
        a_label.pack(side=tk.LEFT)
        a_entry.pack(side=tk.LEFT, padx=2)
        n_label.pack(side=tk.LEFT, padx=(10,0))
        n_entry.pack(side=tk.LEFT, padx=2)
        b_label.pack(side=tk.LEFT, padx=(10,0))
        b_entry.pack(side=tk.LEFT, padx=2)
        m_label.pack(side=tk.LEFT, padx=(10,0))
        m_entry.pack(side=tk.LEFT, padx=2)

        # Поля для преобразования X: cX^n
        cxn_frame = tk.Frame(win, bg=BG_PINK)
        cxn_c_label = tk.Label(cxn_frame, text="c (X):", bg=BG_PINK, fg=FG_TEXT)
        cxn_c_entry = tk.Entry(cxn_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        cxn_c_entry.insert(0, "1")
        cxn_n_label = tk.Label(cxn_frame, text="n (степень X):", bg=BG_PINK, fg=FG_TEXT)
        cxn_n_entry = tk.Entry(cxn_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        cxn_n_entry.insert(0, "1")
        cxn_c_label.pack(side=tk.LEFT)
        cxn_c_entry.pack(side=tk.LEFT, padx=2)
        cxn_n_label.pack(side=tk.LEFT, padx=(10,0))
        cxn_n_entry.pack(side=tk.LEFT, padx=2)

        # Поля для преобразования Y: cY^n
        cyn_frame = tk.Frame(win, bg=BG_PINK)
        cyn_c_label = tk.Label(cyn_frame, text="c (Y):", bg=BG_PINK, fg=FG_TEXT)
        cyn_c_entry = tk.Entry(cyn_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        cyn_c_entry.insert(0, "1")
        cyn_n_label = tk.Label(cyn_frame, text="n (степень Y):", bg=BG_PINK, fg=FG_TEXT)
        cyn_n_entry = tk.Entry(cyn_frame, width=4, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        cyn_n_entry.insert(0, "1")
        cyn_c_label.pack(side=tk.LEFT)
        cyn_c_entry.pack(side=tk.LEFT, padx=2)
        cyn_n_label.pack(side=tk.LEFT, padx=(10,0))
        cyn_n_entry.pack(side=tk.LEFT, padx=2)

        def update_fields(*args):
            idx = op_names.index(op_var.get())
            op_type = operations[idx][2]
            if op_type in ['xy', 'xx', 'yy']:
                coeffs_frame.pack(pady=5)
                cxn_frame.pack_forget()
                cyn_frame.pack_forget()
            elif op_type == 'cxn':
                coeffs_frame.pack_forget()
                cxn_frame.pack(pady=5)
                cyn_frame.pack_forget()
            elif op_type == 'cyn':
                coeffs_frame.pack_forget()
                cxn_frame.pack_forget()
                cyn_frame.pack(pady=5)
            else:
                coeffs_frame.pack_forget()
                cxn_frame.pack_forget()
                cyn_frame.pack_forget()
        op_var.trace_add('write', update_fields)
        update_fields()

        text_frame = tk.Frame(win, bg=BG_PINK)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        result_text = tk.Text(text_frame, height=15, width=110, font=("Consolas", 10), wrap="none", bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        yscroll = tk.Scrollbar(text_frame, orient="vertical", command=result_text.yview)
        result_text.configure(yscrollcommand=yscroll.set)
        result_text.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        def pow_distribution(dist, power):
            result = defaultdict(float)
            for x, p in dist.items():
                result[x ** power] += p
            return dict(result)

        def show_result():
            idx = op_names.index(op_var.get())
            func = operations[idx][1]
            op_type = operations[idx][2]
            # Для операций с коэффициентами и степенями
            if op_type == 'xy':
                try:
                    a = int(a_entry.get())
                    b = int(b_entry.get())
                    n = int(n_entry.get())
                    m = int(m_entry.get())
                except Exception:
                    messagebox.showerror("Ошибка", "Введите целые коэффициенты a, b и степени n, m!")
                    return
                distX_mod = multiply_by_constant(pow_distribution(self.distX, n), a)
                distY_mod = multiply_by_constant(pow_distribution(self.distY, m), b)
                if idx == 0:
                    res = add_distributions(distX_mod, distY_mod)
                elif idx == 1:
                    res = multiply_distributions(distX_mod, distY_mod)
            elif op_type == 'xx':
                try:
                    a = int(a_entry.get())
                    b = int(b_entry.get())
                    n = int(n_entry.get())
                    m = int(m_entry.get())
                except Exception:
                    messagebox.showerror("Ошибка", "Введите целые коэффициенты a, b и степени n, m!")
                    return
                distX1_mod = multiply_by_constant(pow_distribution(self.distX, n), a)
                distX2_mod = multiply_by_constant(pow_distribution(self.distX, m), b)
                if idx == 5:
                    res = add_distributions(distX1_mod, distX2_mod)
                elif idx == 6:
                    res = multiply_distributions(distX1_mod, distX2_mod)
            elif op_type == 'yy':
                try:
                    a = int(a_entry.get())
                    b = int(b_entry.get())
                    n = int(n_entry.get())
                    m = int(m_entry.get())
                except Exception:
                    messagebox.showerror("Ошибка", "Введите целые коэффициенты a, b и степени n, m!")
                    return
                distY1_mod = multiply_by_constant(pow_distribution(self.distY, n), a)
                distY2_mod = multiply_by_constant(pow_distribution(self.distY, m), b)
                if idx == 8:
                    res = add_distributions(distY1_mod, distY2_mod)
                elif idx == 9:
                    res = multiply_distributions(distY1_mod, distY2_mod)
            elif op_type == 'cxn':
                try:
                    c = int(cxn_c_entry.get())
                    n = int(cxn_n_entry.get())
                except Exception:
                    messagebox.showerror("Ошибка", "Введите целые значения c и n для X!")
                    return
                res = multiply_by_constant(pow_distribution(self.distX, n), c)
            elif op_type == 'cyn':
                try:
                    c = int(cyn_c_entry.get())
                    n = int(cyn_n_entry.get())
                except Exception:
                    messagebox.showerror("Ошибка", "Введите целые значения c и n для Y!")
                    return
                res = multiply_by_constant(pow_distribution(self.distY, n), c)
            else:
                res = func(self.distX, self.distY)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"{'xi':>10}{'pi':>15}{'Накопленная pi':>20}\n")
            result_text.insert(tk.END, '-' * 45 + '\n')
            cumulative = 0
            values = []
            probabilities = []
            for xi in sorted(res):
                pi = res[xi]
                cumulative += pi
                result_text.insert(tk.END, f"{xi:>10}{pi:>15.4f}{cumulative:>20.4f}\n")
                values.append(xi)
                probabilities.append(pi)
            stats = distribution_stats(res)
            text = ""
            text += f"\nМатематическое ожидание: M = {stats['mean']:.4f}\n"
            text += f"Дисперсия: D = {stats['var']:.4f}\n"
            text += "Начальные моменты:\n"
            for k, mu in enumerate(stats['moments'], 1):
                text += f"μ{k} = {mu:.4f}\n"
            text += "Центральные моменты:\n"
            for k, mu in enumerate(stats['cmoments'], 1):
                text += f"μ°{k} = {mu:.4f}\n"
            text += f"Среднеквадратичное отклонение: σ = {stats['std']:.4f}\n"
            text += f"Коэффициент асимметрии: As = {stats['skew']:.4f}\n"
            text += f"Коэффициент эксцесса: Ex = {stats['kurt']:.4f}\n"
            result_text.insert(tk.END, text)

        tk.Button(win, text="Показать результат", command=show_result, bg=BTN_PINK, fg=FG_TEXT, relief=tk.FLAT, activebackground=BTN_PINK).pack(pady=10)

    def add_row(self, table):
        """Добавляет новую строку (0, 0.0) в указанную таблицу."""
        table.insert("", tk.END, values=(0, 0.0))

    def delete_row(self, table):
        """Удаляет выделенные строки из таблицы, либо последнюю строку, если ничего не выделено."""
        selected = table.selection()
        if not selected:
            children = table.get_children()
            if children:
                table.delete(children[-1])
        else:
            for item in selected:
                table.delete(item)

    def save_main_table(self):
        """Сохраняет значения из таблиц X и Y, нормализует вероятности, обновляет распределения и таблицы."""
        try:
            self.X, self.pX = self.get_table_data(self.table_X)
            self.Y, self.pY = self.get_table_data(self.table_Y)
            if not self.X or not self.Y:
                messagebox.showerror("Ошибка", "Массивы не могут быть пустыми!")
                return
            sumPX = sum(self.pX)
            sumPY = sum(self.pY)
            if sumPX == 0 or sumPY == 0:
                messagebox.showerror("Ошибка", "Сумма вероятностей не может быть 0!")
                return
            self.pX = [round(px / sumPX, 2) for px in self.pX]
            self.pY = [round(py / sumPY, 2) for py in self.pY]
            self.update_table(self.table_X, self.X, self.pX)
            self.update_table(self.table_Y, self.Y, self.pY)
            self.stats_text.delete(1.0, tk.END)
            self.distX = create_distribution_series(self.X, self.pX)
            self.distY = create_distribution_series(self.Y, self.pY)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка ввода: {e}")

    def get_table_data(self, table):
        """Считывает значения из таблицы и возвращает два списка: значения и вероятности. Пропускает строки с пустыми ячейками."""
        X, pX = [], []
        for item in table.get_children():
            vals = table.item(item)['values']
            if vals[0] == '' or vals[1] == '':
                continue
            try:
                X.append(int(vals[0]))
                pX.append(float(vals[1]))
            except Exception:
                continue
        return X, pX

    def update_table(self, table, X, pX):
        """Очищает таблицу и заполняет её новыми значениями X и pX."""
        table.delete(*table.get_children())
        for x, px in zip(X, pX):
            table.insert("", tk.END, values=(x, px))

    def edit_cell_main(self, event, table):
        """Позволяет редактировать ячейку таблицы по двойному клику мыши."""
        item = table.identify_row(event.y)
        column = table.identify_column(event.x)
        if not item or not column:
            return
        col = int(column.replace('#', '')) - 1
        old_val = table.item(item)['values'][col]
        entry = tk.Entry(self.root, width=8, bg=ENTRY_BG, fg=FG_TEXT, relief=tk.FLAT)
        entry.insert(0, str(old_val))
        x = event.x_root - self.root.winfo_rootx()
        y = event.y_root - self.root.winfo_rooty()
        entry.place(x=x, y=y)
        entry.focus()
        def save_edit(event=None):
            try:
                new_val = entry.get()
                vals = list(table.item(item)['values'])
                vals[col] = float(new_val) if col == 1 else int(new_val)
                table.item(item, values=vals)
                entry.destroy()
            except Exception:
                entry.destroy()
        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)

if __name__ == "__main__":
    root = tk.Tk()
    app = DistributionApp(root)
    root.mainloop()
