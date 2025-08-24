import tkinter as tk
import random

class SnakeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Snake Game")
        self.master.resizable(False, False)

        self.canvas = tk.Canvas(master, width=640, height=640, bg="black")
        self.canvas.pack()

        self.snake = []
        self.food = None
        self.super_food = None # New attribute for super food
        self.super_food_timer = None # New attribute for super food timer
        self.direction = "Right"
        self.running = False
        
        self.score = 0
        self.score_display = self.canvas.create_text(50, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 16), anchor="nw")

        self.create_snake()
        self.create_food()

        self.master.bind("<KeyPress>", self.change_direction)
        # Remove automatic start_game call
        # self.start_game()
        self.start_button = tk.Button(master, text="Start Game", command=self.start_game)
        self.start_button.pack()

    def reset_game(self):
        self.running = False
        if self.food: self.canvas.delete(self.food)
        if self.super_food: self.canvas.delete(self.super_food)
        if self.super_food_timer: self.master.after_cancel(self.super_food_timer)
        for segment in self.snake: self.canvas.delete(segment)
        self.snake = []
        self.direction = "Right"
        self.score = 0
        self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
        self.canvas.delete("game_over_text") # Tag for game over text
        self.create_snake()
        self.create_food()

    def create_snake(self):
        # Initial snake: 3 segments
        self.snake = []
        for i in range(3):
            x = 100 - i * 20
            y = 100
            segment = self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="green")
            self.snake.append(segment)

    def create_food(self):
        while True:
            x = random.randint(0, 640 // 20 - 1) * 20
            y = random.randint(0, 640 // 20 - 1) * 20
            # Ensure food does not spawn on the snake
            if not any(self.check_collision(x, y, self.canvas.coords(segment)) for segment in self.snake):
                break
        self.food = self.canvas.create_oval(x, y, x + 20, y + 20, fill="red")

    def create_super_food(self):
        if self.super_food:  # If super food already exists, don't create another
            return
        while True:
            x = random.randint(0, 640 // 20 - 1) * 20
            y = random.randint(0, 640 // 20 - 1) * 20
            # Ensure super food does not spawn on the snake or regular food
            snake_collision = any(self.check_collision(x, y, self.canvas.coords(segment)) for segment in self.snake)
            food_coords = self.canvas.coords(self.food) if self.food else []
            food_collision = self.check_collision(x, y, food_coords) if food_coords else False

            if not snake_collision and not food_collision:
                break
        self.super_food = self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="blue")
        self.super_food_timer = self.master.after(5000, self.remove_super_food) # 5 seconds

    def remove_super_food(self):
        if self.super_food:
            self.canvas.delete(self.super_food)
            self.super_food = None
        if self.super_food_timer:
            self.master.after_cancel(self.super_food_timer)
            self.super_food_timer = None

    def move_snake(self):
        if not self.running: return

        head_x1, head_y1, head_x2, head_y2 = self.canvas.coords(self.snake[0])
        
        if self.direction == "Right":
            new_head_x1 = head_x1 + 20
            new_head_y1 = head_y1
        elif self.direction == "Left":
            new_head_x1 = head_x1 - 20
            new_head_y1 = head_y1
        elif self.direction == "Up":
            new_head_x1 = head_x1
            new_head_y1 = head_y1 - 20
        elif self.direction == "Down":
            new_head_x1 = head_x1
            new_head_y1 = head_y1 + 20

        # Game over conditions (modified for wrap-around)
        if new_head_x1 < 0:
            new_head_x1 = 640 - 20 # Wrap to right
        elif new_head_x1 >= 640:
            new_head_x1 = 0 # Wrap to left (changed from new_head_x2 > 640)
        if new_head_y1 < 0:
            new_head_y1 = 640 - 20 # Wrap to bottom
        elif new_head_y1 >= 640:
            new_head_y1 = 0 # Wrap to top (changed from new_head_y2 > 640)

        new_head_x2 = new_head_x1 + 20
        new_head_y2 = new_head_y1 + 20
        
        # Check for collision with itself
        if any(self.check_collision(new_head_x1, new_head_y1, self.canvas.coords(segment)) for segment in self.snake[1:]):
            self.game_over()
            return

        # Add new head
        new_head = self.canvas.create_rectangle(new_head_x1, new_head_y1, new_head_x2, new_head_y2, fill="green")
        self.snake.insert(0, new_head)

        # Check for food collision
        if self.check_collision(new_head_x1, new_head_y1, self.canvas.coords(self.food)):
            self.score += 10
            self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
            self.canvas.delete(self.food)
            self.create_food()
            if self.score % 50 == 0: # Create super food every 50 points
                self.create_super_food()
        elif self.super_food and self.check_collision(new_head_x1, new_head_y1, self.canvas.coords(self.super_food)):
            self.score += 30
            self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
            self.remove_super_food() # This will delete the super_food and cancel its timer
        else:
            # Remove tail if no food eaten
            tail = self.snake.pop()
            self.canvas.delete(tail)

        self.master.after(100, self.move_snake)

    def change_direction(self, event):
        if event.keysym == "Up" and self.direction != "Down":
            self.direction = "Up"
        elif event.keysym == "Down" and self.direction != "Up":
            self.direction = "Down"
        elif event.keysym == "Left" and self.direction != "Right":
            self.direction = "Left"
        elif event.keysym == "Right" and self.direction != "Left":
            self.direction = "Right"
            
    def check_collision(self, x1, y1, coords):
        fx1, fy1, fx2, fy2 = coords
        return x1 < fx2 and x1 + 20 > fx1 and y1 < fy2 and y1 + 20 > fy1

    def game_over(self):
        self.running = False
        self.canvas.create_text(640/2, 640/2, text="Game Over!", fill="white", font=("Arial", 40), tag="game_over_text")
        # Recreate the start_button for "Play Again"
        self.start_button = tk.Button(self.master, text="Play Again", command=self.restart_game)
        self.start_button.pack()

    def start_game(self):
        # Destroy the button when the game starts
        if self.start_button:
            self.start_button.destroy()
            self.start_button = None # Clear the reference
        self.running = True
        self.move_snake()

    def restart_game(self):
        self.reset_game()
        # The start_game function will now create a new button if self.start_button is None.
        # self.start_button is already None after reset_game which calls create_snake and create_food (which use canvas.coords(self.snake[0]))
        # and start_game destroys it. The button needs to be created again. So we just call start_game().
        # However, start_game should not destroy itself in this case.
        
        # Let's refactor: game_over creates the button, and start_game destroys it (if it exists) and starts the game.
        # restart_game should just call reset_game and then start_game (which will destroy the Play Again button).
        self.start_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
