import tkinter as tk
import math as math
operation = ""

def calculate():
    global operation
    try:
        result = str(eval(operation))
        textOutput.delete(1.0, "end")
        textOutput.insert(1.0, result)
    except:
        clear()
        textOutput.insert(1.0, "Error.")

def clear():
    global operation
    operation = ""
    textOutput.delete(1.0, "end")

def updateScreen(userInput):
    global operation
    operation += str(userInput)
    textOutput.delete(1.0, "end")
    textOutput.insert(1.0, operation)

root = tk.Tk()
root.geometry("315x275")
root.resizable(False, False)

textOutput = tk.Text(root, height=2, width=16, font=("consolas", 24))
textOutput.grid(columnspan=5)

gambiarra = [1, 2, 3, 1, 2, 3, 1, 2, 3]

def defaultBtn(row, col, txt):
    tk.Button(root, text=txt, 
                command=lambda freeze = txt: updateScreen(txt),
                width=3,
                font=("consolas", 16)).grid(row = row, column = col)

for i in range(1,10):
    iRow = math.ceil(i / 3) #111 222 333
    iColumn = gambiarra[i-1]
    print(iColumn)
    i = str(i)
    defaultBtn(iRow, iColumn, i)
    
li = ["0", "+", "-", "*", "/"]
for c in range(1, 5):
    defaultBtn(c, 4, li[c])

defaultBtn(4, 2, "0")

tk.Button(root, text="=", 
                command=lambda: calculate(),
                width=3,
                font=("consolas", 16)).grid(row = 4, column = 3)

tk.Button(root, text="C", 
                command=lambda: clear(),
                width=3,
                font=("consolas", 16)).grid(row = 4, column = 1)

root.mainloop()
