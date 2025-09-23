from PIL import ImageTk
from tkinter import Button
from tkinter import *
import tkinter as tk
import ctypes
import time
import re
import os

main_window = tk.Tk()
main_window.title("Savva OS 4.0 test")
main_window.geometry("1000x500")
main_window.resizable(False, False)
canvas = Canvas(main_window, width=1000, height=500)
canvas.pack()

#Картинки
wallaper = PhotoImage(file='Hello.png')
image_internet = PhotoImage(file='Internet.png')

button_internet = tk.Button(main_window, image=image_internet, command=lambda: internet())
button_internet.place(x=100, y=0)

canvas.create_image(0,0,anchor=NW,image=wallaper)

def internet():
    internet_window = tk.Tk()
    internet_window.title("Интернет")
    internet_window.geometry("1050x500")
    canvas_internet = Canvas(internet_window, width=1050, height=500)
    canvas_internet.pack()

    wallaper_internet = PhotoImage(file='sait.png')
    canvas_internet.create_image(0,0,anchor=NW,image=wallaper_internet)

    internet_window.mainloop()

canvas.create_image(0, 0, anchor = NW, image=wallaper)
main_window.mainloop()