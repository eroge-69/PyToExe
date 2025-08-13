
"""def arrayfun(a,b):
    b = list(a)



def errorfun():
    global screentext
    print("Error")
    screentext = "ERROR"
    print(screentext)
    updatescreen()


def leadingzeros(): # removes leadingzeros
    global screentext
    screentext = float(screentext)
    screentext = str(screentext)
    updatescreen()


def testfun1(): #if there are more than 24 characters it turns to standard form
    leadingzeros()
    global screentext, screenarray, sf, powercount #gloablise variables
    print(screentext)
    screentextlen = len(screentext) # calcualtes length of text
    if screentextlen > 24:# 24 is max character limit
        screenfloat = float(screentext) # cast to float
        power = screentextlen - 1 # calculates power
        print(power)
        if power > 50:
            errorfun()
        else:
            screenarray = list(screentext) # turns string into an array
            screenten = screenarray[:10] # only uses first 10 items in array
            screenten.insert(1,".")
            screenten.append("x10^")
            screenten.append(power)
            screentext = "".join(str(x) for x in screenten)
            print(screentext)


    else:
        screentext = screentext
    updatescreen()"""

# notes



# import libaries
import tkinter as tk
import math

#set window---
window = tk.Tk()
window.geometry("310x465")#310,440
#window.minsize(310,440)
#window.maxsize(310,440)
window.title("Calculator")  # names the window
photo = tk.PhotoImage(file = 'calc2png.png')  # changes the icon of the window
window.wm_iconphoto(False, photo)


#def variables---
buttony = 3 # height of the buttons
buttonx = 5 # width of the buttons
screentextarray=["0"]
current = []
operation = 0
screentextfloat = 0
currentfloat = 0
functionpress = 0
memory = 0
memorypress = 0


screentext = ""
screenarray = []
sf = False
#create functions---


def testfun():
    hello


#update screen---
def updatescreen():
    global screentext, screentextarray
    screentext = "".join(str(x) for x in screentextarray)#turns array into string
    screen.config(text = screentext)# updates the screen

#stores value after function press---
def currentvalue():
    global screentextarray, current
    current = screentextarray #current = the value on screen
    screentextarray = [] # clears value on screen

#convert array to float--
def array2float():
    global screentextfloat, currentfloat, screentextarray, current
    if screentextarray:
        screentextfloat = "".join(str(x) for x in screentextarray)# joins array into string
        screentextfloat = float(screentextfloat) # converts to float
    else:
        screentextfloat = 0
    if current:
        currentfloat = "".join(str(x) for x in current)
        currentfloat = float(currentfloat)
    else:
        currentfloat = 0


#calculates result--
def result():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    array2float()
    if operation == 1:
        screentext = currentfloat + screentextfloat
        print(screentext, currentfloat, screentextfloat)
    elif operation == 2:
        screentext = currentfloat - screentextfloat
    elif operation == 3:
        screentext = currentfloat * screentextfloat
    elif operation == 4:
        screentext = currentfloat / screentextfloat
    elif operation == 5:
        screentext = math.sqrt(currentfloat)
    elif operation == 6:
        screentext = currentfloat/100
    elif operation == 0:
        screentext = screentext

    operation = 0
    screentextarray =list(str(screentext))
    updatescreen()
    screentextarray = []


#entervalues to screen ---
#appends item to end of list: updates the screen
def enterzero():
    screentextarray.append("0")
    updatescreen()

def enterdoublezero():
    screentextarray.append("00")
    updatescreen()

def enterone():
    screentextarray.append("1")
    updatescreen()

def entertwo():
    screentextarray.append("2")
    updatescreen()

def enterthree():
    screentextarray.append("3")
    updatescreen()

def enterfour():
    screentextarray.append("4")
    updatescreen()

def enterfive():
    screentextarray.append("5")
    updatescreen()

def entersix():
    screentextarray.append("6")
    updatescreen()

def enterseven():
    screentextarray.append("7")
    updatescreen()

def entereight():
    screentextarray.append("8")
    updatescreen()

def enternine():
    screentextarray.append("9")
    updatescreen()

def enterdecimal(): # checks if you can enter a decmial point
    global screentextarray
    if "." in screentextarray:
        screentextarray = screentextarray
    else:
        screentextarray.append(".")
    updatescreen()


#clear functions---
#All clear

def ACfunc():
    global screentextarray, functionpress
    functionpress = 0
    screentextarray = []
    updatescreen()

#clear last entry
def CEfunc():
    global screentextarray, current, functionpress
    functionpress = functionpress -1
    if functionpress < 0:
        functionpress = 0
    else:
        functionpress = functionpress
    screentextarray = current
    updatescreen()

#backspace
def removedigit():
    global screentextarray
    if len(screentextarray) == 0: #if no value on screen it wont remove
        screentextarray = screentextarray
    else:
        screentextarray.pop()
    updatescreen()


#functions---
#calls current value:sets operation to number
def additionpress():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    currentvalue()
    operation = 1

def subtractionpress():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    currentvalue()
    operation = 2

def multiplicationpress():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    currentvalue()
    operation = 3

def divisionpress():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    currentvalue()
    operation = 4

def rootpress():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    currentvalue()
    operation = 5
    result()


def percentagepress():
    global operation, screentextarray, current, screentext, currentfloat, screentexfloat
    currentvalue()
    operation = 6
    result()


#memory functions--
#M+
def mempluspress():
    global memory, screentext, screentextarray
    memory = memory + float(screentext) #memory adds the value on screen
    print(memory)
    screentextarray = []
    updatescreen()# clear screen
#M-
def memminuspress():
    global memory, screentext, screentextarray
    memory = memory - float(screentext) # memory subtract value on  screen
    screentextarray = []
    updatescreen()# clear screen

def memoryclearrecall():
    global memorypress, screentext, memory,screentextarray
    if memorypress == 0: #if MCR hasnt been pressed
        screentext = memory
        screentext = str(screentext)
        screentextarray = list(screentext) # sets screen variable to memory
        memorypress = 1 # shows that MCR has been pressed
        updatescreen() # displays memory

    else:
        memory = 0 # resets value of memory
        screentextarray = ['M', 'e', 'm', 'o', 'r', 'y', ' ', 'C', 'l', 'e', 'a', 'r', 'e', 'd']
        updatescreen() # displays "Memory Cleared"
        screentextarray = [] # next click will reset screen




#create frame---
frame = tk.LabelFrame(window,padx = 10, pady = 10, bg = "White", relief = tk.RIDGE, width = 500, height = 500 )
frame.grid(padx = 5, pady = 5) # creates the frame

#create result box---
screen= tk.Label(frame, text = "---", font = 20, width = 30, height = 3, borderwidth = 2, relief = tk.GROOVE)
screen.grid(column = 0, row = 0, columnspan = 5,pady = 2) # allows result to span all columns

#create buttons---
#test button---
test=tk.Button(window,text = "test",command = testfun)
test.grid()

#column 0---
#create button: place button
memclear = tk.Button(frame, text = "MRC", font = 20, width = buttonx, height = buttony, command = memoryclearrecall)
memclear.grid(column = 0, row = 1)

delete = tk.Button(frame, text = "→", font = 20, width = buttonx, height = buttony, command = removedigit)
delete.grid(column = 0, row = 2)

CE = tk.Button(frame, text = "CE", font = 20, width = buttonx, height = buttony, command = CEfunc)
CE.grid(column = 0, row = 3)

AC = tk.Button(frame, text = "AC", font = 20, width = buttonx, height = buttony, command = ACfunc)
AC.grid(column = 0, row = 4)

zero = tk.Button(frame, text = "0", font = 20, width = buttonx, height = buttony, command = enterzero)
zero.grid(column = 0 , row = 5)

#column 1---
#create button: place button
memminus = tk.Button(frame, text = "M-", font = 20, width = buttonx, height = buttony, command = memminuspress)
memminus.grid(column = 1 , row = 1)

seven = tk.Button(frame, text = "7", font = 20, width = buttonx, height = buttony, command = enterseven)
seven.grid(column = 1, row =2)

four = tk.Button(frame, text = "4", font = 20, width = buttonx, height = buttony, command = enterfour)
four.grid(column = 1, row = 3)

one = tk.Button(frame, text = "1", font = 20, width = buttonx, height = buttony, command =enterone)
one.grid(column = 1, row = 4)

doublezero = tk.Button(frame, text = "00", font = 20, width = buttonx, height = buttony, command = enterdoublezero)
doublezero.grid(column = 1, row = 5)

#column 2---
#create button: place button
memplus = tk.Button(frame, text = "M+", font = 20, width = buttonx, height = buttony, command = mempluspress)
memplus.grid(column =2, row = 1)

eight = tk.Button(frame, text = "8", font = 20, width = buttonx, height = buttony, command = entereight)
eight.grid(column =2 ,row =2)

five = tk.Button(frame, text = "5", font = 20, width = buttonx, height = buttony, command = enterfive)
five.grid(column = 2, row = 3)

two = tk.Button(frame, text = "2", font = 20, width = buttonx, height = buttony, command = entertwo)
two.grid(column = 2, row = 4)

decimal = tk.Button(frame, text = "●", font = 20, width = buttonx, height = buttony, command = enterdecimal)
decimal.grid(column = 2, row = 5)

#column 3---
#create button: place button
root = tk.Button(frame, text = "√", font = 20, width = buttonx, height = buttony, command = rootpress)
root.grid(column = 3, row =1)

nine = tk.Button(frame, text = "9", font = 20, width = buttonx, height = buttony, command = enternine)
nine.grid(column = 3, row =2)

six = tk.Button(frame, text = "6", font = 20, width = buttonx, height = buttony, command =entersix)
six.grid(column = 3, row = 3)

three = tk.Button(frame, text = "3", font = 20, width = buttonx, height = buttony, command = enterthree)
three.grid(column = 3, row = 4)

equals = tk.Button(frame, text = "=", font = 20, width = buttonx, height = buttony, command = result)
equals.grid(column = 3, row = 5)

#column 4---
#create button: place button
percentage = tk.Button(frame, text = "%", font = 20, width = buttonx, height = buttony, command = percentagepress)
percentage.grid(column = 4, row = 1)

divide = tk.Button(frame, text = "÷", font = 20, width = buttonx, height = buttony, command = divisionpress)
divide.grid(column = 4, row = 2)

multiply = tk.Button(frame, text = "x", font = 20, width = buttonx, height = buttony, command = multiplicationpress)
multiply.grid(column = 4, row = 3)

minus = tk.Button(frame, text = "-", font = 20, width = buttonx, height = buttony, command = subtractionpress)
minus.grid(column = 4, row = 4)

add = tk.Button(frame, text = "+", font = 20, width = buttonx, height = buttony, command = additionpress)
add.grid(column = 4, row = 5)



#mainloop
window.mainloop()

