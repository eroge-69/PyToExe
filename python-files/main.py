import requests
from tkinter import *
from tkinter import messagebox
from tkinter import Tk

def clicked1():
     response = requests.get('http://admin:admin@192.168.100.249/protect/rb0s.cgi')
     if response.status_code == 200:
       messagebox.showinfo('Кирочная', 'ворота открыты')
     else:
        messagebox.showinfo('Кирочная', 'Ошибка')

# def clicked2():
#      response = requests.get('http://admin:admin@192.168.100.248/protect/rb0s.cgi')
#      if  response.status_code == 200:
#        messagebox.showinfo('Фурштатская', 'ворота открыты')
#      else:
#        messagebox.showinfo('Фурштатская', 'Ошибка')

root = Tk()
root.overrideredirect(1)
root.title("ВОРОТА")
root.lift()
root.attributes('-topmost',True)
root.after_idle(root.attributes,'-topmost',True)
root.geometry('75x30')
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 4
y = 1 #(root.winfo_screenheight() - root.winfo_reqheight()) / 2
root.wm_geometry("+%d+%d" % (x * 3 , y))

btn = Button(root, text="Кирочная", command=clicked1)
btn.grid(column=1, row=0)
# btn = Button(root, text="Фурштатская", command=clicked2)
# btn.grid(column=2, row=0)
root.mainloop()