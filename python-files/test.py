from tkinter import *
from tkinter import messagebox

class TestShakhsiat:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("0x0")
        self.ask()
        self.root.mainloop()


    def ask(self):
       while True:
        self.answer =  messagebox.askyesno(title="تست گرایش", message="آیا تو گی هستی؟")
        if self.answer == True:
           messagebox.showinfo(message="=) میدونستم گی ای")
           break

        else:
           messagebox.showerror(message="نه تو گی ای حتمی")
            

TestShakhsiat()
