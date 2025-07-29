from tkinter import *
from pytube import YouTube

root = Tk()
root.geometry( '550x300')
root.resizable(0, 0)
root.title('DILE NO A LA PIRATERÍA, DESCARGA DE MANERA 100% LEGAL')
root.configure(bg='#AACDE2')

Label(root, text='Descarga tus videos y disfruta 💪',
      font='arial 20 bold', bg='#AACDE2').place(x=50, y=50)

link = StringVar()
Label(root, text='Pásame el link aquí, porfa', font='arial 12',
      bg='#AACDE2').place(x=190, y=100)
link_enter = Entry(root, width=70,
                   textvariable=link).place(x=60, y=150)

def Downloader():
    url =YouTube(str(link.get()))
    video = url.streams.get_highest_resolution()
    video.download()
    Label(root, text='PIRATEADO CON ÉXITO🤐', font='arial 32 bold',
          bg='#AACDE2', fg='#857199').place(x=0, y=200)

Button(root, text='DESCARGAR 😎', font='arial 20 bold italic',
       bg='#857199', padx=2,
       command=Downloader).place(x=150, y=200)

root.mainloop()