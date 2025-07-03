#imports
import turtle
from tkinter import messagebox
import random
import os
from time import sleep

turtle.shape("classic")

#defining
def ding():
    tr.home()
    ts.clearscreen()
    ts.bgcolor("black")
    tr.color("white")
    tr.speed(1)
    for i in range(random.randint(2, 5)):
        tr.write("loading....", move=True, align='center', font=("Courier", 50, "bold"))
        tr.home()
    ts.clearscreen()
    ts.bgcolor("black")
    tr.write(f"""
{os.getlogin()}, your package is at
{random.randint(0, 180)}°{random.randint(20, 104)}'{random.randint(0, 40)}''N
{random.randint(0, 180)}°{random.randint(20, 104)}'{random.randint(0, 40)}''E

wish you good luck.""", move=False, align="center", font=("Courier", 30, "bold"))
def package_ask():
    packask = ts.textinput(None, "would you like to get a package?")
    if packask == "yes":
            ding()

#introduction
ts = turtle.Screen()
tr = turtle.Turtle()
ts.bgcolor("black")
tr.color("#3b1b2b")
messagebox.showinfo(None, "start?")
for o in range(3):
    tr.write("treasured.", move=True, align='center', font=("Courier", 50, "italic", "bold"))
    tr.left(180)
    tr.forward(200)
    tr.right(90)
    tr.forward(50)

#requests
request = ts.textinput(None, "type request here......")
if request == "complaint":
    ts.textinput(None, "type complaint here......")
    messagebox.showinfo(None, "ok, the dev will probably fix your problem....")
    package_ask()
if request == "rate":
    ts.textinput(None, "rate us here......")
    messagebox.showinfo(None, "thanks!")
    package_ask()
if request == "package":
    messagebox.showinfo(None, "we can only send you the package if you read the TERMS and CONDITIONS so go READ THEM........")
    ding()
if request == "exit":
    ts.bye()