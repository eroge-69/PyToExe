from tkinter import *
import random
def cli():
    t=0
    e=int(kl.get())
    w=int(kl1.get())
    print("Среднее вероятное значение",w*e/2)
    r=w
    while r!=0:
        t=t+random.randint(1,e)
        print(t)
        r=r-1
    d = "Среднее вероятное значение: {}".format(w*e/2)
    a = "результат: {}".format(t)
    s = "коэффицент удачи: {}".format(round(t/(w*e/2)-1,2))
    print("коэффицент удачи: ",(round(t/(w*e/2),2))*100-100,'%')
    res1.configure(text=s)
    res.configure(text=a)
    res2.configure(text=d)
DND = Tk()
DND.title("DnD кидалка кубиков")
DND.geometry("500x400")
qq=Label(DND,text="Сколько кубиков",font=(1000))
qq.grid(column=0, row=0)
qq1=Label(DND,text="Какие кубики",font=(1000))
qq1.grid(column=1, row=0)
kl=Entry(DND,width=10)
kl.grid(column=1, row=1)
kl1=Entry(DND,width=10)
kl1.grid(column=0, row=1)
kid = Button(DND, text="Кинуть",command=cli)  
kid.grid(column=2, row=1)
res2=Label(DND,text="",font=(1000))
res2.grid(column=0,row=2)
res=Label(DND,text="",font=(1000))
res.grid(column=0,row=3)
res1=Label(DND,text="",font=(1000))
res1.grid(column=0,row=4)
