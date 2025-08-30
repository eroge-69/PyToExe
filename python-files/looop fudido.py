from tkinter import *
from tkinter import ttk, font


i = 0

while i == 0:
 janela = Tk()
 janela.title('Hackeado Otário')
 janela.geometry()
 janela.maxsize(770,140)
 janela.minsize(770,140)
 janela.resizable(False,False)
 janela.config(background="#000000")
 janela.iconbitmap('hacker_118137.ico')


 texto = ttk.Label(
     janela,
     text='Vo Fritar Tudo',
     font=('Comic Sans MS', 80),
     foreground='#0D691A',
     background='#000000'
 )
 texto.pack() 

 janela.mainloop()



