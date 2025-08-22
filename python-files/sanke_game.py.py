import tkinter as tk
import random
import os
from tkinter import simpledialog

# ==============================
# Game Settings
# ==============================
WIDTH = 600
HEIGHT = 400
SQUARE_SIZE = 20
DELAY = 150  # starting speed (ms)
LEVEL_UP_SPEED = 15
MAX_LEVEL = 10
UPDATE_CODE = "Abdu2011"

# Track this file's last modification time
GAME_FILE = __file__
STAMP_FILE = "last_update.stamp"

if not os.path.exists(STAMP_FILE):
    with open(STAMP_FILE, "w") as f:
        f.write(str(os.path.getmtime(GAME_FILE)))

with open(STAMP_FILE, "r") as f:
    last_update = float(f.read().strip())


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="blue")
        self.canvas.pack()

        self.running = False
        self.level = 1
        self.score = 0
        self.delay = DELAY
        self.snake = []
        self.food = None
        self.food_eaten = 0
        self.direction = "Right"
        self.update_required = False

        # Buttons
        self.update_button = tk.Button(root, text="Update", font=("Arial", 20),
                                       command=self.show_update_prompt)
        self.restart_button = tk.Button(root, text="Restart", font=("Arial", 20),
                                        command=self.start_game)

        # Check update before showing anything
        self.check_update_on_start()

        # Bind keys
        root.bind("<Key>", self.key_press)

    # ========= UPDATE CHECK =========
    def check_update_on_start(self):
        global last_update
        current = os.path.getmtime(GAME_FILE)
        if current != last_update:
            self.update_required = True
            self.show_update_message()
        else:
            self.show_controls()

    def show_update_message(self):
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 40,
                                text="⚠️ Update Required!", fill="yellow", font=("Arial", 20))
        self.canvas.create_text(WIDTH/2, HEIGHT/2,
                                text="Enter update code = Abdu2011", fill="white", font=("Arial", 20))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 40,
                                text="Click Update button below", fill="white", font=("Arial", 20))
        self.update_button.pack(pady=10)

    def show_update_prompt(self):
        if self.update_required:
            code = simpledialog.askstring("Update", "Enter update code:")
            if code == UPDATE_CODE:
                self.update_button.pack_forget()
                self.update_required = False
                # save new stamp
                with open(STAMP_FILE, "w") as f:
                    f.write(str(os.path.getmtime(GAME_FILE)))
                self.show_controls()
            else:
                self.canvas.create_text(WIDTH/2, HEIGHT/2 + 80,
                                        text="❌ Wrong Code!", fill="red", font=("Arial", 20))

    # ========= GAME =========
    def show_controls(self):
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 60,
                                text="Snake Game Controls", fill="white", font=("Arial", 20))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 20,
                                text="Arrow Keys - Move", fill="white", font=("Arial", 20))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 20,
                                text="S - Stop | R - Resume | Q - Quit", fill="white", font=("Arial", 20))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 60,
                                text="Press ENTER to start...", fill="yellow", font=("Arial", 20))
        self.root.bind("<Return>", lambda e: self.start_game())

    def start_game(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.running = True
        self.level = 1
        self.score = 0
        self.delay = DELAY
        self.food_eaten = 0
        self.spawn_food()
        self.update_game()

    def spawn_food(self):
        x = random.randrange(0, WIDTH, SQUARE_SIZE)
        y = random.randrange(0, HEIGHT, SQUARE_SIZE)
        self.food = (x, y)

    def draw_grid(self):
        # Draw grid lines
        for x in range(0, WIDTH, SQUARE_SIZE):
            self.canvas.create_line(x, 0, x, HEIGHT, fill="lightblue")
        for y in range(0, HEIGHT, SQUARE_SIZE):
            self.canvas.create_line(0, y, WIDTH, y, fill="lightblue")

    def draw_snake_food(self):
        self.canvas.delete("all")
        # Draw grid
        self.draw_grid()
        # Draw snake
        for x, y in self.snake:
            self.canvas.create_rectangle(x, y, x+SQUARE_SIZE, y+SQUARE_SIZE, fill="green")
        # Draw food
        if self.food:
            fx, fy = self.food
            self.canvas.create_rectangle(fx, fy, fx+SQUARE_SIZE, fy+SQUARE_SIZE, fill="red")
        # Draw score and level in yellow
        self.canvas.create_text(80, 20, text=f"Score: {self.score}", fill="yellow", font=("Arial", 20))
        self.canvas.create_text(500, 20, text=f"Level: {self.level}", fill="yellow", font=("Arial", 20))

    def update_game(self):
        if not self.running:
            return

        head_x, head_y = self.snake[0]
        if self.direction == "Left":
            head_x -= SQUARE_SIZE
        elif self.direction == "Right":
            head_x += SQUARE_SIZE
        elif self.direction == "Up":
            head_y -= SQUARE_SIZE
        elif self.direction == "Down":
            head_y += SQUARE_SIZE

        new_head = (head_x, head_y)

        if (head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT or new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food_eaten += 1
            self.spawn_food()
            if self.food_eaten % 2 == 0:
                self.level += 1
                self.delay = max(50, self.delay - LEVEL_UP_SPEED)
                if self.level > MAX_LEVEL:
                    self.game_over(True)
                    return
        else:
            self.snake.pop()

        self.draw_snake_food()
        self.root.after(self.delay, self.update_game)

    def key_press(self, event):
        if event.keysym in ["Left", "Right", "Up", "Down"]:
            if (event.keysym == "Left" and self.direction != "Right") or \
               (event.keysym == "Right" and self.direction != "Left") or \
               (event.keysym == "Up" and self.direction != "Down") or \
               (event.keysym == "Down" and self.direction != "Up"):
                self.direction = event.keysym
        elif event.keysym.lower() == "s":
            self.running = False
        elif event.keysym.lower() == "r":
            if not self.running:
                self.running = True
                self.update_game()
        elif event.keysym.lower() == "q" or event.keysym == "Escape":
            self.root.destroy()

    def game_over(self, max_level=False):
        self.running = False
        self.canvas.delete("all")
        if max_level:
            msg = "🎉 You reached Level 10! Game Over!"
        else:
            msg = "💀 Game Over!"
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 20, text=msg, fill="red", font=("Arial", 20))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 20, text="Press ENTER to Restart", fill="white", font=("Arial", 20))
        self.root.bind("<Return>", lambda e: self.start_game())


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
