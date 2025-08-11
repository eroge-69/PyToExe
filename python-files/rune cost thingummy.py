import tkinter
from tkinter import *
from tkinter import ttk
import tkinter.messagebox

def calculate_runes():
    startlevel = from_input.get()
    endlevel = to_input.get()
    total = 0
    try:
        startlevel = int(startlevel)
        endlevel = int(endlevel)
    except TypeError:
        return
    total = 0
    for i in range(startlevel,endlevel):
        x = ((i + 81)-92)*0.02
        x = round(x,0)
        if x < 0: x = 0
        cost = ((x+0.1)*((i+81)**2))+1
        cost = round(cost,0)
        total += int(cost)
    
    tkinter.messagebox.showinfo("Result",f"You need {total} runes to get from level {startlevel} to level {endlevel}.")






root = Tk()
root.geometry("700x420")
root.title("Calculate needed runes")

title_label = Label(root,font=("System",30), text="Rune Calculator")
title_label.pack(padx=20,pady=20)

from_label = Label(root,font=("System",10),text="From Level:")
from_label.pack()

from_input = Entry(root,font=("System",30))
from_input.pack(padx=20,pady=20)

to_label = Label(root, font=("System",10),text="To Level:")
to_label.pack()

to_input = Entry(root, font=("System",30))
to_input.pack(padx=20,pady=20)

calculate_button = Button(root,font=("System",30),text="Calculate Required Runes",command=calculate_runes)
calculate_button.pack()




root.mainloop()