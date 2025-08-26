from tkinter import *
import time
from time import strftime

def updateTime(): #creates a clock
    stringTime = strftime("%H:%M %p") #gives the clock hours and minutes
    clock.config(text=stringTime) #configurates the clock
    clock.after(1000, updateTime) #updates the clock every second

window = Tk()
window.title("Immani")
window.configure(bg = "#FFB3C6")
window.geometry("2000x1600")
window.columnconfigure(0,weight = 0) #adds a weight to a column
window.columnconfigure(1,weight = 1)#adds a weight to a column
window.columnconfigure(2,weight = 1)#adds a weight to a column
window.columnconfigure(3,weight = 1)#adds a weight to a column
window.columnconfigure(4,weight = 1)#adds a weight to a column
window.columnconfigure(5,weight = 1)#adds a weight to a column
window.columnconfigure(6,weight = 1)#adds a weight to a column
window.columnconfigure(7,weight = 1)#adds a weight to a column
window.columnconfigure(8,weight = 1)#adds a weight to a column
window.columnconfigure(9,weight = 1)#adds a weight to a column
window.columnconfigure(10,weight = 0)#adds a weight to a column
window.columnconfigure(11,weight = 1)#adds a weight to a column
window.columnconfigure(12,weight = 1)#adds a weight to a column
window.columnconfigure(13,weight = 1)#adds a weight to a column
window.columnconfigure(14,weight = 1)#adds a weight to a column
window.columnconfigure(15,weight = 1)#adds a weight to a column
window.columnconfigure(16,weight = 1)#adds a weight to a column
window.columnconfigure(17,weight = 1)#adds a weight to a column
window.columnconfigure(18,weight = 1)#adds a weight to a column
window.columnconfigure(19,weight = 1)#adds a weight to a column
window.columnconfigure(20,weight = 0)#adds a weight to a column
window.columnconfigure(21,weight = 1)#adds a weight to a column
window.columnconfigure(22,weight = 1)#adds a weight to a column
window.columnconfigure(23,weight = 1)#adds a weight to a column
window.columnconfigure(24,weight = 1)#adds a weight to a column
window.columnconfigure(25,weight = 0)#adds a weight to a column


window.rowconfigure(0,weight = 0)#adds a weight to a row
window.rowconfigure(1,weight = 0)#adds a weight to a row
window.rowconfigure(2,weight = 0)#adds a weight to a row
window.rowconfigure(3,weight = 1)#adds a weight to a row
window.rowconfigure(4,weight = 1)#adds a weight to a row
window.rowconfigure(5,weight = 1)#adds a weight to a row
window.rowconfigure(6,weight = 1)#adds a weight to a row
window.rowconfigure(7,weight = 1)#adds a weight to a row
window.rowconfigure(8,weight = 1)#adds a weight to a row
window.rowconfigure(9,weight = 1)#adds a weight to a row
window.rowconfigure(10,weight = 1)#adds a weight to a row
window.rowconfigure(11,weight = 1)#adds a weight to a row
window.rowconfigure(12,weight = 1)#adds a weight to a row
window.rowconfigure(13,weight = 0)#adds a weight to a row
window.rowconfigure(14,weight = 0)#adds a weight to a row
window.rowconfigure(15,weight = 0)#adds a weight to a row
window.rowconfigure(16,weight = 0)#adds a weight to a row
window.rowconfigure(17,weight = 0)#adds a weight to a row
window.rowconfigure(18,weight = 0)#adds a weight to a row
window.rowconfigure(19,weight = 0)#adds a weight to a row
window.rowconfigure(20,weight = 0)#adds a weight to a row
window.rowconfigure(21,weight = 0)#adds a weight to a row
window.rowconfigure(22,weight = 0)#adds a weight to a row
window.rowconfigure(23,weight = 1)#adds a weight to a row
window.rowconfigure(24,weight = 1)#adds a weight to a row
window.rowconfigure(25,weight = 0)#adds a weight to a row

title = Label(window, text = "IMMANI <3", font = ("calibri",50,"bold"), bg = "#FFB3C6", fg = "#000000") #creates a title for the page
title.grid(row = 1, column = 10, sticky = "nsew") #positions the title on the window

clock = Label(window, font = ("calibri", 40, "bold"), bg = "#FFB3C6", fg = "#000000") #creates the clock display as a label
clock.grid(row = 0, column = 25, sticky = "ne") #positions the clock on the window

updateTime()
window.mainloop()