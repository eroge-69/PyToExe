import turtle
import keyboard


t = turtle.Turtle()
turtle.title("my drawing software")
screen = turtle.Screen()
width, height = 1.0, 1.0
screen.setup(width=1.0, height=1.0)
t.speed(2)
t.color("black")
t.fillcolor("black")


def on_key_press():
    
    if keyboard.is_pressed("right"):
        t.right(2)
    if keyboard.is_pressed("left"):
        t.left(2)
    if keyboard.is_pressed("up"):
        t.forward(1)
    if keyboard.is_pressed("a"):
        t.up()
    if keyboard.is_pressed("d"):
        t.down()
    if keyboard.is_pressed("r"):
        t.clear()
        t.reset()
        t.speed(2)
    if keyboard.is_pressed("z"):
        t.setheading(0)
    elif keyboard.is_pressed("x"):
        t.setheading(90)
    elif keyboard.is_pressed("c"):
        t.setheading(180)
    elif keyboard.is_pressed("v"):
        t.setheading(270)
    if keyboard.is_pressed("q"):
        t.begin_fill()
    if keyboard.is_pressed("e"):
        t.end_fill()
    if keyboard.is_pressed("1"):
        t.pensize(1)
    if keyboard.is_pressed("2"):
        t.pensize(2)
    if keyboard.is_pressed("3"):
        t.pensize(3)
    if keyboard.is_pressed("5"):
        t.color("red")
        t.fillcolor("red")
    if keyboard.is_pressed("6"):
        t.color("blue")
        t.fillcolor("blue")
    if keyboard.is_pressed("7"):
        t.color("green")
        t.fillcolor("green")
    if keyboard.is_pressed("0"):
        t.color("black")
        t.fillcolor("black")
    
    
    
while True:
    on_key_press()
    if keyboard.is_pressed("esc"):
        turtle.bye()
turtle.done()