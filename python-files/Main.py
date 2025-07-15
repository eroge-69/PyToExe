# SETUP


# Imports
import turtle
import pygame as pg
from time import sleep
import sys
from math import degrees, atan2

sys.setrecursionlimit(1000000000)

# Initialization pygame and joystick
pg.init()
pg.joystick.init()

# Screen setup
screen = turtle.Screen()
screen.bgcolor('black')
screen.setup(1000, 500)
screen.title('Capture The Flag')

print('Both Joysticks Found, Continuing')

redj = pg.joystick.Joystick(0)
bluej = pg.joystick.Joystick(1)

# START MENU


run_main = False
t = turtle.Turtle()


def downline(y):
    t.penup()
    t.setx(0)
    t.sety(t.ycor() - y)
    t.pendown()


def menuScreenActions():
    global run_main

    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        elif event.type == pg.JOYBUTTONDOWN:
            if not run_main:
                if event.joy == 0 and event.button == 0 and redj:
                    run_main = True

                elif event.joy == 1 and event.button == 0 and bluej:
                    run_main = True

                elif event.joy == 0 and event.button == 2 and redj:
                    quit()

                elif event.joy == 1 and event.button == 2 and bluej:
                    quit()


def menuLoop():
    global run_main
    run_main = False

    t.hideturtle()
    t.speed(0)

    t.penup()
    t.setx(-225)
    t.sety(125)
    t.pendown()

    t.penup()
    t.setx(-225)
    t.sety(125)
    t.pendown()

    t.color('red')
    t.write('Capture', align='center', font=('Arial', 90, 'normal'))

    t.penup()
    t.setx(75)
    t.pendown()

    t.color('white')
    t.write('The', align='center', font=('Arial', 90, 'normal'))

    t.penup()
    t.setx(300)
    t.pendown()

    t.color('blue')
    t.write('Flag', align='center', font=('Arial', 90, 'normal'))

    downline(150)

    t.color('white')
    t.write('Press A to start', align='center', font=('arial', 45, 'italic'))
    downline(50)
    t.write('Press X to quit', align='center', font=('arial', 45, 'italic'))

    while not run_main:
        menuScreenActions()


menuLoop()

screen.clearscreen()
screen.bgcolor('black')


# END SCREEN

def win(winner):
    global screen
    global vhelp

    screen.clearscreen()

    screen.bgcolor('black')

    vhelp.penup()
    vhelp.sety(-50)
    vhelp.pendown()

    if winner == 'Team Red':
        vhelp.color('red')
        vhelp.write('{} Wins!'.format(winner), align='center', font=('Arial', 100, 'normal'))

        sleep(3)

        quit()

    else:
        vhelp.color('blue')
        vhelp.write('{} Wins!'.format(winner), align='center', font=('Arial', 100, 'normal'))

        sleep(3)

        quit()


# GAME


# Create main turtles
redt = turtle.Turtle()
bluet = turtle.Turtle()
redf = turtle.Turtle()
bluef = turtle.Turtle()

# Create text turtles

vhelp = turtle.Turtle()
counter = turtle.Turtle()
stracker = turtle.Turtle()

# Creat starting point turtles
rstart = turtle.Turtle()
bstart = turtle.Turtle()

# Scoring
rscore = 0
bscore = 0

# Flag Detection
rhas = False
bhas = False

# Red player setup
redt.penup()
redt.speed(0)
redt.turtlesize(2, 2, 1)
redt.fillcolor('red')

# Blue player setup
bluet.penup()
bluet.speed(0)
bluet.turtlesize(2, 2, 1)
bluet.fillcolor('blue')

# Red flag setup
redf.penup()
redf.speed(0)
redf.shape('circle')
redf.turtlesize(1.25, 1.25, .5)
redf.fillcolor('red')

# Blue flag setup
bluef.penup()
bluef.speed(0)
bluef.shape('circle')
bluef.turtlesize(1.25, 1.25, .5)
bluef.fillcolor('blue')

# Middle line and end text setup
vhelp.hideturtle()
vhelp.speed(0)
vhelp.penup()
vhelp.sety(250)
vhelp.pendown()
vhelp.color('white')
vhelp.sety(-250)

# Starting countdown setup
counter.hideturtle()
counter.speed(0)
counter.penup()
counter.color('white')

# Score tracker setup
stracker.speed(0)
stracker.penup()
stracker.hideturtle()
stracker.color('white')

# Red starting point setup
rstart.speed(0)
rstart.penup()
rstart.setx(-360)
rstart.shape('circle')
rstart.color('dark red')

# Blue starting point setup
bstart.speed(0)
bstart.penup()
bstart.setx(360)
bstart.shape('circle')
bstart.color('dark blue')


# Update Score tracker definition block
def points():
    global stracker
    global rscore, bscore

    stracker.clear()

    stracker.setx(-490)
    stracker.sety(225)

    stracker.pendown()

    stracker.write("Red's Score: {}/3.".format(rscore), font=('Arial', 15, 'normal'))

    stracker.penup()
    stracker.sety(200)
    stracker.pendown()

    stracker.write("Blue's Score: {}/3.".format(bscore), font=('Arial', 15, 'normal'))

    stracker.penup()
    stracker.sety(0)


# Screen round setup definition block
def setup():
    global redf, bluef
    global vhelp
    global redt, bluet

    redt.setx(-350)
    redt.sety(0)
    redt.setheading(0)

    bluet.setx(350)
    bluet.sety(0)
    bluet.setheading(180)

    redf.setx(-400)
    redf.sety(0)

    bluef.setx(400)
    bluef.sety(0)

    points()


# Flag setbacker definition block
def f_bk(f):
    global rhas, bhas

    if f == redf:
        bhas = False

        f.setx(-400)
        f.sety(0)
    else:
        rhas = False

        f.setx(400)
        f.sety(0)


# Turtle setbacker definition block
def s_start(t):
    if t == redt:
        f_bk(bluef)

        t.setx(-350)
        t.sety(0)

        t.setheading(0)

    else:
        f_bk(redf)

        t.setx(350)
        t.sety(0)

        t.setheading(180)


# Main setback events definition block
def tag(type, outt):
    if type == 'pvp':
        global redt, bluet

        if bluet.xcor() >= 0:
            s_start(redt)
        else:
            s_start(bluet)

    else:
        s_start(outt)


# Round starting definition block
def start():
    global counter

    setup()

    counter.pendown()

    counter.write('3', align='center', font=('Arial', 100, 'normal'))
    sleep(1)
    counter.clear()

    counter.write('2', align='center', font=('Arial', 100, 'normal'))
    sleep(1)
    counter.clear()

    counter.write('1', align='center', font=('Arial', 100, 'normal'))
    sleep(1)
    counter.clear()

    counter.write('Go!', align='center', font=('Arial', 100, 'normal'))
    sleep(0.5)
    counter.clear()


start()


# Action detector definition block
def frame():
    global redj, bluej
    global redt, bluet
    global rscore, bscore
    global rhas, bhas

    blueh = bluej.get_axis(1)
    bluev = bluej.get_axis(0)

    redh = redj.get_axis(0)
    redv = redj.get_axis(1)

    dead_zone = 0.3

    if abs(blueh) < dead_zone:
        blueh = 0
    if abs(bluev) < dead_zone:
        bluev = 0

    dx = blueh * 10
    dy = -bluev * 10

    # Move the turtle
    bluet.goto(bluet.xcor() + dx, bluet.ycor() + dy)

    if blueh != 0 or bluev != 0:
        angle = degrees(atan2(-bluev, blueh))
        bluet.setheading(angle)

    if redj.get_button(2) == 1 or bluej.get_button(2) == 1:
        quit()

    if abs(redh) < dead_zone:
        redh = 0
    if abs(redv) < dead_zone:
        redv = 0

    dx = redh * 10
    dy = -redv * 10

    # Move the turtle
    redt.goto(redt.xcor() + dx, redt.ycor() + dy)

    if redh != 0 or redv != 0:
        angle = degrees(atan2(-redv, redh))
        redt.setheading(angle)

    if redj.get_button(2) == 1 or bluej.get_button(2) == 1:
        quit()

    if redf.distance(bluet) <= 35:
        bhas = True

        redf.setx(bluet.xcor())
        redf.sety(bluet.ycor())

    if bluef.distance(redt) <= 35:
        rhas = True

        bluef.setx(redt.xcor())
        bluef.sety(redt.ycor())

    if bhas and bluet.xcor() >= 0:
        rhas = False
        bhas = False

        if bscore == 2:
            win('Team Blue')
        else:
            bscore += 1
            start()

    elif rhas and redt.xcor() <= 0:
        rhas = False
        bhas = False

        if rscore == 2:
            win('Team Red')
        else:
            rscore += 1
            start()

    if bluet.distance(redt) <= 15:
        tag('pvp', None)

    x = redt.xcor()
    y = redt.ycor()

    if x > 500 or x < -500 or y > 250 or y < -250:
        tag('tout', redt)

    x = bluet.xcor()
    y = bluet.ycor()

    if x > 500 or x < -500 or y > 250 or y < -250:
        tag('tout', bluet)

    sleep(0.025)
    frame()


frame()

screen.update()
screen.mainloop()