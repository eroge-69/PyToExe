#!/usr/bin/env python3
"""
CPU Visualizer — blinking pixels & bars
Author: ChatGPT (Sebastian's helper)

How to run:
    python3 cpu_visualizer.py

Optional (recommended for real CPU stats on all OSes):
    pip install psutil

Controls:
    - Press "F" to toggle fullscreen
    - Press "Q" or Esc to quit
    - Press "B" to toggle bars on/off
    - Press "P" to toggle pixel grid on/off
    - Press "G" to increase pixel grid size
    - Press "H" to decrease pixel grid size
"""
import sys
import time
import math
import random
import threading
import os
from dataclasses import dataclass

# Try to use psutil if available
try:
    import psutil
except Exception:
    psutil = None

try:
    import tkinter as tk
except Exception as e:
    print("Dieses Programm benötigt Tkinter. Bitte installieren Sie tkinter für Ihre Plattform.")
    print("Fehler:", e)
    sys.exit(1)


@dataclass
class Config:
    width: int = 1000
    height: int = 600
    fps: int = 30               # target frames per second
    grid_cols: int = 64         # initial pixel grid width
    grid_rows: int = 32         # initial pixel grid height
    grid_margin: int = 12
    info_height: int = 38
    bar_area_width: int = 260   # width reserved for bars at the left
    bg: str = "#0b0f14"
    fg: str = "#c8d2e0"
    bar_bg: str = "#1a2330"
    bar_fg: str = "#6aa0ff"
    pixel_off: str = "#10161e"
    pixel_on: str = "#7bd8ff"
    pixel_mid: str = "#36b0ff"


class CPUMeter:
    def __init__(self):
        self.lock = threading.Lock()
        self.num_cores = os.cpu_count() or 1
        self.percents = [0.0] * self.num_cores
        self.overall = 0.0
        self.procs = None
        self.cswitches = None
        self.running = True
        self.interval = 0.2  # seconds
        # Prime psutil if available to get proper first readings
        if psutil:
            try:
                psutil.cpu_percent(interval=None, percpu=True)
            except Exception:
                pass
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def _poll_loop(self):
        while self.running:
            try:
                if psutil:
                    per = psutil.cpu_percent(interval=None, percpu=True)
                    overall = float(sum(per))/len(per) if per else psutil.cpu_percent(interval=None) or 0.0
                    procs = len(psutil.pids())
                    cs = psutil.cpu_stats().ctx_switches if hasattr(psutil, "cpu_stats") else None
                else:
                    # Fallback: try system load (Unix), scaled to 0..100 approx
                    try:
                        load1, _, _ = os.getloadavg()
                        # Normalize by cores, clamp to 0..100
                        overall = max(0.0, min(100.0, (load1 / (self.num_cores or 1)) * 100.0))
                    except Exception:
                        overall = random.uniform(10, 70)
                    per = [overall] * self.num_cores
                    procs = None
                    cs = None

                with self.lock:
                    self.percents = per
                    self.overall = overall
                    self.procs = procs
                    self.cswitches = cs
            except Exception:
                # Robustness: never crash the polling loop
                pass
            time.sleep(self.interval)

    def snapshot(self):
        with self.lock:
            return (self.percents[:], self.overall, self.procs, self.cswitches)

    def stop(self):
        self.running = False


class Visualizer(tk.Tk):
    def __init__(self, cfg: Config, meter: CPUMeter):
        super().__init__()
        self.title("CPU Visualizer — Pixels & Bars")
        self.cfg = cfg
        self.meter = meter
        self.geometry(f"{cfg.width}x{cfg.height}")
        self.configure(bg=cfg.bg)
        self.canvas = tk.Canvas(self, width=cfg.width, height=cfg.height, highlightthickness=0, bg=cfg.bg)
        self.canvas.pack(fill="both", expand=True)

        # State
        self.last_time = time.time()
        self.frame_time = 1.0 / max(1, cfg.fps)
        self.show_bars = True
        self.show_pixels = True
        self.pixel_grid = []
        self.rects = []
        self.fullscreen = False
        self.seed = random.randint(0, 10**9)

        # Bindings
        self.bind("<Escape>", lambda e: self.quit_app())
        self.bind("<q>", lambda e: self.quit_app())
        self.bind("<Q>", lambda e: self.quit_app())
        self.bind("<f>", self.toggle_fullscreen)
        self.bind("<F>", self.toggle_fullscreen)
        self.bind("<b>", self.toggle_bars)
        self.bind("<B>", self.toggle_bars)
        self.bind("<p>", self.toggle_pixels)
        self.bind("<P>", self.toggle_pixels)
        self.bind("<g>", lambda e: self.resize_grid(scale=1.25))
        self.bind("<G>", lambda e: self.resize_grid(scale=1.25))
        self.bind("<h>", lambda e: self.resize_grid(scale=0.8))
        self.bind("<H>", lambda e: self.resize_grid(scale=0.8))

        self.after(0, self.setup_scene)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def toggle_bars(self, event=None):
        self.show_bars = not self.show_bars

    def toggle_pixels(self, event=None):
        self.show_pixels = not self.show_pixels

    def resize_grid(self, scale=1.0):
        cols = max(8, int(self.cfg.grid_cols * scale))
        rows = max(8, int(self.cfg.grid_rows * scale))
        self.cfg.grid_cols, self.cfg.grid_rows = cols, rows
        self.setup_grid()

    def setup_scene(self):
        self.canvas.delete("all")
        self.setup_grid()
        self.after(0, self.loop)

    def setup_grid(self):
        # Compute layout areas
        w = self.canvas.winfo_width() or self.cfg.width
        h = self.canvas.winfo_height() or self.cfg.height
        info_h = self.cfg.info_height
        bar_w = self.cfg.bar_area_width if self.show_bars else 0

        grid_x = bar_w + self.cfg.grid_margin
        grid_y = self.cfg.grid_margin + info_h
        grid_w = max(10, w - grid_x - self.cfg.grid_margin)
        grid_h = max(10, h - grid_y - self.cfg.grid_margin)

        cols = self.cfg.grid_cols
        rows = self.cfg.grid_rows
        cell_w = grid_w / cols
        cell_h = grid_h / rows

        # Precreate rectangles
        self.pixel_grid = []
        self.canvas.delete("pixel")
        for r in range(rows):
            row = []
            for c in range(cols):
                x0 = grid_x + c * cell_w
                y0 = grid_y + r * cell_h
                x1 = x0 + cell_w - 1
                y1 = y0 + cell_h - 1
                rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.cfg.pixel_off, outline="", tags=("pixel",))
                row.append(rect)
            self.pixel_grid.append(row)

        # Precreate bar background
        self.canvas.delete("bars")
        if self.show_bars:
            self.canvas.create_rectangle(0, info_h, bar_w, h, fill=self.cfg.bar_bg, outline="", tags=("bars",))

    def loop(self):
        now = time.time()
        if now - self.last_time >= self.frame_time:
            self.last_time = now
            self.update_frame()
        self.after(int(self.frame_time * 1000 / 2), self.loop)

    def update_frame(self):
        per_core, overall, procs, cs = self.meter.snapshot()
        w = self.canvas.winfo_width() or self.cfg.width
        h = self.canvas.winfo_height() or self.cfg.height
        info_h = self.cfg.info_height

        # Clear info line
        self.canvas.delete("info")
        info_text = f"CPU gesamt: {overall:5.1f}%"
        if procs is not None:
            info_text += f"  |  Prozesse: {procs}"
        if cs is not None:
            info_text += f"  |  Kontextwechsel: {cs:,}"
        info_text += "  |  [F]ullscreen  [B]ars  [P]ixels  [G/H] Grid±  [Q]uit"
        self.canvas.create_rectangle(0, 0, w, info_h, fill=self.cfg.bg, outline="", tags=("info",))
        self.canvas.create_text(12, info_h/2, text=info_text, anchor="w", fill=self.cfg.fg, font=("JetBrains Mono", 12), tags=("info",))

        # Bars
        self.canvas.delete("baritem")
        if self.show_bars:
            bar_w = self.cfg.bar_area_width
            bar_x0, bar_x1 = 16, bar_w - 16
            # If psutil missing, draw only one bar
            cores = len(per_core) if psutil else 1
            for i in range(cores):
                val = per_core[i] if psutil else overall
                y0 = info_h + 16 + i * 20
                y1 = y0 + 14
                self.canvas.create_rectangle(bar_x0, y0, bar_x1, y1, fill=self.cfg.bg, outline="", tags=("baritem",))
                # fill
                fill_x = bar_x0 + (bar_x1 - bar_x0) * (max(0.0, min(100.0, val)) / 100.0)
                self.canvas.create_rectangle(bar_x0, y0, fill_x, y1, fill=self.cfg.bar_fg, outline="", tags=("baritem",))
                # label
                self.canvas.create_text(bar_x0, y0-1, text=(f"Kern {i}" if psutil else "Gesamt"),
                                        anchor="sw", fill=self.cfg.fg, font=("JetBrains Mono", 9), tags=("baritem",))

        # Pixels (blink based on utilization-driven probability)
        if self.show_pixels and self.pixel_grid:
            cols = len(self.pixel_grid[0])
            rows = len(self.pixel_grid)
            # Flicker probability scaled by overall; also add subtle wave so it doesn't look uniform
            p_on = max(0.02, min(0.98, (overall/100.0) * 0.9 + 0.05))
            t = time.time()
            wave = (math.sin(t * 2.0) + 1.0) * 0.04  # 0..0.08
            p_on = max(0.0, min(1.0, p_on + wave))

            rnd = random.Random(self.seed + int(t*10))
            for r, row in enumerate(self.pixel_grid):
                for c, rect in enumerate(row):
                    # Make clusters by mixing random with a smooth pattern
                    noise = rnd.random()
                    pattern = (math.sin((c + t*3) * 0.23) * math.cos((r - t*2) * 0.19) + 1) * 0.25
                    intensity = p_on*0.6 + noise*0.3 + pattern*0.1
                    # Thresholds for off/mid/on
                    if intensity > 0.66:
                        color = self.cfg.pixel_on
                    elif intensity > 0.45:
                        color = self.cfg.pixel_mid
                    else:
                        color = self.cfg.pixel_off
                    self.canvas.itemconfig(rect, fill=color)

    def quit_app(self):
        try:
            self.meter.stop()
        except Exception:
            pass
        self.destroy()


def main():
    cfg = Config()
    meter = CPUMeter()
    app = Visualizer(cfg, meter)
    app.mainloop()


if __name__ == "__main__":
    main()
