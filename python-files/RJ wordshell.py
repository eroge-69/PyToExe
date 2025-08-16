from tkinter import *
from tkinter import filedialog

root=Tk()
root.geometry("600x600")
root.title("RJ wordshell")
root.config(bg='black')
root.resizable(False,False)

def save_file():
    open_file=filedialog.asksaveasfile(mode='w',defaultextension='.txt')
    if open_file is None:
        return
    Text=str(Entry.get(1.0,END))
    open_file.write(Text)
    open_file.close()

def open_file():
        file=filedialog.askopenfile(mode='r',filetype=[('text files','*.txt')])
        if file is not None:
            content=file.read()
            Entry.insert(INSERT,content)

b1=Button(root,width='20',height='2',bg='#fff',text='save file',command=save_file).place(x=100,y=8)
b1=Button(root,width='20',height='2',bg='#fff',text='open file',command=open_file).place(x=350,y=8)

Entry=Text(root,width='75',height='144',wrap=WORD)
Entry.place(x=10,y=60)

root.mainloop()
