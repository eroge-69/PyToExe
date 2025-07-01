import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math

# Плотности материалов (кг/м3)
DENSITIES = {
    "Бетон": 2400,
    "Кирпич": 1800,
    "Гипсокартон": 800,
    "Минвата": 150,
    "Пенопласт": 30
}

# Расчёт массы на м2 по закону Рэлея: L = 20*log10(m*f) - 47.4
# Обратная формула: m = 10**((L + 47.4)/20) / f
def mass_per_area(L, f):
    return 10**((L + 47.4) / 20) / f

class SoundInsulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расчёт звукоизоляции")
        self.geometry("650x500")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)
        self.create_widgets()

    def create_widgets(self):
        # Режим
        self.mode = tk.StringVar(value="new")
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="Планируется", variable=self.mode,
                        value="new", command=self.on_mode_change).pack(side="left")
        ttk.Radiobutton(mode_frame, text="Уже есть", variable=self.mode,
                        value="exist", command=self.on_mode_change).pack(side="left", padx=10)

        # Форма ввода
        self.frm = ttk.Frame(self)
        self.frm.grid(row=1, column=0, sticky="ew", padx=10)
        self.frm.columnconfigure(1, weight=1)
        self.frm.columnconfigure(3, weight=1)

        # Первая стена
        ttk.Label(self.frm, text="Материал стены:").grid(row=0, column=0, sticky="w")
        self.material = ttk.Combobox(self.frm, values=list(DENSITIES.keys()), state="readonly")
        self.material.current(0)
        self.material.grid(row=0, column=1, sticky="ew")
        ttk.Label(self.frm, text="Толщина стены (мм):").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.wall1_th = ttk.Entry(self.frm)
        self.wall1_th.insert(0, "100")
        self.wall1_th.grid(row=0, column=3, sticky="ew")

        # Частота и ослабление
        ttk.Label(self.frm, text="Частота (Гц):").grid(row=1, column=0, sticky="w")
        self.freq = ttk.Entry(self.frm)
        self.freq.insert(0, "1000")
        self.freq.grid(row=1, column=1, sticky="ew")
        ttk.Label(self.frm, text="Требуемое ослабление (дБ):").grid(row=1, column=2, sticky="w", padx=(10,0))
        self.Lreq = ttk.Entry(self.frm)
        self.Lreq.insert(0, "50")
        self.Lreq.grid(row=1, column=3, sticky="ew")

        # Вторая стена (режим exist)
        self.lbl_mat2 = ttk.Label(self.frm, text="Материал второй стены:")
        self.lbl_mat2.grid(row=2, column=0, sticky="w")
        self.material2 = ttk.Combobox(self.frm, values=list(DENSITIES.keys()), state="readonly")
        self.material2.current(0)
        self.material2.grid(row=2, column=1, sticky="ew")
        self.lbl_th2 = ttk.Label(self.frm, text="Толщина второй стены (мм):")
        self.lbl_th2.grid(row=2, column=2, sticky="w", padx=(10,0))
        self.wall2_th = ttk.Entry(self.frm)
        self.wall2_th.insert(0, "100")
        self.wall2_th.grid(row=2, column=3, sticky="ew")

        # Материал изоляции (режим exist)
        self.lbl_ins = ttk.Label(self.frm, text="Материал изоляции:")
        self.lbl_ins.grid(row=3, column=0, sticky="w")
        self.ins_material = ttk.Combobox(self.frm, values=list(DENSITIES.keys()), state="readonly")
        self.ins_material.current(list(DENSITIES.keys()).index("Минвата"))
        self.ins_material.grid(row=3, column=1, sticky="ew")

        # Кнопка расчёта
        self.calc_btn = ttk.Button(self.frm, text="Рассчитать", command=self.calculate)
        self.calc_btn.grid(row=4, column=0, columnspan=4, pady=10)

        # Результат
        self.result = ttk.Label(self, text="", font=("Arial", 12))
        self.result.grid(row=2, column=0, sticky="n")

        # Canvas
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        self.canvas.bind("<Configure>", lambda e: self.draw_canvas())

        self.on_mode_change()

    def on_mode_change(self):
        exists = self.mode.get() == "exist"
        for w in (self.lbl_mat2, self.material2, self.lbl_th2, self.wall2_th, self.lbl_ins, self.ins_material):
            if exists:
                w.grid()
            else:
                w.grid_remove()
        self.draw_canvas()

    def calculate(self):
        try:
            f = float(self.freq.get())
            L = float(self.Lreq.get())
            t1 = float(self.wall1_th.get()) / 1000
            rho1 = DENSITIES[self.material.get()]
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ввод данных")
            return

        if self.mode.get() == "new":
            m_req = mass_per_area(L, f)
            thick = m_req / rho1
            res = f"Необходимая толщина стены: {thick*1000:.1f} мм"
        else:
            try:
                t2 = float(self.wall2_th.get()) / 1000
                rho2 = DENSITIES[self.material2.get()]
                rho_ins = DENSITIES[self.ins_material.get()]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный ввод данных")
                return
            m_req = mass_per_area(L, f)
            m_known = rho1 * t1 + rho2 * t2
            m_ins = max(0, m_req - m_known)
            thick_ins = m_ins / rho_ins
            res = (f"Материал изоляции: {self.ins_material.get()}\n"
                   f"Толщина изоляции: {thick_ins*1000:.1f} мм")
        self.result.config(text=res)
        self.draw_canvas()

    def draw_canvas(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        try:
            t1 = float(self.wall1_th.get())
        except:
            t1 = 100
        if self.mode.get() == "exist":
            try:
                ins = float(self.result.cget("text").split()[2])
            except:
                ins = 50
            try:
                t2 = float(self.wall2_th.get())
            except:
                t2 = 100
            layers = [t1, ins, t2]
            colors = ["#999", "#fc0", "#999"]
            texts = ["Стена", "Изоляция", "Стена"]
        else:
            try:
                thick = float(self.result.cget("text").split()[2])
            except:
                thick = 100
            layers = [thick]
            colors = ["#999"]
            texts = ["Стена"]
        total = sum(layers)
        if total <= 0:
            return
        scale = (w - 20) / total
        x = 10
        y0, y1 = h-30, 30
        for i, val in enumerate(layers):
            x1 = x + val * scale
            self.canvas.create_rectangle(x, y0, x1, y1, fill=colors[i], outline="#000")
            cx = x + (x1 - x) / 2
            cy = y1 + 10
            self.canvas.create_text(cx, cy, text=texts[i], font=("Arial", 10, "bold"))
            x = x1

if __name__ == "__main__":
    SoundInsulationApp().mainloop()
