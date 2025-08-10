import tkinter as tk
import random
import winsound
import threading
import time
import math

class RhythmGame:
    def __init__(self, root):
        self.root = root
        self.root.title("FREQ")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=400, height=600, highlightthickness=0)
        self.canvas.pack()

        self.hit_zone_y = 500
        self.hit_zone_height = 30
        self.circle_radius = 25
        self.base_speed = 3
        self.max_speed = 13
        self.speed = self.base_speed
        self.spawn_interval = 1200

        self.score = 0
        self.combo = 0

        self.circles = []
        self.particles = []
        self.running = False

        self.bg_top_color = (15, 32, 39)
        self.bg_bottom_color = (44, 83, 100)

        self.draw_gradient_bg()
        self.score_text = None
        self.hit_miss_text = None

        self.start_button = None
        self.countdown_text = None

        # List of random subtitles (like splash texts)
        self.subtitles = [
            "(Pronounced 'Freak')",
            "You spin me right round!",
            "Rhythm is life.",
            "Press all the circles!",
            "Get ready to FREQ out!",
            "Not your average rhythm game.",
            "Keep calm and hit perfect.",
            "Where beats meet pixels.",
            "Glitching in style.",
            "Stay on the beat!",
            "Warning: Addictive gameplay.",
            "Circles gonna circle.",
            "Make every hit count!",
            "Sync or miss!",
            "Dance your fingers off.",
            "Freakiest game in the world",
            "Powered by Tinker Python library"
        ]

        self.show_start_menu()

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def lerp_color(self, c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    def draw_gradient_bg(self):
        self.canvas.delete("bg")
        steps = 100
        for i in range(steps):
            ratio = i / steps
            color = self.lerp_color(self.bg_top_color, self.bg_bottom_color, ratio)
            hex_color = self.rgb_to_hex(color)
            y1 = int(600 * i / steps)
            y2 = int(600 * (i + 1) / steps)
            self.canvas.create_rectangle(0, y1, 400, y2, fill=hex_color, width=0, tags="bg")

    # ---------------------------
    # Start Menu with Effects
    # ---------------------------
    def show_start_menu(self):
        self.canvas.delete("all")
        self.draw_gradient_bg()

        # Create title starting off-screen
        self.canvas.create_text(
            200, -100, text="FREQ", fill="#00ffff",
            font=("Segoe UI Black", 72, "bold"),
            tags="title", anchor="center"
        )

        # Choose a random subtitle from the list
        random_subtitle = random.choice(self.subtitles)

        # Subtitle
        self.canvas.create_text(
            200, 250, text=random_subtitle,
            fill="#00cccc", font=("Segoe UI", 20, "italic"),
            tags="subtitle", anchor="center"
        )

        # Start button
        self.start_button = tk.Button(
            self.root, text="Start Game", font=("Segoe UI", 24, "bold"),
            bg="#00ffff", fg="#002222", activebackground="#00cccc",
            bd=0, highlightthickness=0,
            command=self.start_countdown
        )
        self.canvas.create_window(200, 350, window=self.start_button)

        self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg="#00cccc"))
        self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg="#00ffff"))

        # Animate title and glow
        self.animate_title_drop()
        self.animate_title_glow()

    def animate_title_drop(self, target_y=180):
        coords = self.canvas.coords("title")
        if coords:
            x, y = coords
            if y < target_y:
                self.canvas.move("title", 0, 10)
                self.root.after(20, self.animate_title_drop)
            else:
                self.play_title_sound()

    def animate_title_glow(self):
        if not self.start_button:
            return
        t = time.time()
        glow = int((math.sin(t * 2) + 1) / 2 * 128) + 127  # 127–255
        color = self.rgb_to_hex((0, glow, glow))
        self.canvas.itemconfig("title", fill=color)
        self.root.after(50, self.animate_title_glow)

    def play_title_sound(self):
        def sound():
            for freq in range(400, 800, 50):
                winsound.Beep(freq, 30)
        threading.Thread(target=sound, daemon=True).start()

    # ---------------------------
    # Countdown and Game Start
    # ---------------------------
    def start_countdown(self):
        if self.start_button:
            self.start_button.destroy()
            self.start_button = None
        self.canvas.delete("title")
        self.canvas.delete("subtitle")

        self.countdown_number = 3
        self.countdown_text = self.canvas.create_text(200, 300, text=str(self.countdown_number),
                                                      fill="#00ffff", font=("Segoe UI Black", 96, "bold"),
                                                      anchor="center")
        self.countdown_fade_in_step = 0
        self.countdown_fade_out_step = 0
        self.fade_in_countdown()

    def fade_in_countdown(self):
        steps = 10
        if self.countdown_fade_in_step <= steps:
            t = self.countdown_fade_in_step / steps
            color = self.lerp_color(self.bg_bottom_color, (0, 255, 255), t)
            hex_color = self.rgb_to_hex(color)
            self.canvas.itemconfig(self.countdown_text, fill=hex_color)
            self.countdown_fade_in_step += 1
            self.root.after(50, self.fade_in_countdown)
        else:
            self.root.after(600, self.fade_out_countdown)

    def fade_out_countdown(self):
        steps = 10
        if self.countdown_fade_out_step <= steps:
            t = 1 - (self.countdown_fade_out_step / steps)
            color = self.lerp_color(self.bg_bottom_color, (0, 255, 255), t)
            hex_color = self.rgb_to_hex(color)
            self.canvas.itemconfig(self.countdown_text, fill=hex_color)
            self.countdown_fade_out_step += 1
            self.root.after(50, self.fade_out_countdown)
        else:
            self.countdown_number -= 1
            if self.countdown_number > 0:
                self.canvas.itemconfig(self.countdown_text, text=str(self.countdown_number))
                self.countdown_fade_in_step = 0
                self.countdown_fade_out_step = 0
                self.fade_in_countdown()
            else:
                self.canvas.delete(self.countdown_text)
                self.start_game()

    # ---------------------------
    # Main Game
    # ---------------------------
    def start_game(self):
        self.canvas.delete("all")
        self.draw_gradient_bg()
        self.running = True
        self.score = 0
        self.combo = 0
        self.speed = self.base_speed
        self.circles = []
        self.particles = []

        self.hit_zone_rect = self.canvas.create_rectangle(0, self.hit_zone_y,
                                                          400, self.hit_zone_y + self.hit_zone_height,
                                                          fill="#00ffff", outline="#00ffff", width=3, tags="hit_zone")

        self.score_text = self.canvas.create_text(10, 10, anchor="nw", fill="#00ffff",
                                                  font=("Segoe UI", 22, "bold"),
                                                  text=f"Score: {self.score}  Combo: {self.combo}")

        self.hit_miss_text = self.canvas.create_text(200, 100, text="", fill="#00ffff",
                                                    font=("Segoe UI Black", 42, "bold"), anchor="center")

        self.spawn_circle()
        self.update()
        self.animate_hit_zone_glow()

    def animate_hit_zone_glow(self):
        if not self.running:
            return
        t = time.time()
        glow = int((math.sin(t * 6) + 1) / 2 * 128) + 127
        glow_color = (0, glow, glow)
        color = self.rgb_to_hex(glow_color)
        self.canvas.itemconfig(self.hit_zone_rect, outline=color)
        self.root.after(50, self.animate_hit_zone_glow)

    def spawn_circle(self):
        if not self.running:
            return
        x = random.randint(self.circle_radius, 400 - self.circle_radius)
        shadow = self.canvas.create_oval(x - self.circle_radius + 4, -self.circle_radius * 2 + 4,
                                         x + self.circle_radius + 4, 0 + 4,
                                         fill="#660000", outline="")
        circle = self.canvas.create_oval(x - self.circle_radius, -self.circle_radius * 2,
                                         x + self.circle_radius, 0,
                                         fill="#ff3333", outline="#ff6666", width=2)
        self.circles.append((circle, shadow))
        delay = max(400, self.spawn_interval - int(self.combo * 30))
        self.root.after(delay, self.spawn_circle)

    def update(self):
        if not self.running:
            return

        to_remove = []
        # Slower speed scaling
        target_speed = min(self.base_speed + self.combo * 0.1, self.max_speed)
        self.speed += (target_speed - self.speed) * 0.1

        for circle, shadow in self.circles:
            self.canvas.move(circle, 0, self.speed)
            self.canvas.move(shadow, 0, self.speed)
            x1, y1, x2, y2 = self.canvas.coords(circle)
            if y1 > 600:
                self.combo = 0
                self.update_score_text()
                self.show_hit_miss("Miss!", "red")
                to_remove.append((circle, shadow))

        for circle, shadow in to_remove:
            self.canvas.delete(circle)
            self.canvas.delete(shadow)
            self.circles.remove((circle, shadow))

        self.update_particles()
        self.root.after(16, self.update)

    def update_score_text(self):
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}  Combo: {self.combo}")

    def show_hit_miss(self, text, color):
        self.canvas.itemconfig(self.hit_miss_text, text=text, fill=color)
        self.root.after(800, lambda: self.canvas.itemconfig(self.hit_miss_text, text=""))

    def update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['dy'] += 0.1
            p['life'] -= 1
            self.canvas.coords(p['id'], p['x']-3, p['y']-3, p['x']+3, p['y']+3)
            if p['life'] <= 0:
                self.canvas.delete(p['id'])
                self.particles.remove(p)

    def create_particles(self, x, y):
        for _ in range(15):
            dx = random.uniform(-2, 2)
            dy = random.uniform(-3, 0)
            particle_id = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#00ffff", outline="")
            self.particles.append({'id': particle_id, 'x': x, 'y': y, 'dx': dx, 'dy': dy, 'life': random.randint(15, 30)})

    def on_click(self, event):
        if not self.running:
            return
        for circle, shadow in self.circles:
            x1, y1, x2, y2 = self.canvas.coords(circle)
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            dist = ((event.x - cx) ** 2 + (event.y - cy) ** 2) ** 0.5
            if dist < self.circle_radius:
                # Check if circle is inside the hit zone
                if self.hit_zone_y <= cy <= self.hit_zone_y + self.hit_zone_height:
                    self.score += 100 + self.combo * 5
                    self.combo += 1
                    self.update_score_text()
                    self.show_hit_miss("Perfect!", "#00ffff")
                    self.create_particles(cx, cy)
                    self.canvas.delete(circle)
                    self.canvas.delete(shadow)
                    self.circles.remove((circle, shadow))
                    return
                else:
                    self.combo = 0
                    self.update_score_text()
                    self.show_hit_miss("Miss!", "red")
                    return
        # If clicked on empty space:
        self.combo = 0
        self.update_score_text()
        self.show_hit_miss("Miss!", "red")

def main():
    root = tk.Tk()
    game = RhythmGame(root)
    root.bind("<Button-1>", game.on_click)
    root.mainloop()

if __name__ == "__main__":
    main()
