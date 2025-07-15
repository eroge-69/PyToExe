Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import turtle
import random
import time

# Set up the screen
screen = turtle.Screen()
screen.title("Dodge the Raindrops!")
screen.bgcolor("lightgreen")
screen.setup(width=600, height=600)
screen.tracer(0)  # Stops automatic screen updates

# Player (turtle)
player = turtle.Turtle()
player.shape("turtle")
player.color("green")
player.penup()
player.goto(0, -250)
player.speed(0)

# Raindrop
raindrop = turtle.Turtle()
raindrop.shape("circle")
raindrop.color("blue")
raindrop.penup()
raindrop.goto(random.randint(-280, 280), 250)
raindrop.speed(0)

# Score display
score = 0
score_writer = turtle.Turtle()
score_writer.hideturtle()
score_writer.penup()
score_writer.goto(0, 260)
score_writer.write(f"Score: {score}", align="center", font=("Arial", 16, "bold"))

# Move player left and right
def move_left():
...     x = player.xcor()
...     if x > -280:
...         player.setx(x - 20)
... 
... def move_right():
...     x = player.xcor()
...     if x < 280:
...         player.setx(x + 20)
... 
... # Keyboard controls
... screen.listen()
... screen.onkeypress(move_left, "Left")
... screen.onkeypress(move_right, "Right")
... 
... # Main game loop
... start_time = time.time()
... while True:
...     screen.update()  # Refresh the screen
...     y = raindrop.ycor()
...     raindrop.sety(y - 10)  # Raindrop falls
... 
...     # Update score based on time survived
...     score = int(time.time() - start_time)
...     score_writer.clear()
...     score_writer.write(f"Score: {score}", align="center", font=("Arial", 16, "bold"))
... 
...     # Check for collision
...     if raindrop.distance(player) < 20:
...         score_writer.clear()
...         score_writer.goto(0, 0)
...         score_writer.write(f"Game Over! Score: {score}", align="center", font=("Arial", 24, "bold"))
...         break
... 
...     # Reset raindrop if it falls off screen
...     if raindrop.ycor() < -280:
...         raindrop.goto(random.randint(-280, 280), 250)
... 
