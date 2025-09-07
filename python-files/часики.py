import time
from tkinter import Tk, Label, StringVar

def update_time():
    current_time = time.strftime('%H:%M:%S')
    time_var.set(current_time)
    root.after(1000, update_time)

root = Tk()
root.title("Часы")
time_var = StringVar()

label = Label(root, textvariable=time_var, font=('Arial', 80),
             bg='black', fg='lime').pack(padx=20, pady=20)

update_time()
root.mainloop()