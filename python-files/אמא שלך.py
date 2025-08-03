import tkinter as tk

root = tk.Tk()

bg = '#04000f'

site = tk.Label(root,text='https: / / xeno.onl',fg='white',bg=bg,font=('Arial black',8))
site.place(x=180,y=17)

version = tk.Label(root,text='v1.2.45',fg='#387fd2',bg=bg,font=('Segoe UI', 13))
version.place(x=120,y=13)

xenolabel = tk.Label(root,text='Xeno',fg='white',bg=bg,font=('Arial Black',16))
xenolabel.place(x=57,y=9)

xenosymbol = tk.Label(root,text='🪐',fg='white',bg=bg,font=('courier new',40))
xenosymbol.place(x=0,y=-5)

frame = tk.Frame(width=99999,bg='white')
frame.place(x=0,y=50)


Xbtn = tk.Button(root,text='X',fg='white',bg=bg,bd=0,font=('courier', 21))
Xbtn.place(x=640)

maxbtn = tk.Button(root,text='🗖',fg='white',bg=bg,bd=0,font=('courier', 21))
maxbtn.place(x=600,y=-2)

Minibtn = tk.Button(root,height=-1,text='ˍ',fg='white',bg=bg,bd=0,font=('courier', 30))
Minibtn.place(x=550,y=-23)

maintextbox = tk.Text(root,width=100,height=16,bg=bg,fg='white',bd=0,selectbackground='#1919FF',font=('arial black',10))
maintextbox.place(x=0,y=52)

icon1 = tk.Button(root,text='⚙',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon1.place(x=0,y=360)

icon2 = tk.Button(root,text='📁',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon2.place(x=39,y=360)

icon3 = tk.Button(root,text='💾',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon3.place(x=81,y=360)

icon4 = tk.Button(root,text='⌫',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon4.place(x=121,y=360)

icon5 = tk.Button(root,text='🔗',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon5.place(x=520,y=360)

icon6 = tk.Button(root,text='📃',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon6.place(x=562,y=360)

icon7 = tk.Button(root,text='💻',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon7.place(x=605,y=360)

icon8 = tk.Button(root,text='▷',bd=0,fg='white',bg=bg,font=('arial black', 15))
icon8.place(x=650,y=360)

frame2 = tk.Frame(width=99999,bg='white')
frame2.place(x=0,y=350)

root.title('xeno python remake😂')

root.geometry('685x410')

root.config(bg='#04000f')

root.resizable(False,False)

root.mainloop()
