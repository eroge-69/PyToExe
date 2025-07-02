import time
import tkinter as tk
def a():
    current_time = time.strftime('%H:%M:%S')
    label.config(text=current_time)
    label.after(1000, a)
t = tk.Tk()
t.title('Clock')
t.geometry('250x100')
t.configure(bg='black')
label = tk.Label(t, font=('irancell', 40), bg='black', fg='green')
label.pack()
a()



