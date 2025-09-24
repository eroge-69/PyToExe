from tkinter import *
from tkinter import ttk
import random
from tkinter.messagebox import showerror, showwarning, showinfo
 
root = Tk()
root.title("Комп дал Error")
root.geometry("150x150")

a = random.randint(0, 1920)
root.geometry("+"+str(random.randint(0, 1920))+"+"+str(random.randint(0, 1080)))
root.configure(bg='red')
    
 
 

root.mainloop()
