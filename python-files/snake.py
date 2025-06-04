import tkinter as tk
import random
import os
import json
import sys
import time

try:
    import pygame
    pygame.init()
    pygame.mixer.init()
    sound_enabled = True
except:
    sound_enabled = False

CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
DEFAULT_SPEED = 150

SCORE_FILE = "snake_highscore.json"

DARK_THEME = {"bg": "#121212", "snake": "#00FF00", "food": "#FF0000", "text": "#FFFFFF"}
LIGHT_THEME = {"bg": "#FFFFFF", "snake": "#008000", "food": "#FF0000", "text": "#000000"}

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake")
        self.theme = DARK_THEME
        self.speed = DEFAULT_SPEED
        self.paused = False
        self.load_high_score()

        self.loading_screen()

        self.canvas = tk.Canvas(root, width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE)
        self.canvas.pack()
        self.label = tk.Label(root, font=("Arial", 14))
        self.label.pack()

        self.control_frame = tk.Frame(root)
        self.control_frame.pack()

        self.pause_btn = tk.Button(self.control_frame, text="⏸ Pause", command=self.show_pause_menu)
        self.pause_btn.grid(row=0, column=0, padx=5)

        self.dark_mode_btn = tk.Button(self.control_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        self.dark_mode_btn.grid(row=0, column=1, padx=5)

        self.apply_theme()
        self.reset_game()
        self.root.bind("<Key>", self.key_press)
        self.update()

    def loading_screen(self):
        load = tk.Toplevel(self.root)
        load.geometry("300x100")
        load.title("Loading...")
        tk.Label(load, text="Loading Snake Game...").pack(pady=20)
        self.root.update()
        time.sleep(random.uniform(2, 5))
        load.destroy()

    def toggle_theme(self):
        self.theme = LIGHT_THEME if self.theme == DARK_THEME else DARK_THEME
        self.dark_mode_btn.config(text="🌙 Dark Mode" if self.theme == DARK_THEME else "☀️ Light Mode")
        self.apply_theme()
        self.draw()

    def apply_theme(self):
        self.root.config(bg=self.theme["bg"])
        self.label.config(bg=self.theme["bg"], fg=self.theme["text"])
        self.control_frame.config(bg=self.theme["bg"])
        self.canvas.config(bg=self.theme["bg"])
        for widget in self.control_frame.winfo_children():
            widget.config(bg=self.theme["bg"], fg=self.theme["text"])

    def load_high_score(self):
        try:
            with open(SCORE_FILE, "r") as f:
                self.high_score = json.load(f).get("high_score", 0)
        except:
            self.high_score = 0

    def save_high_score(self):
        with open(SCORE_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def reset_game(self):
        self.snake = [(5, 5), (4, 5)]
        self.direction = (1, 0)
        self.spawn_food()
        self.score = 0
        self.paused = False
        self.gameover = False
        self.speed = DEFAULT_SPEED
        self.update_label()
        self.draw()

    def spawn_food(self):
        while True:
            self.food = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if self.food not in self.snake:
                break

    def key_press(self, e):
        k = e.keysym
        if k == "r" or k == "R":
            self.reset_game()
            return
        if self.paused: return
        if k == "Left" and self.direction != (1, 0): self.direction = (-1, 0)
        elif k == "Right" and self.direction != (-1, 0): self.direction = (1, 0)
        elif k == "Up" and self.direction != (0, 1): self.direction = (0, -1)
        elif k == "Down" and self.direction != (0, -1): self.direction = (0, 1)

    def update_label(self):
        self.label.config(text=f"Score: {self.score}  |  High Score: {self.high_score}")

    def show_pause_menu(self):
        self.paused = True
        pause_window = tk.Toplevel(self.root)
        pause_window.title("Paused")
        pause_window.geometry("250x180")
        pause_window.config(bg=self.theme["bg"])

        tk.Label(pause_window, text="Difficulty", bg=self.theme["bg"], fg=self.theme["text"]).pack()
        slider = tk.Scale(pause_window, from_=50, to=300, orient="horizontal", bg=self.theme["bg"], fg=self.theme["text"])
        slider.set(self.speed)
        slider.pack()

        def resume():
            self.speed = slider.get()
            self.paused = False
            self.draw()
            pause_window.destroy()
            if hasattr(self, "gameover") and self.gameover:
                self.reset_game()

        tk.Button(pause_window, text="Resume", command=resume, bg=self.theme["bg"], fg=self.theme["text"]).pack(pady=10)

    def update(self):
        if not self.paused:
            head_x, head_y = self.snake[0]
            dx, dy = self.direction
            new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)  # wrap around screen

            if new_head in self.snake:
                self.game_over()
                return

            self.snake.insert(0, new_head)

            if new_head == self.food:
                self.score += 1
                for _ in range(3):  # +4 length in total (1 from insert, +3 extra)
                    self.snake.append(self.snake[-1])
                self.spawn_food()
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            else:
                self.snake.pop()

            self.update_label()
            self.draw()

        self.root.after(self.speed, self.update)

    def game_over(self):
        self.paused = True
        self.gameover = True
        self.canvas.create_text(GRID_WIDTH*CELL_SIZE//2, GRID_HEIGHT*CELL_SIZE//2, text="GAME OVER", fill="red", font=("Arial", 32, "bold"))

    def draw(self):
        self.canvas.delete("all")
        for x, y in self.snake:
            self.canvas.create_rectangle(x*CELL_SIZE, y*CELL_SIZE, (x+1)*CELL_SIZE, (y+1)*CELL_SIZE, fill=self.theme["snake"], outline="")
        fx, fy = self.food
        self.canvas.create_rectangle(fx*CELL_SIZE, fy*CELL_SIZE, (fx+1)*CELL_SIZE, (fy+1)*CELL_SIZE, fill=self.theme["food"], outline="")


if __name__ == '__main__':
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
