
import turtle
import random

# Screen setup
screen = turtle.Screen()
screen.title("Catch the Falling Star")
screen.bgcolor("lightblue")
screen.setup(width=600, height=600)
screen.tracer(0)

# Basket (player)
basket = turtle.Turtle()
basket.shape("square")
basket.color("brown")
basket.shapesize(stretch_wid=1, stretch_len=5)
basket.penup()
basket.goto(0, -250)

# Star (falling object)
star = turtle.Turtle()
star.shape("circle")
star.color("yellow")
star.penup()
star.goto(random.randint(-280, 280), 250)
star.speed(0)

# Score display
score = 0
score_writer = turtle.Turtle()
score_writer.hideturtle()
score_writer.penup()
score_writer.goto(0, 260)
score_writer.write(f"Score: {score}", align="center", font=("Arial", 16, "bold"))

# Basket movement
def move_left():
    x = basket.xcor()
    if x > -250:
        basket.setx(x - 20)

def move_right():
    x = basket.xcor()
    if x < 250:
        basket.setx(x + 20)

screen.listen()
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")

# Main game loop
fall_speed = 5
misses = 0

while True:
    screen.update()
    y = star.ycor()
    star.sety(y - fall_speed)

    # Check for catch
    if star.distance(basket) < 50 and star.ycor() < -220:
        score += 1
        score_writer.clear()
        score_writer.write(f"Score: {score}", align="center", font=("Arial", 16, "bold"))
        star.goto(random.randint(-280, 280), 250)

    # Check if missed
    if star.ycor() < -280:
        misses += 1
        star.goto(random.randint(-280, 280), 250)

    # End game if too many misses
    if misses >= 5:
        score_writer.clear()
        score_writer.goto(0, 0)
        score_writer.write("Game Over", align="center", font=("Arial", 24, "bold"))
        break
