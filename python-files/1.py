from tkinter import *  
from tkinter import messagebox  
  
  
def clicked():  
    messagebox.showinfo('Заголовок', 'и зачем?')  
  
  
window = Tk()  
window.title("Добро пожаловать в приложение PythonRu")  
window.geometry('10x30')  
btn = Button(window, text='Клик', command=clicked)  
btn.grid(column=0, row=0)  
window.mainloop()
