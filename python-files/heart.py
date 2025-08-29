import math
import turtle
import random

    

def xt(t):
    return 16 * math.sin(t) ** 3

def yt(t):
    return 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)

text = turtle.Turtle()
textq = turtle.Turtle()

t = turtle.Turtle()
t.speed(9999999999999999999999999999999)
turtle.colormode(255)
turtle.Screen() .bgcolor(0, 0, 0)
for i in range(64):
    t.goto((xt(i) * 20, yt(i) * 20))
    t.pencolor(255, 0, 0)
    t.goto(0, 0)


#t.begin_fill()
#for i in range(360):
#    angle = math.radians(i)
#    t.goto(xt(angle) * 20, yt(angle) * 20)
#t.end_fill()

shadow = turtle.Turtle()
shadow.speed(999)
shadow.hideturtle()
shadow.penup()
shadow.goto(0, 100)  # смещение тени
shadow.pencolor(200, 200, 200)
shadow.pendown()
for i in range(360):
    angle = math.radians(i)
    shadow.goto(xt(angle) * 20, yt(angle) * 20)

z = random.randint(1, 3)
q = random.randint(1, 10)
text.penup()
text.goto(0, -400)
if z == 1:
    text.color(255, 0, 0)
elif z == 2:
    text.color(255, 255, 255)
elif z == 3:
    text.color(0, 255, 0)

if q == 1:
    text.write("Ты самая лучшая", align="center", font=("Segoe Script", 24, "bold"))
elif q == 2:
    text.write("Ты мое счастье", align="center", font=("Segoe Script", 24, "bold"))
elif q == 3:
    text.write("Спасибо что ты есть", align="center", font=("Segoe Script", 24, "bold"))
elif q == 4:
    text.write("Ты мой самый дорогой человек", align="center", font=("Segoe Script", 24, "bold"))
elif q == 5:
    text.write("Мне так повезло с тобой", align="center", font=("Segoe Script", 24, "bold"))
elif q == 6:
    text.write("Я тебя люблю", align="center", font=("Segoe Script", 24, "bold"))
elif q == 7:
    text.write("Я тебя люблю", align="center", font=("Segoe Script", 24, "bold"))
elif q == 8:
    text.write("Я тебя люблю", align="center", font=("Segoe Script", 24, "bold"))
elif q == 9:
    text.write("Я тебя люблю", align="center", font=("Segoe Script", 24, "bold"))
elif q == 10:
    text.write("Я тебя люблю", align="center", font=("Segoe Script", 24, "bold"))

text.hideturtle()

textq.penup()
textq.goto(0, 250)
textq.color(255, 255, 255)
textq.write("Я тебя люблю", align="center", font=("Segoe Script", 24, "bold"))
textq.hideturtle()

t.hideturtle()
turtle.update()
turtle.mainloop()