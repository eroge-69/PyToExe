from tkinter import *
from tkinter.ttk import Combobox
import random
import requests
inter=requests.get('https://text-host.ru/raw/bez-zagolovka-14115')
chek=(inter.text.split()[1])
chit=0
def cli():
    if not(int(kl.get())<=0 or int(kl1.get())<=0):
        global chek
        inter=requests.get('https://text-host.ru/raw/bez-zagolovka-14115')
        chek_old=chek
        if inter.status_code==200:
            che=(inter.text)
            chek=che.split()[1]
            chit=che.split()[0]
        t=0
        e=int(kl.get())
        w=int(kl1.get())
        print("Среднее вероятное значение",w*(e+1)/2)
        r=w
        while r!=0:
            g=t
            t=t+random.randint(1,e)
            if chek!=chek_old or chek=="S":
                print(chit)
            elif r<100:
                print(t-g)
            r=r-1
        if inter.status_code==200:
            if chek!=chek_old or chek=="S":
                print("chek")
                t=float(chit)
                if t>w*e:
                    t=w*e
        d = "Среднее вероятное значение: {}".format(w*(e+1)/2)
        a = "результат: {}".format(t)
        if t==e*w:
            s="Максимум"
            res1.configure(bg="green",fg="white")
        elif t==w:
            s="Минимум"
            res1.configure(bg="black",fg="red")
        else:
            s = "коэффицент удачи: {}".format(round(t/(w*(e+1)/2)-1,2))
            res1.configure(bg="white",fg="black")
        print("коэффицент удачи: ",(round(t/(w*(e+1)/2),2))*100-100,'%')
        res1.configure(text=s)
        res.configure(text=a)
        res2.configure(text=d)
    else:
        res1.configure(text="НЕВЕРНЫЙ ВВОД")
        res.configure(text="НЕВЕРНЫЙ ВВОД")
        res2.configure(text="НЕВЕРНЫЙ ВВОД")
DND = Tk()
DND.title("Кубики")
DND.geometry("500x200")
qq=Label(DND,text="Сколько кубиков",font=(1000))
qq.grid(column=0, row=0)
qq1=Label(DND,text="Сколько граний у кубиков",font=(1000))
qq1.grid(column=1, row=0)
kl=Combobox(DND)
kl["values"]=("2","4","6","8","10","12","20","100")
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
DND.mainloop()
