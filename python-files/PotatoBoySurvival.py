### IMPORTS ###
import turtle as trtl #Turtle interface, used for game functionality, shortened to trtl
import random as rnd #Random, used to randomly generate enemy movements, shortened to rnd

### Screen Setup ###
trtl.clearscreen()
screen = trtl.Screen()
trtl.title("Potato Boy Survival")
screen.setup(700,700)
screen._root.resizable(False, False)
screen.bgpic("bg.gif")

### Carrot Setup ###
# Before player setup so that the player will apear above the carrots on the screen #
screen.addshape("carrotMan.gif")
carrots = []    
for i in range(3):
    carrots.append(trtl.Turtle())
    carrots[i].shape("carrotMan.gif")
    carrots[i].penup()
    carrots[i].speed(0)
    if i == 0:
        carrots[i].goto(300,300)
    elif i == 1:
        carrots[i].goto(-300,300)
    elif i == 2:
        carrots[i].goto(-300,-300)

### Player Setup ###
screen.addshape("sized.gif")
Player = trtl.Turtle()
Player.shape("sized.gif")
Player.penup()
Player.speed(0)
Player.goto(100,-100)

### Player Movement Functions ###

#Moves The Player Up
def Up():
    Player.seth(90)
    xCor, yCor = Player.position()
    if CheckOutBounds(25, "Up", xCor, yCor):
        Player.forward(25)
    
#Moves The Player Right
def Right():
    xCor, yCor = Player.position()
    Player.seth(0)
    if CheckOutBounds(10, "Right", xCor, yCor):
        Player.forward(10)

#Moves The Player Left
def Left():
    xCor, yCor = Player.position()
    Player.seth(180)
    if CheckOutBounds(10, "Left", xCor, yCor):
        Player.forward(10)

#Moves The Player Down
def Down():
    Player.seth(270)
    xCor, yCor = Player.position()
    if CheckOutBounds(10, "Down", xCor, yCor):
        Player.forward(10)

### Checks If Enemies And/Or The Player Is Out Of Bounds ###
def CheckOutBounds(speed, direction, xCor, yCor):
    if direction == "Up" and yCor + speed < 330:
        return True 
    elif direction == "Down" and yCor - speed > -290:
        return True
    elif direction == "Right" and xCor + speed < 300:
        return True
    elif direction == "Left" and xCor - speed > -320:
        return True

### Key Presses For Player Movement ###

#Up Movements
screen.onkey(Up, "Up")
screen.onkey(Up, "w")

#Left Movements
screen.onkey(Left, "Left")
screen.onkey(Left, "a")

#Right Movements
screen.onkey(Right, "Right")
screen.onkey(Right, "d")

#Down Movements
screen.onkey(Down, "Down")
screen.onkey(Down, "s")

#Looks for key presses
screen.listen() 

### Enemy Movements [Random] ###
def CarrotMovement():
    for i in range(len(carrots)):
        direction = rnd.randint(0,3) * 90
        carrots[i].seth(direction)
        if direction == 0:
            direction = "Right"
        elif direction == 90:
            direction = "Up"
        elif direction == 180:
            direction = "Left"
        else:
            direction = "Down"
        carX, carY = carrots[i].position()

        if CheckOutBounds(17, direction, carX, carY):
            carrots[i].forward(17)
    screen.ontimer(CarrotMovement, 25)
        
### Timers ###
screen.ontimer(CarrotMovement, 25)

### End of Main Loop ###
trtl.Screen().mainloop()