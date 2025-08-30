#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt I used to generate this file (for transparency):
"Create a complete, self-contained Snake game in Python using Tkinter. 
Requirements: 
- Use a Canvas-based grid (20px cell size), window ~ 600x420.
- Arrow keys to control direction; ignore direct reversal into the next cell.
- Place food at random empty cells; snake grows by 1 segment when it eats.
- Track and display score and high score; add Pause/Resume (P) and Restart (R) keys.
- End the game when the snake hits walls or itself; show a 'Game Over' overlay with instructions.
- Keep code in a single file with clear structure (SnakeGame class). 
- Avoid external dependencies; only use the Python standard library."
"""

import random
import tkinter as tk
from dataclasses import dataclass

# --- Configuration ---
CELL = 20                   # cell size in pixels
COLS = 30                   # number of columns
ROWS = 21                   # number of rows
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
TICK_MS = 120               # milliseconds per move (lower = faster)

SNAKE_COLOR = "#27ae60"
SNAKE_HEAD_COLOR = "#1e8449"
FOOD_COLOR = "#e74c3c"
BG_COLOR = "#111827"
GRID_COLOR = "#1f2937"
TEXT_COLOR = "#f3f4f6"
OVERLAY_BG = "#000000"
OVERLAY_ALPHA = 0.40

@dataclass
class Point:
    x: int
    y: int

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def to_xy(self):
        """Return top-left and bottom-right pixel coords for this cell rect."""
        return (self.x * CELL, self.y * CELL, (self.x + 1) * CELL, (self.y + 1) * CELL)


class SnakeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Snake Game (Tkinter)")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Score label
        self.score_var = tk.StringVar(value="Score: 0    High: 0")
        self.score_lbl = tk.Label(root, textvariable=self.score_var, font=("Segoe UI", 12, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        self.score_lbl.grid(row=1, column=0, sticky="w")
        # Controls hint
        self.help_lbl = tk.Label(root, text="Arrows: Move    P: Pause/Resume    R: Restart    Q: Quit",
                                 font=("Segoe UI", 10), fg=TEXT_COLOR, bg=BG_COLOR)
        self.help_lbl.grid(row=1, column=2, sticky="e")
        root.grid_columnconfigure(1, weight=1)

        # Key bindings
        root.bind("<Up>", lambda e: self.set_dir(Point(0, -1)))
        root.bind("<Down>", lambda e: self.set_dir(Point(0, 1)))
        root.bind("<Left>", lambda e: self.set_dir(Point(-1, 0)))
        root.bind("<Right>", lambda e: self.set_dir(Point(1, 0)))
        root.bind("<Key-p>", self.toggle_pause)
        root.bind("<Key-P>", self.toggle_pause)
        root.bind("<Key-r>", self.restart)
        root.bind("<Key-R>", self.restart)
        root.bind("<Key-q>", lambda e: root.destroy())
        root.bind("<Key-Q>", lambda e: root.destroy())

        # Game state
        self.after_id = None
        self.high_score = 0
        self.reset_state()
        self.draw_grid()
        self.draw_everything()
        self.loop()

    # --- Game lifecycle ---

    def reset_state(self):
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [Point(cx - 1, cy), Point(cx, cy), Point(cx + 1, cy)]
        self.direction = Point(1, 0)  # moving right
        self.pending_dir = self.direction
        self.score = 0
        self.paused = False
        self.game_over = False
        self.food = self.random_free_cell()
        self.overlay_items = []

    def restart(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.canvas.delete("all")
        self.reset_state()
        self.draw_grid()
        self.draw_everything()
        self.loop()

    def loop(self):
        if not self.paused and not self.game_over:
            self.step()
        self.after_id = self.root.after(TICK_MS, self.loop)

    # --- Input ---

    def set_dir(self, new_dir: Point):
        # Prevent reversing into the next cell
        if (new_dir.x == -self.direction.x and new_dir.y == -self.direction.y):
            return
        self.pending_dir = new_dir

    def toggle_pause(self, event=None):
        if self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.show_overlay("Paused\n\nPress P to Resume")
        else:
            self.clear_overlay()

    # --- Mechanics ---

    def step(self):
        self.direction = self.pending_dir
        new_head = self.snake[-1] + self.direction

        # Collisions with walls
        if not (0 <= new_head.x < COLS and 0 <= new_head.y < ROWS):
            self.end_game()
            return

        # Collisions with self
        if any(seg.x == new_head.x and seg.y == new_head.y for seg in self.snake):
            self.end_game()
            return

        # Move snake
        self.snake.append(new_head)

        # Check food
        if new_head.x == self.food.x and new_head.y == self.food.y:
            self.score += 1
            self.food = self.random_free_cell()
        else:
            # pop tail
            self.snake.pop(0)

        # Redraw
        self.draw_everything()

    def end_game(self):
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
        self.update_score_label()
        self.show_overlay("Game Over\n\nR: Restart   Q: Quit")

    def random_free_cell(self) -> Point:
        occupied = {(p.x, p.y) for p in self.snake}
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if (x, y) not in occupied:
                return Point(x, y)

    # --- Rendering ---

    def draw_grid(self):
        # Subtle grid lines
        for x in range(0, WIDTH, CELL):
            self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
        for y in range(0, HEIGHT, CELL):
            self.canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)

    def draw_everything(self):
        self.canvas.delete("snake")
        self.canvas.delete("food")
        # Draw snake
        for i, seg in enumerate(self.snake):
            x1, y1, x2, y2 = seg.to_xy()
            color = SNAKE_HEAD_COLOR if i == len(self.snake) - 1 else SNAKE_COLOR
            self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline="", tags="snake")
        # Draw food
        fx1, fy1, fx2, fy2 = self.food.to_xy()
        pad = 3
        self.canvas.create_oval(fx1 + pad, fy1 + pad, fx2 - pad, fy2 - pad, fill=FOOD_COLOR, outline="", tags="food")

        self.update_score_label()

    def update_score_label(self):
        self.score_var.set(f"Score: {self.score}    High: {self.high_score}")

    # --- Overlay helpers ---

    def show_overlay(self, message: str):
        self.clear_overlay()
        # Semi-transparent overlay: Tkinter doesn't support alpha on Canvas fill,
        # so we simulate with multiple rectangles to give a dimming effect.
        steps = 10
        for i in range(steps):
            alpha = OVERLAY_ALPHA / steps * (i + 1)
            # approximate alpha by stacking faint rectangles
            item = self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=OVERLAY_BG, outline="", stipple="gray50")
            self.overlay_items.append(item)
        text = self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text=message,
                                       fill=TEXT_COLOR, font=("Segoe UI", 20, "bold"), justify="center")
        self.overlay_items.append(text)

    def clear_overlay(self):
        for item in self.overlay_items:
            self.canvas.delete(item)
        self.overlay_items.clear()

def main():
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
