import tkinter as tk
import math
import threading
import keyboard

esp_enabled = True

def toggle_esp():
    global esp_enabled
    esp_enabled = not esp_enabled

keyboard.add_hotkey('f1', toggle_esp)

# Dummy enemy locations (simulated)
enemies = [
    {"x": 700, "y": 400, "distance": 280},
    {"x": 1200, "y": 300, "distance": 500},
    {"x": 950, "y": 600, "distance": 150}
]

def draw_esp():
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.overrideredirect(1)
    root.geometry("1920x1080+0+0")
    root.wm_attributes("-transparentcolor", "black")
    root.configure(bg='black')

    canvas = tk.Canvas(root, width=1920, height=1080, bg='black', highlightthickness=0)
    canvas.pack()

    def update():
        canvas.delete("all")
        if esp_enabled:
            for enemy in enemies:
                if enemy["distance"] <= 300:
                    x, y = enemy["x"], enemy["y"]

                    canvas.create_line(960, 1080, x, y, fill="red", width=2)
                    canvas.create_line(x, y, x, y+40, fill="green", width=2)
                    canvas.create_line(x-15, y+20, x+15, y+20, fill="green", width=2)
                    canvas.create_line(x, y+40, x-10, y+70, fill="green", width=2)
                    canvas.create_line(x, y+40, x+10, y+70, fill="green", width=2)

        root.after(50, update)

    update()
    root.mainloop()

threading.Thread(target=draw_esp).start()

while True:
    pass
