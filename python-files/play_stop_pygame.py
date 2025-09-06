import tkinter
from pygame import mixer
from tkinter import filedialog


#fonction play
def fonction_lecture1():
    mixer.music.load(son01)
    mixer.music.play()
    
def fonction_lecture2():
    mixer.music.load(son02)
    mixer.music.play()
    
def fonction_lecture3():
    mixer.music.load(son03)
    mixer.music.play()

def fonction_lecture4():
    mixer.music.load(son04)
    mixer.music.play()

def fonction_lecture5():
    mixer.music.load(son05)
    mixer.music.play()

#fonction stop
def fonction_stop():
    mixer.music.fadeout(2500) 

#fonction ouvrir fichier barre du menu
def fonction_ouvrir():
    filedialog.askopenfilename
    
#variables
son01 = "mp3/3 - revue des troupes.mp3"
son02 = "mp3/1 - garde a vous.mp3"
son03 = "4 - ouvrez&fermez le ban.mp3"
son04 = "mp3/2 - couleur + marseillaise.mp3"   
son05 = "5 - Aux Champs.mp3"  


#https://www.youtube.com/watch?v=C4GufpmKIdo
mixer.init()

fenetre = tkinter.Tk()
fenetre.title("Table de mixage")
fenetre.geometry("500x500", bg="blue")

#creer menu
menu_h = tkinter.Menu(fenetre)

#creer les menus avec la cascade
menu_fichier = tkinter.Menu(menu_h, tearoff=0)
menu_edition = tkinter.Menu(menu_h, tearoff=0)
menu_h.add_cascade(label="Fichier", menu=menu_fichier)
menu_h.add_cascade(label="Edition", menu=menu_edition)

#sous menu
menu_fichier.add_command(label="Nouveau")
menu_fichier.add_command(label="Ouvrir", command=fonction_ouvrir)
menu_fichier.add_command(label="Quitter", command=exit)

menu_edition.add_command(label="Parametre")

#placement du menu
fenetre.config(menu=menu_h)


btn01 = tkinter.Button(fenetre, text="Revue des troupes", command=fonction_lecture1)
btn02 = tkinter.Button(fenetre, text="Garde a vous", command=fonction_lecture2)
btn03 = tkinter.Button(fenetre, text="Ouvrez/fermez le ban", command=fonction_lecture3)
btn04 = tkinter.Button(fenetre, text="Couleurs + Marseillaise", command=fonction_lecture4)
btn05 = tkinter.Button(fenetre, text="Stop", command=fonction_stop)
btn06 = tkinter.Button(fenetre, text="Aux Champs", command=fonction_lecture5)

btn01.place(x=120, y=130)
btn02.place(x=250, y=130)
btn03.place(x=100, y=200)
btn04.place(x=250, y=200)
btn05.place(x=300, y=350)
btn06.place(x=400, y=400)


fenetre.mainloop()