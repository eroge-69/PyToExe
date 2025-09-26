from tkinter import *

def nop():
	print(" ")

tk = Tk()
tk.protocol("WM_DELETE_WINDOW", nop)
tk.title("r")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
can = Canvas(tk, width=180, height=260, bd=0, highlightthickness=0)
can.pack()
our = PhotoImage(file = "pack.png")
our = our.subsample(3,3)
our_label = Label(tk)
our_label.image = our
our_label["image"] = our_label.image
our_label.place(x = 0, y = 0)
tk.mainloop()
