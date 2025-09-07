o = 0
i = 0
d = "-"
print loading...
import pyautogui
import turtle
import random
turtle.Turtle
turtle.right(50)
turtle.forward(10)
turtle.forward(10)
turtle.forward(10)
turtle.circle(20)
turtle.bgcolor("black")



for _ in range(10000000000000):
    turtle.pencolor("red")
    turtle.speed(10)
    turtle.goto(random.randint(-400, 400), random.randint(-400, 400) )
    asd = random.randint(0, 10)
    if asd == 10:
        i += 1
        print(i)
        turtle.clear()
        turtle.pencolor("yellow")
        turtle.circle(5)
        turtle.write("1")
        turtle.goto(0, 0)
    else:
        turtle.write(o)
        o += 1
        turtle.title(o)
        print(i)
        
