###### proba_вікно 
#  vva 27-06-2025
######
from tkinter import *

##перехоплення натискання Enter і ',' (кома) 
def check_enter(event) :    
    if event.keysym =='Return':
      write()  # Додайте тут код, натискання Enter
    elif event.char == ',':
      
      global schet_widget
      focused_widget = " "       # поле в якому курсор
      focused_widget = root.focus_get()  
      global pole
      global pole1
      pole = ' '
      pole = focused_widget.get() ##  запам'ятати зміст поля 

      if focused_widget != schet_widget:
         
         schet_widget = focused_widget     ##  запам'ятати поле         
         pole1=pole=pole.replace(',','.')     ##Замінює кому на крапку 
         focused_widget.delete(0,len(pole))
         focused_widget.insert(0,pole)       ##  вставити змінену строку в поле
       
      else :
         c.create_text(240, 360 ,            # повторне натискання коми в тому ж полі
              text="десяткові дроби вносити через <.>", # текст на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")            
         focused_widget.delete(0,len(pole))  ##  очисти поле 
         focused_widget.insert(0,pole1)      ##  вставити змінену строку в поле

root = Tk()                                 # створюємо кореневий об'єкт - вікно

root.title ( 'Tkinter 4568' )               # встановлюємо заголовок 
 
root.geometry("600x600")                    # встановлюємо розміри вікна 

root.config(width=600, height=600, bg='steelblue', borderwidth=10, relief=SUNKEN )

label1 = Label(text=" КАЛЬКУЛЯТОР ",bg='steel blue',fg='yellow', font=("Arial", 18 )) # створюємо заголовок прогр
label1.place(x=170, y=10)
##  оголошуємо змінні
global rez 
text1=''
text2=''
text3=''
u1text=StringVar()
c1text=StringVar()   
c2text=StringVar()
u2text=StringVar()
global u1_name
global c1_name 
global c2_name
global u2_name
global event  
global quit_button
global nquit_button

schet_widget= ''
rez=0

def rezist () :
    global rez                  ##  оголошуєм резистивний дільник
    rez=1
    rnach_button.destroy()
    cnach_button.destroy()
    label2 = Label(text="резистивний дільник ", bg='steelblue', fg='yellow', font=("Arial", 14 )) # створюємо текстову мітку
    label2.place(x=170, y=45) # розміщуємо мітку у вікні
    sxema()
    vvod_dan ()
    knopka ()


def emnist () :
    global rez                   ##  оголошуєм ємнісний  дільник            
    global sxema
    rez=0
    rnach_button.destroy()
    cnach_button.destroy()
    label2 = Label(text="   ємнісний дільник    ", bg='steelblue', fg='yellow', font=("Arial", 14 )) # створюємо текстову мітку
    label2.place(x=170, y=45) # розміщуємо мітку у вікні
    sxema()
    vvod_dan ()
    knopka ()
##  вибір дільника 
rnach_button = Button(text="РЕЗИСТИВНИЙ", fg="red", command=rezist , font=("Arial", 12 ))
rnach_button.place(x=110, y=50)
cnach_button = Button(text=" ЄМНІСТНИЙ ", fg="green", command=emnist , font=("Arial", 12 ))
cnach_button.place(x=290, y=50)
##  малюнок дільника
def sxema():
   global c                
   c = Canvas(root, width=555, height=410,bg = 'light blue')# створення полотна шириною та висотою 
   c.place(x=10, y=100)

   ### Схема 

   c.create_text(60, 170 ,                           # координати центрування тексту
              text=" U1,B ",            # текст, що відображатиметься на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")

   if rez==0 :
   
       c.create_text(270, 130,                            # координати центрування тексту
              text=" C1,мкФ ",            # текст, що відображатиметься на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")

       c.create_text(270,240,                            # координати центрування тексту
              text=" С2,мкФ ",            # текст, що відображатиметься на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")
   elif rez==1 :
       c.create_text(270, 130,                            # координати центрування тексту
              text=" R1,Ом ",            # текст, що відображатиметься на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")

       c.create_text(270,240,                            # координати центрування тексту
              text=" R2,Ом ",            # текст, що відображатиметься на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")


   c.create_text(375, 240,                            # координати центрування тексту
              text=" U2,B ",            # текст, що відображатиметься на полотні
              justify=CENTER,                      # вирівнювання тексту по центру
              font="Verdana 14")


   c.create_line(80, 100, 200, 100,width=5)          # малювання лінії
   if rez==0 :
      c.create_line(200, 100, 200, 150,width=5)
      c.create_line(180, 150, 220, 150,width=5)
      c.create_line(180, 160, 220, 160,width=5)
      c.create_line(200, 160, 200, 210,width=5)          #середина   C
      c.create_line(200, 210, 200, 260,width=5)
      c.create_line(180, 260, 220, 260,width=5)
      c.create_line(180, 270, 220, 270,width=5)
      c.create_line(200, 270, 200, 320,width=5)
   elif rez==1 :
      c.create_line(200, 100, 200, 130,width=5)
      c.create_line(190, 130, 210, 130,width=5)
      c.create_line(190, 130, 190, 180,width=5)
      c.create_line(210, 130, 210, 180,width=5)
      c.create_line(190, 180, 210, 180,width=5)
      c.create_line(200, 180, 200, 210,width=5)          #середина   R
      c.create_line(200, 210, 200, 240,width=5)
      c.create_line(190, 240, 210, 240,width=5)
      c.create_line(190, 240, 190, 290,width=5) 
      c.create_line(210, 240, 210, 290,width=5)
      c.create_line(190, 290, 210, 290,width=5)
      c.create_line(200, 290, 200, 320,width=5)

   c.create_line(200, 210, 400, 210,width=5)
   c.create_line(80, 320, 400, 320,width=5)

   c.create_line(100, 200, 100, 100,                   # координати лінії 1
              fill='black',                          # колір лінії 
              width=5,                             # ширина лінії                                          
              arrow=LAST,                          # розміщення стрілки в кінці лінії
              arrowshape="10 30 10")               # розміри стрілки
##### dash=(10, 2), # для малювання штрихами (довжина пунктиру, довжина пропуску)

   c.create_line(100, 220, 100, 320,                   # координати лінії 2
              fill='black',                          # колір лінії 
              width=5,                             # ширина лінії
              arrow=LAST,                          # розміщення стрілки в кінці лінії
              arrowshape="10 30 10")               # розміри стрілки
##### dash=(10, 2), # для малювання штрихами (довжина пунктиру, довжина пропуску)

   c.create_line(330, 210, 330, 320,                   # координати лінії 3
              fill='black',                          # колір лінії 
              width=5,                             # ширина лінії
              arrow=BOTH,                          # розміщення стрілки в кінці лінії
              arrowshape="10 30 10")               # розміри стрілки
##### dash=(10, 2), # для малювання штрихами (довжина пунктиру, довжина пропуску)'''

####Вводимо данні
def vvod_dan (): 
    global u1_name
    global c1_name 
    global c2_name
    global u2_name
   
    u1_name = Entry(root , textvariable=u1text  )  # створення та розміщення однорядкового текстового поля
    u1_name.focus_set()
    u1_name.place(x=80, y=290, width= 60 )

    c1_name = Entry(root , textvariable=c1text)    # створення та розміщення однорядкового текстового поля
    c1_name.place(x=240, y=250, width= 80 ) 

    c2_name = Entry(root , textvariable=c2text)    # створення та розміщення однорядкового текстового поля
    c2_name.place(x=240, y=360, width= 80 )

    u2_name = Entry(root , textvariable=u2text)     # створення та розміщення однорядкового текстового
    u2_name.place(x=350, y=360, width= 60)
           
    root.bind("<KeyPress>", check_enter)         ## звʼязуємо натискання клавіш <Return> і ","

## знищення кнопок Y/N 
def destroy_button():

    quit_button.destroy()
    nquit_button.destroy()             
    tk_button['text'] = "Очистити"
    tk_button['command']=ochistka
## розрахунок схеми
def calk():
   text1 = u1_name.get()
   text2 = c1_name.get()
   text3 = c2_name.get()
   u_in = int(text1)
   c1 = float(text2)
   c2 = float(text3)
   u_c2 =round(( u_in * (c2 / ( c1 + c2 ) ) ),2)
   u2text.set(str(u_c2))
   tk_button['text'] = "Кінець"
   global quit_button
   global nquit_button

    # створення кнопки, що закриває розрахунок (вбудована команда quit)
   quit_button = Button(frame, text="Y", fg="red", command=quit)
   quit_button.pack(side=LEFT)
   # створення кнопки, що продовжує розрахунок 
   nquit_button = Button(frame, text="N", fg="green" , command=destroy_button )
   nquit_button.pack(side=LEFT)
## підготовка наступного розрахуноку схеми   
def ochistka():   

   if rez==0 :
       tk_button['text'] = "Введіть U1,C1,C2"
   elif rez==1 :
       tk_button['text'] = "Введіть U1,R1,R2"
   
   tk_button['command']= write
    ###text1=''
    ###text2=''
    ###text3=''
    ###text1 = u1_name.get()
    ###text2 = c1_name.get()
    ###text3 = c2_name.get()
   u1text.set('')
   c1text.set('')
   c2text.set('')
   u2text.set('')
   u1_name.focus_set()
 #  створення вводу данних    
def write():                    
   
   if u1_name.get() =='':
      u1_name.focus_set()
   elif c1_name.get() =='':
      c1_name.focus_set()
   elif c2_name.get() =='':
      c2_name.focus_set()
      
   if u1_name.get() !='' and c1_name.get() !='' and c2_name.get() !='' :
       
      tk_button['text'] = "Розрахувати"
      tk_button['command']= calk
      u2_name.focus_set()
      c.create_rectangle(20, 350, 550, 380,         #стираємо текст  "десяткові дроби вносити через <.>"
                   fill='light blue',                # колір заливки  
                   width=0)                         # ширина межі
 # створення кнопки для меню
def  knopka () :
      global tk_button
      global frame 
      frame = Frame(root)              #  створення фрейму, у якому розміщуватимуться кнопки
      frame.pack(side=BOTTOM)
      
      tk_button = Button(frame , command=write)
      if rez==0 :
       tk_button['text'] = "Введіть U1,C1,C2"
      elif rez==1 :
       tk_button['text'] = "Введіть U1,R1,R2"
      
      tk_button.pack(side=LEFT)


root.mainloop()

#######     




