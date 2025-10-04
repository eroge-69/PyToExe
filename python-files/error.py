import tkinter as tk
import random as rand

# Window setup #
resolution_x= 1080/2
resolution_y= 1920/2

root = tk.Tk()
window_width= 300
window_height= 100

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x= (screen_width//2) - (window_width//2)
center_y= (screen_height//2) - (window_height//2)

root.title("My first Project")
root.attributes("-topmost", True)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
label= tk.Label(root, text= "Hello World!", font= ("Arial", 32))
label.pack(pady= 10)


def make_window():
    r= tk.Tk()
    r.title("Virus")
    r.geometry(f"+{rand.randint(0,screen_width-300)}+{rand.randint(0, screen_height-100)}")
    r.tk_setPalette("Red")
    r.attributes("-topmost", True)

    label= tk.Label(r, text= "ERROR", font= ("Didot", 50))
    label.pack()

    r.protocol("WM_DELETE_WINDOW", make_window)
    r.mainloop()
    

root.protocol("WM_DELETE_WINDOW", make_window)
root.mainloop()