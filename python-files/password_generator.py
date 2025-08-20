from tkinter import *
root =  Tk()

root.geometry("1270x600")
root.title("Password generator")

root.resizable(False,False)

check = Checkbutton(root,text="numbers")
check2 = Checkbutton(root,text="symbol")

label1 = Label(root,text="your password",font={50,"calibri","BOLD"})



check.pack()
check2.pack()
label1.pack()
root.mainloop()

#strong password generator
