from tkinter import *
root = Tk()
root.title('Вычисление объема молочной железы (аугментационной маммопластика)')

# первая метка в строке 0, столбце 0 (0 по умолчанию)
# парамет sticky  означает выравнивание. W, E,N,S — запад, восток, север, юг
Label(root, text='H - проекция высоты МЖ, см').grid(row=0, sticky=W)

# вторая метка в строке 1
Label(root, text='А - проекция, см').grid(row=1, sticky=W)
# третья метка в строке 2
Label(root, text='В - проекция, см').grid(row=2, sticky=W)

# создаем виджеты текстовых полей
EntryA = Entry(root, width=10, font='Arial 16')
EntryB = Entry(root, width=10, font='Arial 16')
EntryC = Entry(root, width=10, font='Arial 16')
EntryD = Entry(root, width=30, font='Arial 16')

# размещаем первые два поля справа от меток, второй столбец (отсчет от нуля)
EntryA.grid(row=0, column=1, sticky=E)
EntryB.grid(row=1, column=1, sticky=E)
EntryC.grid(row=2, column=1, sticky=E)
# третье текстовое поле ввода занимает всю ширину строки 2
# columnspan — объединение ячеек по столбцам; rowspan — по строкам
EntryD.grid(row=4, columnspan=3)

def VolBefore():
    h = EntryA.get() # берем текст из первого поля
    h = int(h) # преобразуем в число целого типа

    a = EntryB.get() 
    a = int(a)

    b = EntryB.get() 
    b = int(b)

    result = str(1/12*a*b*h*3.14) # результат переведем в строку для дальнейшего вывода
    EntryD.delete(0, END) # очищаем текстовое поле полностью
    EntryD.insert(0, result) # вставляем результат в начало 

# размещаем кнопку в строке 4 во втором столбце 
but = Button(root, text='Вычислить объем',command=VolBefore)
but.grid(row=3, column=1, sticky=E)

root.mainloop()