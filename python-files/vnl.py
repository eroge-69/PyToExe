from tkinter import *
from tkinter import ttk

clicks = 0


def click_button():
    global clicks
    clicks += 1
    # изменяем текст на кнопке
    btn["text"] = f"нажатий {clicks}"


root = Tk()
root.title("button")
root.geometry("250x150")

btn = ttk.Button(text="жми", command=click_button)
btn.pack()
root.mainloop()