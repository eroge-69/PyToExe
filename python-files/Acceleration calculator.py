import math
import time
from tkinter import *
from tkinter import messagebox

def main():
    global window2
    global Entrywin
    global Entrywin1
    global Entrywin2
    global Ans
    window1.destroy()
    window2 = Tk()
    window2.title("Acceleration Calculator")
    window2.geometry("900x530")
    window2.config(bg="#00ff00")
    
    labelwin = Label(window2, text="Enter Final Velocity (km/h): ", font=("Impact", 35), bg="#00ff00")
    labelwin.grid(column=0, row=0)
    Entrywin = Entry(window2, font=("Impact", 25))
    Entrywin.grid(column=1, row=0)
    
    labelwin1 = Label(window2, text="Enter Initial Velocity (km/h): ", font=("Impact", 35), bg="#00ff00")
    labelwin1.grid(column=0, row=1)
    Entrywin1 = Entry(window2, font=("Impact", 25))
    Entrywin1.grid(column=1, row=1)
    
    labelwin2 = Label(window2, text="Enter Time (s): ", font=("Impact", 35), bg="#00ff00")
    labelwin2.grid(column=0, row=2)
    Entrywin2 = Entry(window2, font=("Impact", 25))
    Entrywin2.grid(column=1, row=2)
    
    but1 = Button(window2, text="Calculate", font=("Impact", 25), command=main2, bg="blue", activebackground="red", fg="red", activeforeground="blue")
    Ans = Label(window2, font=("Impact", 38), bg="#00ff00")
    Ans.grid(row=4, column=0, columnspan=2)
    but1.grid(row=3, column=0, columnspan=2)
    
    window2.mainloop()

def main2():
    
    try:
        final1 = float(Entrywin.get())  
        initial1 = float(Entrywin1.get())  
        time_value = float(Entrywin2.get())
        
        if time_value == 0:
            messagebox.showerror(title="Error2", message="Time cannot be zero.")
            return  
        
        initial2 = initial1 / 3.6  
        final2 = final1 / 3.6      
        acc = (final2 - initial2) / time_value
        
        Ans.config(text=(f"{acc:.2f} m/s²"))  

    except ValueError:
        messagebox.showerror(title="Error", message="Error please Enter a valid number!")
def main3():
    window1.destroy()
    global window3
    global entini1
    global entvel1
    global enttim
    global answerlabel
    window3 = Tk()
    window3.title("Acceleration Calculator")
    window3.geometry("900x530")
    window3.config(bg="#00ff00")
    fin1 = Label(window3, text="Enter Final Velocity (m/s): ", font=("Impact", 35), bg="#00ff00")
    fin1.grid(column=0,row=0)
    inv2 = Label(window3, text="Enter initial Velocity (m/s): ", font=("Impact", 35), bg="#00ff00").grid(column=0, row=1)
    time3 = Label(window3, text="Time in seconds: ", font=("Impact", 35), bg="#00ff00").grid(column=0,row=2)
    entvel1 = Entry(window3, font=("Impact", 25))
    entvel1.grid(column=2,row=0)
    entini1 = Entry(window3, font=("Impact", 25))
    entini1.grid(column=2,row=1)
    enttim = Entry(window3, font=("Impact", 25))
    enttim.grid(column=2,row=2)
    submit = Button(window3, text="Calculate", font=("Impact", 25), command=main4,
                     bg="blue", activebackground="red", fg="red", activeforeground="blue")
    answerlabel = Label(window3, font=("Impact", 35), bg="#00ff00")
    answerlabel.grid(column=0,columnspan=3,row=5)
    submit.grid(column=0,columnspan=3,row=4)
    window3.mainloop()
def main4():
    try:
        final_velocity = float(entvel1.get())
        initial_velocity = float(entini1.get())
        time_secs = float(enttim.get())
        accelerate = (final_velocity-initial_velocity)/time_secs
        answerlabel.config(text=(f"Answer: {accelerate}m/s²"))
    except ValueError:
        messagebox.showerror(title="Error", message="Enter a number.")
def creditshow():
    credit_window = Tk()
    credit_window.title("Creator of Accleration calculator.")
    credit_window.geometry("480x480")
    credit_window.config(bg="#0200f0")
    credlab = Label(credit_window, text="Creator: Ayan Ashraf", bg="red",font=("Impact", 38)).pack(side=TOP)

window1 = Tk()
window1.geometry("500x500")
window1.title("Acceleration Calculator")
window1.config(bg="#00ff00")
label1 = Label(window1, text="km/h to m/s²", font=("Impact", 30), bg="#00ff00")
label1.grid(column=0, row=0)
label2 = Label(window1, text="m/s to m/s²", font=("Impact", 30), bg="#00ff00")
label2.grid(column=0,row=1)

Button1 = Button(window1, text="Continue", font=("Impact", 25), command=main, bg="blue", activebackground="red", fg="red", activeforeground="blue")
Button1.grid(column=1, row=0)
Button2 = Button(window1, text="Continue",
                  font=("Impact", 25), command=main3, bg="blue", activebackground="red", fg="red", activeforeground="blue")
Button2.grid(column=1, row=1)
credit = Button(window1, text="Credits",  font=("Impact", 25), command=creditshow, 
                bg="blue", activebackground="red", fg="red", activeforeground="blue").grid(column=0,row=8, columnspan=3)
window1.mainloop()
