import tkinter as tk
from tkinter import colorchooser
import colorsys

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s * 100, v * 100

def hsv_to_rgb(h, s, v):
    h = clamp(h, 0, 360) / 360.0
    s = clamp(s, 0, 100) / 100.0
    v = clamp(v, 0, 100) / 100.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r_raw = r * 255
    g_raw = g * 255
    b_raw = b * 255
    was_clamped = (
        r_raw < 0 or r_raw > 255 or
        g_raw < 0 or g_raw > 255 or
        b_raw < 0 or b_raw > 255
    )
    r = round(clamp(r_raw, 0, 255))
    g = round(clamp(g_raw, 0, 255))
    b = round(clamp(b_raw, 0, 255))
    return r, g, b, was_clamped

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100
    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255
    k = min(c, m, y)
    if k == 1:
        return 0, 0, 0, 100
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return c * 100, m * 100, y * 100, k * 100

def cmyk_to_rgb(c, m, y, k):
    c = clamp(c, 0, 100) / 100.0
    m = clamp(m, 0, 100) / 100.0
    y = clamp(y, 0, 100) / 100.0
    k = clamp(k, 0, 100) / 100.0
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    was_clamped = (
        r < 0 or r > 255 or
        g < 0 or g > 255 or
        b < 0 or b > 255
    )
    r = round(clamp(r, 0, 255))
    g = round(clamp(g, 0, 255))
    b = round(clamp(b, 0, 255))
    return r, g, b, was_clamped

Xn, Yn, Zn = 95.047, 100.000, 108.883

def lab_f(t):
    delta = 6/29
    if t > delta**3:
        return t**(1/3)
    else:
        return t / (3 * delta**2) + 4/29

def lab_f_inv(t):
    delta = 6/29
    if t > delta:
        return t**3
    else:
        return 3 * delta**2 * (t - 4/29)

def rgb_to_lab(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    r = r/12.92 if r <= 0.04045 else ((r+0.055)/1.055)**2.4
    g = g/12.92 if g <= 0.04045 else ((g+0.055)/1.055)**2.4
    b = b/12.92 if b <= 0.04045 else ((b+0.055)/1.055)**2.4
    X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    X *= 100
    Y *= 100
    Z *= 100
    fx = lab_f(X / Xn)
    fy = lab_f(Y / Yn)
    fz = lab_f(Z / Zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return L, a, b_val

def lab_to_rgb(L, a, b_val):
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b_val / 200
    X = Xn * lab_f_inv(fx)
    Y = Yn * lab_f_inv(fy)
    Z = Zn * lab_f_inv(fz)
    X /= 100
    Y /= 100
    Z /= 100
    r = X * 3.2404542 - Y * 1.5371385 - Z * 0.4985314
    g = -X * 0.9692660 + Y * 1.8760108 + Z * 0.0415560
    b = X * 0.0556434 - Y * 0.2040259 + Z * 1.0572252
    r_gamma = 12.92 * r if r <= 0.0031308 else 1.055 * r**(1/2.4) - 0.055
    g_gamma = 12.92 * g if g <= 0.0031308 else 1.055 * g**(1/2.4) - 0.055
    b_gamma = 12.92 * b if b <= 0.0031308 else 1.055 * b**(1/2.4) - 0.055
    was_clamped = (
        r_gamma * 255 < 0 or r_gamma * 255 > 255 or
        g_gamma * 255 < 0 or g_gamma * 255 > 255 or
        b_gamma * 255 < 0 or b_gamma * 255 > 255
    )
    r_final = clamp(r_gamma * 255, 0, 255)
    g_final = clamp(g_gamma * 255, 0, 255)
    b_final = clamp(b_gamma * 255, 0, 255)
    return round(r_final), round(g_final), round(b_final), was_clamped

class ColorConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Конвертер цветов: CMYK ↔ LAB ↔ HSV")
        self.root.geometry("1200x600")
        self.root.resizable(False, False)
        self.root.config(bg="#f5f5f5")
        self.c_var = tk.DoubleVar(value=0.0)
        self.m_var = tk.DoubleVar(value=0.0)
        self.y_var = tk.DoubleVar(value=0.0)
        self.k_var = tk.DoubleVar(value=0.0)
        self.l_var = tk.DoubleVar(value=50.0)
        self.a_var = tk.DoubleVar(value=0.0)
        self.b_var = tk.DoubleVar(value=0.0)
        self.h_var = tk.DoubleVar(value=0.0)
        self.s_var = tk.DoubleVar(value=0.0)
        self.v_var = tk.DoubleVar(value=100.0)
        self.c_str = tk.StringVar(value="0")
        self.m_str = tk.StringVar(value="0")
        self.y_str = tk.StringVar(value="0")
        self.k_str = tk.StringVar(value="0")
        self.l_str = tk.StringVar(value="50.00")
        self.a_str = tk.StringVar(value="0.00")
        self.b_str = tk.StringVar(value="0.00")
        self.h_str = tk.StringVar(value="0")
        self.s_str = tk.StringVar(value="0")
        self.v_str = tk.StringVar(value="100")
        self.updating = False
        self.last_changed_model = None
        self.focused_entry = None
        self.create_widgets()
        self.bind_stringvars()
        self.update_from_hsv()

    def bind_stringvars(self):
        for var in [self.c_var, self.m_var, self.y_var, self.k_var,
                    self.l_var, self.a_var, self.b_var,
                    self.h_var, self.s_var, self.v_var]:
            var.trace_add("write", lambda *args: self.update_display_vars())

    def create_widgets(self):
        self.preview = tk.Label(
            self.root,
            bg="#ffffff",
            width=80,
            height=4,
            relief="groove",
            borderwidth=2
        )
        self.preview.pack(pady=12)
        self.btn_pick = tk.Button(
            self.root,
            text="🎨 Выбрать цвет из палитры",
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            command=self.pick_color,
            padx=10,
            pady=5
        )
        self.btn_pick.pack(pady=5)
        self.warning_label = tk.Label(
            self.root,
            text="",
            fg="red",
            font=("Arial", 10, "italic"),
            bg="#f5f5f5",
            height=1,
            wraplength=800
        )
        self.warning_label.pack(pady=5)
        models_frame = tk.Frame(self.root, bg="#f5f5f5")
        models_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        frame_cmyk = self.create_model_frame(models_frame, "CMYK", [
            ("C", self.c_var, self.c_str, 0, 100),
            ("M", self.m_var, self.m_str, 0, 100),
            ("Y", self.y_var, self.y_str, 0, 100),
            ("K", self.k_var, self.k_str, 0, 100)
        ])
        frame_lab = self.create_model_frame(models_frame, "LAB", [
            ("L", self.l_var, self.l_str, 0, 100),
            ("a", self.a_var, self.a_str, -128, 127),
            ("b", self.b_var, self.b_str, -128, 127)
        ])
        frame_hsv = self.create_model_frame(models_frame, "HSV", [
            ("H", self.h_var, self.h_str, 0, 360),
            ("S", self.s_var, self.s_str, 0, 100),
            ("V", self.v_var, self.v_str, 0, 100)
        ])
        frame_cmyk.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        frame_lab.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        frame_hsv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    def create_model_frame(self, parent, title, components):
        frame = tk.LabelFrame(
            parent,
            text=title,
            font=("Arial", 12, "bold"),
            padx=10,
            pady=8,
            bg="#ffffff",
            relief="ridge",
            borderwidth=2
        )
        for name, dvar, svar, min_val, max_val in components:
            comp_frame = tk.Frame(frame, bg="#ffffff")
            comp_frame.pack(fill=tk.X, pady=3)
            label = tk.Label(
                comp_frame,
                text=f"{name}:",
                width=3,
                anchor="w",
                font=("Arial", 10),
                bg="#ffffff"
            )
            label.pack(side=tk.LEFT)
            entry = tk.Entry(
                comp_frame,
                textvariable=svar,
                width=10,
                font=("Arial", 10),
                justify="right"
            )
            entry.pack(side=tk.LEFT, padx=5)
            entry.dvar = dvar
            entry.svar = svar
            entry.model = title.lower()
            entry.bind("<FocusIn>", self.on_entry_focus_in)
            entry.bind("<FocusOut>", self.on_entry_focus_out)
            entry.bind("<Return>", lambda e: self.on_entry_focus_out(e))
            resolution = 0.1 if max_val <= 100 else 1
            if min_val < 0 and max_val > 100:
                resolution = 1
            scale = tk.Scale(
                comp_frame,
                from_=min_val,
                to=max_val,
                variable=dvar,
                orient=tk.HORIZONTAL,
                resolution=resolution,
                showvalue=False,
                length=200,
                bg="#ffffff",
                troughcolor="#e0e0e0",
                command=lambda x, m=title.lower(): self.on_slider_move(m)
            )
            scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        return frame

    def on_entry_focus_in(self, event):
        entry = event.widget
        self.focused_entry = entry
        entry.svar.set(str(entry.dvar.get()))

    def on_entry_focus_out(self, event):
        entry = event.widget
        self.focused_entry = None
        try:
            value = float(entry.svar.get())
            entry.dvar.set(value)
        except ValueError:
            entry.svar.set(str(entry.dvar.get()))
        self.sync_from_changed_var(entry.dvar)

    def on_slider_move(self, model_name):
        model_map = {'cmyk': 'cmyk', 'lab': 'lab', 'hsv': 'hsv'}
        self.last_changed_model = model_map.get(model_name, None)
        self.update_display_vars()
        if model_name == 'cmyk':
            self.update_from_cmyk()
        elif model_name == 'lab':
            self.update_from_lab()
        elif model_name == 'hsv':
            self.update_from_hsv()

    def pick_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет")[1]
        if color_code:
            r = int(color_code[1:3], 16)
            g = int(color_code[3:5], 16)
            b = int(color_code[5:7], 16)
            self.last_changed_model = None  # Все модели активны для обновления
            self.set_rgb(r, g, b, from_model=None, was_clamped=False)
            self.update_display_vars()
            self.root.update_idletasks()  # 👈 Синхронизируем ползунки визуально

    def update_display_vars(self):
        if self.updating:
            return

        models = {
            'cmyk': [(self.c_var, self.c_str), (self.m_var, self.m_str), (self.y_var, self.y_str), (self.k_var, self.k_str)],
            'lab': [(self.l_var, self.l_str), (self.a_var, self.a_str), (self.b_var, self.b_str)],
            'hsv': [(self.h_var, self.h_str), (self.s_var, self.s_str), (self.v_var, self.v_str)]
        }
        for model_name, var_list in models.items():
            for dvar, svar in var_list:
                if self.focused_entry and self.focused_entry.svar == svar:
                    continue
                value = dvar.get()
                if model_name == 'lab' and self.last_changed_model != 'lab':
                    svar.set(f"{value:.2f}")
                elif self.last_changed_model != model_name:
                    svar.set(str(int(round(value))))
                else:
                    svar.set(str(value))

    def sync_from_changed_var(self, changed_var):
        if self.updating:
            return
        if changed_var in (self.c_var, self.m_var, self.y_var, self.k_var):
            self.update_from_cmyk()
        elif changed_var in (self.l_var, self.a_var, self.b_var):
            self.update_from_lab()
        elif changed_var in (self.h_var, self.s_var, self.v_var):
            self.update_from_hsv()

    def update_from_cmyk(self):
        self.last_changed_model = 'cmyk'
        c, m, y, k = self.c_var.get(), self.m_var.get(), self.y_var.get(), self.k_var.get()
        r, g, b, was_clamped = cmyk_to_rgb(c, m, y, k)
        self.set_rgb(r, g, b, from_model='cmyk', was_clamped=was_clamped)

    def update_from_lab(self):
        self.last_changed_model = 'lab'
        L, a, b_val = self.l_var.get(), self.a_var.get(), self.b_var.get()
        r, g, b, was_clamped = lab_to_rgb(L, a, b_val)
        self.set_rgb(r, g, b, from_model='lab', was_clamped=was_clamped)

    def update_from_hsv(self):
        self.last_changed_model = 'hsv'
        h, s, v = self.h_var.get(), self.s_var.get(), self.v_var.get()
        r, g, b, was_clamped = hsv_to_rgb(h, s, v)
        self.set_rgb(r, g, b, from_model='hsv', was_clamped=was_clamped)

    def set_rgb(self, r, g, b, from_model=None, was_clamped=False):
        if self.updating:
            return

        self.updating = True
        c, m, y, k = rgb_to_cmyk(r, g, b)
        L, a, b_lab = rgb_to_lab(r, g, b)
        h, s, v = rgb_to_hsv(r, g, b)
        if self.last_changed_model != 'cmyk':
            self.c_var.set(c)
            self.m_var.set(m)
            self.y_var.set(y)
            self.k_var.set(k)
        if self.last_changed_model != 'lab':
            self.l_var.set(L)
            self.a_var.set(a)
            self.b_var.set(b_lab)
        if self.last_changed_model != 'hsv':
            self.h_var.set(h)
            self.s_var.set(s)
            self.v_var.set(v)
        hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        self.preview.config(bg=hex_color)
        if was_clamped:
            self.warning_label.config(
                text="⚠️ Цвет выходит за границы sRGB — значения RGB были обрезаны для корректного отображения"
            )
        else:
            self.warning_label.config(text="")
        self.update_display_vars()
        self.updating = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorConverterApp(root)
    root.mainloop()