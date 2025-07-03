import random
from turtle import Turtle, Screen
screen = Screen()

nigers = ["nigg", "nogg", "nagg", "negg", "nugg"]
colors = ["black", "red", "blue", "green", "yellow"]
screen.setup(width=400, height=400)

# setting up nigers
for niger in nigers:
    globals()[niger] = Turtle(shape="turtle",)
    globals()[niger].color(colors[nigers.index(niger)])
    globals()[niger].penup()
    globals()[niger].goto(x= -180, y= -100 + nigers.index(niger)*50)

bet = screen.textinput("nigers race!", "which niger will win?")

#racing
race = True
winner = "none"
while race:
    globals()[niger].speed("fast")
    for niger in nigers:
        globals()[niger].forward(random.randint(1, 5))
        if globals()[niger].pos()[0] > 170:
            race = False
            winner = niger

if bet == winner:
    print(f"Your niger {bet} won!")
else:
    print(f"your niger did not win. The winner is {winner}")








screen.exitonclick()
