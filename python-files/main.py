from tkinter import *

root = Tk()
root.title('Calculator')
root.geometry('300x400')
root.iconbitmap('icon.ico')

def one():
    entry.insert(END, '1')

def two():
    entry.insert(END, '2')

def three():
    entry.insert(END, '3')

def four():
    entry.insert(END, '4')

def five():
    entry.insert(END, '5')

def six():
    entry.insert(END, '6')

def seven():
    entry.insert(END, '7')

def eight():
    entry.insert(END, '8')

def nine():
    entry.insert(END, '9')

def zero():
    entry.insert(END, '0')

def equals():
    try:
        r = entry.get()
        entry.delete(0, END)
        entry.insert(0, eval(r))
    except (ZeroDivisionError, NameError, SyntaxError):
        entry.delete(0, END)
        entry.insert(0, 'Error')

entry = Entry()
entry.place(x=85, y=50)

btn_1n = Button(text='1', font=('TkDefaultFont', 13), command=one)
btn_1n.place(x=90, y=110)

btn_2n = Button(text='2', font=('TkDefaultFont', 13), command=two)
btn_2n.place(x=130, y=110)

btn_3n = Button(text='3', font=('TkDefaultFont', 13), command=three)
btn_3n.place(x=170, y=110)

btn_4n = Button(text='4', font=('TkDefaultFont', 13), command=four)
btn_4n.place(x=90, y=150)

btn_5n = Button(text='5', font=('TkDefaultFont', 13), command=five)
btn_5n.place(x=130, y=150)

btn_6n = Button(text='6', font=('TkDefaultFont', 13), command=six)
btn_6n.place(x=170, y=150)

btn_7n = Button(text='7', font=('TkDefaultFont', 13), command=seven)
btn_7n.place(x=90, y=190)

btn_8n = Button(text='8', font=('TkDefaultFont', 13), command=eight)
btn_8n.place(x=130, y=190)

btn_9n = Button(text='9', font=('TkDefaultFont', 13), command=nine)
btn_9n.place(x=170, y=190)

btn_0n = Button(text='0', font=('TkDefaultFont', 13), command=zero)
btn_0n.place(x=130, y=230)

btn_equals = Button(text='=', font=('TkDefaultFont', 13), command=equals)
btn_equals.place(x=210, y=270)

def division():
    entry.insert(END, '/')

def mlp():
    entry.insert(END, '*')

def minus():
    entry.insert(END, '-')

def plus():
    entry.insert(END, '+')

btn_division = Button(text='/', font=('TkDefaultFont', 13), command=division)
btn_division.place(x=210, y=230)

btn_mlp = Button(text='*', font=('TkDefaultFont', 13), command=mlp)
btn_mlp.place(x=210, y=190)

btn_minus = Button(text='-', font=('TkDefaultFont', 13), command=minus)
btn_minus.place(x=210, y=150)

btn_plus = Button(text='+', font=('TkDefaultFont', 13), command=plus)
btn_plus.place(x=210, y=110)

def bs():
    entry.delete(len(entry.get()) - 1, END)

def cls():
    entry.delete(0, END)

btn_bs = Button(text='←', font=('TkDefaultFont', 13), command=bs)
btn_bs.place(x=50, y=110)

btn_cls = Button(text='CLS', font=('TkDefaultFont', 13), command=cls)
btn_cls.place(x=35, y=150)

root.mainloop()
