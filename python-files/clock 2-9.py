from  tkinter import *
from tkinter.ttk import *

from  time import  strftime

window = Tk()
window.title('"ЭЛЕКТРОНИКА"')
window.geometry('390x80')

lable = Label(window, font=('arial', 52), background='black', foreground='green')

def time():
    string = strftime('%H:%M:%S %p')
    lable.config(text=string)
    lable.after(1000, time)

lable.pack(anchor='center')
time()

mainloop()