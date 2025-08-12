import tkinter as tk
import random
import time
import os

try:
    import pygame
except ImportError:
    print("pygame is required for sound playback. Install it with 'pip install pygame'")
    pygame = None

PASSWORD = "iamyou"
POPUP_COUNT = 5
MOVE_INTERVAL = 0.02

PHRASES = [
    "CHAOS MODE!",
    "LOL 😂",
    "Click me!",
    "Too fast for you?",
    "Try again...",
    "Randomness++",
    "So many windows",
    "Catch me if you can",
    "🤣🤣🤣",
    "No escape!",
    "Boom! 💥",
    "👀👀👀"
]

FONTS = [
    ("Arial", 20),
    ("Comic Sans MS", 24, "bold"),
    ("Courier", 18, "italic"),
    ("Helvetica", 22, "bold italic"),
    ("Times", 26, "bold"),
    ("Impact", 28)
]

SOUND_FILE = os.path.join(os.path.dirname(__file__), "Leck Sibbi - Nimo - SoundLoadMate.com.mp3")
VOLUME = 0.8

class MovingPopup:
    def __init__(self, root, id):
        self.id = id
        self.root = tk.Toplevel(root)
        self.root.title(f"Popup {id}")
        self.root.configure(bg=self.random_color())
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        phrase = random.choice(PHRASES)
        font_choice = random.choice(FONTS)
        self.label = tk.Label(self.root, text=phrase, font=font_choice,
                              fg=self.random_color(), bg=self.random_color())
        self.label.pack(expand=True, fill="both", padx=20, pady=20)

        stop_btn = tk.Button(self.root, text="STOP", command=self.safe_exit,
                             bg="red", fg="white", font=("Arial", 14, "bold"))
        stop_btn.pack(pady=5)

        self.moving = True
        self.current_x = random.randint(0, 500)
        self.current_y = random.randint(0, 300)
        self.target_x = self.current_x
        self.target_y = self.current_y
        self.steps = 0
        self.root.geometry(f"+{self.current_x}+{self.current_y}")

        self.animate()

    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def animate(self):
        if not self.moving:
            return
        self.label.config(text=random.choice(PHRASES), fg=self.random_color())
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if self.steps <= 0:
            self.target_x = random.randint(0, screen_width - 200)
            self.target_y = random.randint(0, screen_height - 100)
            self.steps = random.randint(10, 30)
        dx = (self.target_x - self.current_x) / self.steps
        dy = (self.target_y - self.current_y) / self.steps
        self.current_x += dx
        self.current_y += dy
        self.steps -= 1
        self.root.geometry(f"+{int(self.current_x)}+{int(self.current_y)}")
        self.root.after(int(MOVE_INTERVAL * 1000), self.animate)

    def close(self):
        self.moving = False
        self.root.destroy()

    def safe_exit(self):
        os._exit(0)

class PopupManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.popups = {}
        self.password_correct = False
        self.popup_count = POPUP_COUNT

        if pygame:
            pygame.mixer.init()
            try:
                pygame.mixer.music.load(SOUND_FILE)
                pygame.mixer.music.set_volume(VOLUME)
            except Exception as e:
                print(f"Error loading sound: {e}")

        self.root.bind_all("<Escape>", lambda e: self.quit_all())

    def quit_all(self):
        self.close_all_popups()
        if pygame:
            pygame.mixer.music.stop()
        self.root.quit()
        os._exit(0)

    def create_popups(self, count=None):
        if count is None:
            count = self.popup_count
        for i in range(len(self.popups) + 1, len(self.popups) + count + 1):
            popup = MovingPopup(self.root, i)
            self.popups[i] = popup

    def close_all_popups(self):
        for p in list(self.popups.values()):
            p.close()
        self.popups.clear()

    def show_password_prompt(self):
        def check_password():
            pwd = entry.get()
            if pwd == PASSWORD:
                self.password_correct = True
                self.quit_all()
            else:
                entry.delete(0, tk.END)
                self.popup_count += 5
                self.create_popups(5)

        top = tk.Toplevel(self.root)
        top.title("Password Required")
        top.geometry("300x120")
        label = tk.Label(top, text="Enter password:")
        label.pack(pady=5)
        entry = tk.Entry(top, show="*")
        entry.pack(pady=5)
        entry.focus_set()
        btn = tk.Button(top, text="Submit", command=check_password)
        btn.pack(pady=5)

    def run_cycle(self):
        confirm = tk.Toplevel()
        confirm.title("Confirmation")
        tk.Label(confirm, text="Actually run it?", font=("Arial", 14)).pack(pady=10)
        tk.Button(confirm, text="Yes", command=confirm.destroy,
                  width=10, bg="green", fg="white").pack(side="left", padx=20, pady=10)
        tk.Button(confirm, text="No", command=lambda: os._exit(0),
                  width=10, bg="red", fg="white").pack(side="right", padx=20, pady=10)

        self.root.wait_window(confirm)

        if pygame:
            try:
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error playing sound: {e}")

        self.show_password_prompt()
        self.create_popups()

        while not self.password_correct:
            try:
                self.root.update()
            except tk.TclError:
                break
            time.sleep(0.01)

if __name__ == "__main__":
    manager = PopupManager()
    manager.run_cycle()
