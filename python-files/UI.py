from tkinter import *

def msgShow():
    label["text"]="I love Python"
    label["bg"]="lightyellow"
    label["fg"]="blue"
    label["width"]=30
    
window=Tk()
window.title("ch18_12")
window.geometry("300x150")
label=Label(window)
btn=Button(window, text="Message", command=msgShow)

label.pack()
btn.pack()

window.mainloop()