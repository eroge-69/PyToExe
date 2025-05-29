# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import cm

# Константы для оформления
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#e1e1e1"
FRAME_COLOR = "#ffffff"
TEXT_COLOR = "#333333"
ACCENT_COLOR = "#4a6ea9"

a = 1.1
b = 0.8

def real_u(X, Y):
    return np.sin(X) + np.cos(2*X*Y)

def f(x, y):
    return 1.1*np.sin(x) +(3.2*x*x +4.4*y*y)*np.cos(x*y)*np.cos(x*y)

def find_eigen_values():
    global a, b
    n = int(entry_step.get())
    h = 1/n
    eps = float(entry_error.get())

    # Initialize and normalize u
    u = np.ones((n + 1, n + 1))
    if n == 2:
        eigen_value = round(8 * (a + b),1)
        label_max_eigen_value['text'] = str(eigen_value)
        label_min_eigen_value['text'] = str(eigen_value)
        return
    for i in range(n + 1):
        u[i][0] = 0
        u[i][n] = 0
        u[0][i] = 0
        u[n][i] = 0
    u = u / np.linalg.norm(u)

    # Find maximum eigenvalue
    max_eigen_value = 0
    prev_eigen = float('inf')
    while abs(prev_eigen - max_eigen_value) >= eps:
        v = np.zeros_like(u)
        for i in range(1, n):
            for j in range(1, n):
                v[i][j] = -a*(u[i+1][j] - 2*u[i][j] + u[i-1][j])/(h*h) - b*(u[i][j+1] - 2*u[i][j] + u[i][j-1])/(h*h)
        
        prev_eigen = max_eigen_value
        max_eigen_value = np.sum(u * v) / np.sum(u * u)  # Rayleigh quotient for better stability
        u = v / np.linalg.norm(v)
    
    # Find minimum eigenvalue using shifted power method
    u = np.ones((n + 1, n + 1))  # Reinitialize with random vector
    for i in range(n + 1):
        u[i][0] = 0
        u[i][n] = 0
        u[0][i] = 0
        u[n][i] = 0
    u = u / np.linalg.norm(u)
    
    min_eigen_value = 0
    prev_eigen = float('inf')
    shift = max_eigen_value  # Shift by maximum eigenvalue
    
    while abs(prev_eigen - min_eigen_value) >= eps:
        v = np.ones((n+1,n+1))
        for i in range(1, n):
            for j in range(1, n):
                v[i][j] = shift * u[i][j] - (-a*(u[i+1][j] - 2*u[i][j] + u[i-1][j])/(h*h) - b*(u[i][j+1] - 2*u[i][j] + u[i][j-1])/(h*h))
        
        prev_eigen = min_eigen_value
        min_eigen_value = shift - np.sum(u * v) / np.sum(u * u)  # Rayleigh quotient for shifted matrix
        u = v / np.linalg.norm(v)
    
    label_max_eigen_value['text'] = str(max_eigen_value)
    label_min_eigen_value['text'] = str(min_eigen_value)
        

def update_iteration_info(method, iteration, diff_norm, solution_error, alpha_k=None):
    if method == "Якоби":
        label_method_jacobi['text'] = f"Метод: {method}"
        label_iteration_jacobi['text'] = f"Итерация: {iteration}"
        label_diff_norm_jacobi['text'] = f"Норма разности: {diff_norm:.16f}"
        label_solution_error_jacobi['text'] = f"Ошибка решения: {solution_error:.16f}"
    else:
        label_method_desc['text'] = f"Метод: {method}"
        label_iteration_desc['text'] = f"Итерация: {iteration}"
        label_diff_norm_desc['text'] = f"Норма разности: {diff_norm:.16f}"
        label_solution_error_desc['text'] = f"Ошибка решения: {solution_error:.16f}"
        if alpha_k is not None:
            label_alpha_desc['text'] = f"Alpha_k: {alpha_k:.16f}"
        else:
            label_alpha_desc['text'] = ""

def plot_min_desc_method():
    
    global ani, a, b

    # Считываем параметры сетки и критерий останова
    n = int(entry_step.get())
    h = 1.0 / n
    eps = float(entry_error.get())
    skip = int(entry_skip.get())
    prev_u = np.zeros((n + 1, n + 1))
    # Инициализация массивов решения и невязок
    u = np.zeros((n+1, n+1))
    r = np.zeros_like(u)
    Ar = np.zeros_like(u)

    # Устанавливаем граничные значения по точному решению
    for i in range(n+1):
        x = i * h
        u[i, 0]   = real_u(x, 0)
        u[i, n]   = real_u(x, 1)
        u[0, i]   = real_u(0, x)
        u[n, i]   = real_u(1, x)

    # Таблица точного решения для оценки ошибки
    exact = np.zeros_like(u)
    for i in range(n+1):
        for j in range(n+1):
            exact[i, j] = real_u(i*h, j*h)

    # Настройка графика
    fig, ax = plt.subplots(figsize=(8,6))
    plt.title("Метод минимальных невязок", fontsize=12)
    mask = np.ones_like(u)  # Изначально всё видимо

# Пример: вырезаем треугольник в левом нижнем углу (x + y < 0.5)
    for i in range(n+1):
        for j in range(n+1):
            x, y = i * h, j * h            
            if (y - x) >= 0.5 and (x <= 0.5):  # Условие для первого треугольника
                mask[i, j] = np.nan
            if (1 - x) + y <= 0.5:  # Условие для второго треугольника
                mask[i, j] = np.nan


    vmin = np.min(u)  # Минимум без учёта NaN
    vmax = np.max(u)  # Максимум без учёта NaN
    plt.cm.viridis.set_bad(color='white') 
    img = ax.imshow(u.T, origin='lower', cmap=plt.cm.viridis, extent=(0,1,0,1), vmin = vmin,vmax = vmax)
    plt.colorbar(img, ax=ax, shrink=0.8)

    iteration = 0
    diff_norm = np.inf

    def update(frame):
        nonlocal u,prev_u, r, Ar, iteration, diff_norm

        # Останов, если достигнут критерий
        if diff_norm <= eps:
            return (img,)
        prev_u = u.copy()
        # Вычисляем невязку r = A u - f
        for i in range(1, n):
            for j in range(1, n):
                lap_u = (u[i+1,j] - 2*u[i,j] + u[i-1,j] + u[i,j+1] - 2*u[i,j] + u[i,j-1]) / h**2
                r[i,j] = a * (u[i+1,j] - 2*u[i,j] + u[i-1,j]) / h**2 + \
                          b * (u[i,j+1] - 2*u[i,j] + u[i,j-1]) / h**2 + f(i*h, j*h)

        # Применяем оператор A к r
        for i in range(1, n):
            for j in range(1, n):
                Ar[i,j] = (a * (r[i+1,j] - 2*r[i,j] + r[i-1,j]) + \
                           b * (r[i,j+1] - 2*r[i,j] + r[i,j-1])) / h**2

        # Находим шаговой параметр alpha = (r, Ar) / (Ar, Ar)
        inner_r_Ar = np.sum(r[1:-1,1:-1] * Ar[1:-1,1:-1])
        inner_Ar_Ar = np.sum(Ar[1:-1,1:-1]**2)
        alpha = inner_r_Ar / inner_Ar_Ar if inner_Ar_Ar != 0 else 0.0

        # Обновляем решение: u_{k+1} = u_k + alpha * r_k
        u[1:-1,1:-1] = u[1:-1,1:-1] - alpha * r[1:-1,1:-1]

        # Вычисляем критерий сходимости
        diff_norm = 0;
        for i in range(1, n):
            for j in range(1, n):
                diff_norm = max(diff_norm, abs(u[i][j] - prev_u[i][j]))
        u_masked = u.copy()
        u_masked[np.isnan(mask)] = np.nan 
        # Обновление итерации
        iteration += 1
        solution_error = 0
        for i in range(1, n):
            for j in range(1, n):
                # solution_error = (u[i][j] - exact_solution[i][j]) ** 2
                solution_error = max(solution_error, abs(u[i][j] - exact[i][j]))
        # При необходимости обновить информацию и график
            # Оценка погрешности решения
            update_iteration_info("Мин. невязки", iteration, diff_norm, solution_error, alpha)
            img.set_array(u_masked.T)
            img.set_clim(np.min(u), np.max(u))
            
       #print("MinRes: alpha =", alpha, "max(r) =", np.max(np.abs(r[1:-1,1:-1])))
        return (img,)
    
    # Анимация
    ani = FuncAnimation(fig, update, frames=range(10000), interval=100, blit=True, repeat=False)
    plt.tight_layout()
    plt.show()

def plot_jacobi_method():
    global ani, a, b
    n = int(entry_step.get())
    h = 1 / n
    
    entry_h['text'] = str(h)
    eps = float(entry_error.get())
    skip_value = int(entry_skip.get())

    u = np.zeros((n+1, n+1))
    next_u = np.zeros((n+1, n+1))
    prev_u = np.zeros((n+1, n+1))
    
    for i in range(n+1):
        next_u[i][0] = real_u(i * h, 0)
        next_u[i][n] = real_u(i * h, 1)
        next_u[0][i] = real_u(0, i * h)
        next_u[n][i] = real_u(1, i * h)
    
    fig = plt.figure(3, figsize=(8, 6))
    ax = fig.add_subplot(111)
    plt.title("Метод Якоби", fontsize=12, pad=20)
    mask = np.ones_like(u)  # Изначально всё видимо

# Пример: вырезаем треугольник в левом нижнем углу (x + y < 0.5)
    for i in range(n+1):
        for j in range(n+1):
            x, y = i * h, j * h            
            if (y - x) >= 0.5 and (x <= 0.5):  # Условие для первого треугольника
                mask[i, j] = np.nan
            if (1 - x) + y <= 0.5:  # Условие для второго треугольника
                mask[i, j] = np.nan

    vmin = np.min(u)  # Минимум без учёта NaN
    vmax = np.max(u)  # Максимум без учёта NaN
    plt.cm.plasma.set_bad(color='white') 
    img = ax.imshow(u.T, origin='lower', cmap=plt.cm.plasma, extent=(0, 1, 0, 1), vmin = vmin, vmax = vmax)
    plt.colorbar(img, ax=ax, shrink=0.8)
    
    diff_norm = float('+inf')
    solution_error = float('+inf')
    iteration = 0

    exact_solution = np.zeros((n+1, n+1))
    for i in range(n+1):
        for j in range(n+1):
            exact_solution[i][j] = real_u(i*h, j*h)
    
    def update(frame):
        nonlocal u, next_u, prev_u, diff_norm, solution_error, iteration
        
        if diff_norm <= eps:
            return img,
        
        prev_u = u.copy()
        
        for i in range(1, n):
            for j in range(1, n):
                x_i = h * i
                t_j = h * j
                next_u[i][j] = (a*(u[i+1][j] + u[i-1][j]) + b*(u[i][j+1] + u[i][j-1]) + f(x_i, t_j) * h * h) / (2*a+2*b)
        u = next_u.copy()
        u_masked = u.copy()
        u_masked[np.isnan(mask)] = np.nan 
        diff_norm = 0
        for i in range(1, n):
            for j in range(1, n):
                diff_norm = max(diff_norm, abs(u[i][j] - prev_u[i][j]))
    
        solution_error = 0
        for i in range(1, n):
            for j in range(1, n):
                solution_error = max(solution_error, abs(u[i][j] - exact_solution[i][j]))
        
        iteration += 1
        update_iteration_info("Якоби", iteration, diff_norm, solution_error)

        if iteration % skip_value != 0:
            return img,
        
        img.set_array(u_masked.T)
        img.set_clim(np.min(u), np.max(u))
        
        return img,
    
    ani = FuncAnimation(
        fig, 
        update, 
        frames=range(5000),
        interval=100,      
        blit=True,         
        repeat=False       
    )
    
    plt.tight_layout()
    plt.show()

def plot_real_function():
    n = int(entry_step.get()) + 1
    step = 1 / n
    X = np.arange(0, 1, step)
    Y = np.arange(0, 1, step)
    X, Y = np.meshgrid(X, Y)
    Z = real_u(X, Y)

    plt.figure(1, figsize=(8, 6))
    plt.imshow(Z, origin='lower', cmap='magma', extent=(0,1,0,1))
    plt.colorbar(shrink=0.8)
    plt.title("Точное решение", fontsize=12, pad=20)
    plt.show()
def research():
    
    n = int(entry_step.get())
    h = 1 / n
    
    entry_h['text'] = str(h)
# Create main window
root = Tk()
root.geometry('1000x600')
root.configure(bg=BG_COLOR)
root.title("Решение задачи Дирихле для уравнения Пуассона")

style = ttk.Style()
style.configure('TFrame', background=BG_COLOR)
style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 10))
style.configure('TButton', background=BUTTON_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 10), borderwidth=1)
style.configure('TLabelframe', background=FRAME_COLOR, relief='solid', borderwidth=1)
style.configure('TLabelframe.Label', background=FRAME_COLOR, foreground=ACCENT_COLOR, font=('Helvetica', 10, 'bold'))
style.configure('TEntry', fieldbackground='white', foreground=TEXT_COLOR)

frm = ttk.Frame(root, padding=15)
frm.pack(fill=BOTH, expand=True)

# Parameters frame
params_frame = ttk.LabelFrame(frm, text="Параметры решения", padding=10)
params_frame.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

label_step = ttk.Label(params_frame, text='Размерность сетки:')
label_step.grid(column=0, row=0, sticky="w", pady=3)

entry_step = ttk.Entry(params_frame, width=10)
entry_step.insert(0, '10')
entry_step.grid(column=1, row=0, padx=5, pady=3)

label_error = ttk.Label(params_frame, text='Точность (ε):')
label_error.grid(column=0, row=1, sticky="w", pady=3)


label_h = ttk.Label(params_frame, text='Шаг:')
label_h.grid(column=2, row=0, sticky="w", pady=3)
entry_h = ttk.Label(params_frame, width=10)
entry_h['text'] = '0.1'
entry_h.grid(column=3, row=0, padx=5, pady=3)
entry_error = ttk.Entry(params_frame, width=10)
entry_error.insert(0, '0.01')
entry_error.grid(column=1, row=1, padx=5, pady=3)

label_skip = ttk.Label(params_frame, text='Частота отрисовки:')
label_skip.grid(column=0, row=2, sticky="w", pady=3)

entry_skip = ttk.Entry(params_frame, width=10)
entry_skip.insert(0, '10')
entry_skip.grid(column=1, row=2, padx=5, pady=3)

# Eigenvalues frame
eigen_frame = ttk.LabelFrame(frm, text="Собственные значения", padding=10)
eigen_frame.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")

label_min_eigen = ttk.Label(eigen_frame, text='Минимальное:')
label_min_eigen.grid(column=0, row=0, sticky="w", pady=3)

label_min_eigen_value = ttk.Label(eigen_frame, text='0', foreground=ACCENT_COLOR, font=('Helvetica', 10, 'bold'))
label_min_eigen_value.grid(column=1, row=0, padx=5, pady=3)

label_max_eigen = ttk.Label(eigen_frame, text='Максимальное:')
label_max_eigen.grid(column=0, row=1, sticky="w", pady=3)

label_max_eigen_value = ttk.Label(eigen_frame, text='0', foreground=ACCENT_COLOR, font=('Helvetica', 10, 'bold'))
label_max_eigen_value.grid(column=1, row=1, padx=5, pady=3)

# Buttons frame
buttons_frame = ttk.Frame(frm, padding=10)
buttons_frame.grid(column=0, row=1, columnspan=2, padx=5, pady=10, sticky="nsew")

btn_style = {'width': 20, 'padding': 5}
btn_style2 = {'width': 30, 'padding': 5}
ttk.Button(buttons_frame, text='Точное решение', command=plot_real_function, style='TButton', **btn_style).grid(column=0, row=0, padx=5)
ttk.Button(buttons_frame, text='Метод Якоби', command=plot_jacobi_method, style='TButton', **btn_style).grid(column=1, row=0, padx=5)
ttk.Button(buttons_frame, text='Метод Минимальных невязок', command=plot_min_desc_method, style='TButton', **btn_style2).grid(column=2, row=0, padx=5)
ttk.Button(buttons_frame, text='Найти собственные значения', command=find_eigen_values, style='TButton', **btn_style2).grid(column=3, row=0, padx=5)
ttk.Button(buttons_frame, text='Обновить шаг', command=research, style='TButton', **btn_style).grid(column=0, row=1, padx=5)

# Iteration info frames
iter_frame_jacobi = ttk.LabelFrame(frm, text="Метод Якоби - информация", padding=10)
iter_frame_jacobi.grid(column=0, row=2, padx=5, pady=5, sticky="nsew")

label_method_jacobi = ttk.Label(iter_frame_jacobi, text="Метод: ")
label_method_jacobi.grid(column=0, row=0, sticky="w", pady=2)

label_iteration_jacobi = ttk.Label(iter_frame_jacobi, text="Итерация: ")
label_iteration_jacobi.grid(column=0, row=1, sticky="w", pady=2)

label_diff_norm_jacobi = ttk.Label(iter_frame_jacobi, text="Норма разности: ")
label_diff_norm_jacobi.grid(column=0, row=2, sticky="w", pady=2)

label_solution_error_jacobi = ttk.Label(iter_frame_jacobi, text="Ошибка решения: ")
label_solution_error_jacobi.grid(column=0, row=3, sticky="w", pady=2)

iter_frame_desc = ttk.LabelFrame(frm, text="Метод Минимальных невязок - информация", padding=10)
iter_frame_desc.grid(column=1, row=2, padx=5, pady=5, sticky="nsew")

label_method_desc = ttk.Label(iter_frame_desc, text="Метод: ")
label_method_desc.grid(column=0, row=0, sticky="w", pady=2)

label_iteration_desc = ttk.Label(iter_frame_desc, text="Итерация: ")
label_iteration_desc.grid(column=0, row=1, sticky="w", pady=2)

label_diff_norm_desc = ttk.Label(iter_frame_desc, text="Норма разности: ")
label_diff_norm_desc.grid(column=0, row=2, sticky="w", pady=2)

label_solution_error_desc = ttk.Label(iter_frame_desc, text="Ошибка решения: ")
label_solution_error_desc.grid(column=0, row=3, sticky="w", pady=2)

label_alpha_desc = ttk.Label(iter_frame_desc, text="")
label_alpha_desc.grid(column=0, row=4, sticky="w", pady=2)

# Configure grid weights
frm.columnconfigure(0, weight=1)
frm.columnconfigure(1, weight=1)
frm.rowconfigure(0, weight=0)
frm.rowconfigure(1, weight=0)
frm.rowconfigure(2, weight=1)

root.mainloop()