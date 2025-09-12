from tkinter import *

def b1(event):
    root.title('Левая кнопка мыши')
def b3(event):
    root.title('Правая кнопка мыши')

def move(event):
    x = event.x
    y = event.y
    s = "Движение мышью {}x{}".format(x,y)
    root.title(s)


root = Tk()
root.geometry('500x400')
root.title('Действия мыши')
root.bind('<Button-1>',b1)
root.bind('<Button-3>',b3)
root.bind('<Motion>',move)

root.mainloop()
