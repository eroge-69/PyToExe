from tkinter import *
from tkinter import ttk
import random 

root = Tk()
root.geometry("500x500")
root.title("Устный счёт генератор")
root.resizable(False,False)

slojnost = ["+", "+ -", "+ - *", "+ - * /"]

slojnostN = 0
kolPr = 0
kolDey = 0
nmbDo = 0

def regen():
    global slojnost
    global kolPr
    global kolDey
    global nmbDo
    if hardCombobox.get() == "+":
        slojnost = 1
    elif hardCombobox.get() == "+ -":
        slojnost = 2
    elif hardCombobox.get() == "+ - * /":
        slojnost = 3
    elif hardCombobox.get() == "+ - * /":
        slojnost = 4
    kolPr = int(howManyEntry.get())
    kolDey = int(howManyDeyEntry.get())
    nmbDo = int(howManyNmbEntry.get())

    for i in range(kolPr):
        for x in range(kolDey):
            if x != kolDey-1:
                dey = random.randint(1,slojnost+1)
                if dey == 1:
                    deyStr = "+"
                elif dey == 2:
                    deyStr = "-"
                elif dey == 3:
                    deyStr = "*"
                elif dey == 4:
                    deyStr = "/"
            if nmbDo >= 50 and dey == 3:
                rndNmb = random.randint(1,nmbDo//10)
            else:
                rndNmb = random.randint(1,nmbDo)
            if x == kolDey-1:
                print(str(rndNmb),end='\n')
            else:
                print(str(rndNmb),end='')
            if x != kolDey-1:
                print(deyStr,end='')

#config
howManyEntry = ttk.Entry(justify="center",width=5)
howManyLabel = ttk.Label(justify="center",text="Кол-во примеров")

howManyDeyEntry = ttk.Entry(justify="center",width=5)
howManyDeyLabel = ttk.Label(justify="center",text="Кол-во действий")

howManyNmbEntry = ttk.Entry(justify="center",width=5)
howManyNmbLabel = ttk.Label(justify="center",text="Числа до")

hardCombobox = ttk.Combobox(justify="center",values=slojnost,width=8)
hardLabel = ttk.Label(justify="center",text="Сложность")

regenBtn = ttk.Button(text="Сгенерировать!",command=regen)

#place
howManyEntry.place(x=50,y=250)
howManyLabel.place(x=15,y=230)

howManyDeyEntry.place(x=160,y=250)
howManyDeyLabel.place(x=125,y=230)

howManyNmbEntry.place(x=105,y=290)
howManyNmbLabel.place(x=95,y=270)

hardCombobox.place(x=250,y=250)
hardLabel.place(x=250,y=230)

regenBtn.place(x=180,y=300)
