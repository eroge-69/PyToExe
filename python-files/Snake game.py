import tkinter as tk
import random

# Constants
WIDTH = 1200
HEIGHT = 800
BLOCK_SIZE = 40
UPDATE_DELAY = 150  # ms

directions = {
    "Left": (-1, 0),
    "Right": (1, 0),
    "Up": (0, -1),
    "Down": (0, 1),
}

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="light green")
        self.canvas.pack()

        self.root.bind("<KeyPress>", self.handle_keypress)

        self.score = 0
        self.running = True
        self.game_over_displayed = False

        self.reset_game()
        self.update()

    def reset_game(self):
        self.snake = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = "Right"
        self.food = self.spawn_food()
        self.score = 0
        self.running = True
        self.game_over_displayed = False
        self.canvas.delete("all")

    def spawn_food(self):
        while True:
            x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            if (x, y) not in self.snake:
                return (x, y)

    def handle_keypress(self, event):
        key = event.keysym
        if key in directions:
            new_dir = key
            if (directions[new_dir][0] + directions[self.direction][0] != 0 or
                directions[new_dir][1] + directions[self.direction][1] != 0):
                self.direction = new_dir
        elif key.lower() == "r":
            if not self.running:
                self.reset_game()
                self.update()

    def move_snake(self):
        head_x, head_y = self.snake[-1]
        dx, dy = directions[self.direction]
        new_head = (head_x + dx * BLOCK_SIZE, head_y + dy * BLOCK_SIZE)

        if (
            new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT
        ):
            self.running = False
            return

        self.snake.append(new_head)

        if new_head == self.food:
            self.food = self.spawn_food()
            self.score += 1
        else:
            self.snake.pop(0)

    def update(self):
        if self.running:
            self.move_snake()
            self.draw()
            self.root.after(UPDATE_DELAY, self.update)
        else:
            if not self.game_over_displayed:
                self.canvas.create_text(WIDTH // 2, HEIGHT // 2, fill="red",
                                        font="Arial 30 bold", text="Game Over")
                self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 40, fill="white",
                                        font="Arial 16", text="Press 'R' to Restart")
                self.game_over_displayed = True

    def draw(self):
        self.canvas.delete("all")

        # Draw food
        fx, fy = self.food
        self.canvas.create_rectangle(fx, fy, fx + BLOCK_SIZE, fy + BLOCK_SIZE, fill="red")

        # Draw snake
        for x, y in self.snake:
            self.canvas.create_rectangle(x, y, x + BLOCK_SIZE, y + BLOCK_SIZE, fill="green")

        # Draw score (top-left corner)
        self.canvas.create_text(10, 10, anchor="nw", fill="white",
                                font="Arial 14 bold", text=f"Score: {self.score}")

# Run the game
root = tk.Tk()
root.title("Kirill snakes-game")
game = SnakeGame(root)
root.mainloop()
