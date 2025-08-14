import tkinter as tk
from PIL import Image, ImageTk
import os
import glob
import random
import math
import sys

# -------- CONFIG --------
NUM_BATCH = 6
SPEED_MIN, SPEED_MAX = 2, 6
SCALE_MIN, SCALE_MAX = 0.2, 0.5
ROTATE_SPEED_MAX = 3
UPDATE_DELAY = 20  # ms
MOUSE_REPULSION = 60  # pixels
BATCH_INTERVAL = 8000  # ms
# ----------------------

# -------- DETERMINE IMAGE FOLDER --------
if getattr(sys, 'frozen', False):
    # Running as .exe
    IMAGE_FOLDER = os.path.dirname(sys.executable)
else:
    # Running as script (.py)
    IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__))

# -------- MOVING IMAGE CLASS --------
class MovingImage:
    def __init__(self, canvas, image_path):
        self.canvas = canvas
        self.orig_img = Image.open(image_path).convert("RGBA")

        self.scale = random.uniform(SCALE_MIN, SCALE_MAX)
        self.dx = random.uniform(SPEED_MIN, SPEED_MAX) * random.choice([-1, 1])
        self.dy = random.uniform(SPEED_MIN, SPEED_MAX) * random.choice([-1, 1])
        self.rotate_speed = random.uniform(-ROTATE_SPEED_MAX, ROTATE_SPEED_MAX)
        self.angle = 0
        self.pattern = random.choice(["straight", "diagonal", "sin"])
        self.x = random.randint(0, canvas.winfo_screenwidth())
        self.y = random.randint(0, canvas.winfo_screenheight())
        self.update_image()
        self.id = canvas.create_image(self.x, self.y, image=self.tk_image, anchor='nw')

    def update_image(self):
        w, h = self.orig_img.size
        new_w = max(1, int(w * self.scale))
        new_h = max(1, int(h * self.scale))
        img = self.orig_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        img = img.rotate(self.angle, expand=True)
        self.tk_image = ImageTk.PhotoImage(img)

    def move(self, mouse_pos):
        sw, sh = self.canvas.winfo_screenwidth(), self.canvas.winfo_screenheight()
        mx, my = mouse_pos

        self.angle += self.rotate_speed
        self.update_image()
        self.canvas.itemconfig(self.id, image=self.tk_image)

        # Movement patterns
        if self.pattern == "straight":
            self.x += self.dx
            self.y += self.dy
        elif self.pattern == "diagonal":
            self.x += self.dx
            self.y += self.dx
        elif self.pattern == "sin":
            self.x += self.dx
            self.y += math.sin(self.x / 50) * 3

        # Bounce edges
        if self.x < 0 or self.x > sw - 50: self.dx *= -1
        if self.y < 0 or self.y > sh - 50: self.dy *= -1

        # Mouse repulsion
        dist_x, dist_y = self.x - mx, self.y - my
        distance = math.hypot(dist_x, dist_y)
        if distance < MOUSE_REPULSION and distance != 0:
            strength = (MOUSE_REPULSION - distance)/MOUSE_REPULSION * 4
            self.x += dist_x/distance * strength
            self.y += dist_y/distance * strength

        self.canvas.coords(self.id, self.x, self.y)

# -------- MAIN WINDOW --------
root = tk.Tk()
root.attributes("-topmost", True)
root.overrideredirect(True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.configure(bg="white")
root.attributes("-transparentcolor", "white")
root.bind("<Escape>", lambda e: root.destroy())

canvas = tk.Canvas(root, width=root.winfo_screenwidth(),
                   height=root.winfo_screenheight(),
                   highlightthickness=0, bg='white')
canvas.pack()

# -------- LOAD IMAGES --------
image_files = []
for ext in ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp'):
    image_files.extend(glob.glob(os.path.join(IMAGE_FOLDER, ext)))

if not image_files:
    raise ValueError("No images found in the folder!")

# -------- BATCH MANAGEMENT --------
batch_index = 0
current_images = []

def load_next_batch():
    global batch_index, current_images
    canvas.delete("all")
    random.shuffle(image_files)
    start = batch_index * NUM_BATCH
    end = start + NUM_BATCH
    batch = image_files[start:end]

    # Repeat images if not enough for batch
    while len(batch) < NUM_BATCH:
        batch += image_files[:NUM_BATCH - len(batch)]
    batch_index = (batch_index + 1) % (len(image_files) // NUM_BATCH + 1)

    current_images[:] = [MovingImage(canvas, img) for img in batch]

# -------- UPDATE LOOP --------
def update():
    mouse_pos = (root.winfo_pointerx(), root.winfo_pointery())
    for img in current_images:
        img.move(mouse_pos)
    root.after(UPDATE_DELAY, update)

# -------- BATCH CYCLE LOOP --------
def batch_cycle():
    load_next_batch()
    root.after(BATCH_INTERVAL, batch_cycle)

# -------- START --------
batch_cycle()
update()
root.mainloop()
