import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyvista as pv

# Класс слоя композита
class CompositeLayer:
    def __init__(self, thickness, theta_deg, E1, E2, G12, nu12):
        self.thickness = thickness
        self.theta = np.radians(theta_deg)
        self.E1 = E1
        self.E2 = E2
        self.G12 = G12
        self.nu12 = nu12
        self.nu21 = (E2 / E1) * nu12
        self.Q = self.calc_local_stiffness_matrix()

    def calc_local_stiffness_matrix(self):
        denom = 1 - self.nu12 * self.nu21
        Q11 = self.E1 / denom
        Q22 = self.E2 / denom
        Q12 = self.nu12 * self.E2 / denom
        Q66 = self.G12
        Q = np.array([
            [Q11, Q12, 0],
            [Q12, Q22, 0],
            [0,   0,   Q66]
        ])
        return Q

    def transform_Q(self):
        m = np.cos(self.theta)
        n = np.sin(self.theta)
        T = np.array([
            [m**2, n**2, 2*m*n],
            [n**2, m**2, -2*m*n],
            [-m*n, m*n, m**2 - n**2]
        ])
        T_inv = np.linalg.inv(T)
        Qbar = T_inv @ self.Q @ T_inv.T
        return Qbar

# Класс композитного ламината
class CompositeLaminate:
    def __init__(self, layers):
        self.layers = layers
        self.total_thickness = sum(layer.thickness for layer in layers)
        self.z = self.calc_z_coordinates()

    def calc_z_coordinates(self):
        z = [-self.total_thickness / 2]
        for layer in self.layers:
            z.append(z[-1] + layer.thickness)
        return z

    def stiffness_matrices(self):
        A = np.zeros((3, 3))
        B = np.zeros((3, 3))
        D = np.zeros((3, 3))
        for i, layer in enumerate(self.layers):
            Qbar = layer.transform_Q()
            z_k = self.z[i]
            z_k1 = self.z[i + 1]
            dz = z_k1 - z_k
            A += Qbar * dz
            B += 0.5 * Qbar * (z_k1 ** 2 - z_k ** 2)
            D += (1 / 3) * Qbar * (z_k1 ** 3 - z_k ** 3)
        return {'A': A, 'B': B, 'D': D}

    def ABD_matrix(self):
        mats = self.stiffness_matrices()
        A = mats['A']
        B = mats['B']
        D = mats['D']
        ABD = np.block([
            [A, B],
            [B, D]
        ])
        return ABD

    def solve_midplane_strain_curvature(self, N, M):
        ABD = self.ABD_matrix()
        load = np.hstack((N, M))
        try:
            solution = np.linalg.solve(ABD, load)
        except np.linalg.LinAlgError:
            raise ValueError("Матрица ABD вырождена и не может быть обращена.")
        epsilon_0 = solution[:3]
        kappa = solution[3:]
        return epsilon_0, kappa

    def stress_in_layer(self, layer_index, epsilon_0, kappa):
        z_mid = 0.5 * (self.z[layer_index] + self.z[layer_index + 1])
        strain = epsilon_0 + kappa * z_mid
        layer = self.layers[layer_index]
        Qbar = layer.transform_Q()
        sigma = Qbar @ strain
        return sigma

    def stress_analysis(self, epsilon_0, kappa):
        stresses = []
        for i in range(len(self.layers)):
            sigma = self.stress_in_layer(i, epsilon_0, kappa)
            stresses.append(sigma)
        return stresses

# Диалог для добавления слоя с Combobox для толщины
class LayerInputDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавить слой")
        self.resizable(False, False)
        self.result = None

        thickness_options = [0.05 * i for i in range(1, 21)]  # 0.05 мм ... 1.00 мм с шагом 0.05 мм

        ttk.Label(self, text="Толщина слоя (мм):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.thickness_var = tk.StringVar(value="0.10")
        self.thickness_combo = ttk.Combobox(self, textvariable=self.thickness_var,
                                            values=[f"{v:.2f}" for v in thickness_options], width=10)
        self.thickness_combo.grid(row=0, column=1, padx=5, pady=5)
        self.thickness_combo.set("0.10")  # Значение по умолчанию
        self.thickness_combo['state'] = 'normal'  # Можно менять вручную, если хотите запретить - 'readonly'

        ttk.Label(self, text="Угол ориентации (град):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.theta_var = tk.DoubleVar(value=0.0)
        ttk.Entry(self, textvariable=self.theta_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Модуль упругости E1 (ГПа):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.E1_var = tk.DoubleVar(value=130.0)
        ttk.Entry(self, textvariable=self.E1_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Модуль упругости E2 (ГПа):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.E2_var = tk.DoubleVar(value=10.0)
        ttk.Entry(self, textvariable=self.E2_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self, text="Модуль сдвига G12 (ГПа):").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.G12_var = tk.DoubleVar(value=5.0)
        ttk.Entry(self, textvariable=self.G12_var).grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self, text="Коэффициент Пуассона nu12:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.nu12_var = tk.DoubleVar(value=0.3)
        ttk.Entry(self, textvariable=self.nu12_var).grid(row=5, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.on_add).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side='left', padx=5)

    def on_add(self):
        try:
            thickness_str = self.thickness_combo.get()
            thickness = float(thickness_str)
            theta = self.theta_var.get()
            E1 = self.E1_var.get()
            E2 = self.E2_var.get()
            G12 = self.G12_var.get()
            nu12 = self.nu12_var.get()

            if thickness <= 0:
                raise ValueError("Толщина должна быть положительной.")
            if not (0 <= nu12 <= 0.5):
                raise ValueError("Коэффициент Пуассона должен быть в диапазоне 0..0.5.")
            if E1 <= 0 or E2 <= 0 or G12 <= 0:
                raise ValueError("Модули упругости должны быть положительными.")

            self.result = (thickness, theta, E1, E2, G12, nu12)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка ввода", str(e))

# Главный класс приложения
class CompositeLaminateApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расчет композитного ламината с моделью сосуда")
        self.geometry("950x700")
        self.resizable(True, True)

        self.laminate = None
        self.create_widgets()

    def create_widgets(self):
        # Рамка параметров слоев
        self.frame_layers = ttk.LabelFrame(self, text="Параметры слоев композита")
        self.frame_layers.pack(fill='x', padx=10, pady=5)

        self.layers_tree = ttk.Treeview(self.frame_layers,
                                        columns=("thickness", "theta", "E1", "E2", "G12", "nu12"),
                                        show='headings', height=6)
        col_names = {"thickness": "Толщина (мм)", "theta": "Угол (°)", "E1": "E1 (ГПа)",
                     "E2": "E2 (ГПа)", "G12": "G12 (ГПа)", "nu12": "nu12"}
        for col, name in col_names.items():
            self.layers_tree.heading(col, text=name)
            self.layers_tree.column(col, width=100, anchor='center')
        self.layers_tree.pack(side='left', fill='x', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.frame_layers)
        btn_frame.pack(side='left', fill='y', padx=5)
        ttk.Button(btn_frame, text="Добавить слой", command=self.add_layer_dialog).pack(pady=5)
        ttk.Button(btn_frame, text="Удалить слой", command=self.delete_selected_layer).pack(pady=5)
        ttk.Button(btn_frame, text="Очистить все", command=self.clear_layers).pack(pady=5)

        # Рамка параметров сосуда
        self.frame_shell = ttk.LabelFrame(self, text="Параметры цилиндрического сосуда")
        self.frame_shell.pack(fill='x', padx=10, pady=5)

        ttk.Label(self.frame_shell, text="Радиус (м):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.radius_var = tk.DoubleVar(value=0.25)
        ttk.Entry(self.frame_shell, textvariable=self.radius_var, width=15).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_shell, text="Длина (м):").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.length_var = tk.DoubleVar(value=1.0)
        ttk.Entry(self.frame_shell, textvariable=self.length_var, width=15).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.frame_shell, text="Толщина стенки (мм):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.wall_thickness_var = tk.DoubleVar(value=10.0)
        ttk.Entry(self.frame_shell, textvariable=self.wall_thickness_var, width=15).grid(row=1, column=1, padx=5, pady=5)

        # Давление
        self.frame_pressure = ttk.LabelFrame(self, text="Нагрузки и давление")
        self.frame_pressure.pack(fill='x', padx=10, pady=5)

        ttk.Label(self.frame_pressure, text="Внутреннее давление (Па):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.p_internal_var = tk.DoubleVar(value=1e6)
        ttk.Entry(self.frame_pressure, textvariable=self.p_internal_var, width=15).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_pressure, text="Скорость жидкости (м/с):").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.velocity_var = tk.DoubleVar(value=0.0)
        ttk.Entry(self.frame_pressure, textvariable=self.velocity_var, width=15).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.frame_pressure, text="Плотность жидкости (кг/м³):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.density_var = tk.DoubleVar(value=1000.0)
        ttk.Entry(self.frame_pressure, textvariable=self.density_var, width=15).grid(row=1, column=1, padx=5, pady=5)

        # Ввод внешних нагрузок N и M (если требуется)
        self.frame_loads = ttk.LabelFrame(self, text="Внешние нагрузки (N — Н/м, M — Н·м/м)")
        self.frame_loads.pack(fill='x', padx=10, pady=5)

        load_labels = ["Nx", "Ny", "Nxy", "Mx", "My", "Mxy"]
        self.load_vars = []
        for i, label in enumerate(load_labels):
            ttk.Label(self.frame_loads, text=label).grid(row=0, column=i, padx=5)
            var = tk.DoubleVar(value=0.0)
            self.load_vars.append(var)
            ttk.Entry(self.frame_loads, textvariable=var, width=10).grid(row=1, column=i, padx=5)

        # Кнопки
        btn_frame_main = ttk.Frame(self)
        btn_frame_main.pack(fill='x', padx=10, pady=10)

        self.btn_calculate = ttk.Button(btn_frame_main, text="Выполнить расчет", command=self.calculate)
        self.btn_calculate.pack(side='left', padx=5)

        self.btn_visualize = ttk.Button(btn_frame_main, text="Показать 3D модель сосуда", command=self.visualize_3d)
        self.btn_visualize.pack(side='left', padx=5)
        self.btn_visualize['state'] = 'disabled'

        self.btn_save = ttk.Button(btn_frame_main, text="Сохранить результаты", command=self.save_results)
        self.btn_save.pack(side='left', padx=5)
        self.btn_save['state'] = 'disabled'

        # Окно вывода результатов
        self.text_output = tk.Text(self, height=20, wrap='word')
        self.text_output.pack(fill='both', expand=True, padx=10, pady=5)

    def add_layer_dialog(self):
        dlg = LayerInputDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            thickness, theta, E1, E2, G12, nu12 = dlg.result
            self.layers_tree.insert('', 'end', values=(f"{thickness:.3f}", f"{theta:.1f}",
                                                       f"{E1:.3f}", f"{E2:.3f}", f"{G12:.3f}", f"{nu12:.3f}"))

    def delete_selected_layer(self):
        selected = self.layers_tree.selection()
        for item in selected:
            self.layers_tree.delete(item)

    def clear_layers(self):
        for item in self.layers_tree.get_children():
            self.layers_tree.delete(item)

    def calculate(self):
        try:
            # Слои
            layers = []
            for item in self.layers_tree.get_children():
                vals = self.layers_tree.item(item)['values']
                thickness = float(vals[0]) / 1000.0  # мм -> м
                theta = float(vals[1])
                E1 = float(vals[2]) * 1e9  # ГПа -> Па
                E2 = float(vals[3]) * 1e9
                G12 = float(vals[4]) * 1e9
                nu12 = float(vals[5])
                layer = CompositeLayer(thickness, theta, E1, E2, G12, nu12)
                layers.append(layer)

            if not layers:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один слой.")
                return

            self.laminate = CompositeLaminate(layers)

            # Геометрия сосуда
            R = self.radius_var.get()
            L = self.length_var.get()
            wall_thickness = self.wall_thickness_var.get() / 1000.0  # мм -> м
            if wall_thickness <= 0 or R <= 0 or L <= 0:
                messagebox.showerror("Ошибка", "Параметры геометрии должны быть положительными.")
                return

            # Внутреннее и динамическое давление
            p_internal = self.p_internal_var.get()
            velocity = self.velocity_var.get()
            density = self.density_var.get()

            if density < 0 or p_internal < 0 or velocity < 0:
                messagebox.showerror("Ошибка", "Давление, скорость и плотность должны быть неотрицательными.")
                return

            # Динамическое давление жидкости (динамическая нагрузка) p_dyn = 0.5 * rho * v^2
            p_dynamic = 0.5 * density * velocity ** 2

            # Полное внутреннее давление
            p_total = p_internal + p_dynamic

            # Расчет усилий мембранных (адаптируем для нашего ламината):
            # Nx = p_total * R, Ny = p_total * R / 2, Nxy=0 (упрощение для цилиндра)
            Nx = p_total * wall_thickness * R  # умножаем на толщину ламината, чтобы получить силу на метр ширины
            Ny = p_total * wall_thickness * R / 2
            Nxy = 0.0

            # Моменты считаем нулевыми
            Mx = My = Mxy = 0.0

            # Добавим внешние нагрузки из формы
            N_user = np.array([var.get() for var in self.load_vars[:3]])
            M_user = np.array([var.get() for var in self.load_vars[3:]])

            N = np.array([Nx, Ny, Nxy]) + N_user
            M = np.array([Mx, My, Mxy]) + M_user

            # Решение
            epsilon_0, kappa = self.laminate.solve_midplane_strain_curvature(N, M)
            stresses = self.laminate.stress_analysis(epsilon_0, kappa)

            # Вывод
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, f"Параметры сосуда:\n")
            self.text_output.insert(tk.END, f"  Радиус: {R:.4f} м\n  Длина: {L:.4f} м\n  Толщина: {wall_thickness:.6f} м\n\n")
            self.text_output.insert(tk.END, f"Внутреннее давление: {p_internal:.2f} Па\n")
            self.text_output.insert(tk.END, f"Динамическое давление: {p_dynamic:.2f} Па\n")
            self.text_output.insert(tk.END, f"Общее давление: {p_total:.2f} Па\n\n")
            self.text_output.insert(tk.END, "Расчетные мембранные усилия N (Н/м):\n")
            self.text_output.insert(tk.END, f"  Nx = {N[0]:.4e}, Ny = {N[1]:.4e}, Nxy = {N[2]:.4e}\n")
            self.text_output.insert(tk.END, "Моменты M (Н·м/м):\n")
            self.text_output.insert(tk.END, f"  Mx = {M[0]:.4e}, My = {M[1]:.4e}, Mxy = {M[2]:.4e}\n\n")

            self.text_output.insert(tk.END, f"Общая толщина ламината: {self.laminate.total_thickness:.6f} м\n\n")

            mats = self.laminate.stiffness_matrices()
            fmt = {'float_kind': lambda x: f"{x:.3e}"}
            self.text_output.insert(tk.END, "Матрица A (Н/м):\n")
            self.text_output.insert(tk.END, np.array2string(mats['A'], precision=3, formatter=fmt) + "\n\n")
            self.text_output.insert(tk.END, "Матрица B (Н):\n")
            self.text_output.insert(tk.END, np.array2string(mats['B'], precision=3, formatter=fmt) + "\n\n")
            self.text_output.insert(tk.END, "Матрица D (Н·м):\n")
            self.text_output.insert(tk.END, np.array2string(mats['D'], precision=3, formatter=fmt) + "\n\n")

            self.text_output.insert(tk.END, f"Средние деформации ε0:\n{epsilon_0}\n\n")
            self.text_output.insert(tk.END, f"Кривизна κ:\n{kappa}\n\n")

            self.text_output.insert(tk.END, "Напряжения по слоям (Па):\n")
            for i, sigma in enumerate(stresses, 1):
                self.text_output.insert(tk.END, f"  Слой {i}: σx={sigma[0]:.4e}, σy={sigma[1]:.4e}, τxy={sigma[2]:.4e}\n")

            self.btn_save['state'] = 'normal'
            self.btn_visualize['state'] = 'normal'

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при расчете:\n{e}")

    def save_results(self):
        if not self.laminate:
            messagebox.showwarning("Внимание", "Нет результатов для сохранения.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not filename:
            return

        try:
            text = self.text_output.get(1.0, tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
            messagebox.showinfo("Сохранено", f"Результаты сохранены в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def visualize_3d(self):
        # Простая 3D модель цилиндра с цветовой заливкой по совокупной напряженности σ_eq

        if not self.laminate:
            messagebox.showwarning("Внимание", "Сначала выполните расчет.")
            return

        # Габариты
        R = self.radius_var.get()
        L = self.length_var.get()
        thickness = self.wall_thickness_var.get() / 1000.0

        n_theta = 60
        n_length = 30

        theta = np.linspace(0, 2 * np.pi, n_theta)
        z = np.linspace(0, L, n_length)
        Theta, Z = np.meshgrid(theta, z)

        X_outer = (R + thickness / 2) * np.cos(Theta)
        Y_outer = (R + thickness / 2) * np.sin(Theta)
        Z_outer = Z

        X_inner = (R - thickness / 2) * np.cos(Theta)
        Y_inner = (R - thickness / 2) * np.sin(Theta)
        Z_inner = Z

        points_outer = np.vstack((X_outer.ravel(), Y_outer.ravel(), Z_outer.ravel())).T

        stresses = self.laminate.stress_analysis(*self.laminate.solve_midplane_strain_curvature(
            np.array([
                self.p_internal_var.get() * thickness * R,
                self.p_internal_var.get() * thickness * R / 2,
                0
            ]),
            np.zeros(3)
        ))

        sigma_layer1 = stresses[0]
        sigma_eq = np.linalg.norm(sigma_layer1)  # число для цвета

        scalars = np.full(points_outer.shape[0], sigma_eq)

        mesh = pv.StructuredGrid()
        mesh.points = points_outer
        mesh.dimensions = (n_theta, n_length, 1)

        mesh.point_data["σ_eq"] = scalars

        plotter = pv.Plotter()
        plotter.add_mesh(mesh, scalars="σ_eq", cmap='jet', show_edges=True)
        plotter.add_axes()
        plotter.show()

if __name__ == "__main__":
    app = CompositeLaminateApp()
    app.mainloop()
