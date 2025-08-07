
import turtle
import time

screen = turtle.Screen()
screen.bgcolor("black")
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(3)

def draw_rectangle(t, width, height, color):
    t.color("white", color)
    t.begin_fill()
    for _ in range(2):
        t.forward(width)
        t.left(90)
        t.forward(height)
        t.left(90)
    t.end_fill()

def draw_cake():
    pen.up()
    pen.goto(-75, -100)
    pen.down()
    draw_rectangle(pen, 150, 30, "pink")  # Bottom layer

    pen.up()
    pen.goto(-60, -70)
    pen.down()
    draw_rectangle(pen, 120, 30, "lightblue")  # Middle layer

    pen.up()
    pen.goto(-45, -40)
    pen.down()
    draw_rectangle(pen, 90, 30, "lightgreen")  # Top layer

def draw_candle():
    pen.up()
    pen.goto(-5, -10)
    pen.down()
    draw_rectangle(pen, 10, 40, "white")  # Candle

    # Flame
    pen.up()
    pen.goto(0, 35)
    pen.down()
    pen.color("orange")
    pen.begin_fill()
    pen.circle(5)
    pen.end_fill()

def show_message():
    pen.up()
    pen.goto(-120, 100)
    pen.color("magenta")
    pen.write("I love you Girish <3", font=("Comic Sans MS", 18, "bold"))

# Animation
draw_cake()
time.sleep(0.5)
draw_candle()
time.sleep(0.5)
show_message()

# Keep the window open
turtle.done()
