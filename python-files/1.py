from tkinter import *  
from tkinter import messagebox
import time as t
  
def clicked():  
    messagebox.showinfo('не жми куда попало', 'и зачем?')
    messagebox.showinfo('и вот что ты будешь делать?','и вот что ты будешь делать?')
    messagebox.showinfo('было только 1 задание', 'было только 1 задание')
    messagebox.showinfo('и ты с ним не справился','и ты с ним не справился')
    messagebox.showinfo('с 1 заданием', 'с 1 заданием')
    messagebox.showinfo('тебе сказали не нажимать на что попало','тебе сказали не нажимать на что попало')
    messagebox.showinfo( 'а ты что сделал?', 'а ты что сделал?')
    messagebox.showinfo( 'а уже поздно', 'а уже поздно')
    t.sleep(20)

  
window = Tk()
window.title("не нажимай")
window.title("Добро пожаловать в приложение PythonRu")  
window.geometry('1900x1050')  
btn = Button(window, text='Клик', command=clicked)  
btn.grid(column=10, row=10)  
window.mainloop()
