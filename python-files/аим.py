import random
import tkinter as tk

def hit(event):
    global score
    if not running:
        return
    items = canvas.find_overlapping(event.x, event.y, event.y)
    if target in items:
        score += 1
        lbl_score.config(text = f"Очки: {score}")
        place_target()


def place_target():
    x = random.randint(target_size, w - target_size)
    y = random.randint(target_size, h - target_size)
    convas.coords(target, x - target_size // 2, y - target_size // 2,)
                x + target_size // 2, y + target_size // 2)



def countdown():
    global time_left, running
    if not running:
        return

    if time_left <= 0:
        running = False
        lbl_time.config(text="Время: 0 - Игра окончена")
        return
    time_left -= 1
    lbl_time.config(text=f"Время: {time_left}")
    root.after(1000, countdown)


def start_game():
    global score, time_left, running
    score = 0
    time_left = time_limit
    running = True
    lbl_score.config(text=f"Очки:{score}")
    lbl_time.config(text=f"Время:{time_left}")
    place_target()
    countdown()


   
w,h = 600, 400
target_size = 40
time_limit = 30

root = tk.Tk()
root.title("Аим тренажёр")

score = 0
time_left = time_limit
running = False

lbl_score = tk.Label(root, text=f"Очки: {score}", font=("Arial", 14))
lbl_time = tk.Label(root, text=f"Время: {time_left}", font=("Arial", 14))

lbl_score.pack(side = "left", padx = 10)
lbl_time.pack(side = "right", padx = 10)

canvas = tk.Canvas(root, width= w, height= h, bg="white")
canvas.pack()

target = canvas.creat_oval(0,0 target_size, target_size, fill="red", tags = "target")

btn_start = tk.Button(root, text="Старт", command=start_game)
btn_start.pack(pady = 6)

canvas.tag_bind("target", "<Button-1>", hit)
