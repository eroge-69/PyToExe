import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

plt.style.use('seaborn')
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['grid.alpha'] = 0.5


def update_plot():
    try:
        params = {
            'm': float(m_entry.get()),
            'L': float(L_entry.get()),
            'L1': float(L1_entry.get()),
            'k': float(k_entry.get()),
            'beta': float(beta_entry.get()),
            'g': float(g_entry.get()),
            'phi1_0': float(phi1_entry.get()),
            'phi2_0': float(phi2_entry.get()),
            't_max': float(t_max_entry.get())
        }

        if (params['m'] <= 0 or params['L'] <= 0 or params['L1'] < 0 or
                params['k'] < 0 or params['beta'] < 0 or params['g'] <= 0 or
                params['t_max'] <= 0):
            raise ValueError("Параметры должны быть положительными (L1, k, β могут быть равны нулю)")

        omega_1 = np.sqrt(params['g'] / params['L'])
        omega_2 = np.sqrt(
            params['g'] / params['L'] + 2 * params['k'] * params['L1'] ** 2 / (params['m'] * params['L'] ** 2))
        freq_label.config(text=f"Нормальные частоты: ω1 = {omega_1:.3f} рад/с, ω2 = {omega_2:.3f} рад/с")

        phi1_0_rad = np.radians(params['phi1_0'])
        phi2_0_rad = np.radians(params['phi2_0'])
        y0 = [phi1_0_rad, 0, phi2_0_rad, 0]
        t_span = (0, params['t_max'])
        t_eval = np.linspace(0, params['t_max'], 1000)

        def system(t, y):
            phi1, omega1, phi2, omega2 = y
            dphi1_dt = omega1
            domega1_dt = (-(params['beta'] / params['m']) * omega1 -
                          (params['g'] / params['L']) * np.sin(phi1) -
                          (params['k'] * params['L1'] ** 2 / (params['m'] * params['L'] ** 2)) * (phi1 - phi2))
            dphi2_dt = omega2
            domega2_dt = (-(params['beta'] / params['m']) * omega2 -
                          (params['g'] / params['L']) * np.sin(phi2) +
                          (params['k'] * params['L1'] ** 2 / (params['m'] * params['L'] ** 2)) * (phi1 - phi2))
            return [dphi1_dt, domega1_dt, dphi2_dt, domega2_dt]

        sol = solve_ivp(system, t_span, y0, t_eval=t_eval, method='RK45')
        phi1, omega1, phi2, omega2, t = sol.y[0], sol.y[1], sol.y[2], sol.y[3], sol.t

        ax1.clear()
        ax2.clear()

        ax1.plot(t, np.degrees(phi1), label='φ1(t)', color='#1f77b4', linewidth=2)
        ax1.plot(t, np.degrees(phi2), label='φ2(t)', color='#ff7f0e', linewidth=2)
        ax1.set_xlabel('Время, с')
        ax1.set_ylabel('Угол, °')
        ax1.set_title('Угловое положение маятников')
        ax1.legend(loc='upper right')
        ax1.grid(True, linestyle='--', alpha=0.7)

        ax2.plot(t, np.degrees(omega1), label='ω1(t)', color='#1f77b4', linewidth=2)
        ax2.plot(t, np.degrees(omega2), label='ω2(t)', color='#ff7f0e', linewidth=2)
        ax2.set_xlabel('Время, с')
        ax2.set_ylabel('Угловая скорость, °/с')
        ax2.set_title('Угловые скорости маятников')
        ax2.legend(loc='upper right')
        ax2.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        canvas.draw()

    except ValueError as e:
        freq_label.config(text=f"Ошибка: {str(e)}", foreground='red')
        ax1.clear()
        ax2.clear()
        ax1.text(0.5, 0.5, 'Ошибка в параметрах',
                 ha='center', va='center', transform=ax1.transAxes, color='red')
        ax2.text(0.5, 0.5, 'Проверьте введенные значения',
                 ha='center', va='center', transform=ax2.transAxes, color='red')
        canvas.draw()


root = tk.Tk()
root.title("Симулятор связанных маятников")
root.geometry("1400x800")
root.minsize(1200, 700)

default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(size=12)
root.option_add("*Font", default_font)

style = ttk.Style()
style.configure('TFrame', background='#f0f0f0')
style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 12))
style.configure('TEntry', font=('Helvetica', 12), padding=5)
style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=8, background='#4CAF50', foreground='white')
style.map('TButton', background=[('active', '#45a049')])

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

params_frame = ttk.LabelFrame(main_frame, text="Параметры системы", padding=(15, 10))
params_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

graph_frame = ttk.Frame(main_frame)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

params = [
    ('Масса маятника, m (кг)', '1.0'),
    ('Длина нити, L (м)', '1.0'),
    ('Расстояние до пружины, L1 (м)', '0.5'),
    ('Жесткость пружины, k (Н/м)', '10.0'),
    ('Коэффициент трения, β (кг/с)', '0.1'),
    ('Ускорение свободного падения, g (м/с²)', '9.81'),
    ('Начальный угол 1-го маятника, φ1(0) (°)', '10.0'),
    ('Начальный угол 2-го маятника, φ2(0) (°)', '5.0'),
    ('Время моделирования, t_max (с)', '20.0')
]

entries = []
for i, (label, default) in enumerate(params):
    frame = ttk.Frame(params_frame)
    frame.pack(fill=tk.X, pady=5)

    ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))
    entry = ttk.Entry(frame)
    entry.insert(0, default)
    entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    entries.append(entry)

m_entry, L_entry, L1_entry, k_entry, beta_entry, g_entry, phi1_entry, phi2_entry, t_max_entry = entries

freq_label = ttk.Label(params_frame, text="Нормальные частоты: ω1 = ?, ω2 = ?",
                       font=('Helvetica', 12, 'bold'), foreground='#333333')
freq_label.pack(pady=(15, 5), fill=tk.X)

update_btn = ttk.Button(params_frame, text="Запустить моделирование", command=update_plot)
update_btn.pack(pady=10, fill=tk.X)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=100)
fig.set_facecolor('#f0f0f0')
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_plot()

root.mainloop()