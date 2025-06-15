from tkinter import *
from tkinter import messagebox
tk = Tk()
tk.title('Авторизация')
tk.geometry('500x500')
tk.resizable(False, False)

def New_window():
    tk.destroy()
    Nw = Tk()
    Nw.title('...')
    Nw.attributes('-fullscreen', True)
    Nw.resizable(False, False, **('width', 'height'))
    make_logo(Nw)
    Label(Nw, 'Я люблю Аню...', 'pink', ('Comic Sans MS', 20, 'bold'), **('text', 'bg', 'font')).place(900, 500, **('x', 'y'))
    Label(Nw, 'Но не могу об этом сказать...', 'pink', ('Comic Sans MS', 20, 'bold'), **('text', 'bg', 'font')).place(800, 600, **('x', 'y'))


def make_logo(t):
    img = PhotoImage('thumb-1920-174837.png', **('file',))
    lbl_img = Label(t)
    lbl_img.image = img
    lbl_img['image'] = lbl_img.image
    lbl_img.place(-2, -2, **('x', 'y'))


def buttn_click():
    l = Login.get()
    p = Password.get()
    if l == 'anned0' and p == 'Dior':
        messagebox.showinfo('Authorization', 'Authorization completed', **('title', 'message'))
        New_window()
        return None
    None.showinfo('Authorization', 'Invalid login or password', **('title', 'message'))
    login.delete(0, END)
    password.delete(0, END)


def make_label(text):
    return Label(text, ('Comic Sans MS', 24, 'bold'), **('text', 'font'))

make_label('Login').place(50, 150, **('x', 'y'))
make_label('Password').place(50, 250, **('x', 'y'))
Login = StringVar()
Password = StringVar()
login = Entry(('Comic Sans MS', 20, 'bold'), '15', Login, **('font', 'width', 'textvariable'))
password = Entry(('Comic Sans MS', 20, 'bold'), 15, Password, '*', **('font', 'width', 'textvariable', 'show'))
login.get()
password.get()
login.place(200, 150, **('x', 'y'))
password.place(200, 250, **('x', 'y'))
btn = Button('Войти', buttn_click, 15, 1, 'cyan', ('Comic Sans MS', 20, 'bold'), **('text', 'command', 'width', 'height', 'bg', 'font')).place(130, 350, **('x', 'y'))
mainloop()