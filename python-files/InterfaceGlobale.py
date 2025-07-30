# Créé par nebuleuse, le 30/07/2025 en Python 3.7
#http://sdz.tdct.org/sdz/interface-graphique-pygame-pour-python.html#Lesinterfacesgraphiques
from pygame import*
from pygame.locals import*
import pygame
import sys
from random import *
from pygame import event
from math import*
import time
import subprocess



class BoutonRadio:
    def __init__(self,nom,coord):
        self.nom=nom   # Le nom de la case, par exemple "A1"
        self.coord=coord   # [centre,rayon]
        self.etat=0   # L'état de la case (0 = vide, 1 = activée, 2 = une autre activation)
        self.passage=0   # Indicateur pour savoir si la souris est passée dessus
        self.color0=pygame.Color(235,235,255)
        self.color1=pygame.Color(70,70,255)
        self.colorOutside=(0,0,0)
        self.Hitbox=pygame.Rect(coord[0][0]-coord[1],coord[0][1]-coord[1],coord[1]*2,coord[1]*2)
    def activation(self):
        if self.etat==0:
            self.etat=1
        else:
            self.etat=0
    def Apassage(self,a):
        if a=="1":
            self.passage="1"
        else:
            self.passage=0
    def affichage(self):
        if self.etat==1:
            c=self.color1
        else:
            c=self.color0
        pygame.draw.circle(screen,c,self.coord[0],self.coord[1])

        coord2=(self.coord[0][0]-1,self.coord[0][1])

        ep=round(0.3*self.coord[1])
        if self.passage=="1":
            pygame.draw.circle(screen,self.colorOutside,coord2,self.coord[1]+1,round(ep/1.55))
        else:
            pygame.draw.circle(screen,self.colorOutside,coord2,self.coord[1]+1,ep+2)
        pygame.display.flip()

class Texte:
    def __init__(self,texte,coord,font):
        self.texte=texte
        self.font=font
        self.mode="D"    # Début  /  Fin  /  Milieu
        self.coord=coord   # point eu centre du texte (horizontal)
        self.color=(0,0,0)


    def affichage(self):
        taille=self.font.size(self.texte)
        if self.mode=="D":
            coord2=(self.coord[0],self.coord[1]-(taille[1]//2))
        elif self.mode=="M":
            coord2=(self.coord[0]-(taille[0]//2),self.coord[1]-(taille[1]//2))
        else:
            coord2=(self.coord[0]-taille[0],self.coord[1]-(taille[1]//2))
        rendu = self.font.render(self.texte,True,self.color)
        screen.blit(rendu,coord2)




def liste_texte(l):
    texte=l[0]
    for y in range(1,len(l)):
        texte=texte+l[y]
    return texte


pygame.init()###########################################################
clock=pygame.time.Clock()###############################################
s_width=1000############################################################
s_height=600###########################################################
screen=pygame.display.set_mode((s_width,s_height))######################

fontBase = pygame.font.SysFont(None,50)
font = pygame.font.SysFont("Arial",10)

Alphabet=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]


screen.fill((255,255,255))
liste_cases=[]

## Moulecoef
BMC=BoutonRadio("BMC",[(300,120),20])
liste_cases.append(BMC)

TBMC=Texte("Coefficient Moule",(340,120),fontBase)
TMC=Texte("Permet d'obtenir le coefficient multiplicateur qui permet de modifier les proportion des ingrédient en changeant de moule",(341,150),font)
TMC.color=(255,10,10)

TBMC.affichage()
TMC.affichage()
BMC.affichage()

## TartelettesTarte
BTT=BoutonRadio("BTT",[(290,320),20])
liste_cases.append(BTT)

TBTT=Texte("Convertisseur Tartelettes/Tarte",(340,320),fontBase)
TTT=Texte("Permet d'obtenir le diamètre Z d'une tarte à partir de X tartelettes de diamètre Y, et inversement",(341,350),font)
TTT.color=(255,10,10)

TBTT.affichage()
TTT.affichage()
BTT.affichage()



while True:

# ---------- Permet de fermer la fenêtre sans crash ---------- #
    for events in pygame.event.get():
        if events.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
# ------------------------------------------------------------ #

        if events.type==pygame.MOUSEBUTTONDOWN:

            if BMC.Hitbox.collidepoint(events.pos):
                BMC.activation()
                BMC.Apassage("0")
                BMC.affichage()
                time.sleep(1)
                pygame.quit()
                subprocess.run(["python", "Moulecoef.py"])
                sys.exit()

            elif BTT.Hitbox.collidepoint(events.pos):
                BTT.activation()
                BTT.Apassage("0")
                BTT.affichage()
                time.sleep(1)
                pygame.quit()
                subprocess.run(["python", "TartelettesTarte.py"])
                sys.exit()


# ---------- Entoure le case en rouge si la souris est dessus ---------- #
    mouse_position = pygame.mouse.get_pos()
    for c2 in liste_cases:
        if c2.Hitbox.collidepoint(mouse_position):
            c2.Apassage("1")
        else:
            c2.Apassage("0")
        c2.affichage()
# --------------------------------------------------------------------- #






    pygame.display.flip()
    clock.tick(60)
