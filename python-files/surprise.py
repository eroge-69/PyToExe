import turtle

turtle.setup(800,600)
turtle.bgcolor("black")
turtle.title("Сюрприз для тебя ❤")

pen= turtle.Turtle()

def curve():
    for i in range(200):
        pen.right(1)
        pen.forward(1)
        
def draw_heart():
    pen.pensize(4)
    pen.color("red")
    pen.begin_fill()
    pen.left(140)
    pen.forward(113)
    curve()
    pen.left(120)
    curve()
    pen.forward(112)
    pen.end_fill()
    
def write_message():
    pen.penup()
    pen.goto(0,-150)
    pen.color("white")
    pen.write("Я люблю тебя!"
              "Прости меня:(", align="center", font=("Arial", 24,"bold"))
   
turtle.speed(0)
draw_heart()
write_message()


