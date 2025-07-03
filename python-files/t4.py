from tkinter import*
root=Tk()
root.title('калькулятор')
root.geometry('262x400+230+50')
root['bg']='Maroon'
ent = Entry(justify='right')#текстове поле справа наліво
ent.place(x=20,y=20,width=220,height=30)

def btnClear_click():
 ent.delete(0,END) 
btnClear=Button(text='C',font='14',command=btnClear_click)
btnClear.place(x=20,y=70,width=100,height=40)

def btnEqual_click():
    text=ent.get()
    rezalt=0
    if '+' in text:
        splitted_text=text.split('+')
        first=float(splitted_text[0])
        second=float(splitted_text[1])
        rezalt=first+second
    if '-' in text:
        splitted_text=text.split('+')
        first=float(splitted_text[0])
        second=float(splitted_text[1])
        rezalt=first-second
    if '*' in text:
        splitted_text=text.split('*')
        first=float(splitted_text[0])
        second=float(splitted_text[1])
        rezalt=first+second
    if '/' in text:
        splitted_text=text.split('+')
        first=float(splitted_text[0])
        second=float(splitted_text[1])
        rezalt=first/second
    ent.delete(0,END)
    ent.insert(0,rezalt)
btnEqual=Button(text='=',font='14',command=btnEqual_click)
btnEqual.place(x=140,y=70,width=100,height=40)

def btn7_click():
 ent.insert(END,'7')   
btn7=Button(text='7',font='14',command=btn7_click)
btn7.place(x=20,y=130,width=40,height=40)

def btn8_click():
 ent.insert(END,'8')   
btn8=Button(text='8',font='14',command=btn8_click)
btn8.place(x=80,y=130,width=40,height=40)

def btn9_click():
 ent.insert(END,'9') 
btn9=Button(text='9',font='14',command=btn9_click)
btn9.place(x=140,y=130,width=40,height=40)

def btnsl_click():
 ent.insert(END,'/') 
btnsl=Button(text='/',font='14',command=btnsl_click)
btnsl.place(x=200,y=130,width=40,height=40)

def btn4_click():
 ent.insert(END,'4') 
btn4=Button(text='4',font='14',command=btn4_click)
btn4.place(x=20,y=190,width=40,height=40)

def btn1_click():
 ent.insert(END,'1') 
btn1=Button(text='1',font='14',command=btn1_click)
btn1.place(x=20,y=250,width=40,height=40)

def btn5_click():
 ent.insert(END,'5') 
btn5=Button(text='5',font='14',command=btn5_click)
btn5.place(x=80,y=190,width=40,height=40)

def btn2_click():
 ent.insert(END,'2') 
btn2=Button(text='2',font='14',command=btn2_click)
btn2.place(x=80,y=250,width=40,height=40)

def btn6_click():
 ent.insert(END,'6') 
btn6=Button(text='6',font='14',command=btn6_click)
btn6.place(x=140,y=190,width=40,height=40)

def btnzv_click():
 ent.insert(END,'*') 
btnzv=Button(text='*',font='14',command=btnzv_click)
btnzv.place(x=200,y=190,width=40,height=40)

def btn3_click():
 ent.insert(END,'3') 
btn3=Button(text='3',font='14',command=btn3_click)
btn3.place(x=140,y=250,width=40,height=40)

def btnmin_click():
 ent.insert(END,'-') 
btnmin=Button(text='-',font='14',command=btnmin_click)
btnmin.place(x=200,y=250,width=40,height=40)


def btn0_click():
 ent.insert(END,'0') 
btn0=Button(text='0',font='14',command=btn0_click)
btn0.place(x=20,y=310,width=100,height=40)

def btnt_click():
 ent.insert(END,'.') 
btnt=Button(text='.',font='14',command=btnt_click)
btnt.place(x=140,y=310,width=40,height=40)

def btnpl_click():
 ent.insert(END,'+') 
btnpl=Button(text='+',font='14',command=btnpl_click)
btnpl.place(x=200,y=310,width=40,height=40)

