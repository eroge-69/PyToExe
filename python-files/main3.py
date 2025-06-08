from tkinter import*


def open_window_2_buttons():
    qqq.destroy()
    
    www = Tk()
    www.title("mashin")
    
    label = Label(www, text="mashin hesab mahmoly ya mashin hesab furmoly").grid(row=0, column=0)

    
    dokmashinh = Button(www, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='mashin hesab mahmoly', command=lambda:wsw(0) ).grid(row=1, column=0)

    dokmashinf = Button(www, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='mashin hesab furmoly', command=lambda:wsw(1) ).grid(row=1, column=1)

    www.mainloop()



def open_window_8_buttons():
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

    dokmanfmanf = Button(frame, padx=8, pady=8, bd=8, fg='black', font=('arial', 20, 'bold'), text="manfy_manfy", command=lambda:wsw(0) ).grid(row=3, column=0, sticky="nsew")


    mmm.mainloop()








qqq = Tk()
qqq.title("نرم افزار")



dokmash = Button(qqq, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='ماشين حساب', command=open_window_2_buttons ).grid(row=0, column=0)

dokyad = Button(qqq, padx=16, pady=16, bd=8, fg='black', font=('arial', 20, 'bold'), text='يادگيري', command=open_window_8_buttons ).grid(row=0, column=1)






qqq.mainloop()
