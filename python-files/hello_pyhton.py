import tkinter as tk
import random

# Game settings
WIDTH = 800
HEIGHT = 600
CAR_WIDTH = 50
CAR_HEIGHT = 90
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 90
CAR_SPEED = 20
ENEMY_SPEED = 10
FPS = 30

# Colors
WHITE = "#FFFFFF"
BLACK = "#000000"
RED = "#FF0000"
GREEN = "#00FF00"

# Set up the main window
root = tk.Tk()
root.title("Car Game")

# Set up the canvas
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=WHITE)
canvas.pack()

# Player car
player_car = canvas.create_rectangle(WIDTH // 2 - CAR_WIDTH // 2, HEIGHT - CAR_HEIGHT - 10, 
                                     WIDTH // 2 + CAR_WIDTH // 2, HEIGHT - 10, fill=GREEN)

# List to hold enemies
enemies = []

# Score
score = 0
score_text = canvas.create_text(10, 10, anchor="nw", text=f"Score: {score}", font=("Arial", 20), fill=BLACK)

# Move the player's car
def move_car(event):
    x, y, _, _ = canvas.coords(player_car)
    if event.keysym == "Left" and x > 0:
        canvas.move(player_car, -CAR_SPEED, 0)
    elif event.keysym == "Right" and x < WIDTH - CAR_WIDTH:
        canvas.move(player_car, CAR_SPEED, 0)

# Generate a new enemy car
def create_enemy():
    x = random.randint(0, WIDTH - ENEMY_WIDTH)
    enemy = canvas.create_rectangle(x, -ENEMY_HEIGHT, x + ENEMY_WIDTH, 0, fill=RED)
    enemies.append(enemy)

# Move the enemies
def move_enemies():
    global score
    for enemy in enemies[:]:
        canvas.move(enemy, 0, ENEMY_SPEED)
        _, y1, _, y2 = canvas.coords(enemy)

        # Check if enemy goes off the screen or collides with player
        if y2 > HEIGHT:
            canvas.delete(enemy)
            enemies.remove(enemy)
            score += 1  # Increase score for passing an enemy

        # Check for collision with the player car
        player_coords = canvas.coords(player_car)
        enemy_coords = canvas.coords(enemy)
        if (player_coords[0] < enemy_coords[2] and player_coords[2] > enemy_coords[0] and
            player_coords[1] < enemy_coords[3] and player_coords[3] > enemy_coords[1]):
            game_over()
            return

    canvas.after(1000 // FPS, move_enemies)  # Call move_enemies again after a short delay

# Update score on screen
def update_score():
    canvas.itemconfig(score_text, text=f"Score: {score}")
    canvas.after(1000, update_score)  # Update score every second

# End the game
def game_over():
    canvas.create_text(WIDTH // 2, HEIGHT // 2, text="GAME OVER", font=("Arial", 40), fill=BLACK)
    canvas.after(2000, root.quit)  # Close the game after 2 seconds

# Start the game
def start_game():
    create_enemy()
    move_enemies()
    update_score()
    root.bind("<Left>", move_car)
    root.bind("<Right>", move_car)
    root.after(2000, start_game)  # Create new enemy every 2 seconds

# Run the game
start_game()
root.mainloop()
