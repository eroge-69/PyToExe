from turtle import *
t = Turtle()
t.color('blue')
t.shape('circle')
t.speed(0)
t.pensize(5)
def draw(x, y):
    t.goto(x, y)
def move(x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()
def green():
    t.color('green')
def red():
    t.color('red')
def blue():
    t.color('blue')
def Left():
    t.goto(t.xcor() - 5, t.ycor())
def Right():
    t.goto(t.xcor() + 5, t.ycor())
def Up():
    t.goto(t.xcor(), t.ycor() + 5)
def Down():
    t.goto(t.xcor(), t.ycor() - 5)
def begin():
    t.begin_fill()
def end():
    t.end_fill()
scr = t.getscreen()
scr.listen()
scr.onkey(green, 'g')
scr.onkey(blue, 'b')
scr.onkey(red, 'r')
scr.onscreenclick(move)
t.ondrag(draw)
scr.onkey(Left, 'Left')
scr.onkey(Right, 'Right')
scr.onkey(Up, 'Up')
scr.onkey(Down, 'Down')
scr.onkey(begin, 's')
scr.onkey(end, 'e')