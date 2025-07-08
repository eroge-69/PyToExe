#GUI that allows user to toggle Windows Key functionality 

import keyboard 
from tkinter import *

window = Tk()
window.title("NoWinKey")
winBlocked = False

def disable():
    global winBlocked
    winBlocked = True
    keyboard.block_key('win')
    enable.configure(state=ACTIVE)
    disable.configure(state=DISABLED)
    dLabel.configure(text='Current Status: DISABLED')
   
def enable():
    global winBlocked
    if winBlocked == True:
        winBlocked = False
        keyboard.unblock_key('win')
        disable.configure(state=ACTIVE)
        enable.configure(state=DISABLED)
        dLabel.configure(text='Current Status: ENABLED')
    else:
        disable.configure(state=ACTIVE)
        enable.configure(state=DISABLED)

myLabel = Label(window, text='Toggle your \'Windows Key\' functionality',padx=10, pady=10)
disable = Button(window, text='DISABLE', padx=30, pady=10, command=disable)
enable = Button(window, text='ENABLE', padx=30, pady=10, command=enable)
emptyBottom = Label(text="")
dLabel = Label(window, text='Current Status: ENABLED')

myLabel.grid(row=2, columnspan=4)
disable.grid(row=4, column=1)
enable.grid(row=4, column=2)
emptyBottom.grid(row=5, columnspan=4)
dLabel.grid(row=6, columnspan=4)

window.mainloop()
