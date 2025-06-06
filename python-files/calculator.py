import tkinter as tk

def one():
    
    screen.insert(tk.END,1)
def two():
    x=2
    screen.insert(tk.END,x)
def three():
    x =3
    screen.insert(tk.END,x)
def four():
    x=4
    screen.insert(tk.END,x)
    
def five():
    x=5
    screen.insert(tk.END,x)
def six():
    x=6
    screen.insert(tk.END,x)
def seven():
    x =7
    screen.insert(tk.END,x)
def eight():
    x =8
    screen.insert(tk.END,x)
def night():
    x =9
    screen.insert(tk.END,x)
def zero():
    x=0
    screen.insert(tk.END,x)

def point():
    x="."
    screen.insert(tk.END,x)
def plus():
    x="+"
    screen.insert(tk.END,x)
def minus():
    x="-"
    screen.insert(tk.END,x)
def devide():
    x="/"
    screen.insert(tk.END,x)
def by():
    x="*"
    screen.insert(tk.END,x)        
def de_l_et():
    screen.delete(0,tk.END)

def calc():
    x=str(eval(screen.get()))
    
    screen.delete(0,tk.END)
    screen.insert(0,x)

# fah = (celcius*9/5)+32
#   output_l.delete(0,tk.END)
#    output_l.insert(0,fah)

root =tk.Tk()
root.title("calculator")
screen =tk.Entry(root,)


one_b =tk.Button(root,text="1",
                command=one,
                height=0,
                width=5)
two_b=tk.Button(root,
               text="2",
               command=two,
               height=0
               ,width=5)
three_b =tk.Button(root,
                  text="3",
                  command=three,
                  height=0,
                  width=5)
four_b=tk.Button(root,
                text="4",
                command=four,
                height=0,
                width=5)
five_b=tk.Button(root,
                text="5",
                command=five,
                height=0,
                width=5)
six_b =tk.Button(root,
                text="6",
                command=six,
                height=0,
                width=5)                                                  
seven_b=tk.Button(root,text="7",command=seven,height=0,width=5)
eight_b=tk.Button(root,text="8",command=eight,height=0,width=5)
night_b=tk.Button(root,text='9',command=night,height=0,width=5)
zero_b=tk.Button(root,text="0",command=zero,height=0,width=5)
plus_b=tk.Button(root,text="+",command=plus,height=0,width=5)
point_b=tk.Button(root,text=".",command=point,height=0,width=5)
devide_b=tk.Button(root,text="/",command=devide,height=0,width=5)
by_b=tk.Button(root,text="x",command=by,height=0,width=5)
minus_b=tk.Button(root,text="-",command=minus,height=0,width=5)
calc_b=tk.Button(root,text="=",command=calc,height=0,width=5)
delete_b=tk.Button(root,text="del",command=de_l_et,height=0,width=5)

screen.grid()
one_b.grid(column=1)
four_b.grid(column=1)
seven_b.grid(column=1)
zero_b.grid(column=1)
minus_b.grid(column=1)
two_b.grid(row=1,column=2)
five_b.grid(row=2,column=2)
eight_b.grid(row=3,column=2)
point_b.grid(row=4,column=2)
by_b.grid(row=5,column=2)
three_b.grid(row=1,column=3)
six_b.grid(row=2,column=3)
night_b.grid(row=3,column=3)
plus_b.grid(row=4,column=3)
devide_b.grid(row=5,column=3)
delete_b.grid(row=6,column=2)
calc_b.grid(column=1,row=6)
root.mainloop()