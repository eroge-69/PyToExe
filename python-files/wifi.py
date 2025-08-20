from tkinter import *
import os
import subprocess

win = Tk()
win.minsize(400,100)
win.resizable(NO,NO)
win.title('Wifi Hostpost')

a=''
s=''

def onichan():
    global state
    state=True
    global s
    s = ""
    a=ssid.get()
    b=pas.get()
    s += subprocess.check_output('netsh wlan set hostednetwork mode=allow ssid='+a+' key='+b, shell=True, text=True)
    
    s += subprocess.check_output('netsh wlan start hostednetwork',shell=True,text=True)
    
    
    
    msg.config(text = s) 
    global exp1
    exp1=False
    resh.forget()
    clr.forget()    

def off():
    global state
    global s
    state=False
    s = subprocess.check_output('netsh wlan stop hostednetwork', shell=True, text=True)
    msg.config(text = s)
    global exp1
    exp1=False
    resh.forget()
    clr.forget()    
    
    
def M():
    msg.config(text=s)
    global exp1
    global exp
    exp1=False
    if not exp:
        det.pack(padx=5, pady=5)
        exp=True
        resh.forget()
        clr.forget()        

    else:
        det.forget()
        exp=False
                
def D():
    global state
    global a
    if state:
        a=subprocess.check_output('arp -a | findstr "192.168"', shell=True, text=True)
        
    else:
        a='Turn on first'
        
    msg.config(text=a)
    global exp1
    global exp
    exp=False
    if not exp1:
        det.pack(padx=5, pady=5)
        exp1=True

        msg.config(text=a)
        
        resh.pack(side=LEFT)
        clr.pack(side=LEFT)
    else:
        det.forget()
        resh.forget()
        clr.forget()
        exp1=False





def chk():
    if(chkVar.get() == 0):
        pas.config(show="")
    else:
        pas.config(show="*")
        
def c():
    os.system('arp -d *')
    msg.config(text='')
    
    
def r():
    global a
    if state:
        a=subprocess.check_output('arp -a | findstr "192.168"', shell=True, text=True)
    else:
        a='Turn on first'
    
    msg.config(text=a)    
#######################
f = Frame(win)
f.pack(pady= 10)

on=Button(f,text='ON',width=10,command=onichan, height=3)
on.pack(side=LEFT, padx=30)

off=Button(f,text='OFF',width=10,command=off, height=3)
off.pack(side=RIGHT, padx=30)
#######################

f = Frame(win)
f.pack(pady=10)

txt=Label(f,text='SSID',width=5)
txt.pack(side=LEFT)

ssid=Entry(f,width=15)
ssid.pack(side=LEFT)
ssid.insert(0, "MyWiFi")
#######################


f = Frame(win)
f.pack()

txt2=Label(f,text='PASS',width=5)
txt2.pack(side=LEFT)

pas=Entry(f,width=15, show="*")
pas.pack(side=LEFT)
pas.insert(0, "123456789")

chkVar = IntVar()
see = Checkbutton(win, command=chk, variable=chkVar)
see.place(x=270,y=116)
chkVar.set(1)
#######################

f = Frame(win)
f.pack(pady=10)

more=Button(f,text='More',command=M,width=5)
more.pack(side=LEFT)

devices=Button(f,text='Devices',command=D,width=5)
devices.pack(side=LEFT,padx=10)

det=Frame(win,relief='groove',borderwidth=1)
msg = Label(det,text="",width=54,height=15)
msg.pack()
#######################

resh=Button(win,text='Refresh',command=r,width=5)
clr=Button(win,text='Clear',command=c,width=5)


exp=False
exp1=False

state=False

win.mainloop()