import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import time
import pygame
from pathlib import Path
import pygame
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = Path(sys._MEIPASS)  # PyInstaller temp folder
    except AttributeError:
        base_path = Path(__file__).parent
    return base_path / relative_path


# Define the base path relative to this script
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# Constants
TRACK_LENGTH = 16
TRACK_HEIGHT = 120
MOVE_INTERVAL_MS = 5000
RESULTS_FILE = "race_results.txt"

# Initialize pygame mixer for sounds
pygame.mixer.init()

# Load sounds (make sure these files exist in assets/)
finish_sound = pygame.mixer.Sound(str(ASSETS_DIR / "sound_finish.wav"))

class RacingGame:
    def __init__(self, root, canvas, player_names, last_results_label):
        self.root = root
        self.canvas = canvas
        self.player_names = ["Machine"] + player_names
        self.positions = [0]*4
        self.finished = [False]*4
        self.move_times = [[] for _ in range(4)]
        self.last_results_label = last_results_label
        self.running = False
        self.start_time = None
        self.car_items = []
        self.lane_y_positions = []
        self.create_track()
        self.start_countdown()

    def create_track(self):
        self.canvas.delete("all")
        bg = Image.open(ASSETS_DIR / "background.png").resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bg_photo = ImageTk.PhotoImage(bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        lane_width = WINDOW_WIDTH // 5
        lane_height = TRACK_HEIGHT - 20

        def remove_white(img):
            img = img.convert("RGBA")
            data = [(255, 255, 255, 0) if px[0] > 200 and px[1] > 200 and px[2] > 200 else px for px in img.getdata()]
            img.putdata(data)
            return img

        car_paths = [
            ASSETS_DIR / "car1.jpg",
            ASSETS_DIR / "car2.jpg",
            ASSETS_DIR / "car3.webp",  # converted from webp
            ASSETS_DIR / "car4.jpg"
        ]

        self.car_photos = [ImageTk.PhotoImage(remove_white(Image.open(p).resize((lane_width, lane_height)))) for p in car_paths]

        self.lane_y_positions = [TRACK_HEIGHT * (i + 1) for i in range(4)]
        for i, photo in enumerate(self.car_photos):
            y = self.lane_y_positions[i]
            car = self.canvas.create_image(0, y, anchor="w", image=photo)
            self.car_items.append(car)
            # Show driver names just above their cars
            self.canvas.create_text(10, y - 20, anchor="w", text=self.player_names[i], font=("Arial", 14, "bold"), fill="black")

        # Buttons for players (lanes 2-4)
        self.buttons = []
        for i in range(1, 4):
            btn = tk.Button(self.root, text=f"Move {self.player_names[i]}",
                            command=lambda i=i: self.move_car(i), bg="lightblue")
            btn.place(x=100 + i * 150, y=20)
            self.buttons.append(btn)

        # Race timer text in top-left
        self.timer_text = self.canvas.create_text(10, 10, anchor="nw", text="Time: 0.0s",
                                                  font=("Arial", 16, "bold"), fill="white")

    def start_countdown(self):
        self.countdown_val = 3
        self.countdown_text = self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                                                      text="3", font=("Arial", 60), fill="red")
        self._countdown()

    def _countdown(self):
        if self.countdown_val > 0:
            self.canvas.itemconfig(self.countdown_text, text=str(self.countdown_val))
            self.countdown_val -= 1
            self.root.after(1000, self._countdown)
        else:
            self.canvas.itemconfig(self.countdown_text, text="GO!")
            self.root.after(1000, lambda: self.canvas.delete(self.countdown_text))
            self.running = True
            self.start_time = time.time()
            self.update_timer()
            self.machine_loop()

    def update_timer(self):
        elapsed = time.time() - self.start_time
        self.canvas.itemconfig(self.timer_text, text=f"Time: {elapsed:.1f}s")
        if self.running:
            self.root.after(100, self.update_timer)

    def move_car(self, i):
        if not self.running or self.finished[i]:
            return
        self.move_times[i].append(time.time())
        if self.positions[i] < TRACK_LENGTH - 1:
            self.positions[i] += 1
            self.animate(i)
        if self.positions[i] >= TRACK_LENGTH - 1:
            self.finished[i] = True
            finish_sound.play()
            self.check_end()

    def machine_loop(self):
        if self.running and not self.finished[0]:
            self.move_car(0)
        if self.running:
            self.root.after(MOVE_INTERVAL_MS, self.machine_loop)

    def animate(self, i):
        x = self.positions[i] * 50
        y = self.lane_y_positions[i]

        def up():
            self.canvas.coords(self.car_items[i], x, y - 10)
            self.root.after(100, down)

        def down():
            self.canvas.coords(self.car_items[i], x, y)

        self.canvas.coords(self.car_items[i], x, y)
        up()

    def check_end(self):
        if any(pos >= TRACK_LENGTH - 1 for pos in self.positions):
            self.running = False
            # fireworks_sound.play()
            self.show_results()

    def show_results(self):
        popup = tk.Toplevel(self.root)
        popup.title("Race Results")
        popup.configure(bg="black")

        # Load and resize the fireworks GIF
        gif = Image.open(ASSETS_DIR / "fireworks.gif")
        frames = [ImageTk.PhotoImage(frame.copy().resize((500, 400))) for frame in ImageSequence.Iterator(gif)]

        # Set up a label to hold the background GIF
        label = tk.Label(popup, bg="black")
        label.pack(fill="both", expand=True)

        # Animate the GIF — must come after 'label' is defined
        def animate(idx=0):
            label.config(image=frames[idx])
            popup.after(100, lambda: animate((idx + 1) % len(frames)))

        animate()

        # Overlay frame for text
        overlay = tk.Frame(popup, bg="black")
        overlay.place(relx=0.5, rely=0.5, anchor="center")

        # Sort results and log them
        sorted_positions = sorted(enumerate(self.positions), key=lambda x: x[1], reverse=True)
        places = ["🏆 1st", "🥈 2nd", "🥉 3rd", "4th"]
        content_lines = ["Last Game Results:"]

        with open(RESULTS_FILE, "a", encoding="utf-8") as f:
            f.write(f"Game at {time.ctime()}:\n")
            for i, (idx, pos) in enumerate(sorted_positions):
                avg = self.avg_time(idx)
                line = f"{places[i]} {self.player_names[idx]} — moves: {pos}, avg time: {avg:.2f}s"
                content_lines.append(line)
                f.write(line + "\n")
            f.write("\n")

        self.last_results_label.config(text="\n".join(content_lines))

        # Display results on top of GIF
        for line in content_lines:
            tk.Label(overlay, text=line, font=("Arial", 16, "bold"), fg="white", bg="black").pack(pady=2)

        # New game button
        tk.Button(overlay, text="Start New Game",
                command=lambda: [popup.destroy(), ask_names(self.root)],
                font=("Arial", 12, "bold"), bg="white", fg="black").pack(pady=10)

        # Fireworks animation
        gif = Image.open(ASSETS_DIR / "fireworks.gif")
        frames = [ImageTk.PhotoImage(frame.copy().resize((200, 200))) for frame in ImageSequence.Iterator(gif)]
        label = tk.Label(popup, bg="white")
        label.pack()

        def animate(idx=0):
            label.config(image=frames[idx])
            popup.after(100, lambda: animate((idx + 1) % len(frames)))

        animate()

    def avg_time(self, i):
        times = self.move_times[i]
        if len(times) < 2:
            return 0.0
        return sum(times[j] - times[j - 1] for j in range(1, len(times))) / (len(times) - 1)


def ask_names(root):
    # Clear all widgets
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root)
    frame.pack(pady=50)

    entries = []
    for i in range(3):
        tk.Label(frame, text=f"Player {i + 1} (Lane {i + 2}):").pack()
        e = tk.Entry(frame)
        e.pack()
        entries.append(e)

    # Label for last game results top-right corner
    last_results_label = tk.Label(root, text="", font=("Arial", 10), justify="right")
    last_results_label.place(relx=1, rely=0, anchor="ne")

    def start_game():
        names = [e.get().strip() for e in entries]
        if all(names):
            frame.destroy()
            canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
            canvas.pack()
            RacingGame(root, canvas, names, last_results_label)
            root.bind('<q>', lambda e: root.destroy())

    tk.Button(frame, text="Start Game", command=start_game).pack(pady=10)


def main():
    global root, WINDOW_WIDTH, WINDOW_HEIGHT
    root = tk.Tk()
    root.title("Racing Game")

    bg_img = Image.open(ASSETS_DIR / "background.png")
    WINDOW_WIDTH, WINDOW_HEIGHT = bg_img.size

    ask_names(root)
    root.mainloop()


if __name__ == "__main__":
    main()
