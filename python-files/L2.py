import turtle as draw

#_______просто_многоугольник______
def Poly(num):
    if num > 500: num = 500
    for i in range(num):
        draw.forward(500//num)
        draw.right(360/num)
    draw.up()
    draw.done()

#_______узор_из_фигур______
def Polys(num):
    if (num > 35): num = 35
    draw.begin_fill()
    step = 0
    i = num
    while (i > 0):
        draw.down()
        draw.forward(60//num)
        step += 60//num
        for j in range(num):
            draw.forward(300//num)
            draw.right(360/num)
        draw.up()
        if (step >= 420//num):
            i -= 1
            step = 0
            draw.right(360/num)
    draw.end_fill()

#_______цветочек______
def Flower(num):
    if (num > 300): num = 300
    draw.begin_fill()
    for i in range(num):
        draw.circle(75)
        draw.up()
        draw.forward(300//num)
        draw.left(360/num)
        draw.down()
    draw.up()
    draw.end_fill()
    draw.done()
        

#_______main______
num = 0
while (num < 3):
    try:
        num = int(input("Введите количество углов фигуры/лепестков(большее 2): "))
    except ValueError:
        print("Введите правильно число")
        continue
    
figure = 0
while not(figure in [1,2,3]):
    try:
        figure = int(input("Выберите, какую фигуру нарисовать (1 - простой многоугольник, 2 - узор из многоугольников, 3 - цветок с n-лепестков: "))
    except ValueError:
        continue
        print("ошибка")

draw.up()
draw.goto(-100,100)
draw.speed(0)
draw.down()
draw.tracer(0)
draw.color("blue","green")

if (figure == 1):
    Poly(num)
elif (figure == 2):
    Polys(num)
else:
    Flower(num)

