# -*- coding: utf-8 -*-
"""
onco_entropy_gui.py
Программа для ввода клинических данных пациента и построения прогноза
по модели «энтропия – рак».  Графический интерфейс реализован на tkinter,
графики – matplotlib, интеграция ОДУ – scipy.integrate.solve_ivp.

Требуемые пакеты:
    pip install matplotlib scipy
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.integrate import solve_ivp
import csv
import os

# ----------------------------------------------------------------------
# -------------------------- Модель ------------------------------------
# ----------------------------------------------------------------------
class EntropyCancerModel:
    """
    Класс, реализующий систему ОДУ из пунктов 2‑3 ваших материалов:

        dS/dt = c * M(t) + d * D(t)
        dV/dt = -k * dS/dt + a * M(t) - b * D(t)

    Параметры модели задаются в конструкторе.
    """
    def __init__(self,
                 k: float = 1.0,
                 a: float = 0.5,
                 b: float = 0.5,
                 c: float = 0.3,
                 d: float = 0.2):
        self.k = k
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def rhs(self, t, y, M_func, D_func):
        """
        Правая часть ОДУ.
        y[0] = S(t) – энтропия
        y[1] = V(t) – восстановительная функция
        M_func(t) и D_func(t) – функции метаболической активности и уровня повреждений.
        """
        S, V = y
        M = M_func(t)
        D = D_func(t)

        dSdt = self.c * M + self.d * D
        dVdt = -self.k * dSdt + self.a * M - self.b * D
        return [dSdt, dVdt]

    def predict(self,
                t_start: float,
                S0: float,
                V0: float,
                t_end: float,
                M_func,
                D_func,
                dt: float = 0.1):
        """
        Интегрирует систему от t_start до t_end.
        Возвращает массивы времени, S(t) и V(t).
        """
        sol = solve_ivp(
            fun=lambda t, y: self.rhs(t, y, M_func, D_func),
            t_span=(t_start, t_end),
            y0=[S0, V0],
            method='RK45',
            t_eval=np.arange(t_start, t_end + dt, dt),
            vectorized=False,
            rtol=1e-6,
            atol=1e-9,
        )
        if not sol.success:
            raise RuntimeError("Интегрирование ODE не удалось")
        return sol.t, sol.y[0], sol.y[1]

# ----------------------------------------------------------------------
# -------------------------- GUI ---------------------------------------
# ----------------------------------------------------------------------
class OncoEntropyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Прогноз онкологического состояния (энтропия)")
        self.geometry("1600x840")
        self.resizable(False, False)

        # --- модель с «по‑умолчанию» коэффициентами ---
        self.model = EntropyCancerModel()

        # хранилище введённых точек
        self.points = []   # каждый элемент: dict(time, S, M, D, stage)

        # UI
        self._create_widgets()
        self._create_plot()

    # ------------------------------------------------------------------
    def _create_widgets(self):
        # Левая панель – ввод данных
        left = ttk.Frame(self, padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Этап наблюдения", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 5)
        )

        # --------------------------------------------------------------
        # 1️⃣ Список, который используется при построении GUI
        stages = [
            "Подготовка к лечению",   # Pre‑treatment
            "Лечение",               # Treatment
            "Ремиссия",              # Remission
            "Выздоровление"          # Cured
        ]
        # --------------------------------------------------------------

        self.entries = {}   # (stage, field) -> widget

        for i, stg in enumerate(stages, start=1):
            ttk.Label(left, text=stg + ":", foreground="#003366").grid(
                row=i, column=0, sticky="w", pady=2
            )
            frame = ttk.Frame(left)
            frame.grid(row=i, column=1, sticky="w")
            # поля: time, S, M, D
            for j, name in enumerate(["time (мес)", "S", "M", "D"]):
                e = ttk.Entry(frame, width=8)
                e.grid(row=0, column=j, padx=2)
                self.entries[(stg, name)] = e

        # Кнопки управления
        btn_frame = ttk.Frame(left, padding=(0, 20, 0, 0))
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        ttk.Button(btn_frame, text="Построить график", command=self.build_plot).grid(
            row=0, column=0, padx=5, pady=5
        )
        ttk.Button(btn_frame, text="Сохранить CSV", command=self.save_csv).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(btn_frame, text="Сохранить PNG", command=self.save_png).grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Button(btn_frame, text="Настройки модели", command=self.open_settings).grid(
            row=0, column=3, padx=5, pady=5
        )

    # ------------------------------------------------------------------
    def _create_plot(self):
        # Правая панель – график
        right = ttk.Frame(self, padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.ax.set_title("Прогноз изменения энтропии и восстановления")
        self.ax.set_xlabel("Время, мес.")
        self.ax.set_ylabel("Значения")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    def _collect_input(self):
        """Собирает данные из полей ввода, проверяет корректность."""
        self.points.clear()

        # --------------------------------------------------------------
        # 2️⃣ Порядок, в котором программа «читает» введённые точки
        stages_order = [
            "Подготовка к лечению",
            "Лечение",
            "Ремиссия",
            "Выздоровление"
        ]
        # --------------------------------------------------------------

        for stg in stages_order:
            raw = {
                "time": self.entries[(stg, "time (мес)")].get().strip(),
                "S": self.entries[(stg, "S")].get().strip(),
                "M": self.entries[(stg, "M")].get().strip(),
                "D": self.entries[(stg, "D")].get().strip(),
            }
            if all(v == "" for v in raw.values()):
                continue    # точка не задана

            try:
                point = {
                    "stage": stg,
                    "time": float(raw["time"]),
                    "S": float(raw["S"]),
                    "M": float(raw["M"]),
                    "D": float(raw["D"]),
                }
            except ValueError:
                raise ValueError(f"Некорректные числовые данные в блоке {stg}")

            self.points.append(point)

        if not self.points:
            raise ValueError("Не введено ни одной точки наблюдения")
        self.points.sort(key=lambda p: p["time"])

    # ------------------------------------------------------------------
    def _make_piecewise_functions(self):
        """
        Возвращает функции M(t) и D(t), построенные как линейные интерполяции
        между известными точками. Если точка отсутствует, считается, что
        значение остаётся константой (последнее известное).
        """
        times = [p["time"] for p in self.points]
        M_vals = [p["M"] for p in self.points]
        D_vals = [p["D"] for p in self.points]

        def M_func(t):
            if t <= times[0]:
                return M_vals[0]
            if t >= times[-1]:
                return M_vals[-1]
            return np.interp(t, times, M_vals)

        def D_func(t):
            if t <= times[0]:
                return D_vals[0]
            if t >= times[-1]:
                return D_vals[-1]
            return np.interp(t, times, D_vals)

        return M_func, D_func

    # ------------------------------------------------------------------
    def build_plot(self):
        """Основная кнопка – построить график и выполнить предсказание."""
        try:
            self._collect_input()
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        # Последняя известная точка – старт интеграции
        last_point = self.points[-1]
        t_start = last_point["time"]
        S0 = last_point["S"]
        V0 = 0.0                     # пока V0 неизвестна – берём 0

        # Интегрируем модель
        horizon = 12                # по умолчанию – 12 месяцев вперёд
        t_end = t_start + horizon
        M_func, D_func = self._make_piecewise_functions()
        t_pred, S_pred, V_pred = self.model.predict(
            t_start=t_start,
            S0=S0,
            V0=V0,
            t_end=t_end,
            M_func=M_func,
            D_func=D_func,
            dt=0.05
        )

        # --------------------------------------------------------------
        # Очищаем старый график и рисуем новые кривые
        self.ax.clear()
        self.ax.set_title("Прогноз изменения энтропии и восстановления")
        self.ax.set_xlabel("Время, мес.")
        self.ax.set_ylabel("Значения")
        self.ax.grid(True)

        # 1) измеренные точки S
        self.ax.scatter(
            [p["time"] for p in self.points],
            [p["S"] for p in self.points],
            color="blue",
            label="Измеренные S"
        )

        # 2) предсказанная кривая S(t)
        self.ax.plot(t_pred, S_pred, color="red", label="Прогноз S(t)")

        # 3) предсказанная кривая V(t) (добавляем вторую ось)
        self.ax2 = self.ax.twinx()
        self.ax2.plot(t_pred, V_pred, color="green", linestyle="--", label="Прогноз V(t)")
        self.ax2.set_ylabel("V(t)")

        # 4) легенды
        lines, labels = self.ax.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax.legend(lines + lines2, labels + labels2, loc="upper left")
        # --------------------------------------------------------------

        self.canvas.draw()
        # Сохраняем массивы предсказания для экспорта
        self.prediction = {
            "t": t_pred,
            "S": S_pred,
            "V": V_pred
        }

    # ------------------------------------------------------------------
    def save_csv(self):
        """Записывает в CSV все введённые точки и полученный прогноз."""
        if not hasattr(self, "prediction"):
            messagebox.showwarning("Нет графика", "Сначала построьте график")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")],
            title="Сохранить данные как CSV"
        )
        if not file_path:
            return

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Этап", "time (мес)", "S", "M", "D"])
            for p in self.points:
                writer.writerow([
                    p["stage"],
                    f"{p['time']:.2f}",
                    f"{p['S']:.4f}",
                    f"{p['M']:.4f}",
                    f"{p['D']:.4f}"
                ])

            writer.writerow([])   # пустая строка – разделитель
            writer.writerow(["Прогноз"])
            writer.writerow(["time (мес)", "S", "V"])
            for t, S, V in zip(
                self.prediction["t"],
                self.prediction["S"],
                self.prediction["V"]
            ):
                writer.writerow([f"{t:.2f}", f"{S:.4f}", f"{V:.4f}"])

        messagebox.showinfo("Сохранено", f"Данные записаны в {os.path.basename(file_path)}")

    # ------------------------------------------------------------------
    def save_png(self):
        """Экспорт текущего графика в PNG."""
        if not hasattr(self, "prediction"):
            messagebox.showwarning("Нет графика", "Сначала построьте график")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("All files", "*.*")],
            title="Сохранить график как PNG"
        )
        if not file_path:
            return

        self.fig.savefig(file_path, dpi=300, bbox_inches="tight")
        messagebox.showinfo("Сохранено", f"График сохранён в {os.path.basename(file_path)}")

    # ------------------------------------------------------------------
    def open_settings(self):
        """Окно для редактирования коэффициентов модели."""
        SettingsDialog(self, self.model)

# ----------------------------------------------------------------------
# ------------------- Окно настроек модели ----------------------------
# ----------------------------------------------------------------------
class SettingsDialog(tk.Toplevel):
    """Диалоговое окно, где пользователь может изменить коэффициенты модели."""
    def __init__(self, master: tk.Tk, model: EntropyCancerModel):
        super().__init__(master)
        self.title("Настройки модели")
        self.resizable(False, False)
        self.model = model

        self.vars = {}
        for i, name in enumerate(["k", "a", "b", "c", "d"]):
            ttk.Label(self, text=f"{name} =").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            v = tk.DoubleVar(value=getattr(self.model, name))
            entry = ttk.Entry(self, textvariable=v, width=10)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.vars[name] = v

        ttk.Button(self, text="Применить", command=self.apply).grid(
            row=5, column=0, columnspan=2, pady=10
        )

    def apply(self):
        try:
            for name, var in self.vars.items():
                setattr(self.model, name, float(var.get()))
        except ValueError:
            messagebox.showerror("Ошибка", "Все коэффициенты должны быть числами")
            return
        self.destroy()
        messagebox.showinfo("Настройки", "Коэффициенты модели обновлены")

# ----------------------------------------------------------------------
# --------------------------- Запуск -----------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = OncoEntropyApp()
    app.mainloop()