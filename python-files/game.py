import tkinter as tk, random, time, os
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────
W, H          = 1280, 720          # start‑up window size
BG            = "#0d0d10"
ACCENT        = "#9b5de5"
TEXT          = "#ffffff"
HIT_COLOR     = "#35e8a4"
CROSSHAIR_PNG = "crosshair.png"     # 64×64 transparent image
DIFFICULTY    = {
    "Easy"  : {"rate": 900, "radius": 32},
    "Medium": {"rate": 650, "radius": 26},
    "Hard"  : {"rate": 450, "radius": 22}
}
# ───────────────────────────────────────────────────────────────────────────

class AimTrainer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SCUBA’S AIM TRAINER")
        self.root.configure(bg=BG)
        self.fullscreen = False
        self.root.geometry(f"{W}x{H}+60+40")
        self.root.bind("<F11>", self.toggle_full)
        self.root.bind("<Escape>", self.end_full)

        # ---------- top bar ----------
        bar = tk.Frame(root, bg=BG)
        bar.pack(pady=6)
        tk.Label(bar, text="SCUBA’S AIM TRAINER",
                 font=("Consolas", 22, "bold"), fg=ACCENT, bg=BG).grid(row=0, column=0, columnspan=3)

        # Controls
        tk.Button(bar, text="Start", command=self.start,
                  bg="#222", fg=TEXT, width=8).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(bar, text="Restart", command=self.restart,
                  bg="#444", fg=TEXT, width=8).grid(row=1, column=1, padx=4, pady=4)

        # Difficulty dropdown
        self.dvar = tk.StringVar(value="Medium")
        diff_menu = tk.OptionMenu(bar, self.dvar, *DIFFICULTY.keys())
        diff_menu.config(bg="#333", fg=TEXT, width=8)
        diff_menu.grid(row=1, column=2, padx=4, pady=4)

        # Timer dropdown
        self.tvar = tk.StringVar(value="60")  # seconds
        tk.OptionMenu(bar, self.tvar, "30", "60", "∞").grid(row=1, column=3, padx=4)

        # ---------- canvas ----------
        self.cv = tk.Canvas(root, bg=BG, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        self.cv.focus_set()                     # capture key / click
        self.cv.bind("<Button-1>", self.shoot)
        self.cv.bind("<Motion>", self.move_crosshair)

        # crosshair image
        self.crosshair = None
        if Path(CROSSHAIR_PNG).exists():
            self.cross_img = tk.PhotoImage(file=CROSSHAIR_PNG)
            self.crosshair = self.cv.create_image(0, 0, image=self.cross_img)

        # stats / timer
        self.info = tk.Label(root, fg=TEXT, bg=BG, font=("Consolas", 12))
        self.info.pack(pady=4)

        # game vars
        self.reset_game()

    # ---------- Game state ----------
    def reset_game(self):
        self.targets = set()
        self.hits = self.misses = 0
        self.start_ts = None
        self.session = 0
        self.spawn_loop_id = None
        self.timer_loop_id = None
        self.cv.delete("all")
        if self.crosshair:  # redraw crosshair on top
            self.crosshair = self.cv.create_image(0, 0, image=self.cross_img)

    def start(self):
        # init session
        self.reset_game()
        self.session = 0 if self.tvar.get() == "∞" else int(self.tvar.get())
        self.start_ts = time.time()
        self.spawn_target()            # spawn first immediately
        self.update_timer()
        self.spawn_loop()

    def restart(self):
        self.reset_game()
        self.start()

    # ---------- Spawn & timer loops ----------
    def spawn_loop(self):
        if self.session and (time.time() - self.start_ts) >= self.session:
            return
        self.spawn_target()
        rate = DIFFICULTY[self.dvar.get()]["rate"]
        self.spawn_loop_id = self.root.after(rate, self.spawn_loop)

    def update_timer(self):
        if self.session:
            remaining = self.session - (time.time() - self.start_ts)
            if remaining <= 0:
                self.end_game(); return
            timer_str = f"{remaining:4.1f}s"
        else:
            timer_str = "∞"
        acc = 100 * self.hits / max(1, self.hits + self.misses)
        cpm = self.hits / max(1, time.time() - self.start_ts) * 60
        self.info.config(text=f"Time:{timer_str}  Hits:{self.hits}  "
                              f"Misses:{self.misses}  Acc:{acc:4.1f}%  CPM:{cpm:4.0f}")
        self.timer_loop_id = self.root.after(200, self.update_timer)

    def spawn_target(self):
        r = DIFFICULTY[self.dvar.get()]["radius"]
        w, h = self.cv.winfo_width(), self.cv.winfo_height()
        x, y = random.randint(r, max(r, w - r)), random.randint(r, max(r, h - r))
        tid = self.cv.create_oval(x - r, y - r, x + r, y + r,
                                  fill=ACCENT, outline="")
        self.targets.add(tid)
        # auto despawn to count as miss
        self.root.after(2000, lambda t=tid: self.despawn(t))

    def despawn(self, tid):
        if tid in self.targets:
            self.targets.remove(tid)
            self.cv.delete(tid)
            self.misses += 1

    # ---------- Shooting logic ----------
    def shoot(self, ev):
        x = self.cv.canvasx(ev.x); y = self.cv.canvasy(ev.y)
        collided = self.cv.find_overlapping(x, y, x, y)
        scored = False
        for cid in collided:
            if cid in self.targets:
                scored = True
                self.cv.delete(cid)
                self.targets.remove(cid)
        if scored:
            self.hits += 1
        else:
            self.misses += 1

    def move_crosshair(self, ev):
        if self.crosshair:
            self.cv.coords(self.crosshair, ev.x, ev.y)

    # ---------- Finish ----------
    def end_game(self):
        # stop loops
        if self.spawn_loop_id: self.root.after_cancel(self.spawn_loop_id)
        if self.timer_loop_id: self.root.after_cancel(self.timer_loop_id)
        self.cv.delete("all")
        msg = (f"SESSION COMPLETE\n\nHits: {self.hits}\n"
               f"Misses: {self.misses}\n"
               f"Accuracy: {100*self.hits/max(1,self.hits+self.misses):.1f}%")
        self.cv.create_text(self.cv.winfo_width()//2, self.cv.winfo_height()//2,
                            text=msg, fill=ACCENT, font=("Consolas", 26), justify="center")

    # ---------- Fullscreen helpers ----------
    def toggle_full(self, _=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def end_full(self, _=None):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)

# ── Run ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    AimTrainer(root)
    root.mainloop()
