"""Snake game using turtle library."""
import turtle
import random
import asyncio
import time

def snake_up():
    global direction
    direction = north
def snake_down():
    global direction
    direction = south
def snake_left():
    global direction
    direction = west
def snake_right():
    global direction
    direction = east
image = "textures/backgroundv2.gif"
wn = turtle.Screen()

egg = turtle.Turtle()
wn.addshape(image)
turtle.shape(image)
dim = 770
half = dim / 2
wn.setup(dim, dim)
egg.shape("square")
egg.color("green")
egg.speed("fastest")
egg.turtlesize(2, 2)
egg.penup()

snake = []
length = 5
move = 40
east, south, west, north = 0, 270, 180, 90
direction = east
for body in range(length):
    snake.append(egg.clone())
    snake[body].forward(move * body)
egg.goto((random.randint(-9, 9) * 40), (random.randint(-9, 9) * 40))
egg.turtlesize(1.5)
egg.shape("circle")
egg.color("red")
wn.onkeypress(snake_up, "w")
wn.onkeypress(snake_down, "s")
wn.onkeypress(snake_left, "a")
wn.onkeypress(snake_right, "d")
wn.listen()

def reloadfunc(snek):
    posy = ((random.randint(-9, 9) * 40), (random.randint(-9, 9) * 40))
    snekpos = []
    for i in range(len(snake)):
        snekpos.append(snek[i].position())
    if posy not in snek:
        return posy
    else:
        reloadfunc(snek)

async def calculate(snek, eg):
    if snek[-1].distance(eg) < move - 5:
        position = ((random.randint(-9, 9) * 40), (random.randint(-9, 9) * 40))
        position = snek[-1].pos()
        print(position)
        snekpos = []
        for i in range(len(snake)):
            snekpos.append(snek[i].position())
        if position not in snekpos:
            eg.goto(position)
        else:
            eg.goto(reloadfunc(snek))
        return ["e", eg]
    else:
        snek[0].hideturtle()
        snek.pop(0)
        return ["s", snek]
def moves(snek):
    snek.append(snake[-1].clone())
    snek[-1].setheading(direction)
    snek[-1].forward(move)
frame = 0
while True:
    time.sleep(0.001)
    frame += 1
    frameIs = frame / 5
    if str(frameIs)[-1] == '0':
        moves(snake)
        same = 0
        if __name__ == "__main__":
            listThing = asyncio.run(calculate(snake, egg))
        if listThing[0] == "e":
            egg = listThing[1]
        else:
            snake = listThing[1]
        for body in snake:
            if snake[-1].distance(body) < 10:
                same += 1
        if same > 1:
            break
        if snake[-1].xcor() > half:
            snake[-1].setx(-360)
            listThing = asyncio.run(calculate(snake, egg))
        if snake[-1].xcor() < -half:
            snake[-1].setx(360)
            listThing = asyncio.run(calculate(snake, egg))
        if snake[-1].ycor() > half:
            snake[-1].sety(-360)
            listThing = asyncio.run(calculate(snake, egg))
        if snake[-1].ycor() < -half:
            snake[-1].sety(360)
            listThing = asyncio.run(calculate(snake, egg))


wn.exitonclick()