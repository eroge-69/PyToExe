from tkinter import *

window = Tk()
window.title("калькулятор")
window.geometry('500x600+700+100')

def input_into_entry(symbol):
    entry.insert(50,symbol)

def clear():
    entry.delete(0,END)

def clear1():
    entry.delete(0,1)

def count_result():
    text = entry.get()
    result = 0
   
    if '+' in text:
        splitted_text = text.split('+')
        first = float(splitted_text[0])
        second = float(splitted_text[1])
        result = first + second
       
    if '-' in text:
        splitted_text = text.split('-')
        first = float(splitted_text[0])
        second = float(splitted_text[1])
        result = first - second    
    if ':' in text:
        splitted_text = text.split(':')
        first = float(splitted_text[0])
        second = float(splitted_text[1])
        result = first / second 
    if 'x' in text:
        splitted_text = text.split('x')
        first = float(splitted_text[0])
        second = float(splitted_text[1])
        result = first * second
    clear()     
    entry.insert(0, result)





entry = Entry(window, width = 25,  font = ('', 26))
entry.place(x = 5, y = 40)

btn1 = Button(window, bg='grey', fg='blue', text = '1', font=('', 40), command = lambda:input_into_entry('1'))
btn1.place(x=30, y=100, width=110, height=100)

btn2 = Button(window, bg='grey', fg='blue', text = '2',font=('', 40), command = lambda:input_into_entry('2'))
btn2.place(x=140, y=100, width=110, height=100)

btn3 = Button(window, bg='grey', fg='blue', text = '3',font=('', 40), command = lambda:input_into_entry('3'))
btn3.place(x=250, y=100, width=110, height=100)

btn4 = Button(window, bg='grey', fg='blue', text = '4',font=('', 40), command = lambda:input_into_entry('4'))
btn4.place(x=30, y=200, width=110, height=100)

btn5 = Button(window, bg='grey', fg='blue', text = '5',font=('', 40), command = lambda:input_into_entry('5'))
btn5.place(x=140, y=200, width=110, height=100)

btn6 = Button(window, bg='grey', fg='blue', text = '6',font=('', 40), command = lambda:input_into_entry('6'))
btn6.place(x=250, y=200, width=110, height=100)

btn7 = Button(window, bg='grey', fg='blue', text = '7',font=('', 40), command = lambda:input_into_entry('7'))
btn7.place(x=30, y=300, width=110, height=100)

btn8 = Button(window, bg='grey', fg='blue', text = '8',font=('', 40), command = lambda:input_into_entry('8'))
btn8.place(x=140, y=300, width=110, height=100)

btn9 = Button(window, bg='grey', fg='blue', text = '9',font=('', 40), command = lambda:input_into_entry('9'))
btn9.place(x=250, y=300, width=110, height=100)

btn0 = Button(window, bg='grey', fg='blue', text = '0',font=('', 40), command = lambda:input_into_entry('0'))
btn0.place(x=140, y=400, width=110, height=100)

btnCE= Button(window, bg='grey', fg='black', text = 'CE',font=('', 20), command = clear)
btnCE.place(x=30, y=400, width=55, height=100)

btnR = Button(window, bg='grey', fg='black', text = '=',font=('', 40), command = count_result)
btnR.place(x=250, y=400, width=110, height=100)

btnD = Button(window, bg='grey', fg='black', text = ':',font=('', 40), command = lambda:input_into_entry(':'))
btnD.place(x=360, y=400, width=110, height=100)

btnU = Button(window, bg='grey', fg='black', text = 'x',font=('', 40), command = lambda:input_into_entry('x'))
btnU.place(x=360, y=300, width=110, height=100)

btnP = Button(window, bg='grey', fg='black', text = '+',font=('', 40), command = lambda:input_into_entry('+'))
btnP.place(x=360, y=100, width=110, height=100)

btnM = Button(window, bg='grey', fg='black', text = '-',font=('', 40), command = lambda:input_into_entry('-'))
btnM.place(x=360, y=200, width=110, height=100)

btnS = Button(window, bg='grey', fg='black', text = 'C',font=('', 20), command = clear1)
btnS.place(x=85, y=400, width=55, height=100)

window.mainloop()