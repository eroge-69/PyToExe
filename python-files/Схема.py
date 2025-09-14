from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import sys
import pygame
import time
import pandas as pd
global spisok
global grup
spisok = [["РЩ6", "От ВРУ" , "СИП 3х120" ,0, "QF1 ВА4764 С64" , 3, 0, 1],[1, 'ВА4729 С25', 'ВВГнг 3х2,5', 'Розетка', 0, 0, 0, 0], [4, 'ВА101 С25', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [2, 'ВА4729 С16', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [3, 'ВА4729 С16', 'ВВГнг 3х2', 'Розетка', 0, 0, 0, 0], [1, 'ВА4729 С16', 'ВВГнг 3х2', 'Неизвестный потребитель', 0, 0, 0, 0], [1, 'ВА4729 С25', 'ВВГнг 3х2,5', 'Розетка', 0, 0, 0, 0], [4, 'ВА101 С25', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [2, 'ВА4729 С16', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [3, 'ВА4729 С16', 'ВВГнг 3х2', 'Розетка', 0, 0, 0, 0], [1, 'ВА4729 С16', 'ВВГнг 3х2', 'Неизвестный потребитель', 0, 0, 0, 0], [1, 'ВА4729 С25', 'ВВГнг 3х2,5', 'Розетка', 0, 0, 0, 0], [4, 'ВА101 С25', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [2, 'ВА4729 С16', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [3, 'ВА4729 С16', 'ВВГнг 3х2', 'Розетка', 0, 0, 0, 0], [1, 'ВА4729 С16', 'ВВГнг 3х2', 'Неизвестный потребитель', 0, 0, 0, 0], [1, 'ВА4729 С25', 'ВВГнг 3х2,5', 'Розетка', 0, 0, 0, 0], [4, 'ВА101 С25', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [2, 'ВА4729 С16', 'ВВГнг 3х2', 'Освещение', 0, 0, 0, 0], [3, 'ВА4729 С16', 'ВВГнг 3х2', 'Розетка', 0, 0, 0, 0], [1, 'ВА4729 С16', 'ВВГнг 3х2', 'Неизвестный потребитель', 0, 0, 0, 0]]


shit, vvod, vkabel, vav, vavtomat, pitf, schet, grup = spisok[0]
gr=1
root = Tk()
root.title("Праграмма саздания схем.")
root.geometry("700x600") 
a1,avtomat,kabel,potrebitel,r1,r2,r3,r4 = spisok[1]

def insert_text():
    global spisok
    file_name = fd.askopenfilename(initialdir='/Saves',
        filetypes=[("правельный файл", "*.xlsx"),
                   ("All files", "*.*")])
    if file_name=="":restarter()
    else :
        df = pd.read_excel(file_name)
        spisok=df.values.tolist()
        restarter()
    
 
 
def extract_text():
    global spisok
    
    file_name = fd.asksaveasfilename(initialdir='/Saves',initialfile='Безымянный.xlsx',
        filetypes=[("правельный файл", "*.xlsx"),
                   ("All files", "*.*")])
                   
    
    
    
    if file_name=="":restarter()
    else:
        df = pd.DataFrame(spisok)
        df.to_excel(file_name, index=False)
    
def restarter():
    global spisok
    
    shit, vvod, vkabel, vav, vavtomat, pitf, schet, grup = spisok[0]
    a1,avtomat,kabel,potrebitel,r1,r2,r3,r4 = spisok[1]
    entry1.delete(0, END)
    entry1.insert(0, shit)
    entry2.delete(0, END)
    entry2.insert(0, vvod)
    entry3.delete(0, END)
    entry3.insert(0, vkabel)
    entry4.delete(0, END)
    entry4.insert(0, vavtomat)
    entry5.delete(0, END)
    entry5.insert(0, int(pitf))
    entry6.delete(0, END)
    entry6.insert(0, int(grup))
    entry10.delete(0, END)
    entry10.insert(0, a1)
    entry11.delete(0, END)
    entry11.insert(0, avtomat)
    entry12.delete(0, END)
    entry12.insert(0, kabel)
    entry13.delete(0, END)
    entry13.insert(0, potrebitel)
    entry14.delete(0, END)
    entry14.insert(0, vav)


def VaVTDA():
    if vavt.get() == 1:
        entry4.config(state='normal')
        entry4.delete(0, END)
        entry14.config(state='normal')
        entry14.delete(0, END)
        
    else :
        shit, vvod, vkabel, vav, vavtomat, pitf, schet, grup = spisok[0]
        spisok[0]=shit, vvod, vkabel, 0, vavtomat, pitf, schet, grup
        entry14.delete(0, END)
        entry4.delete(0, END)
        entry14.insert(0, 0)
        entry4.insert(0, "")
        entry4.config(state='disabled')
        entry14.config(state='disabled')
        

def SHEDA():
    shit, vvod, vkabel, vav, vavtomat, pitf, schet, grup = spisok[0]
    spisok[0]=shit, vvod, vkabel, vav, vavtomat, pitf, int(SHE.get()), grup
    
def click_button():
    print(spisok)
    spisok[0]=entry1.get(),entry2.get(),entry3.get(),int(entry14.get()),entry4.get(),int(entry5.get()),int(SHE.get()),int(entry6.get())
    grup=int(entry6.get())
    print(spisok)

    
def click_button2():
    global gr
    f1=spisok[0]
    grup=f1[7]
    gr+=1
    if gr>int(grup):gr-=1
    gr2="Гр."+str(gr)
    a1,avtomat,kabel,potrebitel,r1,r2,r3,r4 = spisok[gr]
    label = ttk.Label(text=gr2)
    label.place(x=300,y=1)
    print(grup)
    entry10.delete(0, END)
    entry10.insert(0, a1)
    entry11.delete(0, END)
    entry11.insert(0, avtomat)
    entry12.delete(0, END)
    entry12.insert(0, kabel)
    entry13.delete(0, END)
    entry13.insert(0, potrebitel)

    

    
def click_button3():
    global gr
    gr-=1
    if gr<1:gr=1
    gr2="Гр."+str(gr)
    a1,avtomat,kabel,potrebitel,r1,r2,r3,r4 = spisok[gr]
    label = ttk.Label(text=gr2)
    label.place(x=300,y=1)
    entry10.delete(0, END)
    entry10.insert(0, a1)
    entry11.delete(0, END)
    entry11.insert(0, avtomat)
    entry12.delete(0, END)
    entry12.insert(0, kabel)
    entry13.delete(0, END)
    entry13.insert(0, potrebitel)


def click_button4():
    global gr
    global spisok
    spisok[gr]=int(entry10.get()),entry11.get(),entry12.get(),entry13.get(),0,0,0,0
    print(spisok)



def click_button5():
    print(spisok)
    pygame.init()

    screen = pygame.display.set_mode((1500, 852))
    screen.fill((255, 255, 255))
    kolonka = pygame.image.load("images/колонка.png")
    pusto = pygame.image.load("images/пусто.png")
    avt1p = pygame.image.load("images/автомат1п.png")
    avt1pbpe = pygame.image.load("images/автомат1пбре.png")
    avt2p = pygame.image.load("images/автомат2п.png")
    avt3p = pygame.image.load("images/автомат3п.png")
    avt3pbpe = pygame.image.load("images/автомат3пбре.png")
    scet = pygame.image.load("images/счетчик.png")
    vvavt = pygame.image.load("images/vvavt.png")
    pit1f = pygame.image.load("images/пит1ф.png")
    pit2f = pygame.image.load("images/пит2ф.png")
    pit3f = pygame.image.load("images/пит3ф.png")
    pitlin = pygame.image.load("images/питлин.png")
    lnpe = pygame.image.load("images/LNPE.png")
    uzo1p = pygame.image.load("images/узо1п.png")
    uzo3p = pygame.image.load("images/узо3п.png")
    uzo1pbpe = pygame.image.load("images/узо1пбре.png")
    vuzo = pygame.image.load("images/вузо.png")
    vpred = pygame.image.load("images/впред.png")
    pred1p = pygame.image.load("images/пред1п.png")
    pred3p = pygame.image.load("images/пред3п.png")
    pred1pbpe = pygame.image.load("images/пред1пбре.png")
    
    pitlin.set_colorkey((255, 255, 255))
    clock = pygame.time.Clock()
    sprite=avt3pbpe
    faz=pit3f
    #background_image = pygame.image.load("images/ббб.png")
    df = pd.read_excel("kord.xls")
    kord=df.values.tolist()
    x,y,xpitlin,ypitlin,xtext7,ytext7=kord[1]
    i=1
    #screen.blit(background_image, (0, 0))
    f1 = pygame.font.SysFont('arial', 14)
    f2 = pygame.font.SysFont('arial', 20)
    f3 = pygame.font.SysFont('arial', 50)
    
    play = True
    while play:
        
        shit, vvod, vkabel, vav, vavtomat, pitf, schet, grup = spisok[0]
        a1,avtomat,kabel,potrebitel,r1,r2,r3,r4 = spisok[i]
        if int(a1)==0: sprite=pusto
        if int(a1)==1: sprite=avt1p
        if int(a1)==2: sprite=avt2p
        if int(a1)==3: sprite=avt3p
        if int(a1)==4: sprite=avt1pbpe
        if int(a1)==5: sprite=avt3pbpe
        if int(a1)==6: sprite=uzo1p
        if int(a1)==7: sprite=uzo3p
        if int(a1)==8: sprite=uzo1pbpe
        if int(a1)==9: sprite=pred1p
        if int(a1)==10: sprite=pred3p
        if int(a1)==11: sprite=pred1pbpe


        
        if int(pitf)==1:faz=pit1f
        if int(pitf)==2:faz=pit2f
        if int(pitf)==3:faz=pit3f




        
        text1 = f1.render(avtomat, True, (0, 0, 0))
        text2 = f1.render(potrebitel, True, (0, 0, 0))
        text3 = f1.render(kabel, True, (0, 0, 0))
        text4 = f1.render(vkabel, True, (0, 0, 0))
    
        text5 = f1.render(vavtomat, True, (0, 0, 0))
        text6 = f1.render(vvod, True, (0, 0, 0))
        text7 = f2.render(shit, True, (0, 0, 0))
        sprite3 = pygame.transform.rotate(text1, 90)
        sprite4 = pygame.transform.rotate(text2, 90)
        sprite5 = pygame.transform.rotate(text3, 90)
        screen.blit(kolonka, (x-10, y+365))
        screen.blit(text4, (xpitlin+300,ypitlin+45))
        screen.blit(text5, (xpitlin+150,ypitlin+22))
        screen.blit(text6, (xpitlin+420,ypitlin+62))
        screen.blit(text7, (xtext7,ytext7))
        screen.blit(sprite, (x, y))
        kolonka.blit(sprite, (x, y+200))
        screen.blit(sprite3, (x, y+130))
        screen.blit(sprite4, (x+10,y+380))
        screen.blit(sprite5, (x, y+270))
        screen.blit(pitlin, (xpitlin,ypitlin))
        if int(schet)==1:screen.blit(scet, (xpitlin+100,ypitlin+54))
        screen.blit(faz, (xpitlin+330,ypitlin+63))
        if int(vav)==1:screen.blit(vvavt, (xpitlin+170,ypitlin+58))
        if int(vav)==2:screen.blit(vuzo, (xpitlin+170,ypitlin+58))
        if int(vav)==3:screen.blit(vpred, (xpitlin+170,ypitlin+58))
        pygame.display.update()
        clock.tick(60)
        if i<int(grup) :
            x=x+56
            i+=1
        else:
            screen.blit(lnpe, (x+60,y-10))
            time.sleep(1)
            file_name = fd.asksaveasfilename(initialdir='/Saves',initialfile='screenshot.png',
                                                filetypes=[("правельный файл", "*.png"),
                                                           ("All files", "*.*")])
            if file_name=="":file_name="Не задано.png"
            pygame.image.save(screen, file_name)
            play = False
            pygame.quit()
            #pygame.quit()
    #if i>7 : screen.quit()

    
label = ttk.Label(text="Название, место расположения щита")
label.pack(anchor=NW)
entry1 = ttk.Entry()
entry1.pack(anchor=NW, padx=6, pady=6)
entry1.insert(0, shit)

label = ttk.Label(text="Откуда приходит питание")
label.pack(anchor=NW)
entry2 = ttk.Entry()
entry2.pack(anchor=NW, padx=6, pady=6)
entry2.insert(0, vvod)

label = ttk.Label(text="Данные питающей линии")
label.pack(anchor=NW)
entry3 = ttk.Entry()
entry3.pack(anchor=NW, padx=6, pady=6)
entry3.insert(0, vkabel)


vavt = IntVar()
vavt_checkbutton = ttk.Checkbutton(text="Есть Ус-во. защиты на вводе", variable=vavt, command=VaVTDA)
vavt_checkbutton.pack(padx=6, pady=6, anchor=NW)

label = ttk.Label(text="Данные ус-ва. защиты  Тип ус-ва. защиты 1,2,3")
label.pack(anchor=NW)
entry4 = ttk.Entry(state="disabled")
entry4.pack(anchor=NW, padx=6, pady=6)
entry4.insert(0, vavtomat)

SHE = IntVar()
SHE_checkbutton = ttk.Checkbutton(text="Есть счетчик", variable=SHE, command=SHEDA)
SHE_checkbutton.pack(padx=6, pady=6, anchor=NW)

label = ttk.Label(text="Количество фаз")
label.pack(anchor=NW)
entry5 = ttk.Entry()
entry5.pack(anchor=NW, padx=6, pady=6)
entry5.insert(0, int(pitf))

label = ttk.Label(text="Количество Групп")
label.pack(anchor=NW)
entry6 = ttk.Entry()
entry6.pack(anchor=NW, padx=6, pady=6)
entry6.insert(0, int(grup))

btn = ttk.Button(text="Дальше", command=click_button)
btn.pack(anchor=NW)


gr2="Гр."+str(gr)
label = ttk.Label(text=gr2)
label.place(x=300,y=1)


label = ttk.Label(text="Количество полюсов")
label.place(x=300,y=30)
entry10 = ttk.Entry()
entry10.place(x=300,y=50)
entry10.insert(0, a1)


label = ttk.Label(text="Данные автомата")
label.place(x=300,y=80)
entry11 = ttk.Entry()
entry11.place(x=300,y=100)
entry11.insert(0, avtomat)

label = ttk.Label(text="Данные КЛ")
label.place(x=300,y=130)
entry12 = ttk.Entry()
entry12.place(x=300,y=150)
entry12.insert(0, kabel)

label = ttk.Label(text="Потребитель")
label.place(x=300,y=180)
entry13 = ttk.Entry()
entry13.place(x=300,y=200,width=280, height=40 )
entry13.insert(0, potrebitel)

entry14 = ttk.Entry()
entry14.insert(0, vav)
entry14.place(x=160,y=214,width=28, height=20 )
entry14.config(state='disabled')

label = ttk.Label(text="1-Автомат")
label.place(x=197,y=205)
label = ttk.Label(text="2-Узо")
label.place(x=197,y=220)
label = ttk.Label(text="3-Предоранитель")
label.place(x=197,y=235)

label = ttk.Label(text="0-Пусто")
label.place(x=450,y=0)
label = ttk.Label(text="1-Автомат 1ф")
label.place(x=450,y=20)
label = ttk.Label(text="2-Автомат 2ф")
label.place(x=450,y=40)
label = ttk.Label(text="3-Автомат 3ф")
label.place(x=450,y=60)
label = ttk.Label(text="4-Автомат 1фб-PE")
label.place(x=450,y=80)
label = ttk.Label(text="5-Автомат 3фб-PE")
label.place(x=450,y=100)
label = ttk.Label(text="6-Узо 1ф")
label.place(x=450,y=120)
label = ttk.Label(text="7-Узо 3ф")
label.place(x=450,y=140)
label = ttk.Label(text="8-Узо 1фб-PE")
label.place(x=450,y=160)
label = ttk.Label(text="9-Пред 1ф")
label.place(x=550,y=0)
label = ttk.Label(text="10-Пред 3ф")
label.place(x=550,y=20)
label = ttk.Label(text="11-Пред 1фб-РЕ")
label.place(x=550,y=40)


btn2 = ttk.Button(text="Вперет", command=click_button2)
btn2.place(x=400,y=250)

btn3 = ttk.Button(text="Назат", command=click_button3)
btn3.place(x=300,y=250)

btn4 = ttk.Button(text="Сохраница", command=click_button4)
btn4.place(x=350,y=280)

btn5 = ttk.Button(text="Рисовать", command=click_button5)
btn5.place(x=350,y=380)

btn6 = ttk.Button(text="Сохранить в файл", command=extract_text)
btn6.place(x=35,y=450)

btn7 = ttk.Button(text="Загрузить из файла", command=insert_text)
btn7.place(x=170,y=450)

root.mainloop()
