import tkinter as tk
root = tk.Tk()

def open1():
    root1 = tk.Toplevel(root)
    tk.Label(root1, text="سیمکارت مورد نظر خود را بنویسید").pack()
    tk.Label(root1,text="ایرانسل").pack()
    tk.Label(root1,text="همراه اول").pack()
    tk.Label(root1,text="رایتل").pack()
    tk.Entry(root1).pack()
    tk.Button(root1,text="click").pack()



tk.Label(root,text="سلام دوست عزیز").pack()
tk.Label(root,text="لطفا به سوالات زیر پاسخ بده").pack()
tk.Label(text="نام").pack()
tk. Entry().pack()
tk.Label(text="نام خانوادگی").pack()
tk.Entry().pack()
tk.Label(text="سال تولد").pack()
tk.Entry().pack()
tk.Label(text="ماه تولد").pack()
tk.Entry().pack()
tk.Label(text="روز تولد").pack()
tk.Entry().pack()
tk.Label(text="کد ملی").pack()
tk.Entry().pack()
tk.Label(text="زاده").pack()
tk.Entry().pack()
tk.Label(text="محل سکونت").pack()
tk.Entry().pack()
tk.Button(text="click",command=open1 ).pack()
root.mainloop()


