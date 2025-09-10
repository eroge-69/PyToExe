r=0.0225
a=0.172
R=0.04
p=0.0021
C=706.90

from tkinter import *
root = Tk()#создать окно
root.title("Калькулятор")#задать название
root.geometry('520x400')#установка размера
My_label = Label(root, text ='Калькулятор', font = ('Times New Roman', 16, 'bold'))#текст ячейки и его параметры
My_label.place(x=180, y=10)#задать каординаты ячейки


My_label = Label(root, text ='Длительность импульса', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=300, y=35)
T= Entry(width=15, bd=5, justify="center")#задать поле условия
T.place(x=300, y=60)

My_label = Label(root, text ='Напряжение с ТПИ', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=300, y=105)
U= Entry(width=15, bd=5, justify="center")#задать поле условия
U.place(x=300, y=130)

My_label = Label(root, text ='Радиус пятна на цели', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=300, y=175)
R1= Entry(width=15, bd=5, justify="center")#задать поле условия
R1.place(x=300, y=200)



My_label = Label(root, text ='Энергия', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=40, y=35)
Energia=Entry(root, width=20, justify="center", bd=3)#задать поле ответа энергии
Energia.place(x=40, y=60)

My_label = Label(root, text ='Мощность', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=40, y=90)
Power=Entry(root, width=20, justify="center", bd=3)#задать поле ответа мощности
Power.place(x=40, y=115)

My_label = Label(root, text ='Плотность нергии на выходе', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=40, y=145)
Znacenie1=Entry(root, width=20, justify="center", bd=3)#задать поле ответа плотность энергии на выходе лазера
Znacenie1.place(x=40, y=170)

My_label = Label(root, text ='Плотность энергии на цели', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=40, y=200)
Znacenie2=Entry(root, width=20, justify="center", bd=3)#задать поле ответа плотность энергии на цели
Znacenie2.place(x=40, y=225)

My_label = Label(root, text ='Плотность мощности на выходе', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=40, y=255)
Znacenie3=Entry(root, width=20, justify="center", bd=3)#задать поле ответаплотность мощности на выходе лазера 
Znacenie3.place(x=40, y=280)

My_label = Label(root, text ='Плотность мощности на цели', font = ('GOST type B', 12, 'bold'))#текст ячейки и его параметры
My_label.place(x=40, y=310)
Znacenie4=Entry(root, width=20, justify="center", bd=3)#задать поле ответаплотность мощности на цели
Znacenie4.place(x=40, y=335)

def raschet(T,U,R1):
	T=float(T)
	U=float(U)

	if R1=='':
		R1=1

	R1=float(R1)
	K=a*p*C
	S=3.14*r**2 #площадь лазерного изл.
	T=T/1000
	S1=3.14*R1**2/100 #площадь лазерного изл. на цели

	Tk1=U/4.73 #конечная температура ТПИ

	E12=(Tk1*K*T*3.14**0.5)/(2*(1-R)*S*(a*T)**0.5)
	E11=(Tk1*K*T)/((1-R)*r*S)
	E1=(E12+E11)/2

	E1=100*E1/9-E1 #энергия на выходе
	QE=E1/S #плотность энергии на выходе лазера
	QE1=E1/S1 # плотность энергии на цели
	P=E1/T/1000 # мощьность
	QP=1#лотность энерии на выходе лазера
	QP1=P/S1 # плотность мощности на цели
	
	return [E1,P,QE,QE1,QP,QP1]

def button_click():
	Energia.delete(0, END)
	Power.delete(0, END)
	Znacenie1.delete(0, END)
	Znacenie2.delete(0, END)
	Znacenie3.delete(0, END)
	Znacenie4.delete(0, END)
	Raschet=raschet(T.get(),U.get(),R1.get())
	Energia.insert(0, Raschet[0])
	Power.insert(0, Raschet[1])
	Znacenie1.insert(0, Raschet[2])
	Znacenie2.insert(0, Raschet[3])
	Znacenie3.insert(0, Raschet[4])
	Znacenie4.insert(0, Raschet[5])

button=Button(width=15, bd=7, bg="green", command=button_click, text ="Расчитать")
button.place(x=300, y=335)

#root.mainloop()