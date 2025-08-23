Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from PIL import Image, ImageTk  # You need to have pillow installed
import os

WIDTH, HEIGHT = 800, 400
GRAVITY = 1
JUMP_SPEED = -15
MOVE_SPEED = 5

class Platformer:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="skyblue")
        self.canvas.pack()

        self.load_images()
        self.setup_game()

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.update()

    def load_images(self):
        self.images = {
            "mario_right": ImageTk.PhotoImage(Image.open("mario_right.png")),
            "mario_left": ImageTk.PhotoImage(Image.open("mario_left.png")),
            "luigi_right": ImageTk.PhotoImage(Image.open("luigi_right.png")),
            "luigi_left": ImageTk.PhotoImage(Image.open("luigi_left.png")),
            "goomba": ImageTk.PhotoImage(Image.open("goomba.png")),
        }

    def setup_game(self):
        self.dx = 0
        self.dy = 0
        self.on_ground = False
        self.direction = "right"

        # Restart button
        self.restart_button = tk.Button(self.root, text="Restart", command=self.restart_game)
        self.restart_button.pack()

        # Character select
        self.char = tk.StringVar(value="mario")
        tk.Radiobutton(self.root, text="Mario", variable=self.char, value="mario", command=self.restart_game).pack(side="left")
        tk.Radiobutton(self.root, text="Luigi", variable=self.char, value="luigi", command=self.restart_game).pack(side="left")

        self.create_level()

    def create_level(self):
        self.canvas.delete("all")

        self.platforms = [
            self.canvas.create_rectangle(0, HEIGHT - 40, WIDTH, HEIGHT, fill="green"),
            self.canvas.create_rectangle(150, 300, 350, 320, fill="brown"),
            self.canvas.create_rectangle(450, 250, 650, 270, fill="brown"),
            self.canvas.create_rectangle(100, 180, 250, 200, fill="brown"),
        ]
        self.ground = self.platforms[0]

        # Player
        self.player_image = self.images[f"{self.char.get()}_right"]
        self.player = self.canvas.create_image(50, HEIGHT - 60, image=self.player_image, anchor="nw")

        # Goombas
        self.goombas = []
        for x in [500, 200]:
            g = self.canvas.create_image(x, HEIGHT - 72, image=self.images["goomba"], anchor="nw", tags="dir_left")
            self.goombas.append(g)

    def restart_game(self):
        self.create_level()
        self.dx = 0
        self.dy = 0

    def key_press(self, event):
        if event.keysym == "Left":
            self.dx = -MOVE_SPEED
            self.direction = "left"
            self.update_player_image()
        elif event.keysym == "Right":
            self.dx = MOVE_SPEED
            self.direction = "right"
            self.update_player_image()
        elif event.keysym == "space" and self.on_ground:
            self.dy = JUMP_SPEED
            self.on_ground = False

    def key_release(self, event):
        if event.keysym in ("Left", "Right"):
            self.dx = 0

    def update_player_image(self):
        name = f"{self.char.get()}_{self.direction}"
        self.player_image = self.images[name]
        self.canvas.itemconfig(self.player, image=self.player_image)

    def move_player(self):
        self.dy += GRAVITY

        self.canvas.move(self.player, self.dx, 0)
        self.handle_horizontal_collision()

        self.canvas.move(self.player, 0, self.dy)
        self.handle_vertical_collision()

    def handle_horizontal_collision(self):
        x1, y1 = self.canvas.coords(self.player)
        x2, y2 = x1 + 32, y1 + 32
        for plat in self.platforms:
            px1, py1, px2, py2 = self.canvas.coords(plat)
            if y2 > py1 and y1 < py2:
                if x2 > px1 and x1 < px2:
                    if self.dx > 0:
                        self.canvas.move(self.player, px1 - x2, 0)
                    elif self.dx < 0:
                        self.canvas.move(self.player, px2 - x1, 0)

    def handle_vertical_collision(self):
        x1, y1 = self.canvas.coords(self.player)
        x2, y2 = x1 + 32, y1 + 32
        self.on_ground = False
        for plat in self.platforms:
            px1, py1, px2, py2 = self.canvas.coords(plat)
            if x2 > px1 and x1 < px2:
                if y2 > py1 and y1 < py2:
                    if self.dy > 0:
                        self.canvas.move(self.player, 0, py1 - y2)
                        self.dy = 0
                        self.on_ground = True
                    elif self.dy < 0:
                        self.canvas.move(self.player, 0, py2 - y1)
                        self.dy = 0

    def move_goombas(self):
        for g in self.goombas:
...             tags = self.canvas.gettags(g)
...             x, y = self.canvas.coords(g)
...             dir_right = "dir_right" in tags
...             dx = 1.5 if dir_right else -1.5
...             self.canvas.move(g, dx, 0)
... 
...             # Check for platform underneath
...             gx1, gy1 = self.canvas.coords(g)
...             below = self.canvas.find_overlapping(gx1 + 16, gy1 + 33, gx1 + 16, gy1 + 34)
...             on_platform = any(obj in self.platforms or obj == self.ground for obj in below)
...             if not on_platform:
...                 new_dir = "dir_left" if dir_right else "dir_right"
...                 self.canvas.itemconfig(g, tags=(new_dir,))
... 
...     def update(self):
...         self.move_player()
...         self.move_goombas()
...         self.root.after(20, self.update)
... 
... # Main execution
... if __name__ == "__main__":
...     try:
...         from PIL import Image, ImageTk
...     except ImportError:
...         print("Please install Pillow: pip install pillow")
...         exit()
... 
...     if not all(os.path.exists(f) for f in [
...         "mario_right.png", "mario_left.png",
...         "luigi_right.png", "luigi_left.png",
...         "goomba.png"
...     ]):
...         print("Please make sure all required images are in the same folder:")
...         print("- mario_right.png, mario_left.png")
...         print("- luigi_right.png, luigi_left.png")
...         print("- goomba.png")
...         exit()
... 
    root = tk.Tk()
    root.title("Mario Platformer (Python + Tkinter)")
    game = Platformer(root)
    root.mainloop()
