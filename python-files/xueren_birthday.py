import random
import math
from tkinter import *
from math import sin, cos, pi, log

# 基础设置
CANVAS_WIDTH = 720
CANVAS_HEIGHT = 580
CENTER_X = CANVAS_WIDTH / 2
CENTER_Y = CANVAS_HEIGHT / 2
BG_COLOR = "black"
FONT = ("ZCOOL KuaiLe", 18)  # 使用你安装的字体
TEXT_COLOR = "#FFD3E0"
HEART_COLOR = "#ff69b4"

# 文字内容
intro = "送给我最喜欢的雪人 ☃️"
heart_messages = [
    "今天是你的生日 🎂",
    "谢谢你一直以来的陪伴 ✨",
    "愿你每天都开开心心，永远幸福 🐰🎈"
]
final_message = "生日快乐！Happy Birthday! 🎉🎉🎉"

def heart_function(t, ratio=16):
    x = 16 * sin(t) ** 3
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    x *= ratio
    y *= ratio
    x += CENTER_X
    y += CENTER_Y
    return int(x), int(y)

class Heart:
    def __init__(self, frame_total=20):
        self.frame_total = frame_total
        self._points = set()
        self._edges = set()
        self.frames = {}
        self.build(1600)
        for frame in range(frame_total):
            self.calc(frame)

    def build(self, count):
        for _ in range(count):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))
        for x, y in list(self._points):
            for _ in range(2):
                x0, y0 = self._scatter(x, y, 0.05)
                self._edges.add((x0, y0))

    def _scatter(self, x, y, beta):
        ratio_x = -beta * log(random.random())
        ratio_y = -beta * log(random.random())
        dx = ratio_x * (x - CENTER_X)
        dy = ratio_y * (y - CENTER_Y)
        return x - dx, y - dy

    def _move(self, x, y, ratio):
        force = 1 / (((x - CENTER_X) ** 2 + (y - CENTER_Y) ** 2) ** 0.52)
        dx = ratio * force * (x - CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def _curve(self, p):
        return 2 * (2 * sin(4 * p)) / (2 * pi)

    def calc(self, frame):
        ratio = 10 * self._curve(frame / 10 * pi)
        points = []
        for x, y in self._points:
            x, y = self._move(x, y, ratio)
            size = random.randint(1, 2)
            points.append((x, y, size))
        for x, y in self._edges:
            x, y = self._move(x, y, ratio)
            size = random.randint(1, 2)
            points.append((x, y, size))
        self.frames[frame] = points

    def render(self, canvas, frame):
        canvas.delete("particles")
        for x, y, size in self.frames[frame % self.frame_total]:
            canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR, tags="particles")

class Snow:
    def __init__(self, canvas, count=120):
        self.canvas = canvas
        self.flakes = []
        for _ in range(count):
            x = random.randint(0, CANVAS_WIDTH)
            y = random.randint(-CANVAS_HEIGHT, CANVAS_HEIGHT)
            r = random.randint(2, 4)
            speed = random.uniform(1, 3)
            flake = canvas.create_oval(x, y, x + r, y + r, fill="white", outline="", tags="snow")
            self.flakes.append((flake, r, speed))

    def update(self):
        for flake, r, speed in self.flakes:
            self.canvas.move(flake, 0, speed)
            coords = self.canvas.coords(flake)
            if coords[1] > CANVAS_HEIGHT:
                x = random.randint(0, CANVAS_WIDTH)
                self.canvas.coords(flake, x, 0, x + r, r)

def firework_burst(x, y, color=None, count=30):
    for _ in range(count):
        angle = random.uniform(0, 2 * pi)
        speed = random.uniform(2, 6)
        dx = cos(angle) * speed
        dy = sin(angle) * speed
        r = random.randint(2, 4)
        animate_burst(x, y, dx, dy, r, color or random.choice(["#ffcc00", "#66ffff", "#cc66ff"]))

def animate_burst(x, y, dx, dy, r, color, step=0):
    if step > 10:
        return
    x += dx
    y += dy
    oval = canvas.create_oval(x, y, x + r, y + r, fill=color, outline="", tags="firework")
    canvas.after(50, lambda: (canvas.delete(oval), animate_burst(x, y, dx, dy, r, color, step + 1)))

def type_text(text, color=TEXT_COLOR, hold=2000, callback=None):
    def show(i=0):
        if i <= len(text):
            canvas.delete("text")
            canvas.create_text(CENTER_X, CENTER_Y, text=text[:i], fill=color, font=FONT, tags="text")
            canvas.after(80, lambda: show(i + 1))
        elif callback:
            canvas.after(hold, callback)
    show()

def draw_heart(frame=0):
    heart.render(canvas, frame)
    if heart_anim[0]:
        root.after(70, lambda: draw_heart(frame + 1))

def update_snow():
    if snow_anim[0]:
        snow.update()
        root.after(40, update_snow)

def start_intro():
    global snow
    snow = Snow(canvas)
    snow_anim[0] = True
    update_snow()
    type_text(intro, callback=next_stage)

def next_stage():
    snow_anim[0] = False
    canvas.delete("snow")
    canvas.delete("text")
    canvas.after(1000, show_heart_sequence)

def show_heart_sequence(index=0):
    if index == 0:
        heart_anim[0] = True
        draw_heart()
    if index < len(heart_messages):
        type_text(heart_messages[index], callback=lambda: show_heart_sequence(index + 1))
    else:
        heart_anim[0] = False
        canvas.delete("particles")
        canvas.delete("text")
        canvas.after(1000, show_final)

def show_final():
    canvas.delete("particles")
    canvas.delete("text")
    firework_burst(CENTER_X, CENTER_Y)
    type_text(final_message)
    run_firework_loop(1)

def run_firework_loop(count):
    if count < 12:
        firework_burst(
            random.randint(100, CANVAS_WIDTH - 100),
            random.randint(100, CANVAS_HEIGHT - 100)
        )
        canvas.after(500, lambda: run_firework_loop(count + 1))
    else:
        canvas.delete("firework")

# 初始化窗口
root = Tk()
root.title("送给雪人的生日动画")
root.configure(bg="black")
canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=BG_COLOR, highlightthickness=0)
canvas.pack()

heart = Heart()
snow_anim = [False]
heart_anim = [False]

# 启动
root.after(1000, start_intro)
root.mainloop()
