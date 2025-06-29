from turtle import *

t = Turtle()
scr = t.getscreen()
t.shape("circle")
t.pensize(5)
t.speed(0)
t.pendown()

def draw(x,y):
    t.goto(x,y)
    
def move(x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()

def begin():
    t.begin_fill()

def end_fill():
    t.end_fill()

def q():
    t.pensize(1)
def w():
    t.pensize(2)
def e():
    t.pensize(3)
def r():
    t.pensize(4)
def h():
    t.pensize(5)
def l():
    t.pensize(6)
def u():
    t.pensize(7)
def i():
    t.pensize(8)
def o():
    t.pensize(9)
def p():
    t.pensize(10)
def z():
    t.goto(t.xcor() + 5, t.ycor())
def c():
    t.goto(t.xcor() - 5, t.ycor())
def v():
    t.goto(t.xcor(), t.ycor() + 5)
def b():
    t.goto(t.xcor(), t.ycor() - 5)


scr.onkey(begin, "e")
scr.onkey(end_fill, "r")
scr.onkey(q, "1")
scr.onkey(w, "2")
scr.onkey(e, "3")
scr.onkey(r, "4")
scr.onkey(h, "5")
scr.onkey(l, "6")
scr.onkey(u, "7")
scr.onkey(i, "8")
scr.onkey(o, "9")
scr.onkey(p, "0")
scr.onkey(z, "Right")
scr.onkey(c, "Left")
scr.onkey(v, "Up")
scr.onkey(b, "Down")
    

scr.listen()
scr.onscreenclick(move)
t.ondrag(draw)


