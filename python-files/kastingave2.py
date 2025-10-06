#!/usr/bin/env python3
import tkinter
from tkinter import *
from PIL import Image, ImageTk


start=Tk()
start.title("CNC xxl-bestanden voor SCM TECH Z5  HAST    -J. Vanderstegen")
start.geometry('1350x700+5+10')
image1 = Image.open("C:\TECH_Z5.jpeg")
image2 = Image.open("C:\kast.jpg")
test = ImageTk.PhotoImage(image1)
test2 = ImageTk.PhotoImage(image2)
def begin():
    start.quit()
    start.destroy()
label =tkinter.Label(width=800, height=600,text="HAST",font=("Arial Bold", 70), image=test)
label.image = test
label2=tkinter.Label(width=300, height=600, image=test2)
label2.image=test2
label3=Label(start, text="CNC SCM KASTEN ",font=("Arial Bold", 70))

label4=Label(start, text="J. Vanderstegen ",font=("Helvetica", 14))

# Position image
label.place(x=50, y=100)
label2.place(x=900,y=100)
label3.place(x=300,y=15)
label4.place(x=1200,y=600)
btnstart=Button(start, text="START",command=begin)
btnstart.place(x=1200,y=650)
start.mainloop()


from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile

basis=Tk()
basis.geometry("1350x700+5+10")
basis.title("CNC J. Vanderstegen")
basis.configure(bg='lemonchiffon')



kasthoogtelbl=Label(basis, text="Kasthoogte = ",width=20, height =2,bd=3,relief="sunken",bg="lightyellow")
kasthoogtelbl.place(x=20,y=50)

kastbreedtelbl=Label(basis, text="Kastbreedte = ",width=20, height =2,bd=3,relief="sunken",bg="lightyellow")
kastbreedtelbl.place(x=20,y=100)

kastdieptelbl=Label(basis, text="Kastdiepte = ",width=20, height =2,bd=3,relief="sunken",bg="lightyellow")
kastdieptelbl.place(x=20,y=150)

plaatdiktelbl=Label(basis, text="Plaatdikte = ", width=20, height = 2, bd=3, relief="sunken", bg="lightyellow")
plaatdiktelbl.place(x=20,y=200)

rugafstlbl=Label(basis, text="Rugafstand = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
rugafstlbl.place(x=20,y=250)

rugdiktelbl=Label(basis, text="Rugdikte = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
rugdiktelbl.place(x=20,y=300)

leggervastlbl=Label(basis, text="Aantal vaste leggers = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
leggervastlbl.place(x=20,y=350)

opm1lbl=Label(basis, text="enkel bij 1 of 2 vaste leggers",width=30, height =1,bd=3,fg="red",bg="lightyellow")
opm1lbl.place(x=280,y=390)

tussenafstlbl=Label(basis, text="Tussenafstand onder = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
tussenafstlbl.place(x=20,y=400)

opm2lbl=Label(basis, text="enkel bij 2 vaste leggers",width=30, height =1,bd=3,fg="red",bg="lightyellow")
opm2lbl.place(x=280,y=440)

tussenafst2lbl=Label(basis, text="Tussenafstand midden = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
tussenafst2lbl.place(x=20,y=450)

drevelafstlbl=Label(basis, text="Tussenafstand drevels = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
drevelafstlbl.place(x=20,y=500)   

diepte_drevlbl=Label(basis, text="Diepte drevelboringen = ",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
diepte_drevlbl.place(x=20,y=550)   

rijboringstart=Label(basis, text="startafst. rijb. per vak",width=30, height=2,bd=3, relief="sunken", bg="lightyellow")
rijboringstart.place(x=20, y=600)

tussenafstrijb=Label(basis, text="tussenafstand rijb",width=30, height=2,bd=3, relief="sunken", bg="lightyellow")
tussenafstrijb.place(x=20, y=650)

invoerkaho=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoerkaho.place(x=300,y=60)

invoerkabr=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoerkabr.place(x=300,y=110)

invoerkadi=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoerkadi.place(x=300,y=160)

invoerplaatd=Entry(basis, width=20, bd=2, font=("Helvetica","12"))
invoerplaatd.place(x=300, y=210)

invoerrugafst=Entry(basis, width=20, bd=2, font=("Helvetica","12"))
invoerrugafst.place(x=300, y=260)

invoerrugdikte=Entry(basis, width=20, bd=2, font=("Helvetica","12"))
invoerrugdikte.place(x=300, y=310)

invoerleva=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoerleva.place(x=300,y=360)

invoer_tussenafst=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoer_tussenafst.place(x=300,y=410)

invoer_tussenafst2=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoer_tussenafst2.place(x=300,y=460)

invoerafstdrev=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoerafstdrev.place(x=300,y=510)

invoerdieptedrev=Entry(basis, width=20, bd=2,font=("Helvetica","12"))
invoerdieptedrev.place(x=300,y=560)

invoerrijbafst1=Entry(basis, width=6, bd=2, font=("Helvetica","12"))
invoerrijbafst1.place(x=300,y=610)


opm3lbl=Label(basis,text="vak1 (O)",width=7, height =1,fg="red",bg="lightyellow",font=("Helvetica","10"))
opm3lbl.place(x=300,y=590)

opm4lbl=Label(basis,text="vak2 (M)",width=7, height =1,fg="red",bg="lightyellow",font=("Helvetica","10"))
opm4lbl.place(x=360,y=590)

opm5lbl=Label(basis,text="vak3 (B)",width=7, height =1,fg="red",bg="lightyellow",font=("Helvetica","10"))
opm5lbl.place(x=420,y=590)

invoerrijbafst2=Entry(basis, width=6, bd=2, font=("Helvetica","12"))
invoerrijbafst2.place(x=360,y=610)

invoerrijbafst3=Entry(basis, width=6, bd=2, font=("Helvetica","12"))
invoerrijbafst3.place(x=420,y=610)

invoerrijbtus=Entry(basis, width=20, bd=2, font=("Helvetica","12"))
invoerrijbtus.place(x=300,y=660)

weergave=Text(basis, height=35, width=65,bg="white",fg="black", bd=3, relief="sunken", font=("Helvetica","12"))
weergave.place(x=500,y=50)



def toekennen():
    
    global hozijkant
    global kastdiepte
    global kasthoogte
    global plaatdikte
    global brzijkant
    global lkopbod
    global brkopbod
    global rugafstand
    global rugdikte
    global aantleggersv
    kastbreedte=invoerkabr.get()
    kasthoogte=invoerkaho.get()
    kastdiepte=invoerkadi.get()
    aantleggersv=invoerleva.get()
    plaatdikte=invoerplaatd.get()
    rugafstand=invoerrugafst.get()
    rugdikte=invoerrugdikte.get()       
    brkopbod=float(kastdiepte)- (float(rugafstand)+float(rugdikte))
    brzijkant=kastdiepte
    hozijkant= float(kasthoogte)
    lkopbod=float(kastbreedte) - float(plaatdikte)*2
    
def zijkantcnc():
    global hozijkant    
    global kastdiepte
    global plaatdikte
    global brzijkant
    global rugafstand
    global rugdikte
    global aantal_drevels
    global drevelafstand
    global tussenafstand
    global tussenafstand2
    global aantleggersv
    global rijbafst1
    global rijbafst2
    global rijbafst3
    global rijbtus
    tussenafstand=invoer_tussenafst.get()
    tussenafstand2=invoer_tussenafst2.get()
    DX = str(hozijkant)
    DY = kastdiepte
    DZ = plaatdikte
    drevelafstand=int(invoerafstdrev.get())
    aantleggersv=invoerleva.get()
    diepte_drevelgaten=invoerdieptedrev.get()
    aantal_drevels= int((float(DY)-57-float(rugafstand)-float(rugdikte)-25)/drevelafstand) +1
    rijbafst1=invoerrijbafst1.get()
    rijbtus=invoerrijbtus.get()
    rijbafst2=invoerrijbafst2.get()
    rijbafst3=invoerrijbafst3.get()
    #PLAATAFMETINGEN
    weergave.insert(END,"H DX="+ DX + " DY=" + DY+ " DZ=" + DZ + ' -IL C=0 T=196608 R=99 *MM /"johan" BX=2.000 BY=2.000 BZ=0.000 V=10')
    weergave.insert(END,"\n")
    weergave.insert(END,"REF DX="+ DX + " DY=" + DY + " DZ=" + DZ + " FLD=IL BX=2.000 BY=2.000 BZ=0.000")
    weergave.insert(END,"\n")
    weergave.insert(END,"O X=0 Y=0 Z=0 F=1 ;Changeplane")
    weergave.insert(END,"\n")
    #RONDFREZING
    weergave.insert(END,"XGIN G=2 R=3 Q=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XG0 X=" + str(float(DX)/2)+" Y=0 Z=-" + str(float(DZ)+2)+" T=109 P=0 D=18 C=1 s=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X="+DX)
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P Y="+DY)
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P Y=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=" + str(float(DX)/2))
    weergave.insert(END,"\n")
    weergave.insert(END,"XGOUT G=2 R=3 Q=0 L=0")
    weergave.insert(END,"\n")
    #DREVELBORINGEN
    weergave.insert(END,"XBO X="+str(float(DZ)/2) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
    weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DZ)/2) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" # x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"')
    weergave.insert(END,"\n")
    if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):
        weergave.insert(END,"XBO X="+str(float(DZ)/2) +" Y= "+str(float(rugafstand)+float(rugdikte)+25) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
        weergave.insert(END,"\n")
    if aantleggersv =="1":
        weergave.insert(END,"XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25))+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" # x=0 y=-"+ str(drevelafstand)+" D=8 N="+'"P"')
        weergave.insert(END,"\n")
        if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):  
            weergave.insert(END,"XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str(float(rugafstand)+float(rugdikte)+25)+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
            weergave.insert(END,"\n")
    if aantleggersv =="2":
        weergave.insert(END,"XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" # x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(DZ)*2.5+float(tussenafstand)+float(tussenafstand2)) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(DZ)*2.5+float(tussenafstand)+float(tussenafstand2)) +" Y=" +str((float(DY)- 25-32))+" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" # x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"')
        weergave.insert(END,"\n")
        if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):
            weergave.insert(END,"XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str(float(rugafstand)+float(rugdikte)+25)+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
            weergave.insert(END,"\n")
            weergave.insert(END,"XBO X="+str(float(DZ)*2.5+float(tussenafstand)+float(tussenafstand2)) +" Y=" +str(float(rugafstand)+float(rugdikte)+25)+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
            weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DX)-float(DZ)/2) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
    weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DX)-float(DZ)/2) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" # x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"')
    weergave.insert(END,"\n")
    if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):      
        weergave.insert(END,"XBO X="+str(float(DX)-float(DZ)/2) +" Y= "+str(float(rugafstand)+float(rugdikte)+25) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"')
        weergave.insert(END,"\n")
    #RIJBORINGEN
    if aantleggersv=="0":
        aantrijb1 =int( (float(DX) - 2*float(DZ)- 2* float(rijbafst1))/float(rijbtus) )
        rijbstart=(float(DX)- aantrijb1*float(rijbtus))/2
        weergave.insert(END,"XBO X="+ str(rijbstart)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb1+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+ str(rijbstart)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb1+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
    if aantleggersv=="1":
        tussenafstand2=float(DX)-3*float(DZ)-float (tussenafstand)
        aantrijb1=int((float(tussenafstand)-2*float(rijbafst1))/float(rijbtus))
        rijbstart=(float(tussenafstand)-(aantrijb1*float(rijbtus)))/2
       
        weergave.insert(END,"XBO X="+ str(rijbstart+float(DZ))+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb1+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+ str(rijbstart+ float(DZ))+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb1+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        
        aantrijb2= int((float(tussenafstand2)-2*float(rijbafst2))/float(rijbtus))
        rijbstart2=(float(tussenafstand2)-aantrijb1*float(rijbtus))/2
        
        weergave.insert(END,"XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb2+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb2+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")

    if aantleggersv=="2":
        tussenafstand3=float(DX)-4*float(DZ)-float (tussenafstand)-float(tussenafstand2)
        aantrijb1=int((float(tussenafstand)-2*float(rijbafst1))/float(rijbtus))
        rijbstart=(float(tussenafstand)-(aantrijb1*float(rijbtus)))/2
        
        weergave.insert(END,"XBO X="+ str(rijbstart+float(DZ))+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb1+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+ str(rijbstart+ float(DZ))+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb1+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        
        aantrijb2= int((float(tussenafstand2)-2*float(rijbafst2))/float(rijbtus))
        rijbstart2=(float(tussenafstand2)-aantrijb2*float(rijbtus))/2
       
        weergave.insert(END,"XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb2+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb2+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        aantrijb3=int((float(tussenafstand3)-2*float(rijbafst3))/float(rijbtus))
        rijbstart3=(float(tussenafstand3)-aantrijb3*float(rijbtus))/2
        weergave.insert(END,"XBO X="+ str(float(DZ)*3+float(tussenafstand)+float(tussenafstand2)+rijbstart3)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32) +" Z=-10 R="+str(aantrijb3+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+ str(float(DZ)*3+float(tussenafstand)+float(tussenafstand2)+rijbstart3)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb3+1)+" # x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        weergave.insert(END,"\n")
    #groef rug
    weergave.insert(END,"XGIN G=1 R=3 Q=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XG0 X=0 Y="+str(float(rugafstand)+float(rugdikte))+" Z=-8 T=104 P=0 D=8 C=1 s=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=" +DX)
    weergave.insert(END,"\n")
    weergave.insert(END,"XGOUT G=1 R=3 Q=0 L=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XGIN G=1 R=3 Q=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XG0 X=0 Y="+str(float(rugafstand)-0.5)+" Z=-8 T=104 P=0 D=8 C=2 s=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=" +DX)
    weergave.insert(END,"\n")
    weergave.insert(END,"XGOUT G=1 R=3 Q=0 L=0")
    weergave.insert(END,"\n")

def zopslaan():    
    global hozijkant    
    global kastdiepte
    global plaatdikte
    global brzijkant
    global rugafstand
    global rugdikte
    global aantal_drevels
    global drevelafstand
    global tussenafstand
    global tussenafstand2
    global aantleggersv
    global rijbafst1
    global rijbtus
    tussenafstand=invoer_tussenafst.get()
    tussenafstand2=invoer_tussenafst2.get()
    DX = str(hozijkant)
    DY = kastdiepte
    DZ = plaatdikte
    drevelafstand=int(invoerafstdrev.get())
    aantleggersv=invoerleva.get()
    diepte_drevelgaten=invoerdieptedrev.get()
    aantal_drevels= int((float(DY)-57-float(rugafstand)-float(rugdikte)-25)/drevelafstand) +1
    #PLAATAFMETINGEN
    file = filedialog.asksaveasfilename(
        filetypes=[("cnc bestand", ".xxl")],
    defaultextension=".xxl")
    f=open(file,'w')
    f.write("H DX="+ DX + " DY=" + DY+ " DZ=" + DZ + ' -IL C=0 T=196608 R=99 *MM /"johan" BX=2.000 BY=2.000 BZ=0.000 V=10'+"\n")
    f.write("REF DX="+ DX + " DY=" + DY + " DZ=" + DZ + " FLD=IL BX=2.000 BY=2.000 BZ=0.000"+"\n")
    f.write("O X=0 Y=0 Z=0 F=1 ;Changeplane"+"\n")
    #RONDFREZING
    f.write("XGIN G=2 R=3 Q=0"+"\n")
    f.write("XG0 X=" + str(float(DX)/2)+" Y=0 Z=-" + str(float(DZ)+2)+" T=109 P=0 D=18 C=1 s=0"+"\n")
    f.write("XL2P X=" +DX+"\n")
    f.write("XL2P Y="+DY+"\n") 
    f.write("XL2P X=0"+"\n") 
    f.write("XL2P Y=0"+"\n")
    f.write("XL2P X=" + str(float(DX)/2)+"\n")
    f.write("XGOUT G=2 R=3 Q=0 L=0"+"\n")
    #DREVELBORINGEN
    f.write("XBO X="+str(float(DZ)/2) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
    f.write("XBO X="+str(float(DZ)/2) +" Y=" +str((float(DY)- 25-32))+" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"'+"\n")
    if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):
        f.write("XBO X="+str(float(DZ)/2) +" Y= "+str(float(rugafstand)+float(rugdikte)+25) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
    if aantleggersv =="1":
        f.write("XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
        f.write("XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" x=0 y=-"+ str(drevelafstand)+" D=8 N="+'"P"'+"\n")
        if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):  
            f.write("XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str(float(rugafstand)+float(rugdikte)+25)+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")    
    if aantleggersv =="2":
        f.write("XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
        f.write("XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"'+"\n")
        f.write("XBO X="+str(float(DZ)*2.5+float(tussenafstand)+float(tussenafstand2)) +" Y=" +str(float(DY)- 25) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
        f.write("XBO X="+str(float(DZ)*2.5+float(tussenafstand)+float(tussenafstand2)) +" Y=" +str((float(DY)- 25-32)) +" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"'+"\n")
        if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):
            f.write("XBO X="+str(float(DZ)/2+float(DZ)+float(tussenafstand)) +" Y=" +str(float(rugafstand)+float(rugdikte)+25)+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
            f.write("XBO X="+str(float(DZ)*2.5+float(tussenafstand)+float(tussenafstand2)) +" Y=" +str(float(rugafstand)+float(rugdikte)+25)+" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")         
    f.write("XBO X="+str(float(DX)-float(DZ)/2) +" Y=" +str((float(DY)- 25)) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")  
    f.write("XBO X="+str(float(DX)-float(DZ)/2) +" Y=" +str((float(DY)- 25-32))+" Z=-"+diepte_drevelgaten+" R="+ str(aantal_drevels) +" x=0 y=-"+str(drevelafstand)+" D=8 N="+'"P"'+"\n")        
    if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-float(rugafstand)-float(rugdikte)-49):      
        f.write("XBO X="+str(float(DX)-float(DZ)/2) +" Y="+str(float(rugafstand)+float(rugdikte)+25) +" Z=-"+diepte_drevelgaten+" R=1 x=0 y=0 D=8 N="+'"P"'+"\n")
    #RIJBORINGEN
    if aantleggersv=="0":
        aantrijb1 =int( (float(DX) - 2*float(DZ)- 2* float(rijbafst1))/float(rijbtus) )
        rijbstart=(float(DX)-2*float(DZ)- aantrijb1*float(rijbtus))/2
        f.write("XBO X="+ str(rijbstart+float(DZ))+ " Y=50" +" Z=-10 R="+str(aantrijb1+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        f.write("XBO X="+ str(rijbstart+float(DZ))+ " Y="+str(float(DY)-float(rugafstand)- float(rugdikte)-32)+" Z=-10 R="+str(aantrijb1+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
    if aantleggersv=="1":
        tussenafstand2=float(DX)-3*float(DZ)-float (tussenafstand)
        aantrijb1=int((float(tussenafstand)-2*float(rijbafst1))/float(rijbtus))
        rijbstart=(float(tussenafstand)-(aantrijb1*float(rijbtus)))/2
        
        f.write("XBO X="+ str(rijbstart+float(DZ))+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb1+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        f.write("XBO X="+ str(rijbstart+ float(DZ))+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb1+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        
        aantrijb2= int((float(tussenafstand2)-2*float(rijbafst2))/float(rijbtus))
        rijbstart2=(float(tussenafstand2)-aantrijb2*float(rijbtus))/2
        
        f.write("XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb2+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        f.write("XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb2+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")

    if aantleggersv=="2":
        tussenafstand3=float(DX)-4*float(DZ)-float (tussenafstand)-float(tussenafstand2)
        aantrijb1=int((float(tussenafstand)-2*float(rijbafst1))/float(rijbtus))
        rijbstart=(float(tussenafstand)-(aantrijb1*float(rijbtus)))/2
        
        f.write("XBO X="+ str(rijbstart+float(DZ))+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb1+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        f.write("XBO X="+ str(rijbstart+ float(DZ))+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb1+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        
        aantrijb2= int((float(tussenafstand2)-2*float(rijbafst2))/float(rijbtus))
        rijbstart2=(float(tussenafstand2)-aantrijb2*float(rijbtus))/2
        
        f.write("XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb2+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        
        f.write("XBO X="+ str(float(DZ)*2+float(tussenafstand)+rijbstart2)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32)+" Z=-10 R="+str(aantrijb2+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        aantrijb3=int((float(tussenafstand3)-2*float(rijbafst3))/float(rijbtus))
        rijbstart3=(float(tussenafstand3)-aantrijb3*float(rijbtus))/2
       
        f.write("XBO X="+ str(float(DZ)*3+float(tussenafstand)+float(tussenafstand2)+rijbstart3)+ " Y="+str(float(rugafstand)+ float(rugdikte)+32) +" Z=-10 R="+str(aantrijb3+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
        f.write("XBO X="+ str(float(DZ)*3+float(tussenafstand)+float(tussenafstand2)+rijbstart3)+ " Y=" +str(float(DY)-50) +" Z=-10 R="+str(aantrijb3+1)+" x=" + rijbtus +" y=0"+ " D=5 N="+'"P"')
        f.write("\n")
    #groef rug
    f.write("XGIN G=1 R=3 Q=0")
    f.write("\n")
    f.write("XG0 X=0 Y="+str(float(rugafstand)+float(rugdikte))+" Z=-8 T=104 P=0 D=8 C=1 s=0")
    f.write("\n")
    f.write("XL2P X=" +DX)
    f.write("\n")
    f.write("XGOUT G=1 R=3 Q=0 L=0")
    f.write("\n")
    f.write("XGIN G=1 R=3 Q=0")
    f.write("\n")
    f.write("XG0 X=0 Y="+str(float(rugafstand)-0.5)+" Z=-8 T=104 P=0 D=8 C=2 s=0")
    f.write("\n")
    f.write("XL2P X=" +DX)
    f.write("\n")
    f.write("XGOUT G=1 R=3 Q=0 L=0")
    f.write("\n")
    f.close()
def kopcnc():
    global kastbreedte
    kastbreedte=invoerkabr.get()
    global kastdiepte
    global plaatdikte
    global rugafstand
    global rugdikte
    DX=str(float(kastbreedte)-2*float(plaatdikte))
    DY=str(float(kastdiepte)-float(rugafstand)-float(rugdikte))
    DZ= plaatdikte
    drevelafstand=int(invoerafstdrev.get())
    aantal_drevels= int((float(DY)-57-25)/drevelafstand) +1
    
    #RONDFREZING
    weergave.delete(1.0,END)
    weergave.insert(END,"H DX="+ DX + " DY=" + DY+ " DZ=" + DZ + ' -IL C=0 T=196608 R=99 *MM /"johan" BX=2.000 BY=2.000 BZ=0.000 V=10')
    weergave.insert(END,"\n")
    weergave.insert(END,"REF DX="+ DX + " DY=" + DY + " DZ=" + DZ + " FLD=IL BX=2.000 BY=2.000 BZ=0.000")
    weergave.insert(END,"\n")
    weergave.insert(END,"O X=0 Y=0 Z=0 F=1 ;Changeplane")
    weergave.insert(END,"\n")
    
   

    weergave.insert(END,"XGIN G=2 R=3 Q=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XG0 X=" + str(float(DX)/2)+" Y=0 Z=-" + str(float(DZ)+2)+" T=109 P=0 D=18 C=1 s=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=" +DX)
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P Y="+DY)
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P Y=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"XL2P X=" + str(float(DX)/2))
    weergave.insert(END,"\n")
    weergave.insert(END,"XGOUT G=2 R=3 Q=0 L=0")
    weergave.insert(END,"\n")
    weergave.insert(END,"F = 3")
    weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25)+' Z=-20 R=1 x=0 y=0 D=8 G=1 N="P"')
    weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25-32)+" Z=-20"+" R=" +str(int(aantal_drevels))+" x=0  y=-"+str(drevelafstand)+' D= 8 G=1 N=\"P\"')
    weergave.insert(END,"\n")
    weergave.insert(END,"F=2")
    weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25)+' Z=-20 R=1 x=0 y=0 D=8 G=1 N="P"')
    weergave.insert(END,"\n")
    weergave.insert(END,"XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25-32)+" Z=-20"+" R=" +str(int(aantal_drevels))+" x=0  y=-"+str(drevelafstand)+' D= 8 G=1 N=\"P\"')
    weergave.insert(END,"\n")
    if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-49):
        weergave.insert(END,"XBO X="+str(float(DZ)/2) +" Y=25" + " Z=-20 R=1 x=0 y=0 D=8 N="+'"P"'+"\n")       
        weergave.insert(END,"F=3")
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(DZ)/2) +" Y=25" +" Z=-20 R=1 x=0 y=0 D=8 N="+'"P"'+"\n")

    

def kopslaan():
    global kastbreedte
    kastbreedte=invoerkabr.get()
    global kastdiepte
    global plaatdikte
    global rugafstand
    global rugdikte
    DX=str(float(kastbreedte)-2*float(plaatdikte))
    DY=str(float(kastdiepte)-float(rugafstand)-float(rugdikte))
    DZ= plaatdikte
    drevelafstand=float(invoerafstdrev.get())
    aantal_drevels= float((float(DY)-57-25)/drevelafstand) +1
    weergave.delete(1.0,END)
    file = filedialog.asksaveasfilename(
        filetypes=[("cnc bestand", ".xxl")],
    defaultextension=".xxl")
    f=open(file,'w')
    f.write("H DX="+ DX + " DY=" + DY+ " DZ=" + DZ + ' -IL C=0 T=196608 R=99 *MM /"johan" BX=2.000 BY=2.000 BZ=0.000 V=10')
    f.write("\n")
    f.write("REF DX="+ DX + " DY=" + DY + " DZ=" + DZ + " FLD=IL BX=2.000 BY=2.000 BZ=0.000")
    f.write("\n")
    f.write("O X=0 Y=0 Z=0 F=1 ;Changeplane")
    f.write("\n")
    f.write("XGIN G=2 R=3 Q=0")
    f.write("\n")
    f.write("XG0 X=" + str(float(DX)/2)+" Y=0 Z=-" + str(float(DZ)+2)+" T=109 P=0 D=18 C=1 s=0")
    f.write("\n")
    f.write("XL2P X=" +DX)
    f.write("\n")
    f.write("XL2P Y="+DY)
    f.write("\n")
    f.write("XL2P X=0")
    f.write("\n")
    f.write("XL2P Y=0")
    f.write("\n")
    f.write("XL2P X=" + str(float(DX)/2))
    f.write("\n")
    f.write("XGOUT G=2 R=3 Q=0 L=0")
    f.write("\n")

    f.write("F=3")
    f.write("\n")
    f.write("XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25)+' Z=-20 R=1 x=0 y=0 D=8 G=1 N="P"')
    f.write("\n")
    f.write("XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25-32)+" Z=-20"+" R=" +str(int(aantal_drevels))+" x=0 y=-"+str(drevelafstand)+' D=8 G=1 N=\"P\"')
    f.write("\n")
    f.write("F=2")
    f.write("\n")
    f.write("XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25)+' Z=-20 R=1 x=0 y=0 D=8 G=1 N="P"')
    f.write("\n")
    f.write("XBO X="+str(float(DZ)/2)+ " Y="+ str(float(DY)-25-32)+" Z=-20"+" R=" +str(int(aantal_drevels))+" x=0 y=-"+str(drevelafstand)+' D=8 G=1 N=\"P\"')
    f.write("\n")
    if (25+32+(aantal_drevels -1)*drevelafstand) < (float(DY)-49):
        f.write("XBO X="+str(float(DZ)/2) +" Y=25" + " Z=-20 R=1 x=0 y=0 D=8 N="+'"P"'+"\n")       
        f.write("F=3")
        f.write("\n")
        f.write("XBO X="+str(float(DZ)/2) +" Y=25" +" Z=-20 R=1 x=0 y=0 D=8 N="+'"P"'+"\n")

def deuren():
    weergave.delete(1.0,END)
    global tussenafstand
    tussenafstand=invoer_tussenafst.get()
    
    global tussenafstand2
    tussenafstand2=invoer_tussenafst2.get()
    global kastbreedte
    kastbreedte=invoerkabr.get()
    global kasthoogte
    kasthoogte=invoerkaho.get()
    global plaatdikte
    global DX
    global aantleg
    aantleg=invoerleva.get()
    plaatdikte=invoerplaatd.get()
    if float(aantleg)==0:
        tussenafstand=float(kasthoogte)-2*float(plaatdikte)
    
    kasthoogtelbl.place_forget()
    kastbreedtelbl.place_forget()
    kastdieptelbl.place_forget()
    plaatdiktelbl.place_forget()
    rugafstlbl.place_forget()
    rugdiktelbl.place_forget()
    leggervastlbl.place_forget()
    tussenafstlbl.place_forget()
    tussenafst2lbl.place_forget()
    drevelafstlbl.place_forget()
    diepte_drevlbl.place_forget()
    rijboringstart.place_forget()
    tussenafstrijb.place_forget()
    invoerkaho.place_forget()
    invoerkabr.place_forget()
    invoerkadi.place_forget()
    invoerplaatd.place_forget()
    invoerrugafst.place_forget()
    invoerrugdikte.place_forget()
    invoerleva.place_forget()
    invoer_tussenafst.place_forget()
    invoer_tussenafst2.place_forget()
    invoerafstdrev.place_forget()
    invoerdieptedrev.place_forget()
    invoerrijbafst1.place_forget()
    invoerrijbafst2.place_forget()
    invoerrijbafst3.place_forget()
    invoerrijbtus.place_forget()
    opm1lbl.place_forget()
    opm2lbl.place_forget()
    opm3lbl.place_forget()
    opm4lbl.place_forget()
    opm5lbl.place_forget()
    image = PhotoImage(file='/media/johan/USB DISK/KAST.png')
    config1lbl=Label(basis, image=image,width=300, height=400)
    config1lbl.place(x=20, y=10)
    deurindelinglbl=Label(basis,text="geef aan voor welke vakken\n de deur komt: vb 1+2\n of 1+2+3 ...\nZet een * er achter als er\neen andere deur boven\nof onder komt\n(let op: enkel als je 2 vaste leggers\ningaf heb je 3 vakken)",width=30, height =8,bd=3,relief="sunken",bg="lightyellow",font=("Helvetica","10"))
    deurindelinglbl.place(x=20,y=420)

    invoerindeling=Entry(basis,width=12, bd=2, font=("Helvetica","12"))
    invoerindeling.place(x=300,y=480)

    oplegzlbl=Label(basis, text="opleg deur op de zijkanten =",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
    oplegzlbl.place(x=20,y=560)

    oplegklbl=Label(basis, text="opleg deur op de kop en bodem =",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
    oplegklbl.place(x=20,y=610)

    invoeroplegz=Entry(basis,width=12, bd=2, font=("Helvetica","12"))
    invoeroplegz.place(x=300,y=570)
    
    invoeroplegk=Entry(basis,width=12, bd=2, font=("Helvetica","12"))
    invoeroplegk.place(x=300,y=620)

    scharnierafstlbl=Label(basis, text="afstand buitenste scharnier",width=30, height =2,bd=3,relief="sunken",bg="lightyellow")
    scharnierafstlbl.place(x=20,y=660)

    scharnierafst=Entry(basis,width=12, bd=2, font=("Helvetica","12"))
    scharnierafst.place(x=300,y=670)
    def deur1():
        global tussenafstand
        global tussenafstand2
        if invoerleva.get()=="1":
            tussenafstand2=str(float(kasthoogte)-3*float(plaatdikte)-float(tussenafstand))
        
        global scharnierafstand
        scharnierafstand=scharnierafst.get()
        global scharniertus
        global oplegz
        oplegz=float(invoeroplegz.get())
        global oplegk
        oplegk=float(invoeroplegk.get())
        if invoerindeling.get()=="1":
            DX= str(float(tussenafstand)+2*oplegk)
        if invoerindeling.get()=="1*":
            DX= str(float(tussenafstand)+2*oplegk-float(plaatdikte)/2)
        if invoerindeling.get()=="2":
            DX= str(float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="2*":
            DX= str(float(tussenafstand2)+2*oplegk-float(plaatdikte)/2)
        if invoerindeling.get()=="2**":
            DX= str(float(tussenafstand2)+2*oplegk-float(plaatdikte))   
        if invoerindeling.get()=="3":
            DX= str(float(kasthoogte)-4*float(plaatdikte)-float(tussenafstand)-float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="3*":
            DX= str(float(kasthoogte)-4.5*float(plaatdikte)-float(tussenafstand)-float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="1+2":
            DX=str(float(tussenafstand)+float(plaatdikte)+float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="1+2*":
            DX=str(float(tussenafstand)+float(plaatdikte)+float(tussenafstand2)+2*oplegk-float(plaatdikte)/2)
        if invoerindeling.get()=="2+3":
            DX=str(float(kasthoogte)-3*float(plaatdikte)-float(tussenafstand)+2*oplegk)
        if invoerindeling.get()=="2+3*":
            DX=str(float(kasthoogte)-3.5*float(plaatdikte)-float(tussenafstand)+2*oplegk)
        if invoerindeling.get()=="1+2+3":
            DX=str(float(kasthoogte)-2*float(plaatdikte)+2*oplegk)    
        if float(DX)<=750:
            aantal=2
        if float(DX)>=750:
            aantal=3
        if float(DX)>=1500:
            aantal=4
        if float(DX)>=2100:
            aantal=5
            
        scharniertus=(float(DX)-2*float(scharnierafstand))/(aantal-1)
       
        
        DY= str(float(kastbreedte)-2*float(plaatdikte)+2*oplegz)
        DZ=str(float(plaatdikte))
        
        weergave.delete(1.0,END)
        weergave.insert(END,"H DX="+ DX + " DY=" + DY+ " DZ=" + DZ + ' -IL C=0 T=196608 R=99 *MM /"johan" BX=2.000 BY=2.000 BZ=0.000 V=10')
        weergave.insert(END,"\n")
        weergave.insert(END,"REF DX="+ DX + " DY=" + DY + " DZ=" + DZ + " FLD=IL BX=2.000 BY=2.000 BZ=0.000")
        weergave.insert(END,"\n")
        weergave.insert(END,"O X=0 Y=0 Z=0 F=1 ;Changeplane")
        weergave.insert(END,"\n")
        #RONDFREZING
        weergave.insert(END,"XGIN G=2 R=3 Q=0")
        weergave.insert(END,"\n")
        weergave.insert(END,"XG0 X=" + str(float(DX)/2)+" Y=0 Z=-" + str(float(DZ)+2)+" T=109 P=0 D=18 C=1 s=0")
        weergave.insert(END,"\n")
        weergave.insert(END,"XL2P X=" +DX)
        weergave.insert(END,"\n")
        weergave.insert(END,"XL2P Y="+DY)
        weergave.insert(END,"\n")
        weergave.insert(END,"XL2P X=0")
        weergave.insert(END,"\n")
        weergave.insert(END,"XL2P Y=0")
        weergave.insert(END,"\n")
        weergave.insert(END,"XL2P X=" + str(float(DX)/2))
        weergave.insert(END,"\n")
        weergave.insert(END,"XGOUT G=2 R=3 Q=0 L=0")
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+scharnierafstand + " Y="+ str(float(DY)-22.5)+' Z=-13 R=1 x=0 y=0 D=35 G=1 N="P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(scharnierafstand)-22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
        weergave.insert(END,"\n")
        weergave.insert(END,"XBO X="+str(float(scharnierafstand)+22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
        weergave.insert(END,"\n")
        for n in range (1,aantal,1):
           
           
            weergave.insert(END,"XBO X="+str(float(scharnierafstand)+scharniertus*n) + " Y="+ str(float(DY)-22.5)+' Z=-13 R=1 x=0 y=0 D=35 G=1 N="P"')
            weergave.insert(END,"\n")
            weergave.insert(END,"XBO X="+str(float(scharnierafstand)+scharniertus*n-22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
            weergave.insert(END,"\n")
            weergave.insert(END,"XBO X="+str(float(scharnierafstand)+scharniertus*n+22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
            weergave.insert(END,"\n")  
    def deuropslaan():
        file = filedialog.asksaveasfilename(
            filetypes=[("cnc bestand", ".xxl")],
        defaultextension=".xxl")
        f=open(file,'w')
        global tussenafstand
        global scharnierafstand
        scharnierafstand=scharnierafst.get()
        global scharniertus
        global oplegz
        oplegz=float(invoeroplegz.get())
        global oplegk
        oplegk=float(invoeroplegk.get())
        if invoerindeling.get()=="1":
            DX= str(float(tussenafstand)+2*oplegk)
        if invoerindeling.get()=="1*":
            DX= str(float(tussenafstand)+2*oplegk-float(plaatdikte)/2)
        if invoerindeling.get()=="2":
            DX= str(float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="2*":
            DX= str(float(tussenafstand2)+2*oplegk-float(plaatdikte)/2)
        if invoerindeling.get()=="2**":
            DX= str(float(tussenafstand2)+2*oplegk-float(plaatdikte))   
        if invoerindeling.get()=="3":
            DX= str(float(kasthoogte)-4*float(plaatdikte)-float(tussenafstand)-float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="3*":
            DX= str(float(kasthoogte)-4.5*float(plaatdikte)-float(tussenafstand)-float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="1+2":
            DX=str(float(tussenafstand)+float(plaatdikte)+float(tussenafstand2)+2*oplegk)
        if invoerindeling.get()=="1+2*":
            DX=str(float(tussenafstand)+float(plaatdikte)+float(tussenafstand2)+2*oplegk-float(plaatdikte)/2)
        if invoerindeling.get()=="2+3":
            DX=str(float(kasthoogte)-3*float(plaatdikte)-float(tussenafstand)+2*oplegk)
        if invoerindeling.get()=="2+3*":
            DX=str(float(kasthoogte)-3.5*float(plaatdikte)-float(tussenafstand)+2*oplegk)
        if invoerindeling.get()=="1+2+3":
            DX=str(float(kasthoogte)-2*float(plaatdikte)+2*oplegk)    
        if float(DX)<=750:
            aantal=2
        if float(DX)>=750:
            aantal=3
        if float(DX)>=1500:
            aantal=4
        if float(DX)>=2100:
            aantal=5
            
        scharniertus=(float(DX)-2*float(scharnierafstand))/(aantal-1)
        
       
        DY= str(float(kastbreedte)-2*float(plaatdikte)+2*oplegz)
        DZ=str(float(plaatdikte))
        
        
        f.write("H DX="+ DX + " DY=" + DY+ " DZ=" + DZ + ' -IL C=0 T=196608 R=99 *MM /"johan" BX=2.000 BY=2.000 BZ=0.000 V=10')
        f.write("\n")
        f.write("REF DX="+ DX + " DY=" + DY + " DZ=" + DZ + " FLD=IL BX=2.000 BY=2.000 BZ=0.000")
        f.write("\n")
        f.write("O X=0 Y=0 Z=0 F=1 ;Changeplane")
        f.write("\n")
        #RONDFREZING
        f.write("XGIN G=2 R=3 Q=0")
        f.write("\n")
        f.write("XG0 X=" + str(float(DX)/2)+" Y=0 Z=-" + str(float(DZ)+2)+" T=109 P=0 D=18 C=1 s=0")
        f.write("\n")
        f.write("XL2P X=" +DX)
        f.write("\n")
        f.write("XL2P Y="+DY)
        f.write("\n")
        f.write("XL2P X=0")
        f.write("\n")
        f.write("XL2P Y=0")
        f.write("\n")
        f.write("XL2P X=" + str(float(DX)/2))
        f.write("\n")
        f.write("XGOUT G=2 R=3 Q=0 L=0")
        f.write("\n")
        f.write("XBO X="+scharnierafstand + " Y="+ str(float(DY)-22.5)+' Z=-13 R=1 x=0 y=0 D=35 G=1 N="P"')
        f.write("\n")
        f.write("XBO X="+str(float(scharnierafstand)-22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
        f.write("\n")
        f.write("XBO X="+str(float(scharnierafstand)+22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
        f.write("\n")
        for n in range (1,aantal,1):
            
            f.write("XBO X="+str(float(scharnierafstand)+scharniertus*n) + " Y="+ str(float(DY)-22.5)+' Z=-13 R=1 x=0 y=0 D=35 G=1 N="P"')
            f.write("\n")
            f.write("XBO X="+str(float(scharnierafstand)+scharniertus*n-22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
            f.write("\n")
            f.write("XBO X="+str(float(scharnierafstand)+scharniertus*n+22.5) + " Y="+ str(float(DY)-32)+' Z=-1 R=1 x=0 y=0 D=3 G=1 N="P"')
            f.write("\n")  
        f.close()
    deur1=Button(basis, text="Tonen CNC deur", width=20, height=2, bd=3, relief="raised", command=deur1)
    deur1.place(x=1100,y=350)
    deuropsl=Button(basis,text="deur opslaan",width=20, height=2, bd=3, relief="raised", command=deuropslaan)
    deuropsl.place(x=1100,y=400)
    mainloop()
def afsluiten():
    basis.quit()
    basis.destroy()
klaar = Button(basis, text ="Invoer klaar",width=20, height=2,bd =3, relief= "raised",command=toekennen)
klaar.place(x=1100,y=50)
zijk_cnc = Button(basis,text ="Tonen CNC zijkant", width=20, height=2, bd=3, relief="raised", command=zijkantcnc)
zijk_cnc.place(x=1100,y=100)            
kop_bodem_legcnc=Button(basis, text="Tonen CNC kop/bodem", width=20,height=2, bd=3, relief="raised", command=kopcnc)
kop_bodem_legcnc.place(x=1100,y=200)

schrijven=Button(basis, text ="Opslaan zijkant", width=20, height=2, bd=3, relief="raised", command=zopslaan)
schrijven.place(x=1100,y=150)

schrijven2=Button(basis, text="Opslaan kop/bodem/legger", width=20, height=2, bd=3, relief="raised", command=kopslaan)
schrijven2.place(x=1100,y=250)
deuren=Button(basis,text ="Ingave deuren",width=20, height=2,bd =3, relief= "raised",command=deuren)
deuren.place(x=1100,y=300)
exit=Button(basis, text="Programma afsluiten",width=20, height=2,bd =3, relief= "raised",command=afsluiten)
exit.place(x=1100,y=500)
mainloop()
