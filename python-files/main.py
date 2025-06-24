import tkinter as tk

window = tk.Tk()
window.title("selam")
window.geometry("300x300")

hello = tk.Label(text="tıklama oyununa hoşgeldin")
hello.pack()
button = tk.Button(text="bana tıkla")
button.pack()
background = tk.Label(text="tıklandığında arka plan rengi değişecek")
background.pack()
def change_color():
        window.config(bg="red")
        background.config(text="renk değişti")
        button.config(text="tekrar tıkla")
        button.config(command=change_color2)
        button.pack()
def change_color2():
        window.config(bg="brown")
        background.config(text="renk değişti")
        button.config(text="tekrar tıkla")
        button.config(command=change_color)
        button.pack() # button.config(command=change_color2)
        # button.pack()
button.config(command=change_color)
button.pack()
tk.mainloop()