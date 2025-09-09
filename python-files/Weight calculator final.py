from tkinter import *

def sel():
   selection = "You selected the option " + str(var.get())
   label.config(text = selection)
   label.place(x=250,y=150)

def Close():
    root.destroy()


def AA():
# SS
    t2.delete(0, 'end')
    num1=float(t1.get())
    num2=float(t3.get())
    off=(3.142*(num1/2)*(num1/2)*num2*(8000/1000000000))
    result1=round(off,ndigits=8)
    t2.insert(END,  str(result1) )
    App=(3.142*(num1/2)*(num1/2)*num2*(8000/1000000000))*1000
    result2=round(App,ndigits=8)
    t4.delete(0, 'end')
    t4.insert(END,  str(result2) )

def BB():
# titanium
    t2.delete(0, 'end')
    num1=float(t1.get())
    num2=float(t3.get())
    off=(3.142*(num1/2)*(num1/2)*num2*(4500/1000000000))
    result1=round(off,ndigits=8)
    t2.insert(END,  str(result1) )
    App=(3.142*(num1/2)*(num1/2)*num2*(4500/1000000000))*1000
    result2=round(App,ndigits=3)
    t4.delete(0, 'end')
    t4.insert(END,  str(result2) )

def CC():
# Aluminium
    t2.delete(0, 'end')
    num1=float(t1.get())
    num2=float(t3.get())
    off=(3.142*(num1/2)*(num1/2)*num2*(2700/1000000000))
    result1=round(off,ndigits=8)
    t2.insert(END,  str(result1) )
    App=(3.142*(num1/2)*(num1/2)*num2*(2700/1000000000))*1000
    result2=round(App,ndigits=3)
    t4.insert(END,  str(result2) )


root = Tk()
var = IntVar()

root.title('Weight Calculator')
#Define the size of window or frame
root.geometry("1000x400")

t1=Entry(bd=3)#dia
t2=Entry(bd=3)#Kgs
t3=Entry(bd=3)#Length
t4=Entry(bd=3)#gram

lbl1=Label(root, text='Enter The Dia')
lbl1.place(x=100, y=120)
t1.place(x=210, y=120)

lbl3=Label(root, text='Enter The Length')
lbl3.place(x=100, y=150)
t3.place(x=210, y=150)

lbl4=Label(root, text='mm')
lbl4.place(x=350, y=150)

lbl5=Label(root, text='mm')
lbl5.place(x=350, y=120)

lbl6=Label(root, text='Kg')
lbl6.place(x=650, y=300)

lbl8=Label(root, text='Grams')
lbl8.place(x=650, y=330)

lbl7= Label(text="Round", fg="Red", font=("Helvetica", 50))
lbl7.place(x=180, y=3)

lbl2=Label(root, text='Result value is')
lbl2.place(x=400, y=300)
t2.place(x=500, y=300)
t4.place(x=500,y=330)


b2=Button(root, text='EXIT',bg='red',command=Close)
b2.place(x=500, y=360)


R1 = Radiobutton(root, text="Stainless Steel", variable=var, value=1,command=AA)
R1.place(x=75,y=180 )

R2 = Radiobutton(root, text="Titanium", variable=var, value=2,command=BB)
R2.place(x=225,y=180 )

R3 = Radiobutton(root, text="Aluminium", variable=var, value=3,command=CC)
R3.place(x=350,y=180 )


#Rectangle

t11=Entry(bd=3)#thickness
t12=Entry(bd=3)#result
t13=Entry(bd=3)#Width
t16=Entry(bd=3)#Length


def DD():
# SS
    t2.delete(0, 'end')
    num1=float(t11.get())
    num2=float(t13.get())
    num3=float(t16.get())
    off=(num1*num2*num3*(8000/1000000000))
    result1=round(off,ndigits=8)
    t2.insert(END,  str(result1) )
    App=(num3*num1*num2*(8000/1000000000))*1000
    result2=round(App,ndigits=3)
    t4.delete(0, 'end')
    t4.insert(END,  str(result2) )


def EE():
# Ti
    t2.delete(0, 'end')
    num1=float(t11.get())
    num2=float(t13.get())
    num3=float(t16.get())
    off=(num1*num2*num3*(4500/1000000000))
    result1=round(off,ndigits=8)
    t2.insert(END,  str(result1) )
    App=(num3*num1*num2*(4500/1000000000))*1000
    result2=round(App,ndigits=3)
    t4.delete(0, 'end')
    t4.insert(END,  str(result2) )


def FF():
# Ti
    t2.delete(0, 'end')
    num1=float(t11.get())
    num2=float(t13.get())
    num3=float(t16.get())
    off=(num1*num2*num3*(2700/1000000000))
    result1=round(off,ndigits=8)
    t2.insert(END,  str(result1) )
    App=(num3*num1*num2*(2700/1000000000))*1000
    result2=round(App,ndigits=3)
    t4.delete(0, 'end')
    t4.insert(END,  str(result2) )







lbl17= Label(text="Rectangle", fg="Red", font=("Helvetica", 45))
lbl17.place(x=580, y=3)

lbl11=Label(root, text='Enter The Thickness')
lbl11.place(x=550, y=120)
t11.place(x=680, y=120)

lbl13=Label(root, text='Enter The Width')
lbl13.place(x=550, y=150)
t13.place(x=680, y=150)

lbl16=Label(root, text='Enter The Length')
lbl16.place(x=550, y=180)
t16.place(x=680, y=180)



lbl14=Label(root, text='mm')
lbl14.place(x=820, y=150)

lbl15=Label(root, text='mm')
lbl15.place(x=820, y=120)

lbl18=Label(root, text='mm')
lbl18.place(x=820, y=180)

R4 = Radiobutton(root, text="Stainless Steel", variable=var, value=4,command=DD)
R4.place(x=500,y=220 )

R5 = Radiobutton(root, text="Titanium", variable=var, value=5,command=EE)
R5.place(x=675,y=220 )

R6 = Radiobutton(root, text="Aluminium", variable=var, value=6,command=FF)
R6.place(x=800,y=220 )




label = Label(root)
#label.pack()
root.mainloop()
