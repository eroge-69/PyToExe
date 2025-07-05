from tkinter import *
import time


root = Tk()
root.title('sosal')
root.geometry('300x150')


def sosal_da():
    for a in main:
        a.grid_forget()
    da_otvet.pack()
    
def sosal_net():
    for a in main:
        a.grid_forget()
    net_otvet.pack()
    button_back.pack()

def back():
    net_otvet.forget()
    button_back.forget()
    sosal_text.grid(row=1, column=2)
    button_da.grid(row=2, column=1)
    button_net.grid(row=2, column=3)





sosal_text = Label(text='Сосал?', font=('arial', 24))

button_da = Button(text='Да', font=('arial', 18), width=4, command=sosal_da)

button_net = Button(text='Нет', font=('arial', 18), width=4, command=sosal_net)

button_back = Button(text='Вернуться', font=('arial', 18),  command=back)



sosal_text.grid(row=1, column=2)
button_da.grid(row=2, column=1)
button_net.grid(row=2, column=3)



da_otvet = Label(text='Другого я и \n не ожидал💕', font=('arial', 24))
net_otvet = Label(text='Пиздабол😡 \n Ответь правильно!!!', font=('arial', 20))


main = [sosal_text, button_da, button_net]




root.mainloop()