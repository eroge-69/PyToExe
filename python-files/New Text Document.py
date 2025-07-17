import tkinter as tk
import random

def draw_static(canvas, width, height):
    canvas.delete("all")
    for _ in range(800):  # change density as needed
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = random.choice(["red", "green", "blue", "white", "black"])
        canvas.create_rectangle(x, y, x+2, y+2, fill=color, outline=color)
    canvas.after(50, draw_static, canvas, width, height)

def on_resize(event):
    draw_static(canvas, event.width, event.height)

root = tk.Tk()
root.title("JScreenFix - Pixel Healer")
root.geometry("800x600")
root.minsize(300, 200)

canvas = tk.Canvas(root, bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

canvas.bind("<Configure>", on_resize)
draw_static(canvas, 800, 600)

root.mainloop()