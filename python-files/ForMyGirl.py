import tkinter as tk
import time
import threading
from math import sin, cos, pi
from random import randint

def create_heart(canvas, x, y, size, color):
    points = []
    for t in range(0, 360, 1):
        angle = pi * t / 180
        x_point = size * 16 * sin(angle)**3
        y_point = -size * (13 * cos(angle) - 5 * cos(2*angle) -
                           2 * cos(3*angle) - cos(4*angle))
        points.append((x + x_point, y + y_point))
    return canvas.create_polygon(points, fill=color, outline='black')

def float_hearts(canvas):
    while True:
        x = randint(50, 350)
        y = 400
        size = 0.5 + randint(0, 5) / 10
        color = f'#{randint(100,255):02x}{randint(50,200):02x}{randint(100,255):02x}'
        heart = create_heart(canvas, x, y, size, color)

        for _ in range(40):
            canvas.move(heart, 0, -5)
            time.sleep(0.05)

        canvas.delete(heart)

def start_animation(canvas):
    threading.Thread(target=float_hearts, args=(canvas,), daemon=True).start()


root = tk.Tk()
root.title("For My Love ❤️")
root.geometry("400x500")
root.configure(bg='pink')

canvas = tk.Canvas(root, width=400, height=400, bg='pink', highlightthickness=0)
canvas.pack()

message = tk.Label(root, text="I ❤️ You, Beautiful", font=("Helvetica", 20, "bold"), bg='pink', fg='red')
message.pack(pady=10)

start_animation(canvas)

root.mainloop()
