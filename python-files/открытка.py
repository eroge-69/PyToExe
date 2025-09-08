# card_for_dad.py
# Запуск: python card_for_dad.py
# Требования: Python 3 (tkinter входит в стандартную библиотеку)

import tkinter as tk
import random
import math
from datetime import datetime

WIDTH, HEIGHT = 700, 450
CONFETTI_COUNT = 40
UPDATE_MS = 30

WISHES = [
    "Здоровья крепкого, как дуб!",
    "Пусть каждый день приносит радость.",
    "Пусть мечты сбываются легко и быстро.",
    "Оставайся таким же заботливым и мудрым.",
    "Побольше позитивных моментов в жизни!"
]

class Confetti:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = random.randrange(0, WIDTH)
        self.y = random.randrange(-HEIGHT, 0)
        self.size = random.randrange(6, 14)
        self.vy = random.uniform(1, 4)
        self.vx = random.uniform(-1.5, 1.5)
        self.color = random.choice([
            "#FF4B4B", "#FFB84B", "#FFF44B", "#4BFFA5", "#4BD6FF", "#B44BFF"
        ])
        self.shape = canvas.create_oval(self.x, self.y,
                                        self.x + self.size, self.y + self.size,
                                        fill=self.color, outline="")

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y - self.size > HEIGHT:
            # заново сбрасываем сверху
            self.x = random.randrange(0, WIDTH)
            self.y = random.randrange(-100, -10)
            self.vy = random.uniform(1, 4)
            self.vx = random.uniform(-1.5, 1.5)
            self.size = random.randrange(6, 14)
            self.color = random.choice([
                "#FF4B4B", "#FFB84B", "#FFF44B", "#4BFFA5", "#4BD6FF", "#B44BFF"
            ])
            self.canvas.coords(self.shape, self.x, self.y,
                               self.x + self.size, self.y + self.size)
            self.canvas.itemconfig(self.shape, fill=self.color)
        else:
            self.canvas.move(self.shape, self.vx, self.vy)

class HeartAnimation:
    def __init__(self, canvas, cx, cy):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.oval_ids = []
        self.t = 0
        self.running = False

    def start(self):
        if not self.running:
            self.t = 0
            self.running = True
            self.step()

    def step(self):
        if not self.running:
            return
        # удаляем предыдущие
        for oid in self.oval_ids:
            try:
                self.canvas.delete(oid)
            except:
                pass
        self.oval_ids = []
        # рисуем сердце параметрически, масштаб зависит от t
        scale = 0.6 + 0.02 * self.t  # растёт
        points = []
        for angle in [i * math.pi / 180 for i in range(0, 360, 6)]:
            x = 16 * math.sin(angle) ** 3
            y = 13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle)
            px = self.cx + x * 7 * scale
            py = self.cy - y * 7 * scale
            points.append((px, py))
        # создаём много маленьких овалов по точкам, чтобы было мягко
        for (px, py) in points[::2]:
            r = random.uniform(4, 9) * scale
            oid = self.canvas.create_oval(px - r, py - r, px + r, py + r, fill="#FF4B8B", outline="")
            self.oval_ids.append(oid)

        self.t += 1
        if self.t < 30:
            self.canvas.after(40, self.step)
        else:
            # плавно исчезаем
            self.fade_out(15)

    def fade_out(self, steps_left):
        if steps_left <= 0:
            for oid in self.oval_ids:
                try:
                    self.canvas.delete(oid)
                except:
                    pass
            self.oval_ids = []
            self.running = False
            return
        # уменьшаем альфо-подобный эффект через уменьшение размеров
        for oid in list(self.oval_ids):
                try:
                    coords = self.canvas.coords(oid)
                    if coords:
                        cx = (coords[0] + coords[2]) / 2
                        cy = (coords[1] + coords[3]) / 2
                        r = (coords[2] - coords[0]) * 0.9
                        self.canvas.coords(oid, cx - r/2, cy - r/2, cx + r/2, cy + r/2)
                except:
                    pass
        self.canvas.after(80, lambda: self.fade_out(steps_left - 1))

def main():
    root = tk.Tk()
    root.title("Открытка папе 🎉")
    root.resizable(False, False)

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#FDF7F0")
    canvas.pack()

    # Большое поздравление
    title = tk.Label(root, text="С ДНЁМ РОЖДЕНИЯ, ПАПА!", font=("Helvetica", 20, "bold"))
    title.place(x=WIDTH//2, y=20, anchor="n")

    # Подзаголовок с именем (можешь заменить "Папа" на конкретное имя прямо в строке ниже)
    name_label = tk.Label(root, text="Для самого лучшего папы на свете", font=("Helvetica", 12))
    name_label.place(x=WIDTH//2, y=55, anchor="n")

    # Большой текст-пожелание (можно изменить)
    wish_text = ("Пусть каждый новый день будет полон счастья, семейного уюта "
                 "и маленьких радостей. Спасибо за заботу и мудрость.")
    msg = tk.Message(root, text=wish_text, width=560, font=("Helvetica", 11))
    msg.place(x=WIDTH//2, y=90, anchor="n")

    # кнопки
    frame = tk.Frame(root)
    frame.place(x=WIDTH//2, y=HEIGHT - 70, anchor="s")

    heart_anim = HeartAnimation(canvas, cx=WIDTH//2, cy=HEIGHT//2 + 20)

    def on_more_wish():
        w = random.choice(WISHES)
        now = datetime.now().strftime("%d.%m.%Y")
        tk.messagebox.showinfo("Ещё одно пожелание", f"{w}\n\nС любовью,твой сын.\n\n{now}")

    import tkinter.messagebox

    more_btn = tk.Button(frame, text="Ещё пожелание", command=on_more_wish, width=18)
    more_btn.grid(row=0, column=0, padx=8, pady=6)

    def on_open_gift():
        heart_anim.start()

    gift_btn = tk.Button(frame, text="Открыть подарок", command=on_open_gift, width=18)
    gift_btn.grid(row=0, column=1, padx=8, pady=6)

    # подпись (можно вручную отредактировать)
    signature = tk.Label(root, text="С любовью, Вадим ♥", font=("Helvetica", 12, "italic"))
    signature.place(x=WIDTH - 20, y=HEIGHT - 20, anchor="se")

    # Конфетти
    confetti = [Confetti(canvas) for _ in range(CONFETTI_COUNT)]

    def update_all():
        for c in confetti:
            c.update()
        # лёгкое мерцание заднего плана (необязательно)
        root.after(UPDATE_MS, update_all)

    update_all()

    # Для удобства — закрытие по Escape
    def on_key(e):
        if e.keysym == "Escape":
            root.destroy()
    root.bind("<Key>", on_key)

    root.mainloop()

if __name__ == "__main__":
    main()
