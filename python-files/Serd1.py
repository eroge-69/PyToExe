from tkinter import *
import math
import time
import threading

N = 40
window_size = 50
center_x, center_y = 250, 200
scale = 10

windows = []


def heart_points(n, scale):
    points = []
    for i in range(n):
        t = math.pi - (i / n) * 2 * math.pi
        x = scale * 16 * math.sin(t) ** 3
        y = -scale * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((center_x + int(x), center_y + int(y)))
    return points


def spawn_heart():
    positions = heart_points(N, scale)
    for (x, y) in positions:
        win = Toplevel()
        win.geometry(f"{window_size}x{window_size}+{x - window_size // 2}+{y - window_size // 2}")
        win.configure(bg="#d00000")

        label = Label(win, text=" ", font=("Arial", 18), bg="#d00000", fg="white")
        label.place(relx=0.5, rely=0.5, anchor="center")

        windows.append(win)
        win.update()

        threading.Timer(7, lambda w=win: w.destroy()).start()

        time.sleep(0.15)


def start():
    threading.Thread(target=spawn_heart, daemon=True).start()


root = Tk()
root.withdraw()
start()
root.mainloop()