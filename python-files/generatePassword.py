from tkinter import *
import string
import secrets

root = Tk()
root.geometry('275x275')
root.resizable(0, 0)
root.title("Генератор паролей")
root['bg'] = 'orange'

def password_generate_logic():
    global text
    ALL_SYMBOLS = (
        string.ascii_lowercase +
        string.ascii_uppercase +
        string.digits          +
        string.punctuation
    ) 

    password = ''.join(secrets.choice( ALL_SYMBOLS ) for _ in range(16))
    text = password

    password_label.config(text=password)
def copy_password():
    root2 = Tk()
    root2.withdraw()
    root2.clipboard_clear()
    root2.clipboard_append(text)
    root2.update()
    root2.destroy()
    
password_label = Label(
    root,
    text='',
    bg='orange',
    font=(('Times New Roman'), 20)
)
password_label.place(relx=0.5,
                     anchor='center',
                     y=95)




Button_Generate = Button(
    root,
    text='Генерировать!',
    font=('Helvetica', 12),
    relief='raised',
    bg='gray',
    fg='white',
    activebackground='pink',
    command=password_generate_logic
    )
Button_Generate.place(
    relx=0.5,
    rely=0.5,
  anchor='center'
)

Button_Copy_Password = Button(
    root,
    text='Copy',
    relief='groove',
    bg = 'gray',
    fg='white',
    activebackground='pink',
    command = copy_password
)
Button_Copy_Password.place(rely=0.5, anchor='center', x=225)



root.mainloop()