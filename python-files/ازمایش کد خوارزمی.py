from tkinter import*

import math

import tkinter as tk
qqq = None

def open_window_2_buttons():
    global www, qqq
    if qqq is not None:
        try:
            qqq.destroy()
        except:
            pass
    
    www = Tk()
    www.title("mashin")
    
    label = Label(www, text="mashin hesab mahmoly ya mashin hesab furmoly")
    label.grid(row=0, column=0)

    dokbargasht = Button(www, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='barghasht', command=bargashtmeno)
    dokbargasht.grid(row=1, column=2)

    dokmashinh = Button(www, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='mashin hesab mahmoly', command=mashinb).grid(row=1, column=0)

    dokmashinf = Button(www, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='mashin hesab furmoly', command=lambda:wsw(1) ).grid(row=1, column=1)

    www.mainloop()





def open_window_8_buttons():
    global ali
    qqq.destroy()
    
    mmm = Tk()
    mmm.title("yadgiry")

    frame = Frame(mmm)

    frame.pack()
    

    label = Label(frame, text="mab hasi ke mi khahid darbare an tozih dade shavad ra nam bebarid:+ or * or - or / or --:").grid(row=0, column=0)


    dokmos = Button(frame, padx=8, pady=8, bd=8, fg='black', font=('arial', 20, 'bold'), text='mosbat', command=lambda:wsw(0) ).grid(row=1, column=0, sticky="nsew")

    dokmanf = Button(frame, padx=8, pady=8, bd=8, fg='black', font=('arial', 20, 'bold'), text='manfy', command=lambda:wsw(1) ).grid(row=1, column=1, sticky="nsew")
    
    doktagh = Button(frame, padx=8, pady=8, bd=8, fg='black', font=('arial', 20, 'bold'), text='taghsim', command=lambda:wsw(0) ).grid(row=2, column=0, sticky="nsew")

    dokzarb = Button(frame, padx=8, pady=8, bd=8, fg='black', font=('arial', 20, 'bold'), text='zarb', command=lambda:wsw(1) ).grid(row=2, column=1, sticky="nsew")

    doktaghir = Button(frame, padx=8, pady=8, bd=8, fg='black', font=('arial', 20, 'bold'), text='zarb', command=lambda:wsw(1) ).grid(row=3, column=0, sticky="nsew")

    mmm.mainloop()


from tkinter import *

# متغیرها و تم‌ها
is_dark = False

light_theme = {
    "bg": "white",
    "fg": "black",
    "button_bg": "lightgray"
}

dark_theme = {
    "bg": "#2e2e2e",
    "fg": "white",
    "button_bg": "#444444"
}

# تابع تغییر مود
def toggle_theme():
    global is_dark
    is_dark = not is_dark
    #toggle_theme()
    try:
        apply_theme()         # روی qqq
        apply_theme_to_window(www)   # اگه فعال بود
        apply_theme_to_window(tree)
    except:
        pass
          


# تابع اعمال تم
def apply_theme():
    theme = dark_theme if is_dark else light_theme
    try:
        qqq.configure(bg=theme["bg"])
    except:
        pass

    for widget in qqq.winfo_children():
        if isinstance(widget, Button):
            widget.configure(bg=theme["button_bg"], fg=theme["fg"])
        elif isinstance(widget, Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, Entry):
            widget.configure(bg=theme["bg"], fg=theme["fg"])






def apply_theme_to_window(window):
    theme = dark_theme if is_dark else light_theme
    try:
        window.configure(bg=theme["bg"])
    except:
        pass

    for widget in window.winfo_children():
        try:
            widget.configure(bg=theme["button_bg"], fg=theme["fg"])
        except:
            pass











def mashinb():
    global tree, operator, hg, nemayesh

    www.destroy()



    tree = Tk()
    tree.title("mashin hesab")       
    operator = ""
    hg = StringVar(tree)
    nemayesh = Entry(tree, font=('arial', 20, 'bold'), textvariable=hg, bd=30, insertwidth=4, bg="powder blue", justify='right')
    nemayesh.grid(columnspan=4)






    dok0 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='0', command=lambda:btnClick(0) ).grid(row=4, column=1)

    dok1 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='1', command=lambda:btnClick(1) ).grid(row=3, column=0)

    dok2 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='2', command=lambda:btnClick(2) ).grid(row=3, column=1)

    dok3 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='3', command=lambda:btnClick(3) ).grid(row=3, column=2)

    dok4 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='4', command=lambda:btnClick(4) ).grid(row=2, column=0)

    dok5 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='5', command=lambda:btnClick(5) ).grid(row=2, column=1)

    dok6 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='6', command=lambda:btnClick(6) ).grid(row=2, column=2)

    dok7 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='7', command=lambda:btnClick(7) ).grid(row=1, column=0)

    dok8 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='8', command=lambda:btnClick(8) ).grid(row=1, column=1)

    dok9 = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='9', command=lambda:btnClick(9) ).grid(row=1, column=2)

    dokplu = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='+', command=lambda:btnClick("+") ).grid(row=2, column=3)

    dokman = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='-', command=lambda:btnClick("-") ).grid(row=3, column=3)

    dokmos = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='=', command=btnEqualsInput).grid(row=4, column=3)

    dokc = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='c', command=btnClearDisplay).grid(row=1, column=3)

    dokzarb = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='*', command=lambda:btnClick("*") ).grid(row=4, column=0)

    doktagh = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='/', command=lambda:btnClick("/") ).grid(row=4, column=2)

    dokdot = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='.', command=lambda:btnClick(".") ).grid(row=5, column=0)

    doktavan = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='**', command=lambda:btnClick("**") ).grid(row=5, column=1)

    dokgazr = Button(tree, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='√', command=lambda:btnClick("√") ).grid(row=5, column=2)

    dokdel = Button(tree, padx=16, pady=16, bd=8, fg='black',font=('arial', 20, 'bold'),text='←', command=btnBackspace).grid(row=5, column=3)

    dokbargasht = Button(tree, padx=16, pady=16, bd=8, fg='black',font=('arial', 20, 'bold'),text='← bargasht', command=bargasht).grid(row=6, column=0, columnspan=2)
                    
                    
    apply_theme_to_window(tree)






    tree.mainloop()





def btnClick(numbers):
    global operator
    operator = operator + str(numbers)
    hg.set(operator)


def btnBackspace():
    global operator
    operator = operator[:-1]
    hg.set(operator)   


def btnClearDisplay():
    global operator
    operator =""
    hg.set("")




def btnEqualsInput():
    global operator
    try:
        if "√" in operator:
            number = float(operator.replace("√", ""))
            result = math.sqrt(number)
        else:
            result = eval(operator)

        hg.set(result)
        operator = str(result)
    except:
        hg.set("ERROR")
        operator = ""


def bargasht():
    tree.destroy()
    open_window_2_buttons()

def bargashtmeno():
    www.destroy()
    asly()


def asly():
    global www, qqq, doktagir
    try:
        www.destroy()
    except:
        pass
    qqq = Tk()
    qqq.title("math")




    dokmash = Button(qqq, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='mashin hesab', command=open_window_2_buttons ).grid(row=0, column=0)

    dokyad = Button(qqq, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='yadgiry', command=open_window_8_buttons ).grid(row=0, column=1)

    doktagir = Button(qqq, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='tagir', command=toggle_theme )
    doktagir.grid(row=0, column=2)
    
    apply_theme_to_window(qqq)

    qqq.mainloop()

asly()








