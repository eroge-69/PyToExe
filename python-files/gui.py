import tkinter as tk
from tkinter import ttk

def yes():
    new_window = tk.Toplevel()
    new_window.title("yes")
    new_window.geometry("300x200")
    label = tk.Label(new_window, text="good!", font='Calibri 40 bold' )
    label.pack(pady=20)

def no():
    new_window = tk.Toplevel()
    new_window.title("no")
    new_window.geometry("300x200")
    label = tk.Label(new_window, text="lies!", font='Calibri 60 bold' )
    label.pack(pady=20)

window = tk.Tk()
window.title('question')
window.geometry('450x150')
title_label = ttk.Label(master=window, text='did this work?', font= 'Calibri 40 bold' )
title_label.pack()

button = ttk.Button(master = window, text = 'yes', command = yes)
button2 = ttk.Button(master = window, text = 'no', command= no)

button.pack(side = 'right', padx=40)
button2.pack(side = 'left', padx= 40)



window.mainloop()