from tkinter import*
from tkinter import PhotoImage

root=Tk()
root.title("Calculator")
root.geometry('350x600')

background_image = PhotoImage(file="C:\\Users\\my pc\\Desktop\\calculater\\1.png")
background_label = Label(root, image=background_image)
background_label.image = background_image
background_label.place(x=0, y=0, relwidth=1, relheight=1)


def  btnclick(num):
    global operator
    operator=operator + str(num)
    _input.set(operator)

def clear():
    global operator
    operator=""
    _input.set("")

def answer():
    global operator
    ans=str(eval(operator))
    _input.set(ans)
    operator = ""

label=Label(root,font=('ariel' ,20,'bold'),text='Calculator',bg='grey',fg='black')
label.grid(columnspan=4)

_input=StringVar()
operator=""

display = Entry(root,font=('ariel' ,20,'bold'), textvariable=_input ,insertwidth=7 , bd=5 ,bg="white",justify='right')
display.grid(columnspan=4)

#------------------Row-1-------------------------------------------------------------------------------------------------------

b7=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="7",bg="grey", command=lambda: btnclick(7) )
b7.grid(row=2,column=0)

b8=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="8",bg="grey", command=lambda: btnclick(8) )
b8.grid(row=2,column=1)

b9=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="9",bg="grey", command=lambda: btnclick(9) )
b9.grid(row=2,column=2)

Add=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="+",bg="grey", command=lambda: btnclick("+") )
Add.grid(row=2,column=3)

#----------------Row-2---------------------------------------------------------------------------------------------------------------

b4=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="4",bg="grey", command=lambda: btnclick(4) )
b4.grid(row=3,column=0)

b5=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="5",bg="grey", command=lambda: btnclick(5) )
b5.grid(row=3,column=1)

b6=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="6",bg="grey", command=lambda: btnclick(6) )
b6.grid(row=3,column=2)

Sub=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text=" -",bg="grey", command=lambda: btnclick("-") )
Sub.grid(row=3,column=3)

#-------------Row-3------------------------------------------------------------------------------------------------------------------

b1=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="1",bg="grey", command=lambda: btnclick(1) )
b1.grid(row=4,column=0)

b2=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="2",bg="grey", command=lambda: btnclick(2) )
b2.grid(row=4,column=1)

b3=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="3",bg="grey", command=lambda: btnclick(3) )
b3.grid(row=4,column=2)

mul=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text=" *",bg="grey", command=lambda: btnclick("*") )
mul.grid(row=4,column=3)

#-----------------Row-4--------------------------------------------------------------------------------------------------------

b0=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="0",bg="grey", command=lambda: btnclick(0) )
b0.grid(row=5,column=0)

bc=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text="c",bg="grey", command=clear)
bc.grid(row=5,column=1)

Decimal=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text=" .",bg="grey", command=lambda: btnclick(".") )
Decimal.grid(row=5,column=2)

Div=Button(root,padx=16,pady=16,bd=4, fg="black", font=('ariel', 20 ,'bold'),text=" /",bg="grey", command=lambda: btnclick("/") )
Div.grid(row=5,column=3) 
#-----------------Row-6------------------------------------------------------------------------------------------------------------------

bequal=Button(root,padx=16,pady=16,bd=4,width = 16, fg="black", font=('ariel', 20 ,'bold'),text="=",bg="grey",command=answer)
bequal.grid(columnspan=4)


l5=Label(root,text="Yuvaraj",font=("Arial",15,'bold'))
l5.grid()
root.mainloop()