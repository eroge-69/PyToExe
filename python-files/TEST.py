
from tkinter import *

icon = PhotoImage(file="E:\Python Projects\logo.jpeg")

#window = Serves as a container to hold the winget
#winget = GUI elements: buttons ,textboxes ,labels images

window = Tk() #creates the instance of the window
window.geometry("640x480")
window.title("CODE TEST INSTANCE 1")

window.config(background="black")

def draw_GUI():
    window.mainloop() #draws the windows


def run():
    for A in [1,23,636,722,69]:
            print(A)
            draw_GUI()

run()