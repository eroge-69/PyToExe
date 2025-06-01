import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

# ---- Функция Снеллиуса (закон преломления) ----
def snells_law(a, n1, n2):
    """
    Функция реализует закон Снеллиуса для расчета угла преломления.
    a   - угол падения (в радианах)
    n1  - показатель преломления первой среды
    n2  - показатель преломления второй среды
    Возвращает угол преломления в радианах, либо None в случае полного внутреннего отражения.
    """
    s = (n1 / n2) * np.sin(a)
    if abs(s) > 1:
        return None  # Полное внутреннее отражение
    return np.arcsin(s)

# ---- Расчет новых координат при продвижении луча ----
def propagate_ray(x, y, a, d):
    """
    x, y    - начальные координаты луча
    a       - угол направления (радианы)
    d       - расстояние перемещения
    Возвращает новые координаты (x_new, y_new)
    """
    return x + d * np.cos(a), y + d * np.sin(a)

# ---- Прохождение луча через одну вращающуюся призму (две поверхности) ----
def riesley_prism(x, y, a, n, ya, za, h, rot_angle, rot_dir):
    """
    x, y            - координаты входа
    a               - угол направления луча (радианы)
    n               - показатель преломления призмы
    ya, za          - углы наклона передней и задней поверхности призмы (радианы)
    h               - толщина призмы (метры)
    rot_angle       - текущий угол поворота призмы (радианы)
    rot_dir         - направление вращения (1 или -1)

    Возвращает координаты выхода и угол выхода. Если есть полное внутреннее отражение, вернет (None, None, None)
    """
    # Учет вращения призмы
    ey, ez = ya + rot_angle * rot_dir, za + rot_angle * rot_dir
    # Преломление на входной поверхности
    b1 = snells_law(a - ey, 1.0, n)
    if b1 is None:
        return None, None, None
    a1 = b1 + ey
    # Прямой ход в толщу призмы (h)
    d1 = h / np.cos(a1 - ez)
    x1, y1 = propagate_ray(x, y, a1, d1)
    # Преломление на выходе из призмы
    b2 = snells_law(a1 - ez, n, 1.0)
    if b2 is None:
        return None, None, None
    ao = b2 + ez
    return x1, y1, ao

# ---- Аналитические расчетные функции для одиночной/двойной призмы ----

def prism_through_thickness(T_max, D, alpha):
    """
    Возвращает толщину призмы между осями в месте прохода луча при клине.
    T_max - максимальная толщина (м)
    D     - диаметр призмы (м)
    alpha - угол клина (радианы)
    """
    return T_max - 0.5 * D * np.tan(alpha)

def lateral_shift_inside_prism(T, alpha, phi_p):
    """
    Считает отклонение внутри призмы за счет разности углов.
    T       - толщина призмы (м)
    alpha   - угол клина (радианы)
    phi_p   - удвоенное отклонение (радианы)
    """
    return T * np.tan(alpha - phi_p)

def lateral_shift_screen(S, phi_o):
    """
    Считает отклонение на экране после выхода из призмы.
    S       - расстояние до экрана (м)
    phi_o   - угол после призмы (радианы)
    """
    return S * np.tan(phi_o)

def deviation_small_angle(n_prism, alpha):
    """
    Малый угол: phi_o ≈ (n - 1) * alpha — быстрое вычисление выходного угла.
    """
    return (n_prism - 1) * alpha

# ---- Визуализация кругового сканирования одной призмой ----
def plot_single_prism_scan(n_prism, alpha_deg, T_max, D, S, N=500, show_steps=False, ax=None):
    """
    Строит окружность смещений луча после одной вращающейся призмы (анализ).
    n_prism    - показатель преломления призмы
    alpha_deg  - угол клина (град)
    T_max      - максимальная толщина (метры)
    D          - диаметр клиновой призмы (метры)
    S          - расстояние до экрана (метры)
    N          - число точек окружности (по умолчанию 500)
    """
    alpha = np.deg2rad(alpha_deg)
    # Исключить невалидные параметры, иначе получится вырождение!
    if alpha == 0 or n_prism == 1 or T_max == 0 or S == 0:
        r = 1e-3 # минимальная окружность, “заглушка”
        xs = np.zeros(N)
        ys = np.zeros(N)
    else:
        T = prism_through_thickness(T_max, D, alpha)
        phi_p = n_prism * alpha
        rT = lateral_shift_inside_prism(T, alpha, phi_p)
        phi_o = deviation_small_angle(n_prism, alpha)
        rS = lateral_shift_screen(S, phi_o)
        r = rT + rS
        thetas = np.linspace(0, 2*np.pi, N)
        xs = r * np.cos(thetas) * 1e3
        ys = r * np.sin(thetas) * 1e3

    show_plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(7,7))
        show_plot = True
    ax.plot(xs, ys, 'b-', label=f"R = {r*1e3:.2f} мм")
    ax.set_title("Круговое сканирование одной призмой")
    ax.set_xlabel("X (мм)")
    ax.set_ylabel("Y (мм)")
    ax.set_aspect('equal', adjustable='datalim') # Квадратный график
    ax.grid(True)
    ax.legend(loc='upper right')
    if show_steps:
        print(f"R = {r*1e3:.3f} мм")
    if show_plot:
        plt.show()
    return r

# ---- Функции для трассировки лучей через телескоп ----
def thin_lens_ray(y, angle, f):
    """
    Прохождение луча через тонкую линзу с фокусным расстоянием f.
    Возвращает угол после линзы (радианы).
    angle — угол до линзы (радианы)
    f — фокусное расстояние (метры)
    y — смещение луча относительно главной оптической оси (метры)
    """
    # Формула: y' ≈ y, alpha2 = alpha1 - y/f
    return angle - y/f

def propagate_to_next(z, y, angle, distance):
    """
    Двигает луч вдоль z на расстояние distance.
    z, y — начальные координаты (метры)
    angle — угол (радианы)
    distance — расстояние вдоль оси (метры)
    Возвращает новые (z, y)
    """
    z_new = z + distance
    y_new = y + distance * np.tan(angle)
    return z_new, y_new

def draw_lens(ax, z, D, color='blue', kind='lens', label=None):
    """
    Нарисовать линзу или фильтр на графике.
    ax - объект matplotlib axes
    z - позиция по оси z
    D - диаметр линзы
    color - цвет линзы
    kind - тип элемента ('lens' или 'filter')
    label - подпись для легенды
    """
    if kind == 'filter':
        ax.add_patch(Rectangle((z-0.001, -D/2), 0.002, D, color=color, alpha=0.4, label=label))
    else:
        ax.plot([z, z], [-D/2, D/2], color=color, linewidth=3, label=label)

def telescope_ray_trace(
    lens1_D=0.05, lens1_f=0.05,  # выпукло-вогнатая, диаметр 50 мм, фокусное 50 мм
    lens2_D=0.01, lens2_f=-0.02, # вогнуто-выпуклая, 10 мм, отриц. фокус (рассеивающая)
    lens3_D=0.01, lens3_f=0.012, # двояковыпуклая, 10 мм, фокус 12 мм
    lens4_D=0.008, lens4_f=0.01, # четвертая линза
    filter_D=0.008, filter_dx=0.01, # фильтр, диаметр 8 мм, длина 10 мм
    spacing1=0.05, spacing2=0.015, spacing3=0.01, spacing4=0.017, spacing5=0.02,
    rays=7, plot_ax=None, show_plot=True
):
    """
    Моделирует и строит ход пучка параллельных лучей через заданную систему телескопа.
    lens*_D — диаметр линзы
    lens*_f — фокусное расстояние линзы
    filter_* — параметры фильтра
    spacing* — расстояние между элементами (в метрах)
    rays — количество моделируемых лучей (по апертуре)
    """
    # Лучи идут вдоль оси z, y — поперечная координата (осевая система)
    # Начальная координата приёмной апертуры (z=0)
    ray_ys = np.linspace(-lens1_D/2*0.9, lens1_D/2*0.9, rays)  # слегка не до края
    ray_angle = 0.0             # параллельно оси
    color_cycle = plt.cm.viridis(np.linspace(0,1,rays))

    # Шаги: [линза1], spacer, [линза2], spacer, [фильтр], spacer, [линза3], spacer, [линза4], до фокуса
    Zs = []
    Ys = []
    for idx, y0 in enumerate(ray_ys):
        z = 0.
        y = y0
        angle = ray_angle
        zz = [z]
        yy = [y]

        # 1. Движение до линзы 1
        z, y = propagate_to_next(z, y, angle, spacing1)
        zz.append(z); yy.append(y)
        # 2. Преломление на линзе 1 (выпукло-вогнатая, собирающая)
        angle = thin_lens_ray(y, angle, lens1_f)
        # 3. Движение до линзы 2
        z, y = propagate_to_next(z, y, angle, spacing2)
        zz.append(z); yy.append(y)
        # 4. Преломление на линзе 2 (вогнуто-выпуклая, рассеивающая)
        angle = thin_lens_ray(y, angle, lens2_f)
        # 5. Движение до фильтра
        z, y = propagate_to_next(z, y, angle, spacing3)
        zz.append(z); yy.append(y)
        # 6. Проходим фильтр (луч не меняет направление)
        z, y = propagate_to_next(z, y, angle, filter_dx)
        zz.append(z); yy.append(y)
        # 7. Движение до линзы 3
        z, y = propagate_to_next(z, y, angle, spacing4)
        zz.append(z); yy.append(y)
        # 8. Преломление на линзе 3 (двояковыпуклая, собирающая)
        angle = thin_lens_ray(y, angle, lens3_f)
        # 9. Движение до линзы 4
        z, y = propagate_to_next(z, y, angle, spacing5)
        zz.append(z); yy.append(y)
        # 10. Преломление на линзе 4
        angle = thin_lens_ray(y, angle, lens4_f)
        # 11. Движение до фокальной плоскости приемника
        z, y = propagate_to_next(z, y, angle, lens4_f*2.5)
        zz.append(z); yy.append(y)

        Zs.append(zz)
        Ys.append(yy)

    # Визуализация
    if plot_ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
    else:
        ax = plot_ax
    for i in range(rays):
        ax.plot(Zs[i], Ys[i], color=color_cycle[i], label=None if i > 0 else 'Параллельный пучок')
    
    # Нарисовать линзы и фильтр
    draw_lens(ax, spacing1, lens1_D, label='Линза 1 (Собирающая)')
    draw_lens(ax, spacing1+spacing2, lens2_D, color='red', label='Линза 2 (Рассеивающая)')
    draw_lens(ax, spacing1+spacing2+spacing3+filter_dx/2, filter_D, color='green', kind='filter', label='Фильтр')
    draw_lens(ax, spacing1+spacing2+spacing3+filter_dx+spacing4, lens3_D, color='orange', label='Линза 3 (Собирающая)')
    draw_lens(ax, spacing1+spacing2+spacing3+filter_dx+spacing4+spacing5, lens4_D, color='purple', label='Линза 4 (Собирающая)')
    
    ax.set_xlabel("z (м)")
    ax.set_ylabel("y (м)")
    ax.set_aspect("auto")
    ax.grid(True)
    ax.set_title("Ход лучей в четырехлинзовом телескопе")
    ax.set_xlim(-0.01, z+0.04)
    ax.set_ylim(-0.03, 0.03)
    # Легенда
    ax.legend(loc='upper right')
    
    if plot_ax is None and show_plot:
        plt.show()
    return Zs, Ys

# ---- Визуализация области двух призм (Рисли) и розетки (rose curve) ----
def plot_risley_prism_annulus(n_prism, alpha_deg, T_max, D, S, ratio=1.5, N=800, show_steps=False, ax=None):
    """
    Строит кольцевую область (аннуляр) и пример розетки для двух вращающихся призм (анализ).
    n_prism    - показатель преломления призмы
    alpha_deg  - угол клина (град)
    T_max      - максимальная толщина (метры)
    D          - диаметр клиновой призмы (метры)
    S          - расстояние до экрана (метры)
    ratio      - отношение скоростей призмы (розетка)
    N          - число точек
    """
    alpha = np.deg2rad(alpha_deg)
    if alpha == 0 or n_prism == 1 or T_max == 0 or S == 0:
        r1 = 1e-3
        r_big = 2*r1
        r_def = r1
        xs = ys = x_out = y_out = x_in = y_in = np.zeros(N)
    else:
        T = prism_through_thickness(T_max, D, alpha)
        phi_p = n_prism * alpha
        rT = lateral_shift_inside_prism(T, alpha, phi_p)
        phi_o = deviation_small_angle(n_prism, alpha)
        rS = lateral_shift_screen(S, phi_o)
        r1 = rT + rS
        r_def = rT
        r_big = 2*r1
        thetas = np.linspace(0, 2*np.pi, N)
        x_out = r_big * np.cos(thetas) * 1e3
        y_out = r_big * np.sin(thetas) * 1e3
        x_in = r_def * np.cos(thetas) * 1e3
        y_in = r_def * np.sin(thetas) * 1e3
        t = np.linspace(0, 2*np.pi, N*2)
        xs = (r1 * np.cos(t) + r1 * np.cos(ratio * t)) * 1e3
        ys = (r1 * np.sin(t) + r1 * np.sin(ratio * t)) * 1e3

    show_plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(7,7))
        show_plot = True
    ax.plot(x_out, y_out, '--', color='orange', label='Внешний край (max)')
    ax.plot(x_in, y_in, '--', color='red', label='Центральный дефект')
    ax.plot(xs, ys, 'b', linewidth=1.5, label=f'Розетка')
    ax.set_title("Risley Prism Scanner — кольцо и розетка")
    ax.set_xlabel("X (мм)")
    ax.set_ylabel("Y (мм)")
    ax.set_aspect('equal', adjustable='datalim')
    ax.legend()
    ax.grid(True)
    if show_steps:
        print(f"R1 = {r1*1e3:.3f} мм")
    if show_plot:
        plt.show()
    return r1, r_big, r_def

# ---- Класс интерфейса tkinter для экспериментов ----
class RisleyPrismGUI:
    def __init__(self, root):
        self.root = root
        root.title("Risley Prism — 3 призмы, циклы вращения, линия трассы")
        # Адаптивность: размер 60% ширины, 70% высоты экрана
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = max(980, int(screen_width*0.6))
        height = max(700, int(screen_height*0.7))
        root.geometry(f"{width}x{height}")
        root.update_idletasks()
        root.minsize(900, 600)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        self.entries = {}
        self.build_left()
        self.build_plot_area()
        self.update_plot()

    def build_left(self):
        # Левая панель ― параметры и кнопки
        frame = ttk.Frame(self.root, padding="8")
        frame.grid(row=0, column=0, sticky="ns")
        param_frame = ttk.LabelFrame(frame, text="Параметры системы", padding="6")
        param_frame.pack(fill=tk.X, pady=2)
        # Параметры модели
        labels_data = [
            ("F", "Δист. до 1 призмы (мм):", "10"),
            ("y1", "угол фронт. 1 (град):", "10"),
            ("z1", "угол тыль. 1 (град):", "0"),
            ("alfa1", "угол падения (град):", "0"),
            ("n1", "n призм1:", "1.51"),
            ("n2", "n призм2:", "1.51"),
            ("n3", "n призм3:", "1.51"),
            ("s1", "Δ1–2 призмы (мм):", "5"),
            ("s2", "Δ2–3 призмы (мм):", "15"),
            ("S",  "Δ до экрана (мм):", "100"),
            ("y2", "угол фронт. 2 (град):", "0"),
            ("z2", "угол тыль. 2 (град):", "10"),
            ("y3", "угол фронт. 3 (град):", "0"),
            ("z3", "угол тыль. 3 (град):", "10"),
            ("w1", "ω1 (об/мин):", "12000"),
            ("w2", "ω2 (об/мин):", "15000"),
            ("w3", "ω3 (об/мин):", "20000"),
            ("h1", "толщина 1 (мм):", "10"),
            ("h2", "толщина 2 (мм):", "10"),
            ("h3", "толщина 3 (мм):", "15"),
            ("rd1","напр.вращ. 1 (1/-1):", "1"),
            ("rd2","напр.вращ. 2 (1/-1):", "-1"),
            ("rd3","напр.вращ. 3 (1/-1):", "1"),
            # Для аналитики
            ("D", "диаметр (мм):", "25.4"),
            # Новый параметр: количество оборотов (циклов)
            ("NCYC", "Число циклов для построения:", "5"),
            ("Nscan", "Число точек на цикл:", "3000"),
        ]
        for i, (key, lab, default) in enumerate(labels_data):
            ttk.Label(param_frame, text=lab).grid(row=i, column=0, sticky=tk.W, padx=2, pady=1)
            e = ttk.Entry(param_frame, width=13)
            e.insert(0, default)
            e.grid(row=i, column=1, sticky=tk.W, padx=2, pady=1)
            self.entries[key] = e

        # Кнопки управления
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=7)
        ttk.Button(btn_frame, text="Построить/Обновить", command=self.update_plot).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Сохранить график", command=self.save_plot).pack(side=tk.LEFT, padx=2)
        # Текстовое поле для вывода результатов расчетов
        results_frame = ttk.LabelFrame(frame, text="Результаты расчёта", padding="7")
        results_frame.pack(fill=tk.X, pady=4)
        self.results_text = tk.Text(results_frame, height=12, width=44, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def build_plot_area(self):
        # Правая зона — matplotlib-виджет для графика
        plotframe = ttk.Frame(self.root)
        plotframe.grid(row=0, column=1, sticky="nsew")
        self.fig = Figure(figsize=(7, 7))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plotframe)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plotframe = plotframe

    def get_params(self):
        """
        Считывает все параметры из формы, приводит их к нужным типам и единицам СИ.
        """
        try:
            ff = lambda k: float(self.entries[k].get())
            p = {
                'F': ff('F') / 1000,
                'y1': np.deg2rad(ff('y1')),
                'z1': np.deg2rad(ff('z1')),
                'alfa1': np.deg2rad(ff('alfa1')),
                'n1': ff('n1'),
                'n2': ff('n2'),
                'n3': ff('n3'),
                's1': ff('s1') / 1000,
                's2': ff('s2') / 1000,
                'S': ff('S') / 1000,
                'y2': np.deg2rad(ff('y2')),
                'z2': np.deg2rad(ff('z2')),
                'y3': np.deg2rad(ff('y3')),
                'z3': np.deg2rad(ff('z3')),
                'w1': np.deg2rad(ff('w1')),
                'w2': np.deg2rad(ff('w2')),
                'w3': np.deg2rad(ff('w3')),
                'h1': ff('h1') / 1000,
                'h2': ff('h2') / 1000,
                'h3': ff('h3') / 1000,
                'rd1': int(self.entries['rd1'].get()),
                'rd2': int(self.entries['rd2'].get()),
                'rd3': int(self.entries['rd3'].get()),
                'D': ff('D') / 1000,
                'NCYC': int(self.entries['NCYC'].get()),
                'Nscan': int(self.entries['Nscan'].get()),
            }
            return p
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка ввода: {e}")
            return None

    def update_plot(self):
        """
        Апдейт графика (и расчет) при изменении параметров или нажатии кнопки.
        Теперь используется аналитическая формула для трёх призм.
        """
        p = self.get_params()
        if not p: return
        self.ax.clear()
        self.results_text.delete(1.0, tk.END)

        Ncycles = p['NCYC']
        Npoints = p['Nscan'] * Ncycles

        n_prism = p['n1']
        alpha_deg = np.rad2deg(p['y1'])
        T_max = p['h1']
        D = p['D']
        S = p['S']
        w1 = p['w1']
        w2 = p['w2']
        w3 = p['w3']
        rd1 = p['rd1']
        rd2 = p['rd2']
        rd3 = p['rd3']

        xs, ys = risley_3prism_trajectory(
            n_prism, alpha_deg, T_max, D, S,
            w1, w2, w3, Npoints=Npoints, Ncycles=Ncycles,
            rd1=rd1, rd2=rd2, rd3=rd3
        )

        self.ax.plot(xs, ys, '-', color="b", linewidth=1.5, label="Аналитическая траектория (3 призмы)")
        fill_percent = plot_density_indicator(self.ax, xs, ys, bins=100)
        self.ax.set_xlabel("X экрана (мм)")
        self.ax.set_ylabel("Y экрана (мм)")
        self.ax.set_title(f"Траектория трёх призм за {Ncycles} цикл(а/ов)")
        self.ax.set_aspect('equal', adjustable='datalim')
        self.ax.grid(True)
        self.ax.legend()
        yspread = np.ptp(ys) if len(ys) else 0
        xspread = np.ptp(xs) if len(xs) else 0
        self.results_text.insert(
            tk.END,
            f"Всего точек: {len(ys)}\nΔY (мм): {yspread:.2f}\nΔX (мм): {xspread:.2f}\n"
            f"Заполнено пространства: {fill_percent:.1f}%\n"
        )
        self.canvas.draw()

    def save_plot(self):
        """
        Сохранить текущий график matplotlib как png-файл.
        """
        try:
            from tkinter import filedialog
            fname = filedialog.asksaveasfilename(defaultextension=".png",
                                    filetypes=[("PNG file","*.png"),("All files","*.*")])
            if fname:
                self.fig.savefig(fname, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Сохранено", f"График сохранён: {fname}")
        except Exception as e:
            messagebox.showerror("Ошибка при сохранении", str(e))

def risley_radii(n_prism, alpha_deg, T_max, D, S):
    """
    Вычисляет радиусы отклонения для каждой призмы (r1, r2, r3) и центральный дефект (r_d).
    Все радиусы в метрах.
    """
    alpha = np.deg2rad(alpha_deg)
    # Для всех трёх призм считаем одинаково (можно расширить для разных параметров)
    T = prism_through_thickness(T_max, D, alpha)
    phi_p = n_prism * alpha
    rT = lateral_shift_inside_prism(T, alpha, phi_p)
    phi_o = deviation_small_angle(n_prism, alpha)
    rS = lateral_shift_screen(S, phi_o)
    r = rT + rS
    r_d = rT  # центральный дефект (радиус "дырки" в центре)
    return r, r, r, r_d

def risley_3prism_trajectory(
    n_prism, alpha_deg, T_max, D, S,
    w1, w2, w3, Npoints=3000, Ncycles=5,
    rd1=1, rd2=1, rd3=1
):
    """
    Строит траекторию для трёх вращающихся призм по аналитическим формулам.
    Возвращает массивы X, Y (мм).
    """
    r1, r2, r3, r_d = risley_radii(n_prism, alpha_deg, T_max, D, S)
    tmax = Ncycles * 2 * np.pi
    t = np.linspace(0, tmax, Npoints)
    # Учитываем направление вращения rd1, rd2, rd3
    x = (r1 + r_d) * np.cos(rd1 * w1 * t) + r2 * np.cos(rd2 * w2 * t) + r3 * np.cos(rd3 * w3 * t)
    y = (r1 + r_d) * np.sin(rd1 * w1 * t) + r2 * np.sin(rd2 * w2 * t) + r3 * np.sin(rd3 * w3 * t)
    return x * 1e3, y * 1e3  # в мм

def plot_density_indicator(ax, xs, ys, bins=100):
    """
    Рисует индикатор плотности точек на графике ax.
    Показывает заполненность (занятое/свободное пространство) в процентах.
    """
    # 2D гистограмма
    H, xedges, yedges = np.histogram2d(xs, ys, bins=bins)
    occupied = np.count_nonzero(H)
    total = H.size
    fill_percent = 100 * occupied / total if total > 0 else 0

    # Визуализация плотности (heatmap)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    ax.imshow(H.T, extent=extent, origin='lower', cmap='hot', alpha=0.35, aspect='auto')

    # Текстовый индикатор
    ax.text(
        0.02, 0.98,
        f"Заполнено: {fill_percent:.1f}%",
        color='black', fontsize=12, fontweight='bold',
        ha='left', va='top', transform=ax.transAxes,
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray')
    )
    return fill_percent

# ---- Точка входа: запуск программы ----
if __name__ == "__main__":
    root = tk.Tk()
    RisleyPrismGUI(root)
    root.mainloop()
