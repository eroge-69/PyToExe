import tkinter as tk
import random
import math

# --- Tunables ---------------------------------------------------------------
WIDTH, HEIGHT = 800, 500
PADDLE_W, PADDLE_H = 12, 90
BALL_SIZE = 14

PADDLE_SPEED = 7            # px per frame (manual)
CPU_BASE_SPEED = 5          # px per frame (AI baseline)
CPU_TRACK_GAIN = 0.18       # how aggressively CPU follows ball
BALL_SPEED = 6.0            # initial px per frame (horizontal magnitude)
BALL_SPIN = 4.0             # how much off-center adds to Vy
BALL_VY_CLAMP = 9.0         # cap vertical speed
WIN_SCORE = 7
FPS = 60                    # target frames per second
# ---------------------------------------------------------------------------

class Pong:
    def __init__(self, root):
        self.root = root
        root.title("Tkinter Pong")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#0b0f19", highlightthickness=0)
        self.canvas.pack()

        # Scores & state
        self.left_score = 0
        self.right_score = 0
        self.paused = False
        self.running = True
        self.cpu_right = False

        # Input handling
        self.held = set()
        self.toggle_latch = set()   # to avoid auto-repeat on toggle keys

        root.bind("<KeyPress>", self._on_keydown)
        root.bind("<KeyRelease>", self._on_keyup)

        # Draw static net
        self._draw_net()

        # Create entities
        self.left = self.canvas.create_rectangle(30, (HEIGHT-PADDLE_H)//2,
                                                 30+PADDLE_W, (HEIGHT-PADDLE_H)//2 + PADDLE_H,
                                                 fill="#e6e6e6", outline="")
        self.right = self.canvas.create_rectangle(WIDTH-30-PADDLE_W, (HEIGHT-PADDLE_H)//2,
                                                  WIDTH-30, (HEIGHT-PADDLE_H)//2 + PADDLE_H,
                                                  fill="#e6e6e6", outline="")
        cx, cy = WIDTH/2, HEIGHT/2
        self.ball = self.canvas.create_oval(cx-BALL_SIZE/2, cy-BALL_SIZE/2,
                                            cx+BALL_SIZE/2, cy+BALL_SIZE/2,
                                            fill="#9fe870", outline="")

        # UI text
        self.score_text = self.canvas.create_text(WIDTH/2, 30, fill="#e6e6e6",
                                                  font=("Consolas", 24, "bold"),
                                                  text="0   PONG   0")
        self.help_text = self.canvas.create_text(WIDTH/2, HEIGHT-20, fill="#9aa4b2",
                                                 font=("Consolas", 12),
                                                 text="[W/S] Left  [↑/↓] Right   [P]ause  [R]eset  [C]PU Right  [Esc/Q] Quit")

        self.banner_items = []  # overlay group

        # Physics
        self.vx = 0.0
        self.vy = 0.0
        self.reset_round(center_scores=True)

        # Main loop
        self._tick()

    # ---------------------- Input -----------------------------------------
    def _on_keydown(self, e):
        ks = e.keysym
        self.held.add(ks)

        # One-shot toggles with latch to avoid repeats
        if ks.lower() in ("p", "r", "c", "q") or ks == "Escape":
            if ks not in self.toggle_latch:
                self.toggle_latch.add(ks)
                if ks.lower() == "p":
                    self.paused = not self.paused
                    if self.paused:
                        self._show_banner("PAUSED")
                    else:
                        self._clear_banner()
                elif ks.lower() == "r":
                    self.reset_round()
                elif ks.lower() == "c":
                    self.cpu_right = not self.cpu_right
                    self._flash_bottom(f"CPU Right: {'ON' if self.cpu_right else 'OFF'}")
                elif ks.lower() in ("q",) or ks == "Escape":
                    self.running = False
                    self.root.destroy()

    def _on_keyup(self, e):
        ks = e.keysym
        if ks in self.held:
            self.held.remove(ks)
        if ks in self.toggle_latch:
            self.toggle_latch.remove(ks)

    # ---------------------- Drawing ---------------------------------------
    def _draw_net(self):
        self.canvas.delete("net")
        x = WIDTH/2
        seg = 12
        gap = 10
        y = 0
        while y < HEIGHT:
            self.canvas.create_line(x, y, x, min(y+seg, HEIGHT), fill="#324055", width=3, tags="net")
            y += seg + gap

    def _update_scoreboard(self):
        self.canvas.itemconfigure(self.score_text, text=f"{self.left_score}   PONG   {self.right_score}")

    def _show_banner(self, msg):
        self._clear_banner()
        rect = self.canvas.create_rectangle(WIDTH*0.2, HEIGHT*0.35, WIDTH*0.8, HEIGHT*0.65,
                                            fill="#111827", outline="#3b82f6", width=3)
        txt = self.canvas.create_text(WIDTH/2, HEIGHT/2, text=msg, fill="#e6e6e6",
                                      font=("Consolas", 28, "bold"))
        self.banner_items = [rect, txt]

    def _clear_banner(self):
        for it in self.banner_items:
            self.canvas.delete(it)
        self.banner_items.clear()

    def _flash_bottom(self, msg, ms=900):
        # Temporary message at bottom
        self.canvas.itemconfigure(self.help_text, text=msg)
        self.root.after(ms, lambda: self.canvas.itemconfigure(
            self.help_text,
            text="[W/S] Left  [↑/↓] Right   [P]ause  [R]eset  [C]PU Right  [Esc/Q] Quit"
        ))

    # ---------------------- Game Logic ------------------------------------
    def reset_round(self, center_scores=False):
        if center_scores:
            self.left_score = 0
            self.right_score = 0
        self._update_scoreboard()
        self._clear_banner()

        # Center paddles
        self._set_rect_center_y(self.left, HEIGHT/2)
        self._set_rect_center_y(self.right, HEIGHT/2)

        # Center ball
        self._set_ball_center(WIDTH/2, HEIGHT/2)

        # Random initial direction
        dirx = random.choice([-1, 1])
        angle = random.uniform(-0.35, 0.35)  # small vertical component
        self.vx = dirx * BALL_SPEED
        self.vy = math.sin(angle) * BALL_SPEED

        # Unpause on reset
        self.paused = False

    def _set_rect_center_y(self, item, cy):
        x1, y1, x2, y2 = self.canvas.coords(item)
        h = (y2 - y1)
        new_y1 = cy - h/2
        new_y2 = cy + h/2
        self.canvas.coords(item, x1, new_y1, x2, new_y2)

    def _set_ball_center(self, cx, cy):
        r = BALL_SIZE/2
        self.canvas.coords(self.ball, cx-r, cy-r, cx+r, cy+r)

    def _get_center_y(self, item):
        x1, y1, x2, y2 = self.canvas.coords(item)
        return (y1 + y2) / 2

    def _move_paddle_manual(self, item, up_key, down_key):
        dy = 0
        if up_key in self.held:
            dy -= PADDLE_SPEED
        if down_key in self.held:
            dy += PADDLE_SPEED
        if dy:
            self._move_paddle(item, dy)

    def _move_paddle_cpu(self, item):
        # Track the ball with some lag and capped speed
        _, by1, _, by2 = self.canvas.coords(self.ball)
        ball_cy = (by1 + by2) / 2
        py = self._get_center_y(item)
        diff = ball_cy - py
        step = CPU_BASE_SPEED + abs(diff) * CPU_TRACK_GAIN
        dy = max(-step, min(step, diff))
        self._move_paddle(item, dy)

    def _move_paddle(self, item, dy):
        # Clamp within top/bottom
        x1, y1, x2, y2 = self.canvas.coords(item)
        if y1 + dy < 0:
            dy = -y1
        if y2 + dy > HEIGHT:
            dy = HEIGHT - y2
        if dy:
            self.canvas.move(item, 0, dy)

    def _rects_intersect(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

    def _ball_center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.ball)
        return (x1+x2)/2, (y1+y2)/2

    def _tick(self):
        if not self.running:
            return

        if not self.paused:
            # --- Input & paddles
            self._move_paddle_manual(self.left, "w", "s")
            if self.cpu_right:
                self._move_paddle_cpu(self.right)
            else:
                self._move_paddle_manual(self.right, "Up", "Down")

            # --- Move ball
            self.canvas.move(self.ball, self.vx, self.vy)
            bx1, by1, bx2, by2 = self.canvas.coords(self.ball)

            # --- Bounce top/bottom
            if by1 <= 0 and self.vy < 0:
                self.vy = -self.vy
                self.canvas.coords(self.ball, bx1, 0, bx2, BALL_SIZE)
            elif by2 >= HEIGHT and self.vy > 0:
                self.vy = -self.vy
                self.canvas.coords(self.ball, bx1, HEIGHT-BALL_SIZE, bx2, HEIGHT)

            # --- Paddle collisions
            lx1, ly1, lx2, ly2 = self.canvas.coords(self.left)
            rx1, ry1, rx2, ry2 = self.canvas.coords(self.right)

            # Left paddle
            if self.vx < 0 and self._rects_intersect((bx1, by1, bx2, by2), (lx1, ly1, lx2, ly2)):
                # place ball just outside paddle to avoid sticking
                overlap = lx2 - bx1
                self.canvas.move(self.ball, overlap + 1, 0)
                _, by1, _, by2 = self.canvas.coords(self.ball)
                hit_offset = ((by1 + by2) / 2) - ((ly1 + ly2) / 2)
                hit_norm = hit_offset / (PADDLE_H / 2)
                self.vx = abs(self.vx) * 1.03
                self.vy = max(-BALL_VY_CLAMP, min(BALL_VY_CLAMP, self.vy + hit_norm * BALL_SPIN))

            # Right paddle
            bx1, by1, bx2, by2 = self.canvas.coords(self.ball)  # refresh after possible move
            if self.vx > 0 and self._rects_intersect((bx1, by1, bx2, by2), (rx1, ry1, rx2, ry2)):
                overlap = bx2 - rx1
                self.canvas.move(self.ball, -(overlap + 1), 0)
                _, by1, _, by2 = self.canvas.coords(self.ball)
                hit_offset = ((by1 + by2) / 2) - ((ry1 + ry2) / 2)
                hit_norm = hit_offset / (PADDLE_H / 2)
                self.vx = -abs(self.vx) * 1.03
                self.vy = max(-BALL_VY_CLAMP, min(BALL_VY_CLAMP, self.vy + hit_norm * BALL_SPIN))

            # --- Scoring (ball off left/right)
            bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
            if bx2 < 0:
                self.right_score += 1
                self._finish_point()
            elif bx1 > WIDTH:
                self.left_score += 1
                self._finish_point()

        # Target frame time
        self.root.after(int(1000 / FPS), self._tick)

    def _finish_point(self):
        self._update_scoreboard()
        if self.left_score >= WIN_SCORE or self.right_score >= WIN_SCORE:
            winner = "Left Player" if self.left_score > self.right_score else "Right Player"
            self._show_banner(f"{winner} Wins!")
            # Reset scores after short celebration
            self.paused = True
            self.root.after(1200, lambda: (self.reset_round(center_scores=True)))
        else:
            self.reset_round(center_scores=False)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = Pong(root)
    root.mainloop()