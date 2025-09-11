"""
A simple Dice Roller for Dungeons and Dragons

Version: 1.0.0
2025-09-11
(c) Sandro Klafack
theneti3@yahoo.de

"""
import tkinter as tk
import random

####### building functions #####

def ShowChoice():
    print(var.get())
    label1.config(text=var.get())
    

roll = 0
def roll_fun():
    roll = random.randint(1, var.get()) # generate random dice
    print(roll)
    result1.config(text=roll)
    # Special cases only D20
    if var.get() == 20:
        if roll == 20:
            special_label.config(text="Hooray! \n Natural 20!!!")
        elif roll == 1:
            special_label.config(text="You had one job... \n Nat 1 - LOOSER!")
        else:
            special_label.config(text="")  # reset, if no special case
    else:
        special_label.config(text="")      # reset for all other dice


####### building GUI ###########

root = tk.Tk()
root.title("DnD Roller")
root.geometry("500x300")
root.resizable(False, False)

root.columnconfigure(0, weight = 1, uniform="a")
root.columnconfigure(1, weight = 1, uniform="a")
root.columnconfigure(2, weight = 1, uniform="a")
root.columnconfigure(3, weight = 1, uniform="a")
root.columnconfigure(4, weight = 1, uniform="a")
root.columnconfigure(5, weight = 1, uniform="a")
root.columnconfigure(6, weight = 1, uniform="a")
root.columnconfigure(7, weight = 1, uniform="a")
root.columnconfigure(8, weight = 1, uniform="a")
root.columnconfigure(9, weight = 1, uniform="a")
root.columnconfigure(10, weight = 1, uniform="a")
root.columnconfigure(11, weight = 1, uniform="a")
root.columnconfigure(12, weight = 1, uniform="a")
root.columnconfigure(13, weight = 1, uniform="a")
root.columnconfigure(14, weight = 1, uniform="a")
root.columnconfigure(15, weight = 1, uniform="a")
root.columnconfigure(16, weight = 1, uniform="a")
root.columnconfigure(17, weight = 1, uniform="a")
root.columnconfigure(18, weight = 1, uniform="a")
root.columnconfigure(19, weight = 1, uniform="a")
root.columnconfigure(20, weight = 1, uniform="a")
root.columnconfigure(21, weight = 1, uniform="a")
root.columnconfigure(22, weight = 1, uniform="a")
root.columnconfigure(23, weight = 1, uniform="a")
root.columnconfigure(24, weight = 1, uniform="a")
root.columnconfigure(25, weight = 1, uniform="a")
######### Checkbutton

var = tk.IntVar() 
#var.set(20)


radio1 = tk.Radiobutton(root, text="D4", variable=var, value=4, command=ShowChoice)
radio2 = tk.Radiobutton(root, text="D6", variable=var, value=6, command=ShowChoice)
radio3 = tk.Radiobutton(root, text="D8", variable=var, value=8, command=ShowChoice)
radio4 = tk.Radiobutton(root, text="D10", variable=var, value=10, command=ShowChoice)
radio5 = tk.Radiobutton(root, text="D12", variable=var, value=12, command=ShowChoice)
radio6 = tk.Radiobutton(root, text="D20", variable=var, value=20, command=ShowChoice)
radio7 = tk.Radiobutton(root, text="D100", variable=var, value=100, command=ShowChoice)

radio1.grid(column= 1, row= 1, columnspan=3)
radio2.grid(column= 1, row= 2, columnspan=3)
radio3.grid(column= 1, row= 3, columnspan=3)
radio4.grid(column= 1, row= 4, columnspan=3)
radio5.grid(column= 1, row= 5, columnspan=3)
radio6.grid(column= 1, row= 6, columnspan=3)
radio7.grid(column= 1, row= 7, columnspan=3)

#dice = var.get()

######### Show Dice Selection

label1 = tk.Label(root)
label2 = tk.Label(root, text="you want to roll:")

label1.grid(column= 3, row = 10, columnspan=3)
label2.grid(column= 3, row = 12, columnspan=5)

########## Roll Button

roll_button = tk.Button(root, text="ROLL!", command=roll_fun)
roll_button.grid(column = 3, row = 15, columnspan=3)

######### Show Roll Result

result1 = tk.Label(root, font=("",16, "bold"))
result1.grid(column= 7, row= 4, columnspan=12)

########## Special cases

# if var.get() == 20:
#         if roll == 20:
#             print("Hooray! Natural 20!!!")
#             special_label.config(text="Hooray! Natural 20!!!")
#         elif roll == 1:
#             print("You had one job... Nat 1 - LOOSER!")
#             special_label.config(text="You had one job... Nat 1 - LOOSER!")
# 
special_label = tk.Label(root, font=("", 14, ""), fg="red")
special_label.grid(column = 7, row = 6, rowspan=2, columnspan=12)

######### Exit Button

exit_but = tk.Button(root, text="Exit", command=root.destroy)
exit_but.grid(column = 25, row = 20, columnspan=3)


####### Finish #################
root.mainloop()