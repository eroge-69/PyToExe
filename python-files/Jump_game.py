import turtle
import random
import time

# --- Screen Setup ---
screen = turtle.Screen()
screen.setup(width=800, height=400) # Adjusted height for a simpler ground game
screen.bgcolor("#87CEEB") # Sky blue background
screen.title("Jump Over Obstacles!")
screen.tracer(0) # Turn off screen updates for smoother animations

# --- Game Constants ---
GROUND_LEVEL = -150
PLAYER_START_X = -250
OBSTACLE_START_X = 350
PLAYER_SIZE = 20 # Width/Height of the player square
OBSTACLE_SIZE = 20 # Width/Height of the obstacle square
JUMP_FORCE = 20 # How high the player jumps initially
GRAVITY = 2 # How fast the player falls
INITIAL_OBSTACLE_SPEED = 8 # Initial speed of obstacles moving left
SPEED_INCREMENT = 0.5 # How much speed increases
SCORE_FOR_SPEED_INCREASE = 5 # Score points after which speed increases

# --- Game Variables ---
game_running = True
score = 0
obstacle_speed = INITIAL_OBSTACLE_SPEED
vertical_velocity = 0 # Current vertical speed of the player during a jump
jump_state = "ground" # Can be "ground", "up", "down"

# --- Player Turtle ---
player = turtle.Turtle()
player.speed(0)
player.shape("square")
player.shapesize(stretch_wid=PLAYER_SIZE/20, stretch_len=PLAYER_SIZE/20)
player.color("darkblue") # Slightly darker blue for player
player.penup()
player.goto(PLAYER_START_X, GROUND_LEVEL)

# --- Obstacle Turtle ---
obstacle = turtle.Turtle()
obstacle.speed(0)
obstacle.shape("square")
obstacle.shapesize(stretch_wid=OBSTACLE_SIZE/20, stretch_len=OBSTACLE_SIZE/20)
obstacle.color("darkgreen") # Slightly darker green for obstacle
obstacle.penup()
obstacle.goto(OBSTACLE_START_X, GROUND_LEVEL)

# --- Score Display Turtle ---
score_display = turtle.Turtle()
score_display.speed(0)
score_display.hideturtle()
score_display.penup()
score_display.goto(0, 150)
score_display.color("black")
score_display.write("Score: 0", align="center", font=("Arial", 24, "normal"))

# --- Game Over Display Turtle ---
game_over_display = turtle.Turtle()
game_over_display.speed(0)
game_over_display.hideturtle()
game_over_display.penup()
game_over_display.goto(0, 0)
game_over_display.color("red")

# --- Decorative Elements ---
# Ground
ground = turtle.Turtle()
ground.speed(0)
ground.hideturtle()
ground.penup()
ground.goto(-400, GROUND_LEVEL - 50) # Position below the player's ground level
ground.pendown()
ground.fillcolor("#8B4513") # Brown color for ground
ground.begin_fill()
for _ in range(2):
    ground.forward(800)
    ground.left(90)
    ground.forward(100) # Height of the ground
    ground.left(90)
ground.end_fill()
ground.penup()

# Sun
sun = turtle.Turtle()
sun.speed(0)
sun.hideturtle()
sun.penup()
sun.goto(300, 150)
sun.dot(50, "yellow") # Yellow circle for the sun

# Clouds (multiple simple cloud shapes)
clouds = []
for _ in range(3): # Create 3 clouds
    cloud = turtle.Turtle()
    cloud.speed(0)
    cloud.hideturtle()
    cloud.penup()
    cloud.color("white")
    cloud.goto(random.randint(-350, 350), random.randint(50, 100))
    # Draw a simple cloud shape
    cloud.begin_fill()
    cloud.circle(20)
    cloud.forward(20)
    cloud.circle(20)
    cloud.forward(20)
    cloud.circle(20)
    cloud.end_fill()
    clouds.append(cloud)

# --- Functions ---
def jump():
    """Initiates a jump if the player is currently on the ground."""
    global jump_state, vertical_velocity
    if game_running and jump_state == "ground": # Only allow jump if game is running
        vertical_velocity = JUMP_FORCE
        jump_state = "up"

def update_score_display_text():
    """Updates the score display on the screen."""
    score_display.clear()
    score_display.write(f"Score: {score}", align="center", font=("Arial", 24, "normal"))

def end_game():
    """Ends the game, displays the game over message, and stops game actions."""
    global game_running
    game_running = False
    screen.onkey(None, "space") # Disable jump key
    player.hideturtle()
    obstacle.hideturtle()
    game_over_display.write(f"GAME OVER!\nFinal Score: {score}", align="center", font=("Arial", 36, "bold"))
    screen.update()

def game_loop():
    """The main animation and game logic loop."""
    global score, obstacle_speed, vertical_velocity, jump_state, game_running

    if not game_running:
        return # Stop the loop if the game is over

    # --- Player Jump Logic ---
    if jump_state == "up" or jump_state == "down":
        player.sety(player.ycor() + vertical_velocity)
        vertical_velocity -= GRAVITY # Apply gravity

        # Transition from ascending to descending
        if vertical_velocity <= 0 and jump_state == "up":
            jump_state = "down"
        
        # Check if player lands back on the ground
        if player.ycor() <= GROUND_LEVEL:
            player.sety(GROUND_LEVEL) # Snap to ground level
            jump_state = "ground"
            vertical_velocity = 0 # Stop vertical movement

    # --- Obstacle Movement ---
    obstacle.setx(obstacle.xcor() - obstacle_speed)

    # Reset obstacle if it moves off-screen to the left
    if obstacle.xcor() < -OBSTACLE_START_X:
        obstacle.setx(OBSTACLE_START_X) # Move obstacle back to the right
        score += 1 # Increment score for successfully passing an obstacle
        update_score_display_text()

        # Increase game speed based on score
        if score > 0 and score % SCORE_FOR_SPEED_INCREASE == 0:
            obstacle_speed += SPEED_INCREMENT
            # print(f"Speed increased to: {obstacle_speed:.1f}") # For debugging

    # --- Collision Detection ---
    # Check if the player and obstacle bounding boxes overlap
    player_left = player.xcor() - PLAYER_SIZE / 2
    player_right = player.xcor() + PLAYER_SIZE / 2
    player_bottom = player.ycor() - PLAYER_SIZE / 2
    player_top = player.ycor() + PLAYER_SIZE / 2

    obstacle_left = obstacle.xcor() - OBSTACLE_SIZE / 2
    obstacle_right = obstacle.xcor() + OBSTACLE_SIZE / 2
    obstacle_bottom = obstacle.ycor() - OBSTACLE_SIZE / 2
    obstacle_top = obstacle.ycor() + OBSTACLE_SIZE / 2

    # Check for X-axis overlap
    x_overlap = not (player_right < obstacle_left or player_left > obstacle_right)
    # Check for Y-axis overlap
    y_overlap = not (player_top < obstacle_bottom or player_bottom > obstacle_top)

    if x_overlap and y_overlap:
        end_game()
        return

    screen.update() # Update the screen to show changes
    # Schedule the next frame of the game loop
    screen.ontimer(game_loop, 20) # Run game_loop every 20 milliseconds (approx. 50 FPS)

# --- Keyboard Bindings ---
screen.listen() # Listen for keyboard input
screen.onkey(jump, "space") # Bind the spacebar to the jump function

# --- Start Game ---
update_score_display_text() # Initialize score display
game_loop() # Start the main game loop

screen.mainloop() # Keep the Turtle graphics window open
