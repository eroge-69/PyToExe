#НАСТРОЙКИ БАЗЫ
import turtle as dd
dd.fillcolor('pink')
dd.bgcolor('black')
dd.color('pink')
dd.pensize(4)
dd.speed(100)

#СЕРДЦЕ
dd.penup()
dd.setpos(0 , -20)
dd.pendown()
def heart(x, y, z, d):
    dd.left(x)
    dd.forward(y)
    for i in range(21):
        dd.forward(z)
        dd.left(d)
dd.begin_fill()
heart(60, 180, 10, 10)
dd.end_fill()
dd.penup()
dd.setpos(0, -20)
dd.pendown()
dd.begin_fill()
heart(38, -180, -10 , -10)
dd.end_fill()
dd.speed(10)

# БУКВА С
dd.penup()
dd.goto(-360, -260)
dd.pendown()
dd.color('white')
dd.setheading(90)
dd.forward(150)
dd.right(90)
dd.forward(100)
dd.penup()
dd.goto(-360, -260)
dd.pendown()
dd.setheading(0)
dd.forward(100)

# БУКВА О
dd.penup()
dd.forward(50)
dd.pendown()
for i in range(4):
    dd.forward(150)
    dd.left(90)

# БУКВА С2
dd.penup()
dd.goto(0, -260)
dd.pendown()
dd.color('white')
dd.setheading(90)
dd.forward(150)
dd.right(90)
dd.forward(100)
dd.penup()
dd.goto(0, -260)
dd.pendown()
dd.setheading(0)
dd.forward(100)

#Буква И
dd.setheading(0)
dd.penup()
dd.forward(50)
dd.pendown()
dd.left(90)
dd.forward(150)
dd.back(150)
dd.right(45)
dd.forward(210)
dd.right(135)
dd.forward(150)

dd.done()





