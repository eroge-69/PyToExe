import turtle as t
t.bgcolor("black")
t.pensize(5)
t.speed(1)
t.color("pink")
t.begin_fill()
t.fillcolor("pink")
t.left(150)
t.forward(180)
t.circle(-90,180)
t.setheading(60)
t.circle(-90,180)
t.forward(180)
t.end_fill()
t.hideturtle()
msg="  te amo mucho, precioso."
t.write(msg,move=True,align="left",
font=("Arial",25,"italic","bold"))

t.done()