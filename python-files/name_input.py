import turtle

scr = turtle.Screen()
scr.setup(800, 600)
scr.title('Naming')

t = turtle.Turtle()
t.penup()
t.pencolor("red")
t.pensize(50)
t.hideturtle()

yourName = scr.textinput("Your First",  "What Is Your Name (optional):")
t.pensize(50)
t.write(yourName)


yourLast = scr.textinput("Your Last", "What is your last Name? (optional):")
t.pensize(50)
t.goto(0, -20)
t.write(yourLast)

yourTube = scr.textinput("Youtube", "What is Your Youtube (optional):")
t.pensize(50)
t.goto(0, -30)
t.write(yourTube)

age = scr.numinput("Your Age", "Enter your age (optional):", 1, minval=1, maxval=100)
t.pensize(50)
t.goto(0, -40)
t.write(age)

end = ("Nice!")

t.goto(0, 100)
t.write(end)

t.hideturtle()