
from tkinter import *
import webbrowser

root = Tk()
root.title('Free vbucks')
root.geometry('500x500')

new = 1
url = "https://freethevbucks.com/"

def openweb():
    webbrowser.open(url,new=new)

Btn = Button(root, text = "free vbucks",command=openweb)
Btn.pack()

root.mainloop()