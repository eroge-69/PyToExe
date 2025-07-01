import tkinter as tk
from tkinter import ttk, messagebox
import math

# Некоторые типовые плотности материалов (кг/м3)
DENSITIES = {
    "Бетон": 2400,
    "Кирпич": 1800,
    "Гипсокартон": 800,
    "Минвата": 150,
    "Пенопласт": 30
}

# Расчёт массы на м2 по закону массы (обратная формула)
def mass_per_area(L, f):
    # L = 20*log10(m*f) - 47.4  =>  m = 10**((L + 47.4)/20) / f
    return 10**((L + 47.4) / 20) / f

class SoundInsulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расчёт звукоизоляции")
        self.geometry("500x400")
        self.create_widgets()

    def create_widgets(self):
        # Тип здания
        self.mode = tk.StringVar(value="new")
        ttk.Radiobutton(self, text="Планируется", variable=self.mode, value="new", command=self.draw_canvas).pack(anchor="w")
        ttk.Radiobutton(self, text="Уже есть",   variable=self.mode, value="exist", command=self.draw_canvas).pack(anchor="w")

        # Общие поля
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=10, pady=10)

        # Материал стены
        ttk.Label(frm, text="Материал стены:").grid(row=0, column=0, sticky="w")
        self.material = ttk.Combobox(frm, values=list(DENSITIES.keys()), state="readonly")
        self.material.current(0)
        self.material.grid(row=0, column=1, sticky="ew")

        # Плотность (отображается, но не редактируется)
        ttk.Label(frm, text="Плотность (кг/м³):").grid(row=1, column=0, sticky="w")
        self.density = ttk.Label(frm, text=str(DENSITIES[self.material.get()]))
        self.density.grid(row=1, column=1, sticky="w")
        self.material.bind("<<ComboboxSelected>>", lambda e: self.density.config(text=str(DENSITIES[self.material.get()])))

        # Частота (Гц)
        ttk.Label(frm, text="Частота (Гц):").grid(row=2, column=0, sticky="w")
        self.freq = ttk.Entry(frm)
        self.freq.insert(0, "1000")
        self.freq.grid(row=2, column=1, sticky="ew")

        # Требуемый коэф. ослабления
        ttk.Label(frm, text="Требуемое ослабление (дБ):").grid(row=3, column=0, sticky="w")
        self.Lreq = ttk.Entry(frm)
        self.Lreq.insert(0, "50")
        self.Lreq.grid(row=3, column=1, sticky="ew")

        # Кнопка расчёта
        ttk.Button(self, text="Рассчитать", command=self.calculate).pack(pady=5)

        # Результат
        self.result = ttk.Label(self, text="", font=("Arial", 12))
        self.result.pack()

        # Canvas для рисунка
        self.canvas = tk.Canvas(self, height=150, bg="white")
        self.canvas.pack(fill="x", padx=10, pady=10)
        self.draw_canvas()

    def calculate(self):
        try:
            f = float(self.freq.get())
            L = float(self.Lreq.get())
            rho = DENSITIES[self.material.get()]
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ввод чисел")
            return

        m = mass_per_area(L, f)  # кг/м2
        thickness = m / rho      # м

        if self.mode.get() == "new":
            text = f"Необходимая толщина стены: {thickness*1000:.1f} мм"
        else:
            # Для существующей стены сначала спросим её толщину
            cur_th = tk.simpledialog.askfloat("Текущая толщина", "Введите текущую толщину стены (мм):")
            if cur_th is None:
                return
            m_cur = rho * (cur_th/1000)
            # Текущее ослабление
            L_cur = 20*math.log10(m_cur * f) - 47.4
            L_add = max(0, L - L_cur)
            m_add = mass_per_area(L_add, f)
            thick_add = m_add / rho
            text = f"Дополнительная толщина изоляции: {thick_add*1000:.1f} мм"
        self.result.config(text=text)
        self.draw_canvas()

    def draw_canvas(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # нарисуем два слоя: стена + изоляция (при существующем режиме)
        wall_th = 50  # мм (пример)
        # масштаб
        scale = w / 300
        # стена
        self.canvas.create_rectangle(10, h-20, 10+wall_th*scale, h- h + 20, fill="#999", outline="#000")
        if self.mode.get() == "exist":
            ins_th = 30  # мм (пример)
            x0 = 10+wall_th*scale
            self.canvas.create_rectangle(x0, h-20, x0+ins_th*scale, h- h + 20, fill="#fc0", outline="#000")
        # подписи
        self.canvas.create_text(10, h-5, anchor="w", text="Стена", font=("Arial", 10, "bold"))
        if self.mode.get() == "exist":
            self.canvas.create_text(10+wall_th*scale, h-5, anchor="w", text="Изоляция", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    app = SoundInsulationApp()
    app.mainloop()
