#moudule
from tkinter import *
from winsound import *

#creat tab
root=Tk()
root.config(bg='light green')
root.title('Car Factory')
root.resizable(False,False)
root.geometry('570x550')
root.iconbitmap('icon.ico')

#import images
pb=PhotoImage(file='b.gif')
psb=PhotoImage(file='Shape key.gif')
psb2=PhotoImage(file='sk2.gif')
c1=PhotoImage(file='c1.gif')
c2=PhotoImage(file='c2.gif')
c3=PhotoImage(file='c3.gif')
c4=PhotoImage(file='c4.gif')
g2=PhotoImage(file='g2.gif')
g3=PhotoImage(file='g3.gif')
s=PhotoImage(file='sumbit.gif')
car_image=PhotoImage(file='b.gif')


#file selector and car creator
name=StringVar()
class Car():
    def __init__(self,Shape,coler,glass):
        global car_image
        if Shape==0:self.Shape='R'
        else:self.Shape='C'
        if coler==0:self.coler='B'
        elif coler==1:self.coler='C'
        elif coler==2:self.coler='M'
        else:self.coler='W'
        if glass==0:self.glass='R'
        else:self.glass='C'
        car_name=self.Shape+self.coler+self.glass+'.gif'
        car_image=PhotoImage(file=car_name)
        display.config(image=car_image)
        display.place(y=40,x=0)
    def __repr__(self):
        car_name=''
        if self.Shape=='R':car_name+='Rectangular'
        else:car_name+='Oval'
        if self.coler=='B':car_name+=' Black'
        elif self.coler=='C':car_name+=' Cyan'
        elif self.coler=='M':car_name+=' Magenta'
        else:car_name+=' White'
        car_name+=' car with '
        if self.glass=='R':car_name+='Recangular'
        else:car_name+='Oval'
        car_name+='Glass'
        return car_name

#format keys functions
a=0
b=0
c=0
def shape_key_format():
    global a
    if a==0:
        shape_button.config(image=psb2,command=shape_key_format)
        a=1
    else:
        shape_button.config(image=psb,command=shape_key_format)
        a=0
    Beep(800,100)
def coler_key_format():
    global b
    if b==0:
        coler_button.config(image=c2,command=coler_key_format)
        b=1
    elif b==1:
        coler_button.config(image=c3,command=coler_key_format)
        b=2
    elif b==2:
        coler_button.config(image=c4,command=coler_key_format)
        b=3
    else:
        b=0
        coler_button.config(image=c1,command=coler_key_format)
    Beep(800,100)
def glass_key_format():
    global c
    if c==0:
        glass_button.config(image=g2,command=glass_key_format)
        c=1
    elif c==1:
        glass_button.config(image=g3,command=glass_key_format)
        c=0
    Beep(800,100)

#create funcition and name set
def sumbit():
    global name
    car=Car(a,b,c)
    name.set(car)
    Beep(800,100)


#car name and up lable
lable_up=Label(text='Car factory(by MM)',font='Nazanin',bg='light green').place(x=0,y=0)
name_lable=Label(textvariable=name,font='Nazanin',bg='light green',foreground='red')
name_lable.place(x=120,y=0)

#display
display=Label(image=pb)
display.place(y=40,x=0)

#keys
shape_button=Button(image=psb,command=shape_key_format)
shape_button.place(x=50,y=440)
coler_button=Button(image=c1,command=coler_key_format)
coler_button.place(y=440,x=150)
glass_button=Button(image=g3,command=glass_key_format)
glass_button.place(y=440,x=250)


#create key
sumbit_b=Button(image=s,command=sumbit)
sumbit_b.place(y=440,x=450)
root.bind('<Return>',lambda event:sumbit())

#finished ui creating
root.mainloop()