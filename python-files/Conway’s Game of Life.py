#!/usr/bin/env python3
"""
Conway's Game of Life - Tkinter single-file implementation.

Controls:
- Left-click / drag: toggle cells
- Space: start / stop simulation
- n: step forward one generation (when paused)
- r: randomize
- c: clear
- w: toggle wrap-around neighbors
- + / -: increase / decrease speed
- Esc or window close: exit
"""

import tkinter as tk
import random

# ----- Config (change these if you want) -----
CELL_SIZE = 12        # pixels per cell
GRID_COLS = 80        # number of columns
GRID_ROWS = 50        # number of rows
BG_COLOR = "#111111"
GRID_COLOR = "#222222"
ALIVE_COLOR = "#21c7a8"
DEAD_COLOR = BG_COLOR
START_RUNNING = False
INITIAL_SPEED_MS = 120  # delay between generations in ms
WRAP_BY_DEFAULT = True
# ---------------------------------------------

class LifeApp:
    def __init__(self, master):
        self.master = master
        master.title("Conway's Game of Life")
        self.cell_size = CELL_SIZE
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size

        self.running = START_RUNNING
        self.speed_ms = INITIAL_SPEED_MS
        self.wrap = WRAP_BY_DEFAULT

        self.grid = [[0]*self.cols for _ in range(self.rows)]
        self.next_grid = [[0]*self.cols for _ in range(self.rows)]

        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        # Draw grid lines once (light)
        self._draw_grid_lines()

        # Rectangle storage to update colors fast
        self.rects = [[None]*self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c*self.cell_size
                y1 = r*self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="", fill=DEAD_COLOR)
                self.rects[r][c] = rect

        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        master.bind("<space>", self.toggle_running)
        master.bind("n", self.step_once)
        master.bind("r", self.randomize_grid)
        master.bind("c", self.clear_grid)
        master.bind("w", self.toggle_wrap)
        master.bind("+", self.speed_up)
        master.bind("-", self.slow_down)
        master.protocol("WM_DELETE_WINDOW", master.destroy)

        # Status label
        self.status = tk.Label(master, text=self._status_text(), anchor="w")
        self.status.pack(fill="x")

        # Start the update loop
        self._job = None
        if self.running:
            self._schedule()

    def _draw_grid_lines(self):
        # faint grid lines to help visualize
        for c in range(0, self.width, self.cell_size):
            self.canvas.create_line(c, 0, c, self.height, fill=GRID_COLOR)
        for r in range(0, self.height, self.cell_size):
            self.canvas.create_line(0, r, self.width, r, fill=GRID_COLOR)

    def _status_text(self):
        return f"{'Running' if self.running else 'Paused'} | Speed: {self.speed_ms} ms | Wrap: {'On' if self.wrap else 'Off'} | Cells: {self.rows}x{self.cols}"

    def on_click(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = 0 if self.grid[r][c] else 1
            self._update_cell_visual(r, c)
            self.status.config(text=self._status_text())

    def on_drag(self, event):
        self.on_click(event)

    def toggle_running(self, event=None):
        self.running = not self.running
        self.status.config(text=self._status_text())
        if self.running:
            self._schedule()
        else:
            if self._job:
                self.master.after_cancel(self._job)
                self._job = None

    def step_once(self, event=None):
        if self.running:
            return
        self._compute_next()
        self._swap_and_draw()

    def randomize_grid(self, event=None):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() < 0.2 else 0
        self._draw_all()
        self.status.config(text=self._status_text())

    def clear_grid(self, event=None):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self._draw_all()
        self.status.config(text=self._status_text())

    def toggle_wrap(self, event=None):
        self.wrap = not self.wrap
        self.status.config(text=self._status_text())

    def speed_up(self, event=None):
        # decrease delay to speed up
        self.speed_ms = max(10, int(self.speed_ms * 0.75))
        self.status.config(text=self._status_text())

    def slow_down(self, event=None):
        # increase delay to slow down
        self.speed_ms = int(self.speed_ms * 1.33)
        self.status.config(text=self._status_text())

    def _schedule(self):
        self._job = self.master.after(self.speed_ms, self._tick)

    def _tick(self):
        self._compute_next()
        self._swap_and_draw()
        if self.running:
            self._schedule()

    def _compute_next(self):
        for r in range(self.rows):
            for c in range(self.cols):
                alive = self.grid[r][c]
                n = self._count_neighbors(r, c)
                if alive:
                    # Any live cell with 2 or 3 live neighbours survives.
                    self.next_grid[r][c] = 1 if (n == 2 or n == 3) else 0
                else:
                    # Any dead cell with exactly 3 live neighbours becomes a live cell.
                    self.next_grid[r][c] = 1 if (n == 3) else 0

    def _count_neighbors(self, r, c):
        total = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr = r + dr
                cc = c + dc
                if self.wrap:
                    rr %= self.rows
                    cc %= self.cols
                    total += self.grid[rr][cc]
                else:
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        total += self.grid[rr][cc]
        return total

    def _swap_and_draw(self):
        # swap references and draw changed cells
        self.grid, self.next_grid = self.next_grid, self.grid
        self._draw_all()

    def _draw_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self._update_cell_visual(r, c)

    def _update_cell_visual(self, r, c):
        rect = self.rects[r][c]
        if self.grid[r][c]:
            self.canvas.itemconfig(rect, fill=ALIVE_COLOR)
        else:
            self.canvas.itemconfig(rect, fill=DEAD_COLOR)

if __name__ == "__main__":
    root = tk.Tk()
    app = LifeApp(root)
    # center window on screen nicely
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - app.width) // 2
    y = (screen_h - app.height) // 2
    root.geometry(f"{app.width}x{app.height+24}+{x}+{y}")
    root.mainloop()
